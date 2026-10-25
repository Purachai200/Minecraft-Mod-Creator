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

public class HangarTransponderItem extends Item {

    public HangarTransponderItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (target instanceof BaseTitanEntity titan) {
            Level level = player.level();
            if (!level.isClientSide) {
                // Link Remote Key Fob to this Titan
                CompoundTag tag = stack.getOrCreateTag();
                tag.putUUID("TitanUUID", titan.getUUID());
                tag.putString("TitanName", titan.getTitanClass().getDisplayName());
                tag.putString("Dimension", level.dimension().location().toString());
                tag.putLong("LastPos", titan.blockPosition().asLong());

                player.sendSystemMessage(Component.translatable("message.titancombat.transponder_linked",
                        titan.getTitanClass().getDisplayName(), titan.blockPosition().getX(), titan.blockPosition().getZ()));
                level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_CHIME.get(), SoundSource.PLAYERS, 1.2F, 1.8F);
                level.playSound(null, player.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.0F, 1.2F);
                return InteractionResult.SUCCESS;
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }
        return super.interactLivingEntity(stack, player, target, hand);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        Player player = context.getPlayer();
        ItemStack stack = context.getItemInHand();
        BlockPos clickedPos = context.getClickedPos().above();

        if (player != null && player.isShiftKeyDown()) {
            return toggleTitanStandby(level, player, stack);
        }

        if (!level.isClientSide && player != null) {
            Vec3 target = Vec3.atBottomCenterOf(clickedPos);
            float yaw = player.getYRot() + 180.0F;
            if (executeWarp(level, player, stack, target, yaw)) {
                return InteractionResult.SUCCESS;
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);

        if (player.isShiftKeyDown()) {
            toggleTitanStandby(level, player, stack);
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
        }

        if (!level.isClientSide) {
            // Determine target position: raycast block or ground 5 blocks in front
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
            executeWarp(level, player, stack, target, yaw);
        }

        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    private boolean executeWarp(Level level, Player player, ItemStack stack, Vec3 target, float yaw) {
        if (!(level instanceof ServerLevel serverLevel)) return false;

        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains("TitanUUID")) {
            player.sendSystemMessage(Component.literal("§c[KEY FOB ERROR] Remote not linked to any Mech! Right-click your Mech first."));
            level.playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.6F);
            return false;
        }

        UUID titanUUID = tag.getUUID("TitanUUID");
        String dim = tag.getString("Dimension");
        long lastPosLong = tag.getLong("LastPos");

        BaseTitanEntity titan = TitanWarpHelper.findTitan(serverLevel.getServer(), titanUUID, player, dim, lastPosLong);
        if (titan == null) {
            player.sendSystemMessage(Component.literal("§c[SIGNAL LOST] Could not locate your Titan. Please ensure its chunk is loaded or re-link with the remote."));
            level.playSound(null, player.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }

        boolean success = TitanWarpHelper.warpTitanTo(titan, serverLevel, target, yaw, player);
        if (success) {
            tag.putString("Dimension", serverLevel.dimension().location().toString());
            tag.putLong("LastPos", titan.blockPosition().asLong());
        }
        return success;
    }

    private InteractionResult toggleTitanStandby(Level level, Player player, ItemStack stack) {
        if (!level.isClientSide && level instanceof ServerLevel serverLevel) {
            CompoundTag tag = stack.getTag();
            if (tag == null || !tag.contains("TitanUUID")) {
                player.sendSystemMessage(Component.literal("§c[KEY FOB ERROR] Remote not linked to any Mech! Right-click your Mech first."));
                return InteractionResult.FAIL;
            }

            UUID titanUUID = tag.getUUID("TitanUUID");
            String dim = tag.getString("Dimension");
            long lastPosLong = tag.getLong("LastPos");

            BaseTitanEntity titan = TitanWarpHelper.findTitan(serverLevel.getServer(), titanUUID, player, dim, lastPosLong);
            if (titan != null) {
                boolean currentStandby = titan.isStandbyMode();
                titan.setStandbyMode(!currentStandby);
                if (currentStandby) {
                    player.sendSystemMessage(Component.literal("§a[REMOTE] " + titan.getTitanClass().getDisplayName() + " Standby disabled. Systems Online."));
                    level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.PLAYERS, 1.2F, 1.5F);
                } else {
                    titan.getNavigation().stop();
                    player.sendSystemMessage(Component.literal("§6[REMOTE] " + titan.getTitanClass().getDisplayName() + " anchored in Standby Mode."));
                    level.playSound(null, player.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.PLAYERS, 1.2F, 0.8F);
                }
                return InteractionResult.SUCCESS;
            } else {
                player.sendSystemMessage(Component.literal("§c[SIGNAL LOST] Could not locate your Titan to toggle standby."));
            }
        }
        return InteractionResult.sidedSuccess(level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        CompoundTag tag = stack.getTag();
        if (tag != null && tag.contains("TitanName")) {
            tooltip.add(Component.literal("Linked Mech: ").withStyle(ChatFormatting.GRAY)
                    .append(Component.literal(tag.getString("TitanName")).withStyle(ChatFormatting.GOLD)));
        } else {
            tooltip.add(Component.literal("No Mech linked. Right-click your Mech to pair.").withStyle(ChatFormatting.DARK_GRAY));
        }
        tooltip.add(Component.literal("Right-click Ground / Air: ").withStyle(ChatFormatting.AQUA)
                .append(Component.literal("Warp Titan to selected location (Dome Shield Active)").withStyle(ChatFormatting.WHITE)));
        tooltip.add(Component.literal("Shift + Right-click: ").withStyle(ChatFormatting.YELLOW)
                .append(Component.literal("Remote Toggle Standby Mode").withStyle(ChatFormatting.WHITE)));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
