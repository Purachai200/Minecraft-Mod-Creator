package com.titancombat.client.model;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.titancombat.entity.transport.TitanCargoBargeEntity;
import com.titancombat.entity.transport.TitanHaulerTruckEntity;
import com.titancombat.entity.transport.TitanSkyCraneDroneEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

public class TransportVehicleModel<T extends BaseTransportVehicleEntity> extends GeoModel<T> {

    private static final float TRUCK_WHEELBASE = 6.75F;
    private static final float MAX_STEER = (float) Math.toRadians(32.0D);

    private String getVehicleType(T animatable) {
        if (animatable instanceof TitanHaulerTruckEntity) return "hauler_truck";
        if (animatable instanceof TitanCargoBargeEntity) return "cargo_barge";
        if (animatable instanceof TitanSkyCraneDroneEntity) return "skycrane_drone";
        if (animatable instanceof com.titancombat.entity.transport.TitanOceanCarrierEntity) return "ocean_carrier";
        if (animatable instanceof com.titancombat.entity.transport.TitanTacticalTruckEntity) return "tactical_truck";
        if (animatable instanceof com.titancombat.entity.transport.TitanChinookTransporterEntity) return "chinook_transporter";
        if (animatable instanceof com.titancombat.entity.transport.TitanV22OspreyEntity) return "v22_osprey";
        if (animatable instanceof com.titancombat.entity.transport.TitanArmoredApcEntity) return "armored_apc";
        if (animatable instanceof com.titancombat.entity.transport.TitanMobileSuitTrailerEntity) return "mobile_suit_trailer";
        if (animatable instanceof com.titancombat.entity.transport.TitanLcacHovercraftEntity) return "lcac_hovercraft";
        if (animatable instanceof com.titancombat.entity.transport.TitanC130HerculesEntity) return "c130_hercules";
        if (animatable instanceof com.titancombat.entity.transport.TitanRepairTruckEntity) return "repair_truck";
        if (animatable instanceof com.titancombat.entity.transport.TitanPatrolBoatEntity) return "patrol_boat";
        if (animatable instanceof com.titancombat.entity.transport.TitanPatrolFrigateEntity) return "patrol_frigate";
        if (animatable instanceof com.titancombat.entity.transport.TitanSkyCarrierEntity) return "sky_carrier";
        return "hauler_truck";
    }

    @Override
    public ResourceLocation getModelResource(T animatable) {
        return new ResourceLocation(TitanCombatMod.MODID, "geo/" + getVehicleType(animatable) + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(T animatable) {
        return com.titancombat.client.CamoTextures.get(
                new ResourceLocation(TitanCombatMod.MODID, "textures/entity/transport/" + getVehicleType(animatable) + ".png"), animatable.getCamo());
    }

    @Override
    public ResourceLocation getAnimationResource(T animatable) {
        return new ResourceLocation(TitanCombatMod.MODID, "animations/" + getVehicleType(animatable) + ".animation.json");
    }

    /** Wheels, steering and hull lean come from the vehicle's real motion, not looping keyframes. */
    @Override
    public void setCustomAnimations(T vehicle, long instanceId, AnimationState<T> state) {
        float speed = vehicle.visSpeed;
        float yawRateRad = vehicle.visYawRate * Mth.DEG_TO_RAD;
        // Positive bone Z roll lifts the right side, so a left turn (negative yaw rate) rolls the hull outward to the right
        float roll = Mth.clamp(yawRateRad * speed * 6.0F, -0.08F, 0.08F);

        // Dynamic Cargo Straps & Clamping Rig Visibility:
        // If the vehicle currently has no mounted Titans or Exoframes, hide the cargo straps/rig!
        boolean hasCargo = vehicle.hasCargo();
        getBone("cargo_straps").ifPresent(b -> b.setHidden(!hasCargo));
        // Shot-off rotors and props disappear
        boolean wrecked = vehicle.isAircraft() && vehicle.isPropulsionDestroyed();
        for (String r : new String[]{"rotor_front", "rotor_aft", "left_rotor", "right_rotor", "prop_1", "prop_2", "prop_3", "prop_4", "rotor_fl", "rotor_fr", "rotor_rl", "rotor_rr"}) {
            getBone(r).ifPresent(b -> {
                b.setHidden(wrecked);
                b.setChildrenHidden(wrecked); // blades are child bones of the hub
            });
        }

        if (vehicle instanceof TitanHaulerTruckEntity || vehicle instanceof com.titancombat.entity.transport.TitanArmoredApcEntity
                || vehicle instanceof com.titancombat.entity.transport.TitanRepairTruckEntity) { // APC shares the 8x8 wheel/steer bone names
            float spin = -Mth.lerp(state.getPartialTick(), vehicle.wheelRotO, vehicle.wheelRot);
            for (String w : new String[]{"wheel_fl1", "wheel_fr1", "wheel_fl2", "wheel_fr2", "wheel_rl1", "wheel_rr1", "wheel_rl2", "wheel_rr2"}) {
                getBone(w).ifPresent(b -> b.setRotX(spin));
            }
            // Recover the wheel angle from how fast the hull is turning for its speed (bicycle model)
            float steer = Math.abs(speed) < 0.02F ? 0.0F
                    : Mth.clamp((float) Math.atan(yawRateRad * TRUCK_WHEELBASE / speed), -MAX_STEER, MAX_STEER);
            getBone("steer_fl1").ifPresent(b -> b.setRotY(-steer));
            getBone("steer_fr1").ifPresent(b -> b.setRotY(-steer));
            getBone("steer_fl2").ifPresent(b -> b.setRotY(-steer * 0.6F)); // second steering axle turns less, like a real 8x8
            getBone("steer_fr2").ifPresent(b -> b.setRotY(-steer * 0.6F));
            getBone("body").ifPresent(b -> b.setRotZ(roll));
        } else if (vehicle instanceof TitanCargoBargeEntity) {
            getBone("hull").ifPresent(b -> {
                b.setRotZ(-roll * 1.5F); // planing hull banks into the turn
                b.setRotX(Mth.clamp(speed * 0.06F, -0.05F, 0.07F)); // bow rises under power
            });
        } else if (vehicle instanceof TitanSkyCraneDroneEntity) {
            getBone("fuselage").ifPresent(b -> {
                b.setRotX(-Mth.clamp(speed * 0.18F, -0.12F, 0.2F)); // nose dips to fly forward
                b.setRotZ(-roll * 2.0F);
            });
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanTacticalTruckEntity) {
            float spin = -Mth.lerp(state.getPartialTick(), vehicle.wheelRotO, vehicle.wheelRot);
            for (String w : new String[]{"wheel_fl", "wheel_fr", "wheel_rl", "wheel_rr"}) {
                getBone(w).ifPresent(b -> b.setRotX(spin));
            }
            float steer = Math.abs(speed) < 0.02F ? 0.0F
                    : Mth.clamp((float) Math.atan(yawRateRad * 4.0F / speed), -MAX_STEER, MAX_STEER);
            getBone("wheel_fl").ifPresent(b -> b.setRotY(-steer));
            getBone("wheel_fr").ifPresent(b -> b.setRotY(-steer));
            getBone("cab").ifPresent(b -> b.setRotZ(roll * 1.2F));
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanChinookTransporterEntity
                || vehicle instanceof com.titancombat.entity.transport.TitanC130HerculesEntity) {
            getBone("fuselage").ifPresent(b -> {
                b.setRotX(-vehicle.getHullPitch()); // nose dips forward in flight; the pilot's seat tilts the same way
                b.setRotZ(vehicle.getHullRoll());
            });
        } else if (vehicle instanceof com.titancombat.entity.transport.BaseShipEntity
                || vehicle instanceof com.titancombat.entity.transport.TitanOceanCarrierEntity
                || vehicle instanceof com.titancombat.entity.transport.TitanLcacHovercraftEntity) {
            getBone("hull").ifPresent(b -> {
                b.setRotZ(-roll * 1.8F);
                b.setRotX(Mth.clamp(speed * 0.04F, -0.03F, 0.05F));
            });
        }
    }
}
