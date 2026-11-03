package com.titancombat.entity.transport;

import com.titancombat.util.InputHelper;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
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

import java.util.List;

/**
 * V-22 Osprey VTOL Tiltrotor Transporter:
 * Features tilting wingtip nacelles (VTOL hover vs high-speed forward cruise).
 * Accommodates multiple human passenger seats (troop transport) and ventral sling hook for Titan / Exoframe.
 */
public class TitanV22OspreyEntity extends BaseTransportVehicleEntity {
    // Cockpit Pilot Seat (x: 0, y: 16, z: -74 in model; +Z forward in vehicle coords: z = +74/16)
    private static final Vec3 PILOT_SEAT_OFFSET = new Vec3(0.0D, 16 / 16.0D - 0.7D, 74 / 16.0D);
    // Ventral Sling Hook for Titan / Exoframe: cargo hangs below the belly like the Chinook's sling load
    private static final Vec3 VENTRAL_SLING_OFFSET = new Vec3(0.0D, -7.5D, 0.0D);

    // Passenger Troop Benches inside Cabin (4 Seats along z: -30, -10, 10, 30)
    private static final Vec3[] TROOP_SEATS = {
            new Vec3(-10 / 16.0D, 16 / 16.0D - 0.7D, 20 / 16.0D),
            new Vec3(10 / 16.0D, 16 / 16.0D - 0.7D, 20 / 16.0D),
            new Vec3(-10 / 16.0D, 16 / 16.0D - 0.7D, -10 / 16.0D),
            new Vec3(10 / 16.0D, 16 / 16.0D - 0.7D, -10 / 16.0D)
    };

    public TitanV22OspreyEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.5F);
    }

    public static AttributeSupplier.Builder createV22OspreyAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 650.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.65D)
                .add(Attributes.ARMOR, 24.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 12.0D);
    }

    @Override
    public int getCargoCapacity() {
        return 1; // 1 heavy slung Titan or Exoframe
    }

    @Override
    protected boolean slingsCargo() {
        return true;
    }

    @Override
    protected boolean shouldTitanKneel() {
        return false; // Hangs suspended upright from ventral sling
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return PILOT_SEAT_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return VENTRAL_SLING_OFFSET;
    }

    public Vec3 getPassengerTroopOffset(int troopIndex) {
        if (troopIndex >= 0 && troopIndex < TROOP_SEATS.length) {
            return TROOP_SEATS[troopIndex];
        }
        return PILOT_SEAT_OFFSET;
    }

    @Override
    protected boolean canAddPassenger(net.minecraft.world.entity.Entity passenger) {
        if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(passenger)) {
            return !hasCargo();
        }
        // Total players: 1 Pilot + 4 Troops
        int playerCount = 0;
        for (var p : this.getPassengers()) {
            if (p instanceof Player) playerCount++;
        }
        return playerCount < 5;
    }

    @Override
    public boolean isAircraft() {
        return true;
    }

    @Override
    public void tick() {
        super.tick();
        // Unmanned in the air: settle down onto whatever is below (ground or a carrier deck)
        if (!this.isNoGravity() && this.getControllingPassenger() == null && !this.onGround() && !this.isInWater()) {
            Vec3 motion = this.getDeltaMovement();
            this.setDeltaMovement(motion.x * 0.9D, Math.max(-0.3D, motion.y - 0.04D), motion.z * 0.9D);
            this.move(net.minecraft.world.entity.MoverType.SELF, this.getDeltaMovement());
            this.resetFallDistance();
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        float forward = driver.zza;
        float strafe = driver.xxa;

        boolean jump = InputHelper.isJumping(driver);
        boolean crouch = TitanSkyCraneDroneEntity.clientDescendHeld; // Shift dismounts, so descend uses the Alt key like the Chinook

        // High-speed VTOL flight physics
        float targetSpeed = forward * 0.95F;
        this.currentSpeed = approach(this.currentSpeed, targetSpeed, 0.04F);

        float steerRate = 2.4F;
        this.yawDelta = -strafe * steerRate;
        this.setYRot(this.getYRot() + this.yawDelta);

        double vert = 0.0D;
        if (jump) {
            vert = 0.45D;
            consumeEnergy(4);
        } else if (crouch) {
            vert = -0.45D;
        } else if (!this.onGround()) {
            vert = -0.02D; // gentle aerodynamic hover
        }

        double yawRad = Math.toRadians(this.getYRot());
        double vx = -Math.sin(yawRad) * this.currentSpeed;
        double vz = Math.cos(yawRad) * this.currentSpeed;

        this.setDeltaMovement(vx, vert, vz);
        this.move(net.minecraft.world.entity.MoverType.SELF, this.getDeltaMovement());

        if (this.level().isClientSide && !this.onGround() && this.tickCount % 2 == 0) {
            double wx1 = this.getX() + Math.cos(yawRad) * 4.6D;
            double wz1 = this.getZ() + Math.sin(yawRad) * 4.6D;
            double wx2 = this.getX() - Math.cos(yawRad) * 4.6D;
            double wz2 = this.getZ() - Math.sin(yawRad) * 4.6D;
            this.level().addParticle(ParticleTypes.CLOUD, wx1, this.getY() + 1.8D, wz1, 0, -0.6D, 0);
            this.level().addParticle(ParticleTypes.CLOUD, wx2, this.getY() + 1.8D, wz2, 0, -0.6D, 0);
        }
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "controller", 2, state -> {
            LivingEntity driver = getControllingPassenger();
            if (driver != null || !this.onGround()) {
                if (Math.abs(this.currentSpeed) > 0.4F) {
                    return state.setAndContinue(RawAnimation.begin().thenLoop("animation.v22_osprey.cruise"));
                }
                return state.setAndContinue(RawAnimation.begin().thenLoop("animation.v22_osprey.fly"));
            }
            return state.setAndContinue(RawAnimation.begin().thenLoop("animation.v22_osprey.idle"));
        }));
    }
}
