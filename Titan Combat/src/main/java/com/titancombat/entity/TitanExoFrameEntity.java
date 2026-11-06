package com.titancombat.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.level.Level;

/** Titan Exo: the MP-05 inner frame wearing the Titanfall titans' shells as armour (scratch/build_titan_exo_assets.py). */
public class TitanExoFrameEntity extends TitanFrameEntity {
    public TitanExoFrameEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    @Override
    public TitanClass getTitanClass() {
        return TitanClass.TITAN_EXO;
    }
}
