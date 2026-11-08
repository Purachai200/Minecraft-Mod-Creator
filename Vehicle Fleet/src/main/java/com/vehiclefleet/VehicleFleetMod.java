package com.vehiclefleet;

import com.mojang.logging.LogUtils;
import com.vehiclefleet.entity.FleetVehicleEntity;
import com.vehiclefleet.entity.FleetVehicleItem;
import com.vehiclefleet.net.FleetNet;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;

import java.util.LinkedHashMap;
import java.util.Map;

@Mod(VehicleFleetMod.MODID)
public class VehicleFleetMod {
    public static final String MODID = "vehiclefleet";
    public static final Logger LOGGER = LogUtils.getLogger();

    public static final DeferredRegister<EntityType<?>> ENTITIES = DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, MODID);
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, MODID);
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, MODID);

    public static final Map<String, RegistryObject<EntityType<FleetVehicleEntity>>> TYPES = new LinkedHashMap<>();
    public static final Map<String, RegistryObject<Item>> VEHICLE_ITEMS = new LinkedHashMap<>();
    public static final RegistryObject<EntityType<com.vehiclefleet.entity.DeckColliderEntity>> DECK_COLLIDER =
            ENTITIES.register("deck_collider", () -> EntityType.Builder.<com.vehiclefleet.entity.DeckColliderEntity>of(com.vehiclefleet.entity.DeckColliderEntity::new, MobCategory.MISC)
                    .sized(1.0F, 1.0F).noSave().noSummon().clientTrackingRange(24).updateInterval(1).build(MODID + ":deck_collider"));

    public static final RegistryObject<Item> CAMO_SPRAY = ITEMS.register("camo_spray",
            () -> new Item(new Item.Properties().stacksTo(1)));

    static {
        for (FleetVehicles.Spec spec : FleetVehicles.all().values()) {
            float w = (float) Math.min(8.0D, Math.max(1.6D, spec.half_width / 8.0D + 0.4D));
            float h = (float) Math.min(4.0D, Math.max(1.5D, spec.height / 16.0D * 0.45D));
            TYPES.put(spec.id, ENTITIES.register(spec.id, () -> EntityType.Builder.<FleetVehicleEntity>of((type, level) -> new FleetVehicleEntity(type, level, spec), MobCategory.MISC)
                    .sized(w, h).clientTrackingRange(24).updateInterval(1).fireImmune().build(MODID + ":" + spec.id)));
            VEHICLE_ITEMS.put(spec.id, ITEMS.register(spec.id, () -> new FleetVehicleItem(spec, new Item.Properties().stacksTo(1))));
        }
        TABS.register("main", () -> CreativeModeTab.builder().title(Component.translatable("itemGroup.vehiclefleet"))
                .icon(() -> new ItemStack(VEHICLE_ITEMS.values().iterator().next().get()))
                .displayItems((params, out) -> {
                    VEHICLE_ITEMS.values().forEach(o -> out.accept(o.get()));
                    out.accept(CAMO_SPRAY.get());
                }).build());
    }

    public VehicleFleetMod() {
        IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();
        ENTITIES.register(bus);
        ITEMS.register(bus);
        TABS.register(bus);
        com.vehiclefleet.sound.FleetSounds.register(bus);
        bus.addListener((FMLCommonSetupEvent e) -> e.enqueueWork(FleetNet::register));
    }
}
