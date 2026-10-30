package com.obsolete.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;

import java.util.List;

public class ExoframeRocketEntity extends ThrowableProjectile {
    private float directDamage = 45.0F;
    private static final float EXPLOSION_RADIUS = 3.5F;
    private int flightTicks = 0;

    public ExoframeRocketEntity(EntityType<? extends ThrowableProjectile> entityType, Level level) {
        super(entityType, level);
        this.noPhysics = false;
    }

    public ExoframeRocketEntity(Level level, LivingEntity shooter) {
        this(level, shooter, 45.0F);
    }

    public ExoframeRocketEntity(Level level, LivingEntity shooter, float directDamage) {
        super(ModEntities.ROCKET.get(), shooter, level);
        this.directDamage = directDamage;
    }

    @Override
    protected void defineSynchedData() {
    }

    @Override
    public boolean isNoGravity() {
        return true;
    }

    @Override
    public void tick() {
        super.tick();
        flightTicks++;
        if (flightTicks > 100) { // Max 5 seconds before self-detonation
            detonate();
            return;
        }

        // Rocket booster thrust smoke and flame
        if (this.level().isClientSide) {
            Vec3 pos = this.position();
            Vec3 delta = this.getDeltaMovement();
            for (int i = 0; i < 2; i++) {
                this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                        pos.x - delta.x * 0.5D + (random.nextDouble() - 0.5D) * 0.1D,
                        pos.y - delta.y * 0.5D + (random.nextDouble() - 0.5D) * 0.1D,
                        pos.z - delta.z * 0.5D + (random.nextDouble() - 0.5D) * 0.1D,
                        0, 0, 0);
            }
            this.level().addParticle(ParticleTypes.FLAME,
                    pos.x - delta.x * 0.3D,
                    pos.y - delta.y * 0.3D,
                    pos.z - delta.z * 0.3D,
                    0, 0, 0);
        }
    }

    @Override
    protected boolean canHitEntity(Entity entity) {
        if (!super.canHitEntity(entity)) return false;
        Entity shooter = this.getOwner();
        if (shooter != null) {
            if (entity == shooter || entity == shooter.getVehicle() || shooter.getPassengers().contains(entity)) {
                return false;
            }
            if (shooter.getVehicle() != null && (entity == shooter.getVehicle() || shooter.getVehicle().getPassengers().contains(entity))) {
                return false;
            }
        }
        return true;
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (!this.level().isClientSide) {
            Entity target = result.getEntity();
            Entity shooter = this.getOwner();
            if (target == shooter || (shooter != null && shooter.getVehicle() == target) || (target.getVehicle() == shooter)) {
                return;
            }
            target.hurt(this.damageSources().mobProjectile(this, shooter instanceof LivingEntity living ? living : null), this.directDamage);
            detonate();
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        if (!this.level().isClientSide) {
            detonate();
        }
    }

    private void detonate() {
        if (!this.level().isClientSide) {
            Entity shooter = this.getOwner();
            Vec3 explosionCenter = this.position();

            // Spawn explosion particles and sound
            this.level().explode(shooter != null ? shooter : this,
                    explosionCenter.x, explosionCenter.y, explosionCenter.z,
                    EXPLOSION_RADIUS, Level.ExplosionInteraction.MOB);

            // Additional kinetic shockwave against entities
            AABB aabb = new AABB(
                    explosionCenter.x - EXPLOSION_RADIUS, explosionCenter.y - EXPLOSION_RADIUS, explosionCenter.z - EXPLOSION_RADIUS,
                    explosionCenter.x + EXPLOSION_RADIUS, explosionCenter.y + EXPLOSION_RADIUS, explosionCenter.z + EXPLOSION_RADIUS);
            List<LivingEntity> nearby = this.level().getEntitiesOfClass(LivingEntity.class, aabb,
                    e -> e != shooter && (shooter == null || e != shooter.getVehicle()));

            for (LivingEntity e : nearby) {
                double dist = e.distanceToSqr(explosionCenter);
                if (dist < EXPLOSION_RADIUS * EXPLOSION_RADIUS) {
                    float factor = (float) (1.0D - Math.sqrt(dist) / EXPLOSION_RADIUS);
                    e.hurt(this.damageSources().explosion(shooter instanceof LivingEntity l ? l : null, this), this.directDamage * factor);
                    Vec3 knock = e.position().subtract(explosionCenter).normalize().scale(factor * 1.5D);
                    e.setDeltaMovement(knock.x, knock.y + 0.3D, knock.z);
                    e.hurtMarked = true;
                }
            }

            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.EXPLOSION_EMITTER,
                        explosionCenter.x, explosionCenter.y, explosionCenter.z, 1, 0, 0, 0, 0);
            }
            this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 2.5F, 0.9F);
            this.discard();
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
