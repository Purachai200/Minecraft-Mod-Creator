package com.titancombat.client.renderer;

import com.titancombat.client.model.TransportVehicleModel;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class TransportVehicleRenderer<T extends BaseTransportVehicleEntity> extends GeoEntityRenderer<T> {

    public TransportVehicleRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new TransportVehicleModel<>());
        this.shadowRadius = 2.4F;
    }

    @Override
    public void render(T entity, float entityYaw, float partialTick, com.mojang.blaze3d.vertex.PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        com.titancombat.TitanCombatMod.LOGGER.info(">>> [RENDER VEHICLE] Rendering: {} at {} yaw={} light={}", entity, entity.position(), entityYaw, packedLight);
        super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
    }

    @Override
    public RenderType getRenderType(T animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
        return RenderType.entityCutoutNoCull(texture);
    }
}
