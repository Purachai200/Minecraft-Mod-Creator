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
 * Heavy Amphibious Landing Barge: High-capacity watercraft built for ocean crossing and beach assault landings.
 * Features an armored catamaran hull, front drop ramp, and spacious deck capable of ferrying up to 2 heavy Titans.
 */
public class TitanCargoBargeEntity extends BaseTransportVehicleEntity {
    private static final Vec3 HELM_OFFSET = new Vec3(0.0D, 2.2D, -4.0D);
    private static final Vec3 CARGO_OFFSET_A = new Vec3(0.0D, 1.85D, 2.5D);
    private static final Vec3 CARGO_OFFSET_B = new Vec3(0.0D, 1.70D, -1.25D);

    public TitanCargoBargeEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.2F);
    }

    public static AttributeSupplier.Builder createBargeAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 650.0D) // Heavily armored floating fortress
                .add(Attributes.MOVEMENT_SPEED, 0.38D)
                .add(Attributes.ARMOR, 26.0D);
    }

    @Override
    public int getCargoCapacity() {
        return 2; // Can carry up to 2 kneeling Titans on its long deck!
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return HELM_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return slotIndex == 0 ? CARGO_OFFSET_A : CARGO_OFFSET_B;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        float forward = driver.zza;
        float strafe = driver.xxa * 0.35F;

        if (forward < 0.0F) {
            forward *= 0.4F;
        }

        boolean inWater = this.isInWater();
        float maxSpeed = inWater ? 0.72F : 0.25F; // Fast on water, crawls slowly if beached on land
        float targetSpeed = forward * maxSpeed;
        this.currentSpeed = this.currentSpeed + (targetSpeed - this.currentSpeed) * 0.12F;

        // Buoyancy: keep floating smoothly on water surface
        double verticalMotion = travelVector.y;
        if (inWater) {
            verticalMotion = 0.08D; // Gentle water buoyancy push
        }

        this.setSpeed(Math.abs(this.currentSpeed));
        applyBaseTravel(new Vec3(strafe, verticalMotion, this.currentSpeed));

        // Water wake & splash particles
        if (inWater && Math.abs(this.currentSpeed) > 0.1F && this.level().isClientSide) {
            double yawRad = this.getYRot() * (Math.PI / 180.0D);
            double bowX = this.getX() + Math.sin(yawRad) * 4.5D;
            double bowZ = this.getZ() - Math.cos(yawRad) * 4.5D;
            for (int i = 0; i < 3; i++) {
                this.level().addParticle(ParticleTypes.SPLASH,
                        bowX + (this.random.nextDouble() - 0.5D) * 3.0D,
                        this.getY() + 0.1D,
                        bowZ + (this.random.nextDouble() - 0.5D) * 3.0D,
                        (this.random.nextDouble() - 0.5D) * 0.2D, 0.1D, (this.random.nextDouble() - 0.5D) * 0.2D);
            }
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "sail", 4, event -> {
            if (Math.abs(this.currentSpeed) > 0.05F) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_cargo_barge.sail"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_cargo_barge.idle"));
        }));
    }
}
