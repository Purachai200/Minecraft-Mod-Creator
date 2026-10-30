package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.obsolete.client.model.ExoframeModel;
import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.core.object.Color;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class ExoframeRenderer extends GeoEntityRenderer<ExoframeEntity> {

    public ExoframeRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new ExoframeModel());
        withScale(ExoframeEntity.MODEL_SCALE);
        this.shadowRadius = 1.0F * ExoframeEntity.MODEL_SCALE;
    }

    @Override
    public RenderType getRenderType(ExoframeEntity animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
        return RenderType.entityCutoutNoCull(texture);
    }

    @Override
    public Color getRenderColor(ExoframeEntity animatable, float partialTick, int packedLight) {
        int color = animatable.getPrimaryColor();
        if (color == 0xFFFFFF) {
            return Color.WHITE;
        }
        float r = ((color >> 16) & 0xFF) / 255.0F;
        float g = ((color >> 8) & 0xFF) / 255.0F;
        float b = (color & 0xFF) / 255.0F;
        return Color.ofRGBA(r, g, b, 1.0F);
    }

    @Override
    public void render(ExoframeEntity entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        poseStack.pushPose();
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
        poseStack.popPose();
    }
}
