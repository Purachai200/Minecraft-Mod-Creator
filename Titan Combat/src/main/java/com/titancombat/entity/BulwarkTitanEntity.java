package com.titancombat.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.level.Level;

/**
 * MP-07 Bulwark: heavy mass-production frame on the Trooper skeleton. Slower and tougher than the
 * Trooper; carries any Trooper weapon module (drawn by TitanWeaponSwapLayer).
 */
public class BulwarkTitanEntity extends BaseTitanEntity {
    public BulwarkTitanEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    public TitanClass getTitanClass() {
        return TitanClass.BULWARK;
    }
}
