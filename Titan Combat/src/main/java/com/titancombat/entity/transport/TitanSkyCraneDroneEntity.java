package com.titancombat.entity.transport;

import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechState;
import com.titancombat.util.InputHelper;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
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
 * Heavy Quad-Rotor Sky-Crane Drone: Heavy aerial transport dropship engineered to airlift Titans across rugged terrain.
 * Capable of VTOL hover, rapid 3D aerial transit (~1.10 blocks/tick), and airborne Combat Hot-Drop deployments.
 */
public class TitanSkyCraneDroneEntity extends BaseTransportVehicleEntity {
    /** Descend key held by the local pilot (set every client tick by KeyInputHandler; flight is client-driven). */
    public static boolean clientDescendHeld = false;

    // Pilot seat in the nose pod: cushion top at model (x0, y24, z-55); -0.7 drops the riding player's hips onto it
    private static final Vec3 COCKPIT_OFFSET = new Vec3(0.0D, 24 / 16.0D - 0.7D, 55 / 16.0D);
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
    public void tick() {
        super.tick();

        // When unmanned in the air, gently auto-descend to land (unless noGravity is enabled for aerial hover / docking)
        if (!this.isNoGravity() && this.getControllingPassenger() == null && !this.onGround() && !this.isInWater()) {
            Vec3 motion = this.getDeltaMovement();
            this.setDeltaMovement(motion.x * 0.92D, Math.max(-0.25D, motion.y - 0.04D), motion.z * 0.92D);
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.resetFallDistance();
        }
    }

    @Override
    public boolean isAircraft() {
        return true;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        // W/S pitch the rotors for forward/back thrust (~83 km/h), A/D yaw the airframe
        updateThrottle(driver, 1.15F, 0.5F, 0.03F, 0.05F, 0.02F);
        this.yawDelta = -driver.xxa * 4.0F;

        // Mass-Based Dynamic Thrust: Check if a heavy Mech is docked
        boolean hasMech = false;
        for (Entity p : this.getPassengers()) {
            if (p instanceof BaseMechEntity) {
                hasMech = true;
                break;
            }
        }
        // Increase upward thrust multiplier to compensate for heavy load
        double thrustMultiplier = hasMech ? 1.55D : 1.0D;

        // Ascend / Descend / Hover controls
        boolean ascend = InputHelper.isJumping(driver);
        // Own descend key (not Shift: Shift is the vanilla dismount and throws the pilot out), or look steeply down.
        boolean descend = driver.getXRot() > 25.0F || (this.level().isClientSide && clientDescendHeld);

        double vertical;
        if (ascend) {
            // Apply upward Y-velocity scaled by mass-based thrust
            vertical = 0.32D * thrustMultiplier;
        } else if (descend) {
            // Controlled descent
            vertical = this.onGround() ? 0.0D : -0.25D;
        } else {
            // Steady hover state: counteracting -0.08 gravity so drone maintains fixed altitude
            vertical = 0.0D;
        }

        // Airframe carries momentum through turns instead of snapping onto the new heading
        double climb = Mth.lerp(0.25D, this.getDeltaMovement().y, vertical);
        moveAlongHeading(0.12F, climb);
        this.resetFallDistance();

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
            // Rotors only spin when piloted or airborne/flying; stopped when parked on ground
            if (this.getControllingPassenger() != null || !this.onGround()) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_skycrane_drone.fly"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.titan_skycrane_drone.idle"));
        }));
    }
}
