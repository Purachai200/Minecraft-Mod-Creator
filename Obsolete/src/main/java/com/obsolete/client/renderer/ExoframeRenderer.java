package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.obsolete.client.model.ExoframeModel;
import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.core.object.Color;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class ExoframeRenderer extends GeoEntityRenderer<ExoframeEntity> {

    /** When true, the client player is riding this exoframe in first-person view. */
    private boolean isFirstPersonPilot = false;

    public ExoframeRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new ExoframeModel());
        withScale(ExoframeEntity.MODEL_SCALE);
        this.shadowRadius = 1.0F * ExoframeEntity.MODEL_SCALE;
        addRenderLayer(new ExoframeFlightBoosterLayer(this));
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
        Minecraft mc = Minecraft.getInstance();
        this.isFirstPersonPilot = mc.options.getCameraType() == CameraType.FIRST_PERSON
                && mc.player != null && mc.player.getVehicle() == entity
                && mc.screen == null;

        poseStack.pushPose();
        try {
            super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
        } finally {
            this.isFirstPersonPilot = false;
        }
        poseStack.popPose();
    }

    @Override
    public void renderCubesOfBone(PoseStack poseStack, GeoBone bone, VertexConsumer buffer, int packedLight, int packedOverlay,
                                  float red, float green, float blue, float alpha) {
        if (this.isFirstPersonPilot && shouldHideCubesInFirstPerson(bone.getName())) {
            // Skip rendering blocking cockpit/head cubes in first person, but still traverse and render arms, hands, and weapons
            return;
        }
        super.renderCubesOfBone(poseStack, bone, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    private boolean shouldHideCubesInFirstPerson(String name) {
        if (name == null) return false;
        if (name.equals("head") || name.equals("torso") || name.equals("pelvis")
                || name.equals("upper_back_seat") || name.equals("backpack")) {
            return true;
        }
        if (name.startsWith("canopy_") || name.startsWith("armor_chest_") || name.startsWith("armor_head_")
                || name.startsWith("sensor_") || name.startsWith("backpack_")) {
            return true;
        }
        if (name.contains("thigh") || name.contains("shin") || name.contains("foot") || name.contains("leg")) {
            return true;
        }
        return false;
    }
}
