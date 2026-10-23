package com.youjosenki.flight;

import net.minecraftforge.common.ForgeConfigSpec;
import org.apache.commons.lang3.tuple.Pair;

public class Config {
    public static final Common COMMON;
    public static final ForgeConfigSpec COMMON_SPEC;

    static {
        Pair<Common, ForgeConfigSpec> specPair = new ForgeConfigSpec.Builder().configure(Common::new);
        COMMON = specPair.getLeft();
        COMMON_SPEC = specPair.getRight();
    }

    public static class Common {
        public final ForgeConfigSpec.IntValue maxEnergy;
        public final ForgeConfigSpec.IntValue maxReceive;
        public final ForgeConfigSpec.IntValue flightEnergyCost;
        public final ForgeConfigSpec.IntValue hoverEnergyCost;
        public final ForgeConfigSpec.IntValue sprintEnergyCost;
        public final ForgeConfigSpec.DoubleValue sprintSpeedMultiplier;
        public final ForgeConfigSpec.BooleanValue preventFallDamage;
        public final ForgeConfigSpec.BooleanValue spawnManaParticles;
        public final ForgeConfigSpec.BooleanValue spawnSmokeParticles;
        public final ForgeConfigSpec.IntValue smokeDensity;

        public Common(ForgeConfigSpec.Builder builder) {
            builder.comment("Youjo Senki: Aerial Mage Equipment Configuration v2.0")
                   .push("general");

            maxEnergy = builder
                    .comment("Maximum Forge Energy (FE) capacity stored in the flight unit.")
                    .defineInRange("maxEnergy", 500_000, 1_000, 100_000_000);

            maxReceive = builder
                    .comment("Maximum FE transfer rate allowed when charging.")
                    .defineInRange("maxReceive", 5_000, 10, 1_000_000);

            flightEnergyCost = builder
                    .comment("FE consumed per tick during active regular flight.")
                    .defineInRange("flightEnergyCost", 80, 0, 10_000);

            hoverEnergyCost = builder
                    .comment("FE consumed per tick while hovering in place.")
                    .defineInRange("hoverEnergyCost", 30, 0, 5_000);

            sprintEnergyCost = builder
                    .comment("FE consumed per tick while sprint boosting in the air.")
                    .defineInRange("sprintEnergyCost", 180, 0, 20_000);

            sprintSpeedMultiplier = builder
                    .comment("Velocity boost multiplier applied when sprint-flying.")
                    .defineInRange("sprintSpeedMultiplier", 1.4, 1.0, 5.0);

            preventFallDamage = builder
                    .comment("Whether wearing the flight unit prevents fall damage when energized.")
                    .define("preventFallDamage", true);

            spawnManaParticles = builder
                    .comment("Whether to emit cyan mana particles from the core and thrusters while flying.")
                    .define("spawnManaParticles", true);

            spawnSmokeParticles = builder
                    .comment("Whether to emit realistic turbine exhaust smoke from the foot thrusters.")
                    .define("spawnSmokeParticles", true);

            smokeDensity = builder
                    .comment("Exhaust smoke particle density (1 = light, 5 = heavy, 10 = extreme).")
                    .defineInRange("smokeDensity", 2, 1, 10);

            builder.pop();
        }
    }
}
