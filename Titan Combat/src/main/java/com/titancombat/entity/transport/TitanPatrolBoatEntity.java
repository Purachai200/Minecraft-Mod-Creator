package com.titancombat.entity.transport;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/** Coastal patrol boat: small, quick and nimble, with a walkable deck. Model: scripts/gen_naval_fleet.py (deck top 1.375 blocks). */
public class TitanPatrolBoatEntity extends BaseShipEntity {
    public TitanPatrolBoatEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createTransportAttributes().add(Attributes.MAX_HEALTH, 260.0D).add(Attributes.ARMOR, 12.0D);
    }

    @Override protected String key() { return "patrol_boat"; }
    @Override protected float maxForward() { return 0.95F; }
    @Override protected float acceleration() { return 0.03F; }
    @Override protected float turnRate() { return 2.6F; }
    @Override protected double waterline() { return 0.7D; }
    @Override protected double sternDistance() { return 6.0D; }
    @Override public int getCargoCapacity() { return 0; }
    @Override protected Vec3 getDriverSeatOffset() { return new Vec3(0.0D, 1.625D - 0.6D, 0.8D); }
    @Override protected Vec3 getTitanCargoOffset(int slotIndex) { return new Vec3(0.0D, 1.4D, -4.0D); }

    @Override
    protected void spawnDeckColliders() {
        DeckColliderEntity.spawnRow(this, 3.0F, 1.0F, 0.0F, 0.375F, -5.6D, 4.4D);
    }
}
