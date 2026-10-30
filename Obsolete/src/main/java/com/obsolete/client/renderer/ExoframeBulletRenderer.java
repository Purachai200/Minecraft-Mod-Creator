package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeBulletEntity;
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
    private static final ResourceLocation TEXTURE = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/projectiles/bullet_tracer.png");

    public ExoframeBulletRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(ExoframeBulletEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTicks, entity.yRotO, entity.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTicks, entity.xRotO, entity.getXRot())));

        VertexConsumer vertexConsumer = buffer.getBuffer(RenderType.entityCutout(this.getTextureLocation(entity)));
        PoseStack.Pose last = poseStack.last();
        Matrix4f pose = last.pose();
        Matrix3f normal = last.normal();

        // Render elongated kinetic bullet quad
        float size = 0.1F;
        float length = 0.5F;
        for (int i = 0; i < 2; i++) {
            poseStack.mulPose(Axis.XP.rotationDegrees(90.0F));
            vertex(vertexConsumer, pose, normal, -length, -size, 0, 0, 0, packedLight);
            vertex(vertexConsumer, pose, normal, length, -size, 0, 1, 0, packedLight);
            vertex(vertexConsumer, pose, normal, length, size, 0, 1, 1, packedLight);
            vertex(vertexConsumer, pose, normal, -length, size, 0, 0, 1, packedLight);
        }

        poseStack.popPose();
        super.render(entity, entityYaw, partialTicks, poseStack, buffer, packedLight);
    }

    private static void vertex(VertexConsumer vc, Matrix4f pose, Matrix3f normal, float x, float y, float z, float u, float v, int light) {
        vc.vertex(pose, x, y, z)
                .color(255, 230, 120, 255)
                .uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY)
                .uv2(light)
                .normal(normal, 0, 1, 0)
                .endVertex();
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull ExoframeBulletEntity entity) {
        return TEXTURE;
    }
}
