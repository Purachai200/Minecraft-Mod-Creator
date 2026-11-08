package com.titancombat.entity.transport;

import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;

/**
 * Base class for all heavy strategic logistics & transport vehicles in Titan Combat.
 * Supports multi-passenger seating: Seat 0 for the human pilot/driver, and Seat 1+ for heavy Titans
 * locked into a kneeling cargo transport state.
 */
public abstract class BaseTransportVehicleEntity extends PathfinderMob implements GeoEntity {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public static final int MAX_ENERGY = 100000;

    public static final EntityDataAccessor<Boolean> DATA_HAS_CARGO =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_RAMP_OPEN =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_HEADLIGHTS =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_ENERGY =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.INT);
    /** 0 = intact, 1 = destroyed: rotors/props for aircraft, wheels/running gear for ground vehicles, screws for ships. */
    public static final EntityDataAccessor<Float> DATA_PROPULSION_DAMAGE =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.FLOAT);
    public static final EntityDataAccessor<Integer> DATA_CAMO =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_FACTION =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.INT);

    /** Signed speed along the heading in blocks/tick. */
    protected float currentSpeed = 0.0F;
    private boolean crashing = false;
    /** Degrees the hull turned this tick; carried onto the driver's view like a boat. */
    protected float yawDelta = 0.0F;
    /** Client-only motion read back from position/rotation so wheels, steering and lean also animate on other players' screens. */
    public float visSpeed, visYawRate, wheelRot, wheelRotO;

    public BaseTransportVehicleEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(1.5F); // Easily climbs 1.5-block steps and road obstacles
        this.setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createTransportAttributes() {
        return PathfinderMob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 450.0D) // Heavily reinforced logistics hull
                .add(Attributes.MOVEMENT_SPEED, 0.40D)
                .add(Attributes.ARMOR, 24.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 12.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 1.0D);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_HAS_CARGO, false);
        this.entityData.define(DATA_RAMP_OPEN, false);
        this.entityData.define(DATA_HEADLIGHTS, true);
        this.entityData.define(DATA_ENERGY, MAX_ENERGY);
        this.entityData.define(DATA_FACTION, 0);
        this.entityData.define(DATA_PROPULSION_DAMAGE, 0.0F);
        this.entityData.define(DATA_CAMO, 0);
    }

    public static final int CAMO_COUNT = 5;

    /** 0 factory paint, 1 woodland, 2 desert, 3 arctic, 4 urban (see CamoTextures). */
    public int getCamo() {
        return this.entityData.get(DATA_CAMO);
    }

    public void setCamo(int camo) {
        this.entityData.set(DATA_CAMO, Math.floorMod(camo, CAMO_COUNT));
    }

    public float getPropulsionDamage() {
        return this.entityData.get(DATA_PROPULSION_DAMAGE);
    }

    public void setPropulsionDamage(float damage) {
        this.entityData.set(DATA_PROPULSION_DAMAGE, Mth.clamp(damage, 0.0F, 1.0F));
    }

    public boolean isPropulsionDestroyed() {
        return getPropulsionDamage() >= 1.0F;
    }

    /** Flies on rotors/props: losing them means no lift. */
    public boolean isAircraft() {
        return false;
    }

    /** Where its propulsion sits as a fraction of hull height: rotors on top for aircraft, wheels at the bottom otherwise. */
    protected boolean isPropulsionHit(Vec3 hitPos) {
        double rel = (hitPos.y - this.getY()) / Math.max(0.5D, this.getBbHeight());
        return isAircraft() ? rel > 0.6D : rel < 0.3D;
    }

    public com.titancombat.entity.MechFaction getFaction() {
        return com.titancombat.entity.MechFaction.byId(this.entityData.get(DATA_FACTION));
    }

    public void setFaction(com.titancombat.entity.MechFaction faction) {
        this.entityData.set(DATA_FACTION, faction.getId());
    }

    public int getEnergy() {
        return this.entityData.get(DATA_ENERGY);
    }

    public void setEnergy(int energy) {
        this.entityData.set(DATA_ENERGY, Mth.clamp(energy, 0, getMaxEnergy()));
    }

    public int getMaxEnergy() {
        return MAX_ENERGY;
    }

    public void consumeEnergy(int amount) {
        if (!this.level().isClientSide) {
            setEnergy(getEnergy() - amount);
        }
    }

    public void addEnergy(int amount) {
        if (!this.level().isClientSide) {
            setEnergy(getEnergy() + amount);
        }
    }

    public boolean hasCargo() {
        return this.entityData.get(DATA_HAS_CARGO);
    }

    public void setHasCargo(boolean hasCargo) {
        this.entityData.set(DATA_HAS_CARGO, hasCargo);
    }

    public boolean isRampOpen() {
        return this.entityData.get(DATA_RAMP_OPEN);
    }

    public void setRampOpen(boolean open) {
        this.entityData.set(DATA_RAMP_OPEN, open);
    }

    public boolean hasHeadlights() {
        return this.entityData.get(DATA_HEADLIGHTS);
    }

    public void setHeadlights(boolean on) {
        this.entityData.set(DATA_HEADLIGHTS, on);
    }

    @Nullable
    public Player getDriver() {
        for (Entity p : this.getPassengers()) {
            if (p instanceof Player player) return player;
        }
        return null;
    }

    @Nullable
    public BaseTitanEntity getMountedTitan() {
        for (Entity p : this.getPassengers()) {
            if (p instanceof BaseTitanEntity titan) {
                return titan;
            }
        }
        return null;
    }

    public int getCargoCapacity() {
        return 1;
    }

    public boolean canMountCargo(Entity entity) {
        int count = 0;
        for (Entity p : this.getPassengers()) {
            if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(p)) count++;
        }
        return count < getCargoCapacity();
    }

    public boolean canMountTitan(BaseTitanEntity titan) {
        return canMountCargo(titan);
    }

    /** Cargo hangs under the belly on a cable (Chinook, Osprey) instead of standing on a deck. */
    protected boolean slingsCargo() {
        return false;
    }

    /** Whether mounted Titans / Exoframes should be locked into a kneeling parking stance (truck/barge) or suspended upright (sky-crane drone/chinook). */
    protected boolean shouldTitanKneel() {
        return true;
    }

    /** Mounts a Titan or Obsolete Exoframe onto this transport vehicle, automatically locking it into a transport state. */
    public boolean lockCargoToDeck(Entity cargo, @Nullable Player pilot) {
        if (!canMountCargo(cargo)) {
            if (pilot != null) pilot.sendSystemMessage(Component.literal("§c[LOGISTICS] Transport bay is at maximum capacity!"));
            return false;
        }

        if (cargo instanceof BaseTitanEntity titan) {
            if (shouldTitanKneel()) {
                titan.setSitting(true);
                titan.setStandbyMode(true);
            } else {
                titan.setSitting(false);
                titan.setStandbyMode(false);
            }
        } else if (com.titancombat.util.CrossModCargoHelper.isExoframe(cargo)) {
            com.titancombat.util.CrossModCargoHelper.setExoframeTransportLock(cargo, true);
        }

        cargo.startRiding(this, true);
        setHasCargo(true);

        this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_PLACE, SoundSource.PLAYERS, 1.4F, 1.2F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.8F, 0.8F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.PISTON_EXTEND, SoundSource.PLAYERS, 1.5F, 0.9F);

        if (pilot != null) {
            String name = (cargo instanceof BaseTitanEntity t) ? t.getTitanClass().getDisplayName() : cargo.getType().getDescription().getString();
            pilot.sendSystemMessage(Component.literal("§a[LOGISTICS LOCK] " + name +
                    " anchored to transport deck with pneumatic magnetic clamps & ratchet straps!"));
        }
        return true;
    }

    public boolean lockTitanToDeck(BaseTitanEntity titan, @Nullable Player pilot) {
        return lockCargoToDeck(titan, pilot);
    }

    /** Releases and unclamps all mounted Titans and Exoframes, allowing them to enter combat. */
    public void releaseMountedTitans(@Nullable Player pilot) {
        boolean released = false;
        for (Entity p : List.copyOf(this.getPassengers())) {
            if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(p)) {
                p.stopRiding();
                if (p instanceof BaseTitanEntity titan) {
                    titan.setSitting(false);
                    titan.setStandbyMode(false);
                } else if (com.titancombat.util.CrossModCargoHelper.isExoframe(p)) {
                    com.titancombat.util.CrossModCargoHelper.setExoframeTransportLock(p, false);
                }
                p.setDeltaMovement(0, 0.1D, 0);

                if (!slingsCargo()) {
                    // Small boost away from vehicle deck so it doesn't clip
                    Vec3 exitDir = Vec3.directionFromRotation(0, this.getYRot() + 180.0F);
                    p.moveTo(p.getX() + exitDir.x * 2.0D, this.getY(), p.getZ() + exitDir.z * 2.0D);
                } // a sling load just drops from where it hangs instead of being pulled up into the cabin

                this.level().playSound(null, this.blockPosition(), SoundEvents.PISTON_CONTRACT, SoundSource.PLAYERS, 1.5F, 1.1F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 1.2F, 0.7F);

                if (pilot != null) {
                    String name = (p instanceof BaseTitanEntity t) ? t.getTitanClass().getDisplayName() : p.getType().getDescription().getString();
                    pilot.sendSystemMessage(Component.literal("§e[LOGISTICS RELEASE] Clamps unlocked! " +
                            name + " disembarked and combat-ready."));
                }
                released = true;
            }
        }
        if (released) {
            setHasCargo(false);
        }
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);

        // 1. Refuel Vehicle Engine with Titan Battery / Heavy Battery / Fusion Battery
        if (held.getItem() instanceof com.titancombat.item.TitanBatteryItem) {
            int batteryEnergy = com.titancombat.item.TitanBatteryItem.getEnergy(held);
            if (batteryEnergy <= 0) {
                if (!this.level().isClientSide) {
                    player.sendSystemMessage(Component.literal("§c[LOGISTICS] Battery is completely depleted! Charge it in a Battery Charger."));
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide);
            }
            if (getEnergy() >= getMaxEnergy()) {
                if (!this.level().isClientSide) {
                    player.sendSystemMessage(Component.literal("§e[LOGISTICS] Vehicle fuel cell is already at 100% capacity (" + String.format("%,d", getMaxEnergy()) + " FE)!"));
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide);
            }
            int needed = getMaxEnergy() - getEnergy();
            int transfer = Math.min(needed, batteryEnergy);
            addEnergy(transfer);
            com.titancombat.item.TitanBatteryItem.setEnergy(held, batteryEnergy - transfer);

            this.level().playSound(null, this.blockPosition(), SoundEvents.EXPERIENCE_ORB_PICKUP, SoundSource.PLAYERS, 1.2F, 1.4F);
            this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 0.8F, 1.8F);
            if (!this.level().isClientSide) {
                player.sendSystemMessage(Component.literal(String.format("§a[LOGISTICS] Vehicle Engine Refueled: +%,d FE (%,d / %,d FE | %d%%)",
                        transfer, getEnergy(), getMaxEnergy(), Math.round((float) getEnergy() * 100.0F / (float) getMaxEnergy()))));
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // 2. Repair Vehicle Hull
        if (held.is(Items.IRON_INGOT) || held.is(Items.IRON_BLOCK)) {
            if (this.getHealth() < this.getMaxHealth() || getPropulsionDamage() > 0.0F) {
                if (!this.level().isClientSide) {
                    float healAmount = held.is(Items.IRON_BLOCK) ? 250.0F : 35.0F;
                    this.heal(healAmount);
                    setPropulsionDamage(getPropulsionDamage() - (held.is(Items.IRON_BLOCK) ? 1.0F : 0.15F));
                    if (!player.getAbilities().instabuild) held.shrink(1);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.0F, 1.2F);
                    player.sendSystemMessage(Component.literal("§a[MAINTENANCE] Transport hull repaired: " + (int) this.getHealth() + " / " + (int) this.getMaxHealth() + " HP"));
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide);
            }
        }

        // 2. Unclamp / Release Titans (Shift + Right-Click empty hand)
        if (held.isEmpty() && player.isShiftKeyDown() && hasCargo()) {
            if (!this.level().isClientSide) {
                releaseMountedTitans(player);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // 3. Board as Driver (Right-Click empty hand)
        if (held.isEmpty() && !player.isPassenger()) {
            if (!this.level().isClientSide) {
                if (getDriver() == null) {
                    player.startRiding(this);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_DOOR_OPEN, SoundSource.PLAYERS, 1.2F, 1.0F);
                    player.sendSystemMessage(Component.literal("§a[LOGISTICS] Pilot helm engaged. Ready to transport heavy machinery."));
                }
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        return super.mobInteract(player, hand);
    }

    private boolean collidersSpawned = false;

    /** Ships and hovercraft override this to lay walkable deck tiles (see DeckColliderEntity); whatever stands on them rides along. */
    protected void spawnDeckColliders() {
    }

    @Override
    public void tick() {
        this.yawDelta = 0.0F;
        super.tick();
        if (!this.level().isClientSide && !this.collidersSpawned) {
            this.collidersSpawned = true;
            spawnDeckColliders();
        }
        // A vehicle hull points where it drives, never where a mob body would turn to look
        this.yBodyRot = this.getYRot();
        this.yHeadRot = this.getYRot();

        if (this.level().isClientSide) {
            double yawRad = Math.toRadians(this.getYRot());
            float forward = (float) ((this.getX() - this.xo) * -Math.sin(yawRad) + (this.getZ() - this.zo) * Math.cos(yawRad));
            this.visSpeed += (forward - this.visSpeed) * 0.3F;
            this.visYawRate += (Mth.wrapDegrees(this.getYRot() - this.yRotO) - this.visYawRate) * 0.3F;
            this.wheelRotO = this.wheelRot;
            this.wheelRot += forward / 0.875F; // radians rolled by the truck's 14px-radius wheel
            com.titancombat.client.VehicleEngineSound.ensure(this); // client-only branch, so the class never loads on a server
            float dmg = getPropulsionDamage();
            if (dmg > 0.3F && this.random.nextFloat() < dmg) {
                double top = isAircraft() ? this.getBbHeight() : this.getBbHeight() * 0.6D;
                this.level().addParticle(dmg >= 1.0F ? net.minecraft.core.particles.ParticleTypes.LARGE_SMOKE : net.minecraft.core.particles.ParticleTypes.SMOKE,
                        this.getX() + (this.random.nextDouble() - 0.5D) * this.getBbWidth(), this.getY() + top,
                        this.getZ() + (this.random.nextDouble() - 0.5D) * this.getBbWidth(), 0.0D, 0.08D, 0.0D);
            }
        } else if (isAircraft() && isPropulsionDestroyed()) {
            // Server sees the client-flown wreck land: impact blast (no block damage)
            if (!this.onGround()) {
                this.crashing = true;
            } else if (this.crashing) {
                this.crashing = false;
                this.level().explode(this, this.getX(), this.getY(), this.getZ(), 2.5F, net.minecraft.world.level.Level.ExplosionInteraction.NONE);
            }
        }

        // Sync cargo state & lock docked Mechs into static weight
        boolean hasTitan = false;
        for (Entity p : this.getPassengers()) {
            if (p instanceof BaseTitanEntity titan) {
                hasTitan = true;
                // Keep mounted titan safely in appropriate transport state
                if (shouldTitanKneel()) {
                    if (!titan.isSitting()) {
                        titan.setSitting(true);
                    }
                    if (!titan.isStandbyMode()) {
                        titan.setStandbyMode(true);
                    }
                } else {
                    if (titan.isSitting()) {
                        titan.setSitting(false);
                    }
                }
            }
            if (p instanceof BaseMechEntity mech) {
                // Freeze AI navigation and velocity so docked Mechs act purely as static transport weight
                mech.getNavigation().stop();
                mech.setDeltaMovement(Vec3.ZERO);
                mech.setTarget(null);
                mech.fallDistance = 0.0F;
            }

            // Mobile Repair & Inductive Charging System:
            // Every 20 ticks (1 second), repair HP and recharge docked Titan / Exoframe batteries using vehicle power
            if (!this.level().isClientSide && this.tickCount % 20 == 0 && getEnergy() > 500) {
                com.titancombat.util.CrossModCargoHelper.repairAndChargeCargo(p, getEnergy(), this::consumeEnergy);
            }
        }
        // Drain energy when vehicle is manned
        LivingEntity driver = this.getControllingPassenger();
        if (driver != null && !this.level().isClientSide) {
            boolean moving = Math.abs(this.currentSpeed) > 0.05F || Math.abs(driver.zza) > 0.01F || Math.abs(driver.xxa) > 0.01F;
            int drain = moving ? 4 : 1;
            consumeEnergy(drain);
        }

        if (this.hasCargo() != hasTitan && !this.level().isClientSide) {
            setHasCargo(hasTitan);
        }

        if (!this.level().isClientSide) {
            updateLampsBlockLight();
            tickInteriorPhysics();
        }
    }

    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        for (Entity p : this.getPassengers()) {
            if (p instanceof Player player) return player;
        }
        return null;
    }

    @Override
    public void travel(Vec3 travelVector) {
        if (this.isAlive()) {
            LivingEntity driver = this.getControllingPassenger();
            if (this.isVehicle() && driver != null) {
                // Energy Stall Check: If fuel/energy is 0, engine cuts out
                if (getEnergy() <= 0) {
                    this.currentSpeed = 0.0F;
                    this.setSpeed(0.0F);
                    if (this.tickCount % 40 == 0) {
                        if (driver instanceof Player p && !this.level().isClientSide) {
                            p.displayClientMessage(Component.literal("§c[WARNING] Vehicle Engine Stalled: 0 FE! Insert Titan Battery to refuel."), true);
                            this.level().playSound(null, this.blockPosition(), SoundEvents.FLINTANDSTEEL_USE, SoundSource.PLAYERS, 1.2F, 0.6F);
                        }
                    }
                    super.travel(new Vec3(0, travelVector.y, 0));
                    return;
                }

                if (this.isControlledByLocalInstance()) {
                    if (isAircraft() && isPropulsionDestroyed()) {
                        crashDescent();
                        return;
                    }
                    // Damaged running gear / rotors cap the throttle: 0% damage = full power, 100% = 30%
                    float power = 1.0F - 0.7F * getPropulsionDamage();
                    float zza = driver.zza;
                    driver.zza = zza * power;
                    travelTransport(driver, travelVector);
                    driver.zza = zza;
                    if (isAircraft() && getPropulsionDamage() > 0.5F && !this.onGround()) {
                        // Shot-up rotors can't hold altitude
                        this.move(MoverType.SELF, new Vec3(0.0D, -0.16D * (getPropulsionDamage() - 0.5F), 0.0D));
                    }
                } else {
                    this.setDeltaMovement(Vec3.ZERO);
                }
                return;
            }
        }
        super.travel(travelVector);
    }

    /** Rotors gone: the airframe autorotates down, spinning, and slams in. */
    protected void crashDescent() {
        Vec3 m = this.getDeltaMovement();
        this.setDeltaMovement(m.x * 0.98D, Math.max(-1.2D, Math.min(m.y, 0.0D) - 0.06D), m.z * 0.98D); // no lift left: climb dies at once
        this.yawDelta = 9.0F;
        this.setYRot(this.getYRot() + this.yawDelta);
        this.move(MoverType.SELF, this.getDeltaMovement());
    }

    /** W/S drives toward the target speed, braking first when pushed against the current direction; coasting rolls to a stop. */
    protected void updateThrottle(LivingEntity driver, float maxForward, float maxReverse, float accel, float brake, float drag) {
        float throttle = driver.zza;
        if (throttle != 0.0F && Math.abs(this.currentSpeed) > 0.02F && Math.signum(throttle) != Math.signum(this.currentSpeed)) {
            this.currentSpeed = approach(this.currentSpeed, 0.0F, brake);
        } else if (throttle > 0.0F) {
            this.currentSpeed = approach(this.currentSpeed, maxForward, accel);
        } else if (throttle < 0.0F) {
            this.currentSpeed = approach(this.currentSpeed, -maxReverse, accel);
        } else {
            this.currentSpeed = approach(this.currentSpeed, 0.0F, drag);
        }
    }

    /** Turns the hull by yawDelta, then moves along the heading. grip 1 = tyres hold the line, lower = the hull slides like a boat. */
    protected void moveAlongHeading(float grip, double verticalMotion) {
        this.setYRot(this.getYRot() + this.yawDelta);
        double yawRad = Math.toRadians(this.getYRot());
        Vec3 old = this.getDeltaMovement();
        double vx = Mth.lerp(grip, old.x, -Math.sin(yawRad) * this.currentSpeed);
        double vz = Mth.lerp(grip, old.z, Math.cos(yawRad) * this.currentSpeed);
        this.setDeltaMovement(vx, verticalMotion, vz);
        this.move(net.minecraft.world.entity.MoverType.SELF, this.getDeltaMovement());
        if (this.horizontalCollision) {
            this.currentSpeed *= 0.5F; // ran into a wall
        }
    }

    /** Falling speed for a vehicle that is not floating or flying. */
    protected double gravityMotion() {
        return this.onGround() ? -0.04D : Math.max(-3.0D, (this.getDeltaMovement().y - 0.08D) * 0.98D);
    }

    protected static float approach(float value, float target, float step) {
        return value < target ? Math.min(value + step, target) : Math.max(value - step, target);
    }

    /** Subclasses implement custom driving/sailing/flight physics. */
    protected abstract void travelTransport(LivingEntity driver, Vec3 travelVector);

    /** Offset for the driver's seat (Seat 0). */
    protected abstract Vec3 getDriverSeatOffset();

    /** Player seats (driver + troop seats). Vehicles with troop seats override this. */
    public int getPlayerSeatCapacity() {
        return 1;
    }

    /** Local seat position (+X left, +Y up, +Z forward) for player seat {@code idx}; 0 = driver. */
    public Vec3 getPlayerSeatOffset(int idx) {
        if (idx > 0) {
            if (this instanceof TitanV22OspreyEntity osprey) return osprey.getPassengerTroopOffset(idx - 1);
            if (this instanceof TitanArmoredApcEntity apc) return apc.getTroopSeatOffset(idx - 1);
        }
        return getDriverSeatOffset();
    }

    /** Players currently seated; seat i is taken by the i-th player in passenger order (same order seatOffset uses). */
    public java.util.List<Player> getSeatedPlayers() {
        java.util.List<Player> out = new java.util.ArrayList<>();
        for (Entity p : this.getPassengers()) if (p instanceof Player pl) out.add(pl);
        return out;
    }

    /** Offset for the Titan's cargo mounting position on the deck (Seat 1+). */
    protected abstract Vec3 getTitanCargoOffset(int slotIndex);

    @Override
    public double getPassengersRidingOffset() {
        // Fix vanilla AABB forcing riders onto the roof: set Y-offset strictly inside the cockpit visual model
        return getDriverSeatOffset().y;
    }

    // A machine, not a creature: no footsteps, no "ouch", no fall damage, no lead.
    @Override
    protected void playStepSound(net.minecraft.core.BlockPos pos, net.minecraft.world.level.block.state.BlockState state) {
    }

    @Override
    protected net.minecraft.sounds.SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.IRON_GOLEM_DAMAGE;
    }

    @Override
    protected net.minecraft.sounds.SoundEvent getDeathSound() {
        return SoundEvents.GENERIC_EXPLODE;
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    public boolean canBeLeashed(Player player) {
        return false;
    }

    @Override
    public boolean isPushable() {
        // Heavy military vehicles cannot be pushed by other entities
        return false;
    }

    @Override
    public boolean canCollideWith(Entity other) {
        // Prevent collision with passengers inside the vehicle bounding box
        if (this.hasPassenger(other)) return false;
        if (other instanceof DeckColliderEntity tile && tile.getParent() == this) return false; // own deck tiles
        return super.canCollideWith(other);
    }

    @Override
    protected boolean canAddPassenger(Entity passenger) {
        if (passenger instanceof Player) {
            return getDriver() == null;
        }
        if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(passenger)) {
            int cargoCount = 0;
            for (Entity p : this.getPassengers()) {
                if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(p)) cargoCount++;
            }
            return cargoCount < getCargoCapacity();
        }
        return this.getPassengers().size() < (1 + getCargoCapacity());
    }

    /** Fuselage tilt the model draws from the hull's motion, in radians: + pitch = nose down, + roll = right side up. */
    public float getHullPitch() {
        return 0.0F;
    }

    public float getHullRoll() {
        return 0.0F;
    }

    /** Height in blocks of the bone the hull tilts about. */
    protected double getHullPivotY() {
        return 0.0D;
    }

    /** Nose-down pitch of an aircraft flying forward (client motion; 0 on the server). */
    protected final float flightPitch() {
        return Mth.clamp(this.visSpeed * 0.16F, -0.10F, 0.18F);
    }

    /** Bank into a turn. */
    protected final float flightRoll() {
        return -1.8F * Mth.clamp(this.visYawRate * Mth.DEG_TO_RAD * this.visSpeed * 6.0F, -0.08F, 0.08F);
    }

    @Override
    public net.minecraft.world.phys.AABB getBoundingBoxForCulling() {
        // Hulls are far bigger than their hitbox (the carrier is ~40 blocks long on an 8-block box): cull by the model's reach
        return this.getBoundingBox().inflate(20.0D, 6.0D, 20.0D);
    }

    /** Seat (local frame: +X left, +Y up, +Z forward) for this passenger. */
    private Vec3 seatOffset(Entity passenger) {
        if (passenger instanceof Player player) {
            if (this.getPassengers().indexOf(player) == 0) return getDriverSeatOffset(); // Primary Driver Seat
            // Secondary / Troop Passenger Seats (Osprey, APC, etc.)
            int troopIdx = 0;
            for (Entity p : this.getPassengers()) {
                if (p == player) break;
                if (p instanceof Player) troopIdx++;
            }
            troopIdx = Math.max(0, troopIdx - 1);
            if (this instanceof TitanV22OspreyEntity osprey) return osprey.getPassengerTroopOffset(troopIdx);
            if (this instanceof TitanArmoredApcEntity apc) return apc.getTroopSeatOffset(troopIdx);
            return getDriverSeatOffset();
        }
        if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(passenger)) {
            // Rear Cargo Bed: anchor positions for heavy mechs
            int cargoIndex = 0;
            for (Entity p : this.getPassengers()) {
                if (p == passenger) break;
                if (com.titancombat.util.CrossModCargoHelper.isCargoEligible(p)) cargoIndex++;
            }
            Vec3 localOffset = getTitanCargoOffset(cargoIndex);
            if (slingsCargo()) {
                // Hang the load just under the belly whatever its height, so small Exoframes don't dangle 5 blocks down
                localOffset = new Vec3(localOffset.x, -passenger.getBbHeight() - 0.6D, localOffset.z);
            }
            return localOffset;
        }
        return Vec3.ZERO;
    }

    /** Where a passenger sits in the world: its seat, tilted with the fuselage so it never pokes out of the roof, turned to the heading. */
    public Vec3 seatWorldPos(Entity passenger) {
        Vec3 o = seatOffset(passenger);
        float pitch = getHullPitch(), roll = getHullRoll();
        if (pitch != 0.0F || roll != 0.0F) {
            double h = o.y - getHullPivotY();
            double cp = Math.cos(pitch), sp = Math.sin(pitch);
            double y = h * cp - o.z * sp, z = o.z * cp + h * sp;
            double cr = Math.cos(roll), sr = Math.sin(roll);
            o = new Vec3(o.x * cr + y * sr, getHullPivotY() + y * cr - o.x * sr, z);
        }
        // Standard Minecraft entity local-to-world rotation:
        // localOffset: +X = Left, +Y = Up, +Z = Forward (model +X is also left: GeckoLib mirrors X)
        // Forward unit vector = (-sin(yaw), cos(yaw)), Left unit vector = (cos(yaw), sin(yaw))
        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double cos = Math.cos(yawRad);
        double sin = Math.sin(yawRad);
        return new Vec3(this.getX() + (o.x * cos - o.z * sin), this.getY() + o.y, this.getZ() + (o.x * sin + o.z * cos));
    }

    @Override
    protected void positionRider(Entity passenger, Entity.MoveFunction moveFunction) {
        if (!this.hasPassenger(passenger)) return;

        Vec3 seat = seatWorldPos(passenger);
        moveFunction.accept(passenger, seat.x, seat.y, seat.z);

        if (passenger instanceof Player player) {
            if (this.getPassengers().indexOf(player) == 0) {
                player.yBodyRot = this.getYRot();
            }
        } else if (passenger instanceof LivingEntity living) {
            living.setYRot(this.getYRot());
            living.yRotO = this.getYRot();
            living.yBodyRot = this.getYRot();
            living.yHeadRot = this.getYRot();
            if (living instanceof BaseMechEntity mech) {
                // Completely zero out momentum so docked mechs are purely static cargo weight
                mech.setDeltaMovement(Vec3.ZERO);
                mech.fallDistance = 0.0F;
            } else if (com.titancombat.util.CrossModCargoHelper.isExoframe(living)) {
                living.setDeltaMovement(Vec3.ZERO);
                living.fallDistance = 0.0F;
            }
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        // Vehicle acts as heavy armor for the mounted Titan; absorbs damage
        boolean hurt = super.hurt(source, amount);
        if (hurt && !this.level().isClientSide && !source.is(net.minecraft.tags.DamageTypeTags.IS_FALL)) {
            Vec3 hitPos = source.getSourcePosition();
            float share;
            if (source.is(net.minecraft.tags.DamageTypeTags.IS_EXPLOSION)) {
                share = amount / (this.getMaxHealth() * 0.35F); // blasts shred rotors and tyres wherever they land
            } else if (hitPos != null && isPropulsionHit(hitPos)) {
                share = amount / (this.getMaxHealth() * 0.2F);
            } else {
                share = 0.0F;
            }
            if (share > 0.0F) {
                boolean wasDestroyed = isPropulsionDestroyed();
                setPropulsionDamage(getPropulsionDamage() + share);
                if (!wasDestroyed && isPropulsionDestroyed()) {
                    this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE, SoundSource.NEUTRAL, 2.0F, 0.7F);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_BREAK, SoundSource.NEUTRAL, 1.6F, 0.6F);
                    if (getDriver() != null) {
                        getDriver().displayClientMessage(Component.literal(isAircraft()
                                ? "§c[CRITICAL] ROTOR SYSTEM DESTROYED - LOSING LIFT!" : "§c[CRITICAL] RUNNING GEAR DESTROYED - IMMOBILISED!"), true);
                    }
                }
            }
        }
        return hurt;
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("HasCargo", hasCargo());
        tag.putBoolean("RampOpen", isRampOpen());
        tag.putBoolean("Headlights", hasHeadlights());
        tag.putInt("Energy", getEnergy());
        tag.putInt("Faction", getFaction().getId());
        tag.putFloat("PropulsionDamage", getPropulsionDamage());
        tag.putInt("Camo", getCamo());
        if (!activeLightBlocks.isEmpty()) {
            net.minecraft.nbt.ListTag list = new net.minecraft.nbt.ListTag();
            for (net.minecraft.core.BlockPos pos : activeLightBlocks) {
                list.add(net.minecraft.nbt.NbtUtils.writeBlockPos(pos));
            }
            tag.put("LightBlocks", list);
        }
        if (!fleetVehicleId.isEmpty()) {
            tag.putString("FleetId", fleetVehicleId);
        }
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("HasCargo")) setHasCargo(tag.getBoolean("HasCargo"));
        if (tag.contains("RampOpen")) setRampOpen(tag.getBoolean("RampOpen"));
        if (tag.contains("Headlights")) setHeadlights(tag.getBoolean("Headlights"));
        if (tag.contains("Energy")) setEnergy(tag.getInt("Energy"));
        if (tag.contains("Faction")) setFaction(com.titancombat.entity.MechFaction.byId(tag.getInt("Faction")));
        if (tag.contains("PropulsionDamage")) setPropulsionDamage(tag.getFloat("PropulsionDamage"));
        if (tag.contains("Camo")) setCamo(tag.getInt("Camo"));
        if (tag.contains("LightBlocks", net.minecraft.nbt.Tag.TAG_LIST)) {
            net.minecraft.nbt.ListTag list = tag.getList("LightBlocks", net.minecraft.nbt.Tag.TAG_COMPOUND);
            for (int i = 0; i < list.size(); i++) {
                activeLightBlocks.add(net.minecraft.nbt.NbtUtils.readBlockPos(list.getCompound(i)));
            }
        }
        if (tag.contains("FleetId")) {
            this.fleetVehicleId = tag.getString("FleetId");
        }
    }

    protected String fleetVehicleId = "";
    private final java.util.Set<net.minecraft.core.BlockPos> activeLightBlocks = new java.util.HashSet<>();

    public String getVehicleTypeId() {
        if (fleetVehicleId != null && !fleetVehicleId.isEmpty()) return fleetVehicleId;
        if (this instanceof TitanPatrolBoatEntity) return "fac_patrol";
        if (this instanceof TitanPatrolFrigateEntity) return "corvette_stealth";
        if (this instanceof TitanCargoBargeEntity) return "coaster_freighter";
        if (this instanceof TitanOceanCarrierEntity) return "lpd_assault";
        if (this instanceof TitanC130HerculesEntity) return "c17_airlifter";
        if (this instanceof TitanChinookTransporterEntity) return "mi26_halo";
        if (this instanceof TitanTacticalTruckEntity) return "ural_6x6";
        if (this instanceof TitanHaulerTruckEntity) return "technical_4x4";
        if (this instanceof TitanRepairTruckEntity) return "recovery_6x6";
        if (this instanceof TitanArmoredApcEntity) return "humvee_m1165";
        if (this instanceof TitanV22OspreyEntity) return "mi17_hip";
        if (this instanceof TitanSkyCraneDroneEntity) return "uh60_blackhawk";
        return "technical_4x4";
    }

    public void setFleetVehicleId(String id) {
        this.fleetVehicleId = id;
    }

    public float getYawDelta() {
        return this.yawDelta;
    }

    public Vec3 localToWorld(Vec3 local) {
        float yawRad = this.getYRot() * Mth.DEG_TO_RAD;
        double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
        return new Vec3(this.getX() + local.x * cos - local.z * sin, this.getY() + local.y, this.getZ() + local.x * sin + local.z * cos);
    }

    public Vec3 worldToLocal(Vec3 world) {
        float yawRad = this.getYRot() * Mth.DEG_TO_RAD;
        double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
        double dx = world.x - this.getX(), dy = world.y - this.getY(), dz = world.z - this.getZ();
        return new Vec3(dx * cos + dz * sin, dy, -dx * sin + dz * cos);
    }

    public boolean isInsideInterior(Vec3 worldPos) {
        Vec3 local = worldToLocal(worldPos);
        return com.titancombat.entity.transport.collision.VehicleCollisionManager.isInsideInterior(getVehicleTypeId(), local);
    }

    /** PART C: Places minecraft:light blocks (level 13) in air below ceiling lamps; diffs set to avoid unnecessary updates. */
    protected void updateLampsBlockLight() {
        if (this.level().isClientSide) return;
        java.util.List<Vec3> lamps = com.titancombat.entity.transport.collision.VehicleCollisionManager.getLights(getVehicleTypeId());
        if (lamps.isEmpty()) {
            cleanupLightBlocks();
            return;
        }

        boolean playerNearby = this.level().hasNearbyAlivePlayer(this.getX(), this.getY(), this.getZ(), 64.0D);
        if (!playerNearby || !this.isAlive()) {
            cleanupLightBlocks();
            return;
        }

        java.util.Set<net.minecraft.core.BlockPos> targetPositions = new java.util.HashSet<>();
        for (Vec3 lamp : lamps) {
            Vec3 worldPos = localToWorld(new Vec3(lamp.x, lamp.y - 1.0D, lamp.z));
            targetPositions.add(net.minecraft.core.BlockPos.containing(worldPos));
        }

        if (targetPositions.equals(this.activeLightBlocks)) return;

        java.util.Iterator<net.minecraft.core.BlockPos> it = this.activeLightBlocks.iterator();
        while (it.hasNext()) {
            net.minecraft.core.BlockPos pos = it.next();
            if (!targetPositions.contains(pos)) {
                if (this.level().hasChunkAt(pos)) {
                    net.minecraft.world.level.block.state.BlockState state = this.level().getBlockState(pos);
                    if (state.is(net.minecraft.world.level.block.Blocks.LIGHT)) {
                        this.level().removeBlock(pos, false);
                    }
                }
                it.remove();
            }
        }

        for (net.minecraft.core.BlockPos pos : targetPositions) {
            if (!this.activeLightBlocks.contains(pos)) {
                if (this.level().hasChunkAt(pos)) {
                    net.minecraft.world.level.block.state.BlockState state = this.level().getBlockState(pos);
                    if (state.isAir()) {
                        this.level().setBlock(pos, net.minecraft.world.level.block.Blocks.LIGHT.defaultBlockState()
                                .setValue(net.minecraft.world.level.block.LightBlock.LEVEL, 13)
                                .setValue(net.minecraft.world.level.block.LightBlock.WATERLOGGED, false), 3);
                        this.activeLightBlocks.add(pos);
                    }
                }
            }
        }
    }

    public void cleanupLightBlocks() {
        if (this.activeLightBlocks.isEmpty()) return;
        for (net.minecraft.core.BlockPos pos : this.activeLightBlocks) {
            if (this.level().hasChunkAt(pos)) {
                net.minecraft.world.level.block.state.BlockState state = this.level().getBlockState(pos);
                if (state.is(net.minecraft.world.level.block.Blocks.LIGHT)) {
                    this.level().removeBlock(pos, false);
                }
            }
        }
        this.activeLightBlocks.clear();
    }

    /** PART B: Walking physics inside moving, turning vehicles; carries riders, resolves collision, submarine air pocket. */
    protected void tickInteriorPhysics() {
        if (this.level().isClientSide) return;
        var col = com.titancombat.entity.transport.collision.VehicleCollisionManager.getCollision(getVehicleTypeId());
        if (col.getStaticBoxes().isEmpty()) return;

        net.minecraft.world.phys.AABB searchBox = this.getBoundingBox().inflate(6.0D, 4.0D, 6.0D);
        java.util.List<Player> nearbyPlayers = this.level().getEntitiesOfClass(Player.class, searchBox,
                p -> p.isAlive() && !this.hasPassenger(p) && !p.isSpectator());

        boolean includeDynamic = !isRampOpen();
        boolean isSubmarine = "transport_sub".equals(getVehicleTypeId());
        float turnDelta = this.yawDelta != 0.0F ? this.yawDelta : Mth.wrapDegrees(this.getYRot() - this.yRotO);

        for (Player p : nearbyPlayers) {
            Vec3 local = worldToLocal(p.position());
            Double groundY = col.standY(local.x, local.z, local.y);
            if (groundY != null || isInsideInterior(p.position())) {
                Vec3 worldDelta = p.getDeltaMovement();
                float yawRad = this.getYRot() * Mth.DEG_TO_RAD;
                double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
                double dlx = worldDelta.x * cos + worldDelta.z * sin;
                double dly = worldDelta.y;
                double dlz = -worldDelta.x * sin + worldDelta.z * cos;

                Vec3 resolvedLocal = col.resolveMove(local, new Vec3(dlx, dly, dlz), includeDynamic);
                Vec3 newWorld = localToWorld(resolvedLocal);
                p.setPos(newWorld.x, newWorld.y, newWorld.z);

                if (Math.abs(turnDelta) > 0.001F) {
                    p.setYRot(p.getYRot() + turnDelta);
                    p.yRotO += turnDelta;
                }

                p.fallDistance = 0.0F;
                p.setOnGround(true);

                if (isSubmarine && isInsideInterior(p.position())) {
                    p.setAirSupply(p.getMaxAirSupply());
                    p.clearFire();
                }
            }
        }
    }

    @Override
    public void remove(RemovalReason reason) {
        super.remove(reason);
        cleanupLightBlocks();
    }

    @Override
    public void onRemovedFromWorld() {
        super.onRemovedFromWorld();
        cleanupLightBlocks();
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }
}
