package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Containers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeMiningDrillItem extends ExoframeWeaponItem {

    public ExoframeMiningDrillItem(Properties properties) {
        super(properties.stacksTo(1), 6, "tool_mining_drill");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        // Mining drill operates on mech kinetic power / no ammo needed
        return true;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        if (!(exoframe.level() instanceof ServerLevel serverLevel)) return false;

        Vec3 eyePos = pilot.getEyePosition();
        Vec3 look = pilot.getLookAngle();
        double reach = 10.0D;
        Vec3 reachEnd = eyePos.add(look.scale(reach));

        BlockHitResult hit = serverLevel.clip(new ClipContext(
                eyePos, reachEnd,
                ClipContext.Block.COLLIDER,
                ClipContext.Fluid.NONE,
                exoframe
        ));

        if (hit.getType() == HitResult.Type.BLOCK) {
            BlockPos center = hit.getBlockPos();
            boolean mined = false;
            int radius = 1;

            for (int dx = -radius; dx <= radius; dx++) {
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dz = -radius; dz <= radius; dz++) {
                        BlockPos target = center.offset(dx, dy, dz);
                        if (target.distSqr(center) > 2.6D) continue;
                        BlockState state = serverLevel.getBlockState(target);
                        if (state.isAir()) continue;

                        float hardness = state.getDestroySpeed(serverLevel, target);
                        if (hardness >= 0.0F && hardness <= 50.0F && !state.is(Blocks.BEDROCK)) {
                            List<ItemStack> drops = Block.getDrops(state, serverLevel, target, null, pilot, new ItemStack(net.minecraft.world.item.Items.NETHERITE_PICKAXE));
                            serverLevel.destroyBlock(target, false, pilot);
                            for (ItemStack drop : drops) {
                                Containers.dropItemStack(serverLevel, exoframe.getX(), exoframe.getY() + 0.5D, exoframe.getZ(), drop);
                            }
                            mined = true;
                        }
                    }
                }
            }

            if (mined) {
                serverLevel.playSound(null, center, SoundEvents.ANVIL_HIT, SoundSource.PLAYERS, 1.2F, 1.8F);
                serverLevel.playSound(null, center, SoundEvents.GRINDSTONE_USE, SoundSource.PLAYERS, 1.5F, 1.3F);
                exoframe.triggerRecoilAnim();
                return true;
            }
        }
        return false;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.drill_desc").withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.obsolete.drill_spec").withStyle(ChatFormatting.GRAY));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
