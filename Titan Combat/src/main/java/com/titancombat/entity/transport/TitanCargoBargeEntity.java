package com.titancombat.entity.transport;

import com.titancombat.entity.BaseMechEntity;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
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
    // Helm seat inside the wheelhouse: cushion top at model (x0, y26, z73); -0.7 drops the riding player's hips onto it
    private static final Vec3 HELM_OFFSET = new Vec3(0.0D, 26 / 16.0D - 0.7D, -73 / 16.0D);
    // Well deck top y10; strap bays at model z-50 (bow) and z6
    private static final Vec3 CARGO_OFFSET_A = new Vec3(0.0D, 10 / 16.0D, 50 / 16.0D);
    private static final Vec3 CARGO_OFFSET_B = new Vec3(0.0D, 10 / 16.0D, -6 / 16.0D);

    public TitanCargoBargeEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.2F);
    }

    @Override
    protected boolean shouldTitanKneel() {
        return false; // Titans stand upright on the amphibious barge well deck with secure deck lashings
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
    public void tick() {
        super.tick();

        // Native ship water collision & proportional buoyancy logic
        if (this.isInWater()) {
            double fluidHeight = this.getFluidHeight(FluidTags.WATER);
            // The barge hull has target waterline equilibrium at 0.55 blocks submerged
            double targetWaterline = 0.55D;

            int mechCount = 0;
            for (Entity p : this.getPassengers()) {
                if (p instanceof BaseMechEntity) mechCount++;
            }

            Vec3 motion = this.getDeltaMovement();
            if (fluidHeight > 0.0D) {
                // Deeper submergence produces a proportionally stronger upward push
                double buoyancyStiffness = 0.08D + (mechCount * 0.025D);
                double depthError = fluidHeight - targetWaterline;
                double upwardForce = depthError * buoyancyStiffness;

                // Vertical damping (0.80) to eliminate bouncing oscillation
                double newY = (motion.y * 0.80D) + upwardForce;
                newY = Mth.clamp(newY, -0.35D, 0.35D);

                this.setDeltaMovement(motion.x, newY, motion.z);
                this.resetFallDistance();
            }
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        boolean inWater = this.isInWater();
        // Twin waterjets on water (~86 km/h), amphibious tracks on land (~43 km/h)
        float maxSpeed = inWater ? 1.2F : 0.6F;
        updateThrottle(driver, maxSpeed, maxSpeed * 0.4F, inWater ? 0.03F : 0.02F, 0.045F, inWater ? 0.008F : 0.03F);

        // Waterjets vector thrust, so the hull can pivot slowly at rest and turns hardest at cruise
        float turnRate = 1.2F + 2.8F * Math.min(1.0F, Math.abs(this.currentSpeed) / maxSpeed);
        this.yawDelta = -driver.xxa * turnRate * (this.currentSpeed < -0.02F ? -1.0F : 1.0F);

        // On water the hull carries momentum sideways through a turn; on land the tracks grip
        moveAlongHeading(inWater ? 0.1F : 0.6F, inWater ? this.getDeltaMovement().y : gravityMotion());

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
            if (Math.abs(this.visSpeed) > 0.03F) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_cargo_barge.sail"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_cargo_barge.idle"));
        }));
    }
}
