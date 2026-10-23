package com.titancombat.item;

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

    public static final RegistryObject<Item> PAINT_SPRAY_CAN = ITEMS.register("paint_spray_can",
            () -> new PaintSprayCanItem(new Item.Properties().stacksTo(1).durability(64).rarity(Rarity.RARE)));

    public static final RegistryObject<Item> TITAN_BATTERY = ITEMS.register("titan_battery",
            () -> new TitanBatteryItem(new Item.Properties().stacksTo(4).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> EMPTY_BATTERY = ITEMS.register("empty_battery",
            () -> new Item(new Item.Properties().stacksTo(8).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> TITAN_AMMO = ITEMS.register("titan_ammo",
            () -> new TitanAmmoItem(new Item.Properties().stacksTo(64).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> PILOT_LICENSE = ITEMS.register("pilot_license",
            () -> new PilotLicenseItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

    public static final RegistryObject<Item> BLOWTORCH = ITEMS.register("blowtorch",
            () -> new MaintenanceBlowtorchItem(new Item.Properties().stacksTo(1).durability(150).rarity(Rarity.UNCOMMON)));

    public static final RegistryObject<Item> HANGAR_TRANSPONDER = ITEMS.register("hangar_transponder",
            () -> new HangarTransponderItem(new Item.Properties().stacksTo(1).rarity(Rarity.EPIC)));

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

    public static void register(IEventBus eventBus) {
        ITEMS.register(eventBus);
    }
}
