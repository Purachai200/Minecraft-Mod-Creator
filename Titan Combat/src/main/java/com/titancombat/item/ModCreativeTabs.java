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
                        output.accept(ModItems.BULWARK_BEACON.get());
                        output.accept(ModItems.EXO_FRAME_BEACON.get());
                        output.accept(ModItems.TITAN_EXO_BEACON.get());
                        output.accept(ModItems.SERVO_OVERDRIVE_MODULE.get());
                        output.accept(ModItems.REINFORCED_PLATING_MODULE.get());
                        output.accept(ModItems.SHIELD_CAPACITOR_MODULE.get());
                        output.accept(ModItems.NANITE_REPAIR_MODULE.get());
                        output.accept(ModItems.TARGETING_COMPUTER_MODULE.get());
                        output.accept(ModItems.TITAN_FRAME_BEACON.get());
                        output.accept(ModItems.STRIKER_FRAME_BEACON.get());
                        output.accept(ModItems.VANGUARD_FRAME_BEACON.get());
                        output.accept(ModItems.COLOSSUS_FRAME_BEACON.get());
                        output.accept(ModItems.TERRAIN_FRAME_BEACON.get());
                        output.accept(ModItems.CYCLOPS_FRAME_BEACON.get());
                        output.accept(ModItems.SPIDER_FRAME_BEACON.get());
                        // Modular Frame Armor Archetypes (All 17 Theme Variants registered into JEI / Creative Tab)
                        for (com.titancombat.entity.TitanArmorTheme theme : com.titancombat.entity.TitanArmorTheme.values()) {
                            ItemStack head = new ItemStack(ModItems.TITAN_ARMOR_HEAD.get());
                            TitanArmorItem.setTheme(head, theme);
                            output.accept(head);

                            ItemStack chest = new ItemStack(ModItems.TITAN_ARMOR_CHEST.get());
                            TitanArmorItem.setTheme(chest, theme);
                            output.accept(chest);

                            ItemStack arms = new ItemStack(ModItems.TITAN_ARMOR_ARMS.get());
                            TitanArmorItem.setTheme(arms, theme);
                            output.accept(arms);

                            ItemStack legs = new ItemStack(ModItems.TITAN_ARMOR_LEGS.get());
                            TitanArmorItem.setTheme(legs, theme);
                            output.accept(legs);
                        }
                        output.accept(ModItems.MODULE_CLOAKING.get());
                        output.accept(ModItems.MODULE_PHASE_WARP.get());
                        output.accept(ModItems.MODULE_SONAR_SCANNER.get());
                        output.accept(ModItems.HANGAR_TRANSPONDER.get());
                        output.accept(ModItems.PILOT_LICENSE.get());
                        output.accept(ModItems.TRANSPORT_WINCH.get());
                        output.accept(ModItems.VEHICLE_WRENCH.get());
                        output.accept(ModItems.HAULER_TRUCK.get());
                        output.accept(ModItems.CARGO_BARGE.get());
                        output.accept(ModItems.SKYCRANE_DRONE.get());
                        output.accept(ModItems.OCEAN_CARRIER.get());
                        output.accept(ModItems.PATROL_BOAT.get());
                        output.accept(ModItems.PATROL_FRIGATE.get());
                        output.accept(ModItems.SKY_CARRIER.get());
                        output.accept(ModItems.TACTICAL_TRUCK.get());
                        output.accept(ModItems.CHINOOK_TRANSPORTER.get());
                        output.accept(ModItems.V22_OSPREY.get());
                        output.accept(ModItems.ARMORED_APC.get());
                        output.accept(ModItems.LCAC_HOVERCRAFT.get());
                        output.accept(ModItems.C130_HERCULES.get());
                        output.accept(ModItems.REPAIR_TRUCK.get());
                        output.accept(com.titancombat.block.ModBlocks.VEHICLE_ASSEMBLY_BAY.get());
                        output.accept(ModItems.MOBILE_SUIT_TRAILER.get());
                        output.accept(ModBlocks.HANGAR_DOCK.get());

                        // Maintenance & Weaponry
                        output.accept(ModItems.TITAN_BATTERY.get());
                        output.accept(ModItems.HEAVY_TITAN_BATTERY.get());
                        output.accept(ModItems.DENSE_FUSION_BATTERY.get());
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
                        output.accept(ModItems.HOWITZER_MODULE.get());
                        output.accept(ModItems.HOWITZER_SHELLS.get());
                        output.accept(ModItems.HOWITZER_SMOKE_SHELLS.get());
                        output.accept(ModItems.ROCKET_LAUNCHER_MODULE.get());
                        output.accept(ModItems.AMMO_ROCKET_SALVO.get());
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
