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
    private static final Vec3 DRIVER_OFFSET = new Vec3(0.0D, 2.1D, 3.0D);
    private static final Vec3 CARGO_OFFSET = new Vec3(0.0D, 2.50D, -0.7D); // the loaded pose leans the Titan forward, so this lands its knees on the Z=+28 straps

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
        float forward = driver.zza;
        float strafe = driver.xxa * 0.4F;

        if (forward < 0.0F) {
            forward *= 0.45F; // Slower reverse
        }

        // Heavy vehicle acceleration smoothing
        float targetSpeed = forward * 0.78F;
        this.currentSpeed = this.currentSpeed + (targetSpeed - this.currentSpeed) * 0.15F;

        this.setSpeed(Math.abs(this.currentSpeed));
        applyBaseTravel(new Vec3(strafe, travelVector.y, this.currentSpeed));

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
            if (Math.abs(this.currentSpeed) > 0.05F) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_hauler_truck.drive"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_hauler_truck.idle"));
        }));
    }
}
