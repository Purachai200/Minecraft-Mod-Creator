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
import software.bernie.geckolib.core.object.PlayState;

/**
 * 8x8 Heavy Flatbed Transporter Truck: Military heavy logistics vehicle designed for rapid overland transit.
 * Can haul 1 full-size Titan in kneeling lockdown at high road cruise speeds.
 */
public class TitanHaulerTruckEntity extends BaseTransportVehicleEntity {
    // Left-hand driver's seat in the cab: cushion top at model (x13, y42, z-56); -0.7 drops the riding player's hips onto it
    private static final Vec3 DRIVER_OFFSET = new Vec3(13 / 16.0D, 42 / 16.0D - 0.7D, 56 / 16.0D);
    // Flatbed deck top is y34, straps centred at model z30; the kneeling pose draws the Titan ~1.3 blocks
    // forward of its position, so anchor it that far behind the straps (measured in autotest shot 06)
    private static final Vec3 CARGO_OFFSET = new Vec3(0.0D, 34 / 16.0D, -30 / 16.0D - 1.3D);
    private static final float WHEELBASE = 6.75F; // blocks between the steering pair and the rear bogie
    private static final float MAX_STEER_RAD = (float) Math.toRadians(32.0D);

    /** Smoothed A/D input, -1..1 (positive = left). */
    private float steer = 0.0F;

    public TitanHaulerTruckEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.6F); // Climbs curbs and small natural stone shelves
    }

    public static AttributeSupplier.Builder createHaulerAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 500.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.42D) // Rapid road transit (~0.78 blocks/tick with driver)
                .add(Attributes.ARMOR, 28.0D);
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return DRIVER_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return CARGO_OFFSET;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        updateThrottle(driver, 0.8F, 0.25F, 0.018F, 0.05F, 0.006F + Math.abs(this.currentSpeed) * 0.01F);

        // A/D turn the front wheels; the hull follows the wheels (bicycle model), so no turning on the spot
        this.steer = approach(this.steer, driver.xxa, 0.12F);
        float steerRad = this.steer * MAX_STEER_RAD;
        this.yawDelta = -(float) Math.toDegrees(this.currentSpeed * Math.tan(steerRad) / WHEELBASE);

        moveAlongHeading(1.0F, gravityMotion());

        // Wheel road dust particles while driving fast
        if (Math.abs(this.currentSpeed) > 0.15F && this.onGround() && this.level().isClientSide) {
            double yawRad = this.getYRot() * (Math.PI / 180.0D);
            double backX = this.getX() - Math.sin(yawRad) * 4.0D;
            double backZ = this.getZ() + Math.cos(yawRad) * 4.0D;
            this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                    backX + (this.random.nextDouble() - 0.5D) * 1.5D,
                    this.getY() + 0.2D,
                    backZ + (this.random.nextDouble() - 0.5D) * 1.5D,
                    0, 0.05D, 0);
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "drive", 4, event -> {
            if (Math.abs(this.visSpeed) > 0.03F) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_hauler_truck.drive"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_hauler_truck.idle"));
        }));
    }
}
