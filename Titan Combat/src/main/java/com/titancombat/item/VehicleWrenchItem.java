package com.titancombat.item;

import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.titancombat.entity.transport.TitanCargoBargeEntity;
import com.titancombat.entity.transport.TitanChinookTransporterEntity;
import com.titancombat.entity.transport.TitanHaulerTruckEntity;
import com.titancombat.entity.transport.TitanOceanCarrierEntity;
import com.titancombat.entity.transport.TitanSkyCraneDroneEntity;
import com.titancombat.entity.transport.TitanTacticalTruckEntity;
import com.titancombat.entity.transport.TitanV22OspreyEntity;
import com.titancombat.entity.transport.TitanArmoredApcEntity;
import com.titancombat.entity.transport.TitanMobileSuitTrailerEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Titan Logistics & Vehicle Deconstruction Wrench:
 * Shift + Right-Click any transport vehicle or titan to safely deconstruct it back into a portable deployment item.
 */
public class VehicleWrenchItem extends Item {

    public VehicleWrenchItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        Level level = player.level();

        // Check if target is a transport vehicle
        if (target instanceof BaseTransportVehicleEntity vehicle) {
            // Require sneaking to prevent accidental disassembly while trying to mount or fuel
            if (!player.isShiftKeyDown()) {
                if (level.isClientSide) {
                    player.displayClientMessage(Component.literal("§e[WRENCH] Hold Shift + Right-Click to deconstruct vehicle back into an item."), true);
                }
                return InteractionResult.sidedSuccess(level.isClientSide);
            }

            if (!level.isClientSide) {
                // 1. Release cargo first if vehicle has mounted Titans or Exoframes
                if (vehicle.hasCargo() || !vehicle.getPassengers().isEmpty()) {
                    vehicle.releaseMountedTitans(player);
                }

                // If player or another mob is still riding, dismount them
                for (Entity passenger : List.copyOf(vehicle.getPassengers())) {
                    passenger.stopRiding();
                }

                // 2. Identify corresponding deploy item
                ItemStack dropStack = getDeployItemStack(vehicle);

                // 3. Play mechanical deconstruction sound & particles
                BlockPos pos = vehicle.blockPosition();
                level.playSound(null, pos, SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.4F, 1.2F);
                level.playSound(null, pos, SoundEvents.ARMOR_EQUIP_IRON, SoundSource.PLAYERS, 1.5F, 0.9F);
                level.playSound(null, pos, SoundEvents.ITEM_PICKUP, SoundSource.PLAYERS, 1.2F, 1.1F);

                // 4. Remove entity from world
                vehicle.discard();

                // 5. Give item to player or drop at feet
                if (!player.getInventory().add(dropStack)) {
                    ItemEntity itemEntity = new ItemEntity(level, player.getX(), player.getY() + 0.5D, player.getZ(), dropStack);
                    level.addFreshEntity(itemEntity);
                }

                player.sendSystemMessage(Component.literal("§a[LOGISTICS] Vehicle safely disassembled into: §f" + dropStack.getHoverName().getString()));
            }

            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        return super.interactLivingEntity(stack, player, target, hand);
    }

    private ItemStack getDeployItemStack(BaseTransportVehicleEntity vehicle) {
        ItemStack stack;
        if (vehicle instanceof TitanHaulerTruckEntity) {
            stack = new ItemStack(ModItems.HAULER_TRUCK.get());
        } else if (vehicle instanceof TitanCargoBargeEntity) {
            stack = new ItemStack(ModItems.CARGO_BARGE.get());
        } else if (vehicle instanceof TitanSkyCraneDroneEntity) {
            stack = new ItemStack(ModItems.SKYCRANE_DRONE.get());
        } else if (vehicle instanceof TitanOceanCarrierEntity) {
            stack = new ItemStack(ModItems.OCEAN_CARRIER.get());
        } else if (vehicle instanceof TitanTacticalTruckEntity) {
            stack = new ItemStack(ModItems.TACTICAL_TRUCK.get());
        } else if (vehicle instanceof TitanChinookTransporterEntity) {
            stack = new ItemStack(ModItems.CHINOOK_TRANSPORTER.get());
        } else if (vehicle instanceof TitanV22OspreyEntity) {
            stack = new ItemStack(ModItems.V22_OSPREY.get());
        } else if (vehicle instanceof TitanArmoredApcEntity) {
            stack = new ItemStack(ModItems.ARMORED_APC.get());
        } else if (vehicle instanceof TitanMobileSuitTrailerEntity) {
            stack = new ItemStack(ModItems.MOBILE_SUIT_TRAILER.get());
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanLcacHovercraftEntity) {
            stack = new ItemStack(ModItems.LCAC_HOVERCRAFT.get());
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanC130HerculesEntity) {
            stack = new ItemStack(ModItems.C130_HERCULES.get());
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanRepairTruckEntity) {
            stack = new ItemStack(ModItems.REPAIR_TRUCK.get());
        } else {
            stack = new ItemStack(ModItems.HAULER_TRUCK.get());
        }

        // Preserve remaining energy in item tag
        CompoundTag tag = stack.getOrCreateTag();
        tag.putInt("SavedEnergy", vehicle.getEnergy());
        tag.putInt("SavedFaction", vehicle.getFaction().getId());
        tag.putInt("SavedCamo", vehicle.getCamo());
        return stack;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Industrial Logistics Deconstruction Tool").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.literal("Shift + Right-Click any transport vehicle to fold it back into an item.").withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.literal("Preserves fuel and disembarks cargo safely.").withStyle(ChatFormatting.GRAY));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
