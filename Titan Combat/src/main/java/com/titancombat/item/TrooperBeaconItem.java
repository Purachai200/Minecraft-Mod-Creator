package com.titancombat.item;

import com.titancombat.entity.TitanClass;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Cheap drop beacon for the light frames: deploys the MP-01 Trooper or the SR-07 Scout (Shift + right-click to switch). */
public class TrooperBeaconItem extends TitanDropBeaconItem {

    public TrooperBeaconItem(Properties properties) {
        super(properties);
    }

    @Override
    protected TitanClass selectedTitan(ItemStack stack) {
        return getSelectedTitan(stack) == TitanClass.SCOUT ? TitanClass.SCOUT : TitanClass.TROOPER;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (!player.isShiftKeyDown()) return InteractionResultHolder.pass(stack);
        if (!level.isClientSide) {
            TitanClass next = selectedTitan(stack) == TitanClass.TROOPER ? TitanClass.SCOUT : TitanClass.TROOPER;
            setSelectedTitan(stack, next);
            player.sendSystemMessage(Component.translatable("message.titancombat.beacon_switched", next.getDisplayName(), next.getRole()));
            level.playSound(null, player.blockPosition(), SoundEvents.UI_BUTTON_CLICK.get(), SoundSource.PLAYERS, 0.8F, 1.4F);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Deploys: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(selectedTitan(stack).getDisplayName() + " (" + selectedTitan(stack).getRole() + ")").withStyle(ChatFormatting.GREEN)));
        tooltip.add(Component.literal("Right-click ground: ").withStyle(ChatFormatting.GREEN)
                .append(Component.literal("Assemble & Deploy on Ground").withStyle(ChatFormatting.WHITE)));
        tooltip.add(Component.literal("Shift + Right-Click in air: ").withStyle(ChatFormatting.DARK_AQUA)
                .append(Component.literal("Trooper / Scout").withStyle(ChatFormatting.YELLOW)));
    }
}
