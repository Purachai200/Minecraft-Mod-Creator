package com.youjosenki.flight.item;

import com.youjosenki.flight.YoujoSenkiMod;
import com.youjosenki.flight.client.model.FlightUnitModel;
import com.youjosenki.flight.sound.FlightSoundProfile;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModItems {
    public static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, YoujoSenkiMod.MODID);

    // ==========================================
    // FACTION 1: THE EMPIRE (IMPERIAL MAGE UNITS)
    // ==========================================
    // 1. Tanya's Quad-Core Prototype (The Empire) - 1,000,000 FE, Cruising 0.082F, Sprint 1.55x, Ceiling 320m, Boost 1.65x, Rain -15%
    public static final RegistryObject<Item> ELENIUM_TYPE95_FLIGHT_UNIT = ITEMS.register("elenium_type95_flight_unit",
            () -> new EleniumFlightUnitItem(1_000_000, 0.082F, 1.55, 0x262D33,
                    FlightUnitModel.FlightDesign.MAGE_UNIT, FlightSoundProfile.PROTOTYPE_MANA_CORE,
                    320, 1.65F, 1.25F, false, 0.15F, EleniumFlightUnitItem.HudGeneration.MILITARY_STANDARD));

    // 2. 203rd Battalion Mass Production Standard (The Empire) - 500,000 FE, Cruising 0.068F, Sprint 1.38x, Ceiling 200m, Boost 1.40x, Rain -25%
    public static final RegistryObject<Item> ELENIUM_TYPE97_FLIGHT_UNIT = ITEMS.register("elenium_type97_flight_unit",
            () -> new EleniumFlightUnitItem(500_000, 0.068F, 1.38, 0x38444C,
                    FlightUnitModel.FlightDesign.MAGE_UNIT, FlightSoundProfile.VINTAGE_EARLY_MAGE,
                    200, 1.40F, 1.0F, false, 0.25F, EleniumFlightUnitItem.HudGeneration.VINTAGE_ANALOG));

    // ==========================================
    // FACTION 2: ALLIED & EUROPEAN NATIONS
    // ==========================================
    // 3. Allied Francois Republic Aerodynamic Rig - 750,000 FE, Cruising 0.074F, Sprint 1.45x, Ceiling 270m, Boost 1.50x, Rain -15%
    public static final RegistryObject<Item> REPUBLIC_TYPE101_FLIGHT_UNIT = ITEMS.register("republic_type101_flight_unit",
            () -> new EleniumFlightUnitItem(750_000, 0.074F, 1.45, 0x25384D,
                    FlightUnitModel.FlightDesign.TACTICAL_WINGS, FlightSoundProfile.AERODYNAMIC_STREAM,
                    270, 1.50F, 1.15F, false, 0.15F, EleniumFlightUnitItem.HudGeneration.MILITARY_STANDARD));

    // 4. Russy Federation Heavy Armored Rig - 1,500,000 FE, Cruising 0.060F, Sprint 1.30x, Ceiling 190m, Boost 1.30x, Rain -30%
    public static final RegistryObject<Item> FEDERATION_TYPE82_FLIGHT_UNIT = ITEMS.register("federation_type82_flight_unit",
            () -> new EleniumFlightUnitItem(1_500_000, 0.060F, 1.30, 0x5C2424,
                    FlightUnitModel.FlightDesign.HEAVY_ROCKET, FlightSoundProfile.HEAVY_ROCKET_BOOSTER,
                    190, 1.30F, 0.85F, false, 0.30F, EleniumFlightUnitItem.HudGeneration.VINTAGE_ANALOG));

    // 5. Unified States Model 1923 "Eagle" Marine Naval Rig - 850,000 FE, Cruising 0.076F, Sprint 1.48x, Ceiling 240m, Boost 1.52x, WATERPROOF, All-Weather
    public static final RegistryObject<Item> ALLIED_TYPE1923_FLIGHT_UNIT = ITEMS.register("allied_type1923_flight_unit",
            () -> new EleniumFlightUnitItem(850_000, 0.076F, 1.48, 0x6C7A89,
                    FlightUnitModel.FlightDesign.BACK_JETPACK, FlightSoundProfile.MODERN_MILITARY_JET,
                    240, 1.52F, 1.0F, true, 0.00F, EleniumFlightUnitItem.HudGeneration.MILITARY_STANDARD));

    // 6. Commonwealth Royal Mark II "Spitfire" - 650,000 FE, Cruising 0.070F, Sprint 1.40x, Ceiling 220m, Boost 1.42x, Rain -20%
    public static final RegistryObject<Item> COMMONWEALTH_MK2_FLIGHT_UNIT = ITEMS.register("commonwealth_mk2_flight_unit",
            () -> new EleniumFlightUnitItem(650_000, 0.070F, 1.40, 0x5E503F,
                    FlightUnitModel.FlightDesign.MAGE_UNIT, FlightSoundProfile.VINTAGE_EARLY_MAGE,
                    220, 1.42F, 1.0F, false, 0.20F, EleniumFlightUnitItem.HudGeneration.VINTAGE_ANALOG));

    // 7. Legadonia Entente Alliance Alpine Rig - 600,000 FE, Cruising 0.066F, Sprint 1.42x, Ceiling 210m, Boost 1.40x, WATERPROOF, All-Weather
    public static final RegistryObject<Item> ENTENTE_SKIRIG_FLIGHT_UNIT = ITEMS.register("entente_skirig_flight_unit",
            () -> new EleniumFlightUnitItem(600_000, 0.066F, 1.42, 0x3D5A45,
                    FlightUnitModel.FlightDesign.MAGE_UNIT, FlightSoundProfile.VINTAGE_EARLY_MAGE,
                    210, 1.40F, 1.1F, true, 0.00F, EleniumFlightUnitItem.HudGeneration.VINTAGE_ANALOG));

    // ==========================================
    // MODERN & TACTICAL MILITARY JETPACKS
    // ==========================================
    // 8. Tactical Combat Jetpack - 800,000 FE, Cruising 0.072F, Sprint 1.45x, Ceiling 250m, Boost 1.55x, Rain -15%
    public static final RegistryObject<Item> TACTICAL_COMBAT_JETPACK = ITEMS.register("tactical_combat_jetpack",
            () -> new EleniumFlightUnitItem(800_000, 0.072F, 1.45, 0x4D5838,
                    FlightUnitModel.FlightDesign.BACK_JETPACK, FlightSoundProfile.MODERN_MILITARY_JET,
                    250, 1.55F, 1.15F, false, 0.15F, EleniumFlightUnitItem.HudGeneration.MILITARY_STANDARD));

    // 9. Titan Heavy Industrial Rocket Rig - 2,500,000 FE, Cruising 0.056F, Sprint 1.25x, Ceiling 180m, Boost 1.25x, Rain -35%
    public static final RegistryObject<Item> HEAVY_INDUSTRIAL_ROCKET_PACK = ITEMS.register("heavy_industrial_rocket_pack",
            () -> new EleniumFlightUnitItem(2_500_000, 0.056F, 1.25, 0xD4A017,
                    FlightUnitModel.FlightDesign.HEAVY_ROCKET, FlightSoundProfile.HEAVY_ROCKET_BOOSTER,
                    180, 1.25F, 0.8F, false, 0.35F, EleniumFlightUnitItem.HudGeneration.VINTAGE_ANALOG));

    // 10. Shadow Recon Apex Delta-Wings - 1,000,000 FE, Cruising 0.084F, Sprint 1.62x, Ceiling 340m, Boost 1.72x, WATERPROOF, All-Weather
    public static final RegistryObject<Item> SHADOW_RECON_WINGS = ITEMS.register("shadow_recon_wings",
            () -> new EleniumFlightUnitItem(1_000_000, 0.084F, 1.62, 0x1C1F24,
                    FlightUnitModel.FlightDesign.TACTICAL_WINGS, FlightSoundProfile.STEALTH_RECON_WHISPER,
                    340, 1.72F, 1.3F, true, 0.00F, EleniumFlightUnitItem.HudGeneration.ADVANCED_DIGITAL));

    // ==========================================
    // ADVANCED EXPERIMENTAL & HEAVY SIEGE RIGS
    // ==========================================
    // 11. Imperial Elenium Type 95 Synchronized Exoskeleton - 2,000,000 FE, Cruising 0.086F, Sprint 1.68x, Ceiling 380m, Boost 1.85x, WATERPROOF, All-Weather
    public static final RegistryObject<Item> ELENIUM_TYPE95_EXO = ITEMS.register("elenium_type95_exo",
            () -> new EleniumFlightUnitItem(2_000_000, 0.086F, 1.68, 0x22303A,
                    FlightUnitModel.FlightDesign.TWIN_DRIVE_EXO, FlightSoundProfile.PROTOTYPE_MANA_CORE,
                    380, 1.85F, 1.4F, true, 0.00F, EleniumFlightUnitItem.HudGeneration.ADVANCED_DIGITAL));

    // 12. Titan Mk-II "Juggernaut" Heavy Siege Rig - 3,500,000 FE, Cruising 0.064F, Sprint 1.35x, Ceiling 220m, Boost 1.45x, Rain -30%
    public static final RegistryObject<Item> TITAN_SIEGE_FRAME = ITEMS.register("titan_siege_frame",
            () -> new EleniumFlightUnitItem(3_500_000, 0.064F, 1.35, 0x483C32,
                    FlightUnitModel.FlightDesign.SIEGE_ARTILLERY, FlightSoundProfile.HEAVY_ROCKET_BOOSTER,
                    220, 1.45F, 0.9F, false, 0.30F, EleniumFlightUnitItem.HudGeneration.MILITARY_STANDARD));

    // ==========================================
    // TACTICAL KINETIC HOVER & GROUND DASH GEAR
    // ==========================================
    // 13. Valkyrie Kinetic Hover-Thrust Boots - 600,000 FE, Cruising 0.078F, Sprint 1.70x, Ceiling 110m (Low altitude), Boost 1.90x (High-response dash), Cooling 1.4F, WATERPROOF, All-Weather, High Ground Locomotion
    public static final RegistryObject<Item> VALKYRIE_THRUST_BOOTS = ITEMS.register("valkyrie_thrust_boots",
            () -> new EleniumFlightUnitItem(600_000, 0.078F, 1.70, 0x4A6984,
                    FlightUnitModel.FlightDesign.THRUST_BOOTS, FlightSoundProfile.MODERN_MILITARY_JET,
                    110, 1.90F, 1.4F, true, 0.00F, EleniumFlightUnitItem.HudGeneration.ADVANCED_DIGITAL));
}
