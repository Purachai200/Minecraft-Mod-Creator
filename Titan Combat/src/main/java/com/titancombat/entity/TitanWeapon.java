package com.titancombat.entity;

import com.titancombat.sound.ModSounds;
import net.minecraft.sounds.SoundEvent;

import java.util.function.Supplier;

/**
 * Titan primary weapons. Any chassis can mount any weapon (installed in the cockpit bay's weapon
 * slot); with the slot empty a titan uses its factory weapon. Each weapon has its own magazine,
 * reload time and dedicated ammunition.
 *
 * raiseTicks: how long the arm takes to bring the weapon up to firing position (Legion's spin-up
 * included) before the first round leaves the barrel.
 */
public enum TitanWeapon {
    //                 id                  factory chassis      mag  reload cd  dmg    speed spread pellets raise ignite boom
    SPLITTER_RIFLE("splitter_rifle", TitanClass.ION,       24,  50,  8,  30.0F, 2.8F, 0.05F, 1,  7,  0, 0.0F, ModSounds.ION_FIRE),
    THERMITE_LAUNCHER("thermite_launcher", TitanClass.SCORCH, 6, 70, 18, 45.0F, 2.0F, 0.1F, 1,  9, 10, 1.2F, ModSounds.SCORCH_FIRE),
    LEADWALL("leadwall", TitanClass.RONIN,                  8,  50, 12, 11.0F, 2.5F, 5.0F, 6,  6,  0, 0.0F, ModSounds.RONIN_FIRE),
    TRACKER_CANNON("tracker_cannon", TitanClass.TONE,      12,  60,  9, 38.0F, 3.0F, 0.0F, 1,  8,  0, 1.0F, ModSounds.TONE_FIRE),
    PREDATOR_CANNON("predator_cannon", TitanClass.LEGION, 100,  90,  3, 13.0F, 3.2F, 0.45F, 1, 16,  0, 0.0F, ModSounds.LEGION_FIRE),
    XO16_CHAINGUN("xo16_chaingun", TitanClass.MONARCH,     50,  55,  5, 18.0F, 2.8F, 0.15F, 1,  8,  0, 0.0F, ModSounds.MONARCH_FIRE),
    PLASMA_RAILGUN("plasma_railgun", TitanClass.NORTHSTAR,  6,  60, 25, 90.0F, 4.5F, 0.0F, 1, 12,  0, 0.0F, ModSounds.NORTHSTAR_FIRE);

    private final String id;
    private final TitanClass factoryChassis;
    private final int magazineSize;
    private final int reloadTicks;
    private final int cooldownTicks;
    private final float damage;
    private final float projectileSpeed;
    private final float spread;
    private final int pellets;
    private final int raiseTicks;
    private final int igniteSeconds;
    private final float explosionPower;
    private final Supplier<SoundEvent> fireSound;

    TitanWeapon(String id, TitanClass factoryChassis, int magazineSize, int reloadTicks, int cooldownTicks, float damage,
                float projectileSpeed, float spread, int pellets, int raiseTicks, int igniteSeconds, float explosionPower,
                Supplier<SoundEvent> fireSound) {
        this.id = id;
        this.factoryChassis = factoryChassis;
        this.magazineSize = magazineSize;
        this.reloadTicks = reloadTicks;
        this.cooldownTicks = cooldownTicks;
        this.damage = damage;
        this.projectileSpeed = projectileSpeed;
        this.spread = spread;
        this.pellets = pellets;
        this.raiseTicks = raiseTicks;
        this.igniteSeconds = igniteSeconds;
        this.explosionPower = explosionPower;
        this.fireSound = fireSound;
    }

    public String getId() { return id; }
    /** The chassis this weapon ships with; its model and first-person rig provide the visuals. */
    public TitanClass getFactoryChassis() { return factoryChassis; }
    public int getMagazineSize() { return magazineSize; }
    public int getReloadTicks() { return reloadTicks; }
    public int getCooldownTicks() { return cooldownTicks; }
    public float getDamage() { return damage; }
    public float getProjectileSpeed() { return projectileSpeed; }
    public float getSpread() { return spread; }
    public int getPellets() { return pellets; }
    public int getRaiseTicks() { return raiseTicks; }
    public int getIgniteSeconds() { return igniteSeconds; }
    public float getExplosionPower() { return explosionPower; }
    public SoundEvent getFireSound() { return fireSound.get(); }

    public String getTranslationKey() {
        return "weapon.titancombat." + id;
    }

    public static TitanWeapon factoryWeaponOf(TitanClass chassis) {
        for (TitanWeapon w : values()) {
            if (w.factoryChassis == chassis) return w;
        }
        return SPLITTER_RIFLE;
    }

    public static TitanWeapon byOrdinal(int ordinal) {
        TitanWeapon[] all = values();
        return ordinal >= 0 && ordinal < all.length ? all[ordinal] : SPLITTER_RIFLE;
    }
}
