package com.obsolete.registry;

import com.obsolete.client.model.ExoframeArmIK;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.item.ExoframeAmmoItem;
import com.obsolete.item.ModItems;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

import java.util.*;

/**
 * Central data-driven registry mapping Exoframe armor, modules, and weapons to:
 * - Model bones to show / hide
 * - First-person pilot occlusion rules
 * - Faction metadata
 * - Cockpit HUD & sensor profiles
 * - Weapon hold definitions for IK posing
 */
public final class ExoframeVariantRegistry {

    public record SensorProfile(
            String camName,
            String camSub,
            int camColor,
            int borderColor
    ) {}

    public record ArmorVariantData(
            Item item,
            ExoframeArmorSlot slot,
            String faction,
            List<String> visibleBones,
            List<String> firstPersonHiddenBones,
            boolean hidesFrameHead,
            SensorProfile sensorProfile
    ) {}

    public record WeaponVariantData(
            Item item,
            String weaponBoneName,
            ExoframeArmIK.Hold hold,
            boolean isMelee,
            boolean isShield
    ) {}

    private static final Map<Item, ArmorVariantData> ARMOR_VARIANTS = new IdentityHashMap<>();
    private static final Map<Item, WeaponVariantData> WEAPON_VARIANTS = new IdentityHashMap<>();
    private static final Map<Item, SensorProfile> SENSOR_PROFILES = new IdentityHashMap<>();
    private static final Set<String> ALL_KNOWN_ARMOR_BONES = new LinkedHashSet<>();
    private static final Set<String> ALL_KNOWN_WEAPON_BONES = new LinkedHashSet<>();

    private static boolean initialized = false;

    public static synchronized void ensureInitialized() {
        if (initialized) return;
        initialized = true;

        // ==================== 1. HEAD ARMOR VARIANTS ====================
        registerArmor(ModItems.ARMOR_SAND_HEAD.get(), ExoframeArmorSlot.HEAD, "Sand",
                List.of("armor_head"), List.of("armor_head"), false,
                new SensorProfile("PMC SLOPED PERISCOPE", "REINFORCED COWL PASS-THROUGH", 0xFFFFCC00, 0xFFFFCC00));

        registerArmor(ModItems.ARMOR_USMC_HEAD.get(), ExoframeArmorSlot.HEAD, "USMC",
                List.of("armor_head_usmc"), List.of("armor_head_usmc"), false,
                new SensorProfile("USMC CANOPY RECON", "MIL-SPEC 4K HDR OPTIC", 0xFF00AAFF, 0xFF00AAFF));

        registerArmor(ModItems.ARMOR_CERBERUS_HEAD.get(), ExoframeArmorSlot.HEAD, "Cerberus",
                List.of("armor_head_dome"), List.of("armor_head_dome"), false,
                new SensorProfile("CERBERUS 360° DOME", "FLIR THERMAL PASS-THROUGH", 0xFF00FF66, 0xFF00FF66));

        registerArmor(ModItems.ARMOR_VOTOMS_HEAD.get(), ExoframeArmorSlot.HEAD, "VOTOMS",
                List.of("armor_head_votoms"), List.of("armor_head_votoms"), false,
                new SensorProfile("VOTOMS 3-LENS TURRET", "ROTARY PRISM PASS-THROUGH", 0xFF00FFEE, 0xFF00FFEE));

        registerArmor(ModItems.ARMOR_MILITIA_HOOD.get(), ExoframeArmorSlot.HEAD, "Outlander",
                List.of("armor_head_hood"), List.of("armor_head_hood"), false,
                new SensorProfile("PMC SLOPED PERISCOPE", "REINFORCED COWL PASS-THROUGH", 0xFFFFCC00, 0xFFFFCC00));

        registerArmor(ModItems.ARMOR_POLAR_HEAD.get(), ExoframeArmorSlot.HEAD, "Polar",
                List.of("armor_head_polar"), List.of("armor_head_polar"), false,
                new SensorProfile("ARCTIC EXPEDITION SENSOR", "ANTI-GLARE INFRARED OPTIC", 0xFF00FFEE, 0xFF00FFEE));

        // 6 New Factions - Head
        registerArmor(ModItems.ARMOR_SALVAGE_HEAD.get(), ExoframeArmorSlot.HEAD, "Salvage",
                List.of("armor_head_salvage"), List.of("armor_head_salvage"), false,
                new SensorProfile("SALVAGE SCRAP VISOR", "ANALOG OPTIC PASS-THROUGH", 0xFFFF9900, 0xFFFF9900));

        registerArmor(ModItems.ARMOR_SHIDEN_HEAD.get(), ExoframeArmorSlot.HEAD, "Shiden",
                List.of("armor_head_shiden"), List.of("armor_head_shiden"), false,
                new SensorProfile("SHIDEN COMBAT OPTIC", "MIL-STD MULTISPECTRAL", 0xFF00EEDD, 0xFF00EEDD));

        registerArmor(ModItems.ARMOR_KHAMSIN_HEAD.get(), ExoframeArmorSlot.HEAD, "Khamsin",
                List.of("armor_head_khamsin"), List.of("armor_head_khamsin"), false,
                new SensorProfile("KHAMSIN DUST FILTER", "THERMAL SAND-PIERCING", 0xFFFFBB33, 0xFFFFBB33));

        registerArmor(ModItems.ARMOR_RIVERINE_HEAD.get(), ExoframeArmorSlot.HEAD, "Riverine",
                List.of("armor_head_riverine"), List.of("armor_head_riverine"), false,
                new SensorProfile("RIVERINE SONAR TURRET", "HYDRODYNAMIC ACOUSTIC OPTIC", 0xFF00CCFF, 0xFF00CCFF));

        registerArmor(ModItems.ARMOR_SPECTER_HEAD.get(), ExoframeArmorSlot.HEAD, "Specter",
                List.of("armor_head_specter"), List.of("armor_head_specter"), true,
                new SensorProfile("SPECTER ECM VISOR", "STEALTH PASSIVE LIDAR", 0xFFCC66FF, 0xFFCC66FF));

        registerArmor(ModItems.ARMOR_VALKYRIE_HEAD.get(), ExoframeArmorSlot.HEAD, "Valkyrie",
                List.of("armor_head_valkyrie"), List.of("armor_head_valkyrie"), true,
                new SensorProfile("VALKYRIE OMNI-ARRAY", "QUANTUM PHASED SCANNER", 0xFF00FFFF, 0xFF00FFFF));

        // Role Variants - Head
        registerArmor(ModItems.ARMOR_POLICE_HEAD.get(), ExoframeArmorSlot.HEAD, "Police",
                List.of("armor_head_police"), List.of("armor_head_police"), false,
                new SensorProfile("POLICE TACTICAL VISOR", "WIDE-ANGLE CROWD SCANNER", 0xFF00AAFF, 0xFF00AAFF));

        registerArmor(ModItems.ARMOR_RESCUE_HEAD.get(), ExoframeArmorSlot.HEAD, "Rescue",
                List.of("armor_head_rescue"), List.of("armor_head_rescue"), false,
                new SensorProfile("RESCUE THERMAL DOMEPOD", "LIFE-SIGN INFRARED SCANNER", 0xFFFF9900, 0xFFFF9900));

        // ==================== 2. CHEST ARMOR VARIANTS ====================
        registerArmor(ModItems.ARMOR_SAND_CHEST.get(), ExoframeArmorSlot.CHEST, "Sand",
                List.of("armor_chest"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_USMC_CHEST.get(), ExoframeArmorSlot.CHEST, "USMC",
                List.of("armor_chest_usmc", "canopy_usmc"), List.of("canopy_usmc"), true, null);

        registerArmor(ModItems.ARMOR_CERBERUS_CHEST.get(), ExoframeArmorSlot.CHEST, "Cerberus",
                List.of("armor_chest_cerberus", "canopy_cerberus"), List.of("canopy_cerberus"), false, null);

        registerArmor(ModItems.ARMOR_ARCTIC_CHEST.get(), ExoframeArmorSlot.CHEST, "Polar",
                List.of("armor_chest_polar", "canopy_polar"), List.of("canopy_polar"), false, null);

        registerArmor(ModItems.ARMOR_MILITIA_CHEST.get(), ExoframeArmorSlot.CHEST, "Outlander",
                List.of("armor_chest_hood", "canopy_hood"), List.of("armor_chest_hood", "canopy_hood"), false,
                new SensorProfile("PMC SLOPED PERISCOPE", "REINFORCED COWL PASS-THROUGH", 0xFFFFCC00, 0xFFFFCC00));

        registerArmor(ModItems.ARMOR_ROLL_CAGE.get(), ExoframeArmorSlot.CHEST, "Industrial",
                List.of("armor_roll_cage"), List.of("armor_roll_cage"), false,
                new SensorProfile("INDUSTRIAL LIDAR ARRAY", "VOLUMETRIC STRATA PASS-THROUGH", 0xFFFFCC00, 0xFFFFCC00));

        // 6 New Factions - Chest
        registerArmor(ModItems.ARMOR_SALVAGE_CHEST.get(), ExoframeArmorSlot.CHEST, "Salvage",
                List.of("armor_chest_salvage", "canopy_salvage"), List.of("canopy_salvage"), false, null);

        registerArmor(ModItems.ARMOR_SHIDEN_CHEST.get(), ExoframeArmorSlot.CHEST, "Shiden",
                List.of("armor_chest_shiden", "canopy_shiden"), List.of("canopy_shiden"), false, null);

        registerArmor(ModItems.ARMOR_KHAMSIN_CHEST.get(), ExoframeArmorSlot.CHEST, "Khamsin",
                List.of("armor_chest_khamsin", "canopy_khamsin"), List.of("canopy_khamsin"), false, null);

        registerArmor(ModItems.ARMOR_RIVERINE_CHEST.get(), ExoframeArmorSlot.CHEST, "Riverine",
                List.of("armor_chest_riverine", "canopy_riverine"), List.of("canopy_riverine"), false, null);

        registerArmor(ModItems.ARMOR_SPECTER_CHEST.get(), ExoframeArmorSlot.CHEST, "Specter",
                List.of("armor_chest_specter", "canopy_specter"), List.of("canopy_specter"), true, null);

        registerArmor(ModItems.ARMOR_VALKYRIE_CHEST.get(), ExoframeArmorSlot.CHEST, "Valkyrie",
                List.of("armor_chest_valkyrie", "canopy_valkyrie"), List.of("canopy_valkyrie"), true, null);

        // Role Variants - Chest
        registerArmor(ModItems.ARMOR_POLICE_CHEST.get(), ExoframeArmorSlot.CHEST, "Police",
                List.of("armor_chest_police", "canopy_police"), List.of("canopy_police"), false, null);

        registerArmor(ModItems.ARMOR_RESCUE_CHEST.get(), ExoframeArmorSlot.CHEST, "Rescue",
                List.of("armor_chest_rescue", "canopy_rescue"), List.of("canopy_rescue"), false, null);

        // ==================== 3. ARMS & SHOULDER VARIANTS ====================
        registerArmor(ModItems.ARMOR_SAND_ARMS.get(), ExoframeArmorSlot.ARMS, "Sand",
                List.of("armor_left_shoulder", "armor_right_shoulder"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_USMC_ARMS.get(), ExoframeArmorSlot.ARMS, "USMC",
                List.of("armor_left_shoulder_usmc", "armor_right_shoulder_usmc"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_CERBERUS_ARMS.get(), ExoframeArmorSlot.ARMS, "Cerberus",
                List.of("armor_left_shoulder_cerberus", "armor_right_shoulder_cerberus"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_POLAR_ARMS.get(), ExoframeArmorSlot.ARMS, "Polar",
                List.of("armor_left_shoulder_polar", "armor_right_shoulder_polar"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_OUTLANDER_ARMS.get(), ExoframeArmorSlot.ARMS, "Outlander",
                List.of("armor_left_shoulder_outlander", "armor_right_shoulder_outlander"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_RED_SHOULDER_ARMS.get(), ExoframeArmorSlot.ARMS, "VOTOMS",
                List.of("armor_left_shoulder_usmc", "armor_right_shoulder_red"), Collections.emptyList(), false, null);

        // 6 New Factions - Arms
        registerArmor(ModItems.ARMOR_SALVAGE_ARMS.get(), ExoframeArmorSlot.ARMS, "Salvage",
                List.of("armor_left_shoulder_salvage", "armor_right_shoulder_salvage"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_SHIDEN_ARMS.get(), ExoframeArmorSlot.ARMS, "Shiden",
                List.of("armor_left_shoulder_shiden", "armor_right_shoulder_shiden"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_KHAMSIN_ARMS.get(), ExoframeArmorSlot.ARMS, "Khamsin",
                List.of("armor_left_shoulder_khamsin", "armor_right_shoulder_khamsin"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_RIVERINE_ARMS.get(), ExoframeArmorSlot.ARMS, "Riverine",
                List.of("armor_left_shoulder_riverine", "armor_right_shoulder_riverine"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_SPECTER_ARMS.get(), ExoframeArmorSlot.ARMS, "Specter",
                List.of("armor_left_shoulder_specter", "armor_right_shoulder_specter"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_VALKYRIE_ARMS.get(), ExoframeArmorSlot.ARMS, "Valkyrie",
                List.of("armor_left_shoulder_valkyrie", "armor_right_shoulder_valkyrie"), Collections.emptyList(), false, null);

        // ==================== 4. LEGS & GREAVES VARIANTS ====================
        registerArmor(ModItems.ARMOR_SAND_LEGS.get(), ExoframeArmorSlot.LEGS, "Sand",
                List.of("armor_left_leg", "armor_right_leg", "armor_left_shin_sand", "armor_right_shin_sand"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_USMC_LEGS.get(), ExoframeArmorSlot.LEGS, "USMC",
                List.of("armor_left_leg_usmc", "armor_right_leg_usmc", "armor_left_shin_usmc", "armor_right_shin_usmc"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_CERBERUS_LEGS.get(), ExoframeArmorSlot.LEGS, "Cerberus",
                List.of("armor_left_leg_cerberus", "armor_right_leg_cerberus", "armor_left_shin_cerberus", "armor_right_shin_cerberus"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_POLAR_LEGS.get(), ExoframeArmorSlot.LEGS, "Polar",
                List.of("armor_left_leg_polar", "armor_right_leg_polar", "armor_left_shin_polar", "armor_right_shin_polar", "armor_left_ski", "armor_right_ski"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_OUTLANDER_LEGS.get(), ExoframeArmorSlot.LEGS, "Outlander",
                List.of("armor_left_leg_outlander", "armor_right_leg_outlander", "armor_left_shin_outlander", "armor_right_shin_outlander"), Collections.emptyList(), false, null);

        // 6 New Factions - Legs
        registerArmor(ModItems.ARMOR_SALVAGE_LEGS.get(), ExoframeArmorSlot.LEGS, "Salvage",
                List.of("armor_left_leg_salvage", "armor_right_leg_salvage", "armor_left_shin_salvage", "armor_right_shin_salvage"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_SHIDEN_LEGS.get(), ExoframeArmorSlot.LEGS, "Shiden",
                List.of("armor_left_leg_shiden", "armor_right_leg_shiden", "armor_left_shin_shiden", "armor_right_shin_shiden"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_KHAMSIN_LEGS.get(), ExoframeArmorSlot.LEGS, "Khamsin",
                List.of("armor_left_leg_khamsin", "armor_right_leg_khamsin", "armor_left_shin_khamsin", "armor_right_shin_khamsin"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_RIVERINE_LEGS.get(), ExoframeArmorSlot.LEGS, "Riverine",
                List.of("armor_left_leg_riverine", "armor_right_leg_riverine", "armor_left_shin_riverine", "armor_right_shin_riverine"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_SPECTER_LEGS.get(), ExoframeArmorSlot.LEGS, "Specter",
                List.of("armor_left_leg_specter", "armor_right_leg_specter", "armor_left_shin_specter", "armor_right_shin_specter"), Collections.emptyList(), false, null);

        registerArmor(ModItems.ARMOR_VALKYRIE_LEGS.get(), ExoframeArmorSlot.LEGS, "Valkyrie",
                List.of("armor_left_leg_valkyrie", "armor_right_leg_valkyrie", "armor_left_shin_valkyrie", "armor_right_shin_valkyrie"), Collections.emptyList(), false, null);

        // Role Variants - Legs
        registerArmor(ModItems.ARMOR_FLOAT_RING.get(), ExoframeArmorSlot.LEGS, "Amphibious",
                List.of("armor_float_ring"), Collections.emptyList(), false, null);

        // ==================== 5. UTILITY & BACKPACK MODULES ====================
        registerArmor(ModItems.MODULE_USMC_COMMS.get(), ExoframeArmorSlot.UTILITY, "USMC",
                List.of("backpack_usmc"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_CERBERUS_PACKS.get(), ExoframeArmorSlot.UTILITY, "Cerberus",
                List.of("backpack_cerberus"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_SHOULDER_MISSILE.get(), ExoframeArmorSlot.UTILITY, "HeavyWeapons",
                List.of("backpack_missile_pod"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_TWIN_MANPADS.get(), ExoframeArmorSlot.UTILITY, "Polar",
                List.of("backpack_manpads"), Collections.emptyList(), false, null);

        // 6 New Factions - Utility
        registerArmor(ModItems.MODULE_SALVAGE_SCRAPS.get(), ExoframeArmorSlot.UTILITY, "Salvage",
                List.of("backpack_salvage"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_SHIDEN_CREST.get(), ExoframeArmorSlot.UTILITY, "Shiden",
                List.of("backpack_shiden"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_KHAMSIN_FILTERS.get(), ExoframeArmorSlot.UTILITY, "Khamsin",
                List.of("backpack_khamsin"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_RIVERINE_SNORKEL.get(), ExoframeArmorSlot.UTILITY, "Riverine",
                List.of("backpack_riverine"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_SPECTER_ECM.get(), ExoframeArmorSlot.UTILITY, "Specter",
                List.of("backpack_specter"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_VALKYRIE_SENSOR.get(), ExoframeArmorSlot.UTILITY, "Valkyrie",
                List.of("backpack_valkyrie"), Collections.emptyList(), false, null);

        // Role Variants - Utility
        registerArmor(ModItems.MODULE_RESCUE_WINCH.get(), ExoframeArmorSlot.UTILITY, "Rescue",
                List.of("backpack_rescue"), Collections.emptyList(), false, null);

        registerArmor(ModItems.MODULE_SEARCH_RADAR.get(), ExoframeArmorSlot.UTILITY, "Radar",
                List.of("backpack_radar"), Collections.emptyList(), false,
                new SensorProfile("TACTICAL SEARCH RADAR", "PHASED-ARRAY ACTIVE PULSER", 0xFF00FF66, 0xFF00FF66));

        registerSensorProfile(ModItems.MODULE_NIGHT_VISION_OPTIC.get(),
                new SensorProfile("CERBERUS 360° DOME", "FLIR THERMAL PASS-THROUGH", 0xFF00FF66, 0xFF00FF66));

        registerSensorProfile(ModItems.MODULE_GEOLOGICAL_SCANNER.get(),
                new SensorProfile("INDUSTRIAL LIDAR ARRAY", "VOLUMETRIC STRATA PASS-THROUGH", 0xFFFFCC00, 0xFFFFCC00));

        registerSensorProfile(ModItems.MODULE_DIVING_BALLAST.get(),
                new SensorProfile("DEEP-SEA HYDRO-OPTIC", "PRESSURE-SEALED SONAR FEED", 0xFF00FFEE, 0xFF00AAFF));

        // Always register cargo crate fallback
        ALL_KNOWN_ARMOR_BONES.add("backpack_cargo");
        ALL_KNOWN_ARMOR_BONES.add("backpack_ammo");

        // ==================== 6. WEAPONS & WORKING TOOLS ====================
        registerWeapon(ModItems.EXOFRAME_ASSAULT_RIFLE.get(), "weapon_assault_rifle", ExoframeArmIK.Hold.RIFLE, false, false);
        registerWeapon(ModItems.EXOFRAME_SNIPER_RIFLE.get(), "weapon_sniper_amr", ExoframeArmIK.Hold.SNIPER, false, false);
        registerWeapon(ModItems.EXOFRAME_MACHINE_GUN.get(), "weapon_machine_gun", ExoframeArmIK.Hold.MACHINE_GUN, false, false);
        registerWeapon(ModItems.EXOFRAME_MINIGUN.get(), "weapon_minigun_m134", ExoframeArmIK.Hold.MINIGUN, false, false);
        registerWeapon(ModItems.EXOFRAME_ROCKET_LAUNCHER.get(), "weapon_rocket_launcher", ExoframeArmIK.Hold.POD_LAUNCHER, false, false);
        registerWeapon(ModItems.EXOFRAME_RPG7.get(), "weapon_rpg7_heavy", ExoframeArmIK.Hold.RPG, false, false);
        registerWeapon(ModItems.TOOL_MINING_DRILL.get(), "tool_mining_drill", ExoframeArmIK.Hold.TOOL_DRILL, false, false);
        registerWeapon(ModItems.TOOL_CHAINSAW.get(), "tool_chainsaw", ExoframeArmIK.Hold.TOOL_SAW, false, false);
        registerWeapon(ModItems.TOOL_CULTIVATOR_PLOW.get(), "tool_cultivator_plow", ExoframeArmIK.Hold.TOOL_DRILL, false, false);

        // 8 New Weapons
        registerWeapon(ModItems.EXOFRAME_BATTLE_RIFLE.get(), "weapon_battle_rifle", ExoframeArmIK.Hold.BATTLE_RIFLE, false, false);
        registerWeapon(ModItems.EXOFRAME_AUTOCANNON_30MM.get(), "weapon_autocannon_30mm", ExoframeArmIK.Hold.AUTOCANNON_30MM, false, false);
        registerWeapon(ModItems.EXOFRAME_SHOTGUN_BREACHER.get(), "weapon_shotgun_breacher", ExoframeArmIK.Hold.SHOTGUN_BREACHER, false, false);
        registerWeapon(ModItems.EXOFRAME_GRENADE_LAUNCHER.get(), "weapon_grenade_launcher", ExoframeArmIK.Hold.GRENADE_LAUNCHER, false, false);
        registerWeapon(ModItems.EXOFRAME_RECOILLESS_RIFLE.get(), "weapon_recoilless_rifle", ExoframeArmIK.Hold.RECOILLESS_RIFLE, false, false);
        registerWeapon(ModItems.EXOFRAME_ATGM_GUIDED.get(), "weapon_atgm_guided", ExoframeArmIK.Hold.ATGM_GUIDED, false, false);
        registerWeapon(ModItems.EXOFRAME_FLAMETHROWER.get(), "weapon_flamethrower", ExoframeArmIK.Hold.FLAMETHROWER, false, false);
        registerWeapon(ModItems.EXOFRAME_VIBRO_BLADE.get(), "weapon_vibro_blade", ExoframeArmIK.Hold.VIBRO_BLADE, true, false);

        // Role Weapons & Equipment
        registerWeapon(ModItems.EXOFRAME_RIOT_SHIELD.get(), "weapon_riot_shield", ExoframeArmIK.Hold.RIFLE, false, true);
        registerWeapon(ModItems.EXOFRAME_STUN_BATON.get(), "weapon_stun_baton", ExoframeArmIK.Hold.STUN_BATON, true, false);
        registerWeapon(ModItems.EXOFRAME_FISHING_ROD.get(), "weapon_fishing_rod", ExoframeArmIK.Hold.FISHING_ROD, false, false);
    }

    public static void registerArmor(Item item, ExoframeArmorSlot slot, String faction,
                                      List<String> visibleBones, List<String> firstPersonHiddenBones,
                                      boolean hidesFrameHead, SensorProfile sensorProfile) {
        ArmorVariantData data = new ArmorVariantData(item, slot, faction, visibleBones, firstPersonHiddenBones, hidesFrameHead, sensorProfile);
        ARMOR_VARIANTS.put(item, data);
        ALL_KNOWN_ARMOR_BONES.addAll(visibleBones);
        if (sensorProfile != null) {
            SENSOR_PROFILES.put(item, sensorProfile);
        }
    }

    public static void registerWeapon(Item item, String weaponBoneName, ExoframeArmIK.Hold hold, boolean isMelee, boolean isShield) {
        WeaponVariantData data = new WeaponVariantData(item, weaponBoneName, hold, isMelee, isShield);
        WEAPON_VARIANTS.put(item, data);
        ALL_KNOWN_WEAPON_BONES.add(weaponBoneName);
    }

    public static void registerSensorProfile(Item item, SensorProfile profile) {
        SENSOR_PROFILES.put(item, profile);
    }

    public static ArmorVariantData getArmorData(Item item) {
        ensureInitialized();
        return ARMOR_VARIANTS.get(item);
    }

    public static WeaponVariantData getWeaponData(Item item) {
        ensureInitialized();
        return WEAPON_VARIANTS.get(item);
    }

    public static SensorProfile getSensorProfile(Item item) {
        ensureInitialized();
        return SENSOR_PROFILES.get(item);
    }

    public static SensorProfile resolveSensorProfile(ItemStack headStack, ItemStack chestStack, ItemStack utilStack, boolean inWater) {
        ensureInitialized();
        // 1. High priority optical override module (e.g. Night Vision)
        if (!utilStack.isEmpty() && utilStack.is(ModItems.MODULE_NIGHT_VISION_OPTIC.get())) {
            SensorProfile sp = getSensorProfile(utilStack.getItem());
            if (sp != null) return sp;
        }
        // 2. Head armor sensor
        if (!headStack.isEmpty()) {
            SensorProfile sp = getSensorProfile(headStack.getItem());
            if (sp != null) return sp;
        }
        // 3. Chest armor sensor / canopy
        if (!chestStack.isEmpty()) {
            SensorProfile sp = getSensorProfile(chestStack.getItem());
            if (sp != null) return sp;
        }
        // 4. Utility module sensor
        if (!utilStack.isEmpty()) {
            SensorProfile sp = getSensorProfile(utilStack.getItem());
            if (sp != null) return sp;
        }
        // 5. Environmental underwater sensor
        if (inWater) {
            return new SensorProfile("DEEP-SEA HYDRO-OPTIC", "PRESSURE-SEALED SONAR FEED", 0xFF00FFEE, 0xFF00AAFF);
        }
        // 6. Default standard sensor
        return new SensorProfile("NOSE SENSOR TURRET", "4K PASS-THROUGH (0.8ms)", 0xFF00AAFF, 0xFF00AAFF);
    }

    public static Set<String> getAllKnownArmorBones() {
        ensureInitialized();
        return Collections.unmodifiableSet(ALL_KNOWN_ARMOR_BONES);
    }

    public static Set<String> getAllKnownWeaponBones() {
        ensureInitialized();
        return Collections.unmodifiableSet(ALL_KNOWN_WEAPON_BONES);
    }

    public static Collection<ArmorVariantData> getAllArmorData() {
        ensureInitialized();
        return Collections.unmodifiableCollection(ARMOR_VARIANTS.values());
    }

    public static ExoframeArmIK.Hold getHoldForWeapon(Item item) {
        WeaponVariantData data = getWeaponData(item);
        return data != null ? data.hold() : ExoframeArmIK.Hold.RIFLE;
    }
}
