package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.ModEntities;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeKitItem extends Item {
    private final int frameTier;

    public ExoframeKitItem(Properties properties, int frameTier) {
        super(properties.stacksTo(1));
        this.frameTier = frameTier;
    }

    public ExoframeKitItem(Properties properties) {
        this(properties, 1);
    }

    public int getFrameTier() {
        return frameTier;
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        Level level = context.getLevel();
        if (level.isClientSide) {
            return InteractionResult.SUCCESS;
        }

        BlockPos pos = context.getClickedPos();
        Direction direction = context.getClickedFace();
        BlockPos spawnPos = pos.relative(direction);

        ExoframeEntity exoframe = ModEntities.EXOFRAME.get().create(level);
        if (exoframe != null) {
            Player player = context.getPlayer();
            float yaw = player != null ? player.getYRot() : 0.0F;
            exoframe.moveTo(spawnPos.getX() + 0.5D, spawnPos.getY(), spawnPos.getZ() + 0.5D, yaw, 0.0F);
            exoframe.yHeadRot = yaw;
            exoframe.yBodyRot = yaw;
            exoframe.setFrameTier(this.frameTier);
            level.addFreshEntity(exoframe);

            level.playSound(null, spawnPos, ModSounds.EXOFRAME_SERVO.get(), SoundSource.PLAYERS, 1.8F, 1.0F);

            if (player != null && !player.getAbilities().instabuild) {
                context.getItemInHand().shrink(1);
            }
            return InteractionResult.CONSUME;
        }

        return InteractionResult.FAIL;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.exoframe_kit_desc").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.exoframe_kit_deploy").withStyle(ChatFormatting.AQUA));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
