package com.titancombat.entity.transport;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Ocean patrol frigate: long-range escort with a stern helipad (helicopters and aircraft park and ride on it) and room for one Titan.
 * Model: scripts/gen_naval_fleet.py. Deck top 2.625 blocks, 6 wide; bridge block z +0.6..+3.9, hangar z -1.4..-3.9.
 */
public class TitanPatrolFrigateEntity extends BaseShipEntity {
    public TitanPatrolFrigateEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createTransportAttributes().add(Attributes.MAX_HEALTH, 700.0D).add(Attributes.ARMOR, 28.0D);
    }

    @Override protected String key() { return "patrol_frigate"; }
    @Override protected float maxForward() { return 0.7F; }
    @Override protected float acceleration() { return 0.016F; }
    @Override protected float turnRate() { return 1.2F; }
    @Override protected double waterline() { return 1.4D; }
    @Override protected double sternDistance() { return 14.0D; }
    @Override public int getCargoCapacity() { return 1; }
    @Override protected Vec3 getDriverSeatOffset() { return new Vec3(0.0D, 5.75D - 0.6D, 2.6D); }
    @Override protected Vec3 getTitanCargoOffset(int slotIndex) { return new Vec3(0.0D, 2.7D, -11.0D); }

    @Override
    protected void spawnDeckColliders() {
        DeckColliderEntity.spawnRow(this, 6.0F, 3.0F, 0.0F, -0.375F, -14.5D, 10.6D);                  // deck (top 2.625)
        DeckColliderEntity.spawnRow(this, 2.75F, 3.0F, 0.0F, 2.625F, 0.6D, 3.85D);                    // bridge block
        DeckColliderEntity.spawnRow(this, 3.5F, 2.1F, 0.0F, 2.625F, -3.9D, -1.4D);                    // hangar
    }
}
