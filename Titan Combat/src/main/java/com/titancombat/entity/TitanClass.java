package com.titancombat.entity;

public enum TitanClass {
    ION("ion", "Ion", "Energy Assault", 350.0D, 100.0F, 0.32D, 25.0D, 2.6F, 4.8F),
    SCORCH("scorch", "Scorch", "Incendiary Siege", 480.0D, 120.0F, 0.25D, 35.0D, 2.8F, 5.0F),
    RONIN("ronin", "Ronin", "High-Speed Striker", 240.0D, 80.0F, 0.38D, 45.0D, 2.4F, 4.6F),
    TONE("tone", "Tone", "Missile Tracker", 350.0D, 100.0F, 0.32D, 28.0D, 2.6F, 4.8F),
    LEGION("legion", "Legion", "Super-Heavy Juggernaut", 550.0D, 150.0F, 0.23D, 30.0D, 3.0F, 5.2F),
    MONARCH("monarch", "Monarch", "Vanguard Support", 350.0D, 120.0F, 0.33D, 26.0D, 2.6F, 4.8F),
    NORTHSTAR("northstar", "Northstar", "Precision Sniper", 240.0D, 80.0F, 0.36D, 60.0D, 2.4F, 4.6F);

    private final String id;
    private final String displayName;
    private final String role;
    private final double maxHealth;
    private final float maxShield;
    private final double moveSpeed;
    private final double attackDamage;
    private final float width;
    private final float height;

    TitanClass(String id, String displayName, String role, double maxHealth, float maxShield, double moveSpeed, double attackDamage, float width, float height) {
        this.id = id;
        this.displayName = displayName;
        this.role = role;
        this.maxHealth = maxHealth;
        this.maxShield = maxShield;
        this.moveSpeed = moveSpeed;
        this.attackDamage = attackDamage;
        this.width = width;
        this.height = height;
    }

    public String getId() {
        return id;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getRole() {
        return role;
    }

    public double getMaxHealth() {
        return maxHealth;
    }

    public float getMaxShield() {
        return maxShield;
    }

    public double getMoveSpeed() {
        return moveSpeed;
    }

    public double getAttackDamage() {
        return attackDamage;
    }

    public float getWidth() {
        return width;
    }

    public float getHeight() {
        return height;
    }

    public static TitanClass byId(String id) {
        for (TitanClass c : values()) {
            if (c.id.equalsIgnoreCase(id)) return c;
        }
        return ION;
    }
}
