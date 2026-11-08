package com.vehiclefleet.client;

import com.vehiclefleet.VehicleFleetMod;
import com.vehiclefleet.entity.FleetVehicleEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

public class FleetModel extends GeoModel<FleetVehicleEntity> {
    private static final String[] WHEELS = {
            "wheel_fl", "wheel_fr", "wheel_rl", "wheel_rr", "wheel_ml", "wheel_mr",
            "wheel_nose", "wheel_l", "wheel_r",
            "wheel_ml0", "wheel_ml1", "wheel_ml2", "wheel_mr0", "wheel_mr1", "wheel_mr2"
    };

    @Override
    public ResourceLocation getModelResource(FleetVehicleEntity e) {
        return new ResourceLocation(VehicleFleetMod.MODID, "geo/" + e.spec.id + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(FleetVehicleEntity e) {
        int v = Math.max(0, Math.min(FleetVehicleEntity.LIVERY_SUFFIX.length - 1, e.getVariant()));
        return new ResourceLocation(VehicleFleetMod.MODID, "textures/entity/" + e.spec.id + FleetVehicleEntity.LIVERY_SUFFIX[v] + ".png");
    }

    @Override
    public ResourceLocation getAnimationResource(FleetVehicleEntity e) {
        return new ResourceLocation(VehicleFleetMod.MODID, "animations/" + e.spec.id + ".animation.json");
    }

    @Override
    public void setCustomAnimations(FleetVehicleEntity vehicle, long instanceId, AnimationState<FleetVehicleEntity> state) {
        super.setCustomAnimations(vehicle, instanceId, state);
        float pt = state.getPartialTick();

        // 1. Dynamic Hull Tilt (pitch & roll from acceleration, waves, and aerodynamic banking)
        float roll = vehicle.getHullRoll();
        float pitch = vehicle.getHullPitch();
        getBone("body").ifPresent(b -> {
            b.setRotZ(roll);
            b.setRotX(pitch);
        });
        getBone("hull").ifPresent(b -> {
            b.setRotZ(roll);
            b.setRotX(pitch);
        });
        getBone("fuselage").ifPresent(b -> {
            b.setRotZ(roll);
            b.setRotX(pitch);
        });

        // 2. Ground vehicles: Steering wheels and rolling wheels
        if (vehicle.spec.isGround()) {
            float maxSteerRad = (float) Math.toRadians(34.0D);
            float steerAngle = -vehicle.steer * maxSteerRad; // Negative Y turns left in GeckoLib
            if (steerAngle == 0.0F && Math.abs(vehicle.visSpeed) > 0.02F) {
                float wheelbase = vehicle.spec.id.contains("technical") ? 3.2F : (vehicle.spec.id.contains("humvee") ? 3.6F : 5.8F);
                steerAngle = -Mth.clamp((float) Math.atan(vehicle.visYawRate * Mth.DEG_TO_RAD * wheelbase / vehicle.visSpeed), -maxSteerRad, maxSteerRad);
            }
            final float fSteer = steerAngle;
            getBone("steer_fl").ifPresent(b -> b.setRotY(fSteer));
            getBone("steer_fr").ifPresent(b -> b.setRotY(fSteer));

            float spin = -Mth.lerp(pt, vehicle.wheelRotO, vehicle.wheelRot);
            for (String w : WHEELS) {
                getBone(w).ifPresent(b -> b.setRotX(spin));
            }
        }

        // 3. Aircraft: Rotors and landing gear wheels
        if (vehicle.spec.isAir()) {
            boolean engineActive = vehicle.getControllingPassenger() != null || !vehicle.onGround() || Math.abs(vehicle.visSpeed) > 0.02F;
            if (engineActive) {
                float mainSpin = (vehicle.tickCount + pt) * 45.0F * Mth.DEG_TO_RAD;
                float tailSpin = (vehicle.tickCount + pt) * 60.0F * Mth.DEG_TO_RAD;
                getBone("main_rotor").ifPresent(b -> b.setRotY(mainSpin));
                getBone("tail_rotor").ifPresent(b -> b.setRotX(tailSpin));
            }

            if (vehicle.onGround()) {
                float spin = -Mth.lerp(pt, vehicle.wheelRotO, vehicle.wheelRot);
                for (String w : WHEELS) {
                    getBone(w).ifPresent(b -> b.setRotX(spin));
                }
            }
        }

        // 4. Ships and Submarines: Propellers and radar
        if (vehicle.spec.isShip() || "transport_sub".equals(vehicle.spec.id)) {
            float screwSpin = (vehicle.tickCount + pt) * (float) vehicle.getDeltaMovement().length() * 40.0F * Mth.DEG_TO_RAD;
            getBone("prop").ifPresent(b -> b.setRotZ(screwSpin));
            float radarSpin = (vehicle.tickCount + pt) * 4.0F * Mth.DEG_TO_RAD;
            getBone("radar").ifPresent(b -> b.setRotY(radarSpin));
        }
    }
}
