package com.titancombat.entity;

public enum TitanClass {
    // Gait numbers were measured from each walk.leg / move.leg animation (see tools/model_viewer.html):
    // how far a planted foot travels per second at 1x playback. Cockpit numbers are the pilot eye
    // position (height above the feet, distance forward of the hips) when standing and kneeling.
    ION("ion", "Ion", "Energy Assault", 350.0D, 100.0F, 0.32D, 25.0D, 2.6F, 4.8F,
            4.7F, 5.3F, 5.86F, 0.75F, 4.26F, 2.10F),
    SCORCH("scorch", "Scorch", "Incendiary Siege", 480.0D, 120.0F, 0.25D, 35.0D, 2.8F, 5.0F,
            5.4F, 8.5F, 5.46F, 0.85F, 4.27F, 1.25F),
    RONIN("ronin", "Ronin", "High-Speed Striker", 240.0D, 80.0F, 0.38D, 45.0D, 2.4F, 4.6F,
            3.9F, 8.0F, 6.34F, 0.50F, 4.08F, 0.90F),
    TONE("tone", "Tone", "Missile Tracker", 350.0D, 100.0F, 0.32D, 28.0D, 2.6F, 4.8F,
            5.4F, 6.4F, 5.96F, 0.50F, 4.23F, 2.00F),
    LEGION("legion", "Legion", "Super-Heavy Juggernaut", 550.0D, 150.0F, 0.23D, 30.0D, 3.0F, 5.2F,
            4.2F, 7.2F, 5.48F, 0.50F, 4.48F, 1.10F),
    MONARCH("monarch", "Monarch", "Vanguard Support", 350.0D, 120.0F, 0.33D, 26.0D, 2.6F, 4.8F,
            5.6F, 6.9F, 6.01F, 0.20F, 4.44F, 1.90F),
    NORTHSTAR("northstar", "Northstar", "Precision Sniper", 240.0D, 80.0F, 0.36D, 60.0D, 2.4F, 4.6F,
            4.3F, 8.4F, 6.30F, 0.45F, 4.37F, 0.95F),
    TROOPER("trooper", "Trooper", "Mass-Production Combat Frame", 240.0D, 60.0F, 0.29D, 20.0D, 2.5F, 4.6F,
            4.8F, 6.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    // Shares the Trooper skeleton (same joints, gait and cockpit), on a lighter, faster frame.
    SCOUT("scout", "Scout", "Fast Recon Frame", 180.0D, 50.0F, 0.40D, 16.0D, 2.3F, 4.6F,
            4.8F, 6.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    // Mass-produced cloaked infiltrator, also on the Trooper skeleton; Defense key toggles the cloak.
    SHADE("shade", "Shade", "Cloaked Infiltrator Frame", 200.0D, 70.0F, 0.34D, 18.0D, 2.4F, 4.6F,
            4.8F, 6.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    // Heavy mass-production frame on the Trooper skeleton: an armoured vehicle that walks (MP-07 Bulwark).
    BULWARK("bulwark", "Bulwark", "Heavy Mass-Production Frame", 300.0D, 90.0F, 0.27D, 24.0D, 2.6F, 4.6F,
            4.8F, 6.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    // Mass-production exoskeleton (MP-05): a bare strut frame that wears the modular armour sets.
    EXO_FRAME("exo_frame", "Exo Frame", "Mass-Production Exoskeleton", 260.0D, 70.0F, 0.33D, 22.0D, 2.5F, 4.6F,
            4.8F, 6.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    // The MP-05 inner frame wearing the real titans as armour (each archetype is one titan's shell).
    TITAN_EXO("titan_exo", "Titan Exo", "Titan-Armour Exoskeleton", 280.0D, 80.0F, 0.33D, 24.0D, 2.5F, 4.6F,
            4.8F, 6.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    // Modular Titan Frames: starting bare, accepting modular armor attachments
    STRIKER_FRAME("striker_frame", "Striker Frame", "Agile Modular Frame", 220.0D, 60.0F, 0.38D, 22.0D, 2.4F, 4.6F,
            4.8F, 7.2F, 5.70F, 0.50F, 4.10F, 1.40F),
    VANGUARD_FRAME("vanguard_frame", "Vanguard Frame", "Medium Modular Frame", 320.0D, 100.0F, 0.31D, 28.0D, 2.6F, 4.8F,
            4.8F, 6.4F, 5.70F, 0.50F, 4.10F, 1.40F),
    COLOSSUS_FRAME("colossus_frame", "Colossus Frame", "Heavy Modular Frame", 480.0D, 140.0F, 0.24D, 35.0D, 2.9F, 5.1F,
            4.2F, 5.6F, 5.70F, 0.50F, 4.10F, 1.40F),
    TERRAIN_FRAME("terrain_frame", "Terrain Frame", "Tactical Ground Frame", 380.0D, 110.0F, 0.28D, 26.0D, 2.6F, 4.8F,
            4.8F, 6.4F, 5.70F, 0.50F, 4.10F, 1.40F),
    CYCLOPS_FRAME("cyclops_frame", "Cyclops Frame", "Industrial Enforcer Frame", 440.0D, 130.0F, 0.25D, 32.0D, 2.8F, 4.9F,
            4.4F, 5.8F, 5.50F, 0.60F, 4.00F, 1.30F),
    SPIDER_FRAME("spider_frame", "Spider Frame", "Heavy Anti-Tank Hexapod", 420.0D, 120.0F, 0.30D, 30.0D, 4.8F, 4.3F,
            5.0F, 7.0F, 3.24F, -1.08F, 2.84F, -1.08F);

    private final String id;
    private final String displayName;
    private final String role;
    private final double maxHealth;
    private final float maxShield;
    private final double moveSpeed;
    private final double attackDamage;
    private final float width;
    private final float height;
    private final float walkGaitSpeed;
    private final float runGaitSpeed;
    private final float cockpitEyeY;
    private final float cockpitForward;
    private final float kneelEyeY;
    private final float kneelForward;

    TitanClass(String id, String displayName, String role, double maxHealth, float maxShield, double moveSpeed, double attackDamage, float width, float height,
               float walkGaitSpeed, float runGaitSpeed, float cockpitEyeY, float cockpitForward, float kneelEyeY, float kneelForward) {
        this.id = id;
        this.displayName = displayName;
        this.role = role;
        this.maxHealth = maxHealth;
        this.maxShield = maxShield;
        this.moveSpeed = moveSpeed;
        this.attackDamage = attackDamage;
        this.width = width;
        this.height = height;
        this.walkGaitSpeed = walkGaitSpeed;
        this.runGaitSpeed = runGaitSpeed;
        this.cockpitEyeY = cockpitEyeY;
        this.cockpitForward = cockpitForward;
        this.kneelEyeY = kneelEyeY;
        this.kneelForward = kneelForward;
    }

    public String getId() {
        return id;
    }

    public float getWeightMultiplier() {
        return switch (this) {
            case RONIN, NORTHSTAR -> 0.75F;
            case ION, TONE, MONARCH, TROOPER -> 1.0F;
            case SCOUT -> 0.7F;
            case SHADE -> 0.85F;
            case BULWARK -> 1.2F;
            case EXO_FRAME -> 0.85F;
            case TITAN_EXO -> 1.0F;
            case STRIKER_FRAME -> 0.75F;
            case VANGUARD_FRAME -> 1.0F;
            case COLOSSUS_FRAME, SCORCH, LEGION -> 1.45F;
            case TERRAIN_FRAME -> 1.15F;
            case CYCLOPS_FRAME -> 1.35F;
            case SPIDER_FRAME -> 0.95F;
        };
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getRole() {
        return role;
    }

    /** Live values from the server config (TitanConfig); the getBase* values are the built-in defaults. */
    public double getMaxHealth() {
        return com.titancombat.TitanConfig.maxHealth(this);
    }

    public float getMaxShield() {
        return com.titancombat.TitanConfig.maxShield(this);
    }

    public double getMoveSpeed() {
        return com.titancombat.TitanConfig.moveSpeed(this) * com.titancombat.TitanConfig.speedMultiplier();
    }

    public double getAttackDamage() {
        return com.titancombat.TitanConfig.meleeDamage(this);
    }

    public double getBaseMaxHealth() {
        return maxHealth;
    }

    public double getBaseMoveSpeed() {
        return moveSpeed;
    }

    public double getBaseAttackDamage() {
        return attackDamage;
    }

    public float getWidth() {
        return width;
    }

    public float getHeight() {
        return height;
    }

    /** Ground speed (blocks/second) that matches walk.leg at 1x playback. */
    public float getWalkGaitSpeed() {
        return walkGaitSpeed;
    }

    /** Ground speed (blocks/second) that matches move.leg (sprint) at 1x playback. */
    public float getRunGaitSpeed() {
        return runGaitSpeed;
    }

    public float getCockpitEyeY(boolean kneeling) {
        return kneeling ? kneelEyeY : cockpitEyeY;
    }

    public float getCockpitForward(boolean kneeling) {
        return kneeling ? kneelForward : cockpitForward;
    }

    /**
     * Jump-jet nozzle exit in blocks from the titan's feet: {sideways, up, backwards}.
     * Derived from each chassis' body3 pivot plus TitanFlightModuleLayer's jetpack mount; keep the two in sync.
     */
    public double[] getJetpackNozzle() {
        return switch (this) {
            case MONARCH -> new double[]{0.60D, 5.48D, 2.39D};
            case ION -> new double[]{0.60D, 4.97D, 2.44D};
            case LEGION -> new double[]{0.70D, 4.55D, 3.54D};
            case SCORCH -> new double[]{0.70D, 4.52D, 4.38D};
            case RONIN -> new double[]{0.55D, 5.61D, 2.02D};
            case NORTHSTAR -> new double[]{0.55D, 5.74D, 2.00D};
            case TONE -> new double[]{0.60D, 5.23D, 2.41D};
            case TROOPER -> new double[]{0.60D, 4.71D, 1.69D};
            case SCOUT -> new double[]{0.60D, 4.45D, 1.41D};
            case SHADE -> new double[]{0.60D, 4.58D, 1.30D};
            case BULWARK -> new double[]{0.60D, 4.71D, 1.80D};
            case EXO_FRAME, TITAN_EXO -> new double[]{0.60D, 4.71D, 1.69D};
            case STRIKER_FRAME -> new double[]{0.55D, 4.60D, 1.50D};
            case VANGUARD_FRAME -> new double[]{0.60D, 4.75D, 1.70D};
            case COLOSSUS_FRAME -> new double[]{0.70D, 4.80D, 2.20D};
            case TERRAIN_FRAME -> new double[]{0.60D, 4.75D, 1.70D};
            case CYCLOPS_FRAME -> new double[]{0.68D, 4.80D, 2.10D};
            case SPIDER_FRAME -> new double[]{1.00D, 3.38D, 1.62D};
        };
    }

    /** Walking speed relative to Ion, used to scale movement per chassis. */
    public float getAgility() {
        return (float) (getMoveSpeed() / 0.32D);
    }

    // Desired ground speeds (blocks/second) for an Ion-class chassis; others scale by agility.
    private static final float BASE_WALK_SPEED = 5.5F;
    private static final float BASE_RUN_SPEED = 8.5F;

    /**
     * Animation playback rate for walking. Movement speed is derived from it (see getWalkSpeed)
     * so the feet never slide: the chassis always covers exactly one stride per step.
     */
    public float getWalkPlayback() {
        return clampPlayback(BASE_WALK_SPEED * getAgility() / walkGaitSpeed);
    }

    public float getRunPlayback() {
        return clampPlayback(BASE_RUN_SPEED * getAgility() / runGaitSpeed);
    }

    /** Walking ground speed in blocks per tick. */
    public double getWalkSpeed() {
        return walkGaitSpeed * getWalkPlayback() / 20.0D;
    }

    /** Sprinting ground speed in blocks per tick. */
    public double getRunSpeed() {
        return runGaitSpeed * getRunPlayback() / 20.0D;
    }

    /**
     * How far (blocks) the planted foot dips below the ground in this chassis' walk/run clips,
     * measured in tools/model_viewer.html. The renderer lifts the model by this much while moving.
     */
    public float getFootSink(boolean running) {
        return switch (this) {
            case ION -> running ? 0.51F : 0.52F;
            case SCORCH -> running ? 0.54F : 0.53F;
            case RONIN -> running ? 0.21F : 0.23F;
            case TONE -> running ? 0.20F : 0.34F;
            case LEGION -> running ? 0.53F : 0.62F;
            case MONARCH -> running ? 0.13F : 0.25F;
            case NORTHSTAR -> running ? 0.26F : 0.10F;
            case TROOPER, SCOUT, SHADE, BULWARK, EXO_FRAME, TITAN_EXO, STRIKER_FRAME, VANGUARD_FRAME, COLOSSUS_FRAME, TERRAIN_FRAME, CYCLOPS_FRAME, SPIDER_FRAME -> running ? 0.25F : 0.30F;
        };
    }

    private static float clampPlayback(float playback) {
        return Math.max(0.85F, Math.min(2.0F, playback)); // up to 2x so the config speed-up isn't clipped
    }

    public static TitanClass byId(String id) {
        for (TitanClass c : values()) {
            if (c.id.equalsIgnoreCase(id)) return c;
        }
        return ION;
    }
}
