package com.titancombat.entity.transport;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechState;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
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
 * Heavy Quad-Rotor Sky-Crane Drone: Heavy aerial transport dropship engineered to airlift Titans across rugged terrain.
 * Capable of VTOL hover, rapid 3D aerial transit (~1.10 blocks/tick), and airborne Combat Hot-Drop deployments.
 */
public class TitanSkyCraneDroneEntity extends BaseTransportVehicleEntity {
    private static final Vec3 COCKPIT_OFFSET = new Vec3(0.0D, 1.4D, 2.8D);
    private static final Vec3 VENTRAL_MOUNT_OFFSET = new Vec3(0.0D, -9.4D, 0.0D); // Titan models are ~100u to the shoulder, so this hangs the shoulders at the Y=-48 clamp pads

    public TitanSkyCraneDroneEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setNoGravity(false);
    }

    @Override
    protected boolean shouldTitanKneel() {
        return false; // Titans are airlifted suspended upright in hot-drop stance
    }

    public static AttributeSupplier.Builder createDroneAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 420.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.45D)
                .add(Attributes.FLYING_SPEED, 0.85D)
                .add(Attributes.ARMOR, 20.0D);
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return COCKPIT_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return VENTRAL_MOUNT_OFFSET;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        float forward = driver.zza;
        float strafe = driver.xxa * 0.5F;

        if (forward < 0.0F) forward *= 0.5F;

        float targetSpeed = forward * 1.10F; // Rapid aerial transit (~80 km/h)
        this.currentSpeed = this.currentSpeed + (targetSpeed - this.currentSpeed) * 0.18F;

        // VTOL Vertical lift: Driver's pitch and jump state
        double vertical = 0.0D;
        if (driver instanceof Player player) {
            // Looking up lifts drone, looking down descends
            double pitchFactor = -Math.sin(driver.getXRot() * (Math.PI / 180.0D)) * 0.6D;
            vertical = pitchFactor;

            // Hover stabilization: counteract gravity when powered
            if (vertical < 0.0D && this.onGround()) {
                vertical = 0.0D;
            } else if (Math.abs(vertical) < 0.05D) {
                vertical = 0.04D; // Steady VTOL hover
            }
        }

        this.setSpeed(Math.abs(this.currentSpeed));
        this.fallDistance = 0.0F; // No fall damage for high-tech sky-crane
        applyBaseTravel(new Vec3(strafe, vertical, this.currentSpeed));

        // Rotor downwash air blast particles
        if (this.level().isClientSide && !this.onGround()) {
            double rx = this.getX();
            double ry = this.getY() - 0.5D;
            double rz = this.getZ();
            for (int i = 0; i < 4; i++) {
                this.level().addParticle(ParticleTypes.CLOUD,
                        rx + (this.random.nextDouble() - 0.5D) * 3.5D,
                        ry,
                        rz + (this.random.nextDouble() - 0.5D) * 3.5D,
                        0, -0.4D, 0);
            }
        }
    }

    /** Airborne Combat Hot-Drop: releases the slung Titan mid-air into an orbital drop posture! */
    public void performAirborneHotDrop(Player pilot) {
        BaseTitanEntity titan = getMountedTitan();
        if (titan == null) {
            pilot.sendSystemMessage(Component.literal("§c[SKY-CRANE] No Titan slung in ventral cargo bay!"));
            return;
        }

        titan.stopRiding();
        titan.setSitting(false);
        titan.setStandbyMode(false);
        titan.setMechState(MechState.DROPPING);
        titan.setDeltaMovement(0, -1.2D, 0); // Fast downward kinetic drop

        this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.PLAYERS, 2.0F, 0.6F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 1.8F, 1.5F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 2.0F, 0.8F);

        pilot.sendSystemMessage(Component.literal("§6[HOT-DROP DEPLOYED] " + titan.getTitanClass().getDisplayName() +
                " released from Sky-Crane! Retro-thrusters primed for combat landing."));
        setHasCargo(false);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "rotors", 2, event -> {
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_skycrane_drone.fly"));
        }));
    }
}
