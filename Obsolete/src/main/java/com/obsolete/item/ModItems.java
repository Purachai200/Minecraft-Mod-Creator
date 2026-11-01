package com.obsolete.item;

import com.obsolete.ObsoleteMod;
import com.obsolete.block.ModBlocks;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, ObsoleteMod.MODID);

    // ==================== 1. DEPLOYMENT ====================
    public static final RegistryObject<Item> EXOFRAME_KIT =
            ITEMS.register("exoframe_kit", () -> new ExoframeKitItem(new Item.Properties(), 1));

    public static final RegistryObject<Item> EXOFRAME_KIT_SALVAGE =
            ITEMS.register("exoframe_kit_salvage", () -> new ExoframeKitItem(new Item.Properties(), 0));

    public static final RegistryObject<Item> EXOFRAME_KIT_ADVANCED =
            ITEMS.register("exoframe_kit_advanced", () -> new ExoframeKitItem(new Item.Properties(), 2));

    public static final RegistryObject<Item> EXOFRAME_KIT_ELITE =
            ITEMS.register("exoframe_kit_elite", () -> new ExoframeKitItem(new Item.Properties(), 3));

    // ==================== 2. OUTCAST SAND PMC ARMOR ====================
    public static final RegistryObject<Item> ARMOR_SAND_HEAD =
            ITEMS.register("armor_sand_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(250), ExoframeArmorSlot.HEAD, 0.15F, "Outcast Sand PMC"));

    public static final RegistryObject<Item> ARMOR_SAND_CHEST =
            ITEMS.register("armor_sand_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(450), ExoframeArmorSlot.CHEST, 0.35F, "Outcast Sand PMC"));

    public static final RegistryObject<Item> ARMOR_SAND_ARMS =
            ITEMS.register("armor_sand_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(300), ExoframeArmorSlot.ARMS, 0.20F, "Outcast Sand PMC"));

    public static final RegistryObject<Item> ARMOR_SAND_LEGS =
            ITEMS.register("armor_sand_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(350), ExoframeArmorSlot.LEGS, 0.25F, "Outcast Sand PMC"));

    // ==================== 3. USMC RECON ARMOR (Olive Drab - Image 1 & 3) ====================
    public static final RegistryObject<Item> ARMOR_USMC_HEAD =
            ITEMS.register("armor_usmc_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(320), ExoframeArmorSlot.HEAD, 0.18F, "Marine Raider"));

    public static final RegistryObject<Item> ARMOR_USMC_CHEST =
            ITEMS.register("armor_usmc_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(520), ExoframeArmorSlot.CHEST, 0.38F, "Marine Raider"));

    public static final RegistryObject<Item> ARMOR_USMC_ARMS =
            ITEMS.register("armor_usmc_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(340), ExoframeArmorSlot.ARMS, 0.22F, "Marine Raider"));

    public static final RegistryObject<Item> ARMOR_USMC_LEGS =
            ITEMS.register("armor_usmc_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(380), ExoframeArmorSlot.LEGS, 0.26F, "Marine Raider"));

    // ==================== 4. CERBERUS PMC NIGHT-OPS ARMOR (Image 2) ====================
    public static final RegistryObject<Item> ARMOR_CERBERUS_HEAD =
            ITEMS.register("armor_cerberus_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(300), ExoframeArmorSlot.HEAD, 0.18F, "Pegaso Black"));

    public static final RegistryObject<Item> ARMOR_CERBERUS_CHEST =
            ITEMS.register("armor_cerberus_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(550), ExoframeArmorSlot.CHEST, 0.40F, "Pegaso Black"));

    public static final RegistryObject<Item> ARMOR_CERBERUS_ARMS =
            ITEMS.register("armor_cerberus_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(350), ExoframeArmorSlot.ARMS, 0.24F, "Pegaso Black"));

    public static final RegistryObject<Item> ARMOR_CERBERUS_LEGS =
            ITEMS.register("armor_cerberus_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(400), ExoframeArmorSlot.LEGS, 0.28F, "Pegaso Black"));

    // ==================== 5. VOTOMS COLLABORATION & GUERRILLA ARMORS (Image 4 & 5) ====================
    public static final RegistryObject<Item> ARMOR_VOTOMS_HEAD =
            ITEMS.register("armor_votoms_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(340), ExoframeArmorSlot.HEAD, 0.20F, "VOTOMS 3-Lens Revolving Turret Camera"));

    public static final RegistryObject<Item> ARMOR_RED_SHOULDER_ARMS =
            ITEMS.register("armor_red_shoulder_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(360), ExoframeArmorSlot.ARMS, 0.25F, "VOTOMS Blood-Red Right Shoulder Set"));

    public static final RegistryObject<Item> ARMOR_MILITIA_HOOD =
            ITEMS.register("armor_militia_hood", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(300), ExoframeArmorSlot.HEAD, 0.18F, "Outlander Heavy"));

    public static final RegistryObject<Item> ARMOR_MILITIA_CHEST =
            ITEMS.register("armor_militia_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(560), ExoframeArmorSlot.CHEST, 0.42F, "Outlander Heavy"));

    public static final RegistryObject<Item> ARMOR_ARCTIC_CHEST =
            ITEMS.register("armor_arctic_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(480), ExoframeArmorSlot.CHEST, 0.35F, "Polar Front"));

    public static final RegistryObject<Item> ARMOR_POLAR_HEAD =
            ITEMS.register("armor_polar_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(320), ExoframeArmorSlot.HEAD, 0.20F, "Polar Front"));

    public static final RegistryObject<Item> ARMOR_POLAR_ARMS =
            ITEMS.register("armor_polar_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(340), ExoframeArmorSlot.ARMS, 0.22F, "Polar Front"));

    public static final RegistryObject<Item> ARMOR_POLAR_LEGS =
            ITEMS.register("armor_polar_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(380), ExoframeArmorSlot.LEGS, 0.24F, "Polar Front"));

    public static final RegistryObject<Item> ARMOR_OUTLANDER_ARMS =
            ITEMS.register("armor_outlander_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(400), ExoframeArmorSlot.ARMS, 0.27F, "Outlander Heavy"));

    public static final RegistryObject<Item> ARMOR_OUTLANDER_LEGS =
            ITEMS.register("armor_outlander_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(440), ExoframeArmorSlot.LEGS, 0.30F, "Outlander Heavy"));

    // ==================== 6. INDUSTRIAL SAFETY ROLL-CAGE ====================
    public static final RegistryObject<Item> ARMOR_ROLL_CAGE =
            ITEMS.register("armor_roll_cage", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(500), ExoframeArmorSlot.CHEST, 0.40F, "Civilian Industrial Safety Roll Cage"));

    // ==================== 6B. NEW FACTION ARMORS (6 SETS) ====================
    // 1. Salvage Militia Set
    public static final RegistryObject<Item> ARMOR_SALVAGE_HEAD =
            ITEMS.register("armor_salvage_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(240), ExoframeArmorSlot.HEAD, 0.14F, "Salvage Militia"));
    public static final RegistryObject<Item> ARMOR_SALVAGE_CHEST =
            ITEMS.register("armor_salvage_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(420), ExoframeArmorSlot.CHEST, 0.32F, "Salvage Militia"));
    public static final RegistryObject<Item> ARMOR_SALVAGE_ARMS =
            ITEMS.register("armor_salvage_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(280), ExoframeArmorSlot.ARMS, 0.18F, "Salvage Militia"));
    public static final RegistryObject<Item> ARMOR_SALVAGE_LEGS =
            ITEMS.register("armor_salvage_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(320), ExoframeArmorSlot.LEGS, 0.22F, "Salvage Militia"));
    public static final RegistryObject<Item> MODULE_SALVAGE_SCRAPS =
            ITEMS.register("module_salvage_scraps", () -> new Item(new Item.Properties().stacksTo(1)));

    // 2. Shiden Corps Set
    public static final RegistryObject<Item> ARMOR_SHIDEN_HEAD =
            ITEMS.register("armor_shiden_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(360), ExoframeArmorSlot.HEAD, 0.22F, "Shiden Corps"));
    public static final RegistryObject<Item> ARMOR_SHIDEN_CHEST =
            ITEMS.register("armor_shiden_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(580), ExoframeArmorSlot.CHEST, 0.44F, "Shiden Corps"));
    public static final RegistryObject<Item> ARMOR_SHIDEN_ARMS =
            ITEMS.register("armor_shiden_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(380), ExoframeArmorSlot.ARMS, 0.26F, "Shiden Corps"));
    public static final RegistryObject<Item> ARMOR_SHIDEN_LEGS =
            ITEMS.register("armor_shiden_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(420), ExoframeArmorSlot.LEGS, 0.30F, "Shiden Corps"));
    public static final RegistryObject<Item> MODULE_SHIDEN_CREST =
            ITEMS.register("module_shiden_crest", () -> new Item(new Item.Properties().stacksTo(1)));

    // 3. Khamsin Long-Range Guard Set
    public static final RegistryObject<Item> ARMOR_KHAMSIN_HEAD =
            ITEMS.register("armor_khamsin_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(330), ExoframeArmorSlot.HEAD, 0.19F, "Khamsin Guard"));
    public static final RegistryObject<Item> ARMOR_KHAMSIN_CHEST =
            ITEMS.register("armor_khamsin_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(500), ExoframeArmorSlot.CHEST, 0.38F, "Khamsin Guard"));
    public static final RegistryObject<Item> ARMOR_KHAMSIN_ARMS =
            ITEMS.register("armor_khamsin_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(350), ExoframeArmorSlot.ARMS, 0.23F, "Khamsin Guard"));
    public static final RegistryObject<Item> ARMOR_KHAMSIN_LEGS =
            ITEMS.register("armor_khamsin_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(390), ExoframeArmorSlot.LEGS, 0.27F, "Khamsin Guard"));
    public static final RegistryObject<Item> MODULE_KHAMSIN_FILTERS =
            ITEMS.register("module_khamsin_filters", () -> new Item(new Item.Properties().stacksTo(1)));

    // 4. Riverine Corps Set
    public static final RegistryObject<Item> ARMOR_RIVERINE_HEAD =
            ITEMS.register("armor_riverine_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(340), ExoframeArmorSlot.HEAD, 0.20F, "Riverine Corps"));
    public static final RegistryObject<Item> ARMOR_RIVERINE_CHEST =
            ITEMS.register("armor_riverine_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(540), ExoframeArmorSlot.CHEST, 0.40F, "Riverine Corps"));
    public static final RegistryObject<Item> ARMOR_RIVERINE_ARMS =
            ITEMS.register("armor_riverine_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(360), ExoframeArmorSlot.ARMS, 0.24F, "Riverine Corps"));
    public static final RegistryObject<Item> ARMOR_RIVERINE_LEGS =
            ITEMS.register("armor_riverine_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(400), ExoframeArmorSlot.LEGS, 0.28F, "Riverine Corps"));
    public static final RegistryObject<Item> MODULE_RIVERINE_SNORKEL =
            ITEMS.register("module_riverine_snorkel", () -> new Item(new Item.Properties().stacksTo(1)));

    // 5. Specter Stealth PMC Set
    public static final RegistryObject<Item> ARMOR_SPECTER_HEAD =
            ITEMS.register("armor_specter_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(350), ExoframeArmorSlot.HEAD, 0.21F, "Specter PMC"));
    public static final RegistryObject<Item> ARMOR_SPECTER_CHEST =
            ITEMS.register("armor_specter_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(560), ExoframeArmorSlot.CHEST, 0.42F, "Specter PMC"));
    public static final RegistryObject<Item> ARMOR_SPECTER_ARMS =
            ITEMS.register("armor_specter_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(370), ExoframeArmorSlot.ARMS, 0.25F, "Specter PMC"));
    public static final RegistryObject<Item> ARMOR_SPECTER_LEGS =
            ITEMS.register("armor_specter_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(410), ExoframeArmorSlot.LEGS, 0.29F, "Specter PMC"));
    public static final RegistryObject<Item> MODULE_SPECTER_ECM =
            ITEMS.register("module_specter_ecm", () -> new Item(new Item.Properties().stacksTo(1)));

    // 6. Valkyrie Special Forces Set
    public static final RegistryObject<Item> ARMOR_VALKYRIE_HEAD =
            ITEMS.register("armor_valkyrie_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(400), ExoframeArmorSlot.HEAD, 0.25F, "Valkyrie Forces"));
    public static final RegistryObject<Item> ARMOR_VALKYRIE_CHEST =
            ITEMS.register("armor_valkyrie_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(650), ExoframeArmorSlot.CHEST, 0.48F, "Valkyrie Forces"));
    public static final RegistryObject<Item> ARMOR_VALKYRIE_ARMS =
            ITEMS.register("armor_valkyrie_arms", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(420), ExoframeArmorSlot.ARMS, 0.28F, "Valkyrie Forces"));
    public static final RegistryObject<Item> ARMOR_VALKYRIE_LEGS =
            ITEMS.register("armor_valkyrie_legs", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(460), ExoframeArmorSlot.LEGS, 0.32F, "Valkyrie Forces"));
    public static final RegistryObject<Item> MODULE_VALKYRIE_SENSOR =
            ITEMS.register("module_valkyrie_sensor", () -> new Item(new Item.Properties().stacksTo(1)));

    // ==================== 7. UTILITY & BACKPACK MODULES ====================
    public static final RegistryObject<Item> MODULE_USMC_COMMS =
            ITEMS.register("module_usmc_comms", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_CERBERUS_PACKS =
            ITEMS.register("module_cerberus_packs", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_SHOULDER_MISSILE =
            ITEMS.register("module_shoulder_missile", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_TWIN_MANPADS =
            ITEMS.register("module_twin_manpads", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_GEOLOGICAL_SCANNER =
            ITEMS.register("module_geological_scanner", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_NIGHT_VISION_OPTIC =
            ITEMS.register("module_night_vision_optic", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_CARGO_CRATE =
            ITEMS.register("module_cargo_crate", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_AGRI_HOPPER =
            ITEMS.register("module_agri_hopper", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_DIVING_BALLAST =
            ITEMS.register("module_diving_ballast", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_TARGETING_COMPUTER =
            ITEMS.register("module_targeting_computer", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> MODULE_FLIGHT_BOOSTER =
            ITEMS.register("module_flight_booster", () -> new ExoframeFlightBoosterItem(
                    new Item.Properties().stacksTo(1), ExoframeFlightBoosterItem.BoosterType.ROCKET_JETPACK));

    public static final RegistryObject<Item> MODULE_VTOL_WINGS =
            ITEMS.register("module_vtol_wings", () -> new ExoframeFlightBoosterItem(
                    new Item.Properties().stacksTo(1), ExoframeFlightBoosterItem.BoosterType.VTOL_WINGS));

    public static final RegistryObject<Item> MODULE_DRONE_LIFTER =
            ITEMS.register("module_drone_lifter", () -> new ExoframeFlightBoosterItem(
                    new Item.Properties().stacksTo(1), ExoframeFlightBoosterItem.BoosterType.DRONE_LIFTER));

    public static final RegistryObject<Item> MODULE_ACTIVE_CLOAK =
            ITEMS.register("module_active_cloak", () -> new Item(new Item.Properties().stacksTo(1)));

    // ==================== 8. SPECIALIZED WORKING TOOLS ====================
    public static final RegistryObject<Item> TOOL_MINING_DRILL =
            ITEMS.register("tool_mining_drill", () -> new ExoframeMiningDrillItem(new Item.Properties()));

    public static final RegistryObject<Item> TOOL_CHAINSAW =
            ITEMS.register("tool_chainsaw", () -> new ExoframeChainsawItem(new Item.Properties()));

    public static final RegistryObject<Item> TOOL_CULTIVATOR_PLOW =
            ITEMS.register("tool_cultivator_plow", () -> new ExoframeCultivatorPlowItem(new Item.Properties()));

    // ==================== 9. TACTICAL WEAPONS ====================
    public static final RegistryObject<Item> EXOFRAME_ASSAULT_RIFLE =
            ITEMS.register("exoframe_assault_rifle", () -> new ExoframeAssaultRifleItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_SNIPER_RIFLE =
            ITEMS.register("exoframe_sniper_rifle", () -> new ExoframeSniperRifleItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_MACHINE_GUN =
            ITEMS.register("exoframe_machine_gun", () -> new ExoframeMachineGunItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_MINIGUN =
            ITEMS.register("exoframe_minigun", () -> new ExoframeMinigunItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_ROCKET_LAUNCHER =
            ITEMS.register("exoframe_rocket_launcher", () -> new ExoframeRocketLauncherItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_RPG7 =
            ITEMS.register("exoframe_rpg7", () -> new ExoframeRPG7Item(new Item.Properties()));

    // ==================== 9B. 8 NEW TACTICAL WEAPONS ====================
    public static final RegistryObject<Item> EXOFRAME_BATTLE_RIFLE =
            ITEMS.register("exoframe_battle_rifle", () -> new ExoframeBattleRifleItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_AUTOCANNON_30MM =
            ITEMS.register("exoframe_autocannon_30mm", () -> new ExoframeAutocannonItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_SHOTGUN_BREACHER =
            ITEMS.register("exoframe_shotgun_breacher", () -> new ExoframeShotgunBreacherItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_GRENADE_LAUNCHER =
            ITEMS.register("exoframe_grenade_launcher", () -> new ExoframeGrenadeLauncherItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_RECOILLESS_RIFLE =
            ITEMS.register("exoframe_recoilless_rifle", () -> new ExoframeRecoillessRifleItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_ATGM_GUIDED =
            ITEMS.register("exoframe_atgm_guided", () -> new ExoframeATGMGuidedItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_FLAMETHROWER =
            ITEMS.register("exoframe_flamethrower", () -> new ExoframeFlamethrowerItem(new Item.Properties()));

    public static final RegistryObject<Item> EXOFRAME_VIBRO_BLADE =
            ITEMS.register("exoframe_vibro_blade", () -> new ExoframeVibroBladeItem(new Item.Properties()));

    // ==================== 9C. ROLE VARIANTS ITEMS ====================
    public static final RegistryObject<Item> ARMOR_POLICE_HEAD =
            ITEMS.register("armor_police_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(350), ExoframeArmorSlot.HEAD, 0.20F, "Tactical Police"));
    public static final RegistryObject<Item> ARMOR_POLICE_CHEST =
            ITEMS.register("armor_police_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(550), ExoframeArmorSlot.CHEST, 0.42F, "Tactical Police"));
    public static final RegistryObject<Item> EXOFRAME_RIOT_SHIELD =
            ITEMS.register("exoframe_riot_shield", () -> new Item(new Item.Properties().durability(650)));
    public static final RegistryObject<Item> EXOFRAME_STUN_BATON =
            ITEMS.register("exoframe_stun_baton", () -> new Item(new Item.Properties().durability(450)));

    public static final RegistryObject<Item> ARMOR_RESCUE_HEAD =
            ITEMS.register("armor_rescue_head", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(380), ExoframeArmorSlot.HEAD, 0.22F, "Disaster Relief NGO"));
    public static final RegistryObject<Item> ARMOR_RESCUE_CHEST =
            ITEMS.register("armor_rescue_chest", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(560), ExoframeArmorSlot.CHEST, 0.40F, "Disaster Relief NGO"));
    public static final RegistryObject<Item> MODULE_RESCUE_WINCH =
            ITEMS.register("module_rescue_winch", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> ARMOR_FLOAT_RING =
            ITEMS.register("armor_float_ring", () -> new ExoframeArmorItem(
                    new Item.Properties().durability(400), ExoframeArmorSlot.LEGS, 0.15F, "Amphibious Buoyancy Ring"));

    public static final RegistryObject<Item> MODULE_SEARCH_RADAR =
            ITEMS.register("module_search_radar", () -> new Item(new Item.Properties().stacksTo(1)));

    public static final RegistryObject<Item> EXOFRAME_FISHING_ROD =
            ITEMS.register("exoframe_fishing_rod", () -> new Item(new Item.Properties().durability(300)));

    // ==================== 10. AMMUNITION ====================
    public static final RegistryObject<Item> AMMO_20MM =
            ITEMS.register("ammo_20mm", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.CALIBER_20MM));

    public static final RegistryObject<Item> AMMO_762_MINIGUN =
            ITEMS.register("ammo_762_minigun", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.CALIBER_762_MINIGUN));

    public static final RegistryObject<Item> AMMO_ROCKET =
            ITEMS.register("ammo_rocket", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.AT_ROCKET));

    public static final RegistryObject<Item> AMMO_RPG_WARHEAD =
            ITEMS.register("ammo_rpg_warhead", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.HEAVY_RPG_WARHEAD));

    // ==================== 10B. 6 NEW AMMUNITIONS ====================
    public static final RegistryObject<Item> AMMO_30MM_AUTOCANNON =
            ITEMS.register("ammo_30mm_autocannon", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.CALIBER_30MM));

    public static final RegistryObject<Item> AMMO_SHOTGUN_SLUG =
            ITEMS.register("ammo_shotgun_slug", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.SHOTGUN_SLUG));

    public static final RegistryObject<Item> AMMO_40MM_GRENADE =
            ITEMS.register("ammo_40mm_grenade", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.GRENADE_40MM));

    public static final RegistryObject<Item> AMMO_84MM_ROCKET =
            ITEMS.register("ammo_84mm_rocket", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.ROCKET_84MM));

    public static final RegistryObject<Item> AMMO_ATGM_MISSILE =
            ITEMS.register("ammo_atgm_missile", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.ATGM_MISSILE));

    public static final RegistryObject<Item> AMMO_NAPALM_CANISTER =
            ITEMS.register("ammo_napalm_canister", () -> new ExoframeAmmoItem(new Item.Properties(), ExoframeAmmoItem.AmmoType.NAPALM_CANISTER));

    // ==================== 11. CRAFTING COMPONENTS & STATION ====================
    public static final RegistryObject<Item> HYDRAULIC_CYLINDER =
            ITEMS.register("hydraulic_cylinder", () -> new Item(new Item.Properties()));

    public static final RegistryObject<Item> SERVO_MOTOR =
            ITEMS.register("servo_motor", () -> new Item(new Item.Properties()));

    public static final RegistryObject<Item> REINFORCED_STEEL_PLATE =
            ITEMS.register("reinforced_steel_plate", () -> new Item(new Item.Properties()));

    public static final RegistryObject<Item> PEDDLER_CORE =
            ITEMS.register("peddler_core", () -> new Item(new Item.Properties()));

    public static final RegistryObject<Item> MECH_ASSEMBLY_STATION_ITEM =
            ITEMS.register("mech_assembly_station", () -> new BlockItem(ModBlocks.MECH_ASSEMBLY_STATION.get(), new Item.Properties()));

    public static void register(IEventBus eventBus) {
        ITEMS.register(eventBus);
    }
}
