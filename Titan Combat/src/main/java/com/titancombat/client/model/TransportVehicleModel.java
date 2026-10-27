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
        return "hauler_truck";
    }

    @Override
    public ResourceLocation getModelResource(T animatable) {
        return new ResourceLocation(TitanCombatMod.MODID, "geo/" + getVehicleType(animatable) + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(T animatable) {
        return new ResourceLocation(TitanCombatMod.MODID, "textures/entity/transport/" + getVehicleType(animatable) + ".png");
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

        if (vehicle instanceof TitanHaulerTruckEntity) {
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
                b.setRotZ(b.getRotZ() - roll * 1.5F); // planing hull banks into the turn
                b.setRotX(b.getRotX() + Mth.clamp(speed * 0.06F, -0.05F, 0.07F)); // bow rises under power
            });
        } else if (vehicle instanceof TitanSkyCraneDroneEntity) {
            getBone("fuselage").ifPresent(b -> {
                b.setRotX(-Mth.clamp(speed * 0.18F, -0.12F, 0.2F)); // nose dips to fly forward
                b.setRotZ(-roll * 2.0F);
            });
        }
    }
}
