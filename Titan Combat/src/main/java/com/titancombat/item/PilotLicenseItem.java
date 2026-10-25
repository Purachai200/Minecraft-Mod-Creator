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
                CompoundTag tag = stack.getOrCreateTag();
                if (titan.getOwnerUUID() == null || titan.getOwnerUUID().isEmpty()) {
                    // Claim unowned Titan
                    titan.setOwner(player);
                    tag.putUUID("TitanUUID", titan.getUUID());
                    tag.putString("TitanName", titan.getTitanClass().getDisplayName());
                    tag.putString("Dimension", level.dimension().location().toString());
                    tag.putLong("LastPos", titan.blockPosition().asLong());

                    player.sendSystemMessage(Component.translatable("message.titancombat.license_bound", titan.getTitanClass().getDisplayName(), player.getName().getString()));
                    player.level().playSound(null, titan.blockPosition(), SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1.0F, 1.2F);
                } else if (player.getUUID().toString().equals(titan.getOwnerUUID())) {
                    tag.putUUID("TitanUUID", titan.getUUID());
                    tag.putString("TitanName", titan.getTitanClass().getDisplayName());
                    tag.putString("Dimension", level.dimension().location().toString());
                    tag.putLong("LastPos", titan.blockPosition().asLong());

                    player.sendSystemMessage(Component.literal("§a[BIOMETRIC VERIFIED] You are the registered pilot of this " + titan.getTitanClass().getDisplayName() + ". Linked to License."));
                    player.level().playSound(null, titan.blockPosition(), SoundEvents.NOTE_BLOCK_CHIME.get(), SoundSource.PLAYERS, 1.0F, 1.8F);
                } else {
                    player.sendSystemMessage(Component.literal("§c[ACCESS DENIED] Titan is registered to Pilot: " + titan.getOwnerName()));
                    player.level().playSound(null, titan.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.2F);
                }
            }
            return InteractionResult.sidedSuccess(player.level().isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
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
        UUID titanUUID = tag != null && tag.contains("TitanUUID") ? tag.getUUID("TitanUUID") : null;
        String dim = tag != null ? tag.getString("Dimension") : null;
        long lastPosLong = tag != null ? tag.getLong("LastPos") : 0;

        BaseTitanEntity titan = TitanWarpHelper.findTitan(serverLevel.getServer(), titanUUID, player, dim, lastPosLong);
        if (titan == null) {
            player.sendSystemMessage(Component.literal("§c[NEURAL LINK LOST] Could not locate your Titan in world. Right-click your Titan with License first."));
            player.level().playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }

        boolean success = TitanWarpHelper.warpTitanTo(titan, serverLevel, target, yaw, player);
        if (success && tag != null) {
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
            tooltip.add(Component.literal("Right-click an unowned Titan to register ownership.").withStyle(ChatFormatting.GRAY));
        }
        tooltip.add(Component.literal("Shift + Right-Click Ground/Air: ").withStyle(ChatFormatting.AQUA)
                .append(Component.literal("Emergency Warp Recall Titan (Dome Shield Active)").withStyle(ChatFormatting.WHITE)));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
