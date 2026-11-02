package com.titancombat.item;

import com.titancombat.entity.TitanWeapon;
import java.util.EnumMap;
import java.util.Map;

import com.titancombat.TitanCombatMod;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, TitanCombatMod.MODID);

    // Tools & Equipment
    public static final RegistryObject<Item> TITAN_DROP_BEACON = ITEMS.register("titan_drop_beacon",
            () -> new TitanDropBeaconItem(new Item.Properties().stacksTo(16).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> TROOPER_BEACON = ITEMS.register("trooper_beacon",
            () -> new TrooperBeaconItem(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> PAINT_SPRAY_CAN = ITEMS.register("paint_spray_can",
            () -> new PaintSprayCanItem(new Item.Properties().stacksTo(1).durability(64).rarity(Rarity.RARE)));

    public static final RegistryObject<Item> TITAN_BATTERY = ITEMS.register("titan_battery",
            () -> new TitanBatteryItem(TitanBatteryItem.TIER_1_CAPACITY, new Item.Properties().stacksTo(1).rarity(Rarity.RARE)));

    public static final RegistryObject<Item> HEAVY_TITAN_BATTERY = ITEMS.register("heavy_titan_battery",
            () -> new TitanBatteryItem(TitanBatteryItem.TIER_2_CAPACITY, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> DENSE_FUSION_BATTERY = ITEMS.register("dense_fusion_battery",
            () -> new TitanBatteryItem(TitanBatteryItem.TIER_3_CAPACITY, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> EMPTY_BATTERY = ITEMS.register("empty_battery",
            () -> new TitanBatteryItem(TitanBatteryItem.TIER_1_CAPACITY, new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> TITAN_AMMO = ITEMS.register("titan_ammo",
            () -> new TitanAmmoItem(new Item.Properties().stacksTo(64).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> PILOT_LICENSE = ITEMS.register("pilot_license",
            () -> new PilotLicenseItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> BLOWTORCH = ITEMS.register("blowtorch",
            () -> new MaintenanceBlowtorchItem(new Item.Properties().stacksTo(1).durability(150).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> HANGAR_TRANSPONDER = ITEMS.register("hangar_transponder",
            () -> new HangarTransponderItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> TRANSPORT_WINCH = ITEMS.register("transport_winch",
            () -> new HeavyTransportWinchItem(new Item.Properties().stacksTo(1).rarity(Rarity.RARE)));

    public static final RegistryObject<Item> HAULER_TRUCK = ITEMS.register("hauler_truck",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.HAULER_TRUCK::get, "Titan 8x8 Hauler Truck", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> CARGO_BARGE = ITEMS.register("cargo_barge",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.CARGO_BARGE::get, "Amphibious Cargo Barge", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> SKYCRANE_DRONE = ITEMS.register("skycrane_drone",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.SKYCRANE_DRONE::get, "Heavy Sky-Crane Drone", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> OCEAN_CARRIER = ITEMS.register("ocean_carrier",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.OCEAN_CARRIER::get, "Oceanic Super-Carrier Barge", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> TACTICAL_TRUCK = ITEMS.register("tactical_truck",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.TACTICAL_TRUCK::get, "Heavy Tactical Technical", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> CHINOOK_TRANSPORTER = ITEMS.register("chinook_transporter",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.CHINOOK_TRANSPORTER::get, "CH-47 Chinook Transporter", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> V22_OSPREY = ITEMS.register("v22_osprey",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.V22_OSPREY::get, "V-22 Osprey Tiltrotor", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> ARMORED_APC = ITEMS.register("armored_apc",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.ARMORED_APC::get, "Armored Combat 8x8 APC", new Item.Properties().stacksTo(1).rarity(Rarity.RARE)));

    public static final RegistryObject<Item> MOBILE_SUIT_TRAILER = ITEMS.register("mobile_suit_trailer",
            () -> new TransportVehicleDeployItem(com.titancombat.entity.ModEntities.MOBILE_SUIT_TRAILER::get, "Mobile Suit Flatbed Trailer", new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> VEHICLE_WRENCH = ITEMS.register("vehicle_wrench",
            () -> new VehicleWrenchItem(new Item.Properties().stacksTo(1).durability(250).rarity(Rarity.RARE)));

    // Assembly Components
    public static final RegistryObject<Item> CHASSIS_FRAME = ITEMS.register("chassis_frame",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> COCKPIT_MODULE = ITEMS.register("cockpit_module",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.RARE)));

    public static final RegistryObject<Item> HYDRAULIC_ACTUATOR = ITEMS.register("hydraulic_actuator",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> FUSION_REACTOR = ITEMS.register("fusion_reactor",
            () -> new Item(new Item.Properties().stacksTo(8).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> WEAPON_MOUNT = ITEMS.register("weapon_mount",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));

    // Titan weapon modules (any chassis) and their dedicated magazines
    // Back-mounted howitzer (a skill module for the back equipment slot) and its shell racks.
    public static final RegistryObject<Item> HOWITZER_MODULE = ITEMS.register("howitzer_module",
            () -> new HowitzerModuleItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> HOWITZER_SHELLS = ITEMS.register("ammo_artillery",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));
    public static final RegistryObject<Item> HOWITZER_SMOKE_SHELLS = ITEMS.register("ammo_artillery_smoke",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));

    // Back-mounted rocket pod module and ammo
    public static final RegistryObject<Item> ROCKET_LAUNCHER_MODULE = ITEMS.register("rocket_launcher_module",
            () -> new RocketLauncherModuleItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> AMMO_ROCKET_SALVO = ITEMS.register("ammo_rocket_salvo",
            () -> new Item(new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON)));

    // Modular Titan Armor Parts
    public static final RegistryObject<Item> TITAN_ARMOR_HEAD = ITEMS.register("titan_armor_head",
            () -> new TitanArmorItem(TitanArmorItem.ArmorSlot.HEAD, new Item.Properties()));
    public static final RegistryObject<Item> TITAN_ARMOR_CHEST = ITEMS.register("titan_armor_chest",
            () -> new TitanArmorItem(TitanArmorItem.ArmorSlot.CHEST, new Item.Properties()));
    public static final RegistryObject<Item> TITAN_ARMOR_ARMS = ITEMS.register("titan_armor_arms",
            () -> new TitanArmorItem(TitanArmorItem.ArmorSlot.ARMS, new Item.Properties()));
    public static final RegistryObject<Item> TITAN_ARMOR_LEGS = ITEMS.register("titan_armor_legs",
            () -> new TitanArmorItem(TitanArmorItem.ArmorSlot.LEGS, new Item.Properties()));

    // Back-Mounted Core Function Modules (Slot 13)
    public static final RegistryObject<Item> MODULE_CLOAKING = ITEMS.register("module_cloaking",
            () -> new TitanCoreModuleItem(TitanCoreModuleItem.CoreType.CLOAKING, new Item.Properties()));
    public static final RegistryObject<Item> MODULE_PHASE_WARP = ITEMS.register("module_phase_warp",
            () -> new TitanCoreModuleItem(TitanCoreModuleItem.CoreType.PHASE_WARP, new Item.Properties()));
    public static final RegistryObject<Item> MODULE_SONAR_SCANNER = ITEMS.register("module_sonar_scanner",
            () -> new TitanCoreModuleItem(TitanCoreModuleItem.CoreType.SONAR_SCANNER, new Item.Properties()));

    // Dedicated Frame Beacons for quick deployment
    public static final RegistryObject<Item> TITAN_FRAME_BEACON = ITEMS.register("titan_frame_beacon",
            () -> new TitanFrameBeaconItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> STRIKER_FRAME_BEACON = ITEMS.register("striker_frame_beacon",
            () -> new TitanFrameBeaconItem(com.titancombat.entity.TitanClass.STRIKER_FRAME, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> VANGUARD_FRAME_BEACON = ITEMS.register("vanguard_frame_beacon",
            () -> new TitanFrameBeaconItem(com.titancombat.entity.TitanClass.VANGUARD_FRAME, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> COLOSSUS_FRAME_BEACON = ITEMS.register("colossus_frame_beacon",
            () -> new TitanFrameBeaconItem(com.titancombat.entity.TitanClass.COLOSSUS_FRAME, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> TERRAIN_FRAME_BEACON = ITEMS.register("terrain_frame_beacon",
            () -> new TitanFrameBeaconItem(com.titancombat.entity.TitanClass.TERRAIN_FRAME, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> CYCLOPS_FRAME_BEACON = ITEMS.register("cyclops_frame_beacon",
            () -> new TitanFrameBeaconItem(com.titancombat.entity.TitanClass.CYCLOPS_FRAME, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));
    public static final RegistryObject<Item> SPIDER_FRAME_BEACON = ITEMS.register("spider_frame_beacon",
            () -> new TitanFrameBeaconItem(com.titancombat.entity.TitanClass.SPIDER_FRAME, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final Map<TitanWeapon, RegistryObject<Item>> WEAPON_MODULES = new EnumMap<>(TitanWeapon.class);
    public static final Map<TitanWeapon, RegistryObject<Item>> WEAPON_MAGAZINES = new EnumMap<>(TitanWeapon.class);
    public static final Map<com.titancombat.entity.TitanFlightModule, RegistryObject<Item>> FLIGHT_MODULES =
            new EnumMap<>(com.titancombat.entity.TitanFlightModule.class);

    static {
        for (TitanWeapon weapon : TitanWeapon.values()) {
            WEAPON_MODULES.put(weapon, ITEMS.register("weapon_" + weapon.getId(),
                    () -> new TitanWeaponItem(weapon, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC))));
            WEAPON_MAGAZINES.put(weapon, ITEMS.register("ammo_" + weapon.getId(),
                    () -> new TitanMagazineItem(weapon, new Item.Properties().stacksTo(16).rarity(Rarity.UNCOMMON))));
        }
        for (com.titancombat.entity.TitanFlightModule module : com.titancombat.entity.TitanFlightModule.values()) {
            if (module == com.titancombat.entity.TitanFlightModule.NONE) continue;
            FLIGHT_MODULES.put(module, ITEMS.register("flight_module_" + module.getId(),
                    () -> new TitanFlightModuleItem(module, new Item.Properties().stacksTo(1).rarity(Rarity.RARE))));
        }
    }

    public static void register(IEventBus eventBus) {
        ITEMS.register(eventBus);
    }
}
