package com.titancombat.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.TitanSmokeShellEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

public class TitanSmokeShellRenderer extends EntityRenderer<TitanSmokeShellEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(TitanCombatMod.MODID, "textures/entity/projectiles/bullet_cuboid.png");

    public TitanSmokeShellRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(TitanSmokeShellEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTicks, entity.yRotO, entity.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTicks, entity.xRotO, entity.getXRot())));

        VertexConsumer vc = buffer.getBuffer(RenderType.entityCutoutNoCull(this.getTextureLocation(entity)));
        PoseStack.Pose last = poseStack.last();
        Matrix4f pose = last.pose();
        Matrix3f normal = last.normal();

        // 3D Olive-Drab Smoke Canister Shell
        float x0 = -0.70F, x1 = 0.25F;
        float y0 = -0.12F, y1 = 0.12F;
        float z0 = -0.12F, z1 = 0.12F;

        // Front Face (+X) - Olive drab nose cap
        renderFace(vc, pose, normal,
                x1, y0, z1, 0.625F, 0.375F,
                x1, y0, z0, 1.000F, 0.375F,
                x1, y1, z0, 1.000F, 0.000F,
                x1, y1, z1, 0.625F, 0.000F,
                1, 0, 0, 75, 95, 65, 255, packedLight);

        // Rear Face (-X) - Dark base
        renderFace(vc, pose, normal,
                x0, y0, z0, 0.625F, 0.750F,
                x0, y0, z1, 1.000F, 0.750F,
                x0, y1, z1, 1.000F, 0.375F,
                x0, y1, z0, 0.625F, 0.375F,
                -1, 0, 0, 50, 50, 50, 255, packedLight);

        // Top Side (+Y) - Forest Green
        renderFace(vc, pose, normal,
                x0, y1, z0, 0.000F, 0.000F,
                x0, y1, z1, 0.000F, 0.500F,
                x1, y1, z1, 0.625F, 0.500F,
                x1, y1, z0, 0.625F, 0.000F,
                0, 1, 0, 85, 110, 75, 255, packedLight);

        // Bottom Side (-Y)
        renderFace(vc, pose, normal,
                x0, y0, z1, 0.000F, 0.500F,
                x0, y0, z0, 0.000F, 1.000F,
                x1, y0, z0, 0.625F, 1.000F,
                x1, y0, z1, 0.625F, 0.500F,
                0, -1, 0, 65, 85, 55, 255, packedLight);

        // Right Side (+Z)
        renderFace(vc, pose, normal,
                x0, y0, z1, 0.000F, 0.500F,
                x1, y0, z1, 0.625F, 0.500F,
                x1, y1, z1, 0.625F, 0.000F,
                x0, y1, z1, 0.000F, 0.000F,
                0, 0, 1, 80, 105, 70, 255, packedLight);

        // Left Side (-Z)
        renderFace(vc, pose, normal,
                x1, y0, z0, 0.625F, 0.500F,
                x0, y0, z0, 0.000F, 0.500F,
                x0, y1, z0, 0.000F, 0.000F,
                x1, y1, z0, 0.625F, 0.000F,
                0, 0, -1, 80, 105, 70, 255, packedLight);

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
        vc.vertex(pose, x1, y1, z1).color(r, g, b, a).uv(u1, v1).overlayCoords(0, 10).uv2(light).normal(normal, nx, ny, nz).endVertex();
        vc.vertex(pose, x2, y2, z2).color(r, g, b, a).uv(u2, v2).overlayCoords(0, 10).uv2(light).normal(normal, nx, ny, nz).endVertex();
        vc.vertex(pose, x3, y3, z3).color(r, g, b, a).uv(u3, v3).overlayCoords(0, 10).uv2(light).normal(normal, nx, ny, nz).endVertex();
        vc.vertex(pose, x4, y4, z4).color(r, g, b, a).uv(u4, v4).overlayCoords(0, 10).uv2(light).normal(normal, nx, ny, nz).endVertex();
    }

    @Override
    public ResourceLocation getTextureLocation(TitanSmokeShellEntity entity) {
        return TEXTURE;
    }
}
