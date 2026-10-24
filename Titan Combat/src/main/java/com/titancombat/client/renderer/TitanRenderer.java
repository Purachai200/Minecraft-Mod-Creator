package com.titancombat.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.titancombat.client.model.TitanModel;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

public class TitanRenderer<T extends BaseTitanEntity> extends GeoEntityRenderer<T> {
    /** Titans keep animating (and stomping) out to this distance even when off-screen. */
    private static final double ANIMATE_RANGE_SQR = 64.0D * 64.0D;

    /** Set while a GUI (cockpit bay preview) draws the titan: always draw, even from inside the cockpit. */
    public static boolean forceDraw = false;

    /** True when this frame should advance animations (footstep keyframes) without drawing anything. */
    private boolean animateOnly = false;

    public TitanRenderer(EntityRendererProvider.Context renderManager) {
        super(renderManager, new TitanModel<>());
        this.shadowRadius = 1.8F;
        addRenderLayer(new com.titancombat.client.renderer.layer.TitanWeaponSwapLayer<>(this));
        addRenderLayer(new com.titancombat.client.renderer.layer.TitanFlightModuleLayer<>(this));
    }

    @Override
    public RenderType getRenderType(T animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
        return RenderType.entityCutoutNoCull(texture);
    }

    /** Pose at the entity's origin this frame; layers use it to turn bone-space points into entity-relative ones. */
    public Matrix4f getEntityRenderTranslations() {
        return this.entityRenderTranslations;
    }

    @Override
    public boolean shouldRender(T entity, Frustum frustum, double camX, double camY, double camZ) {
        // GeckoLib only runs animations (and their footstep sound keyframes) for entities it renders,
        // so a titan walking behind you would go silent. Keep nearby titans "rendering", but only
        // actually draw the ones in view.
        boolean visible = super.shouldRender(entity, frustum, camX, camY, camZ);
        boolean near = entity.distanceToSqr(camX, camY, camZ) < ANIMATE_RANGE_SQR;
        this.animateOnly = !visible;
        return visible || near;
    }

    @Override
    public void render(T entity, float entityYaw, float partialTick, PoseStack poseStack, MultiBufferSource bufferSource, int packedLight) {
        Minecraft mc = Minecraft.getInstance();
        // From the cockpit the hull would cover the camera; the first-person cockpit view draws instead.
        boolean pilotView = !forceDraw && mc.options.getCameraType() == CameraType.FIRST_PERSON && mc.player != null && mc.player.getVehicle() == entity;
        boolean offscreen = !forceDraw && this.animateOnly;
        this.animateOnly = offscreen || pilotView;
        poseStack.pushPose();
        // Eased step-up/step-down so the chassis climbs a block instead of teleporting.
        poseStack.translate(0.0D, entity.getStepOffset(partialTick), 0.0D);
        try {
            super.render(entity, entityYaw, partialTick, poseStack, bufferSource, packedLight);
        } finally {
            this.animateOnly = false;
        }
        if (!offscreen && !forceDraw && entity.isDefenseActive()) {
            renderBarrier(entity, partialTick, poseStack, bufferSource);
        }
        poseStack.popPose();
    }

    private static final ResourceLocation BARRIER_TEXTURE = new ResourceLocation("textures/entity/creeper/creeper_armor.png");
    private static final int BARRIER_LAT = 14;
    private static final int BARRIER_LON = 28;

    /** Defense Matrix: a pulsing blue energy dome around the whole chassis (visible from the cockpit too). */
    private void renderBarrier(T entity, float partialTick, PoseStack poseStack, MultiBufferSource buffers) {
        float time = entity.tickCount + partialTick;
        float scroll = (time * 0.012F) % 1.0F;
        VertexConsumer vc = buffers.getBuffer(RenderType.energySwirl(BARRIER_TEXTURE, scroll, scroll * 0.6F));
        float pulse = 0.75F + 0.25F * Mth.sin(time * 0.25F);
        float r = 0.18F * pulse, g = 0.55F * pulse, b = 1.0F * pulse;

        boolean kneeling = entity.isKneeling();
        float radiusH = kneeling ? 3.6F : 4.2F;
        float radiusV = kneeling ? 3.4F : 4.6F;
        float centerY = kneeling ? 2.6F : 3.7F;

        poseStack.pushPose();
        poseStack.translate(0.0D, centerY, 0.0D);
        Matrix4f pose = poseStack.last().pose();
        Matrix3f normal = poseStack.last().normal();
        for (int i = 0; i < BARRIER_LAT; i++) {
            float t0 = (float) Math.PI * i / BARRIER_LAT, t1 = (float) Math.PI * (i + 1) / BARRIER_LAT;
            for (int j = 0; j < BARRIER_LON; j++) {
                float p0 = (float) (Math.PI * 2) * j / BARRIER_LON, p1 = (float) (Math.PI * 2) * (j + 1) / BARRIER_LON;
                barrierVertex(vc, pose, normal, t0, p0, radiusH, radiusV, r, g, b, j, i);
                barrierVertex(vc, pose, normal, t1, p0, radiusH, radiusV, r, g, b, j, i + 1);
                barrierVertex(vc, pose, normal, t1, p1, radiusH, radiusV, r, g, b, j + 1, i + 1);
                barrierVertex(vc, pose, normal, t0, p1, radiusH, radiusV, r, g, b, j + 1, i);
            }
        }
        poseStack.popPose();
    }

    private static void barrierVertex(VertexConsumer vc, Matrix4f pose, Matrix3f normal, float theta, float phi,
                                      float radiusH, float radiusV, float r, float g, float b, int u, int v) {
        float nx = Mth.sin(theta) * Mth.cos(phi), ny = Mth.cos(theta), nz = Mth.sin(theta) * Mth.sin(phi);
        vc.vertex(pose, nx * radiusH, ny * radiusV, nz * radiusH)
                .color(r, g, b, 1.0F)
                .uv(u * 4.0F / BARRIER_LON, v * 2.0F / BARRIER_LAT)
                .overlayCoords(OverlayTexture.NO_OVERLAY)
                .uv2(LightTexture.FULL_BRIGHT)
                .normal(normal, nx, ny, nz)
                .endVertex();
    }

    @Override
    public void renderRecursively(PoseStack poseStack, T animatable, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                                  VertexConsumer buffer, boolean isReRender, float partialTick, int packedLight, int packedOverlay,
                                  float red, float green, float blue, float alpha) {
        if (this.animateOnly) return;
        super.renderRecursively(poseStack, animatable, bone, renderType, bufferSource, buffer, isReRender, partialTick, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
