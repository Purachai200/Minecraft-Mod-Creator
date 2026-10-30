package com.obsolete.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeAmmoItem extends Item {
    public enum AmmoType {
        CALIBER_20MM("20mm AP Kinetic Shells", 64),
        CALIBER_762_MINIGUN("7.62x51mm Linked Ammo Belt", 128),
        AT_ROCKET("Anti-Tank Guided Missile", 16),
        HEAVY_RPG_WARHEAD("PG-7VR Tandem Warhead", 8),
        CALIBER_30MM("30mm High-Explosive Shells", 64),
        SHOTGUN_SLUG("8-Gauge Heavy Breaching Slugs", 64),
        GRENADE_40MM("40mm High-Explosive Grenade Rounds", 32),
        ROCKET_84MM("84mm HEAT Recoilless Rocket", 16),
        ATGM_MISSILE("Tandem-Warhead Guided ATGM Missile", 8),
        NAPALM_CANISTER("Liquid Napalm Canister", 16);

        private final String displayName;
        private final int defaultMaxStack;

        AmmoType(String displayName, int defaultMaxStack) {
            this.displayName = displayName;
            this.defaultMaxStack = defaultMaxStack;
        }

        public String getDisplayName() {
            return displayName;
        }

        public int getDefaultMaxStack() {
            return defaultMaxStack;
        }
    }

    private final AmmoType ammoType;

    public ExoframeAmmoItem(Properties properties, AmmoType ammoType) {
        super(properties.stacksTo(ammoType.getDefaultMaxStack()));
        this.ammoType = ammoType;
    }

    public AmmoType getAmmoType() {
        return ammoType;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.ammo_type", ammoType.getDisplayName())
                .withStyle(ChatFormatting.YELLOW));
        tooltip.add(Component.translatable("tooltip.obsolete.ammo_compatible")
                .withStyle(ChatFormatting.GRAY));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
