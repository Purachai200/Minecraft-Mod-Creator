package com.titancombat.entity;

/**
 * Modular flight systems that can be installed on any titan chassis.
 * Physics and fuel drain dynamically scale with each chassis' weight class.
 */
public enum TitanFlightModule {
    NONE("none", "None", 0.0F, 1.0F, 0.0F, 0.0F),
    DRONE_LIFTER("drone_lifter", "Heavy Lifter Quad-Drone", 0.32F, 1.15F, 0.42F, 28.0F),
    ROCKET_JETPACK("rocket_jetpack", "Heavy Jump-Jetpack", 0.40F, 1.45F, 0.65F, 32.0F),
    VTOL_GLIDE("vtol_glide", "VTOL Aero-Glide Wings", 0.26F, 1.65F, 0.32F, 24.0F);

    private final String id;
    private final String displayName;
    private final float verticalLift;      // Base climb rate (blocks/tick)
    private final float forwardMultiplier; // Air cruising speed multiplier
    private final float energyDrain;       // Base fuel/battery charge drain per tick
    private final float maxFlightCeiling;  // Maximum altitude above terrain (blocks)

    TitanFlightModule(String id, String displayName, float verticalLift, float forwardMultiplier, float energyDrain, float maxFlightCeiling) {
        this.id = id;
        this.displayName = displayName;
        this.verticalLift = verticalLift;
        this.forwardMultiplier = forwardMultiplier;
        this.energyDrain = energyDrain;
        this.maxFlightCeiling = maxFlightCeiling;
    }

    public String getId() { return id; }
    public String getDisplayName() { return displayName; }
    public float getVerticalLift() { return verticalLift; }
    public float getForwardMultiplier() { return forwardMultiplier; }
    public float getEnergyDrain() { return energyDrain; }
    public float getMaxFlightCeiling() { return maxFlightCeiling; }

    public static TitanFlightModule byOrdinal(int ord) {
        TitanFlightModule[] all = values();
        return ord >= 0 && ord < all.length ? all[ord] : NONE;
    }

    public static TitanFlightModule byId(String id) {
        for (TitanFlightModule m : values()) {
            if (m.id.equalsIgnoreCase(id)) return m;
        }
        return NONE;
    }

    public String getGeoPath() {
        return switch (this) {
            case DRONE_LIFTER -> "geo/flight/drone_lifter.geo.json";
            case ROCKET_JETPACK -> "geo/flight/rocket_jetpack.geo.json";
            case VTOL_GLIDE -> "geo/flight/vtol_glide.geo.json";
            default -> "";
        };
    }

    public String getTexturePath() {
        return switch (this) {
            case DRONE_LIFTER -> "textures/entity/flight/drone_lifter.png";
            case ROCKET_JETPACK -> "textures/entity/flight/rocket_jetpack.png";
            case VTOL_GLIDE -> "textures/entity/flight/vtol_glide.png";
            default -> "";
        };
    }
}
