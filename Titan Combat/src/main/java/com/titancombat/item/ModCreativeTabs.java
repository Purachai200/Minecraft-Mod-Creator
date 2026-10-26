package com.titancombat.item;

import com.titancombat.TitanCombatMod;
import com.titancombat.block.ModBlocks;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, TitanCombatMod.MODID);

    public static final RegistryObject<CreativeModeTab> TITAN_COMBAT_TAB = CREATIVE_MODE_TABS.register("titan_combat_tab",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.titancombat"))
                    .icon(() -> new ItemStack(ModItems.TITAN_BATTERY.get()))
                    .displayItems((parameters, output) -> {
                        // Deployers & Transponders
                        output.accept(ModItems.TITAN_DROP_BEACON.get());
                        output.accept(ModItems.TROOPER_BEACON.get());
                        output.accept(ModItems.HANGAR_TRANSPONDER.get());
                        output.accept(ModItems.PILOT_LICENSE.get());
                        output.accept(ModItems.TRANSPORT_WINCH.get());
                        output.accept(ModItems.HAULER_TRUCK.get());
                        output.accept(ModItems.CARGO_BARGE.get());
                        output.accept(ModItems.SKYCRANE_DRONE.get());
                        output.accept(ModBlocks.HANGAR_DOCK.get());

                        // Maintenance & Weaponry
                        output.accept(ModItems.TITAN_BATTERY.get());
                        output.accept(ModItems.EMPTY_BATTERY.get());
                        output.accept(ModBlocks.BATTERY_CHARGER.get());
                        output.accept(ModItems.BLOWTORCH.get());
                        output.accept(ModItems.TITAN_AMMO.get());
                        for (com.titancombat.entity.TitanWeapon w : com.titancombat.entity.TitanWeapon.values()) {
                            output.accept(ModItems.WEAPON_MODULES.get(w).get());
                            output.accept(ModItems.WEAPON_MAGAZINES.get(w).get());
                        }
                        for (RegistryObject<net.minecraft.world.item.Item> f : ModItems.FLIGHT_MODULES.values()) {
                            output.accept(f.get());
                        }
                        output.accept(ModItems.PAINT_SPRAY_CAN.get());

                        // Modular Assembly Components
                        output.accept(ModItems.CHASSIS_FRAME.get());
                        output.accept(ModItems.COCKPIT_MODULE.get());
                        output.accept(ModItems.HYDRAULIC_ACTUATOR.get());
                        output.accept(ModItems.FUSION_REACTOR.get());
                        output.accept(ModItems.WEAPON_MOUNT.get());
                    })
                    .build());

    public static void register(IEventBus eventBus) {
        CREATIVE_MODE_TABS.register(eventBus);
    }
}
