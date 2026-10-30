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
import net.minecraft.tags.BlockTags;
import net.minecraft.world.Containers;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.*;

public class ExoframeChainsawItem extends ExoframeWeaponItem {

    public ExoframeChainsawItem(Properties properties) {
        super(properties.stacksTo(1), 8, "tool_chainsaw");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
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
            BlockState hitState = serverLevel.getBlockState(center);

            if (hitState.is(BlockTags.LOGS) || hitState.is(BlockTags.LEAVES)) {
                Set<BlockPos> tree = new HashSet<>();
                Queue<BlockPos> queue = new ArrayDeque<>();
                queue.add(center);
                tree.add(center);
                int maxBlocks = 48;

                while (!queue.isEmpty() && tree.size() < maxBlocks) {
                    BlockPos cur = queue.poll();
                    for (Direction d : Direction.values()) {
                        BlockPos n = cur.relative(d);
                        if (!tree.contains(n) && n.distSqr(center) <= 180.0D) {
                            BlockState bs = serverLevel.getBlockState(n);
                            if (bs.is(BlockTags.LOGS) || bs.is(BlockTags.LEAVES)) {
                                tree.add(n);
                                queue.add(n);
                                if (tree.size() >= maxBlocks) break;
                            }
                        }
                    }
                }

                for (BlockPos p : tree) {
                    BlockState bs = serverLevel.getBlockState(p);
                    List<ItemStack> drops = Block.getDrops(bs, serverLevel, p, null, pilot, new ItemStack(net.minecraft.world.item.Items.NETHERITE_AXE));
                    serverLevel.destroyBlock(p, false, pilot);
                    for (ItemStack drop : drops) {
                        Containers.dropItemStack(serverLevel, exoframe.getX(), exoframe.getY() + 0.5D, exoframe.getZ(), drop);
                    }
                }

                serverLevel.playSound(null, center, SoundEvents.WOOD_BREAK, SoundSource.PLAYERS, 2.0F, 0.9F);
                serverLevel.playSound(null, center, SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.2F, 1.6F);
                exoframe.triggerRecoilAnim();
                return true;
            }
        }
        return false;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.chainsaw_desc").withStyle(ChatFormatting.GREEN));
        tooltip.add(Component.translatable("tooltip.obsolete.chainsaw_spec").withStyle(ChatFormatting.GRAY));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
