package com.obsolete.entity.inventory;

public enum ExoframeArmorSlot {
    HEAD(0, "head", "armor_head"),
    CHEST(1, "chest", "armor_chest"),
    ARMS(2, "arms", "armor_left_shoulder,armor_right_shoulder"),
    LEGS(3, "legs", "armor_left_leg,armor_right_leg"),
    UTILITY(4, "utility", ""),
    MAIN_WEAPON(5, "main_weapon", "right_hand_weapon_mount"),
    BACK(6, "back", "torso");

    private final int index;
    private final String name;
    private final String targetBones;

    ExoframeArmorSlot(int index, String name, String targetBones) {
        this.index = index;
        this.name = name;
        this.targetBones = targetBones;
    }

    public int getIndex() {
        return index;
    }

    public String getName() {
        return name;
    }

    public String[] getTargetBones() {
        if (targetBones.isEmpty()) return new String[0];
        return targetBones.split(",");
    }

    public static ExoframeArmorSlot byIndex(int index) {
        for (ExoframeArmorSlot slot : values()) {
            if (slot.index == index) return slot;
        }
        return UTILITY;
    }
}
