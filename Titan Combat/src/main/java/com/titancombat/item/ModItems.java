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
