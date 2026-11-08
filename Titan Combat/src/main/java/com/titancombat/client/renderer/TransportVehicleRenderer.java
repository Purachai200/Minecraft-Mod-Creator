package com.titancombat.client.renderer;

import com.titancombat.client.model.TransportVehicleModel;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

public class TransportVehicleRenderer<T extends BaseTransportVehicleEntity> extends GeoEntityRenderer<T> {

    public TransportVehicleRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new TransportVehicleModel<>());
        this.shadowRadius = 2.4F;
        // PART C: AutoGlowingGeoLayer automatically binds and renders <texture>_glowmask.png with RenderType.eyes full-bright
        this.addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    // Vehicles are machines: no red hurt flash and no mob death tip-over
    @Override
    public int getPackedOverlay(T animatable, float u, float partialTick) {
        return OverlayTexture.NO_OVERLAY;
    }

    /** Faction livery: tint the hull halfway toward the faction colour so texture detail survives; Neutral keeps factory paint. */
    @Override
    public software.bernie.geckolib.core.object.Color getRenderColor(T animatable, float partialTick, int packedLight) {
        com.titancombat.entity.MechFaction faction = animatable.getFaction();
        if (faction == com.titancombat.entity.MechFaction.NEUTRAL) return super.getRenderColor(animatable, partialTick, packedLight);
        int c = faction.getDefaultPrimaryColor();
        return software.bernie.geckolib.core.object.Color.ofRGB(
                (((c >> 16) & 0xFF) + 255) / 2, (((c >> 8) & 0xFF) + 255) / 2, ((c & 0xFF) + 255) / 2);
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

    /** PART C: When camera is inside enclosed decks, clamp block light to min 4 and zero sky light. */
    private int computeInteriorLight(T animatable, int defaultLight) {
        Camera camera = Minecraft.getInstance().gameRenderer.getMainCamera();
        if (camera != null) {
            Vec3 camPos = camera.getPosition();
            if (animatable.isInsideInterior(camPos)) {
                BlockPos pos = BlockPos.containing(camPos);
                int blockLight = Math.max(animatable.level().getBrightness(LightLayer.BLOCK, pos), 4);
                return LightTexture.pack(blockLight, 0);
            }
        }
        return defaultLight;
    }

    @Override
    protected int getBlockLightLevel(T entity, BlockPos pos) {
        if (entity.isInsideInterior(Vec3.atCenterOf(pos))) {
            return Math.max(super.getBlockLightLevel(entity, pos), 4);
        }
        return super.getBlockLightLevel(entity, pos);
    }

    @Override
    public void render(T animatable, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        super.render(animatable, entityYaw, partialTick, poseStack, bufferSource, computeInteriorLight(animatable, packedLight));
    }
}
