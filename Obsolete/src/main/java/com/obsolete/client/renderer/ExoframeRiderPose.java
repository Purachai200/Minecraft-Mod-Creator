package com.obsolete.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderPlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Pilot rides astride like a horse rider (anime pose): legs angled forward-down and spread around the frame's back,
 * arms reaching forward to the control grips. Vanilla has no hook after setupAnim, so the limbs are hidden for the
 * vanilla pass and redrawn here with the same transforms LivingEntityRenderer/PlayerRenderer apply.
 * The angles are mirrored in tools/build_exoframe_geo.py (RIDER envelope) — change both together.
 */
@Mod.EventBusSubscriber(modid = ObsoleteMod.MODID, value = Dist.CLIENT)
public final class ExoframeRiderPose {
    public static final float LEG_FORWARD = 0.9F;   // rad, thighs forward-down
    public static final float LEG_SPREAD = 0.8F;    // rad, straddling outward around the frame
    public static final float ARM_FORWARD = 1.0F;   // rad, hands forward-down onto the grips
    public static final float ARM_SPREAD = 0.12F;

    private static final boolean[] savedVisibility = new boolean[8];

    private ExoframeRiderPose() {
    }

    private static ModelPart[] limbs(PlayerModel<AbstractClientPlayer> m) {
        return new ModelPart[]{m.leftLeg, m.rightLeg, m.leftPants, m.rightPants, m.leftArm, m.rightArm, m.leftSleeve, m.rightSleeve};
    }

    private static boolean piloting(AbstractClientPlayer player) {
        return player.getVehicle() instanceof ExoframeEntity;
    }

    @SubscribeEvent
    public static void onPre(RenderPlayerEvent.Pre event) {
        if (!(event.getEntity() instanceof AbstractClientPlayer player) || !(player.getVehicle() instanceof ExoframeEntity exo)) return;
        // shouldRiderSit() is false, so vanilla never locks the rider's body to the mount: do it here, or the body
        // follows the camera and the legs swing out through the capsule walls. The head may still look ±75°.
        player.yBodyRot = exo.yBodyRot;
        player.yBodyRotO = exo.yBodyRotO;
        player.yHeadRot = exo.yBodyRot + Mth.clamp(Mth.wrapDegrees(player.yHeadRot - exo.yBodyRot), -75.0F, 75.0F);
        player.yHeadRotO = exo.yBodyRotO + Mth.clamp(Mth.wrapDegrees(player.yHeadRotO - exo.yBodyRotO), -75.0F, 75.0F);
        ModelPart[] parts = limbs(event.getRenderer().getModel());
        for (int i = 0; i < parts.length; i++) {
            savedVisibility[i] = parts[i].visible;   // keep the skin-customisation toggles (pants/sleeves)
            parts[i].visible = false;
        }
    }

    @SubscribeEvent
    public static void onPost(RenderPlayerEvent.Post event) {
        if (!(event.getEntity() instanceof AbstractClientPlayer player) || !piloting(player)) return;
        PlayerModel<AbstractClientPlayer> model = event.getRenderer().getModel();
        ModelPart[] parts = limbs(model);
        for (int i = 0; i < parts.length; i++) {
            parts[i].visible = savedVisibility[i];
        }
        if (player.isInvisible()) return;

        pose(model.leftLeg, -LEG_FORWARD, -LEG_SPREAD);
        pose(model.rightLeg, -LEG_FORWARD, LEG_SPREAD);
        pose(model.leftArm, -ARM_FORWARD, -ARM_SPREAD);
        pose(model.rightArm, -ARM_FORWARD, ARM_SPREAD);
        model.leftPants.copyFrom(model.leftLeg);
        model.rightPants.copyFrom(model.rightLeg);
        model.leftSleeve.copyFrom(model.leftArm);
        model.rightSleeve.copyFrom(model.rightArm);

        PoseStack poseStack = event.getPoseStack();
        poseStack.pushPose();
        float bodyYaw = Mth.rotLerp(event.getPartialTick(), player.yBodyRotO, player.yBodyRot);
        poseStack.mulPose(Axis.YP.rotationDegrees(180.0F - bodyYaw));
        poseStack.scale(-1.0F, -1.0F, 1.0F);
        poseStack.scale(0.9375F, 0.9375F, 0.9375F);   // PlayerRenderer.scale
        poseStack.translate(0.0F, -1.501F, 0.0F);
        VertexConsumer buffer = event.getMultiBufferSource().getBuffer(RenderType.entityTranslucent(player.getSkinTextureLocation()));
        int overlay = LivingEntityRenderer.getOverlayCoords(player, 0.0F);
        for (ModelPart part : parts) {
            if (part.visible) {
                part.render(poseStack, buffer, event.getPackedLight(), overlay);
            }
        }
        poseStack.popPose();
    }

    private static void pose(ModelPart part, float xRot, float zRot) {
        part.xRot = xRot;
        part.yRot = 0.0F;
        part.zRot = zRot;
    }
}
