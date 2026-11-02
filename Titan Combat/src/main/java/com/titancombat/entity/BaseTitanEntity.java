package com.titancombat.entity;

import com.titancombat.gui.TitanMenu;
import com.titancombat.item.ModItems;
import com.titancombat.item.PaintSprayCanItem;
import com.titancombat.sound.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.Container;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.HasCustomInventoryScreen;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.Animation;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import net.minecraft.world.level.block.Block;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.List;
import java.util.Queue;
import java.util.Set;

public abstract class BaseTitanEntity extends BaseMechEntity implements GeoEntity, HasCustomInventoryScreen {
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    public static final EntityDataAccessor<Integer> DATA_CAMO_INDEX =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_STANDBY_MODE =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<String> DATA_OWNER_UUID =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.STRING);
    public static final EntityDataAccessor<String> DATA_OWNER_NAME =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.STRING);

    public static final EntityDataAccessor<Boolean> DATA_IS_FIRING =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_IS_MELEEING =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_WEAPON =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_MAGAZINE =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_RELOAD_TICKS =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_WEAPON_LOWERED =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Boolean> DATA_IS_SITTING =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    /** Howitzer back module installed (back equipment slot). */
    public static final EntityDataAccessor<Boolean> DATA_HOWITZER =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_HOWITZER_ROUNDS =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_HOWITZER_RELOAD =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_HOWITZER_SMOKE =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    /** Back-mounted MLRS-6 rocket launcher pod installed (back equipment slot). */
    public static final EntityDataAccessor<Boolean> DATA_ROCKET_POD =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);
    public static final EntityDataAccessor<Integer> DATA_ROCKET_COOLDOWN =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_ROCKET_AMMO =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    /** Ticks left until the howitzer is laid on a new target (turret slewing); it can't fire before. */
    public static final EntityDataAccessor<Integer> DATA_ARTILLERY_LAYING =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<java.util.Optional<BlockPos>> DATA_ARTILLERY_TARGET =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.OPTIONAL_BLOCK_POS);
    public static final EntityDataAccessor<Integer> DATA_SALUTE_TICKS =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Integer> DATA_FLIGHT_MODULE =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.INT);
    public static final EntityDataAccessor<Boolean> DATA_IS_FLYING =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);

    // Entity events (server -> clients) for one-shot client effects: camera shake, muzzle flash, thrusters.
    public static final byte EVENT_MELEE_IMPACT = 70;
    public static final byte EVENT_WEAPON_FIRE = 71;
    public static final byte EVENT_DASH = 72;
    public static final byte EVENT_EMBARK = 73;
    public static final byte EVENT_MELEE_SWING = 74;
    public static final byte EVENT_JUMP = 75;
    public static final byte EVENT_HOWITZER_FIRE = 77;

    /** Thruster fuel for a jump-jet hop. */
    public static final float JUMP_COST = 25.0F;

    /** Length of the boarding sequence (entry_stand_front is 3 s); the pilot can't drive or shoot during it. */
    private static final int BOARDING_TICKS = 60;

    /** Set by the client input handler; only meaningful on the client that is piloting. */
    /** Client: tickCount of the last howitzer shot (EVENT_HOWITZER_FIRE). */
    public int clientFireTick = -100;
    /** Client: howitzer laying as drawn (radians; traverse relative to the hull), slewed toward the solution by TitanModel. */
    public float clientHowitzerTraverse = 0.0F, clientHowitzerElevation = 35.0F * Mth.DEG_TO_RAD, clientHowitzerClock = -1.0F;
    /** Client: 0..1 blend into the howitzer firing stance (TitanModel), and the time it was last updated. */
    public float clientBrace = 0.0F, clientBraceClock = -1.0F;
    public static boolean clientSprintHeld = false;
    public static boolean clientJumpHeld = false;

    protected final SimpleContainer titanInventory = new SimpleContainer(TitanMenu.CONTAINER_SIZE);

    protected int firingCooldown = 0;
    protected int fireAnimTimer = 0;
    protected int meleeCooldown = 0;
    protected int meleeAnimTimer = 0;
    private int pendingMeleeTicks = -1;
    private int boardingTicks = 0;
    private boolean isEmergencyEjecting = false;

    // Client-side locomotion tracking: drives gait selection and animation playback rate.
    public enum Gait { IDLE, WALK, RUN, DASH }
    private Gait gait = Gait.IDLE;
    private double observedSpeed = 0.0D; // blocks per second, smoothed
    private int dashAnimTicks = 0;
    private float smoothedForward = 0.0F;
    private float smoothedStrafe = 0.0F;

    // Legs lag behind the torso when turning; the torso twist is rendered from the difference.
    private float legYaw;
    private boolean legYawValid = false;

    // Client-side smoothed values for the procedural animation layer (TitanModel).
    private float proceduralWeight, proceduralWeightO;
    private float leanForward, leanForwardO, leanSide, leanSideO;
    private double lastSpeed;
    private int airTicks;
    private boolean wasOnGround = true;

    // Uneven ground (client): eased step height and per-foot ground offsets for leg IK.
    private float stepOffset, stepOffsetO;
    private float pelvisDrop, pelvisDropO;
    private float legLiftLeft, legLiftLeftO, legLiftRight, legLiftRightO;
    private float ikWeight, ikWeightO;
    private int ikHoldTicks;
    private float lowerBlend, lowerBlendO; // 1 = weapon arm lowered (H)
    private float gaitLift, gaitLiftO;     // model lift so walking feet don't sink into the ground

    // 0 = kneeling cockpit position, 1 = standing; eased so the pilot rises with the chassis.
    private float standBlend = 1.0F;
    private int standUpAtTick = -1;

    private Vec3 lastNavPos = Vec3.ZERO;
    private int navStuckTicks = 0;
    private TerrainHazard cachedHazard = TerrainHazard.NONE;
    private int lastHazardCheckTick = -10;

    public BaseTitanEntity(EntityType<? extends PathfinderMob> type, Level level) {
        super(type, level);
        this.setMaxUpStep(2.0F);
        this.setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.LAVA, -1.0F);
        this.setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.DANGER_FIRE, -1.0F);
        this.setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.DAMAGE_FIRE, -1.0F);
        this.setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.WATER, -1.0F);
        this.setPathfindingMalus(net.minecraft.world.level.pathfinder.BlockPathTypes.DANGER_OTHER, -1.0F);
    }

    public abstract TitanClass getTitanClass();

    public static AttributeSupplier.Builder createTitanAttributes(TitanClass titanClass) {
        return BaseMechEntity.createAttributes()
                .add(Attributes.MAX_HEALTH, titanClass.getMaxHealth())
                .add(Attributes.MOVEMENT_SPEED, titanClass.getMoveSpeed())
                .add(Attributes.ATTACK_DAMAGE, titanClass.getAttackDamage());
    }

    @Override
    protected void defineSynchedData() {
        super.defineSynchedData();
        this.entityData.define(DATA_CAMO_INDEX, 0);
        this.entityData.define(DATA_STANDBY_MODE, false);
        this.entityData.define(DATA_OWNER_UUID, "");
        this.entityData.define(DATA_OWNER_NAME, "");
        this.entityData.define(DATA_IS_FIRING, false);
        this.entityData.define(DATA_IS_MELEEING, false);
        this.entityData.define(DATA_IS_SITTING, false);
        // Titans arrive unarmed (-1); a weapon module has to be installed in the bay before they can shoot.
        this.entityData.define(DATA_WEAPON, -1);
        this.entityData.define(DATA_MAGAZINE, 0);
        this.entityData.define(DATA_RELOAD_TICKS, 0);
        this.entityData.define(DATA_WEAPON_LOWERED, false);
        this.entityData.define(DATA_SALUTE_TICKS, 0);
        this.entityData.define(DATA_ARTILLERY_TARGET, java.util.Optional.empty());
        this.entityData.define(DATA_ARTILLERY_LAYING, 0);
        this.entityData.define(DATA_HOWITZER, false);
        this.entityData.define(DATA_HOWITZER_ROUNDS, 0);
        this.entityData.define(DATA_HOWITZER_RELOAD, 0);
        this.entityData.define(DATA_HOWITZER_SMOKE, false);
        this.entityData.define(DATA_ROCKET_POD, false);
        this.entityData.define(DATA_ROCKET_COOLDOWN, 0);
        this.entityData.define(DATA_ROCKET_AMMO, 0);
        this.entityData.define(DATA_FLIGHT_MODULE, -1);
        this.entityData.define(DATA_IS_FLYING, false);
    }

    public TitanFlightModule getFlightModule() {
        int id = this.entityData.get(DATA_FLIGHT_MODULE);
        return id < 0 ? TitanFlightModule.NONE : TitanFlightModule.byOrdinal(id);
    }

    public void setFlightModule(TitanFlightModule module) {
        this.entityData.set(DATA_FLIGHT_MODULE, module == null || module == TitanFlightModule.NONE ? -1 : module.ordinal());
    }

    public boolean hasFlightModule() {
        return getFlightModule() != TitanFlightModule.NONE;
    }

    public boolean isFlying() {
        return this.entityData.get(DATA_IS_FLYING);
    }

    public void setFlightThrust(boolean thrusting) {
        this.entityData.set(DATA_IS_FLYING, thrusting && hasFlightModule());
    }

    public int getSaluteTicks() {
        return this.entityData.get(DATA_SALUTE_TICKS);
    }

    public boolean isSaluting() {
        return getSaluteTicks() > 0;
    }

    public void triggerSalute(@Nullable Player pilot) {
        if (this.level().isClientSide || isSaluting() || isKneeling() || this.entityData.get(DATA_IS_MELEEING)) return;
        this.entityData.set(DATA_SALUTE_TICKS, 45);
        this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.4F, 1.1F);
        if (pilot != null) {
            pilot.displayClientMessage(Component.translatable("message.titancombat.salute", this.getTitanClass().getDisplayName()), true);
        }
    }

    public boolean isEmergencyEjecting() {
        return this.isEmergencyEjecting;
    }

    public void setEmergencyEjecting(boolean ejecting) {
        this.isEmergencyEjecting = ejecting;
    }

    public boolean isSitting() {
        return this.entityData.get(DATA_IS_SITTING);
    }

    public void setSitting(boolean sitting) {
        this.entityData.set(DATA_IS_SITTING, sitting);
    }

    private int lastKneelToggleTick = -100;

    public static final byte EVENT_EJECT = 76;
    private static final int EJECT_SELF_DESTRUCT_TICKS = 50;
    private int ejectCountdown = 0;
    @Nullable
    private Player ejectedPilot;

    public boolean isSelfDestructing() {
        return this.ejectCountdown > 0;
    }

    public void toggleKneel() {
        // Ignore repeats until the kneel / stand-up motion has finished.
        if (isBoarding() || this.tickCount - this.lastKneelToggleTick < 28) return;
        doToggleKneel();
    }

    private void doToggleKneel() {
        this.lastKneelToggleTick = this.tickCount;
        boolean nowSitting = !isSitting();
        setSitting(nowSitting);
        if (!this.level().isClientSide) {
            if (!nowSitting) {
                // Rise out of the kneel with the dedicated stand-up clip instead of snapping to idle.
                this.triggerAnim("body", "standing");
            }
            this.level().playSound(null, this.blockPosition(), nowSitting ? ModSounds.TITAN_CABIN_EXIT.get() : ModSounds.TITAN_CABIN_ENTER.get(),
                    SoundSource.PLAYERS, 1.4F, nowSitting ? 0.8F : 1.0F);
            if (this.getFirstPassenger() instanceof Player player) {
                player.displayClientMessage(Component.translatable(nowSitting ?
                        "message.titancombat.kneel_engaged" : "message.titancombat.kneel_disengaged"), true);
            }
        }
    }

    public int getCamoIndex() {
        return this.entityData.get(DATA_CAMO_INDEX);
    }

    public void setCamoIndex(int index) {
        this.entityData.set(DATA_CAMO_INDEX, Math.max(0, Math.min(8, index)));
    }

    public boolean isStandbyMode() {
        return this.entityData.get(DATA_STANDBY_MODE);
    }

    public void setStandbyMode(boolean standby) {
        this.entityData.set(DATA_STANDBY_MODE, standby);
    }

    public String getOwnerUUID() {
        return this.entityData.get(DATA_OWNER_UUID);
    }

    public String getOwnerName() {
        return this.entityData.get(DATA_OWNER_NAME);
    }

    public void setOwner(Player player) {
        this.entityData.set(DATA_OWNER_UUID, player.getUUID().toString());
        this.entityData.set(DATA_OWNER_NAME, player.getName().getString());
    }

    public void clearOwner() {
        this.entityData.set(DATA_OWNER_UUID, "");
        this.entityData.set(DATA_OWNER_NAME, "");
    }

    public SimpleContainer getTitanInventory() {
        return this.titanInventory;
    }

    @Override
    public void openCustomInventoryScreen(Player player) {
        if (player instanceof ServerPlayer serverPlayer) {
            NetworkHooks.openScreen(serverPlayer, new MenuProvider() {
                @Override
                public Component getDisplayName() {
                    return Component.literal(getTitanClass().getDisplayName().toUpperCase() + " TITAN COCKPIT BAY");
                }

                @Nullable
                @Override
                public AbstractContainerMenu createMenu(int id, Inventory inv, Player p) {
                    return new TitanMenu(id, inv, BaseTitanEntity.this);
                }
            }, buf -> buf.writeInt(this.getId()));
        }
    }

    /** Kneeling pose: parked by the pilot, or still crouched from an orbital drop. */
    public boolean isKneeling() {
        MechState state = getMechState();
        return isSitting() || state == MechState.LANDED || state == MechState.DROPPING;
    }

    public boolean isBoarding() {
        return this.boardingTicks > 0;
    }

    public Gait getGait() {
        return this.gait;
    }

    @Override
    protected void positionRider(Entity passenger, Entity.MoveFunction moveFunction) {
        if (this.hasPassenger(passenger)) {
            // Seat the pilot so their eyes sit in this chassis' cockpit (measured per model, standing vs kneeling).
            // Eased between the kneeling and standing cockpit positions as the chassis rises/crouches.
            TitanClass c = getTitanClass();
            float b = this.standBlend;
            double eyeY = Mth.lerp(b, c.getCockpitEyeY(true), c.getCockpitEyeY(false));
            double forwardOffset = Mth.lerp(b, c.getCockpitForward(true), c.getCockpitForward(false));
            float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
            double offsetX = -Math.sin(yawRad) * forwardOffset;
            double offsetZ = Math.cos(yawRad) * forwardOffset;
            double feetY = this.getY() + eyeY - passenger.getEyeHeight() + (this.level().isClientSide ? this.stepOffset + this.gaitLift : 0.0F);
            moveFunction.accept(passenger, this.getX() + offsetX, feetY, this.getZ() + offsetZ);
        }
    }

    @Override
    public Vec3 getDismountLocationForPassenger(LivingEntity passenger) {
        float yawRad = this.yBodyRot * ((float) Math.PI / 180.0F);
        double forwardOffset = 2.4D;
        double offsetX = -Math.sin(yawRad) * forwardOffset;
        double offsetZ = Math.cos(yawRad) * forwardOffset;
        BlockPos dismountPos = BlockPos.containing(this.getX() + offsetX, this.getY(), this.getZ() + offsetZ);
        if (this.level().getBlockState(dismountPos).isAir()) {
            return new Vec3(this.getX() + offsetX, this.getY(), this.getZ() + offsetZ);
        }
        return super.getDismountLocationForPassenger(passenger);
    }

    @Override
    protected void removePassenger(Entity passenger) {
        super.removePassenger(passenger);
        passenger.fallDistance = 0.0F;
        if (!this.level().isClientSide && passenger instanceof Player) {
            this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_CABIN_EXIT.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
        }
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        // Footsteps come from sound keyframes in walk.leg / move.leg (see TitanRenderer) so they land with the feet.
    }

    @Override
    public void performDash(float forward, float strafe) {
        if (this.isSitting() || this.isBoarding()) return;
        if (Math.abs(forward) < 0.1F && Math.abs(strafe) < 0.1F) {
            performJump();
            return;
        }
        float before = getDashCharge();
        super.performDash(forward, strafe);
        if (getDashCharge() < before) {
            this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_DASH.get(), SoundSource.PLAYERS, 2.5F, 1.0F);
            this.level().broadcastEntityEvent(this, EVENT_DASH);
        }
    }

    @Override
    public void ejectPilot() {
        if (this.ejectCountdown > 0 || !(this.getFirstPassenger() instanceof Player pilot)) return;

        // Hatch blows, the seat rockets the pilot skyward, and the abandoned chassis self-destructs.
        this.isEmergencyEjecting = true;
        try {
            pilot.stopRiding();
        } finally {
            this.isEmergencyEjecting = false;
        }
        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double fx = -Math.sin(yawRad), fz = Math.cos(yawRad);
        double top = this.getY() + getTitanClass().getCockpitEyeY(isKneeling()) + 0.5D;
        pilot.teleportTo(this.getX() + fx * 0.6D, top, this.getZ() + fz * 0.6D);
        pilot.setDeltaMovement(fx * 0.6D, 2.4D, fz * 0.6D);
        pilot.hurtMarked = true;
        pilot.fallDistance = 0.0F;
        pilot.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.SLOW_FALLING, 200, 0, false, false, true));

        this.ejectedPilot = pilot;
        this.ejectCountdown = EJECT_SELF_DESTRUCT_TICKS;
        this.setStandbyMode(true);
        this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_CABIN_EXIT.get(), SoundSource.PLAYERS, 2.5F, 1.2F);
        this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_DASH.get(), SoundSource.PLAYERS, 3.0F, 0.7F);
        this.level().playSound(null, this.blockPosition(), SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 1.5F, 1.6F);
        this.level().broadcastEntityEvent(this, EVENT_EJECT);
    }

    /** Server: rocket trail behind the ejected pilot, warning sparks on the chassis, then the blast. */
    private void tickEjectSequence() {
        if (this.ejectCountdown <= 0) return;
        if (!(this.level() instanceof net.minecraft.server.level.ServerLevel server)) return;
        int elapsed = EJECT_SELF_DESTRUCT_TICKS - this.ejectCountdown;
        Player pilot = this.ejectedPilot;
        if (pilot != null && pilot.isAlive() && elapsed < 22) {
            server.sendParticles(ParticleTypes.FLAME, pilot.getX(), pilot.getY() - 0.4D, pilot.getZ(), 6, 0.15D, 0.2D, 0.15D, 0.02D);
            server.sendParticles(ParticleTypes.LARGE_SMOKE, pilot.getX(), pilot.getY() - 0.8D, pilot.getZ(), 3, 0.2D, 0.3D, 0.2D, 0.01D);
        }
        if (elapsed % 5 == 0) {
            server.sendParticles(ParticleTypes.LAVA, this.getX(), this.getY() + 3.5D, this.getZ(), 3, 1.0D, 1.0D, 1.0D, 0.0D);
            this.level().playSound(null, this.blockPosition(), SoundEvents.NOTE_BLOCK_BIT.get(), SoundSource.HOSTILE, 1.5F, 0.5F + elapsed / 50.0F);
        }
        server.sendParticles(ParticleTypes.SMOKE, this.getX(), this.getY() + 4.0D, this.getZ(), 2, 0.8D, 0.8D, 0.8D, 0.02D);
        if (--this.ejectCountdown == 0) {
            this.ejectedPilot = null;
            explodeAndDestroy();
        }
    }

    @Override
    public void setFaction(MechFaction faction) {
        super.setFaction(faction);
        int factionCamo = switch (faction) {
            case APEX_VANGUARD -> 6; // Cobalt Blue
            case VIPER_SYNDICATE -> 2; // Woodland Green
            case CRIMSON_LEGION -> 5; // Crimson Red
            case SOLARIS_CORP -> 7; // Industrial Hazard Yellow
            case SHADOW_OPS -> 8; // Stealth Black Ops
            default -> 0;
        };
        setCamoIndex(factionCamo);
    }

    public enum TerrainHazard {
        NONE,
        LAVA,
        CLIFF
    }

    public TerrainHazard scanTerrainHazardAhead(Vec3 direction, double distance) {
        if (direction.lengthSqr() < 0.001D) return TerrainHazard.NONE;
        Vec3 probe = this.position().add(direction.normalize().scale(distance));
        BlockPos basePos = BlockPos.containing(probe.x, this.getY(), probe.z);

        // 1. Lava / Fire hazard detection
        for (int dy = 1; dy >= -3; dy--) {
            BlockPos checkPos = basePos.above(dy);
            BlockState bs = this.level().getBlockState(checkPos);
            if (bs.is(Blocks.LAVA) || bs.getFluidState().is(FluidTags.LAVA)) {
                return TerrainHazard.LAVA;
            }
        }

        // 2. Steep Cliff / Ravine detection (sheer drop > 3 blocks)
        boolean hasGround = false;
        for (int dy = 0; dy >= -3; dy--) {
            BlockPos checkPos = basePos.above(dy);
            BlockState bs = this.level().getBlockState(checkPos);
            if (!bs.isAir() && (bs.blocksMotion() || !bs.getFluidState().isEmpty())) {
                hasGround = true;
                break;
            }
        }
        if (!hasGround) {
            return TerrainHazard.CLIFF;
        }

        return TerrainHazard.NONE;
    }

    public TerrainHazard getCachedOrScanHazard(Vec3 direction, double distance) {
        if (this.tickCount - lastHazardCheckTick >= 4) {
            lastHazardCheckTick = this.tickCount;
            cachedHazard = scanTerrainHazardAhead(direction, distance);
        }
        return cachedHazard;
    }

    @Override
    public void travel(Vec3 travelVector) {
        if (this.isSitting()) {
            super.travel(Vec3.ZERO);
            return;
        }
        if (this.isAlive() && this.isVehicle()) {
            LivingEntity rider = this.getControllingPassenger();
            if (rider instanceof Player pilot && rider.zza > 0.05F) {
                TerrainHazard hazard = getCachedOrScanHazard(this.getLookAngle(), 1.8D);
                if (hazard != TerrainHazard.NONE) {
                    if (this.level().isClientSide && this.tickCount % 10 == 0) {
                        pilot.displayClientMessage(Component.translatable(hazard == TerrainHazard.LAVA ?
                                "message.titancombat.hud_hazard_lava" : "message.titancombat.hud_hazard_cliff"), true);
                    }
                    if (!this.hasImpulse && this.onGround()) {
                        travelVector = new Vec3(travelVector.x * 0.15D, travelVector.y, travelVector.z * 0.15D);
                    }
                }
            }
        }
        super.travel(travelVector);
    }

    public double getGroundYBelow(int maxProbeDistance) {
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        int startY = Mth.floor(this.getY());
        int minProbe = Math.max(this.level().getMinBuildHeight(), startY - maxProbeDistance);
        int x = Mth.floor(this.getX());
        int z = Mth.floor(this.getZ());
        for (int y = startY; y >= minProbe; y--) {
            pos.set(x, y, z);
            net.minecraft.world.level.block.state.BlockState bs = this.level().getBlockState(pos);
            if (!bs.isAir() && bs.isSolidRender(this.level(), pos)) {
                return y + 1.0D;
            }
        }
        return minProbe;
    }

    /**
     * Heavy-chassis driving: input is smoothed so the titan winds up and brakes with weight, and
     * ground speed is fixed to the gait so the walk/run animations never slide. Sprint (vanilla
     * sprint key) switches to the run gait. Modular flight equipment provides vertical lift,
     * cruising speed boost, and hovering scaled by chassis weight class.
     */
    @Override
    protected void travelPiloted(LivingEntity rider, Vec3 travelVector) {
        float forward = this.isBoarding() ? 0.0F : rider.zza;
        float strafe = this.isBoarding() ? 0.0F : rider.xxa;

        boolean grounded = this.onGround();
        float response = grounded ? 0.12F : 0.03F;
        this.smoothedForward += (forward - this.smoothedForward) * response;
        this.smoothedStrafe += (strafe - this.smoothedStrafe) * response;

        TitanClass c = getTitanClass();
        TitanFlightModule flight = getFlightModule();
        boolean hasFlight = flight != TitanFlightModule.NONE;

        boolean sprinting = clientSprintHeld && forward > 0.5F;
        double topSpeed = sprinting ? c.getRunSpeed() : c.getWalkSpeed();
        if (hasFlight && !grounded) {
            topSpeed *= flight.getForwardMultiplier();
        }
        // Reverse and side-stepping are slower, like a real heavy frame.
        double fwdSpeed = this.smoothedForward * topSpeed * (this.smoothedForward < 0 ? 0.55D : 1.0D);
        double sideSpeed = this.smoothedStrafe * c.getWalkSpeed() * 0.7D;

        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double sin = Math.sin(yawRad), cos = Math.cos(yawRad);
        double wantX = -sin * fwdSpeed + cos * sideSpeed;
        double wantZ = cos * fwdSpeed + sin * sideSpeed;

        Vec3 vel = this.getDeltaMovement();
        // Pull velocity toward the wanted ground velocity; dash impulses bleed off naturally this way.
        // While a dash is bleeding off, hold most of the thrust so it carries ~10 blocks.
        double blend = !grounded ? (hasFlight ? 0.08D : 0.02D) : (this.dashAnimTicks > 0 ? 0.12D : 0.25D);
        double vx = vel.x + (wantX - vel.x) * blend;
        double vz = vel.z + (wantZ - vel.z) * blend;
        double vy = vel.y;
        if (!this.isNoGravity()) vy -= 0.08D;

        if (hasFlight) {
            double groundY = getGroundYBelow((int) flight.getMaxFlightCeiling() + 5);
            double alt = this.getY() - groundY;
            boolean hasFuel = getDashCharge() > 0.5F;
            // Thrust first cancels this tick's gravity; the module's lift is the climb on top of that.
            double hold = this.isNoGravity() ? 0.0D : 0.08D;

            if (hasFuel) {
                if (flight == TitanFlightModule.DRONE_LIFTER) {
                    // Quad-rotor auto-hover: dampens falling speed
                    if (!grounded && vy < -0.04D) {
                        vy = vy * 0.55D;
                    }
                    if (clientJumpHeld && alt < flight.getMaxFlightCeiling()) {
                        double lift = hold + 0.14D * (flight.getVerticalLift() / c.getWeightMultiplier());
                        vy = Math.min(vy + lift, 0.42D);
                    }
                } else if (flight == TitanFlightModule.ROCKET_JETPACK) {
                    if (clientJumpHeld && alt < flight.getMaxFlightCeiling()) {
                        double lift = hold + 0.22D * (flight.getVerticalLift() / c.getWeightMultiplier());
                        vy = Math.min(vy + lift, 0.75D);
                    } else if (!grounded && vy < -0.6D) {
                        vy = -0.6D;
                    }
                } else if (flight == TitanFlightModule.VTOL_GLIDE) {
                    if (!grounded && (Math.abs(forward) > 0.1F || Math.abs(strafe) > 0.1F)) {
                        vy = Math.max(vy, -0.06D);
                    }
                    if (clientJumpHeld && alt < flight.getMaxFlightCeiling()) {
                        double lift = hold + 0.12D * (flight.getVerticalLift() / c.getWeightMultiplier());
                        vy = Math.min(vy + lift, 0.50D);
                    }
                }
            }

            // Ceiling governor
            if (alt >= flight.getMaxFlightCeiling()) {
                if (vy > 0.0D) vy *= 0.15D;
                if (clientJumpHeld && this.tickCount % 40 == 0 && rider instanceof Player pilot) {
                    pilot.displayClientMessage(Component.translatable("message.titancombat.flight_ceiling_reached"), true);
                }
            }
        }

        this.setDeltaMovement(vx, vy, vz);
        this.move(net.minecraft.world.entity.MoverType.SELF, this.getDeltaMovement());
        Vec3 after = this.getDeltaMovement();
        this.setDeltaMovement(after.x, after.y * 0.98D, after.z);
        this.calculateEntityAnimation(false);
    }

    /** Client: measure real ground speed and pick the gait the legs should play. */
    private int lastRicochetTick = -100;

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (!this.level().isClientSide) {
            amount = applyArmorPlating(source, amount);
            if (amount <= 0.0F) {
                playRicochet(source);
                return false;
            }
        }
        return super.hurt(source, amount);
    }

    /**
     * Titan hull plating. Infantry weapons (vanilla arrows/melee and gun mods such as TACZ or
     * Superb Warfare, whose bullets arrive as ordinary projectile/mob damage) mostly glance off;
     * heavy calibers still chip it, explosives and other titans' weapons do real damage.
     */
    protected float applyArmorPlating(DamageSource source, float amount) {
        if (source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) return amount;

        Entity direct = source.getDirectEntity();
        Entity attacker = source.getEntity();
        boolean titanWeapon = direct instanceof TitanEnergyBlastEntity || direct instanceof BaseMechEntity
                || (attacker != null && attacker.getVehicle() instanceof BaseMechEntity && direct == attacker.getVehicle());
        if (titanWeapon) return amount;

        if (source.is(net.minecraft.tags.DamageTypeTags.IS_EXPLOSION)) return amount * 0.6F;
        if (source.is(net.minecraft.tags.DamageTypeTags.IS_FIRE)) return amount * 0.2F;
        if (source.is(net.minecraft.tags.DamageTypeTags.IS_FALL)) return 0.0F;

        // Small arms: rifle/pistol rounds glance; anti-materiel and cannon rounds still bite.
        if (amount < 6.0F) return amount * 0.05F;
        if (amount < 30.0F) return amount * 0.2F;
        return amount * 0.5F;
    }

    private void playRicochet(DamageSource source) {
        if (this.tickCount - this.lastRicochetTick < 3) return;
        this.lastRicochetTick = this.tickCount;
        Vec3 at = source.getSourcePosition() != null ? source.getSourcePosition() : this.position().add(0, 3.0D, 0);
        Vec3 hit = this.position().add(0, 3.0D, 0).add(at.subtract(this.position().add(0, 3.0D, 0)).normalize().scale(1.5D));
        this.level().playSound(null, hit.x, hit.y, hit.z, SoundEvents.SHIELD_BLOCK, SoundSource.HOSTILE, 0.6F, 1.6F + this.random.nextFloat() * 0.3F);
        if (this.level() instanceof net.minecraft.server.level.ServerLevel server) {
            server.sendParticles(ParticleTypes.ELECTRIC_SPARK, hit.x, hit.y, hit.z, 6, 0.2D, 0.2D, 0.2D, 0.15D);
        }
    }

    /** Jump jets: a short vertical burst (Space with no direction held). */
    public void performJump() {
        if (!this.onGround() || getDashCharge() < JUMP_COST) return;
        setDashCharge(getDashCharge() - JUMP_COST);
        Vec3 v = this.getDeltaMovement();
        this.setDeltaMovement(v.x * 1.2D, 1.25D, v.z * 1.2D);
        this.hasImpulse = true;
        this.hurtMarked = true;
        this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_DASH.get(), SoundSource.PLAYERS, 2.2F, 0.8F);
        this.level().broadcastEntityEvent(this, EVENT_JUMP);
    }

    /** Client-only: jetpack nozzle exits relative to the titan's position, as last drawn by TitanFlightModuleLayer. */
    private Vec3[] renderedJetNozzles;
    private int renderedJetNozzlesTick;

    public void setRenderedJetNozzles(Vec3 left, Vec3 right) {
        this.renderedJetNozzles = new Vec3[]{left, right};
        this.renderedJetNozzlesTick = this.tickCount;
    }

    private void spawnFlightParticles() {
        TitanFlightModule flight = getFlightModule();
        if (flight == TitanFlightModule.NONE) return;

        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double fx = -Math.sin(yawRad);  // Forward vector X
        double fz = Math.cos(yawRad);   // Forward vector Z
        double rx = -Math.cos(yawRad);  // Right vector X
        double rz = -Math.sin(yawRad);  // Right vector Z
        double bx = -fx;                // Backward vector X
        double bz = -fz;                // Backward vector Z

        // The flight module is mounted on the upper dorsal reactor/spine (body3).
        // Its vertical height directly tracks the chassis cockpit eye line.
        double eyeY = this.getTitanClass().getCockpitEyeY(false);
        double mountCenterY = this.getY() + eyeY + 0.95D;

        if (flight == TitanFlightModule.DRONE_LIFTER) {
            // 4 Ducted Rotor Nacelles (Front-Left, Front-Right, Rear-Left, Rear-Right)
            // Rotors are elevated high on the dorsal frame, blowing strong downwash downwards.
            double[][] rotors = {
                    {-1.73D, 1.55D, 0.45D},  // Front-Left Rotor
                    { 1.73D, 1.55D, 0.45D},  // Front-Right Rotor
                    {-1.85D, 2.00D, 0.10D},  // Rear-Left Rotor
                    { 1.85D, 2.00D, 0.10D}   // Rear-Right Rotor
            };
            for (double[] r : rotors) {
                double px = this.getX() + rx * r[0] + bx * r[1];
                double py = mountCenterY + r[2];
                double pz = this.getZ() + rz * r[0] + bz * r[1];
                this.level().addParticle(ParticleTypes.CLOUD,
                        px + (this.random.nextDouble() - 0.5D) * 0.25D,
                        py,
                        pz + (this.random.nextDouble() - 0.5D) * 0.25D,
                        (this.random.nextDouble() - 0.5D) * 0.08D,
                        -0.55D,
                        (this.random.nextDouble() - 0.5D) * 0.08D);
            }
        } else if (flight == TitanFlightModule.ROCKET_JETPACK) {
            // Twin Rocket Bell Nozzles (Left and Right), at this chassis' modelled nozzle exits.
            double[] nozzle = this.getTitanClass().getJetpackNozzle();
            double nozzleY = this.getY() + nozzle[1];
            double[][] nozzles = {
                    {-nozzle[0], nozzle[2]}, // Left Nozzle Bell
                    { nozzle[0], nozzle[2]}  // Right Nozzle Bell
            };
            // Prefer where the renderer last drew the nozzles: torso aim/lean swings a rear-mounted pack a long way.
            boolean rendered = this.renderedJetNozzles != null && this.tickCount - this.renderedJetNozzlesTick < 5;
            for (int i = 0; i < nozzles.length; i++) {
                double[] n = nozzles[i];
                double px = this.getX() + rx * n[0] + bx * n[1];
                double py = nozzleY;
                double pz = this.getZ() + rz * n[0] + bz * n[1];
                if (rendered) {
                    px = this.getX() + this.renderedJetNozzles[i].x;
                    py = this.getY() + this.renderedJetNozzles[i].y;
                    pz = this.getZ() + this.renderedJetNozzles[i].z;
                }

                // Blazing rocket exhaust flame bursting directly out of the bell opening
                this.level().addParticle(ParticleTypes.FLAME,
                        px + (this.random.nextDouble() - 0.5D) * 0.18D,
                        py,
                        pz + (this.random.nextDouble() - 0.5D) * 0.18D,
                        (this.random.nextDouble() - 0.5D) * 0.04D,
                        -0.65D,
                        (this.random.nextDouble() - 0.5D) * 0.04D);

                // High-velocity rocket smoke column blasting downward
                this.level().addParticle(ParticleTypes.SMOKE,
                        px + (this.random.nextDouble() - 0.5D) * 0.15D,
                        py - 0.15D,
                        pz + (this.random.nextDouble() - 0.5D) * 0.15D,
                        (this.random.nextDouble() - 0.5D) * 0.04D,
                        -0.50D,
                        (this.random.nextDouble() - 0.5D) * 0.04D);
            }
        } else if (flight == TitanFlightModule.VTOL_GLIDE) {
            // Twin Underwing Vector Turbines (Left and Right Wing)
            // Positioned directly under the wings at the rear turbine exhaust cowls.
            double turbineY = mountCenterY - 0.20D;
            double[][] turbines = {
                    {-1.45D, 1.35D}, // Left Underwing Turbine
                    { 1.45D, 1.35D}  // Right Underwing Turbine
            };
            for (double[] tb : turbines) {
                double px = this.getX() + rx * tb[0] + bx * tb[1];
                double py = turbineY;
                double pz = this.getZ() + rz * tb[0] + bz * tb[1];

                // Cyan soul-fire plasma vector jet streaming backwards and down from turbine cowl
                this.level().addParticle(ParticleTypes.SOUL_FIRE_FLAME,
                        px + (this.random.nextDouble() - 0.5D) * 0.15D,
                        py,
                        pz + (this.random.nextDouble() - 0.5D) * 0.15D,
                        bx * 0.25D + (this.random.nextDouble() - 0.5D) * 0.05D,
                        -0.25D,
                        bz * 0.25D + (this.random.nextDouble() - 0.5D) * 0.05D);

                // High speed vector jet stream smoke
                this.level().addParticle(ParticleTypes.SMOKE,
                        px,
                        py - 0.05D,
                        pz,
                        bx * 0.20D,
                        -0.20D,
                        bz * 0.20D);
            }
        }
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false; // landing jets cushion the chassis
    }

    @Override
    protected float tickHeadTurn(float yRot, float amount) {
        if (this.getControllingPassenger() != null && !isKneeling()) {
            float target = this.getYRot();
            if (!this.legYawValid) {
                this.legYaw = target;
                this.legYawValid = true;
            }
            float diff = Mth.wrapDegrees(target - this.legYaw);
            // The waist can only twist so far before the legs must step around.
            if (Math.abs(diff) > 55.0F) {
                this.legYaw = target - Math.signum(diff) * 55.0F;
                diff = Math.signum(diff) * 55.0F;
            }
            float turnRate = this.gait == Gait.IDLE ? 4.5F : 9.0F;
            this.legYaw += Mth.clamp(diff, -turnRate, turnRate);
            this.yBodyRot = this.legYaw;
            this.yHeadRot = target;
            return amount;
        }
        this.legYawValid = false;
        return super.tickHeadTurn(yRot, amount);
    }

    public float getProceduralWeight(float partial) {
        return Mth.lerp(partial, this.proceduralWeightO, this.proceduralWeight);
    }

    /** Degrees; negative pitches the hull forward (GeckoLib rotX convention). */
    public float getLeanForward(float partial) {
        return Mth.lerp(partial, this.leanForwardO, this.leanForward);
    }

    public float getLeanSide(float partial) {
        return Mth.lerp(partial, this.leanSideO, this.leanSide);
    }

    /** 0..1, how far the weapon arm is lowered (holster key), eased. */
    public float getLowerBlend(float partial) {
        return Mth.lerp(partial, this.lowerBlendO, this.lowerBlend);
    }

    public float getStepOffset(float partial) {
        return Mth.lerp(partial, this.stepOffsetO, this.stepOffset) + Mth.lerp(partial, this.gaitLiftO, this.gaitLift);
    }

    /** Blocks the pelvis is lowered so the foot over lower ground reaches it (<= 0). */
    public float getPelvisDrop(float partial) {
        return Mth.lerp(partial, this.pelvisDropO, this.pelvisDrop) * Mth.lerp(partial, this.ikWeightO, this.ikWeight);
    }

    /** Blocks the given foot must be raised (by bending that leg) after the pelvis drop (>= 0). */
    public float getLegLift(boolean left, float partial) {
        float w = Mth.lerp(partial, this.ikWeightO, this.ikWeight);
        return (left ? Mth.lerp(partial, this.legLiftLeftO, this.legLiftLeft) : Mth.lerp(partial, this.legLiftRightO, this.legLiftRight)) * w;
    }

    /** Height of walkable ground under (x, z) relative to the titan's feet, searched within +-2.5 blocks. */
    private float groundHeightAt(double x, double z) {
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos();
        int top = Mth.floor(this.getY() + 2.5D), bottom = Mth.floor(this.getY() - 2.5D);
        for (int y = top; y >= bottom; y--) {
            pos.set(Mth.floor(x), y, Mth.floor(z));
            net.minecraft.world.phys.shapes.VoxelShape shape = this.level().getBlockState(pos).getCollisionShape(this.level(), pos);
            if (!shape.isEmpty()) {
                return (float) (y + shape.max(net.minecraft.core.Direction.Axis.Y) - this.getY());
            }
        }
        return -2.5F;
    }

    /** Client: ease vertical steps and work out foot placement on uneven ground. */
    private void updateClientTerrain() {
        this.stepOffsetO = this.stepOffset;
        double dy = this.getY() - this.yo;
        // A step up/down while walking is a 1-2 block teleport in vanilla; show it as a short climb instead.
        if (this.onGround() && this.wasOnGround && Math.abs(dy) > 0.3D && Math.abs(dy) < 2.6D) {
            this.stepOffset -= (float) dy;
        }
        this.stepOffset *= 0.6F;
        if (Math.abs(this.stepOffset) < 0.01F) this.stepOffset = 0.0F;

        this.gaitLiftO = this.gaitLift;
        float liftTarget = !this.onGround() || isKneeling() ? 0.0F : switch (this.gait) {
            case WALK -> getTitanClass().getFootSink(false);
            case RUN -> getTitanClass().getFootSink(true);
            default -> 0.0F;
        };
        this.gaitLift += (liftTarget - this.gaitLift) * 0.2F;

        this.lowerBlendO = this.lowerBlend;
        // Only armed titans lower their weapon; unarmed titans use their natural bind rest pose.
        boolean lowered = isWeaponLowered() && hasWeapon() && !isFiringWeapon() && !isKneeling();
        this.lowerBlend = Mth.approach(this.lowerBlend, lowered ? 1.0F : 0.0F, 0.12F);

        this.ikWeightO = this.ikWeight;
        this.pelvisDropO = this.pelvisDrop;
        this.legLiftLeftO = this.legLiftLeft;
        this.legLiftRightO = this.legLiftRight;

        boolean planted = this.onGround() && !isKneeling() && this.gait == Gait.IDLE && getMechState() != MechState.DROPPING;
        // Leaving the ground cancels foot placement at once; otherwise the body would be pulled down to
        // the ground under a jumping titan.
        if (!this.onGround()) this.ikHoldTicks = 10; // let the landing settle before placing feet
        else if (this.ikHoldTicks > 0) this.ikHoldTicks--;
        this.ikWeight = this.onGround() && this.ikHoldTicks == 0 ? Mth.approach(this.ikWeight, planted ? 1.0F : 0.0F, 0.15F) : 0.0F;
        if (this.tickCount % 2 == 0 || this.ikWeight > 0.0F) {
            float yawRad = this.yBodyRot * ((float) Math.PI / 180.0F);
            double rx = -Math.cos(yawRad), rz = -Math.sin(yawRad); // titan's right
            float right = groundHeightAt(this.getX() + rx * 1.1D, this.getZ() + rz * 1.1D);
            float left = groundHeightAt(this.getX() - rx * 1.1D, this.getZ() - rz * 1.1D);
            right = Mth.clamp(right, -1.25F, 0.6F);
            left = Mth.clamp(left, -1.25F, 0.6F);
            float drop = Math.min(0.0F, Math.min(left, right));
            this.pelvisDrop += (drop - this.pelvisDrop) * 0.3F;
            this.legLiftLeft += ((left - drop) - this.legLiftLeft) * 0.3F;
            this.legLiftRight += ((right - drop) - this.legLiftRight) * 0.3F;
        }
    }

    /** Client: procedural weights, lean, thruster/landing effects. */
    private void updateClientMotionFx() {
        this.proceduralWeightO = this.proceduralWeight;
        boolean live = !isKneeling() && !isBoarding() && getMechState() != MechState.DROPPING;
        this.proceduralWeight = Mth.approach(this.proceduralWeight, live ? 1.0F : 0.0F, 0.08F);

        double accel = this.observedSpeed - this.lastSpeed;
        this.lastSpeed = this.observedSpeed;
        float turn = Mth.wrapDegrees(this.yBodyRot - this.yBodyRotO);
        this.leanForwardO = this.leanForward;
        this.leanSideO = this.leanSide;
        float fwdTarget = (float) Mth.clamp(-(this.observedSpeed * 0.6D + accel * 5.0D), -10.0D, 6.0D);
        float sideTarget = Mth.clamp(turn * 0.9F, -8.0F, 8.0F);
        this.leanForward += (fwdTarget - this.leanForward) * 0.15F;
        this.leanSide += (sideTarget - this.leanSide) * 0.15F;

        boolean grounded = this.onGround();
        if (!grounded) this.airTicks++;
        if (grounded && !this.wasOnGround && this.airTicks > 8) {
            com.titancombat.client.TitanClientEffects.onLanding(this, Math.min(1.0F, this.airTicks / 25.0F));
        }
        if (grounded) this.airTicks = 0;
        this.wasOnGround = grounded;

        if (this.isVehicle() || this.dashAnimTicks > 0) {
            com.titancombat.client.TitanClientEffects.thrusterTick(this, this.dashAnimTicks > 0, !grounded && this.airTicks > 1, this.gait == Gait.RUN);
        }
    }

    private void updateClientGait() {
        double dx = this.getX() - this.xo;
        double dz = this.getZ() - this.zo;
        double speed = Math.sqrt(dx * dx + dz * dz) * 20.0D;
        this.observedSpeed += (speed - this.observedSpeed) * 0.35D;

        if (this.dashAnimTicks > 0) {
            this.dashAnimTicks--;
            this.gait = Gait.DASH;
            return;
        }

        if (!this.onGround() && this.airTicks > 4 && this.isVehicle()) {
            this.gait = Gait.DASH; // jump jets / falling: legs tucked in the thruster pose
            return;
        }

        TitanClass c = getTitanClass();
        double walk = c.getWalkSpeed() * 20.0D;
        double run = c.getRunSpeed() * 20.0D;
        double runThreshold = (walk + run) * 0.5D;
        double moveThreshold = this.gait == Gait.IDLE ? 0.9D : 0.5D; // hysteresis

        if (this.observedSpeed < moveThreshold || !this.onGround() && this.observedSpeed < walk * 0.5D) {
            this.gait = Gait.IDLE;
        } else if (this.observedSpeed > (this.gait == Gait.RUN ? runThreshold - 0.6D : runThreshold + 0.3D)) {
            this.gait = Gait.RUN;
        } else {
            this.gait = Gait.WALK;
        }
    }

    /** Playback rate for locomotion clips; fixed per gait so a step always matches one stride. */
    public double getLocomotionPlayback() {
        return switch (this.gait) {
            case WALK -> getTitanClass().getWalkPlayback();
            case RUN -> getTitanClass().getRunPlayback();
            default -> 1.0D;
        };
    }

    @Override
    public void handleEntityEvent(byte id) {
        if (id == EVENT_HOWITZER_FIRE) {
            this.clientFireTick = this.tickCount;  // drives the howitzer recoil in TitanModel
            net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,
                    () -> () -> com.titancombat.client.TitanClientEffects.onHowitzerFired(this));
            return;
        }
        if (id == EVENT_DASH) {
            this.dashAnimTicks = 14;
        } else if (id == EVENT_EMBARK) {
            this.boardingTicks = isKneeling() ? 46 : BOARDING_TICKS;
        }
        if (id >= EVENT_MELEE_IMPACT && id <= EVENT_EJECT) {
            net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT,
                    () -> () -> com.titancombat.client.TitanClientEffects.onEntityEvent(this, id));
            return;
        }
        super.handleEntityEvent(id);
    }

    /** Where shots leave the weapon: the right hand, forward of the chest. */
    public Vec3 getMuzzlePosition() {
        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        double fx = -Math.sin(yawRad), fz = Math.cos(yawRad);
        double rx = -Math.cos(yawRad), rz = -Math.sin(yawRad);
        double up = isKneeling() ? 2.6D : 4.1D;
        return new Vec3(this.getX() + fx * 2.6D + rx * 1.5D, this.getY() + up, this.getZ() + fz * 2.6D + rz * 1.5D);
    }

    @Override
    public void tick() {
        super.tick();
        if (firingCooldown > 0) firingCooldown--;
        if (meleeCooldown > 0) meleeCooldown--;
        if (boardingTicks > 0) boardingTicks--;
        int salute = this.entityData.get(DATA_SALUTE_TICKS);
        if (salute > 0) this.entityData.set(DATA_SALUTE_TICKS, salute - 1);

        this.standBlend = Mth.approach(this.standBlend, isKneeling() ? 0.0F : 1.0F, 1.0F / 26.0F);

        if (this.level().isClientSide) {
            updateClientGait();
            updateClientTerrain();
            updateClientMotionFx();
            if (hasFlightModule() && (isFlying() || (!this.onGround() && this.isVehicle()))) {
                spawnFlightParticles();
            }
        } else {
            if (pendingMeleeTicks >= 0 && --pendingMeleeTicks < 0) {
                resolveMeleeHit();
            }
            tickWeaponSystems();
            tickFlightSystems();
            tickHowitzer();
            tickEjectSequence();
            // Pilot boarded a parked titan: the hatch seals, then the chassis rises on its own.
            if (this.boardingTicks == this.standUpAtTick) {
                this.standUpAtTick = -1;
                if (isSitting() && this.isVehicle()) doToggleKneel();
            }
            // A freshly dropped titan settles into its parked "waiting for pilot" pose.
            if (getMechState() == MechState.LANDED && !this.isVehicle() && !isSitting()) {
                setSitting(true);
            }
        }

        if (fireAnimTimer > 0) {
            if (--fireAnimTimer == 0) {
                this.entityData.set(DATA_IS_FIRING, false);
            }
        }
        if (meleeAnimTimer > 0) {
            if (--meleeAnimTimer == 0) {
                this.entityData.set(DATA_IS_MELEEING, false);
            }
        }

        if (!this.level().isClientSide) {
            // Flight module fuel & thrust handling (server-side)
            TitanFlightModule flight = getFlightModule();
            if (flight != TitanFlightModule.NONE) {
                boolean activeThrust = isFlying() || (!this.onGround() && this.isVehicle());
                if (activeThrust) {
                    float drain = (isFlying() ? flight.getEnergyDrain() : flight.getEnergyDrain() * 0.4F)
                            * getTitanClass().getWeightMultiplier();
                    float currentCharge = getDashCharge();
                    if (currentCharge >= drain) {
                        setDashCharge(currentCharge - drain);
                    } else {
                        // Fuel empty! Try auto-swapping battery from cockpit bay slot 0
                        ItemStack batteryStack = this.titanInventory.getItem(TitanMenu.BATTERY_SLOT);
                        if (!batteryStack.isEmpty() && batteryStack.getItem() instanceof com.titancombat.item.TitanBatteryItem
                                && !batteryStack.is(com.titancombat.item.ModItems.EMPTY_BATTERY.get())) {
                            this.titanInventory.setItem(TitanMenu.BATTERY_SLOT,
                                    new ItemStack(com.titancombat.item.ModItems.EMPTY_BATTERY.get(), batteryStack.getCount()));
                            setDashCharge(100.0F);
                            this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_GET_BATTERY.get(), SoundSource.PLAYERS, 1.5F, 1.0F);
                            if (this.getFirstPassenger() instanceof Player p) {
                                p.sendSystemMessage(Component.translatable("message.titancombat.flight_battery_swapped"));
                            }
                        } else {
                            // Depleted: cut thrust!
                            setDashCharge(0.0F);
                            if (isFlying()) setFlightThrust(false);
                            if (this.tickCount % 40 == 0 && this.getFirstPassenger() instanceof Player p) {
                                p.displayClientMessage(Component.translatable("message.titancombat.flight_battery_depleted"), true);
                                this.level().playSound(null, this.blockPosition(), SoundEvents.FIRE_EXTINGUISH, SoundSource.PLAYERS, 1.0F, 0.7F);
                            }
                        }
                    }
                }
            }

            // 1. Core Battery Bay Continuous Transfer: transfers FE from battery slot 0 into reactor
            if (this.tickCount % 10 == 0) {
                ItemStack batteryStack = this.titanInventory.getItem(TitanMenu.BATTERY_SLOT);
                if (!batteryStack.isEmpty() && batteryStack.getItem() instanceof com.titancombat.item.TitanBatteryItem) {
                    int batEnergy = com.titancombat.item.TitanBatteryItem.getEnergy(batteryStack);
                    if (batEnergy > 0 && getEnergy() < getMaxEnergy()) {
                        int needed = getMaxEnergy() - getEnergy();
                        int transfer = Math.min(batEnergy, Math.min(500, needed));
                        addEnergy(transfer);
                        int remaining = batEnergy - transfer;
                        if (remaining <= 0) {
                            ItemStack empty = new ItemStack(com.titancombat.item.ModItems.EMPTY_BATTERY.get());
                            com.titancombat.item.TitanBatteryItem.setEnergy(empty, 0);
                            this.titanInventory.setItem(TitanMenu.BATTERY_SLOT, empty);
                            this.level().playSound(null, this.blockPosition(), SoundEvents.ITEM_BREAK, SoundSource.PLAYERS, 0.8F, 1.2F);
                            if (this.getFirstPassenger() instanceof Player p) {
                                p.sendSystemMessage(Component.translatable("message.titancombat.battery_bay_depleted"));
                            }
                        } else {
                            com.titancombat.item.TitanBatteryItem.setEnergy(batteryStack, remaining);
                        }
                    }
                }
            }

            // 2. Safe Foliage Trample: crush bushes, vines, flowers, and natural (non-persistent) leaves
            if (this.tickCount % 4 == 0 && (this.isVehicle() || !this.getNavigation().isDone())) {
                if (this.horizontalCollision || this.getDeltaMovement().horizontalDistanceSqr() > 0.04D) {
                    AABB box = this.getBoundingBox().inflate(0.1D, 0.0D, 0.1D);
                    int minX = net.minecraft.util.Mth.floor(box.minX);
                    int maxX = net.minecraft.util.Mth.floor(box.maxX);
                    int minY = net.minecraft.util.Mth.floor(box.minY);
                    int maxY = net.minecraft.util.Mth.floor(box.minY + 2.5D);
                    int minZ = net.minecraft.util.Mth.floor(box.minZ);
                    int maxZ = net.minecraft.util.Mth.floor(box.maxZ);

                    BlockPos.MutableBlockPos mpos = new BlockPos.MutableBlockPos();
                    for (int x = minX; x <= maxX; x++) {
                        for (int y = minY; y <= maxY; y++) {
                            for (int z = minZ; z <= maxZ; z++) {
                                mpos.set(x, y, z);
                                BlockState bs = this.level().getBlockState(mpos);
                                if (bs.isAir()) continue;

                                boolean isNaturalLeaves = (bs.getBlock() instanceof net.minecraft.world.level.block.LeavesBlock)
                                        && bs.hasProperty(net.minecraft.world.level.block.LeavesBlock.PERSISTENT)
                                        && !bs.getValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT);
                                boolean isSoftFoliage = (bs.getBlock() instanceof net.minecraft.world.level.block.BushBlock
                                        || bs.getBlock() instanceof net.minecraft.world.level.block.VineBlock
                                        || bs.is(net.minecraft.tags.BlockTags.FLOWERS));

                                if (isNaturalLeaves || isSoftFoliage) {
                                    this.level().destroyBlock(mpos, false);
                                    if (this.random.nextFloat() < 0.25F) {
                                        this.level().playSound(null, mpos, SoundEvents.GRASS_BREAK, SoundSource.BLOCKS, 0.8F, 1.0F);
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // 3. Intelligent Terrain Hazard Detection (Lava & Cliff Watchdog during AI remote navigation)
            if (this.tickCount % 5 == 0 && !this.isVehicle() && !this.getNavigation().isDone()) {
                Vec3 navDir = this.getDeltaMovement().horizontalDistanceSqr() > 0.001D ? this.getDeltaMovement() : this.getLookAngle();
                TerrainHazard hazard = scanTerrainHazardAhead(navDir, 2.0D);
                if (hazard != TerrainHazard.NONE) {
                    this.getNavigation().stop();
                    this.setStandbyMode(true);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.NOTE_BLOCK_BASS.get(), SoundSource.PLAYERS, 1.5F, 0.5F);

                    String ownerUUID = getOwnerUUID();
                    if (!ownerUUID.isEmpty()) {
                        try {
                            Player owner = this.level().getPlayerByUUID(java.util.UUID.fromString(ownerUUID));
                            if (owner != null) {
                                owner.sendSystemMessage(Component.translatable(hazard == TerrainHazard.LAVA ?
                                        "message.titancombat.hazard_lava" : "message.titancombat.hazard_cliff",
                                        getTitanClass().getDisplayName(), this.blockPosition().getX(), this.blockPosition().getY(), this.blockPosition().getZ()));
                            }
                        } catch (Exception ignored) {}
                    }
                }
            }

            // 4. Anti-stuck watchdog during AI remote walk
            if (this.tickCount % 5 == 0 && !this.isVehicle() && !this.getNavigation().isDone()) {
                if (this.position().distanceToSqr(this.lastNavPos) < 0.04D) {
                    this.navStuckTicks += 5;
                    if (this.navStuckTicks > 60) {
                        this.getNavigation().stop();
                        this.navStuckTicks = 0;
                        this.setStandbyMode(true);
                        this.level().playSound(null, this.blockPosition(), SoundEvents.NOTE_BLOCK_BASS.get(), SoundSource.PLAYERS, 1.5F, 0.6F);

                        String ownerUUID = getOwnerUUID();
                        if (!ownerUUID.isEmpty()) {
                            try {
                                Player owner = this.level().getPlayerByUUID(java.util.UUID.fromString(ownerUUID));
                                if (owner != null) {
                                    owner.sendSystemMessage(Component.translatable("message.titancombat.path_obstructed",
                                            getTitanClass().getDisplayName(), this.blockPosition().getX(), this.blockPosition().getY(), this.blockPosition().getZ()));
                                }
                            } catch (Exception ignored) {}
                        }
                    }
                } else {
                    this.lastNavPos = this.position();
                    this.navStuckTicks = 0;
                }
            }
        }
    }

    public boolean performMeleeAttack(Player pilot) {
        if (this.isSitting() || this.isBoarding()) return false;
        if (meleeCooldown > 0) return false;
        boolean ronin = getTitanClass() == TitanClass.RONIN;
        meleeCooldown = ronin ? 16 : 22; // the full swing has to finish before the next one

        if (!this.level().isClientSide) {
            this.entityData.set(DATA_IS_MELEEING, true);
            this.meleeAnimTimer = ronin ? 20 : 16;

            // Ronin chains its core sword combo while Overdrive is running.
            String clip = ronin && isOverdriveActive() ? "melee_core_" + (1 + this.random.nextInt(3)) : "melee";
            this.triggerAnim("arms", clip);
            this.level().broadcastEntityEvent(this, EVENT_MELEE_SWING);

            if (ronin) {
                this.level().playSound(null, this.blockPosition(), ModSounds.RONIN_SWORD.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
            } else {
                this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_MELEE.get(), SoundSource.PLAYERS, 2.0F, 0.9F);
            }

            // Wind-up first: damage lands when the fist/blade reaches the target in the clip, not on key press.
            this.pendingMeleeTicks = ronin ? 6 : 7;
        }
        return true;
    }

    private void resolveMeleeHit() {
        Entity pilotEntity = this.getControllingPassenger();
        boolean ronin = getTitanClass() == TitanClass.RONIN;

        float yawRad = this.getYRot() * ((float) Math.PI / 180.0F);
        Vec3 forward = new Vec3(-Math.sin(yawRad), 0, Math.cos(yawRad));
        // Short lunge into the strike gives the swing its weight.
        if (this.onGround()) {
            this.setDeltaMovement(this.getDeltaMovement().add(forward.scale(0.35D)));
            this.hasImpulse = true;
        }

        double reach = ronin ? 4.0D : 3.2D;
        Vec3 strikePos = this.position().add(0, 2.5D, 0).add(forward.scale(reach));
        double half = ronin ? 3.0D : 2.4D;
        AABB strikeBox = new AABB(strikePos.x - half, strikePos.y - 2.5D, strikePos.z - half,
                strikePos.x + half, strikePos.y + 2.5D, strikePos.z + half);

        List<LivingEntity> targets = this.level().getEntitiesOfClass(LivingEntity.class, strikeBox,
                e -> e != this && e != pilotEntity && !this.isAlliedTo(e) && e.isAlive());

        float dmg = ronin ? (isOverdriveActive() ? 90.0F : 60.0F) : (getTitanClass() == TitanClass.SCORCH ? 45.0F : 38.0F);
        boolean hit = false;
        for (LivingEntity target : targets) {
            target.hurt(this.damageSources().mobAttack(this), dmg);
            target.knockback(ronin ? 1.2D : 1.8D, -forward.x, -forward.z);
            if (getTitanClass() == TitanClass.SCORCH) {
                target.setSecondsOnFire(6);
            }
            hit = true;
        }

        if (hit) {
            this.level().playSound(null, this.blockPosition(), ronin ? ModSounds.RONIN_SWORD_IMPACT.get() : ModSounds.TITAN_MELEE_IMPACT.get(),
                    SoundSource.PLAYERS, 2.2F, 1.0F);
            this.level().broadcastEntityEvent(this, EVENT_MELEE_IMPACT);
            addCoreCharge(4.0F);
        }
    }

    /** Point the pilot is aiming at: first block or hostile along the view ray, else far away. */
    @Nullable
    private Vec3 pilotAim;
    private int pilotAimTick = -100;

    /** Crosshair target reported by the pilot's client this tick (see TitanFireC2SPacket). */
    public void setPilotAim(Vec3 aim) {
        // Ignore nonsense (or tampered) points far from the titan; fall back to the server's own ray.
        if (aim.distanceToSqr(this.position()) < 256.0D * 256.0D) {
            this.pilotAim = aim;
            this.pilotAimTick = this.tickCount;
        }
    }

    protected Vec3 computeAimPoint(Player pilot) {
        if (this.pilotAim != null && this.tickCount - this.pilotAimTick <= 6) {
            return this.pilotAim;
        }
        double range = 96.0D;
        Vec3 eye = pilot.getEyePosition();
        Vec3 end = eye.add(pilot.getLookAngle().scale(range));
        net.minecraft.world.phys.BlockHitResult blockHit = this.level().clip(new net.minecraft.world.level.ClipContext(
                eye, end, net.minecraft.world.level.ClipContext.Block.COLLIDER, net.minecraft.world.level.ClipContext.Fluid.NONE, pilot));
        if (blockHit.getType() != net.minecraft.world.phys.HitResult.Type.MISS) {
            end = blockHit.getLocation();
        }
        net.minecraft.world.phys.EntityHitResult entityHit = net.minecraft.world.entity.projectile.ProjectileUtil.getEntityHitResult(
                this.level(), pilot, eye, end, new AABB(eye, end).inflate(1.0D),
                e -> e != this && e != pilot && e.isPickable() && !e.isSpectator());
        return entityHit != null ? entityHit.getLocation() : end;
    }

    public boolean isFiringWeapon() {
        return this.entityData.get(DATA_IS_FIRING);
    }

    // ==========================================
    // Weapon handling: raise -> fire -> magazine -> reload, holster
    // ==========================================
    private int lastTriggerTick = -100;
    private int raiseProgress = 0;

    /** The installed weapon, or null while the titan is unarmed (empty weapon slot). */
    @Nullable
    public TitanWeapon getActiveWeapon() {
        int id = this.entityData.get(DATA_WEAPON);
        return id < 0 ? null : TitanWeapon.byOrdinal(id);
    }

    public boolean hasWeapon() {
        return this.entityData.get(DATA_WEAPON) >= 0;
    }

    // ==========================================
    // Artillery fire control: the pilot sets target coordinates (rangefinder mark, typed coordinates or
    // +/- range corrections) and the computer solves the lob onto them.
    // ==========================================
    /** Per-tick gravity of a lobbed shell (TitanEnergyBlastEntity); the launch solve below must match it. */
    public static final double SHELL_GRAVITY = 0.05D;

    @Nullable
    public BlockPos getArtilleryTarget() {
        return this.entityData.get(DATA_ARTILLERY_TARGET).orElse(null);
    }

    /**
     * Sets the fire mission target from pilot input (trust boundary: coordinates come from the client).
     * A null y means "on the ground there". Rejected if outside the howitzer's range from where the titan stands.
     */
    public boolean setArtilleryTarget(Player pilot, int x, @Nullable Integer y, int z) {
        double range = Math.sqrt(Mth.square(x + 0.5D - this.getX()) + Mth.square(z + 0.5D - this.getZ()));
        if (range < Howitzer.MIN_RANGE || range > Howitzer.MAX_RANGE) {
            pilot.displayClientMessage(Component.translatable("message.titancombat.artillery_out_of_range", (int) range,
                    Howitzer.MIN_RANGE, Howitzer.MAX_RANGE), true);
            this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }
        // Only ground the world has generated and loaded: no blind fire into terrain that doesn't exist yet
        // (and Level.getHeight would answer "bottom of the world" there).
        if (!this.level().hasChunk(x >> 4, z >> 4)) {
            pilot.displayClientMessage(Component.translatable("message.titancombat.artillery_not_loaded"), true);
            this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }
        int ty = y != null ? y : this.level().getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
        ty = Mth.clamp(ty, this.level().getMinBuildHeight(), this.level().getMaxBuildHeight());
        this.entityData.set(DATA_ARTILLERY_TARGET, java.util.Optional.of(new BlockPos(x, ty, z)));
        this.entityData.set(DATA_ARTILLERY_LAYING, Howitzer.LAYING_TICKS);
        pilot.displayClientMessage(Component.translatable("message.titancombat.artillery_target_set", x, ty, z, (int) range), true);
        this.level().playSound(null, this.blockPosition(), SoundEvents.NOTE_BLOCK_PLING.get(), SoundSource.PLAYERS, 1.0F, 1.6F);
        return true;
    }

    /** Range correction: walk the target `steps` x 8 blocks further from / closer to the titan on its bearing. */
    public void nudgeArtilleryTarget(Player pilot, int steps) {
        BlockPos t = getArtilleryTarget();
        double bx, bz, range;
        if (t == null) {  // no mission yet: start one 64 blocks ahead of the pilot
            float rad = pilot.getYRot() * Mth.DEG_TO_RAD;
            bx = -Math.sin(rad);
            bz = Math.cos(rad);
            range = 64.0D;
        } else {
            double dx = t.getX() + 0.5D - this.getX(), dz = t.getZ() + 0.5D - this.getZ();
            range = Math.max(1.0D, Math.sqrt(dx * dx + dz * dz));
            bx = dx / range;
            bz = dz / range;
            range += steps * Howitzer.RANGE_STEP;
        }
        range = Mth.clamp(range, Howitzer.MIN_RANGE, Howitzer.MAX_RANGE);
        setArtilleryTarget(pilot, Mth.floor(this.getX() + bx * range), null, Mth.floor(this.getZ() + bz * range));
    }

    public int getArtilleryLaying() {
        return this.entityData.get(DATA_ARTILLERY_LAYING);
    }

    /** Where shells leave the titan: just above its back. */
    public Vec3 getArtilleryMuzzle() {
        return this.position().add(0.0D, this.getBbHeight() + 0.5D, 0.0D);
    }

    /**
     * Launch velocity that lands on `to` after `ticks` ticks, solved for vanilla throwable motion:
     * each tick the shell moves by its velocity, then the velocity is scaled by 0.99 and loses SHELL_GRAVITY.
     */
    public static Vec3 shellVelocity(Vec3 from, Vec3 to, int ticks) {
        double s = (1.0D - Math.pow(0.99D, ticks)) / 0.01D;  // sum of 0.99^k for k < ticks
        Vec3 d = to.subtract(from);
        double vy = (d.y + SHELL_GRAVITY / 0.01D * (ticks - s)) / s;
        return new Vec3(d.x / s, vy, d.z / s);
    }

    /** Longer shots fly higher arcs: about 1.5 s at minimum range, 5.5 s at maximum. */
    public static int shellFlightTicks(double range) {
        return 30 + (int) (range / 2.0D);
    }

    /** Firing solution for the current target: launch velocity, or null with no target. */
    @Nullable
    public Vec3 artillerySolution() {
        BlockPos t = getArtilleryTarget();
        if (t == null) return null;
        Vec3 from = getArtilleryMuzzle(), to = Vec3.atBottomCenterOf(t).add(0.0D, 1.0D, 0.0D);
        return shellVelocity(from, to, shellFlightTicks(to.subtract(from).horizontalDistance()));
    }

    public boolean hasHowitzer() {
        return this.entityData.get(DATA_HOWITZER);
    }

    public boolean hasRocketPod() {
        return this.entityData.get(DATA_ROCKET_POD);
    }

    public int getHowitzerRounds() {
        return this.entityData.get(DATA_HOWITZER_ROUNDS);
    }

    public int getHowitzerReload() {
        return this.entityData.get(DATA_HOWITZER_RELOAD);
    }

    private int howitzerCooldown = 0;
    private int rocketSalvoCooldown = 0;
    /** Fire on lock: a target picked with "fire" on the map fires by itself once the gun is laid. */
    private boolean fireMissionPending = false;

    /** Server tick: install/removal from the back slot, laying countdown, auto-reload, pending fire mission. */
    private void tickHowitzer() {
        boolean rocketInstalled = this.titanInventory.getItem(TitanMenu.FLIGHT_SLOT).getItem() instanceof com.titancombat.item.RocketLauncherModuleItem;
        if (rocketInstalled != hasRocketPod()) {
            this.entityData.set(DATA_ROCKET_POD, rocketInstalled);
        }
        if (rocketSalvoCooldown > 0) rocketSalvoCooldown--;
        if (!this.level().isClientSide) {
            this.entityData.set(DATA_ROCKET_COOLDOWN, rocketSalvoCooldown);
            if (this.tickCount % 5 == 0 && (rocketInstalled || hasRocketPod())) {
                this.entityData.set(DATA_ROCKET_AMMO, countRocketSalvoAmmo());
            }
        }

        boolean installed = this.titanInventory.getItem(TitanMenu.FLIGHT_SLOT).getItem() instanceof com.titancombat.item.HowitzerModuleItem;
        if (installed != hasHowitzer()) {
            this.entityData.set(DATA_HOWITZER, installed);
            if (!installed) {
                this.entityData.set(DATA_HOWITZER_ROUNDS, 0);
                this.entityData.set(DATA_HOWITZER_RELOAD, 0);
                this.fireMissionPending = false;
            }
        }
        if (getArtilleryLaying() > 0) this.entityData.set(DATA_ARTILLERY_LAYING, getArtilleryLaying() - 1);
        if (howitzerCooldown > 0) howitzerCooldown--;
        if (!installed) return;

        int reload = getHowitzerReload();
        if (reload > 0) {
            this.entityData.set(DATA_HOWITZER_RELOAD, reload - 1);
            if (reload == 1) {
                this.entityData.set(DATA_HOWITZER_ROUNDS, Howitzer.ROUNDS_PER_RACK);
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 1.8F, 0.5F);
            }
        } else if (getHowitzerRounds() <= 0 && takeShellRack(getControllingPassenger() instanceof Player p ? p : null)) {
            this.entityData.set(DATA_HOWITZER_RELOAD, Howitzer.RELOAD_TICKS);  // auto-loads the next rack
            this.level().playSound(null, this.blockPosition(), SoundEvents.PISTON_CONTRACT, SoundSource.PLAYERS, 1.6F, 0.6F);
        }
        if (fireMissionPending && getArtilleryLaying() == 0 && getHowitzerReload() == 0 && howitzerCooldown == 0
                && getControllingPassenger() instanceof Player pilot) {
            fireMissionPending = false;
            fireHowitzer(pilot);
        }
    }

    public boolean isHowitzerSmoke() {
        return this.entityData.get(DATA_HOWITZER_SMOKE);
    }

    public void setHowitzerSmoke(boolean smoke) {
        this.entityData.set(DATA_HOWITZER_SMOKE, smoke);
    }

    /** One shell rack from the titan bay, else from the pilot (creative pilots load for free). */
    private boolean takeShellRack(@Nullable Player pilot) {
        net.minecraft.world.item.Item smokeRack = com.titancombat.item.ModItems.HOWITZER_SMOKE_SHELLS.get();
        net.minecraft.world.item.Item regularRack = com.titancombat.item.ModItems.HOWITZER_SHELLS.get();

        if (pilot != null && pilot.getAbilities().instabuild) {
            // In creative mode, if holding smoke shells or titan bay has smoke shells, prioritize smoke
            boolean wantsSmoke = pilot.getMainHandItem().is(smokeRack) || pilot.getOffhandItem().is(smokeRack);
            if (!wantsSmoke) {
                for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
                    if (this.titanInventory.getItem(i).is(smokeRack)) {
                        wantsSmoke = true;
                        break;
                    }
                }
            }
            if (!wantsSmoke && isHowitzerSmoke()) wantsSmoke = true;
            setHowitzerSmoke(wantsSmoke);
            return true;
        }

        // Prioritize currently selected shell type, but fall back to the other if unavailable
        net.minecraft.world.item.Item primary = isHowitzerSmoke() ? smokeRack : regularRack;
        net.minecraft.world.item.Item secondary = isHowitzerSmoke() ? regularRack : smokeRack;

        // 1. Check titan inventory for primary
        for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
            ItemStack st = this.titanInventory.getItem(i);
            if (st.is(primary)) {
                st.shrink(1);
                setHowitzerSmoke(primary == smokeRack);
                return true;
            }
        }
        // 2. Check pilot inventory for primary
        if (pilot != null) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack st = pilot.getInventory().getItem(i);
                if (st.is(primary)) {
                    st.shrink(1);
                    setHowitzerSmoke(primary == smokeRack);
                    return true;
                }
            }
        }
        // 3. Check titan inventory for secondary fallback
        for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
            ItemStack st = this.titanInventory.getItem(i);
            if (st.is(secondary)) {
                st.shrink(1);
                setHowitzerSmoke(secondary == smokeRack);
                return true;
            }
        }
        // 4. Check pilot inventory for secondary fallback
        if (pilot != null) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack st = pilot.getInventory().getItem(i);
                if (st.is(secondary)) {
                    st.shrink(1);
                    setHowitzerSmoke(secondary == smokeRack);
                    return true;
                }
            }
        }
        return false;
    }

    public boolean cycleHowitzerShellType(Player pilot) {
        if (!hasHowitzer()) return false;
        boolean targetSmoke = !isHowitzerSmoke();
        net.minecraft.world.item.Item targetItem = targetSmoke
                ? com.titancombat.item.ModItems.HOWITZER_SMOKE_SHELLS.get()
                : com.titancombat.item.ModItems.HOWITZER_SHELLS.get();

        boolean hasTarget = (pilot != null && pilot.getAbilities().instabuild);
        if (!hasTarget) {
            for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
                if (this.titanInventory.getItem(i).is(targetItem)) {
                    hasTarget = true;
                    break;
                }
            }
        }
        if (!hasTarget && pilot != null) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                if (pilot.getInventory().getItem(i).is(targetItem)) {
                    hasTarget = true;
                    break;
                }
            }
        }

        if (hasTarget) {
            setHowitzerSmoke(targetSmoke);
            this.entityData.set(DATA_HOWITZER_ROUNDS, Howitzer.ROUNDS_PER_RACK);
            this.entityData.set(DATA_HOWITZER_RELOAD, Howitzer.RELOAD_TICKS);
            this.level().playSound(null, this.blockPosition(), SoundEvents.PISTON_CONTRACT, SoundSource.PLAYERS, 1.6F, 0.7F);
            pilot.displayClientMessage(Component.translatable(targetSmoke ? "message.titancombat.howitzer_loaded_smoke" : "message.titancombat.howitzer_loaded_he"), true);
            return true;
        } else {
            pilot.displayClientMessage(Component.translatable("message.titancombat.howitzer_no_alternate_ammo",
                    targetSmoke ? "Smoke Shells" : "HE Shells"), true);
            return false;
        }
    }

    /** Fire request from the pilot (howitzer key or map). With `onLock`, waits for the gun to be laid. */
    public void requestHowitzerFire(Player pilot, boolean onLock) {
        if (hasRocketPod()) {
            fireRocketPodSalvo(pilot);
            return;
        }
        if (!hasHowitzer()) return;
        if (onLock && getArtilleryLaying() > 0) {
            this.fireMissionPending = true;
            return;
        }
        fireHowitzer(pilot);
    }

    public boolean fireRocketPodSalvo(Player pilot) {
        if (!hasRocketPod() || this.isSitting() || this.isBoarding() || rocketSalvoCooldown > 0) return false;
        if (!takeRocketAmmo(pilot)) {
            if (pilot != null) pilot.displayClientMessage(Component.translatable("message.titancombat.rocket_no_ammo"), true);
            return false;
        }

        rocketSalvoCooldown = 25; // 1.25s salvo cooldown
        consumeEnergy(20);

        Vec3 shoulderPos = this.position().add(0, this.getBbHeight() * 0.88D, 0);
        float yawRad = this.yBodyRot * ((float) Math.PI / 180.0F);
        Vec3 right = new Vec3(-Math.cos(yawRad), 0, -Math.sin(yawRad));
        Vec3 forward = new Vec3(-Math.sin(yawRad), 0, Math.cos(yawRad));
        Vec3 launchOrigin = shoulderPos.add(right.scale(1.2D)).add(forward.scale(-0.2D));

        Vec3 aimTarget = computeAimPoint(pilot);
        Vec3 baseAim = aimTarget.subtract(launchOrigin).normalize();

        // Launch 4 rockets in a rapid burst
        for (int i = 0; i < 4; i++) {
            final int delay = i * 2;
            final double spreadX = (this.random.nextDouble() - 0.5D) * 0.12D;
            final double spreadY = (this.random.nextDouble() - 0.5D) * 0.12D;
            final double spreadZ = (this.random.nextDouble() - 0.5D) * 0.12D;

            if (delay == 0) {
                spawnRocket(pilot, launchOrigin, baseAim.add(spreadX, spreadY, spreadZ));
            } else if (this.level() instanceof ServerLevel serverLevel) {
                serverLevel.getServer().tell(new net.minecraft.server.TickTask(serverLevel.getServer().getTickCount() + delay, () -> {
                    if (this.isAlive()) {
                        spawnRocket(pilot, launchOrigin, baseAim.add(spreadX, spreadY, spreadZ));
                    }
                }));
            }
        }

        this.level().playSound(null, this.blockPosition(), ModSounds.TONE_FIRE.get(), SoundSource.PLAYERS, 2.5F, 1.0F);
        return true;
    }

    private void spawnRocket(Player pilot, Vec3 origin, Vec3 dir) {
        TitanBulletEntity rocket = new TitanBulletEntity(this.level(), pilot, 28.0F).withWeapon(TitanWeapon.ROCKET_POD);
        rocket.setPos(origin.x, origin.y, origin.z);
        rocket.shoot(dir.x, dir.y, dir.z, 2.4F, 0.05F);
        this.level().addFreshEntity(rocket);

        if (this.level() instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, origin.x, origin.y, origin.z, 5, 0.2, 0.2, 0.2, 0.02);
            serverLevel.sendParticles(ParticleTypes.FLAME, origin.x, origin.y, origin.z, 4, 0.1, 0.1, 0.1, 0.05);
        }
    }

    private boolean takeRocketAmmo(@Nullable Player pilot) {
        if (pilot != null && pilot.getAbilities().instabuild) return true;
        for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
            ItemStack stack = this.titanInventory.getItem(i);
            if (!stack.isEmpty() && (stack.is(ModItems.AMMO_ROCKET_SALVO.get()) || stack.is(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.ROCKET_POD).get()))) {
                stack.shrink(1);
                return true;
            }
        }
        if (pilot != null) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack stack = pilot.getInventory().getItem(i);
                if (!stack.isEmpty() && (stack.is(ModItems.AMMO_ROCKET_SALVO.get()) || stack.is(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.ROCKET_POD).get()))) {
                    stack.shrink(1);
                    return true;
                }
            }
        }
        return false;
    }

    public int getRocketSalvoCooldown() {
        return this.entityData.get(DATA_ROCKET_COOLDOWN);
    }

    public int getRocketSalvoAmmo() {
        return this.entityData.get(DATA_ROCKET_AMMO);
    }

    public int countRocketSalvoAmmo() {
        int count = 0;
        for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
            ItemStack stack = this.titanInventory.getItem(i);
            if (!stack.isEmpty() && (stack.is(ModItems.AMMO_ROCKET_SALVO.get()) || stack.is(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.ROCKET_POD).get()))) {
                count += stack.getCount();
            }
        }
        if (getControllingPassenger() instanceof Player pilot) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack stack = pilot.getInventory().getItem(i);
                if (!stack.isEmpty() && (stack.is(ModItems.AMMO_ROCKET_SALVO.get()) || stack.is(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.ROCKET_POD).get()))) {
                    count += stack.getCount();
                }
            }
        }
        return count;
    }

    /** Fires one shell onto the target, if there is one in range, the gun is laid and a round is loaded. */
    public boolean fireHowitzer(Player pilot) {
        if (!hasHowitzer() || this.isSitting() || this.isBoarding() || howitzerCooldown > 0) return false;
        BlockPos t = getArtilleryTarget();
        double range = t == null ? 0 : Math.sqrt(Mth.square(t.getX() + 0.5D - getX()) + Mth.square(t.getZ() + 0.5D - getZ()));
        String problem = t == null ? "message.titancombat.artillery_no_target"
                : range < Howitzer.MIN_RANGE || range > Howitzer.MAX_RANGE ? "message.titancombat.artillery_out_of_range"
                : getArtilleryLaying() > 0 ? "message.titancombat.artillery_laying"
                : getHowitzerReload() > 0 ? "message.titancombat.howitzer_reloading"
                : getHowitzerRounds() <= 0 ? "message.titancombat.howitzer_no_shells"
                : null;
        if (problem != null) {
            pilot.displayClientMessage(Component.translatable(problem, (int) range, Howitzer.MIN_RANGE, Howitzer.MAX_RANGE), true);
            this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.8F, 1.4F);
            return false;
        }
        Vec3 velocity = artillerySolution();
        if (velocity == null) return false;
        Vec3 from = getArtilleryMuzzle();
        if (isHowitzerSmoke()) {
            TitanSmokeShellEntity smokeShell = new TitanSmokeShellEntity(this.level(), pilot);
            smokeShell.setPos(from.x, from.y, from.z);
            smokeShell.setDeltaMovement(velocity);
            this.level().addFreshEntity(smokeShell);
        } else {
            TitanEnergyBlastEntity shell = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level())
                    .withStats(Howitzer.DAMAGE, Howitzer.EXPLOSION).lobbed();
            shell.setPos(from.x, from.y, from.z);
            shell.setDeltaMovement(velocity);
            this.level().addFreshEntity(shell);
        }
        this.entityData.set(DATA_HOWITZER_ROUNDS, getHowitzerRounds() - 1);
        howitzerCooldown = Howitzer.COOLDOWN_TICKS;
        this.level().playSound(null, this.blockPosition(), ModSounds.SCORCH_FIRE.get(), SoundSource.PLAYERS, 3.0F, 0.6F);
        this.level().broadcastEntityEvent(this, EVENT_HOWITZER_FIRE);
        if (!System.getProperty("titancombat.autotest", "").isEmpty()) {
            com.titancombat.TitanCombatMod.LOGGER.info("[autotest] howitzer fired at target {} ({} m)", t, (int) range);
        }
        return true;
    }

    public int getMagazine() {
        return this.entityData.get(DATA_MAGAZINE);
    }

    public int getReloadTicks() {
        return this.entityData.get(DATA_RELOAD_TICKS);
    }

    public boolean isReloading() {
        return getReloadTicks() > 0;
    }

    public boolean isWeaponLowered() {
        return this.entityData.get(DATA_WEAPON_LOWERED);
    }

    /** Weapon module in the bay's weapon slot, or null when the slot is empty. */
    @Nullable
    private TitanWeapon installedWeapon() {
        ItemStack module = this.titanInventory.getItem(TitanMenu.WEAPON_SLOT);
        return module.getItem() instanceof com.titancombat.item.TitanWeaponItem w ? w.getWeapon() : null;
    }

    /** Server tick: weapon swaps, reload completion, lowering the gun when the trigger is released. */
    private void tickWeaponSystems() {
        TitanWeapon installed = installedWeapon();
        if (installed != getActiveWeapon()) {
            // New weapon module: it arrives unloaded and has to be readied.
            this.entityData.set(DATA_WEAPON, installed == null ? -1 : installed.ordinal());
            this.entityData.set(DATA_MAGAZINE, 0);
            this.entityData.set(DATA_RELOAD_TICKS, 0);
            this.raiseProgress = 0;
        }

        int reload = getReloadTicks();
        if (reload > 0 && installed != null) {
            this.entityData.set(DATA_RELOAD_TICKS, reload - 1);
            if (reload - 1 == 0) {
                this.entityData.set(DATA_MAGAZINE, getActiveWeapon().getMagazineSize());
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 1.6F, 0.6F);
            }
        }

        // Trigger released for a while: the arm relaxes out of the firing position.
        if (this.tickCount - this.lastTriggerTick > 25 && this.raiseProgress > 0) {
            this.raiseProgress = Math.max(0, this.raiseProgress - 2);
        }
    }

    /** Flight module in the equipment bay slot, or NONE when the slot is empty. */
    public TitanFlightModule installedFlightModule() {
        if (this.titanInventory.getContainerSize() > com.titancombat.gui.TitanMenu.FLIGHT_SLOT) {
            ItemStack stack = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT);
            if (stack.getItem() instanceof com.titancombat.item.TitanFlightModuleItem f) {
                return f.getModule();
            }
        }
        return TitanFlightModule.NONE;
    }

    protected int coreModuleCooldown = 0;
    protected int cloakedTicks = 0;

    /** Server tick: flight equipment swaps (syncs the flight slot with entity flight state). */
    private void tickFlightSystems() {
        TitanFlightModule installed = installedFlightModule();
        if (installed != getFlightModule()) {
            setFlightModule(installed);
        }
        tickCoreModules();
    }

    private void tickCoreModules() {
        if (coreModuleCooldown > 0) coreModuleCooldown--;
        if (cloakedTicks > 0) {
            cloakedTicks--;
            if (cloakedTicks == 0) {
                this.setInvisible(false);
                if (getControllingPassenger() instanceof Player pilot) {
                    pilot.displayClientMessage(Component.translatable("message.titancombat.cloak_off"), true);
                }
                this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1.5F, 1.8F);
            }
        }
    }

    public boolean triggerCoreModule(Player pilot) {
        ItemStack backStack = this.titanInventory.getItem(TitanMenu.FLIGHT_SLOT);
        if (!(backStack.getItem() instanceof com.titancombat.item.TitanCoreModuleItem coreMod)) return false;

        if (coreModuleCooldown > 0) {
            pilot.displayClientMessage(Component.translatable("message.titancombat.core_cooldown", coreModuleCooldown / 20), true);
            this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.8F, 1.4F);
            return false;
        }

        switch (coreMod.getCoreType()) {
            case CLOAKING -> {
                this.setInvisible(true);
                this.cloakedTicks = 300; // 15 seconds
                this.coreModuleCooldown = 400; // 20s cooldown
                pilot.displayClientMessage(Component.translatable("message.titancombat.cloak_engaged"), true);
                this.level().playSound(null, this.blockPosition(), SoundEvents.ILLUSIONER_MIRROR_MOVE, SoundSource.PLAYERS, 2.0F, 0.8F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 1.8F, 1.4F);

                // Pacify mobs
                if (this.level() instanceof net.minecraft.server.level.ServerLevel sl) {
                    for (net.minecraft.world.entity.Mob mob : sl.getEntitiesOfClass(net.minecraft.world.entity.Mob.class, this.getBoundingBox().inflate(32.0D))) {
                        if (mob.getTarget() == this || mob.getTarget() == pilot) {
                            mob.setTarget(null);
                        }
                    }
                    for (int i = 0; i < 20; i++) {
                        sl.sendParticles(ParticleTypes.PORTAL, this.getX(), this.getY() + 2.0D, this.getZ(), 1,
                                (this.random.nextDouble() - 0.5D) * 2.0D, (this.random.nextDouble() - 0.5D) * 2.0D, (this.random.nextDouble() - 0.5D) * 2.0D, 0.1D);
                    }
                }
                return true;
            }
            case PHASE_WARP -> {
                this.coreModuleCooldown = 160; // 8s cooldown
                Vec3 look = this.getLookAngle().multiply(1, 0, 1).normalize();
                Vec3 target = this.position().add(look.scale(14.0D));
                int safeY = this.level().getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, (int) target.x, (int) target.z);

                if (this.level() instanceof net.minecraft.server.level.ServerLevel sl) {
                    // Departure effect
                    for (int i = 0; i < 30; i++) {
                        sl.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, this.getX(), this.getY() + 1.5D, this.getZ(), 1,
                                (this.random.nextDouble() - 0.5D) * 1.5D, (this.random.nextDouble() - 0.5D) * 1.5D, (this.random.nextDouble() - 0.5D) * 1.5D, 0.05D);
                    }
                }
                this.level().playSound(null, this.blockPosition(), SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 2.5F, 0.9F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.WARDEN_SONIC_BOOM, SoundSource.PLAYERS, 1.6F, 1.6F);

                // Teleport
                this.moveTo(target.x, safeY, target.z, this.getYRot(), this.getXRot());
                pilot.moveTo(target.x, safeY + 1.0D, target.z, pilot.getYRot(), pilot.getXRot());

                if (this.level() instanceof net.minecraft.server.level.ServerLevel sl) {
                    // Arrival effect
                    for (int i = 0; i < 30; i++) {
                        sl.sendParticles(ParticleTypes.REVERSE_PORTAL, target.x, safeY + 1.5D, target.z, 1,
                                (this.random.nextDouble() - 0.5D) * 1.5D, (this.random.nextDouble() - 0.5D) * 1.5D, (this.random.nextDouble() - 0.5D) * 1.5D, 0.05D);
                    }
                }
                pilot.displayClientMessage(Component.translatable("message.titancombat.warp_executed"), true);
                return true;
            }
            case SONAR_SCANNER -> {
                this.coreModuleCooldown = 200; // 10s cooldown
                List<LivingEntity> targets = this.level().getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(48.0D),
                        e -> e != this && e != pilot && (e.getVehicle() != this));
                for (LivingEntity e : targets) {
                    e.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.GLOWING, 240, 0, false, false));
                }

                this.level().playSound(null, this.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.get(), SoundSource.PLAYERS, 2.0F, 0.6F);
                this.level().playSound(null, this.blockPosition(), SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 2.0F, 1.4F);

                if (this.level() instanceof net.minecraft.server.level.ServerLevel sl) {
                    for (int i = 0; i < 36; i++) {
                        double angle = (i / 36.0D) * Math.PI * 2.0D;
                        sl.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, this.getX(), this.getY() + 1.5D, this.getZ(), 1,
                                Math.cos(angle) * 0.5D, 0.05D, Math.sin(angle) * 0.5D, 0.02D);
                    }
                }
                pilot.displayClientMessage(Component.translatable("message.titancombat.sonar_ping", targets.size()), true);
                return true;
            }
        }
        return false;
    }

    @Override
    public void toggleDefenseMatrix(Player pilot) {
        if (triggerCoreModule(pilot)) return;
        super.toggleDefenseMatrix(pilot);
    }

    @Override
    public boolean activateCoreOverdrive(Player pilot) {
        if (triggerCoreModule(pilot)) return true;
        return super.activateCoreOverdrive(pilot);
    }

    public boolean hasInstalledBattery() {
        ItemStack batteryStack = this.titanInventory.getItem(TitanMenu.BATTERY_SLOT);
        return !batteryStack.isEmpty() && batteryStack.getItem() instanceof com.titancombat.item.TitanBatteryItem
                && com.titancombat.item.TitanBatteryItem.getEnergy(batteryStack) > 0;
    }

    /** Holster / draw toggle. A lowered gun rides on the back and the arms relax. */
    public void toggleWeaponLowered(Player pilot) {
        boolean lower = !isWeaponLowered();
        this.entityData.set(DATA_WEAPON_LOWERED, lower);
        this.raiseProgress = 0;
        this.entityData.set(DATA_IS_FIRING, false);
        this.fireAnimTimer = 0;
        this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_IRON, SoundSource.PLAYERS, 1.6F, lower ? 0.6F : 0.8F);
        pilot.displayClientMessage(Component.translatable(lower ? "message.titancombat.weapon_lowered" : "message.titancombat.weapon_raised"), true);
    }

    /** Swap in a fresh magazine of this weapon's ammunition (titan bay first, then the pilot). */
    public boolean startReload(Player pilot) {
        if (this.level().isClientSide || isReloading() || this.isSitting() || this.isBoarding()) return false;
        TitanWeapon weapon = getActiveWeapon();
        if (weapon == null) {
            pilot.displayClientMessage(Component.translatable("message.titancombat.no_weapon"), true);
            return false;
        }
        if (getMagazine() >= weapon.getMagazineSize()) return false;

        if (!pilot.getAbilities().instabuild && !consumeMagazine(pilot, weapon)) {
            pilot.displayClientMessage(Component.translatable("message.titancombat.no_magazine",
                    Component.translatable("item.titancombat.ammo_" + weapon.getId())), true);
            this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.4F);
            return false;
        }
        this.entityData.set(DATA_RELOAD_TICKS, weapon.getReloadTicks());
        this.entityData.set(DATA_IS_FIRING, false);
        this.fireAnimTimer = 0;
        this.triggerAnim("arms", "reload");
        this.level().playSound(null, this.blockPosition(), ModSounds.ION_RELOAD.get(), SoundSource.PLAYERS, 1.8F, 1.0F);
        return true;
    }

    private boolean consumeMagazine(Player pilot, TitanWeapon weapon) {
        Container[] sources = {this.titanInventory, pilot.getInventory()};
        // Dedicated magazines first; generic Titan Ammo crates are accepted as a fallback.
        for (boolean generic : new boolean[]{false, true}) {
            for (Container c : sources) {
                for (int i = 0; i < c.getContainerSize(); i++) {
                    ItemStack s = c.getItem(i);
                    boolean match = generic ? s.getItem() instanceof com.titancombat.item.TitanAmmoItem
                            : s.getItem() instanceof com.titancombat.item.TitanMagazineItem m && m.getWeapon() == weapon;
                    if (match) {
                        s.shrink(1);
                        c.setChanged();
                        return true;
                    }
                }
            }
        }
        return false;
    }

    public boolean firePrimaryWeapon(Player pilot) {
        if (this.isSitting() || this.isBoarding()) return false;
        TitanWeapon weapon = getActiveWeapon();
        if (weapon == null) {
            // Unarmed chassis: remind the pilot (throttled) to fit a weapon module in the bay.
            if (this.tickCount - this.lastTriggerTick > 20) {
                pilot.displayClientMessage(Component.translatable("message.titancombat.no_weapon"), true);
                this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.8F, 1.2F);
            }
            this.lastTriggerTick = this.tickCount;
            return false;
        }
        this.lastTriggerTick = this.tickCount;

        // Pulling the trigger with the gun holstered draws it first (takes longer than a raise).
        if (isWeaponLowered()) {
            this.entityData.set(DATA_WEAPON_LOWERED, false);
            this.raiseProgress = -10;
        }

        // Bring the weapon up (aiming pose; Legion spins up its barrels) before any round is fired.
        this.entityData.set(DATA_IS_FIRING, true);
        this.fireAnimTimer = Math.max(this.fireAnimTimer, 14);
        if (isReloading()) return false;
        if (this.raiseProgress < weapon.getRaiseTicks()) {
            this.raiseProgress++;
            return false;
        }
        if (firingCooldown > 0) return false;
        if (getEnergy() <= 0) {
            if (this.tickCount % 20 == 0) {
                pilot.displayClientMessage(Component.translatable("message.titancombat.weapon_no_energy"), true);
                this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.8F, 1.8F);
            }
            return false;
        }

        boolean isOverdrive = isOverdriveActive();
        boolean isUtilityTool = (weapon == TitanWeapon.MINING_DRILL || weapon == TitanWeapon.CHAINSAW);
        boolean freeAmmo = isOverdrive;
        if (!freeAmmo) {
            if (getMagazine() <= 0) {
                // If it's a utility tool, check if reactor/dash energy is available
                if (isUtilityTool && (getDashCharge() > 0 || hasInstalledBattery())) {
                    setDashCharge(Math.max(0.0F, getDashCharge() - 0.2F));
                } else {
                    // Dry: click, then reload automatically if there is a magazine.
                    this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 0.8F, 1.8F);
                    firingCooldown = 10;
                    startReload(pilot);
                    return false;
                }
            } else {
                this.entityData.set(DATA_MAGAZINE, getMagazine() - 1);
            }
        }

        executeWeaponShot(pilot, weapon);
        consumeEnergy(15);
        firingCooldown = isOverdrive ? Math.max(1, Math.round(weapon.getCooldownTicks() * 0.4F)) : weapon.getCooldownTicks();
        if (!isOverdrive) addCoreCharge(2.5F);

        // Hold the aiming pose through the whole fire cycle so automatic fire doesn't flicker back to idle.
        this.fireAnimTimer = Math.max(14, firingCooldown + 8);
        this.level().broadcastEntityEvent(this, EVENT_WEAPON_FIRE);
        return true;
    }

    protected void executeWeaponShot(Player pilot, TitanWeapon weapon) {
        // Converge on whatever is under the pilot's crosshair, fired from the weapon itself.
        Vec3 spawnPos = getMuzzlePosition();
        Vec3 target = computeAimPoint(pilot);
        if (!System.getProperty("titancombat.autotest", "").isEmpty()) {
            com.titancombat.TitanCombatMod.LOGGER.info("[autotest] fired at {} (client aim {}), muzzle {}", target, this.tickCount - this.pilotAimTick <= 2, spawnPos);
        }

        // Specialized excavation and forestry attachments
        if (weapon == TitanWeapon.MINING_DRILL) {
            performDrillExcavation(pilot, target);
            return;
        }
        if (weapon == TitanWeapon.CHAINSAW) {
            performChainsawHarvest(pilot, target);
            return;
        }

        Vec3 aim = target.subtract(spawnPos).normalize();

        float yawRad = this.yBodyRot * ((float) Math.PI / 180.0F);
        Vec3 forward = new Vec3(-Math.sin(yawRad), 0, Math.cos(yawRad));
        Vec3 right = new Vec3(-Math.cos(yawRad), 0, -Math.sin(yawRad));
        Vec3 ejectPos = spawnPos.subtract(aim.scale(0.8D)).add(right.scale(0.4D)).add(0.0D, 0.1D, 0.0D);

        for (int i = 0; i < weapon.getPellets(); i++) {
            TitanBulletEntity round = new TitanBulletEntity(this.level(), pilot, weapon.getDamage()).withWeapon(weapon);
            round.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
            round.shoot(aim.x, aim.y, aim.z, weapon.getProjectileSpeed(), weapon.getSpread());
            this.level().addFreshEntity(round);
        }

        // Fling spent casing for ballistic weapons
        if (weapon != TitanWeapon.SPLITTER_RIFLE && weapon != TitanWeapon.PLASMA_RAILGUN && weapon != TitanWeapon.THERMITE_LAUNCHER && weapon != TitanWeapon.ROCKET_POD) {
            TitanCasingEntity casing = new TitanCasingEntity(this.level(), ejectPos, forward, right);
            this.level().addFreshEntity(casing);
        }
        this.level().playSound(null, this.blockPosition(), weapon.getFireSound(), SoundSource.PLAYERS, 2.2F, 1.0F);

        if (weapon == TitanWeapon.XO16_CHAINGUN && getTitanClass() == TitanClass.MONARCH) {
            this.setShield(this.getShield() + 2.0F); // Monarch's energy siphon
        }
    }

    /** Heavy mining drill excavation: mines blocks in front of the titan and gathers drops to cargo. */
    protected void performDrillExcavation(Player pilot, Vec3 target) {
        if (!(this.level() instanceof net.minecraft.server.level.ServerLevel serverLevel)) return;
        Vec3 start = getMuzzlePosition();
        Vec3 dir = target.subtract(start).normalize();
        double reach = 14.0D;
        net.minecraft.world.phys.BlockHitResult hit = serverLevel.clip(new net.minecraft.world.level.ClipContext(
                start, start.add(dir.scale(reach)),
                net.minecraft.world.level.ClipContext.Block.COLLIDER,
                net.minecraft.world.level.ClipContext.Fluid.NONE,
                this
        ));

        if (hit.getType() == net.minecraft.world.phys.HitResult.Type.BLOCK) {
            BlockPos center = hit.getBlockPos();
            boolean mined = false;
            int radius = 1;
            for (int dx = -radius; dx <= radius; dx++) {
                for (int dy = -radius; dy <= radius; dy++) {
                    for (int dz = -radius; dz <= radius; dz++) {
                        BlockPos p = center.offset(dx, dy, dz);
                        if (p.distSqr(center) > 2.8D) continue;
                        BlockState state = serverLevel.getBlockState(p);
                        if (state.isAir()) continue;
                        float hardness = state.getDestroySpeed(serverLevel, p);
                        if (hardness >= 0.0F && hardness <= 55.0F && !state.is(Blocks.BEDROCK)) {
                            breakAndCollectBlock(serverLevel, p, state, pilot);
                            mined = true;
                        }
                    }
                }
            }
            if (mined) {
                serverLevel.playSound(null, center, SoundEvents.ANVIL_HIT, SoundSource.PLAYERS, 1.2F, 1.8F);
                serverLevel.playSound(null, center, SoundEvents.GRINDSTONE_USE, SoundSource.PLAYERS, 1.4F, 1.4F);
            }
        } else {
            damageMeleeEntitiesInAim(pilot, dir, 28.0F, 10.0D);
        }
    }

    /** Heavy hydraulic chainsaw harvest: fells logs and foliage, gathering timber to cargo. */
    protected void performChainsawHarvest(Player pilot, Vec3 target) {
        if (!(this.level() instanceof net.minecraft.server.level.ServerLevel serverLevel)) return;
        Vec3 start = getMuzzlePosition();
        Vec3 dir = target.subtract(start).normalize();
        double reach = 14.0D;
        net.minecraft.world.phys.BlockHitResult hit = serverLevel.clip(new net.minecraft.world.level.ClipContext(
                start, start.add(dir.scale(reach)),
                net.minecraft.world.level.ClipContext.Block.COLLIDER,
                net.minecraft.world.level.ClipContext.Fluid.NONE,
                this
        ));

        if (hit.getType() == net.minecraft.world.phys.HitResult.Type.BLOCK) {
            BlockPos center = hit.getBlockPos();
            BlockState hitState = serverLevel.getBlockState(center);
            if (hitState.is(net.minecraft.tags.BlockTags.LOGS) || hitState.is(net.minecraft.tags.BlockTags.LEAVES)) {
                Set<BlockPos> tree = new HashSet<>();
                Queue<BlockPos> queue = new ArrayDeque<>();
                queue.add(center);
                tree.add(center);
                int maxBlocks = 48;
                while (!queue.isEmpty() && tree.size() < maxBlocks) {
                    BlockPos cur = queue.poll();
                    for (net.minecraft.core.Direction d : net.minecraft.core.Direction.values()) {
                        BlockPos n = cur.relative(d);
                        if (!tree.contains(n) && n.distSqr(center) <= 200.0D) {
                            BlockState bs = serverLevel.getBlockState(n);
                            if (bs.is(net.minecraft.tags.BlockTags.LOGS) || bs.is(net.minecraft.tags.BlockTags.LEAVES)) {
                                tree.add(n);
                                queue.add(n);
                                if (tree.size() >= maxBlocks) break;
                            }
                        }
                    }
                }
                for (BlockPos p : tree) {
                    BlockState bs = serverLevel.getBlockState(p);
                    breakAndCollectBlock(serverLevel, p, bs, pilot);
                }
                serverLevel.playSound(null, center, SoundEvents.WOOD_BREAK, SoundSource.PLAYERS, 1.8F, 0.8F);
                serverLevel.playSound(null, center, SoundEvents.GRINDSTONE_USE, SoundSource.PLAYERS, 1.2F, 1.6F);
            } else {
                float hardness = hitState.getDestroySpeed(serverLevel, center);
                if (hardness >= 0.0F && hardness <= 25.0F && !hitState.isAir()) {
                    breakAndCollectBlock(serverLevel, center, hitState, pilot);
                    serverLevel.playSound(null, center, SoundEvents.WOOD_BREAK, SoundSource.PLAYERS, 1.4F, 1.0F);
                }
            }
        } else {
            damageMeleeEntitiesInAim(pilot, dir, 36.0F, 10.0D);
        }
    }

    private void breakAndCollectBlock(net.minecraft.server.level.ServerLevel level, BlockPos pos, BlockState state, Player pilot) {
        ItemStack tool = new ItemStack(net.minecraft.world.item.Items.DIAMOND_PICKAXE);
        List<ItemStack> drops = Block.getDrops(state, level, pos, null, pilot, tool);
        level.destroyBlock(pos, false, this);
        for (ItemStack drop : drops) {
            ItemStack remain = insertIntoCargo(drop);
            if (!remain.isEmpty()) {
                Block.popResource(level, pos, remain);
            }
        }
    }

    /** Attempts to insert item into titan cargo slots (3..11), returns uninserted leftovers. */
    public ItemStack insertIntoCargo(ItemStack stack) {
        if (stack.isEmpty()) return ItemStack.EMPTY;
        ItemStack toInsert = stack.copy();
        for (int i = TitanMenu.CARGO_START; i <= TitanMenu.CARGO_END; i++) {
            ItemStack existing = this.titanInventory.getItem(i);
            if (!existing.isEmpty() && ItemStack.isSameItemSameTags(existing, toInsert)) {
                int max = Math.min(existing.getMaxStackSize(), this.titanInventory.getMaxStackSize());
                int space = max - existing.getCount();
                if (space > 0) {
                    int add = Math.min(space, toInsert.getCount());
                    existing.grow(add);
                    toInsert.shrink(add);
                    if (toInsert.isEmpty()) return ItemStack.EMPTY;
                }
            }
        }
        for (int i = TitanMenu.CARGO_START; i <= TitanMenu.CARGO_END; i++) {
            if (this.titanInventory.getItem(i).isEmpty()) {
                this.titanInventory.setItem(i, toInsert.copy());
                return ItemStack.EMPTY;
            }
        }
        return toInsert;
    }

    private void damageMeleeEntitiesInAim(Player pilot, Vec3 aimDir, float damage, double range) {
        Vec3 start = getMuzzlePosition();
        Vec3 end = start.add(aimDir.scale(range));
        AABB box = new AABB(start, end).inflate(2.0D);
        List<LivingEntity> targets = this.level().getEntitiesOfClass(LivingEntity.class, box,
                e -> e != this && e != pilot && e.isAlive() && !this.isAlliedTo(e));
        for (LivingEntity target : targets) {
            target.hurt(this.damageSources().mobAttack(this), damage);
            target.knockback(0.4D, -aimDir.x, -aimDir.z);
        }
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);

        // License / transponder / battery interact in their own interactLivingEntity
        if (held.getItem() instanceof com.titancombat.item.PilotLicenseItem
                || held.getItem() instanceof com.titancombat.item.HangarTransponderItem
                || held.getItem() instanceof com.titancombat.item.TitanBatteryItem) {
            return held.getItem().interactLivingEntity(held, player, this, hand);
        }

        // 1. Repair with Iron Ingot (Heals 25 HP)
        if (held.is(Items.IRON_INGOT)) {
            if (this.getHealth() < this.getMaxHealth()) {
                if (!this.level().isClientSide) {
                    this.heal(25.0F);
                    if (!player.getAbilities().instabuild) held.shrink(1);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.0F, 1.4F);
                    player.sendSystemMessage(Component.translatable("message.titancombat.hull_repaired", (int) this.getHealth(), (int) this.getMaxHealth()));
                } else {
                    for (int i = 0; i < 8; i++) {
                        this.level().addParticle(ParticleTypes.CRIT,
                                this.getX() + (this.random.nextDouble() - 0.5D) * 1.5D,
                                this.getY() + 1.0D + this.random.nextDouble() * 2.0D,
                                this.getZ() + (this.random.nextDouble() - 0.5D) * 1.5D,
                                0, 0.2D, 0);
                    }
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide);
            }
        }

        // 2. Repair with Iron Block (Heals 250 HP)
        if (held.is(Items.IRON_BLOCK)) {
            if (this.getHealth() < this.getMaxHealth()) {
                if (!this.level().isClientSide) {
                    this.heal(250.0F);
                    if (!player.getAbilities().instabuild) held.shrink(1);
                    this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.PLAYERS, 1.2F, 1.0F);
                    player.sendSystemMessage(Component.translatable("message.titancombat.hull_repaired", (int) this.getHealth(), (int) this.getMaxHealth()));
                }
                return InteractionResult.sidedSuccess(this.level().isClientSide);
            }
        }

        // 3. Camo Spray Painting & Dyeing
        if (held.getItem() instanceof PaintSprayCanItem || held.getItem() instanceof DyeItem) {
            if (!this.level().isClientSide) {
                int nextCamo;
                if (held.getItem() instanceof DyeItem dye) {
                    nextCamo = switch (dye.getDyeColor()) {
                        case RED -> 5; // Crimson Red
                        case BLUE, CYAN -> 6; // Cobalt Blue
                        case GREEN, LIME -> 2; // Woodland Green
                        case YELLOW, ORANGE -> 7; // Hazard Industrial
                        case WHITE, LIGHT_GRAY -> 4; // Arctic Snow
                        case BLACK, GRAY -> 8; // Stealth Black Ops
                        case BROWN -> 1; // Desert Tan
                        default -> 3; // Urban Digital
                    };
                } else {
                    nextCamo = (getCamoIndex() + 1) % 9;
                }
                setCamoIndex(nextCamo);
                this.level().playSound(null, this.blockPosition(), SoundEvents.ANVIL_PLACE, SoundSource.PLAYERS, 0.8F, 1.8F);
                player.sendSystemMessage(Component.translatable("message.titancombat.camo_applied", nextCamo));
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Install / Swap Weapon Module directly with Weapon Item
        if (held.getItem() instanceof com.titancombat.item.TitanWeaponItem weaponItem) {
            if (!this.level().isClientSide) {
                ItemStack oldInSlot = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.WEAPON_SLOT);
                this.titanInventory.setItem(com.titancombat.gui.TitanMenu.WEAPON_SLOT, held.split(1));
                this.entityData.set(DATA_WEAPON, weaponItem.getWeapon().ordinal());
                this.entityData.set(DATA_MAGAZINE, 0);
                this.entityData.set(DATA_RELOAD_TICKS, 0);
                this.raiseProgress = 0;
                this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.6F, 1.0F);
                if (!player.getAbilities().instabuild && !oldInSlot.isEmpty()) {
                    if (!player.getInventory().add(oldInSlot)) {
                        this.spawnAtLocation(oldInSlot);
                    }
                }
                player.sendSystemMessage(Component.translatable("message.titancombat.weapon_installed",
                        Component.translatable(weaponItem.getWeapon().getTranslationKey()), getTitanClass().getDisplayName()));
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Install / Swap Flight Module directly with Flight Module Item
        if (held.getItem() instanceof com.titancombat.item.TitanFlightModuleItem flightItem) {
            if (!this.level().isClientSide) {
                ItemStack oldInSlot = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT);
                this.titanInventory.setItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT, held.split(1));
                setFlightModule(flightItem.getModule());
                this.level().playSound(null, this.blockPosition(), SoundEvents.ARMOR_EQUIP_NETHERITE, SoundSource.PLAYERS, 1.6F, 1.0F);
                if (!player.getAbilities().instabuild && !oldInSlot.isEmpty()) {
                    if (!player.getInventory().add(oldInSlot)) {
                        this.spawnAtLocation(oldInSlot);
                    }
                }
                player.sendSystemMessage(Component.translatable("message.titancombat.flight_module_installed",
                        flightItem.getModule().getDisplayName(), getTitanClass().getDisplayName()));
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // Uninstall Weapon or Flight Module with Maintenance Blowtorch when sneaking
        if (held.getItem() instanceof com.titancombat.item.MaintenanceBlowtorchItem && player.isShiftKeyDown() && (hasWeapon() || hasFlightModule())) {
            if (!this.level().isClientSide) {
                if (hasWeapon()) {
                    ItemStack oldStack = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.WEAPON_SLOT);
                    if (oldStack.isEmpty() && getActiveWeapon() != null) {
                        oldStack = new ItemStack(com.titancombat.item.ModItems.WEAPON_MODULES.get(getActiveWeapon()).get());
                    }
                    this.titanInventory.setItem(com.titancombat.gui.TitanMenu.WEAPON_SLOT, ItemStack.EMPTY);
                    this.entityData.set(DATA_WEAPON, -1);
                    this.entityData.set(DATA_MAGAZINE, 0);
                    this.entityData.set(DATA_RELOAD_TICKS, 0);
                    this.raiseProgress = 0;
                    if (!player.getInventory().add(oldStack)) {
                        this.spawnAtLocation(oldStack);
                    }
                    held.hurtAndBreak(1, player, (p) -> p.broadcastBreakEvent(hand));
                    this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 1.0F, 0.8F);
                    player.sendSystemMessage(Component.translatable("message.titancombat.weapon_uninstalled"));
                } else if (hasFlightModule()) {
                    ItemStack oldStack = this.titanInventory.getItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT);
                    if (oldStack.isEmpty()) {
                        TitanFlightModule old = getFlightModule();
                        oldStack = new ItemStack(com.titancombat.item.ModItems.FLIGHT_MODULES.get(old).get());
                    }
                    this.titanInventory.setItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT, ItemStack.EMPTY);
                    setFlightModule(TitanFlightModule.NONE);
                    if (!player.getInventory().add(oldStack)) {
                        this.spawnAtLocation(oldStack);
                    }
                    held.hurtAndBreak(1, player, (p) -> p.broadcastBreakEvent(hand));
                    this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_TRAPDOOR_CLOSE, SoundSource.PLAYERS, 1.0F, 0.8F);
                    player.sendSystemMessage(Component.translatable("message.titancombat.flight_module_uninstalled"));
                }
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // 4. Open Maintenance Cargo Bay Screen (Shift-Click with Empty Hand from outside)
        if (held.isEmpty() && player.isShiftKeyDown() && !this.isVehicle()) {
            if (!this.level().isClientSide) {
                openCustomInventoryScreen(player);
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_DOOR_OPEN, SoundSource.PLAYERS, 1.0F, 0.9F);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // 5. Board Cockpit with BIOMETRIC PILOT LICENSE LOCK (any held item: the mech fallback below skips the lock)
        if (!this.isVehicle() && !player.isPassenger()) {
            if (!this.level().isClientSide) {
                String owner = getOwnerUUID();
                if (!owner.isEmpty() && !player.getUUID().toString().equals(owner)) {
                    player.sendSystemMessage(Component.translatable("message.titancombat.access_denied", getOwnerName()));
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.5F, 0.6F);
                    return InteractionResult.FAIL;
                }

                if (owner.isEmpty()) {
                    BaseTitanEntity existing = com.titancombat.util.TitanWarpHelper.findCurrentTitanOfPlayer(player.getServer(), player);
                    if (existing != null && existing != this) {
                        player.sendSystemMessage(Component.translatable("message.titancombat.single_titan_limit", existing.getTitanClass().getDisplayName()));
                        this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.5F, 0.6F);
                        return InteractionResult.FAIL;
                    }

                    setOwner(player);
                    player.sendSystemMessage(Component.translatable("message.titancombat.neural_link_claimed", player.getName().getString(), getTitanClass().getDisplayName()));
                }
                com.titancombat.item.PilotLicenseItem.autoLinkInventory(player, this);

                setStandbyMode(false);
                player.startRiding(this);
                setMechState(MechState.PILOTED);

                // A standing titan reaches down, lifts the pilot and seals the hatch before it can move.
                if (!isKneeling()) {
                    this.triggerAnim("body", "entry_front");
                    this.boardingTicks = BOARDING_TICKS;
                    this.level().broadcastEntityEvent(this, EVENT_EMBARK);
                } else if (isSitting()) {
                    // Parked: close the hatch, then stand up automatically.
                    this.boardingTicks = 46;
                    this.standUpAtTick = 30;
                    this.level().broadcastEntityEvent(this, EVENT_EMBARK);
                }

                // Authentic Titanfall pneumatic cabin seal sound!
                this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_CABIN_ENTER.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                player.sendSystemMessage(Component.translatable("message.titancombat.os_welcome", getTitanClass().getDisplayName()));
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        return super.mobInteract(player, hand);
    }

    // ==========================================
    // GeckoLib 4 Animation Controllers
    // ==========================================
    // Mirrors the original addon's controller layout:
    //  - "legs": idle / walk / run (sprint) / spurt (dash), played at the gait's stride-matched rate,
    //    carrying the footstep sound keyframes.
    //  - "arms": idle / run sway / firing pose, plus triggered melee swings.
    //  - "body": full-body poses (orbital drop, kneel, stand-up, boarding). Registered last so it wins,
    //    and legs/arms stop while it holds a pose so the two never fight over the arm bones.
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        String p = animPrefix();

        AnimationController<BaseTitanEntity> legs = new AnimationController<>(this, "legs", 6, this::legsPredicate);
        legs.setAnimationSpeedHandler(BaseTitanEntity::getLocomotionPlayback);
        legs.setSoundKeyframeHandler(event -> com.titancombat.client.TitanClientEffects.onSoundKeyframe(
                event.getAnimatable(), event.getKeyframeData().getSound()));
        controllers.add(legs);

        AnimationController<BaseTitanEntity> arms = new AnimationController<>(this, "arms", 5, this::armsPredicate);
        arms.setAnimationSpeedHandler(t -> t.getGait() == Gait.RUN && !t.isFiringWeapon() ? t.getLocomotionPlayback() : 1.0D);
        arms.triggerableAnim("melee", RawAnimation.begin().then(p + "melee", Animation.LoopType.PLAY_ONCE));
        arms.triggerableAnim("reload", RawAnimation.begin().then(p + "reload", Animation.LoopType.PLAY_ONCE));
        if (getTitanClass() == TitanClass.RONIN) {
            for (int i = 1; i <= 3; i++) {
                arms.triggerableAnim("melee_core_" + i, RawAnimation.begin().then(p + "melee_core_" + i, Animation.LoopType.PLAY_ONCE));
            }
        }
        controllers.add(arms);

        AnimationController<BaseTitanEntity> body = new AnimationController<>(this, "body", 8, this::bodyPredicate);
        body.triggerableAnim("standing", RawAnimation.begin().then(p + "standing", Animation.LoopType.PLAY_ONCE));
        body.triggerableAnim("entry_front", RawAnimation.begin().then(p + "entry_stand_front", Animation.LoopType.PLAY_ONCE));
        controllers.add(body);

        // Cockpit hatch swings open while a parked titan waits for its pilot.
        controllers.add(new AnimationController<>(this, "hatch", 10, this::hatchPredicate));
    }

    private String animPrefix() {
        return "animation." + getTitanClass().getId() + "_titan.";
    }

    // GeckoLib won't restart a controller that was stopped if it is handed an identical clip again,
    // which froze titans after their first park/stand cycle. Every predicate goes through these two
    // helpers so a change of clip (including from "stopped") always forces a fresh start.
    private final java.util.Map<String, String> currentClips = new java.util.HashMap<>();

    private PlayState play(AnimationState<BaseTitanEntity> event, String key, RawAnimation animation) {
        String controller = event.getController().getName();
        if (!key.equals(this.currentClips.put(controller, key))) {
            event.getController().forceAnimationReset();
        }
        return event.setAndContinue(animation);
    }

    private PlayState stop(AnimationState<BaseTitanEntity> event) {
        this.currentClips.remove(event.getController().getName());
        return PlayState.STOP;
    }

    protected PlayState bodyPredicate(AnimationState<BaseTitanEntity> event) {
        MechState state = getMechState();
        if (state == MechState.DROPPING) {
            return play(event, "loading", RawAnimation.begin().thenPlayAndHold(animPrefix() + "loading"));
        }
        if (isKneeling()) {
            return play(event, "loaded", RawAnimation.begin().thenLoop(animPrefix() + "loaded"));
        }
        return stop(event);
    }

    protected PlayState hatchPredicate(AnimationState<BaseTitanEntity> event) {
        if (isKneeling() && !this.isVehicle() && getMechState() != MechState.DROPPING) {
            return play(event, "open", RawAnimation.begin().thenPlayAndHold(animPrefix() + "entry_loaded_open_door"));
        }
        return stop(event);
    }

    protected PlayState legsPredicate(AnimationState<BaseTitanEntity> event) {
        if (isKneeling()) return stop(event); // full-body pose owns the legs; play()/stop() restart cleanly
        String p = animPrefix();
        if (isFlying() || (!this.onGround() && hasFlightModule())) {
            return play(event, "flight", RawAnimation.begin().thenPlayAndHold(p + "spurt.leg"));
        }
        return switch (this.gait) {
            case DASH -> play(event, "dash", RawAnimation.begin().thenPlayAndHold(p + "spurt.leg"));
            case RUN -> play(event, "run", RawAnimation.begin().thenLoop(p + "move.leg"));
            case WALK -> play(event, "walk", RawAnimation.begin().thenLoop(p + "walk.leg"));
            default -> play(event, "idle", RawAnimation.begin().thenLoop(p + "idle.leg"));
        };
    }

    protected PlayState armsPredicate(AnimationState<BaseTitanEntity> event) {
        if (isKneeling() || isSaluting()) return stop(event);
        String p = animPrefix();

        if (isFiringWeapon() && !isKneeling() && !isWeaponLowered() && !isReloading()) {
            if (getTitanClass() == TitanClass.LEGION) {
                // Predator cannon spins up before the barrage.
                return play(event, "fire", RawAnimation.begin().thenPlay(p + "fire_pre").thenLoop(p + "fire"));
            }
            return play(event, "fire", RawAnimation.begin().thenLoop(p + "fire"));
        }

        // Unarmed titans (or artillery on the back): stop rifle holding animation to let arms hang and swing naturally.
        if (!hasWeapon()) {
            return stop(event);
        }

        if (this.gait == Gait.RUN && !isKneeling()) {
            return play(event, "run", RawAnimation.begin().thenLoop(p + "move.arm"));
        }

        if (getTitanClass() == TitanClass.RONIN) {
            return play(event, "idle", RawAnimation.begin().thenLoop(p + "idle_sword.arm"));
        }

        return play(event, "idle", RawAnimation.begin().thenLoop(p + "idle.arm"));
    }

    /**
     * Which copy of the weapon is visible. Every model carries the gun twice (in hand and stowed on the
     * back) and Ronin carries its sword twice; the addon hides one of each depending on state. The gun
     * is stowed while parked (so the lowered hand is free for the pilot) and during melee or salute.
     */
    public boolean isWeaponStowed() {
        return (isKneeling() && !isBoarding()) || this.entityData.get(DATA_IS_MELEEING) || isSaluting();
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }

    @Override
    public void die(DamageSource cause) {
        clearOwner();
        super.die(cause);
    }

    @Override
    protected void dropCustomDeathLoot(DamageSource source, int looting, boolean recentlyHit) {
        super.dropCustomDeathLoot(source, looting, recentlyHit);
        for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
            ItemStack stack = this.titanInventory.getItem(i);
            if (!stack.isEmpty()) {
                this.spawnAtLocation(stack);
            }
        }
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putInt("CamoIndex", getCamoIndex());
        tag.putBoolean("StandbyMode", isStandbyMode());
        tag.putBoolean("IsSitting", isSitting());
        tag.putString("OwnerUUID", getOwnerUUID());
        tag.putString("OwnerName", getOwnerName());
        tag.putInt("Magazine", getMagazine());
        if (getArtilleryTarget() != null) tag.putLong("ArtilleryTarget", getArtilleryTarget().asLong());
        tag.putInt("HowitzerRounds", getHowitzerRounds());
        tag.putBoolean("WeaponLowered", isWeaponLowered());
        tag.putString("FlightModule", getFlightModule().getId());

        ListTag listtag = new ListTag();
        for (int i = 0; i < this.titanInventory.getContainerSize(); ++i) {
            ItemStack itemstack = this.titanInventory.getItem(i);
            if (!itemstack.isEmpty()) {
                CompoundTag slotTag = new CompoundTag();
                slotTag.putByte("Slot", (byte) i);
                itemstack.save(slotTag);
                listtag.add(slotTag);
            }
        }
        tag.put("TitanInventory", listtag);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        if (tag.contains("CamoIndex")) setCamoIndex(tag.getInt("CamoIndex"));
        if (tag.contains("StandbyMode")) setStandbyMode(tag.getBoolean("StandbyMode"));
        if (tag.contains("IsSitting")) setSitting(tag.getBoolean("IsSitting"));
        if (tag.contains("OwnerUUID")) this.entityData.set(DATA_OWNER_UUID, tag.getString("OwnerUUID"));
        if (tag.contains("OwnerName")) this.entityData.set(DATA_OWNER_NAME, tag.getString("OwnerName"));
        if (tag.contains("WeaponLowered")) this.entityData.set(DATA_WEAPON_LOWERED, tag.getBoolean("WeaponLowered"));
        if (tag.contains("FlightModule")) {
            TitanFlightModule mod = TitanFlightModule.byId(tag.getString("FlightModule"));
            setFlightModule(mod);
            if (mod != TitanFlightModule.NONE && this.titanInventory.getItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT).isEmpty()) {
                this.titanInventory.setItem(com.titancombat.gui.TitanMenu.FLIGHT_SLOT, new ItemStack(com.titancombat.item.ModItems.FLIGHT_MODULES.get(mod).get()));
            }
        }

        if (tag.contains("TitanInventory", 9)) {
            ListTag listtag = tag.getList("TitanInventory", 10);
            for (int i = 0; i < listtag.size(); ++i) {
                CompoundTag slotTag = listtag.getCompound(i);
                int j = slotTag.getByte("Slot") & 255;
                if (j < this.titanInventory.getContainerSize()) {
                    this.titanInventory.setItem(j, ItemStack.of(slotTag));
                }
            }
        }
        TitanWeapon weapon = installedWeapon();
        this.entityData.set(DATA_WEAPON, weapon == null ? -1 : weapon.ordinal());
        this.entityData.set(DATA_MAGAZINE, weapon == null ? 0 : Math.min(tag.getInt("Magazine"), weapon.getMagazineSize()));
        this.entityData.set(DATA_HOWITZER_ROUNDS, Math.min(tag.getInt("HowitzerRounds"), Howitzer.ROUNDS_PER_RACK));
        if (tag.contains("ArtilleryTarget")) {
            this.entityData.set(DATA_ARTILLERY_TARGET, java.util.Optional.of(BlockPos.of(tag.getLong("ArtilleryTarget"))));
        }
    }
}
