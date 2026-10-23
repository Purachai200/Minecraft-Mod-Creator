package com.titancombat.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.titancombat.client.model.TitanModel;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class TitanRenderer<T extends BaseTitanEntity> extends GeoEntityRenderer<T> {

    public TitanRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new TitanModel<>());
        this.shadowRadius = 1.8F;
    }

    @Override
    public RenderType getRenderType(T animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
        return RenderType.entityCutoutNoCull(texture);
    }

    @Override
    public void render(T entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        Minecraft mc = Minecraft.getInstance();
        // Prevent cockpit camera clipping: In first person, do not render the titan mesh over the pilot's eyes!
        if (mc.options.getCameraType() == CameraType.FIRST_PERSON && mc.player != null && mc.player.getVehicle() == entity) {
            return;
        }
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
    }
}
