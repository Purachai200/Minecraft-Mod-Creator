package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
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
 * Oceanic Super-Carrier Barge: Massive military logistics carrier designed exclusively for open ocean transit.
 * Strictly operates in water (beaches and stalls if driven onto dry land).
 * Features dual heavy cargo decks capable of ferrying up to 2 large Titans or Obsolete Exoframes.
 */
public class TitanOceanCarrierEntity extends BaseTransportVehicleEntity {
    // Elevated Starboard Bridge Observation Deck: helm at model (x: 26, y: 64, z: -38);
    // In local space: +X = left (x = 26/16), Y = up, +Z = forward (z = +38/16)
    private static final Vec3 BRIDGE_HELM_OFFSET = new Vec3(26 / 16.0D, 64 / 16.0D - 0.7D, 38 / 16.0D);

    // Well Deck Bay 1 (Mid-ship cargo deck, behind command bridge): model z = 5 -> local z = -5/16
    private static final Vec3 BAY_BOW_OFFSET = new Vec3(0.0D, 30 / 16.0D, -5 / 16.0D);
    // Well Deck Bay 2 (Aft cargo deck): model z = 52 -> local z = -52/16
    private static final Vec3 BAY_AFT_OFFSET = new Vec3(0.0D, 30 / 16.0D, -52 / 16.0D);

    public TitanOceanCarrierEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(0.6F); // Low step: cannot climb normal ground obstacles
    }

    public static AttributeSupplier.Builder createOceanCarrierAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 900.0D) // Super-heavy reinforced naval hull
                .add(Attributes.MOVEMENT_SPEED, 0.40D)
                .add(Attributes.ARMOR, 32.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 16.0D);
    }

    @Override
    public int getCargoCapacity() {
        return 2; // Dual-bay heavy carrier
    }

    @Override
    protected boolean shouldTitanKneel() {
        return false; // Titans / Mechs stand upright on the broad carrier well deck
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return BRIDGE_HELM_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return slotIndex == 0 ? BAY_BOW_OFFSET : BAY_AFT_OFFSET;
    }

    @Override
    public void tick() {
        super.tick();

        // Native ship water collision & proportional buoyancy logic
        if (this.isInWater()) {
            double fluidHeight = this.getFluidHeight(FluidTags.WATER);
            double targetWaterline = 0.40D; // Clean realistic draft waterline: hull sits proudly atop water!
            Vec3 motion = this.getDeltaMovement();
            if (fluidHeight > 0.0D) {
                double depthError = fluidHeight - targetWaterline;
                double upwardForce = depthError * 0.15D;
                double newY = (motion.y * 0.78D) + upwardForce;
                this.setDeltaMovement(motion.x, newY, motion.z);
            }
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        // STRICT SEA-ONLY ENFORCEMENT:
        // Must be in water to navigate! If beached on land, the ship's massive weight causes it to stall.
        if (!this.isInWater() && this.onGround()) {
            this.currentSpeed = approach(this.currentSpeed, 0.0F, 0.05F);
            this.moveAlongHeading(1.0F, gravityMotion());
            if (driver instanceof Player player && this.tickCount % 40 == 0 && !this.level().isClientSide) {
                player.displayClientMessage(Component.literal("§c[NAVAL WARNING] Ship is beached on dry land! Water depth required to navigate."), true);
                this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_HIT, SoundSource.PLAYERS, 1.2F, 0.6F);
            }
            return;
        }

        // Naval vessel propulsion physics: heavy inertia, smooth glide
        updateThrottle(driver, 0.55F, 0.20F, 0.012F, 0.02F, 0.004F);

        // Rudder steering (rate depends on current headway speed)
        float turnInput = driver.xxa;
        if (Math.abs(turnInput) > 0.01F) {
            float steerPower = Math.signum(this.currentSpeed) * 0.95F;
            if (Math.abs(this.currentSpeed) < 0.05F) steerPower = Math.signum(turnInput) * 0.35F; // Bow thrusters
            this.yawDelta = -turnInput * steerPower;
        } else {
            this.yawDelta = 0.0F;
        }

        moveAlongHeading(1.0F, gravityMotion());

        // Waterjet stern wake particles & bow spray
        if (Math.abs(this.currentSpeed) > 0.08F && this.isInWater() && this.level().isClientSide) {
            double yawRad = this.getYRot() * (Math.PI / 180.0D);
            // Stern waterjets at z = +6 blocks
            double sternX = this.getX() + Math.sin(yawRad) * 6.0D;
            double sternZ = this.getZ() - Math.cos(yawRad) * 6.0D;
            for (int i = 0; i < 3; i++) {
                this.level().addParticle(ParticleTypes.SPLASH,
                        sternX + (this.random.nextDouble() - 0.5D) * 3.5D,
                        this.getY() + 0.3D,
                        sternZ + (this.random.nextDouble() - 0.5D) * 3.5D,
                        -Math.sin(yawRad) * 0.3D, 0.15D, Math.cos(yawRad) * 0.3D);
                this.level().addParticle(ParticleTypes.BUBBLE_POP,
                        sternX + (this.random.nextDouble() - 0.5D) * 2.5D,
                        this.getY() + 0.1D,
                        sternZ + (this.random.nextDouble() - 0.5D) * 2.5D,
                        0, 0.1D, 0);
            }
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "sail", 4, event -> {
            if (Math.abs(this.visSpeed) > 0.03F) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.ocean_carrier.sail"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.ocean_carrier.idle"));
        }));
    }
}
