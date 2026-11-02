package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.titancombat.entity.transport.TitanSkyCraneDroneEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.UUID;

public class HeavyTransportWinchItem extends Item {

    public HeavyTransportWinchItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        Level level = player.level();

        // 1. Target is a Titan or Obsolete Exoframe: Select it for winch loading
        if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(target)) {
            if (!level.isClientSide) {
                CompoundTag tag = stack.getOrCreateTag();
                tag.putUUID("WinchTitanUUID", target.getUUID());
                String cargoName = (target instanceof BaseTitanEntity titan) ? titan.getTitanClass().getDisplayName() : target.getType().getDescription().getString();
                tag.putString("WinchTitanName", cargoName);

                player.sendSystemMessage(Component.literal("§a[WINCH LINKED] " + cargoName +
                        " attached to magnetic cable! Now right-click any Transport Hauler, Barge, Carrier, Truck, or Helo to lock it onto the deck."));
                level.playSound(null, player.blockPosition(), SoundEvents.CHAIN_PLACE, SoundSource.PLAYERS, 1.2F, 1.4F);
                level.playSound(null, player.blockPosition(), SoundEvents.ARMOR_EQUIP_CHAIN, SoundSource.PLAYERS, 1.0F, 1.1F);
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        // 2. Target is a Transport Vehicle: Lock the selected Titan (or unclamp)
        if (target instanceof BaseTransportVehicleEntity vehicle) {
            if (!level.isClientSide) {
                CompoundTag tag = stack.getTag();

                // Airborne Hot-Drop trigger for Sky-Crane
                if (player.isShiftKeyDown() && vehicle instanceof TitanSkyCraneDroneEntity drone && !drone.onGround()) {
                    drone.performAirborneHotDrop(player);
                    return InteractionResult.SUCCESS;
                }

                // If player is sneaking: release clamps
                if (player.isShiftKeyDown() && vehicle.hasCargo()) {
                    vehicle.releaseMountedTitans(player);
                    return InteractionResult.SUCCESS;
                }

                // Load designated Titan or Exoframe
                if (tag != null && tag.contains("WinchTitanUUID")) {
                    UUID cargoUUID = tag.getUUID("WinchTitanUUID");
                    List<LivingEntity> nearbyCargo = level.getEntitiesOfClass(LivingEntity.class, vehicle.getBoundingBox().inflate(32.0D),
                            t -> t.getUUID().equals(cargoUUID) && com.titancombat.util.CrossModCargoHelper.isCargoEligible(t));

                    if (!nearbyCargo.isEmpty()) {
                        LivingEntity cargo = nearbyCargo.get(0);
                        if (vehicle.lockCargoToDeck(cargo, player)) {
                            tag.remove("WinchTitanUUID");
                            tag.remove("WinchTitanName");
                            return InteractionResult.SUCCESS;
                        }
                    } else {
                        player.sendSystemMessage(Component.literal("§c[WINCH ERROR] Selected Titan / Exoframe is too far (>32m) or not found."));
                    }
                } else {
                    // Auto-detect closest Titan / Exoframe within 10 blocks if none specifically tagged
                    List<LivingEntity> nearby = level.getEntitiesOfClass(LivingEntity.class, vehicle.getBoundingBox().inflate(10.0D),
                            t -> !t.isPassenger() && com.titancombat.util.CrossModCargoHelper.isCargoEligible(t));
                    if (!nearby.isEmpty()) {
                        LivingEntity cargo = nearby.get(0);
                        if (vehicle.lockCargoToDeck(cargo, player)) {
                            return InteractionResult.SUCCESS;
                        }
                    } else if (vehicle.hasCargo()) {
                        vehicle.releaseMountedTitans(player);
                        return InteractionResult.SUCCESS;
                    } else {
                        player.sendSystemMessage(Component.literal("§7[WINCH INFO] First right-click your Titan or Exoframe to attach cable, then right-click the vehicle to load."));
                    }
                }
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        return super.interactLivingEntity(stack, player, target, hand);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Industrial Magnetic Winch & Ratchet Cable").withStyle(ChatFormatting.GOLD));
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("WinchTitanName")) {
            tooltip.add(Component.literal("Winch Attached to: ").withStyle(ChatFormatting.GRAY)
                    .append(Component.literal(tag.getString("WinchTitanName")).withStyle(ChatFormatting.GREEN)));
            tooltip.add(Component.literal("Right-click Vehicle: ").withStyle(ChatFormatting.YELLOW)
                    .append(Component.literal("Lock Titan onto transport deck").withStyle(ChatFormatting.WHITE)));
        } else {
            tooltip.add(Component.literal("1. Right-click Titan: Attach winch cable").withStyle(ChatFormatting.GRAY));
            tooltip.add(Component.literal("2. Right-click Vehicle: Lock onto transport deck").withStyle(ChatFormatting.GRAY));
        }
        tooltip.add(Component.literal("Shift + Right-click Vehicle: ").withStyle(ChatFormatting.AQUA)
                .append(Component.literal("Release Clamps / Airborne Hot-Drop").withStyle(ChatFormatting.WHITE)));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
