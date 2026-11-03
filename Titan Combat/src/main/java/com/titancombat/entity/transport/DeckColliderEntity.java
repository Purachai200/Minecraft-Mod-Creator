package com.titancombat.entity.transport;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/**
 * Invisible solid slab that follows a big ship so players can walk its deck and aircraft can land on it.
 * Vanilla entity collision only knows one axis-aligned box per entity, so a long hull is tiled with several
 * square colliders laid along its centreline; each one carries whatever stands on it with the ship.
 * shortcut: square tiles overhang the hull corners by up to ~30% of the beam when the ship sails diagonally;
 * upgrade to a collision mixin if that becomes a problem.
 */
public class DeckColliderEntity extends Entity {
    private static final EntityDataAccessor<Integer> PARENT = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> SIZE = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> HEIGHT = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    /** Tile centre in the parent's local frame (blocks, +X left, +Z forward) and the tile's bottom y offset. */
    private static final EntityDataAccessor<Float> LX = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> LY = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> LZ = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);

    public DeckColliderEntity(EntityType<?> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public static DeckColliderEntity create(EntityType<DeckColliderEntity> type, Entity parent, float size, float height, float lx, float ly, float lz) {
        DeckColliderEntity e = new DeckColliderEntity(type, parent.level());
        e.entityData.set(PARENT, parent.getId());
        e.entityData.set(SIZE, size);
        e.entityData.set(HEIGHT, height);
        e.entityData.set(LX, lx);
        e.entityData.set(LY, ly);
        e.entityData.set(LZ, lz);
        e.followParent(parent);
        e.refreshDimensions();
        return e;
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(PARENT, -1);
        this.entityData.define(SIZE, 1.0F);
        this.entityData.define(HEIGHT, 1.0F);
        this.entityData.define(LX, 0.0F);
        this.entityData.define(LY, 0.0F);
        this.entityData.define(LZ, 0.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (SIZE.equals(key) || HEIGHT.equals(key)) this.refreshDimensions();
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(this.entityData.get(SIZE), this.entityData.get(HEIGHT));
    }

    public Entity getParent() {
        return this.level().getEntity(this.entityData.get(PARENT));
    }

    private Vec3 localToWorld(Entity parent, double x, double y, double z) {
        float yawRad = parent.getYRot() * Mth.DEG_TO_RAD;
        double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
        return new Vec3(parent.getX() + x * cos - z * sin, parent.getY() + y, parent.getZ() + x * sin + z * cos);
    }

    private void followParent(Entity parent) {
        Vec3 p = localToWorld(parent, this.entityData.get(LX), this.entityData.get(LY), this.entityData.get(LZ));
        this.setPos(p.x, p.y, p.z);
        this.xo = p.x; this.yo = p.y; this.zo = p.z;
    }

    @Override
    public void tick() {
        Entity parent = getParent();
        if (parent == null || !parent.isAlive()) {
            if (!this.level().isClientSide) this.discard();
            return;
        }
        // Pick up riders on the tile's old position first: if the ship bobs up before we look, they'd end up inside the tile and drop through
        java.util.List<Entity> riders = ridersOnTop(parent);
        followParent(parent);
        carryRiders(parent, riders);
    }

    private java.util.List<Entity> ridersOnTop(Entity parent) {
        AABB top = this.getBoundingBox();
        AABB zone = new AABB(top.minX, top.maxY - 0.3D, top.minZ, top.maxX, top.maxY + 0.6D, top.maxZ);
        return this.level().getEntities(this, zone, e -> !(e instanceof DeckColliderEntity) && e != parent && !e.isPassenger()
                && e.getX() >= top.minX && e.getX() <= top.maxX && e.getZ() >= top.minZ && e.getZ() <= top.maxZ
                && e.getY() >= top.maxY - 0.3D);
    }

    /** Anything standing on this tile moves and turns with the ship. Players are moved on their own client (it owns their position). */
    private void carryRiders(Entity parent, java.util.List<Entity> riders) {
        double dx = parent.getX() - parent.xo, dy = parent.getY() - parent.yo, dz = parent.getZ() - parent.zo;
        float dYaw = Mth.wrapDegrees(parent.getYRot() - parent.yRotO);
        double deckTop = this.getBoundingBox().maxY;
        for (Entity e : riders) {
            boolean owner = e instanceof Player ? e.isControlledByLocalInstance() && this.level().isClientSide : !this.level().isClientSide;
            if (!owner) continue;
            double rx = e.getX() - parent.xo, rz = e.getZ() - parent.zo; // relative to where the ship was last tick
            float r = dYaw * Mth.DEG_TO_RAD;
            double nx = rx * Math.cos(r) - rz * Math.sin(r), nz = rx * Math.sin(r) + rz * Math.cos(r);
            // Ride the deck height exactly so the bob never leaves anything sunk into the slab
            e.setPos(parent.getX() + nx, Math.max(e.getY() + dy, deckTop), parent.getZ() + nz);
            if (dYaw != 0.0F) {
                e.setYRot(e.getYRot() + dYaw);
                if (e instanceof net.minecraft.world.entity.LivingEntity living) living.setYHeadRot(living.getYHeadRot() + dYaw);
            }
        }
    }

    @Override
    public boolean canBeCollidedWith() {
        return true;
    }

    @Override
    public boolean isPickable() {
        return !this.isRemoved();
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        Entity parent = getParent();
        return parent != null && parent.hurt(source, amount);
    }

    @Override
    public InteractionResult interact(Player player, InteractionHand hand) {
        Entity parent = getParent();
        return parent != null ? player.interactOn(parent, hand) : InteractionResult.PASS;
    }

    @Override
    public boolean shouldBeSaved() {
        return false; // the ship respawns its tiles on load
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {}

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {}
}
