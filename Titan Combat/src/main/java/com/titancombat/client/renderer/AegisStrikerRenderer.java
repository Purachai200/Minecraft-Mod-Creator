package com.titancombat.client.renderer;

import com.titancombat.TitanCombatMod;
import com.titancombat.client.model.AegisStrikerModel;
import com.titancombat.client.renderer.layer.MechFactionColorLayer;
import com.titancombat.entity.AegisStrikerEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;

public class AegisStrikerRenderer extends MobRenderer<AegisStrikerEntity, AegisStrikerModel> {
    private static final ResourceLocation BASE_TEXTURE =
            new ResourceLocation(TitanCombatMod.MODID, "textures/entity/mech/aegis_striker.png");

    public AegisStrikerRenderer(EntityRendererProvider.Context context) {
        super(context, new AegisStrikerModel(context.bakeLayer(AegisStrikerModel.LAYER_LOCATION)), 1.4F);
        this.addLayer(new MechFactionColorLayer(this));
    }

    @Override
    public ResourceLocation getTextureLocation(AegisStrikerEntity entity) {
        return BASE_TEXTURE;
    }
}
