package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.item.ExoframeFlightBoosterItem;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;
import software.bernie.geckolib.util.RenderUtils;

import java.util.List;

public class ExoframeFlightBoosterLayer extends GeoRenderLayer<ExoframeEntity> {
    private static final ResourceLocation JETPACK_GEO = new ResourceLocation(ObsoleteMod.MODID, "geo/equipment/flight_booster.geo.json");
    private static final ResourceLocation JETPACK_TEX = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/equipment/flight_booster.png");

    private static final ResourceLocation WINGS_GEO = new ResourceLocation(ObsoleteMod.MODID, "geo/equipment/vtol_wings.geo.json");
    private static final ResourceLocation WINGS_TEX = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/equipment/vtol_wings.png");

    private static final ResourceLocation DRONE_GEO = new ResourceLocation(ObsoleteMod.MODID, "geo/equipment/drone_lifter.geo.json");
    private static final ResourceLocation DRONE_TEX = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/equipment/drone_lifter.png");

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

        net.minecraft.client.Minecraft mc = net.minecraft.client.Minecraft.getInstance();
        boolean pilotFirstPerson = mc.options.getCameraType() == net.minecraft.client.CameraType.FIRST_PERSON
                && mc.player != null && mc.player.getVehicle() == exoframe && mc.screen == null;
        if (pilotFirstPerson) {
            return;
        }

        ItemStack backStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.BACK.getIndex());
        ResourceLocation geoRes = JETPACK_GEO;
        ResourceLocation texRes = JETPACK_TEX;
        ExoframeFlightBoosterItem.BoosterType bType = ExoframeFlightBoosterItem.BoosterType.ROCKET_JETPACK;

        if (backStack.getItem() instanceof ExoframeFlightBoosterItem booster) {
            bType = booster.getBoosterType();
            switch (bType) {
                case VTOL_WINGS -> {
                    geoRes = WINGS_GEO;
                    texRes = WINGS_TEX;
                }
                case DRONE_LIFTER -> {
                    geoRes = DRONE_GEO;
                    texRes = DRONE_TEX;
                }
                default -> {
                    geoRes = JETPACK_GEO;
                    texRes = JETPACK_TEX;
                }
            }
        }

        BakedGeoModel model = GeckoLibCache.getBakedModels().get(geoRes);
        if (model == null) return;

        this.drawing = true;
        poseStack.pushPose();
        try {
            RenderUtils.translateToPivotPoint(poseStack, bone);

            // Mount position: Attached high and clean on the dorsal spine / upper back
            poseStack.translate(0.0D, 3.2D / 16.0D, 5.8D / 16.0D);

            float scale = 1.0F;
            poseStack.scale(scale, scale, scale);

            boolean activeFlight = exoframe.isFlying();
            boolean boosting = exoframe.isFlightBoosting();

            if (bType == ExoframeFlightBoosterItem.BoosterType.ROCKET_JETPACK) {
                float nozzlePitch = 0.0F;
                if (boosting) {
                    nozzlePitch = 0.42F; // ~24 degrees back
                } else if (activeFlight) {
                    float pulse = (float) Math.sin((exoframe.tickCount + partialTick) * 0.2F) * 0.04F;
                    nozzlePitch = 0.16F + pulse; // ~10 degrees back
                }
                final float finalPitch = nozzlePitch;
                model.getBone("nozzle_left").ifPresent(n -> n.setRotX(finalPitch));
                model.getBone("nozzle_right").ifPresent(n -> n.setRotX(finalPitch));
            } else if (bType == ExoframeFlightBoosterItem.BoosterType.VTOL_WINGS) {
                float wingSweep = boosting ? 0.35F : (activeFlight ? 0.15F : 0.0F);
                model.getBone("left_wing").ifPresent(w -> w.setRotY(wingSweep));
                model.getBone("right_wing").ifPresent(w -> w.setRotY(-wingSweep));
            } else if (bType == ExoframeFlightBoosterItem.BoosterType.DRONE_LIFTER) {
                float rotorRot = (exoframe.tickCount + partialTick) * (boosting ? 1.4F : (activeFlight ? 0.9F : 0.3F));
                model.getBone("fan_fl").ifPresent(f -> f.setRotY(rotorRot));
                model.getBone("fan_fr").ifPresent(f -> f.setRotY(-rotorRot));
                model.getBone("fan_rl").ifPresent(f -> f.setRotY(-rotorRot));
                model.getBone("fan_rr").ifPresent(f -> f.setRotY(rotorRot));
            }

            RenderType modType = RenderType.entityCutoutNoCull(texRes);
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
