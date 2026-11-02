package com.titancombat.client.gui;

import com.titancombat.TitanCombatMod;
import com.titancombat.client.KeyInputHandler;
import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechFaction;
import com.titancombat.entity.TitanClass;
import com.titancombat.entity.TitanWeapon;
import com.titancombat.item.TitanAmmoItem;
import com.titancombat.item.TitanMagazineItem;
import net.minecraft.network.chat.Component;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.List;
import java.util.Locale;

/**
 * Client-side, tick-rate (20 Hz) state for the titan cockpit HUD.
 * <p>
 * Everything that is expensive or allocates (world scans, ray picks, string building) happens here,
 * at most once per tick, so that {@link MechCockpitHudOverlay} can render every frame without
 * allocating. Also hides the vanilla crosshair / hotbar while piloting.
 */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, value = Dist.CLIENT)
public final class CockpitHudState {

    private CockpitHudState() {}

    // ------------------------------------------------------------------ timing
    /** Monotonic client tick counter (also advances while paused, so animations never freeze mid-way). */
    static int clientTicks;

    static final int BOOT_TICKS = 60;      // ~3 s cinematic boot
    static final int HINT_END = 175;       // control legend fades out ~6 s after boarding (after boot)

    // ------------------------------------------------------------------ boarding / boot
    static int boardedVehicleId = Integer.MIN_VALUE;
    static int boardTick = -100000;
    static boolean bootCinematic;
    static boolean wasSitting;
    static int sitChangeTick = -100000;

    static String className = "AEGIS";
    static String roleName = "STRIKER FRAME";
    static String weaponName = "PLASMA BLASTER";
    static String bootChassisLine = "CHASSIS ONLINE";
    static String bootPilotLine = "PILOT: ---";
    static String factionName = "";
    static int reticleIndex = 7;
    static TitanClass titanClass;
    /** Chassis the active weapon ships with (drives the reticle). Null for non-titan mechs. */
    static TitanClass weaponChassis;
    static TitanWeapon activeWeapon;

    // control legend (built once on boarding, key names can be rebound)
    static final String[] HINT_KEYS = new String[11];
    static final String[] HINT_LABELS = {"FIRE", "JUMP JETS", "DASH", "RELOAD", "HOLSTER", "MELEE", "DEFENSE MATRIX",
            "CORE", "KNEEL / PARK", "COCKPIT BAY", "EJECT"};
    static String ejectKey = "X";
    static String coreKey = "V";
    static String kneelKey = "Z";
    static String ejectPrompt = "[X] EJECT";
    static String coreReadyText = "CORE READY  [V]";
    static String parkedText = "PARKED  -  [SHIFT] DISEMBARK  -  [Z] STAND";

    // ------------------------------------------------------------------ damage tracking
    static float lastHealth = -1;
    static float lastShield = -1;
    static float trailHealth;
    static int trailHoldUntil;
    static int damageTick = -100000;
    static int shieldHitTick = -100000;
    static int shieldBreakTick = -100000;

    // ------------------------------------------------------------------ weapon
    static boolean lastFiring;
    static int fireTick = -100000;
    static int hitMarkerTick = -100000;
    static int reserveMags;
    static boolean ammoInfinite;
    static int magazine;
    static int magSize = 1;
    static int reloadTicksLeft;
    static boolean weaponLowered;
    static boolean weaponRaised;
    static int raiseStartTick = -100000;
    static String ammoText = "0";
    static String magSizeText = "/0";
    static String reserveText = "";
    static String reloadPrompt = "RELOAD [R]";
    static String reloadingText = "RELOADING";
    static String holsteredText = "WEAPON STOWED [H]";
    static String raisingText = "READYING";
    private static int lastAmmoShown = Integer.MIN_VALUE;
    private static int lastReserveShown = Integer.MIN_VALUE;
    private static int lastMagSizeShown = Integer.MIN_VALUE;
    static boolean lastCoreReady;
    static int coreReadyTick = -100000;
    static String overdriveText = "";
    static int lastOverdriveTicks = -1;

    // ------------------------------------------------------------------ target / range
    static boolean targetHostile;
    static int targetId = Integer.MIN_VALUE;
    static int lockTick = -100000;
    static String targetLabel = "";
    static String rangeText = "---";
    private static int lastRangeShown = Integer.MIN_VALUE;
    private static int lastTargetDist = Integer.MIN_VALUE;
    private static final double PICK_RANGE = 128.0D;

    // ------------------------------------------------------------------ radar (4 Hz scan, fixed arrays)
    static final double RADAR_RANGE = 32.0D;
    static final int RADAR_MAX = 64;
    static final float[] RADAR_DX = new float[RADAR_MAX];
    static final float[] RADAR_DZ = new float[RADAR_MAX];
    /** 0 = neutral, 1 = friendly, 2 = hostile, 3 = hostile titan/mech */
    static final byte[] RADAR_TYPE = new byte[RADAR_MAX];
    static int radarCount;
    static int hostileCount;
    static String hostileText = "";
    private static int lastRadarTick = -100;
    private static int lastAmmoTick = -100;

    // ------------------------------------------------------------------ number caches (no per-frame allocation)
    static final String[] NUM = new String[1000];
    static final String[] DEG3 = new String[360];
    static final String[] PCT = new String[101];

    static {
        for (int i = 0; i < NUM.length; i++) NUM[i] = Integer.toString(i);
        for (int i = 0; i < DEG3.length; i++) DEG3[i] = String.format(Locale.ROOT, "%03d", i);
        for (int i = 0; i < PCT.length; i++) PCT[i] = i + "%";
        for (int i = 0; i < HINT_KEYS.length; i++) HINT_KEYS[i] = "?";
    }

    static String num(int n) {
        return (n >= 0 && n < NUM.length) ? NUM[n] : Integer.toString(n);
    }

    // =================================================================== tick
    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        clientTicks++;

        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || mc.level == null || !(player.getVehicle() instanceof BaseMechEntity mech)) {
            boardedVehicleId = Integer.MIN_VALUE;
            return;
        }

        if (mech.getId() != boardedVehicleId) {
            onBoard(mc, player, mech);
        }

        updateDamage(mech);
        updateWeapon(player, mech);
        updateTarget(mc, player, mech);

        if (clientTicks - lastRadarTick >= 5) {
            lastRadarTick = clientTicks;
            scanRadar(mc, player, mech);
        }

        boolean sitting = mech instanceof BaseTitanEntity t && t.isSitting();
        if (sitting != wasSitting) {
            wasSitting = sitting;
            sitChangeTick = clientTicks;
        }
    }

    private static void onBoard(Minecraft mc, Player player, BaseMechEntity mech) {
        boardedVehicleId = mech.getId();
        boardTick = clientTicks;
        bootCinematic = mc.options.getCameraType() == CameraType.FIRST_PERSON;
        wasSitting = mech instanceof BaseTitanEntity t && t.isSitting();
        sitChangeTick = -100000;

        titanClass = mech instanceof BaseTitanEntity titan ? titan.getTitanClass() : null;
        if (titanClass != null) {
            className = titanClass.getDisplayName().toUpperCase(Locale.ROOT);
            roleName = titanClass.getRole().toUpperCase(Locale.ROOT);
        } else {
            className = "AEGIS";
            roleName = "STRIKER FRAME";
            weaponName = "PLASMA BLASTER";
            reticleIndex = 7;
        }
        activeWeapon = null;
        weaponChassis = null;
        bootChassisLine = className + " CHASSIS ONLINE";
        String pilot = (mech instanceof BaseTitanEntity titan && !titan.getOwnerName().isEmpty())
                ? titan.getOwnerName() : player.getName().getString();
        bootPilotLine = "PILOT: " + pilot.toUpperCase(Locale.ROOT);
        factionName = MechFaction.byId(mech.getFactionId()).getDisplayName().toUpperCase(Locale.ROOT);

        String jumpKey = keyName(mc.options.keyJump.getTranslatedKeyMessage().getString());
        String reloadKey = keyName(KeyInputHandler.KEY_RELOAD.getTranslatedKeyMessage().getString());
        String holsterKey = keyName(KeyInputHandler.KEY_HOLSTER.getTranslatedKeyMessage().getString());
        HINT_KEYS[0] = "LMB";
        HINT_KEYS[1] = jumpKey;
        HINT_KEYS[2] = jumpKey + "+DIR";
        HINT_KEYS[3] = reloadKey;
        HINT_KEYS[4] = holsterKey;
        HINT_KEYS[5] = keyName(KeyInputHandler.KEY_MELEE.getTranslatedKeyMessage().getString());
        HINT_KEYS[6] = keyName(KeyInputHandler.KEY_DEFENSE.getTranslatedKeyMessage().getString());
        HINT_KEYS[7] = keyName(KeyInputHandler.KEY_CORE.getTranslatedKeyMessage().getString());
        HINT_KEYS[8] = keyName(KeyInputHandler.KEY_KNEEL.getTranslatedKeyMessage().getString());
        HINT_KEYS[9] = keyName(mc.options.keyInventory.getTranslatedKeyMessage().getString());
        HINT_KEYS[10] = keyName(KeyInputHandler.KEY_EJECT.getTranslatedKeyMessage().getString());
        coreKey = HINT_KEYS[7];
        kneelKey = HINT_KEYS[8];
        ejectKey = HINT_KEYS[10];
        reloadPrompt = "RELOAD [" + reloadKey + "]";
        reloadingText = Component.translatable("hud.titancombat.reloading").getString().toUpperCase(Locale.ROOT);
        holsteredText = Component.translatable("hud.titancombat.holstered").getString().toUpperCase(Locale.ROOT)
                + " [" + holsterKey + "]";
        raisingText = Component.translatable("hud.titancombat.raising").getString().toUpperCase(Locale.ROOT);
        String shiftKey = keyName(mc.options.keyShift.getTranslatedKeyMessage().getString());
        ejectPrompt = "[" + ejectKey + "]  EJECT";
        coreReadyText = "CORE READY  [" + coreKey + "]";
        parkedText = "PARKED  -  [" + shiftKey + "] DISEMBARK  -  [" + kneelKey + "] STAND";

        lastHealth = mech.getHealth();
        trailHealth = lastHealth;
        lastShield = mech.getShield();
        damageTick = shieldHitTick = shieldBreakTick = -100000;
        lastFiring = false;
        fireTick = hitMarkerTick = -100000;
        lastCoreReady = mech.getCoreCharge() >= 100.0F;
        coreReadyTick = -100000;
        lastAmmoTick = -100;
        lastAmmoShown = lastReserveShown = lastMagSizeShown = Integer.MIN_VALUE;
        weaponRaised = false;
        raiseStartTick = -100000;
        magazine = mech instanceof BaseTitanEntity titan ? titan.getMagazine() : 0;
        lastRadarTick = -100;
        lastOverdriveTicks = -1;
        targetId = Integer.MIN_VALUE;
        targetHostile = false;
    }

    private static String keyName(String s) {
        String k = s.toUpperCase(Locale.ROOT);
        if (k.startsWith("LEFT ")) k = "L-" + k.substring(5);
        else if (k.startsWith("RIGHT ")) k = "R-" + k.substring(6);
        return k;
    }

    private static void updateDamage(BaseMechEntity mech) {
        float h = mech.getHealth();
        float s = mech.getShield();
        if (lastHealth >= 0 && h < lastHealth - 0.01F) {
            damageTick = clientTicks;
            trailHealth = Math.max(trailHealth, lastHealth);
            trailHoldUntil = clientTicks + 12;
        }
        if (lastShield >= 0 && s < lastShield - 0.01F) {
            shieldHitTick = clientTicks;
            if (s <= 0.01F) shieldBreakTick = clientTicks;
        }
        if (clientTicks > trailHoldUntil && trailHealth > h) {
            trailHealth = Math.max(h, trailHealth - Math.max(0.5F, mech.getMaxHealth() * 0.015F));
        }
        if (trailHealth < h) trailHealth = h;
        lastHealth = h;
        lastShield = s;

        boolean coreReady = mech.getCoreCharge() >= 100.0F;
        if (coreReady && !lastCoreReady) coreReadyTick = clientTicks;
        lastCoreReady = coreReady;

        int od = mech.getOverdriveTicks();
        if (od != lastOverdriveTicks) {
            lastOverdriveTicks = od;
            overdriveText = od > 0 ? String.format(Locale.ROOT, "CORE ACTIVE  %04.1f", od / 20.0F) : "";
        }
    }

    /** Shown in the weapon block while no weapon module is installed. */
    static String noWeaponText = "NO WEAPON - INSTALL IN BAY [E]";

    private static void updateWeapon(Player player, BaseMechEntity mech) {
        ammoInfinite = mech.isOverdriveActive();
        if (!(mech instanceof BaseTitanEntity titan)) {
            // legacy mech without a weapon system
            magazine = magSize = 1;
            reloadTicksLeft = 0;
            weaponLowered = false;
            weaponRaised = false;
            if (lastAmmoShown != -2) {
                lastAmmoShown = -2;
                ammoText = "\u221E";
                magSizeText = "";
                reserveText = "";
            }
            return;
        }

        TitanWeapon weapon = titan.getActiveWeapon();
        if (weapon == null) {
            // Unarmed chassis: no ammo readout, prompt to fit a weapon module in the bay.
            if (activeWeapon != null || weaponName == null || !weaponName.equals(noWeaponText)) {
                activeWeapon = null;
                weaponChassis = titan.getTitanClass();
                reticleIndex = weaponChassis.ordinal() % 16;
                weaponName = noWeaponText;
                lastAmmoShown = -3;
                ammoText = "--";
                magSizeText = "";
                reserveText = "";
                lastMagSizeShown = -1;
                lastReserveShown = -1;
            }
            magazine = 0;
            magSize = 1;
            reloadTicksLeft = 0;
            weaponLowered = false;
            weaponRaised = false;
            return;
        }
        if (weapon != activeWeapon) {
            activeWeapon = weapon;
            weaponChassis = weapon.getFactoryChassis();
            reticleIndex = weaponChassis.ordinal() % 16;
            weaponName = Component.translatable(weapon.getTranslationKey()).getString().toUpperCase(Locale.ROOT);
            lastAmmoTick = -100;
        }

        int mag = titan.getMagazine();
        if (mag < magazine) {
            // a round left the barrel
            fireTick = clientTicks;
            if (targetHostile) hitMarkerTick = clientTicks;
        }
        magazine = mag;
        magSize = Math.max(1, weapon.getMagazineSize());
        reloadTicksLeft = titan.getReloadTicks();
        weaponLowered = titan.isWeaponLowered();

        boolean raised = titan.isFiringWeapon();
        if (raised && !weaponRaised) raiseStartTick = clientTicks;
        weaponRaised = raised;
        lastFiring = raised && clientTicks - fireTick < 6;

        if (clientTicks - lastAmmoTick >= 10) {
            lastAmmoTick = clientTicks;
            int count = 0;
            for (int i = 0; i < titan.getTitanInventory().getContainerSize(); i++) {
                count += magazinesIn(titan.getTitanInventory().getItem(i), weapon);
            }
            for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
                count += magazinesIn(player.getInventory().getItem(i), weapon);
            }
            reserveMags = count;
        }

        int shown = ammoInfinite ? -1 : magazine;
        if (shown != lastAmmoShown) {
            lastAmmoShown = shown;
            ammoText = ammoInfinite ? "\u221E" : num(magazine);
        }
        if (magSize != lastMagSizeShown) {
            lastMagSizeShown = magSize;
            magSizeText = "/" + magSize;
        }
        if (reserveMags != lastReserveShown) {
            lastReserveShown = reserveMags;
            reserveText = "x" + reserveMags + (reserveMags == 1 ? " MAG" : " MAGS");
        }
    }

    /** Magazines in a stack usable by the given weapon (dedicated magazines + legacy generic ammo). */
    static int magazinesIn(ItemStack stack, TitanWeapon weapon) {
        if (stack.isEmpty()) return 0;
        if (stack.getItem() instanceof TitanMagazineItem m) return m.getWeapon() == weapon ? stack.getCount() : 0;
        if (stack.getItem() instanceof TitanAmmoItem) return stack.getCount();
        return 0;
    }

    private static void updateTarget(Minecraft mc, Player player, BaseMechEntity mech) {
        Vec3 eye = player.getEyePosition();
        Vec3 look = player.getViewVector(1.0F);
        Vec3 end = eye.add(look.x * PICK_RANGE, look.y * PICK_RANGE, look.z * PICK_RANGE);
        BlockHitResult block = mc.level.clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        double maxDist = block.getType() != HitResult.Type.MISS ? block.getLocation().distanceTo(eye) : PICK_RANGE;

        Entity target = mc.crosshairPickEntity;
        if (target == mech || target == player) target = null;
        double dist = target != null ? target.distanceTo(player) : maxDist;
        if (target == null) {
            Vec3 end2 = eye.add(look.x * maxDist, look.y * maxDist, look.z * maxDist);
            AABB box = player.getBoundingBox().expandTowards(look.scale(maxDist)).inflate(1.0D);
            EntityHitResult hit = ProjectileUtil.getEntityHitResult(player, eye, end2, box,
                    e -> e != mech && e != player && !e.isSpectator() && e.isPickable() && e.isAlive()
                            && !mech.hasPassenger(e), maxDist * maxDist);
            if (hit != null) {
                target = hit.getEntity();
                dist = hit.getLocation().distanceTo(eye);
            }
        }

        int range = (int) Math.round(Math.min(dist, 999));
        if (range != lastRangeShown) {
            lastRangeShown = range;
            rangeText = (block.getType() == HitResult.Type.MISS && target == null) ? "---m" : num(range) + "m";
        }

        boolean hostile = target instanceof LivingEntity living && classify(mech, player, living) >= 2;
        if (hostile) {
            int d = (int) dist;
            if (target.getId() != targetId || !targetHostile || d != lastTargetDist) {
                if (target.getId() != targetId || !targetHostile) lockTick = clientTicks;
                lastTargetDist = d;
                targetLabel = target.getName().getString().toUpperCase(Locale.ROOT) + "  " + num(d) + "m";
            }
            targetId = target.getId();
        } else {
            targetId = Integer.MIN_VALUE;
        }
        targetHostile = hostile;
    }

    /** 0 neutral, 1 friendly, 2 hostile, 3 hostile mech */
    static int classify(BaseMechEntity mech, Player pilot, LivingEntity e) {
        if (e instanceof BaseMechEntity other) return mech.isAlliedTo(other) ? 1 : 3;
        if (e instanceof Enemy) return 2;
        if (e instanceof Player p) {
            if (p.getTeam() != null && pilot.getTeam() != null && !pilot.isAlliedTo(p)) return 2;
            return 1;
        }
        return 0;
    }

    private static void scanRadar(Minecraft mc, Player player, BaseMechEntity mech) {
        radarCount = 0;
        int hostiles = 0;
        AABB scanBox = mech.getBoundingBox().inflate(RADAR_RANGE, 12.0D, RADAR_RANGE);
        List<LivingEntity> entities = mc.level.getEntitiesOfClass(LivingEntity.class, scanBox,
                e -> e != mech && e != player && e.isAlive() && !mech.hasPassenger(e));
        for (int i = 0; i < entities.size() && radarCount < RADAR_MAX; i++) {
            LivingEntity e = entities.get(i);
            int type = classify(mech, player, e);
            RADAR_DX[radarCount] = (float) (e.getX() - mech.getX());
            RADAR_DZ[radarCount] = (float) (e.getZ() - mech.getZ());
            RADAR_TYPE[radarCount] = (byte) type;
            radarCount++;
            if (type >= 2) hostiles++;
        }
        if (hostiles != hostileCount || hostileText.isEmpty()) {
            hostileCount = hostiles;
            hostileText = hostiles > 0 ? num(hostiles) + " HOSTILE" : "CLEAR";
        }
    }

    // =================================================================== vanilla overlay filtering
    @SubscribeEvent(priority = EventPriority.LOW)
    public static void onRenderOverlayPre(RenderGuiOverlayEvent.Pre event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || !(mc.player.getVehicle() instanceof BaseMechEntity)) return;
        var id = event.getOverlay().id();
        // Our cockpit reticle replaces the vanilla crosshair in every camera mode.
        if (id.equals(VanillaGuiOverlay.CROSSHAIR.id())) {
            event.setCanceled(true);
            return;
        }
        // In first person the pilot looks through the canopy: no hotbar / xp clutter.
        if (mc.options.getCameraType() == CameraType.FIRST_PERSON
                && (id.equals(VanillaGuiOverlay.HOTBAR.id())
                || id.equals(VanillaGuiOverlay.EXPERIENCE_BAR.id())
                || id.equals(VanillaGuiOverlay.ITEM_NAME.id()))) {
            event.setCanceled(true);
        }
    }
}
