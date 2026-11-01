package com.obsolete.entity;

import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.entity.inventory.ExoframeInventory;
import com.obsolete.gui.ExoframeMenu;
import com.obsolete.item.ExoframeAmmoItem;
import com.obsolete.item.ExoframeArmorItem;
import com.obsolete.item.ExoframeWeaponItem;
import com.obsolete.item.ExoframeRocketLauncherItem;
import com.obsolete.item.ExoframeRPG7Item;
import com.obsolete.item.ModItems;
import com.obsolete.network.ExoframeInventorySyncS2CPacket;
import com.obsolete.network.ModNetworking;
import com.obsolete.sound.ModSounds;
import com.obsolete.util.InputHelper;
import com.obsolete.item.ExoframeMiningDrillItem;
import com.obsolete.item.ExoframeChainsawItem;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.storage.loot.BuiltInLootTables;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;

public class ExoframeEntity extends PathfinderMob implements GeoEntity, MenuProvider {

    // Synced Data Accessors
    public static final EntityDataAccessor<Boolean> DATA_IS_CROUCHING =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_IS_MELEEING =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_RECOIL_TICK =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_ARMOR_MASK =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_IS_DYING =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_PRIMARY_COLOR =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_CAMO_PATTERN =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_IS_AIMING =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_FRAME_TIER =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_IS_FLYING =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_IS_BOOSTING =
            SynchedEntityData.defineId(ExoframeEntity.class, EntityDataSerializers.BOOLEAN);

    // Chassis momentum response
    private float smoothedForward = 0.0F;
    private float smoothedStrafe = 0.0F;

    // Modular 7-slot Inventory
    private final ExoframeInventory modularInventory;
    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    // Combat & movement cooldown timers
    private int weaponCooldown = 0;
    private int meleeCooldown = 0;
    private int deathTimer = -1;
    private static final int DEATH_ANIMATION_TICKS = 50; // 2.5 seconds collapse
    private BlockPos lastLightPos = null;

    // Locomotion & effect states
    private int footstepTimer = 0;
    private boolean wasSprintingLastTick = false;
    private int sprintPuffTimer = 0;

    /** Seat cushion height in model px; mirrored as 30.8 - SEAT_LOWER in tools/build_exoframe_geo.py (capsules are fitted to it). */
    public static final double SEAT_CUSHION_Y = 19.8D;

    // Raw Animations
    protected static final RawAnimation ANIM_IDLE = RawAnimation.begin().thenLoop("animation.exoframe.idle");
    protected static final RawAnimation ANIM_WALK = RawAnimation.begin().thenLoop("animation.exoframe.walk");
    protected static final RawAnimation ANIM_SPRINT = RawAnimation.begin().thenLoop("animation.exoframe.sprint");
    protected static final RawAnimation ANIM_JUMP = RawAnimation.begin().thenPlay("animation.exoframe.jump");
    protected static final RawAnimation ANIM_CROUCH = RawAnimation.begin().thenLoop("animation.exoframe.crouch");
    protected static final RawAnimation ANIM_MELEE = RawAnimation.begin().thenPlay("animation.exoframe.melee");
    protected static final RawAnimation ANIM_SHOOT = RawAnimation.begin().thenPlay("animation.exoframe.shoot");
    protected static final RawAnimation ANIM_DEATH = RawAnimation.begin().thenPlayAndHold("animation.exoframe.death");
    /** Render/world scale of the geo model (anime proportions: frame ~2x the pilot's height). */
    public static final float MODEL_SCALE = 1.8F;

    protected static final RawAnimation ANIM_CROUCH_WALK = RawAnimation.begin().thenLoop("animation.exoframe.crouch_walk");
    protected static final RawAnimation ANIM_FLIGHT = RawAnimation.begin().thenLoop("animation.exoframe.flight");
    protected static final RawAnimation ANIM_FLIGHT_BOOST = RawAnimation.begin().thenLoop("animation.exoframe.flight_boost");

    /** Client-only render state: eased 0..1 blend between rest carry and shouldered aim. */
    public float clientAimBlend;
    public float clientAimAge;
    public int clientMeleeTicks;

    public static final String EMOTE_CONTROLLER = "emote";
    /** Emote names as sent by the client; "salute" switches to the left hand when a weapon fills the right. */
    public static final String[] EMOTES = {"salute", "wave", "point", "scan"};

    public ExoframeEntity(EntityType<? extends PathfinderMob> entityType, Level level) {
        super(entityType, level);
        this.setMaxUpStep(2.05F); // long legs at MODEL_SCALE clear 2-block ledges (with floating-point clearance)
        this.modularInventory = new ExoframeInventory(this::syncArmorMaskAndNotify);
        this.setPersistenceRequired();
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 160.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.32D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8D)
                .add(Attributes.ARMOR, 14.0D)
                .add(Attributes.ARMOR_TOUGHNESS, 8.0D)
                .add(Attributes.ATTACK_DAMAGE, 18.0D);
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_IS_CROUCHING, false);
        this.entityData.define(DATA_IS_MELEEING, false);
        this.entityData.define(DATA_RECOIL_TICK, 0);
        this.entityData.define(DATA_ARMOR_MASK, 0);
        this.entityData.define(DATA_IS_DYING, false);
        this.entityData.define(DATA_PRIMARY_COLOR, 0xFFFFFF);
        this.entityData.define(DATA_CAMO_PATTERN, 0);
        this.entityData.define(DATA_IS_AIMING, false);
        this.entityData.define(DATA_FRAME_TIER, 1);
        this.entityData.define(DATA_IS_FLYING, false);
        this.entityData.define(DATA_IS_BOOSTING, false);
    }

    public boolean hasFlightBooster() {
        ItemStack backStack = getModularInventory().getStackInSlot(com.obsolete.entity.inventory.ExoframeArmorSlot.BACK.getIndex());
        if (backStack.isEmpty()) return false;
        return backStack.getItem() instanceof com.obsolete.item.ExoframeFlightBoosterItem
                || backStack.is(com.obsolete.item.ModItems.MODULE_FLIGHT_BOOSTER.get())
                || backStack.getItem().getClass().getName().contains("FlightUnitItem")
                || backStack.getItem().getDescriptionId().contains("flight_unit");
    }

    public boolean isFlying() {
        return this.entityData.get(DATA_IS_FLYING);
    }

    public void setFlying(boolean flying) {
        this.entityData.set(DATA_IS_FLYING, flying);
    }

    public boolean isFlightBoosting() {
        return this.entityData.get(DATA_IS_BOOSTING);
    }

    public void setFlightBoosting(boolean boosting) {
        this.entityData.set(DATA_IS_BOOSTING, boosting);
    }

    public int getFrameTier() {
        return this.entityData.get(DATA_FRAME_TIER);
    }

    public void setFrameTier(int tier) {
        this.entityData.set(DATA_FRAME_TIER, Math.max(0, Math.min(3, tier)));
    }

    public boolean isAiming() {
        return this.entityData.get(DATA_IS_AIMING);
    }

    public void setAiming(boolean aiming) {
        this.entityData.set(DATA_IS_AIMING, aiming);
    }

    public int getPrimaryColor() {
        return this.entityData.get(DATA_PRIMARY_COLOR);
    }

    public void setPrimaryColor(int rgb) {
        this.entityData.set(DATA_PRIMARY_COLOR, rgb);
    }

    public int getCamoPattern() {
        return this.entityData.get(DATA_CAMO_PATTERN);
    }

    public void setCamoPattern(int pattern) {
        this.entityData.set(DATA_CAMO_PATTERN, pattern);
    }

    public ExoframeInventory getModularInventory() {
        return modularInventory;
    }

    public boolean isMechCrouching() {
        return this.entityData.get(DATA_IS_CROUCHING);
    }

    public void setMechCrouching(boolean crouching) {
        this.entityData.set(DATA_IS_CROUCHING, crouching);
        this.refreshDimensions();
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (DATA_IS_CROUCHING.equals(key)) {
            this.refreshDimensions();
        }
    }

    public boolean isMechMeleeing() {
        return this.entityData.get(DATA_IS_MELEEING);
    }

    public boolean isDying() {
        return this.entityData.get(DATA_IS_DYING);
    }

    public int getArmorMask() {
        return this.entityData.get(DATA_ARMOR_MASK);
    }

    public boolean isSlotEquipped(ExoframeArmorSlot slot) {
        return (getArmorMask() & (1 << slot.getIndex())) != 0;
    }

    public boolean isCombatArmored() {
        if (isSlotEquipped(ExoframeArmorSlot.HEAD)) return true;
        ItemStack chest = getEquippedSlot(ExoframeArmorSlot.CHEST);
        return !chest.isEmpty() && !chest.is(ModItems.ARMOR_ROLL_CAGE.get());
    }

    public void syncArmorMaskAndNotify() {
        int mask = 0;
        int slots = modularInventory.getSlots();
        for (int i = 0; i < slots; i++) {
            ItemStack stack = modularInventory.getStackInSlot(i);
            if (!stack.isEmpty()) {
                mask |= (1 << i);
            }
        }
        this.entityData.set(DATA_ARMOR_MASK, mask);

        if (!this.level().isClientSide) {
            for (int i = 0; i < slots; i++) {
                ModNetworking.sendToTracking(new ExoframeInventorySyncS2CPacket(this.getId(), i, modularInventory.getStackInSlot(i)), this);
            }
        }
    }

    @Override
    public void startSeenByPlayer(ServerPlayer player) {
        super.startSeenByPlayer(player);
        // Transmit all equipped modular armor stacks to newly tracking client so armor renders immediately
        int slots = modularInventory.getSlots();
        for (int i = 0; i < slots; i++) {
            ItemStack stack = modularInventory.getStackInSlot(i);
            if (!stack.isEmpty()) {
                ModNetworking.sendToPlayer(new ExoframeInventorySyncS2CPacket(this.getId(), i, stack), player);
            }
        }
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        if (isMechCrouching()) {
            return EntityDimensions.scalable(1.2F * MODEL_SCALE, 1.8F * MODEL_SCALE);
        }
        return EntityDimensions.scalable(1.2F * MODEL_SCALE, 2.2F * MODEL_SCALE);
    }

    public void triggerPilotCameraShake(float intensity, int ticks) {
        if (!this.level().isClientSide && this.getControllingPassenger() instanceof ServerPlayer serverPlayer) {
            com.obsolete.network.ModNetworking.sendToPlayer(new com.obsolete.network.ExoframeCameraShakeS2CPacket(intensity, ticks), serverPlayer);
        } else if (this.level().isClientSide) {
            com.obsolete.client.CameraShakeManager.addShake(intensity, ticks);
        }
    }

    @Override
    public boolean causeFallDamage(float fallDistance, float multiplier, DamageSource source) {
        if (fallDistance > 0.8F) {
            boolean heavy = fallDistance > 2.8F;
            float pitch = 0.95F + (this.random.nextFloat() * 0.1F);
            this.level().playSound(null, this.blockPosition(),
                    heavy ? ModSounds.EXOFRAME_LAND_HEAVY.get() : ModSounds.EXOFRAME_LAND.get(),
                    SoundSource.PLAYERS, heavy ? 2.8F : 1.6F, pitch);

            if (this.level() instanceof ServerLevel serverLevel) {
                if (heavy) {
                    for (int i = 0; i < 16; i++) {
                        double angle = (2.0D * Math.PI * i) / 16.0D;
                        double px = this.getX() + Math.cos(angle) * 2.2D;
                        double pz = this.getZ() + Math.sin(angle) * 2.2D;
                        serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, px, this.getY() + 0.1D, pz, 1, Math.cos(angle) * 0.15D, 0.02D, Math.sin(angle) * 0.15D, 0.02D);
                        serverLevel.sendParticles(ParticleTypes.POOF, px, this.getY() + 0.1D, pz, 1, Math.cos(angle) * 0.1D, 0.05D, Math.sin(angle) * 0.1D, 0.02D);
                    }
                    triggerPilotCameraShake(1.2F, 12);
                } else {
                    serverLevel.sendParticles(ParticleTypes.POOF, this.getX(), this.getY() + 0.1D, this.getZ(), 8, 0.4D, 0.1D, 0.4D, 0.05D);
                    triggerPilotCameraShake(0.4F, 6);
                }
            }
        }
        return false;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean canBeCollidedWith() {
        return true;
    }

    @Override
    public boolean canCollideWith(Entity other) {
        return true;
    }

    @Override
    public boolean isPickable() {
        return true;
    }

    @Override
    public boolean canBeLeashed(Player player) {
        return false;
    }

    @Override
    public boolean isBaby() {
        return false;
    }

    @Override
    public boolean canBreatheUnderwater() {
        return true; // Sealed hydraulic military frame operates underwater
    }

    @Override
    public boolean isPushedByFluid() {
        return false; // Heavy chassis is immune to water currents
    }

    @Override
    public void aiStep() {
        // Vehicle standby behavior: when not piloted, lock chassis & head firmly (no random mob wandering or head twitching)
        if (!this.isVehicle()) {
            this.yHeadRot = this.getYRot();
            this.yBodyRot = this.getYRot();
            this.setSpeed(0.0F);
            this.smoothedForward = 0.0F;
            this.smoothedStrafe = 0.0F;
        }
        super.aiStep();
    }

    @Override
    public boolean showVehicleHealth() {
        // Rendered via custom tactical Sci-Fi HUD
        return false;
    }

    @Override
    public boolean shouldRiderSit() {
        return false; // pilot rides astride; ExoframeRiderPose draws the straddling legs and grip-reaching arms
    }

    @Override
    protected void positionRider(Entity passenger, Entity.MoveFunction moveFunction) {
        if (this.hasPassenger(passenger)) {
            float yawRad = this.getYRot() * Mth.DEG_TO_RAD;
            boolean isFirstPassenger = this.getPassengers().indexOf(passenger) == 0;
            double seat = (SEAT_CUSHION_Y * MODEL_SCALE - 10.0D) / 16.0D;
            double forwardOffset;
            double yOffset;
            if (isFirstPassenger) {
                forwardOffset = -4.3D * MODEL_SCALE / 16.0D;
                yOffset = isMechCrouching() ? seat - 6.0D * MODEL_SCALE / 16.0D : seat;
            } else {
                // Secondary evacuee secured on rear winch cargo mount
                forwardOffset = 18.0D * MODEL_SCALE / 16.0D;
                yOffset = seat + 0.1D;
            }
            double xOffset = -Mth.sin(yawRad) * forwardOffset;
            double zOffset = Mth.cos(yawRad) * forwardOffset;
            moveFunction.accept(passenger, this.getX() + xOffset, this.getY() + yOffset, this.getZ() + zOffset);
        }
    }

    @Override
    public boolean canAddPassenger(Entity passenger) {
        int max = hasItemEquipped(ModItems.MODULE_RESCUE_WINCH.get()) ? 2 : 1;
        return !this.hasPassenger(passenger) && this.getPassengers().size() < max;
    }

    @Override
    protected void addPassenger(Entity passenger) {
        super.addPassenger(passenger);
        // Stand up from park pose when pilot enters
        this.setMechCrouching(false);
        this.setFlying(false);
        this.setFlightBoosting(false);
        this.setAiming(false);
        this.smoothedForward = 0.0F;
        this.smoothedStrafe = 0.0F;
        if (passenger != null) {
            passenger.resetFallDistance();
            passenger.fallDistance = 0.0F;
        }
    }

    @Override
    protected void removePassenger(Entity passenger) {
        super.removePassenger(passenger);
        if (passenger != null) {
            passenger.resetFallDistance();
            passenger.fallDistance = 0.0F;
        }
        if (this.getPassengers().isEmpty()) {
            // When pilot dismounts, terminate all active flight and lower the mech into kneeling park crouch
            this.setFlying(false);
            this.setFlightBoosting(false);
            this.setAiming(false);
            this.setMechCrouching(true);
            this.smoothedForward = 0.0F;
            this.smoothedStrafe = 0.0F;
            this.setDeltaMovement(this.getDeltaMovement().multiply(0.2D, 1.0D, 0.2D));
            if (!this.level().isClientSide) {
                this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_SERVO.get(), SoundSource.PLAYERS, 1.2F, 0.85F);
            }
        }
    }

    @Override
    public Vec3 getDismountLocationForPassenger(LivingEntity passenger) {
        passenger.resetFallDistance();
        passenger.fallDistance = 0.0F;

        // Place dismounting pilot safely 1.35 blocks behind the rear entry of the chassis
        float yawRad = this.getYRot() * Mth.DEG_TO_RAD;
        double rearDist = 1.35D;
        double dx = Mth.sin(yawRad) * rearDist;
        double dz = -Mth.cos(yawRad) * rearDist;
        BlockPos rearPos = BlockPos.containing(this.getX() + dx, this.getY(), this.getZ() + dz);

        Vec3 safePos = net.minecraft.world.entity.vehicle.DismountHelper.findSafeDismountLocation(
                passenger.getType(), this.level(), rearPos, false);
        if (safePos != null) {
            return safePos;
        }

        if (!this.level().getBlockState(rearPos).isSolid() && !this.level().getBlockState(rearPos.above()).isSolid()) {
            return new Vec3(this.getX() + dx, this.getY(), this.getZ() + dz);
        }
        return super.getDismountLocationForPassenger(passenger);
    }

    @Nullable
    @Override
    public LivingEntity getControllingPassenger() {
        Entity passenger = this.getFirstPassenger();
        return passenger instanceof LivingEntity living ? living : null;
    }

    @Override
    public void travel(Vec3 travelVector) {
        if (this.isAlive() && !isDying()) {
            LivingEntity rider = this.getControllingPassenger();
            if (this.isVehicle() && rider != null) {
                // Steer mech with pilot view
                this.setYRot(rider.getYRot());
                this.yRotO = this.getYRot();
                this.setXRot(rider.getXRot() * 0.5F);
                this.setRot(this.getYRot(), this.getXRot());
                this.yBodyRot = this.getYRot();
                this.yHeadRot = this.yBodyRot;

                if (this.isControlledByLocalInstance()) {
                    travelPiloted(rider, travelVector);
                } else if (rider instanceof Player) {
                    this.setDeltaMovement(Vec3.ZERO);
                }
                return;
            }
        }
        super.travel(travelVector);
    }

    protected void travelPiloted(LivingEntity rider, Vec3 travelVector) {
        float targetForward = rider.zza;
        float targetStrafe = rider.xxa * 0.75F;

        if (targetForward <= 0.0F) {
            targetForward *= 0.6F; // Reverse speed penalty
        }

        // Heavy vehicle chassis momentum smoothing
        float accelRate = this.onGround() ? 0.28F : 0.10F;
        smoothedForward += (targetForward - smoothedForward) * accelRate;
        smoothedStrafe += (targetStrafe - smoothedStrafe) * accelRate;

        float speed = (float) this.getAttributeValue(Attributes.MOVEMENT_SPEED);
        if (isAiming()) {
            speed *= 0.65F; // Tactical ADS aim stance speed
        } else if (isMechCrouching()) {
            speed *= 0.50F; // 50% speed while crouching
        } else if (rider.isSprinting() && smoothedForward > 0.1F) {
            speed *= 1.35F; // Sprint boost
        }

        // Flight booster mechanics (Gundam 3D Aerial Free Flight)
        if (hasFlightBooster()) {
            boolean jumping = InputHelper.isJumping(rider);
            // Dedicated descend key (C: Mech Crouch) or pitch dive, leaving Shift exclusively for ground dismount
            boolean crouching = isMechCrouching() || (rider.getXRot() > 25.0F && Math.abs(smoothedForward) > 0.15F);

            if (!isFlying() && !this.onGround() && jumping) {
                setFlying(true);
            }

            if (isFlying()) {
                this.resetFallDistance();

                boolean boosting = rider.isSprinting();
                setFlightBoosting(boosting);

                Vec3 look = rider.getLookAngle();
                float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
                double sin = Math.sin(yawRad);
                double cos = Math.cos(yawRad);

                // High performance Gundam flight speed
                double baseFlightSpeed = 0.44D;
                if (boosting) {
                    baseFlightSpeed = 0.88D; // Supersonic boost dash
                }

                double fwdThrust = smoothedForward * baseFlightSpeed;
                double strafeThrust = smoothedStrafe * (baseFlightSpeed * 0.70D);

                double targetVx = -sin * fwdThrust + cos * strafeThrust;
                double targetVz = cos * fwdThrust + sin * strafeThrust;

                // Vertical flight thrust & hover
                double targetVy;
                if (jumping) {
                    targetVy = boosting ? 0.60D : 0.38D;
                } else if (crouching) {
                    targetVy = -0.42D;
                } else {
                    // Hovering: neutral buoyancy with look-pitch vectoring when moving forward
                    if (Math.abs(smoothedForward) > 0.15F) {
                        targetVy = look.y * fwdThrust * 0.75D;
                    } else {
                        targetVy = 0.0D;
                    }
                }

                Vec3 cur = this.getDeltaMovement();
                double blendH = boosting ? 0.32D : 0.20D;
                double blendV = 0.22D;

                double nextVx = cur.x + (targetVx - cur.x) * blendH;
                double nextVy = cur.y + (targetVy - cur.y) * blendV;
                double nextVz = cur.z + (targetVz - cur.z) * blendH;

                if (this.onGround() && targetVy <= 0.0D && !jumping) {
                    setFlying(false);
                    setFlightBoosting(false);
                }

                this.setDeltaMovement(nextVx, nextVy, nextVz);
                this.move(MoverType.SELF, this.getDeltaMovement());

                if (boosting && this.level().isClientSide) {
                    triggerPilotCameraShake(0.12F, 2);
                }
                return;
            }
        }

        // Amphibious float ring: surface paddling & buoyancy
        if (hasItemEquipped(ModItems.ARMOR_FLOAT_RING.get()) && this.isInWater()) {
            double fluidHeight = this.getFluidHeight(FluidTags.WATER);
            if (fluidHeight > 0.4D) {
                this.setDeltaMovement(this.getDeltaMovement().x, Math.max(this.getDeltaMovement().y, 0.22D), this.getDeltaMovement().z);
            }
            speed *= 1.35F; // Surface paddling boost
        }

        // Space bar jump handling
        if (InputHelper.isJumping(rider) && this.onGround()) {
            this.setDeltaMovement(this.getDeltaMovement().x, 0.62D, this.getDeltaMovement().z);
            this.hasImpulse = true;
            if (!this.level().isClientSide) {
                this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_SERVO.get(), SoundSource.PLAYERS, 1.5F, 1.3F);
            }
        }

        this.setSpeed(speed);
        super.travel(new Vec3(smoothedStrafe, travelVector.y, smoothedForward));
    }

    @Override
    public void tick() {
        super.tick();

        if (weaponCooldown > 0) weaponCooldown--;
        if (meleeCooldown > 0) {
            meleeCooldown--;
            if (meleeCooldown <= 0) {
                this.entityData.set(DATA_IS_MELEEING, false);
            }
        }
        if (this.level().isClientSide) {
            if (isMechMeleeing()) {
                clientMeleeTicks++;
            } else {
                clientMeleeTicks = 0;
            }
        }

        // Dying sequence animation timer
        if (isDying()) {
            if (!this.level().isClientSide) {
                deathTimer--;
                if (deathTimer <= 0) {
                    dropInventoryAndDiscard();
                }
            }
            return;
        }

        // Locomotion, footsteps, servos, exhaust, damage effects
        double horizDistSqr = this.getDeltaMovement().horizontalDistanceSqr();
        boolean isMoving = horizDistSqr > 0.003D;
        boolean isPiloted = this.isVehicle() && this.isAlive() && !isDying();
        if (!isPiloted && isFlying()) {
            setFlying(false);
            setFlightBoosting(false);
        }
        LivingEntity rider = this.getControllingPassenger();
        boolean isSprinting = isMoving && (this.isSprinting() || (rider != null && rider.isSprinting()) || horizDistSqr > 0.035D);

        // Sprint start dark exhaust puff detection
        if (isSprinting && !wasSprintingLastTick) {
            sprintPuffTimer = 6;
        }
        wasSprintingLastTick = isSprinting;

        if (this.level() instanceof ServerLevel serverLevel) {
            // Gundam aerial flight booster thruster VFX & sound
            if (hasFlightBooster() && isFlying()) {
                this.resetFallDistance();

                float yawRad = (float) Math.toRadians(this.getYRot());
                double sin = Math.sin(yawRad);
                double cos = Math.cos(yawRad);

                // Twin nozzles offset: left = -0.38, right = +0.38, rear = -0.52
                double bz = -0.52D;
                double bx = 0.38D;
                double leftX = this.getX() + (-bx * cos + bz * -sin);
                double leftZ = this.getZ() + (-bx * sin + bz * cos);
                double rightX = this.getX() + (bx * cos + bz * -sin);
                double rightZ = this.getZ() + (bx * sin + bz * cos);
                double nozzleY = this.getY() + 1.25D;

                boolean boosting = isFlightBoosting();

                // Thruster flames
                double flameSpeed = boosting ? 0.22D : 0.10D;
                double pvx = -sin * -flameSpeed + (this.random.nextDouble() - 0.5D) * 0.04D;
                double pvz = cos * -flameSpeed + (this.random.nextDouble() - 0.5D) * 0.04D;
                double pvy = boosting ? -0.12D : -0.20D;

                net.minecraft.core.particles.ParticleOptions flameType =
                        boosting ? ParticleTypes.SOUL_FIRE_FLAME : ParticleTypes.FLAME;

                serverLevel.sendParticles(flameType, leftX, nozzleY, leftZ, boosting ? 3 : 1, pvx * 0.5, pvy, pvz * 0.5, 0.02D);
                serverLevel.sendParticles(flameType, rightX, nozzleY, rightZ, boosting ? 3 : 1, pvx * 0.5, pvy, pvz * 0.5, 0.02D);

                if (boosting && this.tickCount % 2 == 0) {
                    serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, leftX, nozzleY, leftZ, 1, 0, 0, 0, 0.05D);
                    serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rightX, nozzleY, rightZ, 1, 0, 0, 0, 0.05D);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, (leftX + rightX) * 0.5, nozzleY, (leftZ + rightZ) * 0.5, 1, pvx, pvy * 0.5, pvz, 0.01D);
                } else if (this.tickCount % 4 == 0) {
                    serverLevel.sendParticles(ParticleTypes.POOF, (leftX + rightX) * 0.5, nozzleY, (leftZ + rightZ) * 0.5, 1, 0, -0.05, 0, 0.01D);
                }

                if (this.tickCount % (boosting ? 10 : 18) == 0) {
                    this.level().playSound(null, this.blockPosition(),
                            SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS,
                            boosting ? 1.4F : 0.85F, boosting ? 1.45F : 1.15F);
                }
            }

            // Footsteps & dust puffs
            if (isMoving && this.onGround()) {
                int stepInterval = isSprinting ? 10 : 18;
                footstepTimer++;
                if (footstepTimer >= stepInterval) {
                    footstepTimer = 0;
                    float stepPitch = 0.92F + this.random.nextFloat() * 0.16F;
                    this.level().playSound(null, this.blockPosition(),
                            isSprinting ? ModSounds.EXOFRAME_STEP_SPRINT.get() : ModSounds.EXOFRAME_STEP.get(),
                            SoundSource.PLAYERS, isSprinting ? 1.4F : 1.0F, stepPitch);

                    // Scaled ground dust puff at foot position
                    boolean leftFoot = (this.tickCount / stepInterval) % 2 == 0;
                    float footAngle = (float) Math.toRadians(this.getYRot() + (leftFoot ? 90 : -90));
                    double fx = this.getX() + Math.cos(footAngle) * 0.45D;
                    double fz = this.getZ() + Math.sin(footAngle) * 0.45D;
                    serverLevel.sendParticles(ParticleTypes.POOF, fx, this.getY() + 0.1D, fz, isSprinting ? 6 : 3, 0.15D, 0.05D, 0.15D, 0.02D);
                    triggerPilotCameraShake(isSprinting ? 0.35F : 0.18F, 4);
                }
            } else {
                footstepTimer = 0;
            }

            // Servo whine following movement velocity
            if (isMoving && this.tickCount % 22 == 0) {
                float servoPitch = 0.85F + (float) Math.min(0.65D, Math.sqrt(horizDistSqr) * 1.5D);
                this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_SERVO.get(), SoundSource.PLAYERS, 0.9F, servoPitch);
            }

            // Engine / APU idle hum while piloted
            if (isPiloted && this.tickCount % 40 == 0) {
                this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_ENGINE_IDLE.get(), SoundSource.PLAYERS, 0.45F, 1.0F);
            }

            // Exhaust smoke from rear manifold
            if (isMoving) {
                boolean emitExhaust = isSprinting || (this.tickCount % 3 == 0);
                if (emitExhaust) {
                    float yawRad = (float) Math.toRadians(this.getYRot());
                    double exX = this.getX() + Math.sin(yawRad) * 0.55D;
                    double exZ = this.getZ() - Math.cos(yawRad) * 0.55D;
                    double exY = this.getY() + 1.8D;
                    if (sprintPuffTimer > 0) {
                        sprintPuffTimer--;
                        serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, exX, exY, exZ, 3, 0.08D, 0.08D, 0.08D, 0.03D);
                    } else {
                        serverLevel.sendParticles(ParticleTypes.SMOKE, exX, exY, exZ, 1, 0.03D, 0.05D, 0.03D, 0.01D);
                    }
                }
            }

            // Water splashes when wading
            if (this.isInWater() && isMoving && this.tickCount % 4 == 0) {
                serverLevel.sendParticles(ParticleTypes.SPLASH, this.getX(), this.getY() + 0.3D, this.getZ(), 8, 0.4D, 0.1D, 0.4D, 0.1D);
                serverLevel.sendParticles(ParticleTypes.BUBBLE, this.getX(), this.getY() + 0.2D, this.getZ(), 4, 0.3D, 0.1D, 0.3D, 0.05D);
            }

            // Low hull health damage sparks & smoke, and cockpit breach alarm
            if (this.isAlive() && !isDying() && this.getHealth() < this.getMaxHealth() * 0.40F) {
                if (this.tickCount % 8 == 0) {
                    double ox = (this.random.nextDouble() - 0.5D) * 0.8D;
                    double oy = 1.0D + this.random.nextDouble() * 0.8D;
                    double oz = (this.random.nextDouble() - 0.5D) * 0.8D;
                    serverLevel.sendParticles(ParticleTypes.SMOKE, this.getX() + ox, this.getY() + oy, this.getZ() + oz, 2, 0.05D, 0.05D, 0.05D, 0.02D);
                    serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, this.getX() + ox, this.getY() + oy, this.getZ() + oz, 1, 0.04D, 0.04D, 0.04D, 0.05D);
                }
                if (this.getHealth() < this.getMaxHealth() * 0.25F && isPiloted && this.tickCount % 50 == 0) {
                    this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_ALARM_LOW_HULL.get(), SoundSource.PLAYERS, 1.0F, 1.0F);
                }
            }
        }

        // Floodlight handling (Rescue Head, Rescue Chest, Roll Cage)
        if (!this.level().isClientSide) {
            boolean hasFloodlights = hasItemEquipped(ModItems.ARMOR_RESCUE_HEAD.get())
                    || hasItemEquipped(ModItems.ARMOR_RESCUE_CHEST.get())
                    || hasItemEquipped(ModItems.ARMOR_ROLL_CAGE.get());
            if (hasFloodlights && this.isAlive() && !isDying()) {
                BlockPos currentLightPos = this.blockPosition().above(2);
                if (!currentLightPos.equals(lastLightPos)) {
                    if (lastLightPos != null && this.level().getBlockState(lastLightPos).is(Blocks.LIGHT)) {
                        this.level().setBlock(lastLightPos, Blocks.AIR.defaultBlockState(), 3);
                    }
                    if (this.level().getBlockState(currentLightPos).isAir()) {
                        this.level().setBlock(currentLightPos, Blocks.LIGHT.defaultBlockState().setValue(BlockStateProperties.LEVEL, 15), 3);
                        lastLightPos = currentLightPos;
                    } else {
                        lastLightPos = null;
                    }
                } else if (lastLightPos != null && !this.level().getBlockState(lastLightPos).is(Blocks.LIGHT) && this.level().getBlockState(lastLightPos).isAir()) {
                    this.level().setBlock(lastLightPos, Blocks.LIGHT.defaultBlockState().setValue(BlockStateProperties.LEVEL, 15), 3);
                }
            } else if (lastLightPos != null) {
                if (this.level().getBlockState(lastLightPos).is(Blocks.LIGHT)) {
                    this.level().setBlock(lastLightPos, Blocks.AIR.defaultBlockState(), 3);
                }
                lastLightPos = null;
            }
        }

        // Active module effects for pilot
        if (this.isVehicle()) {
            if (rider != null) {
                // 1. Diving ballast module: provides rebreather life support (water breathing) while submerged
                if (hasItemEquipped(ModItems.MODULE_DIVING_BALLAST.get()) && this.isInWater()) {
                    if (!this.level().isClientSide) {
                        rider.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 40, 0, false, false, true));
                    }
                    if (InputHelper.isJumping(rider)) {
                        // Blow ballast tanks: buoyant propulsion
                        this.setDeltaMovement(this.getDeltaMovement().add(0, 0.035D, 0));
                    }
                }

                // 2. Rescue sealed capsule: life support (water breathing + fire resistance)
                boolean sealedRescue = hasItemEquipped(ModItems.ARMOR_RESCUE_HEAD.get()) && hasItemEquipped(ModItems.ARMOR_RESCUE_CHEST.get());
                if (sealedRescue && !this.level().isClientSide) {
                    rider.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 40, 0, false, false, true));
                    rider.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 40, 0, false, false, true));
                }

                // 3. Night vision optic module or Cerberus helmet: provides FLIR thermal night-vision
                if (hasItemEquipped(ModItems.MODULE_NIGHT_VISION_OPTIC.get()) || getEquippedSlot(ExoframeArmorSlot.HEAD).is(ModItems.ARMOR_CERBERUS_HEAD.get())) {
                    if (!this.level().isClientSide) {
                        rider.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 220, 0, false, false, false));
                    }
                }
            }
        }

        // Amphibious float ring passive buoyancy (floats mech to water surface even when unpiloted)
        if (hasItemEquipped(ModItems.ARMOR_FLOAT_RING.get()) && this.isInWater()) {
            double fluidHeight = this.getFluidHeight(FluidTags.WATER);
            if (fluidHeight > 0.4D) {
                this.setDeltaMovement(this.getDeltaMovement().x, Math.max(this.getDeltaMovement().y, 0.22D), this.getDeltaMovement().z);
            }
        }

        // Radar scout pulse every 60 ticks
        if (!this.level().isClientSide && this.tickCount % 60 == 0 && hasItemEquipped(ModItems.MODULE_SEARCH_RADAR.get())) {
            int tier = getFrameTier();
            double range = switch (tier) {
                case 0 -> 16.0D;
                case 1 -> 28.0D;
                case 2 -> 40.0D;
                default -> 54.0D;
            };
            AABB radarBox = this.getBoundingBox().inflate(range);
            List<net.minecraft.world.entity.monster.Monster> monsters = this.level().getEntitiesOfClass(net.minecraft.world.entity.monster.Monster.class, radarBox,
                    m -> m.isAlive() && !this.isAlliedTo(m));
            for (var monster : monsters) {
                monster.addEffect(new MobEffectInstance(MobEffects.GLOWING, 60, 0, false, false, false));
            }
            if (!monsters.isEmpty()) {
                this.level().playSound(null, this.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.PLAYERS, 0.8F, 1.8F);
            }
        }
    }

    public boolean hasItemEquipped(Item item) {
        for (int i = 0; i < ExoframeInventory.SLOT_COUNT; i++) {
            if (modularInventory.getStackInSlot(i).is(item)) {
                return true;
            }
        }
        return false;
    }

    public ItemStack getEquippedSlot(ExoframeArmorSlot slot) {
        return modularInventory.getStackInSlot(slot.getIndex());
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        if (isDying()) return InteractionResult.FAIL;

        ItemStack held = player.getItemInHand(hand);
        // Kit Item chassis re-tiering
        if (held.getItem() instanceof com.obsolete.item.ExoframeKitItem kit) {
            if (!this.level().isClientSide) {
                this.setFrameTier(kit.getFrameTier());
                this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_SERVO.get(), SoundSource.PLAYERS, 2.0F, 0.9F);
                String[] tierNames = {"Salvage Militia (Tier 0)", "Standard Military (Tier 1)", "Advanced Special Forces (Tier 2)", "Elite Spec-Ops (Tier 3)"};
                player.displayClientMessage(Component.literal("§6[Chassis Kit Applied] §fFrame upgraded to " + tierNames[kit.getFrameTier()]), true);
                if (!player.getAbilities().instabuild) held.shrink(1);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Custom Paint & Dye System (Dyeing with any of the 16 Minecraft Dyes)
        if (held.getItem() instanceof net.minecraft.world.item.DyeItem dye) {
            if (!this.level().isClientSide) {
                float[] diffuse = dye.getDyeColor().getTextureDiffuseColors();
                int r = (int) (diffuse[0] * 255.0F);
                int g = (int) (diffuse[1] * 255.0F);
                int b = (int) (diffuse[2] * 255.0F);
                setPrimaryColor((r << 16) | (g << 8) | b);

                if (!player.getAbilities().instabuild) {
                    held.shrink(1);
                }
                this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.2F, 1.4F);
                player.displayClientMessage(Component.translatable("message.obsolete.color_changed", dye.getDyeColor().getName().toUpperCase()), true);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Cleaning paint & camo back to factory finish
        if (held.is(net.minecraft.world.item.Items.SPONGE) || held.is(net.minecraft.world.item.Items.WATER_BUCKET)) {
            if (getCamoPattern() != 0 || getPrimaryColor() != 0xFFFFFF) {
                if (!this.level().isClientSide) {
                    setCamoPattern(0);
                    setPrimaryColor(0xFFFFFF);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.BUCKET_EMPTY, SoundSource.PLAYERS, 1.0F, 1.0F);
                    player.displayClientMessage(Component.literal("§b[Exoframe] Cleaned paint & camouflage back to Factory Finish."), true);
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide);
            }
        }

        // Camouflage application using intuitive items
        int newCamo = -1;
        String camoName = "";
        if (held.is(net.minecraft.world.item.Items.VINE) || held.is(net.minecraft.world.item.Items.OAK_LEAVES)) {
            newCamo = 5; camoName = "Jungle Tigerstripe";
        } else if (held.is(net.minecraft.world.item.Items.SAND) || held.is(net.minecraft.world.item.Items.SANDSTONE)) {
            newCamo = 2; camoName = "Desert Nomad";
        } else if (held.is(net.minecraft.world.item.Items.FLINT) || held.is(net.minecraft.world.item.Items.INK_SAC)) {
            newCamo = 3; camoName = "Urban Hex";
        } else if (held.is(net.minecraft.world.item.Items.SNOWBALL) || held.is(net.minecraft.world.item.Items.SNOW_BLOCK)) {
            newCamo = 4; camoName = "Arctic Blizzard";
        } else if (held.is(net.minecraft.world.item.Items.HONEYCOMB)) {
            newCamo = 6; camoName = "Industrial Hazard";
        }

        if (newCamo != -1) {
            if (!this.level().isClientSide) {
                setCamoPattern(newCamo);
                if (!player.getAbilities().instabuild) held.shrink(1);
                this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.0F, 1.6F);
                player.displayClientMessage(Component.literal("§a[Exoframe] Applied Camouflage: §e" + camoName), true);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Shift + Right Click opens Modular Inventory GUI
        if (player.isShiftKeyDown()) {
            if (!this.level().isClientSide && player instanceof ServerPlayer serverPlayer) {
                NetworkHooks.openScreen(serverPlayer, this, buf -> buf.writeInt(this.getId()));
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Worksite block placement while piloting
        if (this.isVehicle() && this.hasPassenger(player) && hasItemEquipped(ModItems.ARMOR_ROLL_CAGE.get())) {
            ItemStack heldItem = player.getItemInHand(hand);
            if (heldItem.getItem() instanceof BlockItem blockItem) {
                Vec3 eyePos = player.getEyePosition();
                Vec3 look = player.getLookAngle();
                Vec3 end = eyePos.add(look.scale(5.5D));
                BlockHitResult hit = this.level().clip(new ClipContext(eyePos, end, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, player));
                if (hit.getType() == HitResult.Type.BLOCK) {
                    BlockPos targetPos = hit.getBlockPos().relative(hit.getDirection());
                    if (this.level().getBlockState(targetPos).canBeReplaced()) {
                        if (!this.level().isClientSide) {
                            BlockState placeState = blockItem.getBlock().defaultBlockState();
                            this.level().setBlock(targetPos, placeState, 3);
                            SoundType soundType = placeState.getSoundType();
                            this.level().playSound(null, targetPos, soundType.getPlaceSound(), SoundSource.BLOCKS, (soundType.getVolume() + 1.0F) / 2.0F, soundType.getPitch() * 0.8F);
                            if (!player.getAbilities().instabuild) {
                                heldItem.shrink(1);
                            }
                        }
                        return InteractionResult.sidedSuccess(this.level().isClientSide);
                    }
                }
            }
        }

        // Mount / Ride Mech
        if (!player.isPassenger() && this.canAddPassenger(player)) {
            if (!this.level().isClientSide) {
                player.startRiding(this);
                this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_SERVO.get(), SoundSource.PLAYERS, 1.5F, 1.1F);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        return super.mobInteract(player, hand);
    }

    private boolean shoulderMissileAlt = false;

    /**
     * Weapon firing server execution.
     */
    public void setWeaponCooldown(int cd) {
        this.weaponCooldown = cd;
    }

    public boolean fireEquippedWeapon(ServerPlayer pilot) {
        if (weaponCooldown > 1 || isDying()) return false;

        ItemStack weaponStack = modularInventory.getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
        if (weaponStack.is(ModItems.EXOFRAME_STUN_BATON.get())) {
            performMeleeAttack(pilot);
            return true;
        }
        if (weaponStack.is(ModItems.EXOFRAME_FISHING_ROD.get())) {
            return performFishing(pilot);
        }
        if (weaponStack.getItem() instanceof ExoframeWeaponItem weaponItem) {
            boolean fired = weaponItem.performFire(this, pilot);
            if (fired) {
                int cd = weaponItem.getFireCooldownTicks();
                if (hasItemEquipped(ModItems.ARMOR_ROLL_CAGE.get()) &&
                        (weaponItem instanceof ExoframeMiningDrillItem || weaponItem instanceof ExoframeChainsawItem)) {
                    cd = Math.max(2, (int) (cd / 2.5F));
                }
                weaponCooldown = cd;
                return true;
            }
        } else {
            ItemStack utilStack = modularInventory.getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
            boolean hasShoulderWeapon = utilStack.is(ModItems.MODULE_SHOULDER_MISSILE.get())
                    || utilStack.is(ModItems.MODULE_TWIN_MANPADS.get())
                    || utilStack.getItem() instanceof ExoframeRocketLauncherItem
                    || utilStack.getItem() instanceof ExoframeRPG7Item;

            if (hasShoulderWeapon) {
                return fireShoulderMissile(pilot);
            }

            // No weapon equipped: default to melee punch
            performMeleeAttack(pilot);
        }
        return false;
    }

    /**
     * Computes the point the pilot is looking at (either block collision or targeted entity within 64 blocks,
     * or at 64 blocks in empty sky) for authentic military FCS reticle convergence.
     */
    public static Vec3 computeTargetConvergence(Level level, ServerPlayer pilot, ExoframeEntity exoframe) {
        Vec3 eyePos = pilot.getEyePosition();
        Vec3 look = pilot.getLookAngle();
        Vec3 rayEnd = eyePos.add(look.scale(64.0D));
        HitResult blockHit = level.clip(new ClipContext(eyePos, rayEnd, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, pilot));
        Vec3 target = blockHit.getType() != HitResult.Type.MISS ? blockHit.getLocation() : rayEnd;

        AABB searchBox = new AABB(eyePos, target).inflate(1.5D);
        EntityHitResult entityHit = ProjectileUtil.getEntityHitResult(level, pilot, eyePos, target, searchBox,
                e -> !e.isSpectator() && e.isPickable() && e != exoframe && e != pilot);
        if (entityHit != null) {
            target = entityHit.getLocation();
        }
        return target;
    }

    /**
     * Fires a rocket or anti-tank guided missile from the shoulder-mounted launcher pods.
     * Alternates left and right shoulder pods with authentic launch smoke and sound.
     */
    public boolean fireShoulderMissile(ServerPlayer pilot) {
        // Check for AT_ROCKET in utility slot or pilot inventory
        boolean hasAmmo = false;
        ItemStack utilStack = modularInventory.getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilStack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.AT_ROCKET) {
            utilStack.shrink(1);
            hasAmmo = true;
        } else {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack stack = pilot.getInventory().getItem(i);
                if (stack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.AT_ROCKET) {
                    stack.shrink(1);
                    hasAmmo = true;
                    break;
                }
            }
        }

        if (!hasAmmo) {
            pilot.displayClientMessage(Component.translatable("message.obsolete.out_of_ammo_rocket").withStyle(ChatFormatting.RED), true);
            return false;
        }

        Level level = this.level();
        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();

        // Alternate left shoulder (+0.75 blocks) and right shoulder (-0.75 blocks) pod launch
        double sideOffset = shoulderMissileAlt ? -0.75D : 0.75D;
        shoulderMissileAlt = !shoulderMissileAlt;

        Vec3 podPos = this.position().add(0, 2.25D * MODEL_SCALE, 0)
                .add(right.scale(sideOffset * MODEL_SCALE))
                .add(forward.scale(0.55D * MODEL_SCALE));

        Vec3 target = computeTargetConvergence(level, pilot, this);
        Vec3 shootDir = target.subtract(podPos).normalize();

        ExoframeRocketEntity rocket = new ExoframeRocketEntity(level, pilot);
        rocket.setPos(podPos.x, podPos.y, podPos.z);
        rocket.shoot(shootDir.x, shootDir.y, shootDir.z, 2.5F, 0.08F);
        level.addFreshEntity(rocket);

        com.obsolete.item.ExoframeWeaponItem.spawnRocketBackblast(level, podPos, forward);

        level.playSound(null, this.blockPosition(), ModSounds.EXOFRAME_ROCKET_FIRE.get(), SoundSource.PLAYERS, 3.2F, 1.0F);
        this.triggerRecoilAnim();
        triggerPilotCameraShake(0.7F, 6);
        this.weaponCooldown = 25; // 1.25s cooldown between shoulder missile salvos
        return true;
    }

    /**
     * Melee attack execution (Phase 6).
     */
    public void performMeleeAttack(ServerPlayer pilot) {
        if (meleeCooldown > 0 || isDying()) return;

        ItemStack mainWpn = modularInventory.getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
        boolean isStunBaton = mainWpn.is(ModItems.EXOFRAME_STUN_BATON.get());
        boolean isBlade = mainWpn.is(ModItems.EXOFRAME_VIBRO_BLADE.get());

        meleeCooldown = isStunBaton ? 12 : (isBlade ? 10 : 15);
        this.entityData.set(DATA_IS_MELEEING, true);

        // Find enemies in front cone (sweep hitbox ~2.8 blocks)
        Vec3 forward = pilot.getLookAngle().normalize();
        Vec3 strikeCenter = this.position().add(0, 1.2D * MODEL_SCALE, 0).add(forward.scale(1.8D * MODEL_SCALE));
        double reach = 1.4D * MODEL_SCALE, high = 1.2D * MODEL_SCALE;
        AABB strikeBox = new AABB(strikeCenter.x - reach, strikeCenter.y - high, strikeCenter.z - reach,
                strikeCenter.x + reach, strikeCenter.y + high, strikeCenter.z + reach);

        List<LivingEntity> targets = this.level().getEntitiesOfClass(LivingEntity.class, strikeBox,
                e -> e != this && e != pilot && !this.isAlliedTo(e));

        float meleeDamage = isBlade ? 34.0F : (isStunBaton ? 18.0F : 24.0F);
        for (LivingEntity target : targets) {
            target.hurt(this.damageSources().mobAttack(this), meleeDamage);
            if (isStunBaton) {
                target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1, false, true, true));
                target.addEffect(new MobEffectInstance(MobEffects.WEAKNESS, 80, 0, false, true, true));
            }
            Vec3 kb = forward.scale(isStunBaton ? 0.7D : (isBlade ? 1.0D : 1.4D)).add(0, 0.35D, 0);
            target.setDeltaMovement(kb);
            target.hurtMarked = true;
        }

        Level level = this.level();
        if (isStunBaton) {
            level.playSound(null, this.blockPosition(), ModSounds.WEAPON_STUN_ZAP.get(), SoundSource.PLAYERS, 2.4F, 1.0F);
        } else if (isBlade) {
            level.playSound(null, this.blockPosition(), ModSounds.WEAPON_BLADE_SWING.get(), SoundSource.PLAYERS, 2.8F, 1.0F);
        } else {
            level.playSound(null, this.blockPosition(), ModSounds.EXOFRAME_MELEE.get(), SoundSource.PLAYERS, 3.2F, 0.95F);
        }

        if (!targets.isEmpty()) {
            if (isBlade) {
                level.playSound(null, this.blockPosition(), ModSounds.WEAPON_BLADE_IMPACT.get(), SoundSource.PLAYERS, 3.0F, 1.0F);
            } else {
                level.playSound(null, this.blockPosition(), ModSounds.WEAPON_MELEE_IMPACT.get(), SoundSource.PLAYERS, 3.4F, 1.0F);
            }
            triggerPilotCameraShake(0.6F, 6);
        }

        if (level instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(isStunBaton ? ParticleTypes.ELECTRIC_SPARK : (isBlade ? ParticleTypes.CRIT : ParticleTypes.SWEEP_ATTACK),
                    strikeCenter.x, strikeCenter.y, strikeCenter.z, isStunBaton ? 10 : (isBlade ? 12 : 3), 0.2D, 0.2D, 0.2D, 0.05D);
        }
    }

    public boolean performFishing(ServerPlayer pilot) {
        if (!(this.level() instanceof ServerLevel serverLevel)) return false;
        // Needs open water beside or below the mech: no fishing on dry land.
        BlockPos at = this.blockPosition();
        BlockPos water = BlockPos.betweenClosedStream(at.offset(-5, -4, -5), at.offset(5, 1, 5))
                .filter(pos -> serverLevel.getFluidState(pos).is(FluidTags.WATER))
                .findFirst().map(BlockPos::immutable).orElse(null);
        if (water == null) {
            serverLevel.playSound(null, at, SoundEvents.FISHING_BOBBER_THROW, SoundSource.PLAYERS, 0.6F, 0.6F);
            this.weaponCooldown = 10;
            return false;
        }
        ItemStack weaponStack = modularInventory.getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
        LootParams params = new LootParams.Builder(serverLevel)
                .withParameter(LootContextParams.ORIGIN, Vec3.atCenterOf(water))
                .withParameter(LootContextParams.TOOL, weaponStack)
                .withParameter(LootContextParams.THIS_ENTITY, this)
                .withLuck(pilot.getLuck())
                .create(LootContextParamSets.FISHING);
        for (ItemStack loot : serverLevel.getServer().getLootData().getLootTable(BuiltInLootTables.FISHING).getRandomItems(params)) {
            if (!pilot.getInventory().add(loot)) {
                pilot.drop(loot, false);
            }
        }
        serverLevel.playSound(null, water, SoundEvents.FISHING_BOBBER_RETRIEVE, SoundSource.PLAYERS, 1.5F, 1.0F);
        serverLevel.sendParticles(ParticleTypes.SPLASH, water.getX() + 0.5D, water.getY() + 1.0D, water.getZ() + 0.5D, 15, 0.5D, 0.2D, 0.5D, 0.1D);
        this.weaponCooldown = 100;   // one catch per 5 s, roughly a vanilla rod's pace
        return true;
    }

    public void triggerRecoilAnim() {
        this.entityData.set(DATA_RECOIL_TICK, this.tickCount);
    }

    public boolean hasShieldEquipped() {
        return hasItemEquipped(ModItems.EXOFRAME_RIOT_SHIELD.get());
    }

    private void damageShieldDurability(float amount) {
        if (this.level().isClientSide) return;
        for (int i = 0; i < modularInventory.getSlots(); i++) {
            ItemStack stack = modularInventory.getStackInSlot(i);
            if (stack.is(ModItems.EXOFRAME_RIOT_SHIELD.get())) {
                int newDamage = stack.getDamageValue() + Math.max(1, (int) amount);
                if (newDamage >= stack.getMaxDamage()) {
                    modularInventory.setStackInSlot(i, ItemStack.EMPTY);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BREAK, SoundSource.PLAYERS, 2.0F, 0.8F);
                    syncArmorMaskAndNotify();
                } else {
                    stack.setDamageValue(newDamage);
                }
                break;
            }
        }
    }

    /**
     * Phase 9 & 10: Damage Interception, Armor Mitigation, & Dynamic Armor Degradation.
     */
    @Override
    public boolean hurt(@NotNull DamageSource source, float amount) {
        if (isDying()) return false;

        // Rescue sealed capsule fire immunity
        boolean sealedRescue = hasItemEquipped(ModItems.ARMOR_RESCUE_HEAD.get()) && hasItemEquipped(ModItems.ARMOR_RESCUE_CHEST.get());
        if (sealedRescue && source.is(DamageTypeTags.IS_FIRE)) {
            return false;
        }

        // Frontal shield block
        if (hasShieldEquipped()) {
            Vec3 damagePos = source.getSourcePosition();
            if (damagePos == null && source.getEntity() != null) {
                damagePos = source.getEntity().position();
            }
            if (damagePos != null) {
                Vec3 toSource = damagePos.subtract(this.position()).normalize();
                float yawRad = this.getYRot() * Mth.DEG_TO_RAD;
                Vec3 lookHoriz = new Vec3(-Mth.sin(yawRad), 0, Mth.cos(yawRad)).normalize();
                double dot = toSource.x * lookHoriz.x + toSource.z * lookHoriz.z;
                if (dot > 0.3D) {
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 2.0F, 0.9F + this.random.nextFloat() * 0.2F);
                    damageShieldDurability(amount);
                    return false;
                }
            }
        }

        boolean isProjectile = source.is(DamageTypeTags.IS_PROJECTILE) || source.getDirectEntity() instanceof net.minecraft.world.entity.projectile.Projectile;

        // Calculate modular armor mitigation factor
        float totalMitigation = 0.0F;
        for (int i = 0; i < 4; i++) { // Head, Chest, Arms, Legs
            ItemStack armorStack = modularInventory.getStackInSlot(i);
            if (armorStack.getItem() instanceof ExoframeArmorItem armorItem) {
                totalMitigation += armorItem.getDamageReduction();
            }
        }
        totalMitigation = Math.min(0.85F, totalMitigation); // Max 85% damage mitigation

        float finalDamage = amount * (1.0F - totalMitigation);

        // Apply durability degradation to equipped modular armor plates
        if (!this.level().isClientSide && amount > 0.5F) {
            applyArmorDegradation(amount, isProjectile);
        }

        return super.hurt(source, finalDamage);
    }

    /**
     * Phase 10: Distributes durability loss across equipped armor. If durability hits 0, permanently destroys plate.
     */
    private void applyArmorDegradation(float rawDamage, boolean isProjectile) {
        int durabilityLoss = Math.max(1, (int) Math.ceil(rawDamage * (isProjectile ? 1.5F : 1.0F)));

        for (int slot = 0; slot < 4; slot++) {
            ItemStack stack = modularInventory.getStackInSlot(slot);
            if (stack.getItem() instanceof ExoframeArmorItem) {
                int slotLoss = durabilityLoss;
                if (slot == ExoframeArmorSlot.CHEST.getIndex()) slotLoss = (int) (durabilityLoss * 0.5F) + 1;
                else if (slot == ExoframeArmorSlot.LEGS.getIndex()) slotLoss = (int) (durabilityLoss * 0.3F) + 1;

                int newDamage = stack.getDamageValue() + slotLoss;
                if (newDamage >= stack.getMaxDamage()) {
                    // Armor Broken Permanently!
                    modularInventory.setStackInSlot(slot, ItemStack.EMPTY);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BREAK, SoundSource.PLAYERS, 2.0F, 0.8F);
                    this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_ARMOR_BREAK.get(), SoundSource.PLAYERS, 2.0F, 1.0F);

                    if (this.level() instanceof ServerLevel serverLevel) {
                        serverLevel.sendParticles(ParticleTypes.LAVA, this.getX(), this.getY() + 1.5D, this.getZ(), 12, 0.3D, 0.5D, 0.3D, 0.1D);
                        serverLevel.sendParticles(ParticleTypes.SMOKE, this.getX(), this.getY() + 1.5D, this.getZ(), 10, 0.3D, 0.4D, 0.3D, 0.05D);
                    }

                    Entity passenger = this.getFirstPassenger();
                    if (passenger instanceof Player player) {
                        player.displayClientMessage(Component.translatable("message.obsolete.armor_destroyed",
                                ExoframeArmorSlot.byIndex(slot).getName().toUpperCase()), true);
                    }
                } else {
                    stack.setDamageValue(newDamage);
                    modularInventory.setStackInSlot(slot, stack);
                }
            }
        }
        syncArmorMaskAndNotify();
    }

    /**
     * Phase 6: Anime-accurate collapse death sequence.
     */
    @Override
    public void die(@NotNull DamageSource source) {
        super.die(source);
        if (!this.level().isClientSide) {
            cleanUpLight();
            this.entityData.set(DATA_IS_DYING, true);
            this.deathTimer = DEATH_ANIMATION_TICKS;

            // Eject pilot safely
            Entity passenger = this.getFirstPassenger();
            if (passenger instanceof Player player) {
                player.stopRiding();
                Vec3 safePos = this.position().add(-1.2D, 0, 0);
                player.teleportTo(safePos.x, safePos.y, safePos.z);
            }

            this.level().playSound(null, this.blockPosition(), ModSounds.EXOFRAME_DEATH.get(), SoundSource.PLAYERS, 2.5F, 0.9F);
        }
    }

    @Override
    public void remove(@NotNull RemovalReason reason) {
        if (!this.level().isClientSide) {
            cleanUpLight();
        }
        super.remove(reason);
    }

    private void cleanUpLight() {
        if (lastLightPos != null) {
            if (this.level().getBlockState(lastLightPos).is(Blocks.LIGHT)) {
                this.level().setBlock(lastLightPos, Blocks.AIR.defaultBlockState(), 3);
            }
            lastLightPos = null;
        }
    }

    private void dropInventoryAndDiscard() {
        for (int i = 0; i < modularInventory.getSlots(); i++) {
            ItemStack stack = modularInventory.getStackInSlot(i);
            if (!stack.isEmpty()) {
                Containers.dropItemStack(this.level(), this.getX(), this.getY() + 0.5D, this.getZ(), stack);
            }
        }
        this.discard();
    }

    @Override
    public void addAdditionalSaveData(@NotNull CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("IsCrouching", isMechCrouching());
        tag.putBoolean("IsAiming", isAiming());
        tag.putInt("PrimaryColor", getPrimaryColor());
        tag.putInt("CamoPattern", getCamoPattern());
        tag.putInt("FrameTier", getFrameTier());
        modularInventory.saveToNbt(tag);
    }

    @Override
    public void readAdditionalSaveData(@NotNull CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("IsCrouching")) setMechCrouching(tag.getBoolean("IsCrouching"));
        if (tag.contains("IsAiming")) setAiming(tag.getBoolean("IsAiming"));
        if (tag.contains("PrimaryColor")) setPrimaryColor(tag.getInt("PrimaryColor"));
        if (tag.contains("CamoPattern")) setCamoPattern(tag.getInt("CamoPattern"));
        if (tag.contains("FrameTier")) setFrameTier(tag.getInt("FrameTier"));
        modularInventory.loadFromNbt(tag);
        syncArmorMaskAndNotify();
    }

    @Override
    public @NotNull Component getDisplayName() {
        return Component.translatable("entity.obsolete.exoframe");
    }

    @Nullable
    @Override
    public AbstractContainerMenu createMenu(int containerId, @NotNull Inventory playerInventory, @NotNull Player player) {
        return new ExoframeMenu(containerId, playerInventory, this);
    }

    // GeckoLib 4 Animation Controllers
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 3, state -> {
            if (isDying()) {
                return state.setAndContinue(ANIM_DEATH);
            }
            if (isFlying()) {
                return state.setAndContinue(isFlightBoosting() ? ANIM_FLIGHT_BOOST : ANIM_FLIGHT);
            }
            if (isMechCrouching()) {
                return state.setAndContinue(state.isMoving() ? ANIM_CROUCH_WALK : ANIM_CROUCH);
            }
            if (!this.onGround()) {
                return state.setAndContinue(ANIM_JUMP);
            }
            if (state.isMoving()) {
                LivingEntity rider = getControllingPassenger();
                if (rider != null && rider.isSprinting()) {
                    return state.setAndContinue(ANIM_SPRINT);
                }
                return state.setAndContinue(ANIM_WALK);
            }
            return state.setAndContinue(ANIM_IDLE);
        }));

        controllers.add(new AnimationController<>(this, "combat", 2, state -> {
            if (isMechMeleeing()) {
                return state.setAndContinue(ANIM_MELEE);
            }
            if (this.tickCount - this.entityData.get(DATA_RECOIL_TICK) < 8) {
                return state.setAndContinue(ANIM_SHOOT);
            }
            return PlayState.STOP;
        }));

        AnimationController<ExoframeEntity> emotes = new AnimationController<>(this, EMOTE_CONTROLLER, 4, state -> PlayState.STOP);
        for (String emote : new String[]{"salute", "salute_left", "wave", "point", "scan"}) {
            emotes.triggerableAnim(emote, RawAnimation.begin().thenPlay("animation.exoframe." + emote));
        }
        controllers.add(emotes);
    }

    /** Server-side: plays a gesture for everyone tracking this exoframe. */
    public void playEmote(String emote) {
        if (isDying() || java.util.Arrays.stream(EMOTES).noneMatch(emote::equals)) return;
        boolean armed = !modularInventory.getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex()).isEmpty();
        triggerAnim(EMOTE_CONTROLLER, emote.equals("salute") && armed ? "salute_left" : emote);
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }
}
