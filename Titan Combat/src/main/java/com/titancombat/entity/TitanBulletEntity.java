package com.titancombat.entity;

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

import java.util.List;

public class TitanBulletEntity extends ThrowableProjectile {
    private float bulletDamage = 35.0F;
    private float explosionPower = 0.0F;
    private int igniteSeconds = 0;
    private int maxLifeTicks = 80;
    private int lifeTicks = 0;
    private boolean hasPlayedFlyby = false;

    public TitanBulletEntity(EntityType<? extends ThrowableProjectile> entityType, Level level) {
        super(entityType, level);
        this.noPhysics = false;
    }

    public TitanBulletEntity(Level level, LivingEntity shooter, float damage) {
        super(ModEntities.TITAN_BULLET.get(), shooter, level);
        this.bulletDamage = damage;
    }

    public TitanBulletEntity withWeapon(TitanWeapon weapon) {
        this.bulletDamage = weapon.getDamage();
        this.explosionPower = weapon.getExplosionPower();
        this.igniteSeconds = weapon.getIgniteSeconds();
        if (this.igniteSeconds > 0) this.setSecondsOnFire(this.igniteSeconds);
        if (weapon.getMaxFlightTicks() > 0) this.maxLifeTicks = weapon.getMaxFlightTicks();
        return this;
    }

    /** Targeting Computer and similar bonuses scale the round after withWeapon set it. */
    public TitanBulletEntity withDamageMultiplier(float multiplier) {
        this.bulletDamage *= multiplier;
        return this;
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
        if (lifeTicks > maxLifeTicks) { // ~400 blocks range unless the weapon burns out sooner
            this.discard();
            return;
        }

        // Supersonic bullet flyby snap sound
        if (!this.level().isClientSide && !hasPlayedFlyby && lifeTicks > 1) {
            Entity shooter = this.getOwner();
            List<LivingEntity> nearby = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(4.0D),
                    e -> e != shooter && (shooter == null || e != shooter.getVehicle()));
            if (!nearby.isEmpty()) {
                hasPlayedFlyby = true;
                float whizPitch = 1.6F + this.random.nextFloat() * 0.3F;
                this.level().playSound(null, this.blockPosition(), SoundEvents.ARROW_SHOOT, SoundSource.PLAYERS, 1.8F, whizPitch);
            }
        }

        // Kinetic contrail with glowing rear tracer flame
        if (this.level().isClientSide) {
            Vec3 pos = this.position();
            Vec3 delta = this.getDeltaMovement();
            this.level().addParticle(ParticleTypes.CRIT,
                    pos.x - delta.x * 0.35D,
                    pos.y - delta.y * 0.35D,
                    pos.z - delta.z * 0.35D,
                    0, 0, 0);
            this.level().addParticle(ParticleTypes.SMALL_FLAME,
                    pos.x - delta.x * 0.55D,
                    pos.y - delta.y * 0.55D,
                    pos.z - delta.z * 0.55D,
                    0, 0, 0);
            if (this.explosionPower > 0.0F) {
                this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                        pos.x - delta.x * 0.4D, pos.y - delta.y * 0.4D, pos.z - delta.z * 0.4D,
                        -delta.x * 0.05D, 0.02D, -delta.z * 0.05D);
            }
        }
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

            DamageSource dmgSource = this.damageSources().mobProjectile(this, shooter instanceof LivingEntity living ? living : null);
            target.hurt(dmgSource, this.bulletDamage);

            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK,
                        target.getX(), target.getY() + target.getEyeHeight() * 0.6D, target.getZ(),
                        12, 0.3D, 0.3D, 0.3D, 0.15D);
                serverLevel.sendParticles(ParticleTypes.CRIT,
                        target.getX(), target.getY() + target.getEyeHeight() * 0.6D, target.getZ(),
                        10, 0.25D, 0.25D, 0.25D, 0.1D);
            }

            if (this.explosionPower > 0.0F) {
                this.level().explode(this, this.getX(), this.getY(), this.getZ(),
                        this.explosionPower, Level.ExplosionInteraction.MOB);
            }

            // Punchy kinetic impact sound
            float pitch = 0.9F + this.random.nextFloat() * 0.2F;
            this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 1.2F, pitch);
            this.level().playSound(null, this.blockPosition(), SoundEvents.PLAYER_ATTACK_CRIT, SoundSource.PLAYERS, 1.4F, 1.1F);
            this.discard();
        }
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        if (!this.level().isClientSide) {
            if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK,
                        result.getLocation().x, result.getLocation().y, result.getLocation().z,
                        8, 0.15D, 0.15D, 0.15D, 0.1D);
                serverLevel.sendParticles(ParticleTypes.SMOKE,
                        result.getLocation().x, result.getLocation().y, result.getLocation().z,
                        8, 0.15D, 0.15D, 0.15D, 0.05D);
            }

            if (this.explosionPower > 0.0F) {
                this.level().explode(this, this.getX(), this.getY(), this.getZ(),
                        this.explosionPower, Level.ExplosionInteraction.MOB);
            }

            float pitch = 1.1F + this.random.nextFloat() * 0.2F;
            this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_PLACE, SoundSource.PLAYERS, 1.0F, pitch);
            this.discard();
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
