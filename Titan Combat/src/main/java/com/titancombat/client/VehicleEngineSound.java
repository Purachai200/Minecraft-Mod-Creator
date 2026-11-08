package com.titancombat.client;

import com.titancombat.entity.transport.*;
import com.titancombat.sound.ModSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

import java.util.Map;
import java.util.WeakHashMap;

/** Looping engine/rotor sound that follows one vehicle; volume and pitch track throttle, flight and speed. */
public class VehicleEngineSound extends AbstractTickableSoundInstance {
    private static final Map<BaseTransportVehicleEntity, VehicleEngineSound> PLAYING = new WeakHashMap<>();

    private final BaseTransportVehicleEntity vehicle;
    private final boolean aircraft;
    private float power; // 0 = engine off, 1 = full power; spools up/down like a real turbine

    private VehicleEngineSound(BaseTransportVehicleEntity vehicle, SoundEvent event, boolean aircraft) {
        super(event, SoundSource.NEUTRAL, SoundInstance.createUnseededRandom());
        this.vehicle = vehicle;
        this.aircraft = aircraft;
        this.looping = true;
        this.delay = 0;
        this.volume = 0.01F;
        this.attenuation = SoundInstance.Attenuation.LINEAR;
        this.x = vehicle.getX();
        this.y = vehicle.getY();
        this.z = vehicle.getZ();
    }

    /** Called every client tick from the vehicle; starts the loop once the engine is running. */
    public static void ensure(BaseTransportVehicleEntity vehicle) {
        if (!isRunning(vehicle)) return;
        VehicleEngineSound s = PLAYING.get(vehicle);
        if (s != null && !s.isStopped()) return;
        s = new VehicleEngineSound(vehicle, eventFor(vehicle), isAircraft(vehicle));
        PLAYING.put(vehicle, s);
        Minecraft.getInstance().getSoundManager().play(s);
    }

    public static boolean anyPlaying() {
        return PLAYING.values().stream().anyMatch(s -> !s.isStopped() && Minecraft.getInstance().getSoundManager().isActive(s));
    }

    private static boolean isAircraft(BaseTransportVehicleEntity v) {
        return v.isAircraft();
    }

    private static boolean isRunning(BaseTransportVehicleEntity v) {
        return v.getControllingPassenger() != null && v.getEnergy() > 0 || (isAircraft(v) && !v.onGround());
    }

    private static SoundEvent eventFor(BaseTransportVehicleEntity v) {
        if (v instanceof TitanChinookTransporterEntity) return ModSounds.VEHICLE_ROTOR_TANDEM.get();
        if (v instanceof TitanV22OspreyEntity) return ModSounds.VEHICLE_ROTOR_TILTROTOR.get();
        if (v instanceof TitanSkyCraneDroneEntity) return ModSounds.VEHICLE_ROTOR_DRONE.get();
        if (v instanceof TitanC130HerculesEntity) return ModSounds.VEHICLE_ENGINE_TURBOPROP.get();
        if (v instanceof TitanLcacHovercraftEntity) return ModSounds.VEHICLE_LIFT_FAN.get();
        if (v instanceof com.titancombat.entity.transport.TitanSkyCarrierEntity) return ModSounds.VEHICLE_LIFT_FAN.get();
        if (v instanceof com.titancombat.entity.transport.BaseShipEntity || v instanceof TitanCargoBargeEntity || v instanceof TitanOceanCarrierEntity) return ModSounds.VEHICLE_ENGINE_SHIP.get();
        if (v instanceof TitanTacticalTruckEntity) return ModSounds.VEHICLE_ENGINE_DIESEL_LIGHT.get();
        return ModSounds.VEHICLE_ENGINE_DIESEL_HEAVY.get();
    }

    @Override
    public void tick() {
        if (this.vehicle.isRemoved()) {
            this.stop();
            return;
        }
        this.x = this.vehicle.getX();
        this.y = this.vehicle.getY();
        this.z = this.vehicle.getZ();

        float speed = Math.min(1.0F, Math.abs(this.vehicle.visSpeed) / 0.8F);
        float target = isRunning(this.vehicle) ? (this.aircraft ? (this.vehicle.onGround() ? 0.65F : 1.0F) : 0.55F + 0.45F * speed) : 0.0F;
        this.power += Mth.clamp(target - this.power, -0.02F, this.aircraft ? 0.015F : 0.04F); // rotors spool slower than diesels
        if (this.power <= 0.0F && target == 0.0F) {
            this.stop();
            return;
        }
        this.volume = (this.aircraft ? 2.2F : 1.4F) * this.power; // >1 widens the linear falloff range
        this.pitch = this.aircraft ? 0.55F + 0.45F * this.power + 0.1F * speed : 0.75F + 0.5F * speed * this.power;
    }
}
