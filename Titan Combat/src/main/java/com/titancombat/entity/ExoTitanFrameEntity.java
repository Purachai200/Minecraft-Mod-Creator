package com.titancombat.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.level.Level;

/** MP-05 Exo Frame: mass-production exoskeleton that wears the modular armour sets (tinted per theme by TitanRenderer). */
public class ExoTitanFrameEntity extends TitanFrameEntity {
    public ExoTitanFrameEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    public TitanClass getTitanClass() {
        return TitanClass.EXO_FRAME;
    }
}
