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

    // Chassis & Locomotion
    public static final RegistryObject<SoundEvent> EXOFRAME_STEP = register("exoframe_step");
    public static final RegistryObject<SoundEvent> EXOFRAME_STEP_SPRINT = register("exoframe_step_sprint");
    public static final RegistryObject<SoundEvent> EXOFRAME_SERVO = register("exoframe_servo");
    public static final RegistryObject<SoundEvent> EXOFRAME_ENGINE_IDLE = register("exoframe_engine_idle");
    public static final RegistryObject<SoundEvent> EXOFRAME_LAND = register("exoframe_land");
    public static final RegistryObject<SoundEvent> EXOFRAME_LAND_HEAVY = register("exoframe_land_heavy");

    // Cockpit & Boarding
    public static final RegistryObject<SoundEvent> EXOFRAME_COCKPIT_OPEN = register("exoframe_cockpit_open");
    public static final RegistryObject<SoundEvent> EXOFRAME_COCKPIT_CLOSE = register("exoframe_cockpit_close");
    public static final RegistryObject<SoundEvent> EXOFRAME_PILOT_MOUNT = register("exoframe_pilot_mount");
    public static final RegistryObject<SoundEvent> EXOFRAME_PILOT_DISMOUNT = register("exoframe_pilot_dismount");
    public static final RegistryObject<SoundEvent> EXOFRAME_ALARM_LOW_HULL = register("exoframe_alarm_low_hull");

    // Ballistic & Heavy Weapons
    public static final RegistryObject<SoundEvent> EXOFRAME_RIFLE_FIRE = register("exoframe_rifle_fire");
    public static final RegistryObject<SoundEvent> WEAPON_SNIPER_FIRE = register("weapon_sniper_fire");
    public static final RegistryObject<SoundEvent> WEAPON_AUTOCANNON_FIRE = register("weapon_autocannon_fire");
    public static final RegistryObject<SoundEvent> WEAPON_MINIGUN_SPINUP = register("weapon_minigun_spinup");
    public static final RegistryObject<SoundEvent> WEAPON_MINIGUN_FIRE = register("weapon_minigun_fire");
    public static final RegistryObject<SoundEvent> WEAPON_MINIGUN_SPINDOWN = register("weapon_minigun_spindown");
    public static final RegistryObject<SoundEvent> WEAPON_SHOTGUN_FIRE = register("weapon_shotgun_fire");
    public static final RegistryObject<SoundEvent> WEAPON_GRENADE_THUMP = register("weapon_grenade_thump");
    public static final RegistryObject<SoundEvent> EXOFRAME_ROCKET_FIRE = register("exoframe_rocket_fire");
    public static final RegistryObject<SoundEvent> WEAPON_RECOILLESS_FIRE = register("weapon_recoilless_fire");
    public static final RegistryObject<SoundEvent> WEAPON_FLAMETHROWER_FIRE = register("weapon_flamethrower_fire");

    // Melee & Tactical
    public static final RegistryObject<SoundEvent> EXOFRAME_MELEE = register("exoframe_melee");
    public static final RegistryObject<SoundEvent> WEAPON_BLADE_SWING = register("weapon_blade_swing");
    public static final RegistryObject<SoundEvent> WEAPON_BLADE_IMPACT = register("weapon_blade_impact");
    public static final RegistryObject<SoundEvent> WEAPON_MELEE_IMPACT = register("weapon_melee_impact");
    public static final RegistryObject<SoundEvent> WEAPON_STUN_ZAP = register("weapon_stun_zap");

    // Handling & Impact
    public static final RegistryObject<SoundEvent> WEAPON_EMPTY_CLICK = register("weapon_empty_click");
    public static final RegistryObject<SoundEvent> WEAPON_RELOAD = register("weapon_reload");
    public static final RegistryObject<SoundEvent> WEAPON_IMPACT_METAL = register("weapon_impact_metal");
    public static final RegistryObject<SoundEvent> EXOFRAME_ARMOR_BREAK = register("exoframe_armor_break");
    public static final RegistryObject<SoundEvent> EXOFRAME_DEATH = register("exoframe_death");

    // Workstation
    public static final RegistryObject<SoundEvent> ASSEMBLY_PROCESS = register("assembly_process");

    private static RegistryObject<SoundEvent> register(String name) {
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(new ResourceLocation(ObsoleteMod.MODID, name)));
    }

    public static void register(IEventBus bus) {
        SOUNDS.register(bus);
    }
}
