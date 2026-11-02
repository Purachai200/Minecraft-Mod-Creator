package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;

/**
 * Mobile Suit Flatbed Heavy Transporter:
 * Massive heavy hauler with an articulated hydraulic launch cradle.
 * Accommodates an entire Titan or Obsolete Exoframe resting securely on the heavy trailer deck.
 */
public class TitanMobileSuitTrailerEntity extends BaseTransportVehicleEntity {
    // Tractor Cab Driver Seat (Inside hollow cab: x=10, z=-72 in model; cushion y=18; +Z forward in vehicle coords: z=+72/16)
    private static final Vec3 CAB_DRIVER_OFFSET = new Vec3(10 / 16.0D, 18 / 16.0D - 0.7D, 72 / 16.0D);

    // Flatbed Transporter Deck (z = 25, y = 22)
    private static final Vec3 TRAILER_CARGO_OFFSET = new Vec3(0.0D, 22 / 16.0D, -25 / 16.0D);

    public TitanMobileSuitTrailerEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.2F);
    }

    public static AttributeSupplier.Builder createMobileSuitTrailerAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 950.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.42D)
                .add(Attributes.ARMOR, 32.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 16.0D);
    }

    @Override
    public int getCargoCapacity() {
        return 1; // 1 giant Mobile Suit / Titan / Exoframe
    }

    @Override
    protected boolean shouldTitanKneel() {
        return true; // Kneels / locks down onto the transport launch bed
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return CAB_DRIVER_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return TRAILER_CARGO_OFFSET;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        float maxFwd = 0.48F;
        float maxRev = 0.18F;
        float accel = 0.016F;
        float brake = 0.04F;
        float drag = 0.012F;
        float steerRate = 1.8F; // Heavy articulated turning radius

        updateThrottle(driver, maxFwd, maxRev, accel, brake, drag);

        float steer = -driver.xxa;
        this.yawDelta = steer * steerRate * Math.signum(this.currentSpeed);

        moveAlongHeading(0.96F, gravityMotion());

        if (this.level().isClientSide && Math.abs(this.currentSpeed) > 0.1F && this.tickCount % 3 == 0) {
            double yawRad = Math.toRadians(this.getYRot());
            // Smoke from dual vertical exhaust stacks
            double sx1 = this.getX() + Math.cos(yawRad) * -1.5D - Math.sin(yawRad) * 3.0D;
            double sz1 = this.getZ() + Math.sin(yawRad) * -1.5D + Math.cos(yawRad) * 3.0D;
            double sx2 = this.getX() + Math.cos(yawRad) * 1.5D - Math.sin(yawRad) * 3.0D;
            double sz2 = this.getZ() + Math.sin(yawRad) * 1.5D + Math.cos(yawRad) * 3.0D;
            this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE, sx1, this.getY() + 3.4D, sz1, 0, 0.1D, 0);
            this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE, sx2, this.getY() + 3.4D, sz2, 0, 0.1D, 0);
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "controller", 2, state -> {
            if (Math.abs(this.currentSpeed) > 0.03F) {
                return state.setAndContinue(RawAnimation.begin().thenLoop("animation.mobile_suit_trailer.drive"));
            }
            return state.setAndContinue(RawAnimation.begin().thenLoop("animation.mobile_suit_trailer.idle"));
        }));
    }
}
