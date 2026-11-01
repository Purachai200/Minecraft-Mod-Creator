package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeBulletEntity;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.jetbrains.annotations.NotNull;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

public class ExoframeBulletRenderer extends EntityRenderer<ExoframeBulletEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/projectiles/bullet_cuboid.png");

    public ExoframeBulletRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(ExoframeBulletEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTicks, entity.yRotO, entity.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTicks, entity.xRotO, entity.getXRot())));

        VertexConsumer vc = buffer.getBuffer(RenderType.entityCutoutNoCull(this.getTextureLocation(entity)));
        PoseStack.Pose last = poseStack.last();
        Matrix4f pose = last.pose();
        Matrix3f normal = last.normal();

        // 3D 4-Sided Square Cuboid Bullet:
        // Length 0.85m (X from -0.65 to +0.20), Square Cross-Section 0.11m x 0.11m (Y and Z from -0.055 to +0.055)
        float x0 = -0.65F, x1 = 0.20F;
        float y0 = -0.055F, y1 = 0.055F;
        float z0 = -0.055F, z1 = 0.055F;

        // Tracers are incandescent thermal kinetic projectiles - rendered at full brightness
        int fullBright = LightTexture.FULL_BRIGHT;

        // 1. Front Nose Face (+X) - Incandescent kinetic penetrator tip
        renderFace(vc, pose, normal,
                x1, y0, z1, 0.625F, 0.375F,
                x1, y0, z0, 1.000F, 0.375F,
                x1, y1, z0, 1.000F, 0.000F,
                x1, y1, z1, 0.625F, 0.000F,
                1, 0, 0, 255, 255, 240, 255, fullBright);

        // 2. Rear Tracer Core (-X) - Hot burning tracer rocket combustion base
        renderFace(vc, pose, normal,
                x0, y0, z0, 0.625F, 0.750F,
                x0, y0, z1, 1.000F, 0.750F,
                x0, y1, z1, 1.000F, 0.375F,
                x0, y1, z0, 0.625F, 0.375F,
                -1, 0, 0, 255, 160, 25, 255, fullBright);

        // 3. Top Square Side (+Y) - Golden-amber tracer streak
        renderFace(vc, pose, normal,
                x0, y1, z0, 0.000F, 0.000F,
                x0, y1, z1, 0.000F, 0.500F,
                x1, y1, z1, 0.625F, 0.500F,
                x1, y1, z0, 0.625F, 0.000F,
                0, 1, 0, 255, 240, 120, 255, fullBright);

        // 4. Bottom Square Side (-Y) - Shaded golden-amber underside
        renderFace(vc, pose, normal,
                x0, y0, z1, 0.000F, 0.500F,
                x0, y0, z0, 0.000F, 1.000F,
                x1, y0, z0, 0.625F, 1.000F,
                x1, y0, z1, 0.625F, 0.500F,
                0, -1, 0, 240, 190, 60, 255, fullBright);

        // 5. Right Square Side (+Z) - Kinetic tracer flank
        renderFace(vc, pose, normal,
                x0, y0, z1, 0.000F, 0.500F,
                x1, y0, z1, 0.625F, 0.500F,
                x1, y1, z1, 0.625F, 0.000F,
                x0, y1, z1, 0.000F, 0.000F,
                0, 0, 1, 255, 220, 90, 255, fullBright);

        // 6. Left Square Side (-Z) - Kinetic tracer flank
        renderFace(vc, pose, normal,
                x1, y0, z0, 0.625F, 0.500F,
                x0, y0, z0, 0.000F, 0.500F,
                x0, y1, z0, 0.000F, 0.000F,
                x1, y1, z0, 0.625F, 0.000F,
                0, 0, -1, 245, 210, 80, 255, fullBright);

        poseStack.popPose();
        super.render(entity, entityYaw, partialTicks, poseStack, buffer, packedLight);
    }

    private static void renderFace(VertexConsumer vc, Matrix4f pose, Matrix3f normal,
                                  float x1, float y1, float z1, float u1, float v1,
                                  float x2, float y2, float z2, float u2, float v2,
                                  float x3, float y3, float z3, float u3, float v3,
                                  float x4, float y4, float z4, float u4, float v4,
                                  float nx, float ny, float nz,
                                  int r, int g, int b, int a, int light) {
        vc.vertex(pose, x1, y1, z1).color(r, g, b, a).uv(u1, v1).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(normal, nx, ny, nz).endVertex();
        vc.vertex(pose, x2, y2, z2).color(r, g, b, a).uv(u2, v2).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(normal, nx, ny, nz).endVertex();
        vc.vertex(pose, x3, y3, z3).color(r, g, b, a).uv(u3, v3).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(normal, nx, ny, nz).endVertex();
        vc.vertex(pose, x4, y4, z4).color(r, g, b, a).uv(u4, v4).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(light).normal(normal, nx, ny, nz).endVertex();
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull ExoframeBulletEntity entity) {
        return TEXTURE;
    }
}
