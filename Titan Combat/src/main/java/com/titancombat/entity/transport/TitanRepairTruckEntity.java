package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;

/**
 * Mobile field repair & recharge truck: parked with the engine running, it welds and charges every Titan,
 * Exoframe and vehicle within reach, paying for it out of its own fuel cell.
 */
public class TitanRepairTruckEntity extends BaseTransportVehicleEntity {
    private static final Vec3 DRIVER_OFFSET = new Vec3(0.625D, 1.5D - 0.6D, 3.34D);
    private static final Vec3 CARGO_OFFSET = new Vec3(0.0D, 2.0D, -2.0D);
    public static final double REPAIR_RADIUS = 10.0D;

    public TitanRepairTruckEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.3F);
    }

    public static AttributeSupplier.Builder createRepairTruckAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 700.0D)
                .add(Attributes.ARMOR, 26.0D);
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return DRIVER_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return CARGO_OFFSET;
    }

    /** Crane deployed: parked with a driver aboard and fuel to spare. */
    public boolean isRepairing() {
        return this.isRampOpen();
    }

    @Override
    public void tick() {
        super.tick();
        if (this.level().isClientSide) {
            if (isRepairing() && this.tickCount % 3 == 0) {
                double yawRad = Math.toRadians(this.getYRot());
                // Welding sparks at the crane tip, swung out to the right side
                double sx = this.getX() - Math.cos(yawRad) * 3.0D, sz = this.getZ() - Math.sin(yawRad) * 3.0D;
                for (int i = 0; i < 4; i++) {
                    this.level().addParticle(ParticleTypes.ELECTRIC_SPARK, sx + this.random.nextGaussian() * 0.2D,
                            this.getY() + 2.4D, sz + this.random.nextGaussian() * 0.2D,
                            this.random.nextGaussian() * 0.15D, 0.1D, this.random.nextGaussian() * 0.15D);
                }
            }
            return;
        }
        boolean parked = Math.abs(this.currentSpeed) < 0.02F && this.getDeltaMovement().horizontalDistanceSqr() < 1.0E-4D;
        boolean repairing = parked && this.getDriver() != null && this.getEnergy() > 1000;
        if (repairing != isRepairing()) setRampOpen(repairing);
        if (!repairing || this.tickCount % 20 != 0) return;

        boolean worked = false;
        for (Entity e : this.level().getEntities(this, this.getBoundingBox().inflate(REPAIR_RADIUS))) {
            if (e instanceof DeckColliderEntity || this.hasPassenger(e)) continue;
            if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(e)) {
                int before = this.getEnergy();
                com.titancombat.util.CrossModCargoHelper.repairAndChargeCargo(e, this.getEnergy(), this::consumeEnergy);
                worked |= this.getEnergy() != before;
            } else if (e instanceof BaseTransportVehicleEntity v && (v.getHealth() < v.getMaxHealth() || v.getPropulsionDamage() > 0.0F)) {
                v.heal(8.0F);
                v.setPropulsionDamage(v.getPropulsionDamage() - 0.05F);
                consumeEnergy(150);
                worked = true;
            }
        }
        if (worked) {
            this.level().playSound(null, this.blockPosition(), com.titancombat.sound.ModSounds.VEHICLE_REPAIR_WELD.get(), SoundSource.NEUTRAL, 1.0F, 0.9F + this.random.nextFloat() * 0.2F);
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        updateThrottle(driver, 0.46F, 0.2F, 0.02F, 0.05F, 0.018F);
        float steer = -driver.xxa;
        this.yawDelta = Math.abs(this.currentSpeed) < 0.03F ? 0.0F : steer * 2.4F * Math.signum(this.currentSpeed);
        moveAlongHeading(0.9F, gravityMotion());
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "controller", 6, state -> {
            if (isRepairing()) return state.setAndContinue(RawAnimation.begin().thenLoop("animation.repair_truck.repair"));
            if (Math.abs(this.visSpeed) > 0.04F) return state.setAndContinue(RawAnimation.begin().thenLoop("animation.repair_truck.drive"));
            return state.setAndContinue(RawAnimation.begin().thenLoop("animation.repair_truck.idle"));
        }));
    }
}
