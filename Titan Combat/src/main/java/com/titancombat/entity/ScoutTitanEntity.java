package com.titancombat.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.level.Level;

/**
 * Scout Class Titan: a light, fast recon frame built on the Trooper skeleton.
 * Designed for standard military deployment, utility excavation, forestry and field defense.
 */
public class ScoutTitanEntity extends BaseTitanEntity {
    public ScoutTitanEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    public TitanClass getTitanClass() {
        return TitanClass.SCOUT;
    }
}
