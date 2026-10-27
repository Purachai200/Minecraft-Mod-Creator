package com.titancombat.item;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.util.TitanWarpHelper;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.UUID;

public class PilotLicenseItem extends Item {

    public PilotLicenseItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseTitanEntity titan) {
            Level level = player.level();
            if (!level.isClientSide) {
                if (player.isShiftKeyDown()) {
                    // UNBIND / CLEAR ACTION
                    if (titan.getOwnerUUID() != null && !titan.getOwnerUUID().isEmpty()) {
                        if (player.getUUID().toString().equals(titan.getOwnerUUID())) {
                            titan.clearOwner();
                            clearLink(stack);
                            if (player.getItemInHand(hand) != stack) {
                                clearLink(player.getItemInHand(hand));
                            }
                            player.sendSystemMessage(Component.translatable("message.titancombat.link_cleared", titan.getTitanClass().getDisplayName()));
                            player.level().playSound(null, titan.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 1.2F, 1.2F);
                            return InteractionResult.SUCCESS;
                        } else {
                            player.sendSystemMessage(Component.translatable("message.titancombat.cannot_unbind_unowned"));
                            player.level().playSound(null, titan.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
                            return InteractionResult.FAIL;
                        }
                    } else {
                        clearLink(stack);
                        if (player.getItemInHand(hand) != stack) {
                            clearLink(player.getItemInHand(hand));
                        }
                        player.sendSystemMessage(Component.translatable("message.titancombat.device_reset"));
                        player.level().playSound(null, titan.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 1.0F, 1.2F);
                        return InteractionResult.SUCCESS;
                    }
                } else {
                    // BIND / CLAIM ACTION
                    if (titan.getOwnerUUID() == null || titan.getOwnerUUID().isEmpty()) {
                        // 1 Pilot = 1 Titan doctrine check
                        BaseTitanEntity existing = TitanWarpHelper.findCurrentTitanOfPlayer(player.getServer(), player);
                        if (existing != null && existing != titan) {
                            player.sendSystemMessage(Component.translatable("message.titancombat.single_titan_limit", existing.getTitanClass().getDisplayName()));
                            player.level().playSound(null, titan.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
                            return InteractionResult.FAIL;
                        }

                        titan.setOwner(player);
                        writeLink(stack, titan);
                        if (player.getItemInHand(hand) != stack) {
                            writeLink(player.getItemInHand(hand), titan);
                        }
                        player.sendSystemMessage(Component.translatable("message.titancombat.license_bound", titan.getTitanClass().getDisplayName(), player.getName().getString()));
                        player.level().playSound(null, titan.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1.0F, 1.2F);
                        return InteractionResult.SUCCESS;
                    } else if (player.getUUID().toString().equals(titan.getOwnerUUID())) {
                        writeLink(stack, titan);
                        if (player.getItemInHand(hand) != stack) {
                            writeLink(player.getItemInHand(hand), titan);
                        }
                        player.sendSystemMessage(Component.literal("§a[BIOMETRIC VERIFIED] You are the registered pilot of this " + titan.getTitanClass().getDisplayName() + ". Linked to License."));
                        player.level().playSound(null, titan.blockPosition(), SoundEvents.NOTE_BLOCK_CHIME.get(), SoundSource.PLAYERS, 1.0F, 1.8F);
                        return InteractionResult.SUCCESS;
                    } else {
                        player.sendSystemMessage(Component.translatable("message.titancombat.access_denied", titan.getOwnerName()));
                        player.level().playSound(null, titan.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
                        return InteractionResult.FAIL;
                    }
                }
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }

    /** Clear the titan's link from a License or Transponder stack. */
    public static void clearLink(ItemStack stack) {
        CompoundTag tag = stack.getTag();
        if (tag != null) {
            tag.remove("TitanUUID");
            tag.remove("TitanName");
            tag.remove("Dimension");
            tag.remove("LastPos");
        }
    }

    /** Write the titan's link (id, name, last known position) into a License or Transponder stack. */
    public static void writeLink(ItemStack stack, BaseTitanEntity titan) {
        CompoundTag tag = stack.getOrCreateTag();
        tag.putUUID("TitanUUID", titan.getUUID());
        tag.putString("TitanName", titan.getTitanClass().getDisplayName());
        tag.putString("Dimension", titan.level().dimension().location().toString());
        tag.putLong("LastPos", titan.blockPosition().asLong());
    }

    /** Explicit pairing required: Pilot devices must be paired by right-clicking a Titan directly. */
    public static void autoLinkInventory(Player player, BaseTitanEntity titan) {
        // Disabled: Pilot devices must be explicitly linked by right-clicking a Titan to avoid accidental cross-linking.
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Player player = context.getPlayer();
        if (player != null && player.isShiftKeyDown()) {
            Level level = context.getLevel();
            if (!level.isClientSide && level instanceof ServerLevel serverLevel) {
                Vec3 target = Vec3.atBottomCenterOf(context.getClickedPos().above());
                float yaw = player.getYRot() + 180.0F;
                if (executeRecallWarp(serverLevel, player, context.getItemInHand(), target, yaw)) {
                    return InteractionResult.SUCCESS;
                }
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        return super.useOn(context);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.isShiftKeyDown()) {
            // Looking up at sky (pitch < -60 degrees): Device wipe / unbind memory
            if (player.getXRot() < -60.0F) {
                if (!level.isClientSide && level instanceof ServerLevel serverLevel) {
                    CompoundTag tag = stack.getTag();
                    if (tag != null && tag.contains("TitanUUID")) {
                        UUID titanUUID = tag.getUUID("TitanUUID");
                        BaseTitanEntity titan = TitanWarpHelper.findTitan(serverLevel.getServer(), titanUUID, player, null, 0);
                        if (titan != null && player.getUUID().toString().equals(titan.getOwnerUUID())) {
                            titan.clearOwner();
                        }
                        tag.remove("TitanUUID");
                        tag.remove("TitanName");
                        tag.remove("Dimension");
                        tag.remove("LastPos");
                        player.sendSystemMessage(Component.translatable("message.titancombat.device_reset"));
                        level.playSound(null, player.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 1.0F, 1.4F);
                    } else {
                        player.sendSystemMessage(Component.translatable("message.titancombat.device_already_empty"));
                        level.playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.6F);
                    }
                }
                return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
            }

            if (!level.isClientSide && level instanceof ServerLevel serverLevel) {
                HitResult hit = player.pick(64.0D, 0.0F, false);
                BlockPos targetPos;
                if (hit.getType() == HitResult.Type.BLOCK && hit instanceof BlockHitResult bHit) {
                    targetPos = bHit.getBlockPos().relative(bHit.getDirection());
                } else {
                    Vec3 look = player.getLookAngle();
                    int tx = Mth.floor(player.getX() + look.x * 5.0D);
                    int tz = Mth.floor(player.getZ() + look.z * 5.0D);
                    targetPos = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, new BlockPos(tx, (int) player.getY(), tz));
                }
                Vec3 target = Vec3.atBottomCenterOf(targetPos);
                float yaw = player.getYRot() + 180.0F;
                executeRecallWarp(serverLevel, player, stack, target, yaw);
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }
        return super.use(level, player, hand);
    }

    private boolean executeRecallWarp(ServerLevel serverLevel, Player player, ItemStack stack, Vec3 target, float yaw) {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains("TitanUUID")) {
            player.sendSystemMessage(Component.translatable("message.titancombat.device_unpaired"));
            player.level().playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }

        UUID titanUUID = tag.getUUID("TitanUUID");
        String dim = tag.getString("Dimension");
        long lastPosLong = tag.getLong("LastPos");

        BaseTitanEntity titan = TitanWarpHelper.findTitan(serverLevel.getServer(), titanUUID, player, dim, lastPosLong);
        if (titan == null) {
            player.sendSystemMessage(Component.literal("§c[NEURAL LINK LOST] Could not locate your Titan in world. Right-click your Titan with License first."));
            player.level().playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }

        boolean success = TitanWarpHelper.warpTitanTo(titan, serverLevel, target, yaw, player);
        if (success) {
            tag.putString("Dimension", serverLevel.dimension().location().toString());
            tag.putLong("LastPos", titan.blockPosition().asLong());
        }
        return success;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("IMC / Militia Certified Pilot License").withStyle(ChatFormatting.GOLD));
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("TitanName")) {
            tooltip.add(Component.literal("Linked Titan: ").withStyle(ChatFormatting.GRAY)
                    .append(Component.literal(tag.getString("TitanName")).withStyle(ChatFormatting.GREEN)));
        } else {
            tooltip.add(Component.literal("Right-click an unowned Titan to register ownership (1 Titan per Pilot).").withStyle(ChatFormatting.GRAY));
        }
        tooltip.add(Component.literal("Shift + Right-Click Titan: ").withStyle(ChatFormatting.RED)
                .append(Component.literal("Unbind & release neural link").withStyle(ChatFormatting.WHITE)));
        tooltip.add(Component.literal("Shift + Look UP + Right-Click: ").withStyle(ChatFormatting.DARK_RED)
                .append(Component.literal("Wipe / Reset device pairing").withStyle(ChatFormatting.WHITE)));
        tooltip.add(Component.literal("Shift + Right-Click Ground/Air: ").withStyle(ChatFormatting.AQUA)
                .append(Component.literal("Tactical Warp Recall Titan (Max 250m, Dome Shield Active)").withStyle(ChatFormatting.WHITE)));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
