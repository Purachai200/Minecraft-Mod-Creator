package com.obsolete.item;

import com.obsolete.entity.inventory.ExoframeArmorSlot;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeArmorItem extends Item {
    private final ExoframeArmorSlot targetSlot;
    private final float damageReduction; // e.g. 0.35F = 35%
    private final String armorSeries;

    public ExoframeArmorItem(Properties properties, ExoframeArmorSlot targetSlot, float damageReduction, String armorSeries) {
        super(properties);
        this.targetSlot = targetSlot;
        this.damageReduction = damageReduction;
        this.armorSeries = armorSeries;
    }

    public ExoframeArmorSlot getTargetSlot() {
        return targetSlot;
    }

    public float getDamageReduction() {
        return damageReduction;
    }

    public String getArmorSeries() {
        return armorSeries;
    }

    @Override
    public boolean isDamageable(ItemStack stack) {
        return true;
    }

    @Override
    public boolean canBeDepleted() {
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.armor_slot", targetSlot.getName().toUpperCase())
                .withStyle(ChatFormatting.GOLD));
        tooltip.add(Component.translatable("tooltip.obsolete.damage_reduction", String.format("%.0f%%", damageReduction * 100))
                .withStyle(ChatFormatting.AQUA));
        tooltip.add(Component.translatable("tooltip.obsolete.durability", (stack.getMaxDamage() - stack.getDamageValue()), stack.getMaxDamage())
                .withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.armor_series", armorSeries)
                .withStyle(ChatFormatting.DARK_GRAY));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
