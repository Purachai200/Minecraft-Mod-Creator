package com.titancombat.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.projectile.ThrowableProjectile;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;

import java.util.List;

public class TitanSmokeShellEntity extends ThrowableProjectile {
    private int lifeTicks = 0;

    public TitanSmokeShellEntity(EntityType<? extends ThrowableProjectile> entityType, Level level) {
        super(entityType, level);
        this.noPhysics = false;
    }

    public TitanSmokeShellEntity(Level level, LivingEntity shooter) {
        super(ModEntities.TITAN_SMOKE_SHELL.get(), shooter, level);
    }

    @Override
    protected void defineSynchedData() {
    }

    @Override
    protected float getGravity() {
        return (float) BaseTitanEntity.SHELL_GRAVITY;
    }

    @Override
    public void tick() {
        super.tick();
        lifeTicks++;
        if (lifeTicks > 300) {
            this.discard();
            return;
        }

        // Flight smoke trail
        if (this.level().isClientSide) {
            Vec3 pos = this.position();
            this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                    pos.x, pos.y, pos.z,
                    (this.random.nextDouble() - 0.5D) * 0.05D,
                    0.02D,
                    (this.random.nextDouble() - 0.5D) * 0.05D);
        }
    }

    @Override
    protected boolean canHitEntity(Entity target) {
        Entity owner = this.getOwner();
        if (owner != null && target == owner.getVehicle()) return false;
        return super.canHitEntity(target);
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        detonateSmoke();
    }

    @Override
    protected void onHitBlock(BlockHitResult result) {
        super.onHitBlock(result);
        detonateSmoke();
    }

    private void detonateSmoke() {
        if (!this.level().isClientSide) {
            Vec3 pos = this.position();

            // Sound
            this.level().playSound(null, this.blockPosition(), SoundEvents.FIREWORK_ROCKET_BLAST, SoundSource.PLAYERS, 2.5F, 0.7F);
            this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXTINGUISH_FIRE, SoundSource.PLAYERS, 2.0F, 0.8F);

            // Spawn lingering smoke cloud
            AreaEffectCloud cloud = new AreaEffectCloud(this.level(), pos.x, pos.y, pos.z);
            cloud.setRadius(7.0F);
            cloud.setRadiusOnUse(-0.5F);
            cloud.setWaitTime(0);
            cloud.setDuration(500); // 25 seconds
            cloud.setRadiusPerTick((12.0F - cloud.getRadius()) / 500.0F);
            cloud.setParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE);
            cloud.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 100, 0, false, false));
            cloud.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 100, 0, false, false));
            this.level().addFreshEntity(cloud);

            if (this.level() instanceof ServerLevel serverLevel) {
                // Dense initial billowing smoke burst
                for (int i = 0; i < 40; i++) {
                    double ox = (this.random.nextDouble() - 0.5D) * 6.0D;
                    double oy = this.random.nextDouble() * 2.5D;
                    double oz = (this.random.nextDouble() - 0.5D) * 6.0D;
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                            pos.x + ox, pos.y + oy, pos.z + oz,
                            1, 0, 0.05D, 0, 0.02D);
                }

                // Pacify hostile mobs in the smoke radius
                List<Mob> nearbyMobs = serverLevel.getEntitiesOfClass(Mob.class, this.getBoundingBox().inflate(12.0D));
                for (Mob mob : nearbyMobs) {
                    mob.setTarget(null);
                    mob.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 200, 0));
                    mob.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 200, 1));
                }
            }

            this.discard();
        }
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }
}
