package com.titancombat.item;

import com.titancombat.entity.TitanClass;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Cheap single-purpose drop beacon: deploys only the MP-01 Trooper, no class switching. */
public class TrooperBeaconItem extends TitanDropBeaconItem {

    public TrooperBeaconItem(Properties properties) {
        super(properties);
    }

    @Override
    protected TitanClass selectedTitan(ItemStack stack) {
        return TitanClass.TROOPER;
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        return InteractionResultHolder.pass(player.getItemInHand(hand));
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Deploys: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal("MP-01 Trooper (" + TitanClass.TROOPER.getRole() + ")").withStyle(ChatFormatting.GREEN)));
        tooltip.add(Component.literal("Right-click ground: ").withStyle(ChatFormatting.GREEN)
                .append(Component.literal("Assemble & Deploy on Ground").withStyle(ChatFormatting.WHITE)));
    }
}
