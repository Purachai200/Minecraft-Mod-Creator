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
 * Heavy Tactical Technical / 4x4 Off-Road Pickup: High-speed military utility vehicle.
 * Fast, agile overland transit with 1.8 block step height for rough combat zones.
 * Has full 2-seater cab (Driver left) and rear flatbed capable of carrying 1 Obsolete Exoframe or Light Titan.
 */
public class TitanTacticalTruckEntity extends BaseTransportVehicleEntity {
    // Left-hand Driver's seat inside Cab: cushion top at model (x: 8, y: 17, z: -10); eye height aligns with windshield
    private static final Vec3 DRIVER_OFFSET = new Vec3(8.0D / 16.0D, 18.0D / 16.0D - 0.7D, 10.0D / 16.0D);

    // Rear Cargo Flatbed: floor y: 15, z: 24 (centered between rollbar and tailgate)
    private static final Vec3 CARGO_OFFSET = new Vec3(0.0D, 15.0D / 16.0D, -24.0D / 16.0D);

    private static final float WHEELBASE = 4.0F;
    private static final float MAX_STEER_RAD = (float) Math.toRadians(36.0D);

    private float steer = 0.0F;

    public TitanTacticalTruckEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.8F); // Agile off-roader: climbs curbs and boulder steps easily
    }

    public static AttributeSupplier.Builder createTacticalTruckAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 380.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.48D) // High tactical speed (~0.88 blocks/tick with driver)
                .add(Attributes.ARMOR, 20.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 8.0D);
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
        // High responsive throttle & quick acceleration
        updateThrottle(driver, 0.90F, 0.35F, 0.024F, 0.06F, 0.008F + Math.abs(this.currentSpeed) * 0.012F);

        // Responsive Ackermann-style steering
        this.steer = approach(this.steer, driver.xxa, 0.16F);
        float steerRad = this.steer * MAX_STEER_RAD;
        this.yawDelta = -(float) Math.toDegrees(this.currentSpeed * Math.tan(steerRad) / WHEELBASE);

        moveAlongHeading(1.0F, gravityMotion());

        // Off-road dirt roost particles
        if (Math.abs(this.currentSpeed) > 0.20F && this.onGround() && this.level().isClientSide) {
            double yawRad = this.getYRot() * (Math.PI / 180.0D);
            double backX = this.getX() - Math.sin(yawRad) * 2.2D;
            double backZ = this.getZ() + Math.cos(yawRad) * 2.2D;
            this.level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                    backX + (this.random.nextDouble() - 0.5D) * 1.2D,
                    this.getY() + 0.1D,
                    backZ + (this.random.nextDouble() - 0.5D) * 1.2D,
                    0, 0.08D, 0);
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "drive", 4, event -> {
            if (Math.abs(this.visSpeed) > 0.03F) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.tactical_truck.drive"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.tactical_truck.idle"));
        }));
    }
}
