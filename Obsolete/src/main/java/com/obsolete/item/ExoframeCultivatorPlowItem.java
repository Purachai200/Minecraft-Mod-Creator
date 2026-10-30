package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Heavy Mechanized Hydraulic Cultivator Plow tool for agriculture exoframe configurations.
 * Tills dirt/grass into farmland in a 3x3 footprint and harvests/replants mature crops.
 */
public class ExoframeCultivatorPlowItem extends ExoframeWeaponItem {

    public ExoframeCultivatorPlowItem(Properties properties) {
        super(properties.stacksTo(1), 6, "tool_cultivator_plow");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        // Agricultural tools operate on mech hydraulic torque
        return true;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        if (!(exoframe.level() instanceof ServerLevel serverLevel)) return false;

        Vec3 eyePos = pilot.getEyePosition();
        Vec3 look = pilot.getLookAngle();
        double reach = 8.0D;
        Vec3 reachEnd = eyePos.add(look.scale(reach));

        BlockHitResult hit = serverLevel.clip(new ClipContext(
                eyePos, reachEnd,
                ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE,
                exoframe
        ));

        BlockPos centerPos;
        if (hit.getType() == HitResult.Type.BLOCK) {
            centerPos = hit.getBlockPos();
        } else {
            // Default to ground directly in front of mech
            centerPos = exoframe.blockPosition().relative(exoframe.getDirection(), 2).below();
        }

        boolean operated = false;
        int radius = 1; // 3x3 swath

        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                BlockPos targetPos = centerPos.offset(dx, 0, dz);
                BlockState state = serverLevel.getBlockState(targetPos);
                BlockPos abovePos = targetPos.above();
                BlockState aboveState = serverLevel.getBlockState(abovePos);

                // 1. Harvest mature crops
                if (state.getBlock() instanceof CropBlock crop && crop.isMaxAge(state)) {
                    List<ItemStack> drops = Block.getDrops(state, serverLevel, targetPos, null, pilot, ItemStack.EMPTY);
                    serverLevel.destroyBlock(targetPos, false);
                    drops.forEach(drop -> Containers.dropItemStack(serverLevel, targetPos.getX() + 0.5, targetPos.getY() + 0.5, targetPos.getZ() + 0.5, drop));
                    // Replant at age 0
                    serverLevel.setBlockAndUpdate(targetPos, crop.getStateForAge(0));
                    operated = true;
                    continue;
                }

                // Also check crop sitting on top of target block
                if (aboveState.getBlock() instanceof CropBlock cropAbove && cropAbove.isMaxAge(aboveState)) {
                    List<ItemStack> drops = Block.getDrops(aboveState, serverLevel, abovePos, null, pilot, ItemStack.EMPTY);
                    serverLevel.destroyBlock(abovePos, false);
                    drops.forEach(drop -> Containers.dropItemStack(serverLevel, abovePos.getX() + 0.5, abovePos.getY() + 0.5, abovePos.getZ() + 0.5, drop));
                    serverLevel.setBlockAndUpdate(abovePos, cropAbove.getStateForAge(0));
                    operated = true;
                    continue;
                }

                // 2. Till dirt/grass into farmland
                if (aboveState.isAir()) {
                    if (state.is(Blocks.GRASS_BLOCK) || state.is(Blocks.DIRT) || state.is(Blocks.DIRT_PATH)) {
                        serverLevel.setBlockAndUpdate(targetPos, Blocks.FARMLAND.defaultBlockState());
                        operated = true;
                    }
                }
            }
        }

        if (operated) {
            serverLevel.playSound(null, centerPos, SoundEvents.HOE_TILL, SoundSource.PLAYERS, 1.2F, 0.85F);
            serverLevel.playSound(null, exoframe.blockPosition(), SoundEvents.IRON_GOLEM_STEP, SoundSource.PLAYERS, 1.0F, 1.4F);
            return true;
        }

        return false;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag isAdvanced) {
        tooltip.add(Component.translatable("tooltip.obsolete.cultivator_desc").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.obsolete.cultivator_spec").withStyle(ChatFormatting.GRAY));
    }
}
