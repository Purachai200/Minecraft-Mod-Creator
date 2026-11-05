package com.youjoarms.config;

import net.minecraftforge.common.ForgeConfigSpec;

public class YoujoArmsConfig {
    public static final ForgeConfigSpec COMMON_SPEC;
    public static final Common COMMON;

    static {
        ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();
        COMMON = new Common(builder);
        COMMON_SPEC = builder.build();
    }

    public static class Common {
        public final ForgeConfigSpec.IntValue maxMana;
        public final ForgeConfigSpec.IntValue manaRegenPerSecond;

        // Formula costs & charge times
        public final ForgeConfigSpec.IntValue explosiveManaCost;
        public final ForgeConfigSpec.IntValue explosiveChargeTicks;
        public final ForgeConfigSpec.DoubleValue explosiveRadius;
        public final ForgeConfigSpec.BooleanValue explosiveBlockDamage;

        public final ForgeConfigSpec.IntValue piercingManaCost;
        public final ForgeConfigSpec.IntValue piercingChargeTicks;
        public final ForgeConfigSpec.DoubleValue piercingDamageMultiplier;

        public final ForgeConfigSpec.IntValue artilleryManaCost;
        public final ForgeConfigSpec.IntValue artilleryChargeTicks;
        public final ForgeConfigSpec.DoubleValue artilleryExplosionRadius;
        public final ForgeConfigSpec.BooleanValue artilleryBlockDamage;

        public final ForgeConfigSpec.IntValue shieldManaCost;
        public final ForgeConfigSpec.IntValue shieldChargeTicks;
        public final ForgeConfigSpec.IntValue shieldDurationTicks;
        public final ForgeConfigSpec.DoubleValue shieldDamageReduction;

        public final ForgeConfigSpec.IntValue barrageManaCost;
        public final ForgeConfigSpec.IntValue barrageChargeTicks;
        public final ForgeConfigSpec.IntValue barrageBolts;
        public final ForgeConfigSpec.DoubleValue barrageBoltDamage;

        public final ForgeConfigSpec.IntValue areaManaCost;
        public final ForgeConfigSpec.IntValue areaChargeTicks;
        public final ForgeConfigSpec.DoubleValue areaRadius;
        public final ForgeConfigSpec.DoubleValue areaDamage;

        public final ForgeConfigSpec.IntValue ultimateManaCost;
        public final ForgeConfigSpec.IntValue ultimateChargeTicks;
        public final ForgeConfigSpec.DoubleValue ultimateRadius;
        public final ForgeConfigSpec.BooleanValue ultimateBlockDamage;

        public Common(ForgeConfigSpec.Builder builder) {
            builder.push("mana");
            maxMana = builder.comment("Maximum mana capacity").defineInRange("maxMana", 100, 10, 1000);
            manaRegenPerSecond = builder.comment("Mana regenerated per second").defineInRange("manaRegenPerSecond", 5, 0, 100);
            builder.pop();

            builder.push("formulas");

            builder.push("explosive");
            explosiveManaCost = builder.comment("Mana cost for Explosive Formula").defineInRange("manaCost", 25, 0, 1000);
            explosiveChargeTicks = builder.comment("Ticks to charge Explosive Formula (20 ticks = 1s)").defineInRange("chargeTicks", 15, 1, 200);
            explosiveRadius = builder.comment("Explosion radius on bullet hit").defineInRange("radius", 2.2D, 0.5D, 10.0D);
            explosiveBlockDamage = builder.comment("Whether explosive formula breaks blocks").define("blockDamage", false);
            builder.pop();

            builder.push("piercing");
            piercingManaCost = builder.comment("Mana cost for Piercing Formula").defineInRange("manaCost", 20, 0, 1000);
            piercingChargeTicks = builder.comment("Ticks to charge Piercing Formula").defineInRange("chargeTicks", 10, 1, 200);
            piercingDamageMultiplier = builder.comment("Damage multiplier for Piercing Formula").defineInRange("damageMultiplier", 1.6D, 1.0D, 10.0D);
            builder.pop();

            builder.push("artillery");
            artilleryManaCost = builder.comment("Mana cost for Artillery Formula").defineInRange("manaCost", 50, 0, 1000);
            artilleryChargeTicks = builder.comment("Ticks to charge Artillery Formula").defineInRange("chargeTicks", 30, 1, 200);
            artilleryExplosionRadius = builder.comment("Artillery shell explosion radius").defineInRange("radius", 4.5D, 1.0D, 20.0D);
            artilleryBlockDamage = builder.comment("Whether artillery shells break blocks").define("blockDamage", false);
            builder.pop();

            builder.push("shield");
            shieldManaCost = builder.comment("Mana cost for the Defensive Shell").defineInRange("manaCost", 30, 0, 1000);
            shieldChargeTicks = builder.comment("Ticks to charge the Defensive Shell").defineInRange("chargeTicks", 15, 1, 200);
            shieldDurationTicks = builder.comment("How long the shell lasts").defineInRange("durationTicks", 200, 20, 2400);
            shieldDamageReduction = builder.comment("Fraction of incoming damage the shell absorbs").defineInRange("damageReduction", 0.8D, 0.0D, 1.0D);
            builder.pop();

            builder.push("barrage");
            barrageManaCost = builder.comment("Mana cost for Barrage").defineInRange("manaCost", 35, 0, 1000);
            barrageChargeTicks = builder.comment("Ticks to charge Barrage").defineInRange("chargeTicks", 20, 1, 200);
            barrageBolts = builder.comment("Magic bolts fired in a fan").defineInRange("bolts", 7, 1, 32);
            barrageBoltDamage = builder.comment("Damage per bolt").defineInRange("boltDamage", 7.0D, 0.0D, 100.0D);
            builder.pop();

            builder.push("area");
            areaManaCost = builder.comment("Mana cost for Area Suppression").defineInRange("manaCost", 45, 0, 1000);
            areaChargeTicks = builder.comment("Ticks to charge Area Suppression").defineInRange("chargeTicks", 25, 1, 200);
            areaRadius = builder.comment("Radius of the ground circle blast").defineInRange("radius", 6.0D, 1.0D, 32.0D);
            areaDamage = builder.comment("Damage to everything inside the circle").defineInRange("damage", 16.0D, 0.0D, 200.0D);
            builder.pop();

            builder.push("ultimate");
            ultimateManaCost = builder.comment("Mana cost for Annihilation").defineInRange("manaCost", 100, 0, 1000);
            ultimateChargeTicks = builder.comment("Ticks to charge Annihilation").defineInRange("chargeTicks", 80, 1, 600);
            ultimateRadius = builder.comment("Blast radius").defineInRange("radius", 9.0D, 1.0D, 32.0D);
            ultimateBlockDamage = builder.comment("Whether Annihilation breaks blocks").define("blockDamage", false);
            builder.pop();

            builder.pop();
        }
    }
}
