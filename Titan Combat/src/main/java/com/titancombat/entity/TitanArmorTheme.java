package com.titancombat.entity;

public enum TitanArmorTheme {
    VANGUARD(0, "Vanguard Infantry", "Standard military composite armor", 0x4C5562, 10.0F, TitanArmorArchetype.INFANTRY),
    STRIKER(1, "Striker Sprinter", "Lightweight high-mobility swept armor", 0x00E5FF, 6.0F, TitanArmorArchetype.AERO),
    COLOSSUS(2, "Colossus Siege", "Super-heavy blast-resistant armor slates", 0x8F1717, 16.0F, TitanArmorArchetype.SIEGE),
    SAND_RAIDER(3, "Sand Raider", "Desert dust-filtered reinforced cowl", 0xB8862F, 8.0F, TitanArmorArchetype.EXPEDITION),
    POLAR_OPERATIVE(4, "Polar Operative", "Thermal-insulated arctic expedition plate", 0xCFD8E2, 9.0F, TitanArmorArchetype.EXPEDITION),
    CERBERUS_HEAVY(5, "Cerberus Heavy", "360-degree hazardous environment dome", 0x16C878, 12.0F, TitanArmorArchetype.SIEGE),
    SHIDEN_SAMURAI(6, "Shiden Samurai", "Articulated bladed shoulder pauldrons", 0x3D8BFF, 11.0F, TitanArmorArchetype.SAMURAI),
    SPECTER_STEALTH(7, "Specter Stealth", "Radar-absorbent matte carbon plating", 0x202026, 7.0F, TitanArmorArchetype.STEALTH),
    VALKYRIE_AERO(8, "Valkyrie Aero", "Swept aerodynamic high-thrust plating", 0xE0B04A, 8.0F, TitanArmorArchetype.AERO),
    SALVAGE_SCRAP(9, "Salvage Scrap", "Reinforced scrap iron & rebar cage", 0x7D5A1E, 8.0F, TitanArmorArchetype.SCRAP),
    RIVERINE_NAVY(10, "Riverine Navy", "Amphibious hydrodynamic pontoons", 0x00879A, 9.0F, TitanArmorArchetype.EXPEDITION),
    POLICE_RIOT(11, "Police Riot", "Ballistic crowd-control polycarbonate shield", 0x1F55D6, 11.0F, TitanArmorArchetype.INFANTRY),
    DISASTER_RESCUE(12, "Disaster Rescue", "High-visibility impact rescue frame", 0xFF6A00, 10.0F, TitanArmorArchetype.INFANTRY),
    KHAMSIN_STORM(13, "Khamsin Storm", "Heat-reflective desert sandstorm plate", 0xD4A030, 9.0F, TitanArmorArchetype.EXPEDITION),
    OUTLANDER_HOOD(14, "Outlander Frontier", "Composite ballistic cowl & hood plating", 0x4F5C35, 7.0F, TitanArmorArchetype.SAMURAI),
    HAZARD_DEMO(15, "Hazard Demolition", "High-explosive ordnance disposal armor", 0xFFD200, 14.0F, TitanArmorArchetype.SIEGE),
    APEX_PREDATOR(16, "Apex Sovereign", "Titanium-alloy golden commander plate", 0xE69500, 13.0F, TitanArmorArchetype.SOVEREIGN);

    private final int id;
    private final String displayName;
    private final String description;
    private final int primaryColor;
    private final float armorValue;
    private final TitanArmorArchetype archetype;

    TitanArmorTheme(int id, String displayName, String description, int primaryColor, float armorValue, TitanArmorArchetype archetype) {
        this.id = id;
        this.displayName = displayName;
        this.description = description;
        this.primaryColor = primaryColor;
        this.armorValue = armorValue;
        this.archetype = archetype;
    }

    public TitanArmorArchetype getArchetype() {
        return archetype;
    }

    public int getId() {
        return id;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public int getPrimaryColor() {
        return primaryColor;
    }

    public float getArmorValue() {
        return armorValue;
    }

    public static TitanArmorTheme byId(int id) {
        for (TitanArmorTheme t : values()) {
            if (t.id == id) return t;
        }
        return VANGUARD;
    }
}
