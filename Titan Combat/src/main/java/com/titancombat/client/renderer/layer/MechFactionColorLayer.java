package com.titancombat.client.renderer.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.titancombat.TitanCombatMod;
import com.titancombat.client.model.AegisStrikerModel;
import com.titancombat.entity.AegisStrikerEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

public class MechFactionColorLayer extends RenderLayer<AegisStrikerEntity, AegisStrikerModel> {
    private static final ResourceLocation PAINT_LAYER =
            new ResourceLocation(TitanCombatMod.MODID, "textures/entity/mech/aegis_striker_paint.png");
    private static final ResourceLocation GLOW_LAYER =
            new ResourceLocation(TitanCombatMod.MODID, "textures/entity/mech/aegis_striker_glow.png");

    public MechFactionColorLayer(RenderLayerParent<AegisStrikerEntity, AegisStrikerModel> renderer) {
        super(renderer);
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource buffer, int packedLight, AegisStrikerEntity entity, float limbSwing, float limbSwingAmount, float partialTick, float ageInTicks, float netHeadYaw, float headPitch) {
        // 1. Dynamic Faction Armor Paint Overlay
        int primaryColor = entity.getPrimaryColor();
        float r = ((primaryColor >> 16) & 0xFF) / 255.0F;
        float g = ((primaryColor >> 8) & 0xFF) / 255.0F;
        float b = (primaryColor & 0xFF) / 255.0F;

        VertexConsumer paintConsumer = buffer.getBuffer(RenderType.entityCutoutNoCull(PAINT_LAYER));
        this.getParentModel().renderToBuffer(poseStack, paintConsumer, packedLight, OverlayTexture.NO_OVERLAY, r, g, b, 1.0F);

        // 2. Emissive Cockpit Visor & Thruster Glow (Fullbright)
        int emissiveColor = entity.getSecondaryColor();
        float er = ((emissiveColor >> 16) & 0xFF) / 255.0F;
        float eg = ((emissiveColor >> 8) & 0xFF) / 255.0F;
        float eb = (emissiveColor & 0xFF) / 255.0F;

        VertexConsumer glowConsumer = buffer.getBuffer(RenderType.eyes(GLOW_LAYER));
        this.getParentModel().renderToBuffer(poseStack, glowConsumer, 15728880, OverlayTexture.NO_OVERLAY, er, eg, eb, 1.0F);
    }
}
