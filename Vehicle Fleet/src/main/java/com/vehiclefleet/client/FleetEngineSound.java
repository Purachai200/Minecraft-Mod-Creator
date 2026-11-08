package com.vehiclefleet.client;

import com.vehiclefleet.entity.FleetVehicleEntity;
import com.vehiclefleet.sound.FleetSounds;
import net.minecraft.client.Minecraft;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;

import java.util.Map;
import java.util.WeakHashMap;

/** Looping engine/rotor sound that follows one vehicle; volume and pitch track throttle, flight and speed. */
public class FleetEngineSound extends AbstractTickableSoundInstance {
    private static final Map<FleetVehicleEntity, FleetEngineSound> PLAYING = new WeakHashMap<>();

    private final FleetVehicleEntity vehicle;
    private final boolean aircraft;
    private float power; // 0 = engine off, 1 = full power; spools up/down like a real turbine

    private FleetEngineSound(FleetVehicleEntity vehicle, SoundEvent event, boolean aircraft) {
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
    public static void ensure(FleetVehicleEntity vehicle) {
        if (!isRunning(vehicle)) return;
        FleetEngineSound s = PLAYING.get(vehicle);
        if (s != null && !s.isStopped()) return;
        s = new FleetEngineSound(vehicle, eventFor(vehicle), isAircraft(vehicle));
        PLAYING.put(vehicle, s);
        Minecraft.getInstance().getSoundManager().play(s);
    }

    public static boolean isAircraft(FleetVehicleEntity v) {
        return v.spec.isAir() || "c17_airlifter".equals(v.spec.id);
    }

    private static boolean isRunning(FleetVehicleEntity v) {
        return v.getControllingPassenger() != null || (isAircraft(v) && !v.onGround()) || (v.spec.isShip() && Math.abs(v.visSpeed) > 0.02F);
    }

    private static SoundEvent eventFor(FleetVehicleEntity v) {
        String id = v.spec.id;
        if ("ah6_littlebird".equals(id)) return FleetSounds.ROTOR_HELO_LITTLEBIRD.get();
        if ("ah64_apache".equals(id) || "comanche".equals(id)) return FleetSounds.ROTOR_HELO_APACHE.get();
        if ("uh1y_venom".equals(id) || "ah1z_viper".equals(id)) return FleetSounds.ROTOR_HELO_VENOM.get();
        if ("mi28_havoc".equals(id)) return FleetSounds.ROTOR_HELO_HAVOC.get();
        if ("ec665_tiger".equals(id)) return FleetSounds.ROTOR_HELO_TIGER.get();
        if ("mi17_hip".equals(id) || "mi26_halo".equals(id)) return FleetSounds.ROTOR_HELO_HEAVY.get();
        if ("uh60_blackhawk".equals(id)) return FleetSounds.ROTOR_HELO_LIGHT.get();
        if ("c17_airlifter".equals(id)) return FleetSounds.ENGINE_JET_HEAVY.get();
        if ("technical_4x4".equals(id) || "humvee_m1165".equals(id)) return FleetSounds.ENGINE_DIESEL_LIGHT.get();
        if ("ural_6x6".equals(id) || "recovery_6x6".equals(id)) return FleetSounds.ENGINE_DIESEL_HEAVY.get();
        if ("transport_sub".equals(id)) return FleetSounds.ENGINE_SUBMARINE.get();
        return FleetSounds.ENGINE_SHIP.get();
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
        this.power += Mth.clamp(target - this.power, -0.02F, this.aircraft ? 0.015F : 0.04F);
        if (this.power <= 0.0F && target == 0.0F) {
            this.stop();
            return;
        }
        this.volume = (this.aircraft ? 2.0F : 1.4F) * this.power;
        this.pitch = this.aircraft ? 0.60F + 0.40F * this.power + 0.1F * speed : 0.75F + 0.45F * speed * this.power;
    }
}
