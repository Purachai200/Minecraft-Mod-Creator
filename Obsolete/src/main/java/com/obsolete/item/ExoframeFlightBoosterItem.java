package com.obsolete.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeFlightBoosterItem extends Item {
    private final String boosterDescription;

    public ExoframeFlightBoosterItem(Properties properties, String boosterDescription) {
        super(properties);
        this.boosterDescription = boosterDescription;
    }

    public String getBoosterDescription() {
        return boosterDescription;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("§b▶ Mech Back Module: §f" + boosterDescription));
        tooltip.add(Component.literal("§7Enables Gundam 3D Aerial Free Flight:"));
        tooltip.add(Component.literal("§e • Space (in air)§7: Hover / Rocket Climb"));
        tooltip.add(Component.literal("§e • C (Mech Crouch)§7: Descend / Land"));
        tooltip.add(Component.literal("§e • Pitch Down / W§7: Flight Vectoring & Dive"));
        tooltip.add(Component.literal("§6 • Sprint (Ctrl)§7: Gundam Supersonic Boost Dash"));
        tooltip.add(Component.literal("§7 • Shift§8: Dismount Cockpit (on ground only)"));
        tooltip.add(Component.literal("§8Install into Mech Back Equipment Slot via loadout menu."));
    }
}
