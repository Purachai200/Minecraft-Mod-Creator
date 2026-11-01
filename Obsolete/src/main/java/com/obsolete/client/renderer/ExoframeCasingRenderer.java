package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeCasingEntity;
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

public class ExoframeCasingRenderer extends EntityRenderer<ExoframeCasingEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/projectiles/casing.png");

    public ExoframeCasingRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(ExoframeCasingEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();

        float yaw = Mth.lerp(partialTicks, entity.prevYaw, entity.yaw);
        float pitch = Mth.lerp(partialTicks, entity.prevPitch, entity.pitch);
        float roll = Mth.lerp(partialTicks, entity.prevRoll, entity.roll);

        poseStack.mulPose(Axis.YP.rotationDegrees(yaw));
        poseStack.mulPose(Axis.XP.rotationDegrees(pitch));
        poseStack.mulPose(Axis.ZP.rotationDegrees(roll));

        VertexConsumer vc = buffer.getBuffer(RenderType.entityCutoutNoCull(this.getTextureLocation(entity)));
        PoseStack.Pose last = poseStack.last();
        Matrix4f pose = last.pose();
        Matrix3f normal = last.normal();

        // 1. Main brass cartridge body (z from -0.10 to +0.04)
        float bx0 = -0.04F, bx1 = 0.04F;
        float by0 = -0.04F, by1 = 0.04F;
        float bz0 = -0.10F, bz1 = 0.04F;

        // Base rim & struck primer face (-Z)
        renderQuad(vc, pose, normal,
                bx0, by0, bz0, 0.625F, 0.750F,
                bx1, by0, bz0, 1.000F, 0.750F,
                bx1, by1, bz0, 1.000F, 0.375F,
                bx0, by1, bz0, 0.625F, 0.375F,
                0, 0, -1, 230, 185, 55, 255, packedLight);

        // Body Top (+Y)
        renderQuad(vc, pose, normal,
                bx0, by1, bz0, 0.000F, 0.000F,
                bx0, by1, bz1, 0.625F, 0.000F,
                bx1, by1, bz1, 0.625F, 0.500F,
                bx1, by1, bz0, 0.000F, 0.500F,
                0, 1, 0, 250, 220, 95, 255, packedLight);

        // Body Bottom (-Y)
        renderQuad(vc, pose, normal,
                bx0, by0, bz1, 0.000F, 0.000F,
                bx0, by0, bz0, 0.625F, 0.000F,
                bx1, by0, bz0, 0.625F, 0.500F,
                bx1, by0, bz1, 0.000F, 0.500F,
                0, -1, 0, 180, 135, 30, 255, packedLight);

        // Body Right (+X)
        renderQuad(vc, pose, normal,
                bx1, by0, bz0, 0.000F, 0.000F,
                bx1, by0, bz1, 0.625F, 0.000F,
                bx1, by1, bz1, 0.625F, 0.500F,
                bx1, by1, bz0, 0.000F, 0.500F,
                1, 0, 0, 225, 180, 50, 255, packedLight);

        // Body Left (-X)
        renderQuad(vc, pose, normal,
                bx0, by0, bz1, 0.000F, 0.000F,
                bx0, by0, bz0, 0.625F, 0.000F,
                bx0, by1, bz0, 0.625F, 0.500F,
                bx0, by1, bz1, 0.000F, 0.500F,
                -1, 0, 0, 215, 170, 45, 255, packedLight);

        // 2. Stepped neck & dark hollow mouth opening (z from 0.04 to 0.09)
        float nx0 = -0.032F, nx1 = 0.032F;
        float ny0 = -0.032F, ny1 = 0.032F;
        float nz0 = 0.04F, nz1 = 0.09F;

        // Neck Top (+Y)
        renderQuad(vc, pose, normal,
                nx0, ny1, nz0, 0.000F, 0.500F,
                nx0, ny1, nz1, 0.625F, 0.500F,
                nx1, ny1, nz1, 0.625F, 1.000F,
                nx1, ny1, nz0, 0.000F, 1.000F,
                0, 1, 0, 240, 205, 85, 255, packedLight);

        // Neck Bottom (-Y)
        renderQuad(vc, pose, normal,
                nx0, ny0, nz1, 0.000F, 0.500F,
                nx0, ny0, nz0, 0.625F, 0.500F,
                nx1, ny0, nz0, 0.625F, 1.000F,
                nx1, ny0, nz1, 0.000F, 1.000F,
                0, -1, 0, 180, 135, 30, 255, packedLight);

        // Neck Right (+X)
        renderQuad(vc, pose, normal,
                nx1, ny0, nz0, 0.000F, 0.500F,
                nx1, ny0, nz1, 0.625F, 0.500F,
                nx1, ny1, nz1, 0.625F, 1.000F,
                nx1, ny1, nz0, 0.000F, 1.000F,
                1, 0, 0, 220, 175, 45, 255, packedLight);

        // Neck Left (-X)
        renderQuad(vc, pose, normal,
                nx0, ny0, nz1, 0.000F, 0.500F,
                nx0, ny0, nz0, 0.625F, 0.500F,
                nx0, ny1, nz0, 0.625F, 1.000F,
                nx0, ny1, nz1, 0.000F, 1.000F,
                -1, 0, 0, 210, 165, 40, 255, packedLight);

        // Spent mouth opening (+Z) - dark hollow powder soot
        renderQuad(vc, pose, normal,
                nx0, ny0, nz1, 0.625F, 0.375F,
                nx1, ny0, nz1, 1.000F, 0.375F,
                nx1, ny1, nz1, 1.000F, 0.000F,
                nx0, ny1, nz1, 0.625F, 0.000F,
                0, 0, 1, 255, 255, 255, 255, packedLight);

        poseStack.popPose();
        super.render(entity, entityYaw, partialTicks, poseStack, buffer, packedLight);
    }

    private static void renderQuad(VertexConsumer vc, Matrix4f pose, Matrix3f normal,
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
    public @NotNull ResourceLocation getTextureLocation(@NotNull ExoframeCasingEntity entity) {
        return TEXTURE;
    }
}
