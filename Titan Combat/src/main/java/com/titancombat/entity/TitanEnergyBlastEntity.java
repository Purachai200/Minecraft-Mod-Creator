package com.titancombat.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;

public class TitanEnergyBlastEntity extends ThrowableItemProjectile {

    public TitanEnergyBlastEntity(EntityType<? extends ThrowableItemProjectile> type, Level level) {
        super(type, level);
    }

    public TitanEnergyBlastEntity(EntityType<? extends ThrowableItemProjectile> type, double x, double y, double z, Level level) {
        super(type, x, y, z, level);
    }

    public TitanEnergyBlastEntity(EntityType<? extends ThrowableItemProjectile> type, LivingEntity shooter, Level level) {
        super(type, shooter, level);
    }

    // Ballistics of the weapon that fired this round (defaults match the old fixed values).
    private float damage = 35.0F;
    private float explosionPower = 1.5F;
    private int igniteSeconds = 0;

    /** Configure this round from the weapon that fired it. */
    public TitanEnergyBlastEntity withWeapon(TitanWeapon weapon) {
        this.damage = weapon.getDamage();
        this.explosionPower = weapon.getExplosionPower();
        this.igniteSeconds = weapon.getIgniteSeconds();
        if (this.igniteSeconds > 0) this.setSecondsOnFire(this.igniteSeconds);
        return this;
    }

    @Override
    protected Item getDefaultItem() {
        return Items.IRON_NUGGET;
    }

    /** Titan rounds fly flat: with vanilla throwable gravity they dropped 3+ blocks at range and missed the reticle. */
    @Override
    protected float getGravity() {
        return 0.0F;
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.level().isClientSide && this.tickCount > 100) {
            this.discard(); // ~250 blocks of travel; don't let misses fly forever
            return;
        }
        if (this.level().isClientSide) {
            for (int i = 0; i < 2; i++) {
                this.level().addParticle(ParticleTypes.ELECTRIC_SPARK,
                        this.getX() + (this.random.nextDouble() - 0.5D) * 0.2D,
                        this.getY() + (this.random.nextDouble() - 0.5D) * 0.2D,
                        this.getZ() + (this.random.nextDouble() - 0.5D) * 0.2D,
                        0, 0, 0);
            }
        }
    }

    @Override
    protected boolean canHitEntity(Entity target) {
        // Never collide with the titan the shooter is piloting (shots leave its own weapon).
        Entity owner = this.getOwner();
        if (owner != null && target == owner.getVehicle()) return false;
        return super.canHitEntity(target);
    }

    @Override
    protected void onHitEntity(EntityHitResult result) {
        super.onHitEntity(result);
        Entity target = result.getEntity();
        Entity owner = this.getOwner();

        if (target != owner && !target.isPassengerOfSameVehicle(this)) {
            DamageSource source = this.damageSources().thrown(this, owner);
            target.hurt(source, this.damage);
            if (this.igniteSeconds > 0) target.setSecondsOnFire(this.igniteSeconds);
        }
    }

    @Override
    protected void onHit(HitResult result) {
        super.onHit(result);
        if (!this.level().isClientSide && !System.getProperty("titancombat.autotest", "").isEmpty()) {
            com.titancombat.TitanCombatMod.LOGGER.info("[autotest] round hit at {}", result.getLocation());
        }
        if (!this.level().isClientSide) {
            if (this.explosionPower > 0.0F) {
                this.level().explode(this, this.getX(), this.getY(), this.getZ(), this.explosionPower, Level.ExplosionInteraction.NONE);
            } else if (this.level() instanceof net.minecraft.server.level.ServerLevel server) {
                // Kinetic rounds: impact sparks and a crack instead of a blast.
                server.sendParticles(ParticleTypes.CRIT, this.getX(), this.getY(), this.getZ(), 6, 0.15D, 0.15D, 0.15D, 0.2D);
                server.sendParticles(ParticleTypes.SMOKE, this.getX(), this.getY(), this.getZ(), 2, 0.1D, 0.1D, 0.1D, 0.02D);
                this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 0.25F, 1.9F);
            }
            this.discard();
        }
    }
}
