package com.titancombat.entity;

import com.titancombat.gui.TitanMenu;
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
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.FluidTags;
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
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.List;

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
    public static final EntityDataAccessor<Boolean> DATA_IS_SITTING =
            SynchedEntityData.defineId(BaseTitanEntity.class, EntityDataSerializers.BOOLEAN);

    protected final SimpleContainer titanInventory = new SimpleContainer(TitanMenu.CONTAINER_SIZE);

    protected int firingCooldown = 0;
    protected int fireAnimTimer = 0;
    protected int meleeCooldown = 0;
    protected int meleeAnimTimer = 0;
    private boolean isEmergencyEjecting = false;

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

    public void toggleKneel() {
        boolean nowSitting = !isSitting();
        setSitting(nowSitting);
        if (!this.level().isClientSide) {
            this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_DOOR_CLOSE, SoundSource.PLAYERS, 1.2F, nowSitting ? 0.7F : 1.1F);
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

    @Override
    protected void positionRider(Entity passenger, Entity.MoveFunction moveFunction) {
        if (this.hasPassenger(passenger)) {
            // Position pilot securely inside upper chest cockpit visor directly behind the dashboard
            double cockpitY = isSitting() ? (this.getY() + 3.0D) : (this.getY() + 4.85D);
            float yawRad = this.yBodyRot * ((float) Math.PI / 180.0F);
            double forwardOffset = isSitting() ? 0.60D : 0.20D;
            double offsetX = -Math.sin(yawRad) * forwardOffset;
            double offsetZ = Math.cos(yawRad) * forwardOffset;
            moveFunction.accept(passenger, this.getX() + offsetX, cockpitY, this.getZ() + offsetZ);
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
        this.playSound(ModSounds.TITAN_STEP.get(), 1.6F, 0.9F + this.random.nextFloat() * 0.2F);
    }

    @Override
    public void performDash(float forward, float strafe) {
        if (this.isSitting()) return;
        super.performDash(forward, strafe);
        this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_DASH.get(), SoundSource.PLAYERS, 2.5F, 1.0F);
    }

    @Override
    public void ejectPilot() {
        this.isEmergencyEjecting = true;
        try {
            super.ejectPilot();
            this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_CABIN_EXIT.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
        } finally {
            this.isEmergencyEjecting = false;
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

    @Override
    public void tick() {
        super.tick();
        if (firingCooldown > 0) firingCooldown--;
        if (meleeCooldown > 0) meleeCooldown--;

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

        // Heavy footstep audio cadence while moving under pilot control
        if (this.isVehicle() && this.onGround() && this.getDeltaMovement().horizontalDistanceSqr() > 0.01D) {
            if (this.tickCount % 12 == 0) {
                this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_STEP.get(), SoundSource.PLAYERS, 1.5F, 0.9F + this.random.nextFloat() * 0.2F);
            }
        }

        if (!this.level().isClientSide) {
            // 1. Core Battery Bay Auto-Charge: checks Slot 0 for swappable titan battery
            if (this.tickCount % 20 == 0) {
                ItemStack batteryStack = this.titanInventory.getItem(TitanMenu.BATTERY_SLOT);
                if (!batteryStack.isEmpty() && batteryStack.getItem() instanceof com.titancombat.item.TitanBatteryItem
                        && !batteryStack.is(com.titancombat.item.ModItems.EMPTY_BATTERY.get())) {
                    if (this.getShield() < this.getMaxShield() || this.getCoreCharge() < 100.0F) {
                        this.setShield(this.getMaxShield());
                        this.addCoreCharge(30.0F);
                        this.titanInventory.setItem(TitanMenu.BATTERY_SLOT, new ItemStack(com.titancombat.item.ModItems.EMPTY_BATTERY.get(), batteryStack.getCount()));
                        this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_GET_BATTERY.get(), SoundSource.PLAYERS, 1.5F, 1.0F);
                        if (this.getFirstPassenger() instanceof Player p) {
                            p.sendSystemMessage(Component.translatable("message.titancombat.battery_recharged", getTitanClass().getDisplayName()));
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
        if (this.isSitting()) return false;
        if (meleeCooldown > 0) return false;
        meleeCooldown = (getTitanClass() == TitanClass.RONIN) ? 12 : 16;

        if (!this.level().isClientSide) {
            this.entityData.set(DATA_IS_MELEEING, true);
            this.meleeAnimTimer = 12;

            if (getTitanClass() == TitanClass.RONIN) {
                this.level().playSound(null, this.blockPosition(), ModSounds.RONIN_SWORD.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
            } else {
                this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_MELEE.get(), SoundSource.PLAYERS, 2.0F, 0.9F);
            }

            Vec3 look = pilot.getLookAngle();
            Vec3 strikePos = this.position().add(0, 2.0D, 0).add(look.scale(3.0D));
            AABB strikeBox = new AABB(strikePos.x - 2.8D, strikePos.y - 2.0D, strikePos.z - 2.8D,
                    strikePos.x + 2.8D, strikePos.y + 2.0D, strikePos.z + 2.8D);

            List<LivingEntity> targets = this.level().getEntitiesOfClass(LivingEntity.class, strikeBox,
                    e -> e != this && e != pilot && !this.isAlliedTo(e) && e.isAlive());

            boolean hit = false;
            float dmg = (float) (getTitanClass() == TitanClass.RONIN ? (isOverdriveActive() ? 90.0F : 60.0F) :
                    (getTitanClass() == TitanClass.SCORCH ? 45.0F : 38.0F));

            for (LivingEntity target : targets) {
                target.hurt(this.damageSources().mobAttack(this), dmg);
                target.knockback(1.5D, -look.x, -look.z);
                if (getTitanClass() == TitanClass.SCORCH) {
                    target.setSecondsOnFire(6);
                }
                hit = true;
            }

            if (hit) {
                if (getTitanClass() == TitanClass.RONIN) {
                    this.level().playSound(null, this.blockPosition(), ModSounds.RONIN_SWORD_IMPACT.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                } else {
                    this.level().playSound(null, this.blockPosition(), ModSounds.TITAN_MELEE_IMPACT.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                }
                addCoreCharge(4.0F);
            }
        }
        return true;
    }

    public boolean firePrimaryWeapon(Player pilot) {
        if (this.isSitting()) return false;
        if (firingCooldown > 0) return false;

        boolean isOverdrive = isOverdriveActive();

        // 1. Check Titan's internal Munitions Bay first!
        boolean hasAmmo = pilot.getAbilities().instabuild || isOverdrive;
        ItemStack ammoStack = ItemStack.EMPTY;

        if (!hasAmmo) {
            for (int i = 0; i < this.titanInventory.getContainerSize(); i++) {
                ItemStack s = this.titanInventory.getItem(i);
                if (s.getItem() instanceof com.titancombat.item.TitanAmmoItem) {
                    hasAmmo = true;
                    ammoStack = s;
                    break;
                }
            }
        }

        // 2. Fallback to Pilot's personal inventory
        if (!hasAmmo) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack s = pilot.getInventory().getItem(i);
                if (s.getItem() instanceof com.titancombat.item.TitanAmmoItem) {
                    hasAmmo = true;
                    ammoStack = s;
                    break;
                }
            }
        }

        if (!hasAmmo) {
            if (!this.level().isClientSide) {
                pilot.sendSystemMessage(Component.translatable("message.titancombat.no_ammo"));
                this.level().playSound(null, this.blockPosition(), SoundEvents.DISPENSER_FAIL, SoundSource.PLAYERS, 1.0F, 1.6F);
            }
            return false;
        }

        TitanClass c = getTitanClass();
        executeWeaponShot(pilot, c);

        if (isOverdrive) {
            firingCooldown = Math.max(1, (int) (firingCooldown * 0.4F));
        } else {
            if (!this.level().isClientSide) {
                addCoreCharge(2.5F);
            }
        }

        if (!pilot.getAbilities().instabuild && !isOverdrive && !ammoStack.isEmpty()) {
            ammoStack.shrink(1);
        }

        if (!this.level().isClientSide) {
            this.entityData.set(DATA_IS_FIRING, true);
            this.fireAnimTimer = 8;
        }
        return true;
    }

    protected void executeWeaponShot(Player pilot, TitanClass c) {
        Vec3 look = pilot.getLookAngle();
        Vec3 spawnPos = this.position().add(0, 2.5D, 0).add(look.scale(1.5D));

        switch (c) {
            case SCORCH -> {
                firingCooldown = 18;
                if (!this.level().isClientSide) {
                    TitanEnergyBlastEntity blast = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                    blast.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                    blast.shoot(look.x, look.y, look.z, 2.0F, 0.5F);
                    blast.setSecondsOnFire(10);
                    this.level().addFreshEntity(blast);
                    this.level().playSound(null, this.blockPosition(), ModSounds.SCORCH_FIRE.get(), SoundSource.PLAYERS, 2.2F, 1.0F);
                }
            }
            case RONIN -> {
                firingCooldown = 10;
                if (!this.level().isClientSide) {
                    for (int i = 0; i < 4; i++) {
                        TitanEnergyBlastEntity pellet = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                        pellet.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                        pellet.shoot(look.x, look.y, look.z, 2.5F, 5.0F);
                        this.level().addFreshEntity(pellet);
                    }
                    this.level().playSound(null, this.blockPosition(), ModSounds.RONIN_FIRE.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                }
            }
            case LEGION -> {
                firingCooldown = 3;
                if (!this.level().isClientSide) {
                    TitanEnergyBlastEntity bullet = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                    bullet.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                    bullet.shoot(look.x, look.y, look.z, 3.2F, 1.5F);
                    this.level().addFreshEntity(bullet);
                    this.level().playSound(null, this.blockPosition(), ModSounds.LEGION_FIRE.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                }
            }
            case NORTHSTAR -> {
                firingCooldown = 25;
                if (!this.level().isClientSide) {
                    TitanEnergyBlastEntity sniper = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                    sniper.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                    sniper.shoot(look.x, look.y, look.z, 4.5F, 0.0F);
                    this.level().addFreshEntity(sniper);
                    this.level().playSound(null, this.blockPosition(), ModSounds.NORTHSTAR_FIRE.get(), SoundSource.PLAYERS, 2.5F, 1.0F);
                }
            }
            case MONARCH -> {
                firingCooldown = 5;
                if (!this.level().isClientSide) {
                    TitanEnergyBlastEntity blast = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                    blast.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                    blast.shoot(look.x, look.y, look.z, 2.8F, 0.8F);
                    this.level().addFreshEntity(blast);
                    this.setShield(this.getShield() + 2.0F);
                    this.level().playSound(null, this.blockPosition(), ModSounds.MONARCH_FIRE.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                }
            }
            case TONE -> {
                firingCooldown = 7;
                if (!this.level().isClientSide) {
                    TitanEnergyBlastEntity cannon = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                    cannon.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                    cannon.shoot(look.x, look.y, look.z, 3.0F, 0.2F);
                    this.level().addFreshEntity(cannon);
                    this.level().playSound(null, this.blockPosition(), ModSounds.TONE_FIRE.get(), SoundSource.PLAYERS, 2.2F, 1.0F);
                }
            }
            default -> { // ION
                firingCooldown = 8;
                if (!this.level().isClientSide) {
                    TitanEnergyBlastEntity blast = new TitanEnergyBlastEntity(ModEntities.ENERGY_BLAST.get(), pilot, this.level());
                    blast.setPos(spawnPos.x, spawnPos.y, spawnPos.z);
                    blast.shoot(look.x, look.y, look.z, 2.8F, 0.4F);
                    this.level().addFreshEntity(blast);
                    this.level().playSound(null, this.blockPosition(), ModSounds.ION_FIRE.get(), SoundSource.PLAYERS, 2.0F, 1.0F);
                }
            }
        }
    }

    @Override
    public InteractionResult mobInteract(Player player, InteractionHand hand) {
        ItemStack held = player.getItemInHand(hand);

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

        // 4. Open Maintenance Cargo Bay Screen (Shift-Click with Empty Hand from outside)
        if (held.isEmpty() && player.isShiftKeyDown() && !this.isVehicle()) {
            if (!this.level().isClientSide) {
                openCustomInventoryScreen(player);
                this.level().playSound(null, this.blockPosition(), SoundEvents.IRON_DOOR_OPEN, SoundSource.PLAYERS, 1.0F, 0.9F);
            }
            return InteractionResult.sidedSuccess(this.level().isClientSide);
        }

        // 5. Board Cockpit with BIOMETRIC PILOT LICENSE LOCK
        if (held.isEmpty() && !this.isVehicle() && !player.isPassenger()) {
            if (!this.level().isClientSide) {
                String owner = getOwnerUUID();
                if (!owner.isEmpty() && !player.getUUID().toString().equals(owner)) {
                    player.sendSystemMessage(Component.translatable("message.titancombat.access_denied", getOwnerName()));
                    this.level().playSound(null, this.blockPosition(), SoundEvents.SHIELD_BLOCK, SoundSource.PLAYERS, 1.5F, 0.6F);
                    return InteractionResult.FAIL;
                }

                if (owner.isEmpty()) {
                    setOwner(player);
                    player.sendSystemMessage(Component.translatable("message.titancombat.neural_link_claimed", player.getName().getString(), getTitanClass().getDisplayName()));
                }

                setStandbyMode(false);
                player.startRiding(this);
                setMechState(MechState.PILOTED);

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
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "legs", 4, this::legsPredicate));
        controllers.add(new AnimationController<>(this, "arms", 4, this::armsPredicate));
    }

    protected PlayState legsPredicate(AnimationState<? extends BaseTitanEntity> event) {
        MechState state = getMechState();
        String prefix = "animation." + getTitanClass().getId() + "_titan.";

        if (state == MechState.DROPPING) {
            return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "loading"));
        }

        if (state == MechState.LANDED || isSitting()) {
            return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "loaded"));
        }

        if (event.isMoving()) {
            if (this.hasImpulse || getDeltaMovement().horizontalDistance() > 0.4D) {
                return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "spurt.leg"));
            }
            return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "walk.leg"));
        }

        return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "idle.leg"));
    }

    protected PlayState armsPredicate(AnimationState<? extends BaseTitanEntity> event) {
        String prefix = "animation." + getTitanClass().getId() + "_titan.";

        if (isSitting()) {
            return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "loaded"));
        }

        if (this.entityData.get(DATA_IS_MELEEING)) {
            return event.setAndContinue(RawAnimation.begin().thenPlay(prefix + "melee"));
        }

        if (this.entityData.get(DATA_IS_FIRING)) {
            return event.setAndContinue(RawAnimation.begin().thenPlay(prefix + "fire"));
        }

        if (event.isMoving()) {
            return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "move.arm"));
        }

        if (getTitanClass() == TitanClass.RONIN) {
            return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "idle_sword.arm"));
        }

        return event.setAndContinue(RawAnimation.begin().thenLoop(prefix + "idle.arm"));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
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
    }
}
