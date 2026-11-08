package com.vehiclefleet.entity;

import com.vehiclefleet.FleetVehicles;
import com.vehiclefleet.VehicleFleetMod;
import com.vehiclefleet.compat.TitanCompat;
import com.vehiclefleet.net.FleetNet;
import com.vehiclefleet.physics.Collisions;
import com.vehiclefleet.physics.VehicleCollisionData;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.DyeItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.LightBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.ForgeRegistries;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.*;

/**
 * Data-driven entity class for Vehicle Fleet.
 * Responsive client-predicted physics (car/truck Ackermann steering, helicopter/aircraft collective/cyclic flight,
 * ship naval buoyancy & rudder steering, submarine dive control), multi-seat riding with realistic cushion seating,
 * dynamic hull tilt, and interior walking.
 */
public class FleetVehicleEntity extends Entity implements GeoEntity {
    private static final EntityDataAccessor<Integer> DATA_VARIANT = SynchedEntityData.defineId(FleetVehicleEntity.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> DATA_OPEN = SynchedEntityData.defineId(FleetVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Boolean> DATA_LIGHTS = SynchedEntityData.defineId(FleetVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> DATA_SPEED = SynchedEntityData.defineId(FleetVehicleEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Boolean> DATA_CARGO = SynchedEntityData.defineId(FleetVehicleEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<String> DATA_SEATS = SynchedEntityData.defineId(FleetVehicleEntity.class, EntityDataSerializers.STRING);
    public static final String[] LIVERY_SUFFIX = {"", "_thai", "_desert", "_arctic", "_blackops", "_un", "_redstar"};
    private static final String[] LIVERY_NAME = {
            "Standard Tactical", "Royal Thai Army", "Desert Expeditionary",
            "Arctic Snow", "Night Ops", "UN Peacekeeper", "Rebel Crimson"
    };
    private static final Map<String, AABB> HULL = new HashMap<>();

    public final FleetVehicles.Spec spec;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private final Map<UUID, Integer> seatMap = new LinkedHashMap<>();
    private String parsedSeats = null;
    private Map<UUID, Integer> clientSeats = new HashMap<>();
    private boolean up, down;
    private double speed, vy, prevSpeed;
    private final Set<Long> lightBlocks = new HashSet<>();
    private boolean collidersSpawned = false;
    private final List<DeckColliderEntity> deckColliders = new ArrayList<>();
    private int lerpSteps;
    private double lerpX, lerpY, lerpZ, lerpYRot, lerpXRot;

    public float yawDelta = 0.0F;
    public float visSpeed, visYawRate, wheelRot, wheelRotO;
    public float steer = 0.0F;

    public FleetVehicleEntity(EntityType<?> type, Level level, FleetVehicles.Spec spec) {
        super(type, level);
        this.spec = spec;
        this.noCulling = true;
        this.blocksBuilding = true;
        this.setMaxUpStep(spec.isGround() ? 1.25F : 0.6F);
    }

    @Override
    protected void defineSynchedData() {
        entityData.define(DATA_VARIANT, 0);
        entityData.define(DATA_OPEN, false);
        entityData.define(DATA_LIGHTS, true);
        entityData.define(DATA_SPEED, 0.0F);
        entityData.define(DATA_CARGO, false);
        entityData.define(DATA_SEATS, "");
    }

    @Override
    protected void readAdditionalSaveData(CompoundTag t) {
        entityData.set(DATA_VARIANT, t.getInt("Variant"));
        entityData.set(DATA_OPEN, t.getBoolean("Open"));
        entityData.set(DATA_LIGHTS, !t.contains("Lights") || t.getBoolean("Lights"));
        lightBlocks.clear();
        for (long l : t.getLongArray("LightBlocks")) lightBlocks.add(l);
    }

    @Override
    protected void addAdditionalSaveData(CompoundTag t) {
        t.putInt("Variant", getVariant());
        t.putBoolean("Open", isOpen());
        t.putBoolean("Lights", entityData.get(DATA_LIGHTS));
        t.putLongArray("LightBlocks", lightBlocks.stream().mapToLong(Long::longValue).toArray());
    }

    @Override
    public Packet<ClientGamePacketListener> getAddEntityPacket() {
        return NetworkHooks.getEntitySpawningPacket(this);
    }

    // ------------------------------------------------------------------ state
    public int getVariant() { return entityData.get(DATA_VARIANT); }

    public boolean isOpen() { return entityData.get(DATA_OPEN); }

    public boolean hasCargo() { return entityData.get(DATA_CARGO); }

    public float getSpeedSynced() { return entityData.get(DATA_SPEED); }

    // ------------------------------------------------------------------ frames (vehicle local: +X left, +Y up, +Z nose)
    public Vec3 toWorld(Vec3 l) {
        double r = Math.toRadians(getYRot()), c = Math.cos(r), s = Math.sin(r);
        return new Vec3(getX() + l.x * c - l.z * s, getY() + l.y, getZ() + l.x * s + l.z * c);
    }

    public Vec3 toLocal(Vec3 w) {
        double r = Math.toRadians(getYRot()), c = Math.cos(r), s = Math.sin(r), dx = w.x - getX(), dz = w.z - getZ();
        return new Vec3(dx * c + dz * s, w.y - getY(), -dx * s + dz * c);
    }

    public Vec3 worldDeltaToLocal(Vec3 d) {
        double r = Math.toRadians(getYRot()), c = Math.cos(r), s = Math.sin(r);
        return new Vec3(d.x * c + d.z * s, d.y, -d.x * s + d.z * c);
    }

    public VehicleCollisionData collision() { return Collisions.get(spec.id); }

    public AABB hull() {
        return HULL.computeIfAbsent(spec.id, id -> {
            double x0 = 1e9, y0 = 1e9, z0 = 1e9, x1 = -1e9, y1 = -1e9, z1 = -1e9;
            for (AABB b : collision().getStaticBoxes()) {
                x0 = Math.min(x0, b.minX); y0 = Math.min(y0, b.minY); z0 = Math.min(z0, b.minZ);
                x1 = Math.max(x1, b.maxX); y1 = Math.max(y1, b.maxY); z1 = Math.max(z1, b.maxZ);
            }
            return x0 > x1 ? new AABB(-1, 0, -1, 1, 2, 1) : new AABB(x0, y0, z0, x1, y1, z1);
        });
    }

    public boolean inHull(Vec3 l) {
        AABB h = hull();
        return l.x >= h.minX - 0.4D && l.x <= h.maxX + 0.4D && l.z >= h.minZ - 0.4D && l.z <= h.maxZ + 0.4D && l.y >= h.minY - 0.4D && l.y <= h.maxY + 2.5D;
    }

    @Override
    public AABB getBoundingBoxForCulling() {
        double r = Math.max(Math.max(Math.abs(spec.length[0]), Math.abs(spec.length[1])), spec.half_width) / 16.0D + 6.0D;
        return getBoundingBox().inflate(r, 6.0D, r);
    }

    // ------------------------------------------------------------------ seats
    private int playerCount() {
        int n = 0;
        for (Entity e : getPassengers()) if (e instanceof Player) n++;
        return n;
    }

    private int cargoCount() {
        int n = 0;
        for (Entity e : getPassengers()) if (!(e instanceof Player)) n++;
        return n;
    }

    private int seatCount() { return Math.max(1, spec.seats.size()); }

    public int seatOf(Entity p) {
        Map<UUID, Integer> m = level().isClientSide ? parseClientSeats() : seatMap;
        Integer i = m.get(p.getUUID());
        if (i != null) return i;
        int idx = 0;
        for (Entity e : getPassengers()) { if (e == p) break; if (e instanceof Player) idx++; }
        return idx;
    }

    private Map<UUID, Integer> parseClientSeats() {
        String s = entityData.get(DATA_SEATS);
        if (!s.equals(parsedSeats)) {
            parsedSeats = s;
            Map<UUID, Integer> m = new HashMap<>();
            for (String part : s.split(";")) {
                String[] kv = part.split("=");
                if (kv.length == 2) {
                    try { m.put(UUID.fromString(kv[0]), Integer.parseInt(kv[1])); } catch (IllegalArgumentException ignored) { }
                }
            }
            clientSeats = m;
        }
        return clientSeats;
    }

    private void syncSeats() {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<UUID, Integer> e : seatMap.entrySet()) sb.append(e.getKey()).append('=').append(e.getValue()).append(';');
        entityData.set(DATA_SEATS, sb.toString());
    }

    private boolean seatTaken(int idx, Entity except) {
        for (Entity e : getPassengers()) if (e != except && e instanceof Player && seatMap.getOrDefault(e.getUUID(), -1) == idx) return true;
        return false;
    }

    @Override
    protected void addPassenger(Entity p) {
        super.addPassenger(p);
        if (!level().isClientSide && p instanceof Player) {
            for (int i = 0; i < seatCount(); i++) if (!seatTaken(i, p)) { seatMap.put(p.getUUID(), i); break; }
            syncSeats();
        }
    }

    @Override
    protected void removePassenger(Entity p) {
        super.removePassenger(p);
        p.fallDistance = 0.0F;
        this.lerpSteps = 0;
        if (!level().isClientSide) { seatMap.remove(p.getUUID()); syncSeats(); }
    }

    @Override
    public Vec3 getDismountLocationForPassenger(LivingEntity p) {
        if (spec.isShip()) {
            return toWorld(new Vec3(0, spec.seats.isEmpty() ? 1.0D : spec.seats.get(0).pos[1] / 16.0D, -1.5D));
        }
        double yawRad = Math.toRadians(getYRot());
        double sideOffset = Math.max(1.2D, spec.half_width / 16.0D + 0.6D);
        double dx = Math.cos(yawRad) * sideOffset;
        double dz = Math.sin(yawRad) * sideOffset;
        return new Vec3(getX() + dx, getY(), getZ() + dz);
    }

    @Override
    protected boolean canAddPassenger(Entity p) {
        if (p instanceof Player) return playerCount() < seatCount();
        return TitanCompat.isCargo(p) && cargoCount() < spec.cargo.size();
    }

    @Override
    public LivingEntity getControllingPassenger() {
        for (Entity e : getPassengers()) if (e instanceof Player p && seatOf(p) == 0) return p;
        return null;
    }

    @Override
    public boolean isControlledByLocalInstance() {
        Entity controller = getControllingPassenger();
        return controller instanceof Player player ? player.isLocalPlayer() : !level().isClientSide;
    }

    @Override
    public double getPassengersRidingOffset() {
        if (!spec.seats.isEmpty()) {
            return spec.seats.get(0).pos[1] / 16.0D - 0.35D;
        }
        return 0.5D;
    }

    public Vec3 transformSeatWithTilt(Vec3 o) {
        float pitch = getHullPitch(), roll = getHullRoll();
        if (pitch != 0.0F || roll != 0.0F) {
            double pivotY = getHullPivotY();
            double h = o.y - pivotY;
            double cp = Math.cos(pitch), sp = Math.sin(pitch);
            double y = h * cp - o.z * sp, z = o.z * cp + h * sp;
            double cr = Math.cos(roll), sr = Math.sin(roll);
            return new Vec3(o.x * cr + y * sr, pivotY + y * cr - o.x * sr, z);
        }
        return o;
    }

    public float getHullPitch() {
        if (spec.isAir()) {
            return Mth.clamp(this.visSpeed * 0.28F, -0.15F, 0.24F);
        }
        if (spec.isShip()) {
            float bowRise = Mth.clamp(this.visSpeed * 0.08F, -0.04F, 0.10F);
            float wavePitch = isInWater() ? (float) Math.cos((tickCount + 0.5F) * 0.06F) * 0.02F : 0.0F;
            return bowRise + wavePitch;
        }
        return Mth.clamp((float) (speed - prevSpeed) * -1.8F, -0.05F, 0.05F);
    }

    public float getHullRoll() {
        if (spec.isAir()) {
            float bankRate = (float) Math.toRadians(this.visYawRate) * (1.2F + this.visSpeed * 2.5F);
            return -Mth.clamp(bankRate, -0.32F, 0.32F);
        }
        if (spec.isShip()) {
            float turnRoll = -Mth.clamp((float) Math.toRadians(this.visYawRate) * this.visSpeed * 4.0F, -0.16F, 0.16F);
            float waveRoll = isInWater() ? (float) Math.sin((tickCount + 0.5F) * 0.08F) * 0.03F : 0.0F;
            return turnRoll + waveRoll;
        }
        float bodyRoll = (float) Math.toRadians(this.visYawRate) * this.visSpeed * 8.0F;
        return Mth.clamp(bodyRoll, -0.14F, 0.14F);
    }

    public double getHullPivotY() {
        return spec.isAir() ? 1.5D : (spec.isShip() ? 1.0D : 0.8D);
    }

    @Override
    protected void positionRider(Entity p, MoveFunction f) {
        if (!hasPassenger(p)) return;
        Vec3 l;
        if (p instanceof Player player) {
            int idx = Math.min(seatOf(player), seatCount() - 1);
            if (spec.seats.isEmpty()) {
                l = new Vec3(0, 0.5D - 0.35D, 0);
            } else {
                FleetVehicles.Seat seat = spec.seats.get(idx);
                l = FleetVehicles.local(seat.pos);
                // Player buttocks rests on seat cushion / bridge console deck
                l = new Vec3(l.x, l.y - 0.35D, l.z);
            }
            l = transformSeatWithTilt(l);
            player.setYRot(getYRot());
            player.yRotO = getYRot();
            player.setYHeadRot(getYRot());
            player.setYBodyRot(getYRot());
        } else {
            int idx = 0;
            for (Entity e : getPassengers()) { if (e == p) break; if (!(e instanceof Player)) idx++; }
            FleetVehicles.Cargo c = spec.cargo.get(Math.min(idx, Math.max(0, spec.cargo.size() - 1)));
            l = FleetVehicles.local(c.pos);
            if (spec.isAir() && c.name.contains("hang")) l = new Vec3(l.x, -p.getBbHeight() - 0.6D, l.z);
            l = transformSeatWithTilt(l);
            p.setYRot(getYRot());
            if (p instanceof LivingEntity le) { le.setYBodyRot(getYRot()); le.setYHeadRot(getYRot()); }
        }
        p.fallDistance = 0.0F;
        Vec3 w = toWorld(l);
        f.accept(p, w.x, w.y, w.z);
    }

    // ------------------------------------------------------------------ interaction
    @Override
    public InteractionResult interact(Player p, InteractionHand hand) {
        ItemStack held = p.getItemInHand(hand);

        // 1. Dedicated Camouflage Spray item: cycles liveries
        if (held.is(VehicleFleetMod.CAMO_SPRAY.get())) {
            if (!level().isClientSide) {
                int next = (getVariant() + 1) % LIVERY_SUFFIX.length;
                entityData.set(DATA_VARIANT, next);
                p.displayClientMessage(Component.literal("§6[Vehicle Fleet] §eCamo applied: §b" + LIVERY_NAME[next] + " §7(" + (next + 1) + "/" + LIVERY_SUFFIX.length + ")"), true);
                level().playSound(null, getX(), getY(), getZ(), SoundEvents.DYE_USE, SoundSource.PLAYERS, 1.0F, 1.2F);
            }
            return InteractionResult.sidedSuccess(level().isClientSide);
        }

        // 2. Minecraft Dyes: paint directly
        if (held.getItem() instanceof DyeItem dye) {
            DyeColor color = dye.getDyeColor();
            int variant = switch (color) {
                case GREEN, LIME -> 1;
                case YELLOW, ORANGE, BROWN -> 2;
                case WHITE, LIGHT_GRAY -> 3;
                case BLACK, GRAY -> 4;
                case LIGHT_BLUE, BLUE, CYAN -> 5;
                case RED, PURPLE, MAGENTA, PINK -> 6;
                default -> 0;
            };
            if (!level().isClientSide) {
                entityData.set(DATA_VARIANT, variant);
                if (!p.getAbilities().instabuild) held.shrink(1);
                p.displayClientMessage(Component.literal("§6[Vehicle Fleet] §aRepainted to: §b" + LIVERY_NAME[variant]), true);
                level().playSound(null, getX(), getY(), getZ(), SoundEvents.DYE_USE, SoundSource.PLAYERS, 1.0F, 1.0F);
            }
            return InteractionResult.sidedSuccess(level().isClientSide);
        }

        // 3. Try deploying cargo (turret, container, spawn egg, block) whether sneaking or standing
        if (!held.isEmpty()) {
            Vec3 eye = p.getEyePosition();
            Vec3 look = p.getViewVector(1.0F);
            Vec3 end = eye.add(look.scale(7.0D));

            // Check if player is aiming directly at a block first (e.g. ContainerBlock on deck)
            ClipContext blockClip = new ClipContext(eye, end, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, p);
            BlockHitResult bhr = level().clip(blockClip);
            if (bhr.getType() == HitResult.Type.BLOCK) {
                BlockPos bpos = bhr.getBlockPos();
                BlockState bstate = level().getBlockState(bpos);
                if (!bstate.isAir()) {
                    InteractionResult bres = bstate.use(level(), p, hand, bhr);
                    if (bres.consumesAction()) {
                        return bres;
                    }
                }
            }

            Vec3 deployPos = null;

            for (DeckColliderEntity dce : deckColliders) {
                if (dce.isAlive()) {
                    AABB box = dce.getBoundingBox();
                    java.util.Optional<Vec3> clip = box.clip(eye, end);
                    if (clip.isPresent()) {
                        deployPos = new Vec3(clip.get().x, box.maxY, clip.get().z);
                        break;
                    }
                }
            }
            if (deployPos == null && p.getY() >= getY() + 0.5D) {
                deployPos = new Vec3(p.getX(), p.getY(), p.getZ());
            }
            if (deployPos == null) {
                AABB box = getBoundingBox();
                java.util.Optional<Vec3> clip = box.clip(eye, end);
                deployPos = clip.orElseGet(() -> new Vec3(getX(), box.maxY, getZ()));
            }

            // Check crowbar / wrench interaction on nearby container block
            ResourceLocation heldKey = ForgeRegistries.ITEMS.getKey(held.getItem());
            String heldPath = heldKey != null ? heldKey.getPath() : "";
            boolean isCrowbar = held.is(ItemTags.create(new ResourceLocation("forge", "tools/crowbar")))
                    || heldPath.contains("crowbar") || heldPath.contains("wrench");
            if (isCrowbar && deployPos != null) {
                BlockPos nearPos = BlockPos.containing(deployPos.x, deployPos.y + 0.5D, deployPos.z);
                for (BlockPos check : BlockPos.betweenClosed(nearPos.offset(-1, -1, -1), nearPos.offset(1, 1, 1))) {
                    BlockState bs = level().getBlockState(check);
                    if (bs.getBlock().getClass().getSimpleName().contains("ContainerBlock")) {
                        InteractionResult res = bs.use(level(), p, hand, new BlockHitResult(deployPos, Direction.UP, check, false));
                        if (res.consumesAction()) return res;
                    }
                }
            }

            InteractionResult cargoRes = DeckColliderEntity.tryDeployCargo(this, p, hand, deployPos);
            if (cargoRes.consumesAction()) return cargoRes;
        }

        // 4. Sneaking (Shift + Right Click): Never hijack click; allow placing turrets/blocks/items
        if (p.isSecondaryUseActive() || p.isShiftKeyDown()) {
            return InteractionResult.PASS;
        }

        // 5. Normal mount
        if (!level().isClientSide) {
            if (canAddPassenger(p)) p.startRiding(this);
            else p.displayClientMessage(Component.translatable("message.vehiclefleet.no_seat"), true);
        }
        return InteractionResult.sidedSuccess(level().isClientSide);
    }

    private static boolean isPlaceableOrItemUse(ItemStack stack) {
        if (stack.isEmpty()) return false;
        net.minecraft.world.item.Item item = stack.getItem();
        if (item instanceof net.minecraft.world.item.BlockItem || item instanceof net.minecraft.world.item.SpawnEggItem) return true;
        String name = item.getClass().getName().toLowerCase();
        return name.contains("turret") || name.contains("place") || name.contains("weapon");
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
        this.resetFallDistance();
        for (Entity p : getPassengers()) {
            p.fallDistance = 0.0F;
        }
    }

    @Override
    public boolean hurt(DamageSource src, float amount) {
        if (!level().isClientSide && !isRemoved() && src.getEntity() instanceof Player pl && (pl.isCreative() || pl.isShiftKeyDown())) {
            if (!pl.isCreative()) spawnAtLocation(new ItemStack(VehicleFleetMod.VEHICLE_ITEMS.get(spec.id).get()));
            discard();
        }
        return false;
    }

    @Override
    public boolean isPickable() { return !isRemoved(); }

    @Override
    public boolean canBeCollidedWith() { return false; }

    public void setInput(Player p, byte flags) {
        if (p == getControllingPassenger()) { up = (flags & 1) != 0; down = (flags & 2) != 0; }
    }

    public static void handleAction(ServerPlayer p, int id) {
        FleetVehicleEntity v = p.getVehicle() instanceof FleetVehicleEntity f ? f : null;
        if (v == null) {
            for (FleetVehicleEntity f : p.level().getEntitiesOfClass(FleetVehicleEntity.class, p.getBoundingBox().inflate(200.0D))) {
                if (f.inHull(f.toLocal(p.position()))) { v = f; break; }
            }
        }
        if (v == null) return;
        switch (id) {
            case FleetNet.ACT_SEAT -> v.switchSeat(p);
            case FleetNet.ACT_OPEN -> {
                if (Math.abs(v.speed) < 0.05D && (!v.spec.isAir() || v.onGround() || v.spec.clips.open != null && v.getControllingPassenger() == null)) v.entityData.set(DATA_OPEN, !v.isOpen());
            }
            case FleetNet.ACT_LIGHTS -> {
                boolean on = !v.entityData.get(DATA_LIGHTS);
                v.entityData.set(DATA_LIGHTS, on);
                p.displayClientMessage(Component.translatable(on ? "message.vehiclefleet.lights_on" : "message.vehiclefleet.lights_off"), true);
            }
            case FleetNet.ACT_RELEASE -> v.releaseCargo();
            case FleetNet.ACT_HORN -> v.honkHorn(p);
            default -> { }
        }
    }

    private void honkHorn(ServerPlayer p) {
        net.minecraft.sounds.SoundEvent sound = spec.isShip() ? com.vehiclefleet.sound.FleetSounds.HORN_SHIP.get() : com.vehiclefleet.sound.FleetSounds.HORN_TRUCK.get();
        level().playSound(null, getX(), getY(), getZ(), sound, SoundSource.PLAYERS, 2.5F, 1.0F);
    }

    private void switchSeat(ServerPlayer p) {
        if (p.getVehicle() != this) {
            if (canAddPassenger(p)) p.startRiding(this);
            else p.displayClientMessage(Component.translatable("message.vehiclefleet.no_seat"), true);
            return;
        }
        int n = seatCount(), cur = seatOf(p);
        for (int i = 1; i < n; i++) {
            int idx = (cur + i) % n;
            if (!seatTaken(idx, p)) {
                seatMap.put(p.getUUID(), idx);
                syncSeats();
                p.displayClientMessage(Component.translatable("message.vehiclefleet.seat", idx + 1, n), true);
                return;
            }
        }
        p.displayClientMessage(Component.translatable("message.vehiclefleet.no_seat"), true);
    }

    private void releaseCargo() {
        for (Entity e : new ArrayList<>(getPassengers())) {
            if (e instanceof Player) continue;
            e.stopRiding();
            Vec3 w = toWorld(new Vec3(spec.half_width / 16.0D + 3.0D, 0, 0));
            e.setPos(w.x, spec.isAir() ? e.getY() : getY(), w.z);
        }
    }

    // ------------------------------------------------------------------ tick
    @Override
    public void lerpTo(double x, double y, double z, float yRot, float xRot, int steps, boolean teleport) {
        if (isControlledByLocalInstance()) {
            lerpSteps = 0;
            return;
        }
        lerpX = x; lerpY = y; lerpZ = z; lerpYRot = yRot; lerpXRot = xRot; lerpSteps = steps;
    }

    @Override
    public void tick() {
        this.yawDelta = 0.0F;
        super.tick();

        if (isControlledByLocalInstance()) {
            this.lerpSteps = 0;
            this.syncPacketPositionCodec(this.getX(), this.getY(), this.getZ());
            LivingEntity driver = getControllingPassenger();
            if (driver == null) { up = false; down = false; }
            float f = driver != null ? driver.zza : 0.0F;
            float s = driver != null ? driver.xxa : 0.0F;
            if ("c17_airlifter".equals(spec.id)) movePlane(driver, f, s);
            else if (spec.isAir()) moveAir(driver, f, s);
            else if (spec.isShip()) moveShip(driver, f, s);
            else moveGround(driver, f, s);

            if (Math.abs(this.yawDelta) > 0.001F) {
                for (Entity passenger : getPassengers()) {
                    if (passenger instanceof Player pl) {
                        pl.setYRot(pl.getYRot() + this.yawDelta);
                        pl.yRotO += this.yawDelta;
                    }
                }
            }

            this.visSpeed = approach(this.visSpeed, (float) this.speed, 0.25F);
            this.visYawRate = approach(this.visYawRate, this.yawDelta, 0.25F);
            this.wheelRotO = this.wheelRot;
            this.wheelRot += (float) (this.speed / 0.875F);
        } else {
            if (lerpSteps > 0) {
                setPos(getX() + (lerpX - getX()) / lerpSteps, getY() + (lerpY - getY()) / lerpSteps, getZ() + (lerpZ - getZ()) / lerpSteps);
                setYRot((float) (getYRot() + Mth.wrapDegrees(lerpYRot - getYRot()) / lerpSteps));
                setXRot((float) (getXRot() + (lerpXRot - getXRot()) / lerpSteps));
                lerpSteps--;
            }
            setDeltaMovement(Vec3.ZERO);

            if (level().isClientSide) {
                double yawRad = Math.toRadians(getYRot());
                float forward = (float) ((getX() - xo) * -Math.sin(yawRad) + (getZ() - zo) * Math.cos(yawRad));
                this.visSpeed += (forward - this.visSpeed) * 0.3F;
                this.visYawRate += (Mth.wrapDegrees(getYRot() - yRotO) - this.visYawRate) * 0.3F;
                this.wheelRotO = this.wheelRot;
                this.wheelRot += forward / 0.875F;
            }
        }

        this.prevSpeed = this.speed;

        for (Entity passenger : getPassengers()) {
            passenger.fallDistance = 0.0F;
        }
        if (level().isClientSide) {
            net.minecraftforge.fml.DistExecutor.unsafeRunWhenOn(net.minecraftforge.api.distmarker.Dist.CLIENT, () -> () -> com.vehiclefleet.client.FleetEngineSound.ensure(this));
        }

        if (!level().isClientSide) {
            if (!collidersSpawned) {
                collidersSpawned = true;
                spawnDeckColliders();
            }
            float spd = (float) speed;
            if (Math.abs(spd - entityData.get(DATA_SPEED)) > 0.004F) entityData.set(DATA_SPEED, spd);
            if (tickCount % 2 == 0) tickAboard();
            tickLights();
            tickDock();
        }
    }

    private void updateThrottle(float input, float maxForward, float maxReverse, float accel, float brake, float drag) {
        if (input != 0.0F && Math.abs(speed) > 0.02F && Math.signum(input) != Math.signum(speed)) {
            speed = approach((float) speed, 0.0F, brake);
        } else if (input > 0.0F) {
            speed = approach((float) speed, maxForward, accel);
        } else if (input < 0.0F) {
            speed = approach((float) speed, -maxReverse, accel);
        } else {
            speed = approach((float) speed, 0.0F, drag);
        }
    }

    private static float approach(float val, float target, float step) {
        return val < target ? Math.min(val + step, target) : Math.max(val - step, target);
    }

    private void moveGround(LivingEntity driver, float f, float s) {
        float maxFwd = (float) spec.speed;
        float maxRev = maxFwd * 0.35F;
        float accel, brake, drag, wheelbase, steerRate;
        if (spec.id.contains("technical")) {
            accel = 0.028F; brake = 0.065F; drag = 0.010F; wheelbase = 3.2F; steerRate = 0.22F;
        } else if (spec.id.contains("humvee")) {
            accel = 0.022F; brake = 0.052F; drag = 0.012F; wheelbase = 3.6F; steerRate = 0.18F;
        } else {
            accel = 0.012F; brake = 0.038F; drag = 0.006F; wheelbase = 5.8F; steerRate = 0.10F;
        }
        updateThrottle(f, maxFwd, maxRev, accel, brake, drag);

        float maxSteerRad = (float) Math.toRadians(34.0D);
        this.steer = approach(this.steer, s, steerRate);
        float steerRad = this.steer * maxSteerRad;
        this.yawDelta = -(float) Math.toDegrees(speed * Math.tan(steerRad) / wheelbase);

        setYRot(getYRot() + this.yawDelta);
        double yawRad = Math.toRadians(getYRot());
        Vec3 old = getDeltaMovement();
        double vx = Mth.lerp(0.95F, old.x, -Math.sin(yawRad) * speed);
        double vz = Mth.lerp(0.95F, old.z, Math.cos(yawRad) * speed);
        vy = onGround() ? -0.04D : Math.max(-1.5D, (vy - 0.08D) * 0.98D);
        setDeltaMovement(vx, vy, vz);
        move(MoverType.SELF, getDeltaMovement());

        if (horizontalCollision) {
            if (onGround() && Math.abs(speed) > 0.01D) {
                Vec3 fwd = Vec3.directionFromRotation(0.0F, getYRot());
                Vec3 h = new Vec3(fwd.x * 0.35D * Math.signum(speed), 1.05D, fwd.z * 0.35D * Math.signum(speed));
                if (level().noCollision(this, getBoundingBox().move(h.x, h.y, h.z))) move(MoverType.SELF, h);
            }
            speed *= 0.5D;
        }

        if (level().isClientSide && onGround() && Math.abs(speed) > 0.18D) {
            double backX = getX() - Math.sin(yawRad) * 2.5D;
            double backZ = getZ() + Math.cos(yawRad) * 2.5D;
            level().addParticle(ParticleTypes.CAMPFIRE_COSY_SMOKE,
                    backX + (random.nextDouble() - 0.5D) * 1.5D, getY() + 0.1D,
                    backZ + (random.nextDouble() - 0.5D) * 1.5D, 0, 0.06D, 0);
        }
    }

    private Double waterTop() {
        BlockPos bp = BlockPos.containing(getX(), getY(), getZ());
        for (int dy = 3; dy >= -4; dy--) {
            BlockPos p = bp.above(dy);
            if (level().getFluidState(p).is(FluidTags.WATER)) return (double) p.getY() + level().getFluidState(p).getHeight(level(), p);
        }
        return null;
    }

    private void moveShip(LivingEntity driver, float f, float s) {
        boolean inWater = isInWater();
        if (!inWater && onGround()) {
            speed = approach((float) speed, 0.0F, 0.05F);
            vy = onGround() ? -0.04D : Math.max(-1.5D, (vy - 0.08D) * 0.98D);
            double yawRad = Math.toRadians(getYRot());
            setDeltaMovement(-Math.sin(yawRad) * speed, vy, Math.cos(yawRad) * speed);
            move(MoverType.SELF, getDeltaMovement());
            return;
        }

        float maxFwd = (float) spec.speed;
        float accel, brake, drag, steerRate;
        if ("fac_patrol".equals(spec.id)) {
            accel = 0.016F; brake = 0.035F; drag = 0.005F; steerRate = 2.4F;
        } else if ("opv_cutter".equals(spec.id) || "corvette_stealth".equals(spec.id)) {
            accel = 0.007F; brake = 0.018F; drag = 0.003F; steerRate = 1.2F;
        } else {
            accel = 0.0028F; brake = 0.008F; drag = 0.0015F; steerRate = 0.45F;
        }
        updateThrottle(f, maxFwd, maxFwd * 0.35F, accel, brake, drag);

        float steerMult = Math.abs(speed) < 0.04F ? 0.4F : Math.signum((float) speed);
        this.yawDelta = Math.abs(s) > 0.01F ? -s * steerMult * steerRate : 0.0F;
        setYRot(getYRot() + this.yawDelta);

        Double top = waterTop();
        double vertMotion;
        if (top != null) {
            double targetY = top - spec.draft / 16.0D;
            vertMotion = Mth.clamp((targetY - getY()) * 0.2D, -0.15D, 0.15D);
        } else {
            vertMotion = onGround() ? -0.04D : Math.max(-1.5D, (vy - 0.08D) * 0.98D);
        }

        if ("transport_sub".equals(spec.id)) {
            if (up) vertMotion = 0.18D;
            else if (down) vertMotion = -0.18D;
        }

        double yawRad = Math.toRadians(getYRot());
        setDeltaMovement(-Math.sin(yawRad) * speed, vertMotion, Math.cos(yawRad) * speed);
        move(MoverType.SELF, getDeltaMovement());

        if (horizontalCollision) speed *= 0.4D;

        if (level().isClientSide && Math.abs(speed) > 0.06D && inWater) {
            double sx = getX() + Math.sin(yawRad) * 4.0D;
            double sz = getZ() - Math.cos(yawRad) * 4.0D;
            level().addParticle(ParticleTypes.SPLASH,
                    sx + (random.nextDouble() - 0.5D) * 2.0D, getY() + 0.3D,
                    sz + (random.nextDouble() - 0.5D) * 2.0D,
                    -Math.sin(yawRad) * 0.2D, 0.15D, Math.cos(yawRad) * 0.2D);
        }
    }

    private void moveAir(LivingEntity driver, float f, float s) {
        float turnRate, accelRate;
        if ("uh60_blackhawk".equals(spec.id)) {
            turnRate = 2.6F; accelRate = 0.045F;
        } else if ("mi17_hip".equals(spec.id)) {
            turnRate = 2.0F; accelRate = 0.035F;
        } else {
            turnRate = 1.1F; accelRate = 0.018F;
        }

        if (Math.abs(s) > 0.01F) {
            this.yawDelta = -s * turnRate;
        } else {
            this.yawDelta = 0.0F;
        }
        setYRot(getYRot() + this.yawDelta);

        double vertSpeed = 0.0D;
        if (up) {
            vertSpeed = "mi26_halo".equals(spec.id) ? 0.28D : 0.38D;
        } else if (down) {
            vertSpeed = -0.32D;
        } else if (!onGround()) {
            vertSpeed = 0.01D;
        }

        if (driver == null && !onGround()) {
            vertSpeed = Math.max(-0.25D, getDeltaMovement().y - 0.04D);
        }

        float targetSpeed = f * (float) spec.speed;
        speed = approach((float) speed, targetSpeed, accelRate);

        double yawRad = Math.toRadians(getYRot());
        double fwdX = -Math.sin(yawRad) * speed;
        double fwdZ = Math.cos(yawRad) * speed;

        setDeltaMovement(fwdX, vertSpeed, fwdZ);
        move(MoverType.SELF, getDeltaMovement());
        resetFallDistance();

        if (horizontalCollision) speed *= 0.5D;

        if (level().isClientSide && !onGround() && driver != null && tickCount % 2 == 0) {
            double px = getX() + (random.nextDouble() - 0.5D) * 4.0D;
            double pz = getZ() + (random.nextDouble() - 0.5D) * 4.0D;
            level().addParticle(ParticleTypes.CLOUD, px, getY() - 0.6D, pz, 0, -0.4D, 0);
        }
    }

    private void movePlane(LivingEntity driver, float f, float s) {
        boolean ground = onGround();
        float maxSpeed = (float) spec.speed;
        float stallSpeed = maxSpeed * 0.40F;
        updateThrottle(f, maxSpeed, ground ? 0.12F : 0.0F, ground ? 0.012F : 0.010F, 0.03F, ground ? 0.01F : 0.002F);
        if (!ground) speed = Math.max(speed, stallSpeed * 0.6F);

        float flying = (float) Math.min(1.0D, Math.abs(speed) / stallSpeed);
        this.yawDelta = -s * (ground ? 1.2F * (float) Math.min(1.0D, Math.abs(speed) * 4.0D) : 1.5F);
        setYRot(getYRot() + this.yawDelta);

        boolean climb = up;
        boolean dive = down;
        double vert;
        if (speed >= stallSpeed) {
            vert = climb ? 0.28D * flying : (dive ? -0.4D : 0.0D);
            if (ground && !climb) vert = onGround() ? -0.04D : Math.max(-1.5D, (vy - 0.08D) * 0.98D);
        } else if (ground) {
            vert = onGround() ? -0.04D : Math.max(-1.5D, (vy - 0.08D) * 0.98D);
        } else {
            vert = Math.max(-0.9D, getDeltaMovement().y - 0.05D);
            if (driver instanceof Player p && tickCount % 30 == 0) {
                p.displayClientMessage(Component.literal("§c[STALL] Airspeed low - throttle up!"), true);
            }
        }

        double yawRad = Math.toRadians(getYRot());
        Vec3 old = getDeltaMovement();
        double grip = ground ? 0.95D : 0.65D;
        double vx = Mth.lerp(grip, old.x, -Math.sin(yawRad) * speed);
        double vz = Mth.lerp(grip, old.z, Math.cos(yawRad) * speed);
        setDeltaMovement(vx, vert, vz);
        move(MoverType.SELF, getDeltaMovement());
        resetFallDistance();
    }

    /** Server side of walking inside: no fall damage, submarines keep their air. Real movement is client side. */
    private void tickAboard() {
        double r = Math.max(Math.max(Math.abs(spec.length[0]), Math.abs(spec.length[1])), spec.half_width) / 16.0D + 6.0D;
        for (Player p : level().getEntitiesOfClass(Player.class, new AABB(getX() - r, getY() - 6, getZ() - r, getX() + r, getY() + 14, getZ() + r))) {
            if (p.isPassenger()) continue;
            Vec3 l = toLocal(p.position());
            if (!inHull(l)) continue;
            Double top = collision().standY(l.x, l.z, l.y);
            if (top != null && l.y - top < 0.7D) {
                p.fallDistance = 0.0F;
                if (spec.id.equals("transport_sub")) p.setAirSupply(p.getMaxAirSupply());
            }
        }
    }

    // ------------------------------------------------------------------ lights: vanilla light blocks hung under every lamp
    private boolean playerNear(double r) {
        return level().getNearestPlayer(this, r) != null;
    }

    private void tickLights() {
        if (tickCount % 5 != 0) return;
        Set<Long> target = new HashSet<>();
        if (entityData.get(DATA_LIGHTS) && playerNear(64.0D)) {
            for (Vec3 lamp : Collisions.lights(spec.id)) target.add(BlockPos.containing(toWorld(lamp.add(0, -1.0D, 0))).asLong());
        }
        for (Iterator<Long> it = lightBlocks.iterator(); it.hasNext(); ) {
            long l = it.next();
            if (!target.contains(l)) { removeLight(BlockPos.of(l)); it.remove(); }
        }
        for (long t : target) {
            if (lightBlocks.contains(t)) continue;
            BlockPos bp = BlockPos.of(t);
            if (!level().isLoaded(bp)) continue;
            BlockState st = level().getBlockState(bp);
            boolean water = st.is(Blocks.WATER) && st.getFluidState().isSource();
            if (st.isAir() || water) {
                level().setBlock(bp, Blocks.LIGHT.defaultBlockState().setValue(LightBlock.LEVEL, 13).setValue(LightBlock.WATERLOGGED, water), 3);
                lightBlocks.add(t);
            }
        }
    }

    private void removeLight(BlockPos bp) {
        if (!level().isLoaded(bp)) return;
        BlockState cur = level().getBlockState(bp);
        if (cur.is(Blocks.LIGHT)) level().setBlock(bp, cur.getFluidState().createLegacyBlock(), 3);
    }

    @Override
    public void remove(RemovalReason reason) {
        if (!level().isClientSide) {
            for (long l : lightBlocks) removeLight(BlockPos.of(l));
            lightBlocks.clear();
            for (DeckColliderEntity c : deckColliders) {
                if (c.isAlive()) c.discard();
            }
            deckColliders.clear();
        }
        super.remove(reason);
    }

    public List<DeckColliderEntity> getDeckColliders() {
        return deckColliders;
    }

    private void spawnDeckColliders() {
        switch (spec.id) {
            case "lpd_assault" -> {
                // Aft flight deck: Y=7.75, width=6.8, Z=[-13.25..-1.25]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 6.8F, 1.5F, 0.0F, 6.25F, -13.25D, -1.25D));
                // Forward well deck/cargo: Y=3.31, width=5.0, Z=[5.62..15.62]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 5.0F, 1.5F, 0.0F, 1.81F, 5.62D, 15.62D));
            }
            case "coaster_freighter" -> {
                // Main cargo deck and hatch: Y=2.75, width=7.0, Z=[-10.75..7.25]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 7.0F, 1.5F, 0.0F, 1.25F, -10.75D, 7.25D));
            }
            case "corvette_stealth" -> {
                // Aft helipad: Y=2.75, width=4.8, Z=[-16.0..-9.5]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 4.8F, 1.5F, 0.0F, 1.25F, -16.0D, -9.5D));
                // Mid deck: Y=2.75, width=4.8, Z=[-8.5..1.25]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 4.8F, 1.5F, 0.0F, 1.25F, -8.5D, 1.25D));
            }
            case "opv_cutter" -> {
                // Aft helipad: Y=2.75, width=4.5, Z=[-12.75..-5.5]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 4.5F, 1.5F, 0.0F, 1.25F, -12.75D, -5.5D));
                // Forward deck: Y=2.75, width=4.5, Z=[-5.5..1.88]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 4.5F, 1.5F, 0.0F, 1.25F, -5.5D, 1.88D));
            }
            case "fac_patrol" -> {
                // Deck: Y=2.75, width=3.6, Z=[-7.0..1.25]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 3.6F, 1.5F, 0.0F, 1.25F, -7.0D, 1.25D));
            }
            case "c17_airlifter" -> {
                // Main cargo bay floor: Y=2.5, width=4.5, Z=[-16.88..11.88]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 4.5F, 1.0F, 0.0F, 1.5F, -16.88D, 11.88D));
                // Aft cargo ramp: Y=2.5, width=3.5, Z=[-21.25..-16.88]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 3.5F, 1.0F, 0.0F, 1.5F, -21.25D, -16.88D));
            }
            case "ural_6x6", "recovery_6x6" -> {
                // Rear flatbed: Y=2.0, width=2.4, Z=[-4.38..0.5]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 2.4F, 1.0F, 0.0F, 1.0F, -4.38D, 0.5D));
            }
            case "technical_4x4" -> {
                // Pickup cargo bed: Y=1.5, width=1.8, Z=[-3.5..-0.25]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 1.8F, 0.8F, 0.0F, 0.7F, -3.5D, -0.25D));
            }
            case "humvee_m1165" -> {
                // Roof mount / rear cargo: Y=2.65, width=2.1, Z=[-1.0..1.38]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 2.1F, 0.8F, 0.0F, 1.85F, -1.0D, 1.38D));
            }
            case "transport_sub" -> {
                // Deck: Y=2.96, width=3.8, Z=[-12.0..12.0]
                deckColliders.addAll(DeckColliderEntity.spawnRow(this, 3.8F, 1.5F, 0.0F, 1.46F, -12.0D, 12.0D));
            }
            default -> {}
        }
    }

    // ------------------------------------------------------------------ optional mech cargo (Titan Combat / Obsolete)
    private void tickDock() {
        if (tickCount % 10 != 0 || spec.cargo.isEmpty() || !TitanCompat.present()) {
            entityData.set(DATA_CARGO, cargoCount() > 0);
            return;
        }
        int have = cargoCount();
        entityData.set(DATA_CARGO, have > 0);
        if (have >= spec.cargo.size()) return;
        FleetVehicles.Cargo slot = spec.cargo.get(have);
        Vec3 w = toWorld(FleetVehicles.local(slot.pos));
        for (Entity e : level().getEntitiesOfClass(Entity.class, new AABB(w, w).inflate(2.5D, spec.isAir() ? 8.0D : 2.5D, 2.5D))) {
            if (e == this || e.isPassenger() || e instanceof Player || !TitanCompat.isCargo(e)) continue;
            e.startRiding(this, true);
            break;
        }
    }

    // ------------------------------------------------------------------ animation
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 4, st -> {
            String c = pickClip();
            if (c == null) return PlayState.STOP;
            return st.setAndContinue(RawAnimation.begin().thenLoop("animation." + spec.id + "." + c));
        }));
        if (spec.clips.beacon != null) {
            controllers.add(new AnimationController<>(this, "beacon", 0, st -> st.setAndContinue(RawAnimation.begin().thenLoop("animation." + spec.id + "." + spec.clips.beacon))));
        }
    }

    private String pickClip() {
        FleetVehicles.Clips c = spec.clips;
        boolean driven = getControllingPassenger() != null;
        if (isOpen() && c.open != null) return c.open;
        if (spec.isAir() && hasCargo() && driven && c.sling != null) return c.sling;
        boolean moving = Math.abs(visSpeed) > 0.02F || Math.abs(speed) > 0.02F || (spec.isAir() && driven);
        if (moving && c.move != null) return c.move;
        if (c.radar != null) return c.radar;
        return c.idle;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
