package com.titancombat;

import com.titancombat.entity.TitanClass;
import com.titancombat.entity.TitanWeapon;
import net.minecraftforge.common.ForgeConfigSpec;

import java.util.EnumMap;
import java.util.Locale;
import java.util.Map;

/**
 * Server config (saves/&lt;world&gt;/serverconfig/titancombat-server.toml, synced to clients so piloting and HUDs agree):
 * global multipliers, every mech's stats and every weapon's damage and handling. Put an edited copy in
 * defaultconfigs/ to apply it to new worlds. Until the config loads (main menu, registration) the built-in values apply.
 */
public final class TitanConfig {
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.DoubleValue SPEED_MULTIPLIER;
    public static final ForgeConfigSpec.DoubleValue HEALTH_MULTIPLIER;
    public static final ForgeConfigSpec.DoubleValue DAMAGE_MULTIPLIER;
    public static final ForgeConfigSpec.DoubleValue OVERDRIVE_BONUS;
    public static final ForgeConfigSpec.DoubleValue PLATING_REDUCTION;
    public static final ForgeConfigSpec.DoubleValue CAPACITOR_BONUS;
    public static final ForgeConfigSpec.DoubleValue NANITE_REPAIR;
    public static final ForgeConfigSpec.DoubleValue TARGETING_BONUS;

    private record MechStats(ForgeConfigSpec.DoubleValue health, ForgeConfigSpec.DoubleValue shield,
                             ForgeConfigSpec.DoubleValue speed, ForgeConfigSpec.DoubleValue melee) {}

    private record WeaponStats(ForgeConfigSpec.DoubleValue damage, ForgeConfigSpec.IntValue magazine,
                               ForgeConfigSpec.IntValue reload, ForgeConfigSpec.IntValue cooldown) {}

    private static final Map<TitanClass, MechStats> MECHS = new EnumMap<>(TitanClass.class);
    private static final Map<TitanWeapon, WeaponStats> WEAPONS = new EnumMap<>(TitanWeapon.class);

    /** Every chassis shipped with a flat 100 shield; the per-class shield numbers were never wired up. */
    private static final double DEFAULT_SHIELD = 100.0D;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();
        b.comment("Global multipliers applied on top of the per-mech and per-weapon values below.").push("global");
        SPEED_MULTIPLIER = b.comment("Walking and running speed of every mech. 1.0 = the original 2.x speed.")
                .defineInRange("speedMultiplier", 1.25D, 0.25D, 3.0D);
        HEALTH_MULTIPLIER = b.comment("Max health of every mech.").defineInRange("healthMultiplier", 1.0D, 0.1D, 10.0D);
        DAMAGE_MULTIPLIER = b.comment("Damage of every mech weapon.").defineInRange("damageMultiplier", 1.0D, 0.0D, 10.0D);
        OVERDRIVE_BONUS = b.comment("Extra speed from a Servo Overdrive Module in the accessory slot (0.35 = +35%).")
                .defineInRange("servoOverdriveBonus", 0.35D, 0.0D, 2.0D);
        PLATING_REDUCTION = b.comment("Reinforced Plating Module: share of incoming damage blocked (0.25 = -25%).")
                .defineInRange("reinforcedPlatingReduction", 0.25D, 0.0D, 0.9D);
        CAPACITOR_BONUS = b.comment("Shield Capacitor Module: extra max shield (0.5 = +50%).")
                .defineInRange("shieldCapacitorBonus", 0.5D, 0.0D, 5.0D);
        NANITE_REPAIR = b.comment("Nanite Repair Module: hull points repaired per second.")
                .defineInRange("naniteRepairPerSecond", 2.0D, 0.0D, 100.0D);
        TARGETING_BONUS = b.comment("Targeting Computer Module: extra weapon damage (0.2 = +20%).")
                .defineInRange("targetingComputerBonus", 0.2D, 0.0D, 5.0D);
        b.pop();

        b.comment("Per-mech stats. speed is the base movement value (blocks/tick scale, Ion = 0.32).").push("mechs");
        for (TitanClass c : TitanClass.values()) {
            b.push(c.getId());
            MECHS.put(c, new MechStats(
                    b.defineInRange("maxHealth", c.getBaseMaxHealth(), 1.0D, 100000.0D),
                    b.defineInRange("maxShield", DEFAULT_SHIELD, 0.0D, 100000.0D),
                    b.defineInRange("speed", c.getBaseMoveSpeed(), 0.01D, 2.0D),
                    b.defineInRange("meleeDamage", c.getBaseAttackDamage(), 0.0D, 10000.0D)));
            b.pop();
        }
        b.pop();

        b.comment("Per-weapon stats. Ticks: 20 = 1 second.").push("weapons");
        for (TitanWeapon w : TitanWeapon.values()) {
            b.push(w.getId().toLowerCase(Locale.ROOT));
            WEAPONS.put(w, new WeaponStats(
                    b.defineInRange("damage", (double) w.getBaseDamage(), 0.0D, 10000.0D),
                    b.defineInRange("magazineSize", w.getBaseMagazineSize(), 1, 10000),
                    b.defineInRange("reloadTicks", w.getBaseReloadTicks(), 0, 2000),
                    b.defineInRange("fireCooldownTicks", w.getBaseCooldownTicks(), 0, 2000)));
            b.pop();
        }
        b.pop();
        SPEC = b.build();
    }

    private TitanConfig() {}

    private static boolean loaded() {
        return SPEC.isLoaded();
    }

    public static double speedMultiplier() {
        return loaded() ? SPEED_MULTIPLIER.get() : 1.0D;
    }

    public static double overdriveBonus() {
        return loaded() ? OVERDRIVE_BONUS.get() : 0.35D;
    }

    public static double platingReduction() {
        return loaded() ? PLATING_REDUCTION.get() : 0.25D;
    }

    public static double capacitorBonus() {
        return loaded() ? CAPACITOR_BONUS.get() : 0.5D;
    }

    public static double naniteRepair() {
        return loaded() ? NANITE_REPAIR.get() : 2.0D;
    }

    public static double targetingBonus() {
        return loaded() ? TARGETING_BONUS.get() : 0.2D;
    }

    public static double maxHealth(TitanClass c) {
        return loaded() ? MECHS.get(c).health().get() * HEALTH_MULTIPLIER.get() : c.getBaseMaxHealth();
    }

    public static float maxShield(TitanClass c) {
        return loaded() ? MECHS.get(c).shield().get().floatValue() : (float) DEFAULT_SHIELD;
    }

    public static double moveSpeed(TitanClass c) {
        return loaded() ? MECHS.get(c).speed().get() : c.getBaseMoveSpeed();
    }

    public static double meleeDamage(TitanClass c) {
        return loaded() ? MECHS.get(c).melee().get() : c.getBaseAttackDamage();
    }

    public static float damage(TitanWeapon w) {
        return loaded() ? (float) (WEAPONS.get(w).damage().get() * DAMAGE_MULTIPLIER.get()) : w.getBaseDamage();
    }

    public static int magazineSize(TitanWeapon w) {
        return loaded() ? WEAPONS.get(w).magazine().get() : w.getBaseMagazineSize();
    }

    public static int reloadTicks(TitanWeapon w) {
        return loaded() ? WEAPONS.get(w).reload().get() : w.getBaseReloadTicks();
    }

    public static int cooldownTicks(TitanWeapon w) {
        return loaded() ? WEAPONS.get(w).cooldown().get() : w.getBaseCooldownTicks();
    }
}
