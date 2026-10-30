package com.obsolete.sound;

import com.obsolete.ObsoleteMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS =
            DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, ObsoleteMod.MODID);

    public static final RegistryObject<SoundEvent> EXOFRAME_STEP = register("exoframe_step");
    public static final RegistryObject<SoundEvent> EXOFRAME_SERVO = register("exoframe_servo");
    public static final RegistryObject<SoundEvent> EXOFRAME_RIFLE_FIRE = register("exoframe_rifle_fire");
    public static final RegistryObject<SoundEvent> EXOFRAME_ROCKET_FIRE = register("exoframe_rocket_fire");
    public static final RegistryObject<SoundEvent> EXOFRAME_MELEE = register("exoframe_melee");
    public static final RegistryObject<SoundEvent> EXOFRAME_ARMOR_BREAK = register("exoframe_armor_break");
    public static final RegistryObject<SoundEvent> EXOFRAME_DEATH = register("exoframe_death");
    public static final RegistryObject<SoundEvent> ASSEMBLY_PROCESS = register("assembly_process");

    private static RegistryObject<SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(ObsoleteMod.MODID, name)));
    }

    public static void register(IEventBus bus) {
        SOUNDS.register(bus);
    }
}
