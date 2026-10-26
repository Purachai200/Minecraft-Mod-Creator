package com.titancombat.client.model;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.titancombat.entity.transport.TitanCargoBargeEntity;
import com.titancombat.entity.transport.TitanHaulerTruckEntity;
import com.titancombat.entity.transport.TitanSkyCraneDroneEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public class TransportVehicleModel<T extends BaseTransportVehicleEntity> extends GeoModel<T> {

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
}
