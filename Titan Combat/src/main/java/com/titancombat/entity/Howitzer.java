package com.titancombat.entity;

/**
 * M-120 back-mounted howitzer: a skill module in the titan's back equipment slot (where a flight module
 * would go), fired on its own key while the titan keeps its hand weapon. Shells come from racks
 * (ModItems.HOWITZER_SHELLS) in the titan bay or the pilot's inventory.
 */
public final class Howitzer {
    public static final int MIN_RANGE = 24;
    /** Kept inside default simulation distance: shells flying into unticked chunks would hang in the air. */
    public static final int MAX_RANGE = 160;
    public static final int RANGE_STEP = 8;
    public static final int ROUNDS_PER_RACK = 4;
    public static final int RELOAD_TICKS = 90;
    public static final int COOLDOWN_TICKS = 40;
    public static final int LAYING_TICKS = 30;
    public static final float DAMAGE = 40.0F;
    public static final float EXPLOSION = 3.0F;

    private Howitzer() {}
}
