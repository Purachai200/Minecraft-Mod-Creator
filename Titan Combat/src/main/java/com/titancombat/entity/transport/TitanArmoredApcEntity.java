package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.tags.FluidTags;
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
 * Armored Combat 8x8 APC / IFV:
 * Heavy amphibious combat infantry fighting vehicle.
 * True land & water mobility with twin stern waterjets, 360-degree rotating autocannon turret,
 * and firing ports permitting passengers to fire guns (TACZ) freely.
 */
public class TitanArmoredApcEntity extends BaseTransportVehicleEntity {
    // Driver Seat (Inside hollow cab facing forward): seat cushion at model y=14, z=-38, x=10 (driver left)
    // Local: x = 10/16, y = 14/16 - 0.7D, z = 38/16 (+Z forward)
    private static final Vec3 DRIVER_OFFSET = new Vec3(10 / 16.0D, 14 / 16.0D - 0.7D, 38 / 16.0D);

    // Rear Tow / Cargo Anchor for Titan / Exoframe
    private static final Vec3 CARGO_OFFSET = new Vec3(0.0D, 36 / 16.0D, -20 / 16.0D);

    // Passenger Troop Benches (4 Seats inside troop compartment)
    private static final Vec3[] TROOP_SEATS = {
            new Vec3(-10 / 16.0D, 14 / 16.0D - 0.7D, 38 / 16.0D), // Commander seat right
            new Vec3(-8 / 16.0D, 14 / 16.0D - 0.7D, 0 / 16.0D),
            new Vec3(8 / 16.0D, 14 / 16.0D - 0.7D, 0 / 16.0D),
            new Vec3(0.0D, 14 / 16.0D - 0.7D, -16 / 16.0D)
    };

    public TitanArmoredApcEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.3F);
    }

    public static AttributeSupplier.Builder createArmoredApcAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 850.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.48D)
                .add(Attributes.ARMOR, 30.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 15.0D);
    }

    @Override
    public int getCargoCapacity() {
        return 1;
    }

    @Override
    protected boolean shouldTitanKneel() {
        return true;
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return DRIVER_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return CARGO_OFFSET;
    }

    public Vec3 getTroopSeatOffset(int idx) {
        if (idx >= 0 && idx < TROOP_SEATS.length) return TROOP_SEATS[idx];
        return DRIVER_OFFSET;
    }

    @Override
    public int getPlayerSeatCapacity() {
        return 5; // 1 pilot/driver + 4 troops
    }

    @Override
    protected boolean canAddPassenger(net.minecraft.world.entity.Entity passenger) {
        if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(passenger)) {
            return !hasCargo();
        }
        int playerCount = 0;
        for (var p : this.getPassengers()) {
            if (p instanceof Player) playerCount++;
        }
        return playerCount < 5;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        float maxFwd = 0.52F;
        float maxRev = 0.22F;
        float accel = 0.022F;
        float brake = 0.05F;
        float drag = 0.016F;
        float steerRate = 2.6F;

        boolean inWater = this.isInWater();
        if (inWater) {
            maxFwd = 0.36F; // Waterjet swimming mode
            steerRate = 1.8F;
        }

        updateThrottle(driver, maxFwd, maxRev, accel, brake, drag);

        float steer = -driver.xxa;
        if (Math.abs(this.currentSpeed) < 0.03F && steer != 0.0F) {
            this.yawDelta = steer * 1.5F; // Pivot turn
        } else {
            this.yawDelta = steer * steerRate * Math.signum(this.currentSpeed);
        }

        double vertMotion;
        if (inWater) {
            double waterY = this.getFluidHeight(FluidTags.WATER);
            vertMotion = waterY > 0.5D ? 0.08D : (waterY < 0.3D ? -0.05D : 0.0D);
            if (this.level().isClientSide && Math.abs(this.currentSpeed) > 0.05F) {
                double yawRad = Math.toRadians(this.getYRot());
                double bx = this.getX() - Math.sin(yawRad) * -2.6D;
                double bz = this.getZ() + Math.cos(yawRad) * -2.6D;
                this.level().addParticle(ParticleTypes.SPLASH, bx, this.getY() + 0.3D, bz, 0, 0.2D, 0);
            }
        } else {
            vertMotion = gravityMotion();
        }

        moveAlongHeading(0.92F, vertMotion);
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "controller", 2, state -> {
            if (Math.abs(this.currentSpeed) > 0.04F) {
                return state.setAndContinue(RawAnimation.begin().thenLoop("animation.armored_apc.drive"));
            }
            return state.setAndContinue(RawAnimation.begin().thenLoop("animation.armored_apc.idle"));
        }));
    }
}
