package com.titancombat.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class TitanCoreModuleItem extends Item {
    public enum CoreType {
        CLOAKING("cloaking", "Active Optical Cloak", 300, 400),       // 15s duration, 20s cooldown
        PHASE_WARP("phase_warp", "Short-Range Phase Warp", 0, 160),    // Instant blink, 8s cooldown
        SONAR_SCANNER("sonar_scanner", "Tactical Pulse Sonar", 240, 200); // 12s duration, 10s cooldown

        private final String id;
        private final String displayName;
        private final int durationTicks;
        private final int cooldownTicks;

        CoreType(String id, String displayName, int durationTicks, int cooldownTicks) {
            this.id = id;
            this.displayName = displayName;
            this.durationTicks = durationTicks;
            this.cooldownTicks = cooldownTicks;
        }

        public String getId() {
            return id;
        }

        public String getDisplayName() {
            return displayName;
        }

        public int getDurationTicks() {
            return durationTicks;
        }

        public int getCooldownTicks() {
            return cooldownTicks;
        }
    }

    private final CoreType coreType;

    public TitanCoreModuleItem(CoreType coreType, Properties properties) {
        super(properties.stacksTo(1).rarity(Rarity.EPIC));
        this.coreType = coreType;
    }

    public CoreType getCoreType() {
        return coreType;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Core Function: ").withStyle(ChatFormatting.GRAY)
                .append(Component.literal(coreType.getDisplayName()).withStyle(ChatFormatting.AQUA)));
        tooltip.add(Component.literal("Back Equipment Slot (Slot 13)").withStyle(ChatFormatting.DARK_GRAY));
        tooltip.add(Component.literal("Key: [C] Defense or [V] Core to activate").withStyle(ChatFormatting.YELLOW));

        switch (coreType) {
            case CLOAKING -> tooltip.add(Component.literal("Renders Titan and pilot completely invisible, clearing hostile mob aggro.").withStyle(ChatFormatting.BLUE));
            case PHASE_WARP -> tooltip.add(Component.literal("Instantly teleports 14m forward through physical obstacles, evading attacks.").withStyle(ChatFormatting.LIGHT_PURPLE));
            case SONAR_SCANNER -> tooltip.add(Component.literal("Pings all enemies within 48m, outlining them through walls with glowing highlight.").withStyle(ChatFormatting.GREEN));
        }
    }
}
