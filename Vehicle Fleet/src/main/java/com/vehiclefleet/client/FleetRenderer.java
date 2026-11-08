package com.vehiclefleet.client;

import com.vehiclefleet.entity.FleetVehicleEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/** Draws the model, then the lamp panels again from <texture>_glowmask.png at full brightness so lamps glow in the dark. */
public class FleetRenderer extends GeoEntityRenderer<FleetVehicleEntity> {
    public FleetRenderer(EntityRendererProvider.Context ctx) {
        super(ctx, new FleetModel());
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
        this.shadowRadius = 0.0F;
    }

    @Override
    public RenderType getRenderType(FleetVehicleEntity animatable, ResourceLocation texture, MultiBufferSource bufferSource, float partialTick) {
        return RenderType.entityTranslucent(texture);
    }
}
