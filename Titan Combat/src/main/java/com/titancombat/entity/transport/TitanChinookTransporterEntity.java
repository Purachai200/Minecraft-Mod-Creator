package com.titancombat.entity.transport;

import com.titancombat.util.InputHelper;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
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
 * CH-47 Chinook Heavy Tandem-Rotor Transporter: Military heavy-lift transport helicopter.
 * Features tandem counter-rotating blades, VTOL capability, cockpit with full view,
 * and dual cargo support: internal cargo bay for Exoframes or ventral sling winch for heavy Titans.
 */
public class TitanChinookTransporterEntity extends BaseTransportVehicleEntity {
    // Flight Deck Left Pilot Seat: cushion at model (x: 7, y: 14, z: -66); forward is +Z in vehicle offset convention:
    private static final Vec3 PILOT_OFFSET = new Vec3(7.0D / 16.0D, 14.0D / 16.0D - 0.5D, 69.0D / 16.0D);

    // Ventral Heavy Sling Winch Position Under Belly: x = 0, y = 7, z = 0; hangs Titan/Exoframe below fuselage
    private static final Vec3 SLING_CARGO_OFFSET = new Vec3(0.0D, -7.5D, 0.0D);

    public TitanChinookTransporterEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setNoGravity(false);
    }

    @Override
    protected boolean slingsCargo() {
        return true;
    }

    @Override
    protected boolean shouldTitanKneel() {
        return false; // Titans / Exoframes are airlifted suspended in sling-load or upright
    }

    public static AttributeSupplier.Builder createChinookAttributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 460.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.44D)
                .add(Attributes.FLYING_SPEED, 0.90D)
                .add(Attributes.ARMOR, 22.0D);
    }

    @Override
    public float getHullPitch() {
        return flightPitch();
    }

    @Override
    public float getHullRoll() {
        return flightRoll();
    }

    @Override
    protected double getHullPivotY() {
        return 1.5D; // "fuselage" bone pivot
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return PILOT_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return SLING_CARGO_OFFSET;
    }

    @Override
    public void tick() {
        super.tick();

        // When unmanned in the air, gently auto-descend to land
        if (!this.isNoGravity() && this.getControllingPassenger() == null && !this.onGround() && !this.isInWater()) {
            Vec3 motion = this.getDeltaMovement();
            this.setDeltaMovement(motion.x * 0.90D, Math.max(-0.25D, motion.y - 0.04D), motion.z * 0.90D);
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.resetFallDistance();
        }

        // Tandem rotor downwash particles when near ground
        if (this.level().isClientSide && !this.onGround() && this.getControllingPassenger() != null) {
            Vec3 pos = this.position();
            if (this.tickCount % 2 == 0) {
                double rad = this.getYRot() * (Math.PI / 180.0D);
                // Front and aft rotor centers
                double fX = pos.x - Math.sin(rad) * 2.6D;
                double fZ = pos.z + Math.cos(rad) * 2.6D;
                double aX = pos.x + Math.sin(rad) * 3.2D;
                double aZ = pos.z - Math.cos(rad) * 3.2D;

                this.level().addParticle(ParticleTypes.CLOUD,
                        fX + (this.random.nextDouble() - 0.5D) * 3.0D, this.getY() - 0.5D, fZ + (this.random.nextDouble() - 0.5D) * 3.0D,
                        0, -0.4D, 0);
                this.level().addParticle(ParticleTypes.CLOUD,
                        aX + (this.random.nextDouble() - 0.5D) * 3.0D, this.getY() - 0.5D, aZ + (this.random.nextDouble() - 0.5D) * 3.0D,
                        0, -0.4D, 0);
            }
        }
    }

    @Override
    public boolean isAircraft() {
        return true;
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        // Tandem-Rotor Aerodynamic Flight Mechanics
        float forwardInput = driver.zza; // W / S
        float strafeInput  = driver.xxa; // A / D
        boolean spaceHeld  = InputHelper.isJumping(driver);
        boolean shiftHeld  = TitanSkyCraneDroneEntity.clientDescendHeld;

        // Yaw Rotation via Rudder Pedals
        if (Math.abs(strafeInput) > 0.01F) {
            this.yawDelta = -strafeInput * 1.8F;
        } else {
            this.yawDelta = 0.0F;
        }
        this.setYRot(this.getYRot() + this.yawDelta);

        // Vertical Collective Lift
        double vertSpeed = 0.0D;
        if (spaceHeld) {
            vertSpeed = 0.38D;
        } else if (shiftHeld) {
            vertSpeed = -0.32D;
        } else if (!this.onGround()) {
            vertSpeed = 0.01D; // Hover equilibrium
        }

        // Horizontal Cyclic Thrust
        float targetSpeed = forwardInput * 0.95F;
        this.currentSpeed = approach(this.currentSpeed, targetSpeed, 0.035F);

        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double fwdX = -Math.sin(yawRad) * this.currentSpeed;
        double fwdZ =  Math.cos(yawRad) * this.currentSpeed;

        this.setDeltaMovement(fwdX, vertSpeed, fwdZ);
        this.move(MoverType.SELF, this.getDeltaMovement());
        this.resetFallDistance();

    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "rotors", 2, event -> {
            if (this.getControllingPassenger() != null || !this.onGround()) {
                return event.setAndContinue(RawAnimation.begin().thenLoop("animation.chinook_transporter.fly"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop("animation.chinook_transporter.idle"));
        }));
    }
}
