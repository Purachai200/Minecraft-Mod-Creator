package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;
import software.bernie.geckolib.util.RenderUtils;

import java.util.List;

public class ExoframeFlightBoosterLayer extends GeoRenderLayer<ExoframeEntity> {
    private static final ResourceLocation GEO_RES = new ResourceLocation(ObsoleteMod.MODID, "geo/equipment/flight_booster.geo.json");
    private static final ResourceLocation TEX_RES = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/equipment/flight_booster.png");

    private boolean drawing = false;

    public ExoframeFlightBoosterLayer(GeoRenderer<ExoframeEntity> renderer) {
        super(renderer);
    }

    @Override
    public void renderForBone(PoseStack poseStack, ExoframeEntity exoframe, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                              VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (this.drawing || !exoframe.hasFlightBooster() || exoframe.isInvisible() || !"torso".equals(bone.getName())) {
            return;
        }

        BakedGeoModel model = GeckoLibCache.getBakedModels().get(GEO_RES);
        if (model == null) return;

        this.drawing = true;
        poseStack.pushPose();
        try {
            // Move origin to torso bone's pivot point
            RenderUtils.translateToPivotPoint(poseStack, bone);

            // Mount position: Attached high and clean on the dorsal spine / upper back
            poseStack.translate(0.0D, 3.2D / 16.0D, 5.8D / 16.0D);

            // Scale to match mech proportions
            float scale = 1.0F;
            poseStack.scale(scale, scale, scale);

            // Dynamic vector nozzle gimbal articulation:
            // When flying or boosting: vector nozzles tilt backward dynamically to produce forward thrust!
            boolean activeFlight = exoframe.isFlying();
            boolean boosting = exoframe.isFlightBoosting();

            float nozzlePitch = 0.0F;
            if (boosting) {
                nozzlePitch = 0.42F; // ~24 degrees back
            } else if (activeFlight) {
                float pulse = (float) Math.sin((exoframe.tickCount + partialTick) * 0.2F) * 0.04F;
                nozzlePitch = 0.16F + pulse; // ~10 degrees back with subtle stabilization pulse
            }

            final float finalPitch = nozzlePitch;
            model.getBone("nozzle_left").ifPresent(n -> n.setRotX(finalPitch));
            model.getBone("nozzle_right").ifPresent(n -> n.setRotX(finalPitch));

            RenderType modType = RenderType.entityCutoutNoCull(TEX_RES);
            VertexConsumer modBuffer = bufferSource.getBuffer(modType);

            List<GeoBone> roots = model.topLevelBones();
            if (roots != null && !roots.isEmpty()) {
                for (GeoBone rootBone : roots) {
                    rootBone.setHidden(false);
                    getRenderer().renderRecursively(poseStack, exoframe, rootBone, modType, bufferSource, modBuffer, false, partialTick,
                            packedLight, packedOverlay, 1.0F, 1.0F, 1.0F, 1.0F);
                }
            } else {
                model.getBone("root").or(() -> model.getBone("docking_mount")).ifPresent(b -> {
                    b.setHidden(false);
                    getRenderer().renderRecursively(poseStack, exoframe, b, modType, bufferSource, modBuffer, false, partialTick,
                            packedLight, packedOverlay, 1.0F, 1.0F, 1.0F, 1.0F);
                });
            }
        } finally {
            poseStack.popPose();
            this.drawing = false;
            bufferSource.getBuffer(renderType);
        }
    }
}
