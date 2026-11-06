package com.titancombat.entity.transport;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
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

import java.util.ArrayList;
import java.util.List;

/**
 * C-130 Hercules: fixed-wing tactical airlifter. Needs a take-off run (no hover), carries one kneeling Titan /
 * Exoframe in the bay, and in flight the release key lowers the ramp and airdrops it under a drogue chute.
 */
public class TitanC130HerculesEntity extends BaseTransportVehicleEntity {
    private static final Vec3 PILOT_OFFSET = new Vec3(0.81D, 3.66D - 0.6D, 9.63D);
    private static final Vec3 BAY_OFFSET = new Vec3(0.0D, 0.875D, 1.75D);
    /** Ramp lip, where airdropped cargo leaves the aircraft. */
    private static final Vec3 RAMP_EXIT = new Vec3(0.0D, -1.5D, -9.0D);
    /** Walkable shell (local +Z forward, model px / 16 from scripts/gen_c130_hercules.py): bay floor top 14 px over z -124..68,
     *  fuselage crown 92 px, wing box 105 px over z +-36, wing panels stepping down from 101 px to 99 px out to x +-236. */
    private static final double BAY_Z_MIN = -4.25D, BAY_Z_MAX = 7.75D;
    private static final float FLOOR_TOP = 0.875F, CROWN_TOP = 5.75F, WING_BOX_TOP = 6.5625F;
    /** Wing panel tiles (centre x, size, top), mirrored to both sides. */
    private static final float[][] WING_TILES = {{4.75F, 4.25F, 6.3125F}, {9.1F, 4.0F, 6.25F}, {12.9F, 3.6F, 6.1875F}};
    private static final float STALL_SPEED = 0.7F;
    private static final float MAX_SPEED = 1.6F;

    /** Loads still under canopy; slowed every tick until they touch down. */
    private final List<Entity> chutes = new ArrayList<>();
    private int rampTimer = 0;
    private boolean collidersSpawned = false;

    public TitanC130HerculesEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.0F);
    }

    public static AttributeSupplier.Builder createC130Attributes() {
        return createTransportAttributes()
                .add(Attributes.MAX_HEALTH, 800.0D)
                .add(Attributes.ARMOR, 20.0D);
    }

    @Override
    public boolean isAircraft() {
        return true;
    }

    @Override
    protected boolean shouldTitanKneel() {
        return true; // a standing Titan doesn't fit the 4.5-block bay
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
        return 2.5D; // "fuselage" bone pivot
    }

    @Override
    protected Vec3 getDriverSeatOffset() {
        return PILOT_OFFSET;
    }

    @Override
    protected Vec3 getTitanCargoOffset(int slotIndex) {
        return BAY_OFFSET;
    }

    private Vec3 local(Vec3 o) {
        double yawRad = Math.toRadians(this.getYRot());
        double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
        return new Vec3(this.getX() + o.x * cos - o.z * sin, this.getY() + o.y, this.getZ() + o.x * sin + o.z * cos);
    }

    /** Ramp down and the load leaves over the lip: under a chute in the air, rolled off onto the ground otherwise. */
    @Override
    public void releaseMountedTitans(Player pilot) {
        setRampOpen(true);
        this.rampTimer = 80;
        boolean airdrop = !this.onGround();
        for (Entity p : List.copyOf(this.getPassengers())) {
            if (!com.titancombat.util.CrossModCargoHelper.isCargoEligible(p)) continue;
            p.stopRiding();
            if (p instanceof com.titancombat.entity.BaseTitanEntity titan) {
                titan.setSitting(false);
                titan.setStandbyMode(false);
            } else {
                com.titancombat.util.CrossModCargoHelper.setExoframeTransportLock(p, false);
            }
            // Clear of the fuselage, whose bay floor is solid
            Vec3 exit = local(RAMP_EXIT);
            p.moveTo(exit.x, airdrop ? exit.y - p.getBbHeight() : this.getY(), exit.z, this.getYRot(), 0.0F);
            p.setDeltaMovement(airdrop ? this.getDeltaMovement().scale(0.5D) : Vec3.ZERO);
            if (airdrop) this.chutes.add(p);
            if (pilot != null) pilot.sendSystemMessage(Component.literal(airdrop ? "§e[AIRDROP] Load away - drogue chute deployed!" : "§e[LOGISTICS RELEASE] Load rolled off the ramp."));
        }
        this.level().playSound(null, this.blockPosition(), airdrop ? SoundEvents.ELYTRA_FLYING : SoundEvents.PISTON_CONTRACT, SoundSource.NEUTRAL, 1.5F, 0.6F);
        setHasCargo(false);
    }

    @Override
    public void tick() {
        super.tick();
        if (!this.level().isClientSide && !this.collidersSpawned) {
            this.collidersSpawned = true;
            // Walkable where the model is: cargo bay floor, fuselage roof fore and aft of the wing, wing box and both wings.
            // Every tile carries whoever stands on it.
            DeckColliderEntity.spawnRow(this, 3.5F, 1.0F, 0.0F, FLOOR_TOP - 1.0F, BAY_Z_MIN, BAY_Z_MAX);
            DeckColliderEntity.spawnRow(this, 4.0F, 0.5F, 0.0F, CROWN_TOP - 0.5F, 2.25D, 10.6D);    // roof over the flight deck and forward bay
            DeckColliderEntity.spawnRow(this, 4.0F, 0.5F, 0.0F, CROWN_TOP - 0.5F, -9.4D, -3.75D);   // roof aft of the wing fairing
            DeckColliderEntity.spawnRow(this, 4.5F, 0.5F, 0.0F, WING_BOX_TOP - 0.5F, -2.25D, 2.25D);
            for (float[] w : WING_TILES) {
                for (int side = -1; side <= 1; side += 2) {
                    DeckColliderEntity.spawnRow(this, w[1], 0.5F, side * w[0], w[2] - 0.5F, -w[1] / 2.0D, w[1] / 2.0D);
                }
            }
        }
        if (this.rampTimer > 0 && --this.rampTimer == 0 && !this.level().isClientSide) setRampOpen(false);

        // Parachute: cap the fall speed and drift until the load lands (server owns the dropped entities)
        this.chutes.removeIf(e -> !e.isAlive() || e.onGround() || e.isInWater());
        for (Entity e : this.chutes) {
            Vec3 m = e.getDeltaMovement();
            e.setDeltaMovement(m.x * 0.9D, Math.max(m.y, -0.28D), m.z * 0.9D);
            e.fallDistance = 0.0F;
            if (this.level() instanceof net.minecraft.server.level.ServerLevel sl && this.tickCount % 3 == 0) {
                sl.sendParticles(ParticleTypes.CLOUD, e.getX(), e.getY() + e.getBbHeight() + 2.0D, e.getZ(), 4, 1.2D, 0.2D, 1.2D, 0.0D);
            }
        }

        // Unmanned in the air: glide down instead of hanging there
        if (this.getControllingPassenger() == null && !this.onGround() && !this.isInWater()) {
            Vec3 m = this.getDeltaMovement();
            this.setDeltaMovement(m.x * 0.98D, Math.max(-0.5D, m.y - 0.03D), m.z * 0.98D);
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.resetFallDistance();
        }
    }

    @Override
    protected void travelTransport(LivingEntity driver, Vec3 travelVector) {
        boolean ground = this.onGround();
        updateThrottle(driver, MAX_SPEED, ground ? 0.12F : 0.0F, ground ? 0.012F : 0.01F, 0.03F, ground ? 0.01F : 0.002F);
        if (!ground) this.currentSpeed = Math.max(this.currentSpeed, 0.2F); // props keep pulling in flight

        float flying = Math.min(1.0F, Math.abs(this.currentSpeed) / STALL_SPEED);
        this.yawDelta = -driver.xxa * (ground ? 1.2F * Math.min(1.0F, Math.abs(this.currentSpeed) * 4.0F) : 1.5F);

        boolean climb = com.titancombat.util.InputHelper.isJumping(driver);
        boolean dive = TitanSkyCraneDroneEntity.clientDescendHeld;
        double vert;
        if (this.currentSpeed >= STALL_SPEED) {
            vert = climb ? 0.28D * flying : dive ? -0.4D : (ground ? 0.0D : 0.0D);
            if (ground && !climb) vert = gravityMotion();
        } else if (ground) {
            vert = gravityMotion();
        } else {
            // Stalled: the wing stops flying and the nose drops
            vert = Math.max(-0.9D, this.getDeltaMovement().y - 0.05D);
            if (driver instanceof Player p && this.tickCount % 30 == 0) p.displayClientMessage(Component.literal("§c[STALL] Airspeed low - throttle up!"), true);
        }
        moveAlongHeading(ground ? 0.95F : 0.6F, vert);
        this.resetFallDistance();
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "controller", 4, state -> {
            if (this.isRampOpen()) return state.setAndContinue(RawAnimation.begin().thenLoop("animation.c130_hercules.ramp_open"));
            if (this.getControllingPassenger() != null || !this.onGround()) return state.setAndContinue(RawAnimation.begin().thenLoop("animation.c130_hercules.fly"));
            return state.setAndContinue(RawAnimation.begin().thenLoop("animation.c130_hercules.idle"));
        }));
    }
}
