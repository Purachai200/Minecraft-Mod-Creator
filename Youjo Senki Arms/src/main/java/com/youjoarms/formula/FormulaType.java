package com.youjoarms.formula;

import com.youjoarms.config.YoujoArmsConfig;

/**
 * Formulas in cast order. {@code rings} is how many magic circles stack in front of the muzzle at full charge:
 * stronger formulas stack more, bigger circles.
 */
public enum FormulaType {
    NONE(0, "None", 0, 0xFF888888),
    EXPLOSIVE(1, "Explosion", 1, 0xFFFF5A1F),
    PIERCING(2, "Penetration", 2, 0xFF00E5FF),
    SHIELD(3, "Defensive Shell", 2, 0xFF7CFFB2),
    BARRAGE(4, "Barrage", 3, 0xFFB46CFF),
    AREA(5, "Area Suppression", 4, 0xFFFF2E63),
    ARTILLERY(6, "Artillery", 5, 0xFFFFD23F),
    ULTIMATE(7, "Annihilation", 6, 0xFFFFB627);

    private final int id;
    private final String displayName;
    private final int rings;
    private final int circleColor; // ARGB

    FormulaType(int id, String displayName, int rings, int circleColor) {
        this.id = id;
        this.displayName = displayName;
        this.rings = rings;
        this.circleColor = circleColor;
    }

    public int getId() {
        return id;
    }

    public String getDisplayName() {
        return displayName;
    }

    public int getRings() {
        return rings;
    }

    public int getCircleColor() {
        return circleColor;
    }

    public int getManaCost() {
        var c = YoujoArmsConfig.COMMON;
        return switch (this) {
            case EXPLOSIVE -> c.explosiveManaCost.get();
            case PIERCING -> c.piercingManaCost.get();
            case SHIELD -> c.shieldManaCost.get();
            case BARRAGE -> c.barrageManaCost.get();
            case AREA -> c.areaManaCost.get();
            case ARTILLERY -> c.artilleryManaCost.get();
            case ULTIMATE -> c.ultimateManaCost.get();
            default -> 0;
        };
    }

    public int getChargeTicks() {
        var c = YoujoArmsConfig.COMMON;
        return switch (this) {
            case EXPLOSIVE -> c.explosiveChargeTicks.get();
            case PIERCING -> c.piercingChargeTicks.get();
            case SHIELD -> c.shieldChargeTicks.get();
            case BARRAGE -> c.barrageChargeTicks.get();
            case AREA -> c.areaChargeTicks.get();
            case ARTILLERY -> c.artilleryChargeTicks.get();
            case ULTIMATE -> c.ultimateChargeTicks.get();
            default -> 0;
        };
    }

    public FormulaType next() {
        FormulaType[] values = values();
        return values[(this.ordinal() + 1) % values.length];
    }

    public static FormulaType byId(int id) {
        for (FormulaType f : values()) {
            if (f.id == id) return f;
        }
        return NONE;
    }
}
