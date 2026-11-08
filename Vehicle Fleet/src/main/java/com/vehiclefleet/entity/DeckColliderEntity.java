package com.vehiclefleet.entity;

import com.vehiclefleet.VehicleFleetMod;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityDimensions;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.ArrayList;
import java.util.List;

/**
 * Invisible solid slab that follows a vehicle so external entities (Immersive Aircraft,
 * SBW turrets, TACZ turrets, cannons, and mobs) can stand, land, and sail along with it.
 */
public class DeckColliderEntity extends Entity {
    private static final EntityDataAccessor<Integer> PARENT = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Float> SIZE = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> HEIGHT = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> LX = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> LY = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Float> LZ = SynchedEntityData.defineId(DeckColliderEntity.class, EntityDataSerializers.FLOAT);

    private double px, py, pz;
    private float pyaw;
    private boolean seen = false;

    public DeckColliderEntity(EntityType<?> type, Level level) {
        super(type, level);
        this.noPhysics = true;
    }

    public static DeckColliderEntity create(EntityType<DeckColliderEntity> type, Entity parent, float size, float height, float lx, float ly, float lz) {
        DeckColliderEntity e = new DeckColliderEntity(type, parent.level());
        e.entityData.set(PARENT, parent.getId());
        e.entityData.set(SIZE, size);
        e.entityData.set(HEIGHT, height);
        e.entityData.set(LX, lx);
        e.entityData.set(LY, ly);
        e.entityData.set(LZ, lz);
        e.followParent(parent);
        e.refreshDimensions();
        return e;
    }

    public static List<DeckColliderEntity> spawnRow(Entity parent, float size, float height, float x, float yBottom, double z0, double z1) {
        EntityType<DeckColliderEntity> type = VehicleFleetMod.DECK_COLLIDER.get();
        double span = Math.abs(z1 - z0);
        int tiles = Math.max(1, (int) Math.ceil(span / size));
        double step = tiles > 1 ? (z1 - z0 - Math.signum(z1 - z0) * size) / (tiles - 1) : 0.0D;
        List<DeckColliderEntity> list = new ArrayList<>(tiles);
        for (int i = 0; i < tiles; i++) {
            float z = tiles > 1 ? (float) (z0 + Math.signum(z1 - z0) * size / 2.0D + i * step) : (float) ((z0 + z1) / 2.0D);
            DeckColliderEntity collider = create(type, parent, size, height, x, yBottom, z);
            parent.level().addFreshEntity(collider);
            list.add(collider);
        }
        return list;
    }

    @Override
    protected void defineSynchedData() {
        this.entityData.define(PARENT, -1);
        this.entityData.define(SIZE, 1.0F);
        this.entityData.define(HEIGHT, 1.0F);
        this.entityData.define(LX, 0.0F);
        this.entityData.define(LY, 0.0F);
        this.entityData.define(LZ, 0.0F);
    }

    @Override
    public void onSyncedDataUpdated(EntityDataAccessor<?> key) {
        super.onSyncedDataUpdated(key);
        if (SIZE.equals(key) || HEIGHT.equals(key)) this.refreshDimensions();
    }

    @Override
    public EntityDimensions getDimensions(Pose pose) {
        return EntityDimensions.fixed(this.entityData.get(SIZE), this.entityData.get(HEIGHT));
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }

    public Entity getParent() {
        return this.level().getEntity(this.entityData.get(PARENT));
    }

    private Vec3 localToWorld(Entity parent, double x, double y, double z) {
        float yawRad = parent.getYRot() * Mth.DEG_TO_RAD;
        double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
        return new Vec3(parent.getX() + x * cos - z * sin, parent.getY() + y, parent.getZ() + x * sin + z * cos);
    }

    private void followParent(Entity parent) {
        Vec3 p = localToWorld(parent, this.entityData.get(LX), this.entityData.get(LY), this.entityData.get(LZ));
        this.setPos(p.x, p.y, p.z);
        this.xo = p.x; this.yo = p.y; this.zo = p.z;
    }

    @Override
    public void tick() {
        Entity parent = getParent();
        if (parent == null || !parent.isAlive()) {
            if (!this.level().isClientSide) this.discard();
            return;
        }
        if (!seen) {
            seen = true;
            px = parent.getX(); py = parent.getY(); pz = parent.getZ(); pyaw = parent.getYRot();
        }
        List<Entity> riders = ridersOnTop(parent);
        followParent(parent);
        carryRiders(parent, riders);
        px = parent.getX(); py = parent.getY(); pz = parent.getZ(); pyaw = parent.getYRot();
    }

    private List<Entity> ridersOnTop(Entity parent) {
        AABB top = this.getBoundingBox();
        AABB zone = new AABB(top.minX - 0.25D, top.maxY - 0.6D, top.minZ - 0.25D, top.maxX + 0.25D, top.maxY + 2.5D, top.maxZ + 0.25D);
        return this.level().getEntities(this, zone, e -> !(e instanceof DeckColliderEntity) && e != parent && !e.isPassenger()
                && e.getY() >= top.maxY - 0.6D && claims(parent, e));
    }

    private boolean claims(Entity parent, Entity e) {
        float yaw = -pyaw * Mth.DEG_TO_RAD;
        double rx = e.getX() - px, rz = e.getZ() - pz;
        double lx = rx * Math.cos(yaw) - rz * Math.sin(yaw), lz = rx * Math.sin(yaw) + rz * Math.cos(yaw);
        double mine = localDistSqr(lx, lz);
        List<DeckColliderEntity> colliders = (!this.level().isClientSide && parent instanceof FleetVehicleEntity fve && !fve.getDeckColliders().isEmpty())
                ? fve.getDeckColliders()
                : this.level().getEntitiesOfClass(DeckColliderEntity.class, e.getBoundingBox().inflate(6.0D));
        for (DeckColliderEntity t : colliders) {
            if (t != this && t.getParent() == parent && Math.abs(t.top() - top()) < 0.01F) {
                double d = t.localDistSqr(lx, lz);
                if (d < mine || (d == mine && t.getId() < this.getId())) return false;
            }
        }
        return true;
    }

    private float top() {
        return this.entityData.get(LY) + this.entityData.get(HEIGHT);
    }

    private double localDistSqr(double lx, double lz) {
        double dx = lx - this.entityData.get(LX), dz = lz - this.entityData.get(LZ);
        return dx * dx + dz * dz;
    }

    /** Anything standing on this tile moves and turns with the parent vehicle. Players on foot are handled by client AboardHandler. */
    private void carryRiders(Entity parent, List<Entity> riders) {
        double dy = parent.getY() - py;
        float dYaw = Mth.wrapDegrees(parent.getYRot() - pyaw);
        double deckTop = this.getBoundingBox().maxY;
        for (Entity e : riders) {
            if (e == null || !e.isAlive() || e == parent || parent.hasPassenger(e)) continue;
            // A player on foot on client side is resolved through AboardHandler
            if (e instanceof Player && this.level().isClientSide && !e.isPassenger()) continue;

            Entity pilot = e instanceof Player ? e : e.getControllingPassenger();
            if (pilot == null && !e.getPassengers().isEmpty()) {
                for (Entity rider : e.getPassengers()) {
                    if (rider instanceof Player) { pilot = rider; break; }
                }
            }
            boolean owner = pilot instanceof Player p ? this.level().isClientSide && p.isLocalPlayer() : !this.level().isClientSide;
            if (!owner) continue;

            double rx = e.getX() - px, rz = e.getZ() - pz;
            float r = dYaw * Mth.DEG_TO_RAD;
            double nx = rx * Math.cos(r) - rz * Math.sin(r), nz = rx * Math.sin(r) + rz * Math.cos(r);
            e.setPos(parent.getX() + nx, Math.max(e.getY() + dy, deckTop), parent.getZ() + nz);
            if (dYaw != 0.0F) {
                e.setYRot(e.getYRot() + dYaw);
                if (e instanceof LivingEntity living) {
                    living.setYHeadRot(living.getYHeadRot() + dYaw);
                    living.setYBodyRot(living.yBodyRot + dYaw);
                }
            }
            e.fallDistance = 0.0F;
            if (!this.level().isClientSide && pilot == null) {
                Vec3 dm = e.getDeltaMovement();
                if (dm.y < 0.0D) e.setDeltaMovement(dm.x * 0.5D, 0.0D, dm.z * 0.5D);
                e.setOnGround(true);
                e.hasImpulse = true;
            }
        }
    }

    @Override
    public boolean canBeCollidedWith() {
        return true;
    }

    @Override
    public boolean isPickable() {
        return !this.isRemoved();
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        Entity parent = getParent();
        return parent != null && parent.hurt(source, amount);
    }

    @Override
    public InteractionResult interact(Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        Entity parent = getParent();
        if (stack.is(VehicleFleetMod.CAMO_SPRAY.get())) {
            return parent instanceof FleetVehicleEntity fve ? fve.interact(player, hand) : InteractionResult.PASS;
        }

        AABB box = this.getBoundingBox();
        Vec3 eye = player.getEyePosition();
        Vec3 look = player.getViewVector(1.0F);
        Vec3 end = eye.add(look.scale(7.0D));

        // A. If player is looking directly at a block (e.g. ContainerBlock on deck), interact with it first
        ClipContext blockClip = new ClipContext(eye, end, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, player);
        BlockHitResult bhr = this.level().clip(blockClip);
        if (bhr.getType() == HitResult.Type.BLOCK) {
            BlockPos bpos = bhr.getBlockPos();
            BlockState bstate = this.level().getBlockState(bpos);
            if (!bstate.isAir()) {
                InteractionResult bres = bstate.use(this.level(), player, hand, bhr);
                if (bres.consumesAction()) {
                    return bres;
                }
            }
        }

        java.util.Optional<Vec3> clip = box.clip(eye, end);
        Vec3 hitVec = clip.orElseGet(() -> new Vec3(player.getX(), box.maxY, player.getZ()));
        Vec3 deployPos = new Vec3(hitVec.x, box.maxY, hitVec.z);

        // B. Crowbar / Wrench interaction on nearby container block
        ResourceLocation heldItemKey = ForgeRegistries.ITEMS.getKey(stack.getItem());
        String heldName = heldItemKey != null ? heldItemKey.getPath() : "";
        boolean isCrowbar = stack.is(ItemTags.create(new ResourceLocation("forge", "tools/crowbar")))
                || heldName.contains("crowbar") || heldName.contains("wrench");
        if (isCrowbar) {
            BlockPos nearPos = BlockPos.containing(hitVec.x, box.maxY + 0.5D, hitVec.z);
            for (BlockPos check : BlockPos.betweenClosed(nearPos.offset(-1, -1, -1), nearPos.offset(1, 1, 1))) {
                BlockState bs = this.level().getBlockState(check);
                if (bs.getBlock().getClass().getSimpleName().contains("ContainerBlock")) {
                    InteractionResult res = bs.use(this.level(), player, hand, new BlockHitResult(hitVec, Direction.UP, check, false));
                    if (res.consumesAction()) return res;
                }
            }
        }

        // 1. Try deploying container, turret, spawn egg, vehicle, or block
        InteractionResult cargoRes = tryDeployCargo(this, player, hand, deployPos);
        if (cargoRes.consumesAction()) return cargoRes;

        // 2. Sneaking: never mount vehicle
        if (player.isSecondaryUseActive() || player.isShiftKeyDown()) {
            return InteractionResult.PASS;
        }

        // 3. Normal click: mount vehicle if parent exists
        return parent != null ? player.interactOn(parent, hand) : InteractionResult.PASS;
    }

    /** Deploys Superb Warfare containers, cargo blocks, TACZ turrets, spawn eggs, and fleet vehicles directly on vehicle decks. */
    public static InteractionResult tryDeployCargo(Entity targetVehicle, Player player, InteractionHand hand, Vec3 hitPos) {
        ItemStack stack = player.getItemInHand(hand);
        if (stack.isEmpty()) return InteractionResult.PASS;

        Level level = targetVehicle.level();
        float yaw = player.getYRot();

        // 1. FIRST PRIORITY: Any BlockItem (including Superb Warfare containers, chests, ammo crates, building blocks)
        // Must be placed as a physical world block on the ship deck so players can interact with it (e.g. use crowbar on container).
        if (stack.getItem() instanceof BlockItem blockItem) {
            int bx = Mth.floor(hitPos.x);
            int bz = Mth.floor(hitPos.z);
            int targetY = Math.max(Mth.floor(hitPos.y + 0.1D), Mth.floor(player.getY()));
            BlockPos placePos = new BlockPos(bx, targetY, bz);
            while ((!level.getBlockState(placePos).canBeReplaced() || level.getFluidState(placePos).isSource()) && placePos.getY() < level.getMaxBuildHeight()) {
                placePos = placePos.above();
            }

            if (!level.isClientSide) {
                Block block = blockItem.getBlock();
                Direction facing = player.getDirection().getOpposite();
                BlockPlaceContext bpc = new BlockPlaceContext(new UseOnContext(player, hand,
                        new BlockHitResult(hitPos, Direction.UP, placePos, false)));
                BlockState state = block.getStateForPlacement(bpc);
                if (state == null) state = block.defaultBlockState();

                if (state.hasProperty(BlockStateProperties.HORIZONTAL_FACING)) {
                    state = state.setValue(BlockStateProperties.HORIZONTAL_FACING, facing);
                } else if (state.hasProperty(BlockStateProperties.FACING)) {
                    state = state.setValue(BlockStateProperties.FACING, facing);
                }

                if (level.setBlock(placePos, state, 3)) {
                    block.setPlacedBy(level, placePos, state, player, stack);
                    BlockEntity be = level.getBlockEntity(placePos);
                    if (be != null) {
                        CompoundTag blockEntityData = BlockItem.getBlockEntityData(stack);
                        if (blockEntityData != null) {
                            be.load(blockEntityData);
                            be.setChanged();
                        }
                    }
                    if (!player.getAbilities().instabuild) stack.shrink(1);
                    SoundType st = state.getSoundType();
                    level.playSound(null, placePos, st.getPlaceSound(), SoundSource.BLOCKS, (st.getVolume() + 1.0F) / 2.0F, st.getPitch() * 0.8F);
                    player.displayClientMessage(Component.literal("§6[Vehicle Fleet] §aPlaced: §b" + stack.getHoverName().getString()), true);
                }
            }
            return InteractionResult.sidedSuccess(level.isClientSide);
        }

        // 2. Non-block item with EntityType in main tag
        String entityId = null;
        CompoundTag entityCustomTag = null;
        CompoundTag mainTag = stack.getTag();
        if (mainTag != null && mainTag.contains("EntityType", Tag.TAG_STRING)) {
            entityId = mainTag.getString("EntityType");
            if (mainTag.contains("Entity", Tag.TAG_COMPOUND)) entityCustomTag = mainTag.getCompound("Entity");
        } else if (mainTag != null && mainTag.contains("Entity", Tag.TAG_COMPOUND)) {
            CompoundTag ent = mainTag.getCompound("Entity");
            if (ent.contains("id", Tag.TAG_STRING)) {
                entityId = ent.getString("id");
                entityCustomTag = ent;
            }
        }

        // 3. TACZ Turret item
        if (entityId == null) {
            ResourceLocation itemKey = ForgeRegistries.ITEMS.getKey(stack.getItem());
            String itemReg = itemKey != null ? itemKey.toString() : "";
            if ("tacz_turrets:turret".equals(itemReg) || stack.getItem().getClass().getSimpleName().contains("TurretItem")) {
                entityId = "tacz_turrets:turret";
            }
        }

        // 4. Minecraft / Forge Spawn Egg
        if (entityId == null && stack.getItem() instanceof SpawnEggItem egg) {
            EntityType<?> eggType = egg.getType(stack.getTag());
            if (eggType != null) {
                ResourceLocation key = ForgeRegistries.ENTITY_TYPES.getKey(eggType);
                if (key != null) entityId = key.toString();
            }
        }

        // 5. FleetVehicleItem (placing another vehicle on deck, e.g. helo or boat)
        if (entityId == null && stack.getItem() instanceof FleetVehicleItem) {
            ResourceLocation itemKey = ForgeRegistries.ITEMS.getKey(stack.getItem());
            if (itemKey != null && "vehiclefleet".equals(itemKey.getNamespace())) {
                entityId = "vehiclefleet:" + itemKey.getPath();
            }
        }

        // Deploy entity if recognized
        if (entityId != null) {
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(entityId));
            if (type == null) {
                type = EntityType.byString(entityId).orElse(null);
            }
            if (type != null) {
                if (!level.isClientSide) {
                    Entity entity = type.create(level);
                    if (entity != null) {
                        if (entityCustomTag != null) {
                            entity.load(entityCustomTag);
                        }
                        entity.moveTo(hitPos.x, hitPos.y + 0.02D, hitPos.z, yaw, 0.0F);
                        level.addFreshEntity(entity);
                        if (!player.getAbilities().instabuild) {
                            stack.shrink(1);
                        }
                        level.playSound(null, hitPos.x, hitPos.y, hitPos.z, SoundEvents.IRON_GOLEM_REPAIR, SoundSource.PLAYERS, 1.0F, 1.0F);
                        level.playSound(null, hitPos.x, hitPos.y, hitPos.z, SoundEvents.CHEST_OPEN, SoundSource.PLAYERS, 1.0F, 1.2F);
                        player.displayClientMessage(Component.literal("§6[Vehicle Fleet] §aDeployed: §b" + entity.getDisplayName().getString()), true);
                    }
                }
                return InteractionResult.sidedSuccess(level.isClientSide);
            }
        }

        return InteractionResult.PASS;
    }

    @Override
    public boolean shouldBeSaved() {
        return false;
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag tag) {}

    @Override
    protected void addAdditionalSaveData(CompoundTag tag) {}
}
