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

import java.util.List;

public class ExoframeBulletEntity extends ThrowableProjectile {
    private float bulletDamage = 26.0F;
    private int lifeTicks = 0;
    private boolean hasPlayedFlyby = false;

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

        // Supersonic bullet flyby snap sound when screaming past living entities
        if (!this.level().isClientSide && !hasPlayedFlyby && lifeTicks > 1) {
            Entity shooter = this.getOwner();
            List<LivingEntity> nearby = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(3.5D),
                    e -> e != shooter && (shooter == null || e != shooter.getVehicle()));
            if (!nearby.isEmpty()) {
                hasPlayedFlyby = true;
                float whizPitch = 1.85F + this.random.nextFloat() * 0.25F;
                this.level().playSound(null, this.blockPosition(), SoundEvents.ARROW_SHOOT, SoundSource.PLAYERS, 1.8F, whizPitch);
            }
        }

        // Trace kinetic contrail with glowing rear tracer flame
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
                serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK,
                        target.getX(), target.getY() + target.getEyeHeight() * 0.6D, target.getZ(),
                        8, 0.2D, 0.2D, 0.2D, 0.15D);
                serverLevel.sendParticles(ParticleTypes.CRIT,
                        target.getX(), target.getY() + target.getEyeHeight() * 0.6D, target.getZ(),
                        8, 0.2D, 0.2D, 0.2D, 0.1D);
            }

            // Punchy kinetic impact sound: heavy metal clang + critical hit crunch
            float pitch = 0.95F + this.random.nextFloat() * 0.15F;
            this.level().playSound(null, this.blockPosition(), com.obsolete.sound.ModSounds.WEAPON_IMPACT_METAL.get(), SoundSource.PLAYERS, 1.5F, pitch);
            this.level().playSound(null, this.blockPosition(), SoundEvents.PLAYER_ATTACK_CRIT, SoundSource.PLAYERS, 1.2F, 1.15F);
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
                        6, 0.12D, 0.12D, 0.12D, 0.1D);
                serverLevel.sendParticles(ParticleTypes.SMOKE,
                        result.getLocation().x, result.getLocation().y, result.getLocation().z,
                        6, 0.1D, 0.1D, 0.1D, 0.05D);
            }

            // High-velocity ricochet / ceramic shatter sound: metal impact + anvil ping
            float pitch = 1.05F + this.random.nextFloat() * 0.2F;
            this.level().playSound(null, this.blockPosition(), com.obsolete.sound.ModSounds.WEAPON_IMPACT_METAL.get(), SoundSource.PLAYERS, 1.3F, pitch);
            this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.7F, 1.85F + this.random.nextFloat() * 0.2F);
            this.discard();
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
