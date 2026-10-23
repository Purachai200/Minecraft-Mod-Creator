package com.titancombat.entity;

public enum MechState {
    IDLE((byte) 0),
    DROPPING((byte) 1),
    LANDED((byte) 2),
    PILOTED((byte) 3),
    DOOMED((byte) 4),
    DESTROYED((byte) 5);

    private final byte id;

    MechState(byte id) {
        this.id = id;
    }

    public byte getId() {
        return id;
    }

    public static MechState byId(byte id) {
        for (MechState state : values()) {
            if (state.id == id) return state;
        }
        return IDLE;
    }
}
