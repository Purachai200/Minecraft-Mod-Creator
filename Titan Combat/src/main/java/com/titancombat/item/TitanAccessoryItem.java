package com.titancombat.item;

import com.titancombat.TitanConfig;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Module for the titan bay's MOD accessory slot; strengths come from the server config. */
public class TitanAccessoryItem extends Item {
    public enum Type {
        OVERDRIVE,   // faster walk and run
        PLATING,     // less incoming damage
        CAPACITOR,   // bigger shield
        NANITE,      // hull self-repair
        TARGETING;   // more weapon damage

        /** The config value shown in the tooltip, as a whole number. */
        long amount() {
            return switch (this) {
                case OVERDRIVE -> Math.round(TitanConfig.overdriveBonus() * 100);
                case PLATING -> Math.round(TitanConfig.platingReduction() * 100);
                case CAPACITOR -> Math.round(TitanConfig.capacitorBonus() * 100);
                case NANITE -> Math.round(TitanConfig.naniteRepair());
                case TARGETING -> Math.round(TitanConfig.targetingBonus() * 100);
            };
        }
    }

    private final Type type;

    public TitanAccessoryItem(Type type, Properties properties) {
        super(properties);
        this.type = type;
    }

    public Type getType() {
        return type;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable(this.getDescriptionId() + ".desc", type.amount()).withStyle(ChatFormatting.GREEN));
        tooltip.add(Component.translatable("item.titancombat.accessory.slot").withStyle(ChatFormatting.GRAY));
    }
}
