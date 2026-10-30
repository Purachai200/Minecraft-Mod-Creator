package com.obsolete.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;

public class ExoframeBulletEntity extends ThrowableProjectile {
    private float bulletDamage = 26.0F;
    private int lifeTicks = 0;

    public ExoframeBulletEntity(EntityType<? extends ThrowableProjectile> entityType, Level level) {
        super(entityType, level);
        this.noPhysics = false;
    }

    public ExoframeBulletEntity(Level level, LivingEntity shooter) {
        this(level, shooter, 26.0F);
    }

    public ExoframeBulletEntity(Level level, LivingEntity shooter, float damage) {
        super(ModEntities.BULLET.get(), shooter, level);
        this.bulletDamage = damage;
    }

    @Override
    protected void defineSynchedData() {
    }

    @Override
    public boolean isNoGravity() {
        return true;
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
    public void tick() {
        super.tick();
        lifeTicks++;
        if (lifeTicks > 60) { // Max 3 seconds flight time (~300 blocks)
            this.discard();
            return;
        }

        // Trace kinetic contrail
        if (this.level().isClientSide) {
            Vec3 pos = this.position();
            Vec3 delta = this.getDeltaMovement();
            this.level().addParticle(ParticleTypes.CRIT,
                    pos.x - delta.x * 0.4D,
                    pos.y - delta.y * 0.4D,
                    pos.z - delta.z * 0.4D,
                    0, 0, 0);
        }
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        if (!this.level().isClientSide) {
            Entity target = result.getEntity();
            Entity shooter = this.getOwner();

            // Don't damage the mech or the pilot that fired it
            if (target == shooter || (shooter != null && shooter.getVehicle() == target) || (target.getVehicle() == shooter)) {
                return;
            }

            DamageSource dmgSource = this.damageSources().mobProjectile(this, shooter instanceof LivingEntity living ? living : null);
            target.hurt(dmgSource, this.bulletDamage);

            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.CRIT,
                        target.getX(), target.getY() + target.getEyeHeight() * 0.6D, target.getZ(),
                        10, 0.2D, 0.2D, 0.2D, 0.1D);
            }
            this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_PLACE, SoundSource.PLAYERS, 1.2F, 1.8F);
            this.discard();
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        if (!this.level().isClientSide) {
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.SMOKE,
                        result.getLocation().x, result.getLocation().y, result.getLocation().z,
                        6, 0.1D, 0.1D, 0.1D, 0.05D);
            }
            this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_HIT, SoundSource.PLAYERS, 0.8F, 1.6F);
            this.discard();
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
