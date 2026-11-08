package com.vehiclefleet.sound;

import com.vehiclefleet.VehicleFleetMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class FleetSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, VehicleFleetMod.MODID);

    public static final RegistryObject<SoundEvent> ROTOR_HELO_HEAVY = registerSoundEvent("vehicle_rotor_helo_heavy");
    public static final RegistryObject<SoundEvent> ROTOR_HELO_LIGHT = registerSoundEvent("vehicle_rotor_helo_light");
    public static final RegistryObject<SoundEvent> ROTOR_HELO_LITTLEBIRD = registerSoundEvent("vehicle_rotor_helo_littlebird");
    public static final RegistryObject<SoundEvent> ROTOR_HELO_APACHE = registerSoundEvent("vehicle_rotor_helo_apache");
    public static final RegistryObject<SoundEvent> ROTOR_HELO_VENOM = registerSoundEvent("vehicle_rotor_helo_venom");
    public static final RegistryObject<SoundEvent> ROTOR_HELO_HAVOC = registerSoundEvent("vehicle_rotor_helo_havoc");
    public static final RegistryObject<SoundEvent> ROTOR_HELO_TIGER = registerSoundEvent("vehicle_rotor_helo_tiger");
    public static final RegistryObject<SoundEvent> ENGINE_JET_HEAVY = registerSoundEvent("vehicle_engine_jet_heavy");
    public static final RegistryObject<SoundEvent> ENGINE_DIESEL_LIGHT = registerSoundEvent("vehicle_engine_diesel_light");
    public static final RegistryObject<SoundEvent> ENGINE_DIESEL_HEAVY = registerSoundEvent("vehicle_engine_diesel_heavy");
    public static final RegistryObject<SoundEvent> ENGINE_SHIP = registerSoundEvent("vehicle_engine_ship");
    public static final RegistryObject<SoundEvent> ENGINE_SUBMARINE = registerSoundEvent("vehicle_engine_submarine");
    public static final RegistryObject<SoundEvent> HORN_TRUCK = registerSoundEvent("vehicle_horn_truck");
    public static final RegistryObject<SoundEvent> HORN_SHIP = registerSoundEvent("vehicle_horn_ship");

    private static RegistryObject<SoundEvent> registerSoundEvent(String name) {
        return SOUND_EVENTS.register(name, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(VehicleFleetMod.MODID, name)));
    }

    public static void register(IEventBus eventBus) {
        SOUND_EVENTS.register(eventBus);
    }
}
