package com.titancombat.entity;

public enum TitanArmorArchetype {
    INFANTRY("infantry", "Standard Tactical Infantry Armor"),
    SIEGE("siege", "Super-Heavy Bunker & Hazard Blast Shielding"),
    SAMURAI("samurai", "Articulated Blade & Kabuto Pauldrons"),
    AERO("aero", "High-Mobility Swept Delta Winglets"),
    SCRAP("scrap", "Welded Rebar Cage & Post-Apocalyptic Iron Sheets"),
    STEALTH("stealth", "Faceted Radar-Absorbent Carbon Cowls"),
    SOVEREIGN("sovereign", "Regal Gilded Imperial Commander Plate"),
    EXPEDITION("expedition", "Heavy Cyclone Pre-Cleaner & Storage Sponsons");

    private final String id;
    private final String description;

    TitanArmorArchetype(String id, String description) {
        this.id = id;
        this.description = description;
    }

    public String getId() {
        return id;
    }

    public String getDescription() {
        return description;
    }
}
