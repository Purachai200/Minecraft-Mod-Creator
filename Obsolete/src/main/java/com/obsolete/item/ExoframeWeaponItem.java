package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

public abstract class ExoframeWeaponItem extends Item {
    private final int fireCooldownTicks;
    private final String weaponModelName;

    public ExoframeWeaponItem(Properties properties, int fireCooldownTicks, String weaponModelName) {
        super(properties);
        this.fireCooldownTicks = fireCooldownTicks;
        this.weaponModelName = weaponModelName;
    }

    public int getFireCooldownTicks() {
        return fireCooldownTicks;
    }

    public String getWeaponModelName() {
        return weaponModelName;
    }

    /**
     * Checks if ammunition exists in either Exoframe's utility slots or pilot's inventory.
     * If consume is true, decrements 1 ammo item.
     */
    public abstract boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume);

    /**
     * Executes the weapon firing logic server-side.
     */
    public abstract boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot);
}
