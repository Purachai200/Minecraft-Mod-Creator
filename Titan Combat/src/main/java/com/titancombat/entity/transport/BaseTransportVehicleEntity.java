package com.titancombat.entity.transport;

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

    public static final EntityDataAccessor<Boolean> DATA_HAS_CARGO =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_RAMP_OPEN =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_HEADLIGHTS =
            SynchedEntityData.defineId(BaseTransportVehicleEntity.class, EntityDataSerializers.BOOLEAN);

    protected float currentSpeed = 0.0F;

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

    public boolean canMountTitan(BaseTitanEntity titan) {
        int count = 0;
        for (Entity p : this.getPassengers()) {
            if (p instanceof BaseTitanEntity) count++;
        }
        return count < getCargoCapacity();
    }

    /** Whether mounted Titans should be locked into a kneeling parking stance (truck/barge) or suspended upright (sky-crane drone). */
    protected boolean shouldTitanKneel() {
        return true;
    }

    /** Mounts a Titan onto this transport vehicle, automatically locking it into a kneeling transport state. */
    public boolean lockTitanToDeck(BaseTitanEntity titan, @Nullable Player pilot) {
        if (!canMountTitan(titan)) {
            if (pilot != null) pilot.sendSystemMessage(Component.literal("§c[LOGISTICS] Transport bay is at maximum capacity!"));
            return false;
        }

        // Lock into kneeling stance for surface decks, or upright standing for aerial hoist
        if (shouldTitanKneel()) {
            titan.setSitting(true);
            titan.setStandbyMode(true);
        } else {
            titan.setSitting(false);
            titan.setStandbyMode(false);
        }
        titan.startRiding(this, true);
        setHasCargo(true);

        this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_PLACE, SoundSource.PLAYERS, 1.4F, 1.2F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.8F, 0.8F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.PISTON_EXTEND, SoundSource.PLAYERS, 1.5F, 0.9F);

        if (pilot != null) {
            pilot.sendSystemMessage(Component.literal("§a[LOGISTICS LOCK] " + titan.getTitanClass().getDisplayName() +
                    " anchored to transport deck with pneumatic magnetic clamps & ratchet straps!"));
        }
        return true;
    }

    /** Releases and unclamps all mounted Titans, allowing them to rise and enter combat. */
    public void releaseMountedTitans(@Nullable Player pilot) {
        boolean released = false;
        for (Entity p : List.copyOf(this.getPassengers())) {
            if (p instanceof BaseTitanEntity titan) {
                titan.stopRiding();
                titan.setSitting(false);
                titan.setStandbyMode(false);
                titan.setDeltaMovement(0, 0.1D, 0);

                // Small boost away from vehicle deck so it doesn't clip
                Vec3 exitDir = Vec3.directionFromRotation(0, this.getYRot() + 180.0F);
                titan.moveTo(titan.getX() + exitDir.x * 2.0D, this.getY(), titan.getZ() + exitDir.z * 2.0D);

                this.level().playSound(null, this.blockPosition(), SoundEvents.PISTON_CONTRACT, SoundSource.PLAYERS, 1.5F, 1.1F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 1.2F, 0.7F);

                if (pilot != null) {
                    pilot.sendSystemMessage(Component.literal("§e[LOGISTICS RELEASE] Clamps unlocked! " +
                            titan.getTitanClass().getDisplayName() + " disembarked and combat-ready."));
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

        // 1. Repair Vehicle Hull
        if (held.is(Items.IRON_INGOT) || held.is(Items.IRON_BLOCK)) {
            if (this.getHealth() < this.getMaxHealth()) {
                if (!this.level().isClientSide) {
                    float healAmount = held.is(Items.IRON_BLOCK) ? 250.0F : 35.0F;
                    this.heal(healAmount);
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

    @Override
    public void tick() {
        super.tick();

        // Sync cargo state
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
                titan.fallDistance = 0.0F;
            }
        }
        if (this.hasCargo() != hasTitan && !this.level().isClientSide) {
            setHasCargo(hasTitan);
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
                this.setYRot(driver.getYRot());
                this.yRotO = this.getYRot();
                this.setXRot(driver.getXRot() * 0.5F);
                this.setRot(this.getYRot(), this.getXRot());
                this.yBodyRot = this.getYRot();
                this.yHeadRot = this.yBodyRot;

                if (this.isControlledByLocalInstance()) {
                    travelTransport(driver, travelVector);
                } else {
                    this.setDeltaMovement(Vec3.ZERO);
                }
                return;
            }
        }
        super.travel(travelVector);
    }

    /** Moves the vehicle using Minecraft's underlying entity physics without re-triggering driver control loop. */
    protected void applyBaseTravel(Vec3 movement) {
        super.travel(movement);
    }

    /** Subclasses implement custom driving/sailing/flight physics. */
    protected abstract void travelTransport(LivingEntity driver, Vec3 travelVector);

    /** Offset for the driver's seat (Seat 0). */
    protected abstract Vec3 getDriverSeatOffset();

    /** Offset for the Titan's cargo mounting position on the deck (Seat 1+). */
    protected abstract Vec3 getTitanCargoOffset(int slotIndex);

    @Override
    protected void positionRider(Entity passenger, Entity.MoveFunction moveFunction) {
        if (!this.hasPassenger(passenger)) return;

        Vec3 localOffset;
        if (passenger instanceof Player) {
            localOffset = getDriverSeatOffset();
        } else if (passenger instanceof BaseTitanEntity) {
            int cargoIndex = 0;
            for (Entity p : this.getPassengers()) {
                if (p == passenger) break;
                if (p instanceof BaseTitanEntity) cargoIndex++;
            }
            localOffset = getTitanCargoOffset(cargoIndex);
        } else {
            localOffset = Vec3.ZERO;
        }

        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double cos = Math.cos(yawRad);
        double sin = Math.sin(yawRad);

        // Transform local (X=strafe, Y=height, Z=forward) to world coordinates
        double worldX = this.getX() + (localOffset.x * cos - localOffset.z * sin);
        double worldY = this.getY() + localOffset.y;
        double worldZ = this.getZ() + (localOffset.x * sin + localOffset.z * cos);

        moveFunction.accept(passenger, worldX, worldY, worldZ);

        if (passenger instanceof BaseTitanEntity titan) {
            titan.setYRot(this.getYRot());
            titan.yRotO = this.getYRot();
            titan.yBodyRot = this.getYRot();
            titan.yHeadRot = this.getYRot();
        }
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        // Vehicle acts as heavy armor for the mounted Titan; absorbs damage
        return super.hurt(source, amount);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("HasCargo", hasCargo());
        tag.putBoolean("RampOpen", isRampOpen());
        tag.putBoolean("Headlights", hasHeadlights());
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("HasCargo")) setHasCargo(tag.getBoolean("HasCargo"));
        if (tag.contains("RampOpen")) setRampOpen(tag.getBoolean("RampOpen"));
        if (tag.contains("Headlights")) setHeadlights(tag.getBoolean("Headlights"));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }
}
