package com.obsolete.item;

import com.obsolete.ObsoleteMod;
import com.obsolete.block.ModBlocks;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ObsoleteMod.MODID);

    public static final RegistryObject<CreativeModeTab> OBSOLETE_TAB =
            CREATIVE_MODE_TABS.register("obsolete_tab", () ->
                    CreativeModeTab.builder()
                            .title(Component.translatable("itemGroup.obsolete"))
                            .icon(() -> new ItemStack(ModItems.EXOFRAME_KIT.get()))
                            .displayItems((parameters, output) -> {
                                output.accept(ModItems.EXOFRAME_KIT.get());
                                output.accept(ModItems.EXOFRAME_KIT_SALVAGE.get());
                                output.accept(ModItems.EXOFRAME_KIT_ADVANCED.get());
                                output.accept(ModItems.EXOFRAME_KIT_ELITE.get());
                                output.accept(ModBlocks.MECH_ASSEMBLY_STATION.get());

                                // 1. Outcast Sand PMC Set
                                output.accept(ModItems.ARMOR_SAND_HEAD.get());
                                output.accept(ModItems.ARMOR_SAND_CHEST.get());
                                output.accept(ModItems.ARMOR_SAND_ARMS.get());
                                output.accept(ModItems.ARMOR_SAND_LEGS.get());

                                // 2. USMC Recon Set (Olive Drab - Image 1 & 3)
                                output.accept(ModItems.ARMOR_USMC_HEAD.get());
                                output.accept(ModItems.ARMOR_USMC_CHEST.get());
                                output.accept(ModItems.ARMOR_USMC_ARMS.get());
                                output.accept(ModItems.ARMOR_USMC_LEGS.get());
                                output.accept(ModItems.MODULE_USMC_COMMS.get());

                                // 3. Cerberus PMC Black Ops Set (Image 2)
                                output.accept(ModItems.ARMOR_CERBERUS_HEAD.get());
                                output.accept(ModItems.ARMOR_CERBERUS_CHEST.get());
                                output.accept(ModItems.ARMOR_CERBERUS_ARMS.get());
                                output.accept(ModItems.ARMOR_CERBERUS_LEGS.get());
                                output.accept(ModItems.MODULE_CERBERUS_PACKS.get());

                                // 4. VOTOMS & Militia Guerrilla Sets (Image 4 & 5)
                                output.accept(ModItems.ARMOR_VOTOMS_HEAD.get());
                                output.accept(ModItems.ARMOR_RED_SHOULDER_ARMS.get());
                                output.accept(ModItems.MODULE_SHOULDER_MISSILE.get());
                                output.accept(ModItems.ARMOR_MILITIA_HOOD.get());
                                output.accept(ModItems.ARMOR_MILITIA_CHEST.get());
                                output.accept(ModItems.ARMOR_ARCTIC_CHEST.get());
                                output.accept(ModItems.ARMOR_POLAR_HEAD.get());
                                output.accept(ModItems.ARMOR_POLAR_ARMS.get());
                                output.accept(ModItems.ARMOR_POLAR_LEGS.get());
                                output.accept(ModItems.MODULE_TWIN_MANPADS.get());
                                output.accept(ModItems.ARMOR_OUTLANDER_ARMS.get());
                                output.accept(ModItems.ARMOR_OUTLANDER_LEGS.get());

                                // 5. Civilian Industrial Roll Cage
                                output.accept(ModItems.ARMOR_ROLL_CAGE.get());

                                // 5B. 6 New Faction Armor Sets
                                // Salvage Militia
                                output.accept(ModItems.ARMOR_SALVAGE_HEAD.get());
                                output.accept(ModItems.ARMOR_SALVAGE_CHEST.get());
                                output.accept(ModItems.ARMOR_SALVAGE_ARMS.get());
                                output.accept(ModItems.ARMOR_SALVAGE_LEGS.get());
                                output.accept(ModItems.MODULE_SALVAGE_SCRAPS.get());

                                // Shiden Corps
                                output.accept(ModItems.ARMOR_SHIDEN_HEAD.get());
                                output.accept(ModItems.ARMOR_SHIDEN_CHEST.get());
                                output.accept(ModItems.ARMOR_SHIDEN_ARMS.get());
                                output.accept(ModItems.ARMOR_SHIDEN_LEGS.get());
                                output.accept(ModItems.MODULE_SHIDEN_CREST.get());

                                // Khamsin Long-Range Guard
                                output.accept(ModItems.ARMOR_KHAMSIN_HEAD.get());
                                output.accept(ModItems.ARMOR_KHAMSIN_CHEST.get());
                                output.accept(ModItems.ARMOR_KHAMSIN_ARMS.get());
                                output.accept(ModItems.ARMOR_KHAMSIN_LEGS.get());
                                output.accept(ModItems.MODULE_KHAMSIN_FILTERS.get());

                                // Riverine Corps
                                output.accept(ModItems.ARMOR_RIVERINE_HEAD.get());
                                output.accept(ModItems.ARMOR_RIVERINE_CHEST.get());
                                output.accept(ModItems.ARMOR_RIVERINE_ARMS.get());
                                output.accept(ModItems.ARMOR_RIVERINE_LEGS.get());
                                output.accept(ModItems.MODULE_RIVERINE_SNORKEL.get());

                                // Specter Stealth PMC
                                output.accept(ModItems.ARMOR_SPECTER_HEAD.get());
                                output.accept(ModItems.ARMOR_SPECTER_CHEST.get());
                                output.accept(ModItems.ARMOR_SPECTER_ARMS.get());
                                output.accept(ModItems.ARMOR_SPECTER_LEGS.get());
                                output.accept(ModItems.MODULE_SPECTER_ECM.get());

                                // Valkyrie Special Forces
                                output.accept(ModItems.ARMOR_VALKYRIE_HEAD.get());
                                output.accept(ModItems.ARMOR_VALKYRIE_CHEST.get());
                                output.accept(ModItems.ARMOR_VALKYRIE_ARMS.get());
                                output.accept(ModItems.ARMOR_VALKYRIE_LEGS.get());
                                output.accept(ModItems.MODULE_VALKYRIE_SENSOR.get());

                                // 6. Modular Role Telemetry Modules
                                output.accept(ModItems.MODULE_GEOLOGICAL_SCANNER.get());
                                output.accept(ModItems.MODULE_NIGHT_VISION_OPTIC.get());
                                output.accept(ModItems.MODULE_CARGO_CRATE.get());
                                output.accept(ModItems.MODULE_AGRI_HOPPER.get());
                                output.accept(ModItems.MODULE_DIVING_BALLAST.get());
                                output.accept(ModItems.MODULE_TARGETING_COMPUTER.get());
                                output.accept(ModItems.MODULE_FLIGHT_BOOSTER.get());
                                output.accept(ModItems.MODULE_VTOL_WINGS.get());
                                output.accept(ModItems.MODULE_DRONE_LIFTER.get());
                                output.accept(ModItems.MODULE_ACTIVE_CLOAK.get());
                                output.accept(ModItems.MODULE_ROLLER_DASH.get());
                                output.accept(ModItems.MODULE_HYDRO_JET.get());

                                // 7. Working Tools
                                output.accept(ModItems.TOOL_MINING_DRILL.get());
                                output.accept(ModItems.TOOL_CHAINSAW.get());
                                output.accept(ModItems.TOOL_CULTIVATOR_PLOW.get());

                                // 8. Tactical Weapons
                                output.accept(ModItems.EXOFRAME_ASSAULT_RIFLE.get());
                                output.accept(ModItems.EXOFRAME_SNIPER_RIFLE.get());
                                output.accept(ModItems.EXOFRAME_MACHINE_GUN.get());
                                output.accept(ModItems.EXOFRAME_MINIGUN.get());
                                output.accept(ModItems.EXOFRAME_ROCKET_LAUNCHER.get());
                                output.accept(ModItems.EXOFRAME_RPG7.get());
                                output.accept(ModItems.EXOFRAME_BATTLE_RIFLE.get());
                                output.accept(ModItems.EXOFRAME_AUTOCANNON_30MM.get());
                                output.accept(ModItems.EXOFRAME_SHOTGUN_BREACHER.get());
                                output.accept(ModItems.EXOFRAME_GRENADE_LAUNCHER.get());
                                output.accept(ModItems.EXOFRAME_RECOILLESS_RIFLE.get());
                                output.accept(ModItems.EXOFRAME_ATGM_GUIDED.get());
                                output.accept(ModItems.EXOFRAME_FLAMETHROWER.get());
                                output.accept(ModItems.EXOFRAME_VIBRO_BLADE.get());
                                output.accept(ModItems.EXOFRAME_ANTITANK_RIFLE.get());
                                output.accept(ModItems.EXOFRAME_PILE_BUNKER.get());
                                output.accept(ModItems.EXOFRAME_SMOKE_LAUNCHER.get());

                                // Role Variants
                                output.accept(ModItems.ARMOR_POLICE_HEAD.get());
                                output.accept(ModItems.ARMOR_POLICE_CHEST.get());
                                output.accept(ModItems.EXOFRAME_RIOT_SHIELD.get());
                                output.accept(ModItems.EXOFRAME_STUN_BATON.get());
                                output.accept(ModItems.ARMOR_RESCUE_HEAD.get());
                                output.accept(ModItems.ARMOR_RESCUE_CHEST.get());
                                output.accept(ModItems.MODULE_RESCUE_WINCH.get());
                                output.accept(ModItems.ARMOR_FLOAT_RING.get());
                                output.accept(ModItems.MODULE_SEARCH_RADAR.get());
                                output.accept(ModItems.EXOFRAME_FISHING_ROD.get());

                                // 9. Ammunition
                                output.accept(ModItems.AMMO_20MM.get());
                                output.accept(ModItems.AMMO_762_MINIGUN.get());
                                output.accept(ModItems.AMMO_ROCKET.get());
                                output.accept(ModItems.AMMO_RPG_WARHEAD.get());
                                output.accept(ModItems.AMMO_30MM_AUTOCANNON.get());
                                output.accept(ModItems.AMMO_SHOTGUN_SLUG.get());
                                output.accept(ModItems.AMMO_40MM_GRENADE.get());
                                output.accept(ModItems.AMMO_84MM_ROCKET.get());
                                output.accept(ModItems.AMMO_ATGM_MISSILE.get());
                                output.accept(ModItems.AMMO_NAPALM_CANISTER.get());

                                // 9. Crafting Components
                                output.accept(ModItems.PEDDLER_CORE.get());
                                output.accept(ModItems.HYDRAULIC_CYLINDER.get());
                                output.accept(ModItems.SERVO_MOTOR.get());
                                output.accept(ModItems.REINFORCED_STEEL_PLATE.get());
                            })
                            .build());

    public static void register(IEventBus eventBus) {
        CREATIVE_MODE_TABS.register(eventBus);
    }
}
