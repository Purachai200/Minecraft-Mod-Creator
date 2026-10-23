package com.titancombat.entity;

import net.minecraft.network.chat.Component;
import net.minecraft.world.item.DyeColor;

public enum MechFaction {
    NEUTRAL(0, "Mercenary / Neutral", 0x7A8288, 0xFFDD00),
    APEX_VANGUARD(1, "Apex Vanguard (Blue)", 0x1E56C8, 0x00E5FF),
    CRIMSON_LEGION(2, "Crimson Legion (Red)", 0xC41E1E, 0xFF3D00),
    VIPER_SYNDICATE(3, "Viper Syndicate (Green)", 0x228B22, 0x00FF66),
    SOLARIS_CORP(4, "Solaris Corp (Gold)", 0xE69500, 0xFFEE33),
    SHADOW_OPS(5, "Shadow Ops (Black/Purple)", 0x202026, 0xBB33FF);

    private final int id;
    private final String displayName;
    private final int defaultPrimaryColor;
    private final int emissiveColor;

    MechFaction(int id, String displayName, int defaultPrimaryColor, int emissiveColor) {
        this.id = id;
        this.displayName = displayName;
        this.defaultPrimaryColor = defaultPrimaryColor;
        this.emissiveColor = emissiveColor;
    }

    public int getId() {
        return id;
    }

    public String getDisplayName() {
        return displayName;
    }

    public int getDefaultPrimaryColor() {
        return defaultPrimaryColor;
    }

    public int getEmissiveColor() {
        return emissiveColor;
    }

    public static MechFaction byId(int id) {
        for (MechFaction f : values()) {
            if (f.id == id) return f;
        }
        return NEUTRAL;
    }

    public static MechFaction byDye(DyeColor dye) {
        return switch (dye) {
            case BLUE, LIGHT_BLUE, CYAN -> APEX_VANGUARD;
            case RED -> CRIMSON_LEGION;
            case GREEN, LIME -> VIPER_SYNDICATE;
            case YELLOW, ORANGE -> SOLARIS_CORP;
            case BLACK, PURPLE, MAGENTA -> SHADOW_OPS;
            default -> NEUTRAL;
        };
    }
}
