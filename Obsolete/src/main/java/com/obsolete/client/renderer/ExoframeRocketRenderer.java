package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeRocketEntity;
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

public class ExoframeRocketRenderer extends EntityRenderer<ExoframeRocketEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(ObsoleteMod.MODID, "textures/entity/projectiles/rocket.png");

    public ExoframeRocketRenderer(EntityRendererProvider.Context context) {
        super(context);
    }

    @Override
    public void render(ExoframeRocketEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        poseStack.pushPose();
        poseStack.mulPose(Axis.YP.rotationDegrees(Mth.lerp(partialTicks, entity.yRotO, entity.getYRot()) - 90.0F));
        poseStack.mulPose(Axis.ZP.rotationDegrees(Mth.lerp(partialTicks, entity.xRotO, entity.getXRot())));

        VertexConsumer vc = buffer.getBuffer(RenderType.entityCutout(TEXTURE));
        PoseStack.Pose last = poseStack.last();
        Matrix4f pose = last.pose();
        Matrix3f normal = last.normal();

        // Render cross-fin missile body
        float size = 0.22F;
        float length = 0.8F;
        for (int i = 0; i < 4; i++) {
            poseStack.mulPose(Axis.XP.rotationDegrees(45.0F));
            vertex(vc, pose, normal, -length, -size, 0, 0, 0, packedLight);
            vertex(vc, pose, normal, length, -size, 0, 1, 0, packedLight);
            vertex(vc, pose, normal, length, size, 0, 1, 1, packedLight);
            vertex(vc, pose, normal, -length, size, 0, 0, 1, packedLight);
        }

        poseStack.popPose();
        super.render(entity, entityYaw, partialTicks, poseStack, buffer, packedLight);
    }

    private static void vertex(VertexConsumer vc, Matrix4f pose, Matrix3f normal, float x, float y, float z, float u, float v, int light) {
        vc.vertex(pose, x, y, z)
                .color(180, 200, 140, 255)
                .uv(u, v)
                .overlayCoords(OverlayTexture.NO_OVERLAY)
                .uv2(light)
                .normal(normal, 0, 1, 0)
                .endVertex();
    }

    @Override
    public @NotNull ResourceLocation getTextureLocation(@NotNull ExoframeRocketEntity entity) {
        return TEXTURE;
    }
}
