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
        tooltip.add(Component.literal("§e • Space§7: Rocket Climb / Ascend"));
        tooltip.add(Component.literal("§e • Shift / Crouch§7: Descend"));
        tooltip.add(Component.literal("§e • W / Look Pitch§7: 3D Directional Vectoring"));
        tooltip.add(Component.literal("§6 • Sprint (Ctrl)§7: Gundam Supersonic Boost Dash"));
        tooltip.add(Component.literal("§8Install into Mech Back Equipment Slot via loadout menu."));
    }
}
