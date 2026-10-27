package com.titancombat.client.renderer;

import com.titancombat.client.model.TransportVehicleModel;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class TransportVehicleRenderer<T extends BaseTransportVehicleEntity> extends GeoEntityRenderer<T> {

    public TransportVehicleRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new TransportVehicleModel<>());
        this.shadowRadius = 2.4F;
    }

    // Vehicles are machines: no red hurt flash and no mob death tip-over
    @Override
    public int getPackedOverlay(T animatable, float u, float partialTick) {
        return OverlayTexture.NO_OVERLAY;
    }

    @Override
    protected float getDeathMaxRotation(T animatable) {
        return 0.0F;
    }

    @Override
    public RenderType getRenderType(T animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
        // Cutout: window panes are alpha-0 texels, so the driver sees out and outsiders see in
        return RenderType.entityCutoutNoCull(texture);
    }
}
