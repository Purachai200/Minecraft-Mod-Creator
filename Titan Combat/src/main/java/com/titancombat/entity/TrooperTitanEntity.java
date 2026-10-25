package com.titancombat.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.level.Level;

/**
 * Trooper Class Titan: An original, modular, mass-produced infantry combat and industrial frame.
 * Designed for standard military deployment, utility excavation, forestry and field defense.
 */
public class TrooperTitanEntity extends BaseTitanEntity {
    public TrooperTitanEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    public TitanClass getTitanClass() {
        return TitanClass.TROOPER;
    }
}
