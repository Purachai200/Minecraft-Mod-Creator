package com.titancombat.sound;

import com.titancombat.TitanCombatMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUND_EVENTS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, TitanCombatMod.MODID);

    public static final RegistryObject<SoundEvent> TITAN_GET_BATTERY = registerSoundEvent("titan_get_battery");
    public static final RegistryObject<SoundEvent> ION_FIRE = registerSoundEvent("ion_fire");
    public static final RegistryObject<SoundEvent> ION_RELOAD = registerSoundEvent("ion_reload");

    public static final RegistryObject<SoundEvent> TITAN_STEP = registerSoundEvent("titan_step");
    public static final RegistryObject<SoundEvent> TITAN_DASH = registerSoundEvent("titan_dash");
    public static final RegistryObject<SoundEvent> TITAN_CABIN_ENTER = registerSoundEvent("titan_cabin_enter");
    public static final RegistryObject<SoundEvent> TITAN_CABIN_EXIT = registerSoundEvent("titan_cabin_exit");

    public static final RegistryObject<SoundEvent> TITAN_MELEE = registerSoundEvent("titan_melee");
    public static final RegistryObject<SoundEvent> TITAN_MELEE_IMPACT = registerSoundEvent("titan_melee_impact");
    public static final RegistryObject<SoundEvent> RONIN_SWORD = registerSoundEvent("ronin_sword");
    public static final RegistryObject<SoundEvent> RONIN_SWORD_IMPACT = registerSoundEvent("ronin_sword_impact");

    public static final RegistryObject<SoundEvent> SCORCH_FIRE = registerSoundEvent("scorch_fire");
    public static final RegistryObject<SoundEvent> TONE_FIRE = registerSoundEvent("tone_fire");
    public static final RegistryObject<SoundEvent> RONIN_FIRE = registerSoundEvent("ronin_fire");
    public static final RegistryObject<SoundEvent> MONARCH_FIRE = registerSoundEvent("monarch_fire");
    public static final RegistryObject<SoundEvent> LEGION_FIRE = registerSoundEvent("legion_fire");
    public static final RegistryObject<SoundEvent> NORTHSTAR_FIRE = registerSoundEvent("northstar_fire");

    private static RegistryObject<SoundEvent> registerSoundEvent(String name) {
        return SOUND_EVENTS.register(name, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(TitanCombatMod.MODID, name)));
    }

    public static void register(IEventBus eventBus) {
        SOUND_EVENTS.register(eventBus);
    }
}
