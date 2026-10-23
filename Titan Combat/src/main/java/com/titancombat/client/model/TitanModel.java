package com.titancombat.client.model;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public class TitanModel<T extends BaseTitanEntity> extends GeoModel<T> {

    @Override
    public ResourceLocation getModelResource(T animatable) {
        String id = animatable.getTitanClass().getId();
        return new ResourceLocation(TitanCombatMod.MODID, "geo/" + id + "_titan.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(T animatable) {
        String id = animatable.getTitanClass().getId();
        int camo = animatable.getCamoIndex();
        if (camo <= 0) {
            return new ResourceLocation(TitanCombatMod.MODID, "textures/entity/titan/" + id + "/" + id + "_titan.png");
        }
        return new ResourceLocation(TitanCombatMod.MODID, "textures/entity/titan/" + id + "/" + id + "_titan_" + camo + ".png");
    }

    @Override
    public ResourceLocation getAnimationResource(T animatable) {
        String id = animatable.getTitanClass().getId();
        return new ResourceLocation(TitanCombatMod.MODID, "animations/" + id + "_titan.animation.json");
    }
}
