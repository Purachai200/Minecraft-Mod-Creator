package com.titancombat.client.cockpit;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderHandEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.renderer.GeoObjectRenderer;

import java.util.EnumMap;
import java.util.Map;

/**
 * First-person piloting view: draws the cockpit cabin (canopy frame + instrument base) and the
 * titan's own arms and weapon in front of the camera, in place of the pilot's hands, the same
 * way the original addon does. Rendered in the hand pass, so it never clips into terrain.
 *
 * The models are authored in Bedrock player space: the pilot's eye sits at (0, 27.6, 0) px and
 * forward is +Z (the canopy frame and the weapon crosshair are centred on that point).
 */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, value = Dist.CLIENT)
public final class CockpitViewRenderer {
    private static final float EYE_HEIGHT_PX = 27.6F;

    private static final GeoObjectRenderer<CockpitPart> RENDERER = new GeoObjectRenderer<>(new CockpitModel()) {
        @Override
        public RenderType getRenderType(CockpitPart animatable, ResourceLocation texture, @Nullable MultiBufferSource bufferSource, float partialTick) {
            return RenderType.entityCutoutNoCull(texture);
        }
    };

    private static final Map<TitanClass, CockpitPart> ARMS = new EnumMap<>(TitanClass.class);
    private static final CockpitPart CABIN_BASE = new CockpitPart(CockpitPart.Kind.CABIN_BASE, TitanClass.ION);
    private static final CockpitPart CABIN_FRAME = new CockpitPart(CockpitPart.Kind.CABIN_FRAME, TitanClass.ION);

    private CockpitViewRenderer() {}

    @SubscribeEvent
    public static void onRenderHand(RenderHandEvent event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.options.getCameraType() != CameraType.FIRST_PERSON) return;
        if (!(mc.player.getVehicle() instanceof BaseTitanEntity titan)) return;

        // The pilot's own hands/items are hidden; the cockpit takes their place.
        event.setCanceled(true);
        if (event.getHand() != InteractionHand.MAIN_HAND) return;

        // Interior panels are self-lit enough to read at night, but still follow daylight.
        int block = Math.max(9, LightTexture.block(event.getPackedLight()));
        int sky = LightTexture.sky(event.getPackedLight());
        int light = LightTexture.pack(block, sky);

        PoseStack pose = event.getPoseStack();
        pose.pushPose();
        // Bedrock player space (+Z forward, eye at 27.6 px) -> camera space (-Z forward, eye at origin).
        pose.mulPose(Axis.YP.rotationDegrees(180.0F));
        pose.translate(0.0F, -EYE_HEIGHT_PX / 16.0F, 0.0F);
        // GeoObjectRenderer centres objects in a block space (+0.5, +0.51, +0.5); undo that.
        pose.translate(-0.5F, -0.51F, -0.5F);

        MultiBufferSource buffers = event.getMultiBufferSource();
        RENDERER.render(pose, CABIN_BASE, buffers, null, null, light);
        RENDERER.render(pose, CABIN_FRAME, buffers, null, null, light);
        // The first-person rig comes from the chassis the mounted weapon was built for, so swapped guns show
        // correctly; unarmed titans show their own arms with the gun hidden (CockpitModel).
        TitanClass rig = titan.hasWeapon() ? titan.getActiveWeapon().getFactoryChassis() : titan.getTitanClass();
        CockpitPart arms = ARMS.computeIfAbsent(rig, c -> new CockpitPart(CockpitPart.Kind.ARMS, c));
        float lower = titan.getLowerBlend(event.getPartialTick());
        if (lower > 0.001F) {
            // Lowered weapon: the arm and gun dip out of the sight line, muzzle down.
            pose.translate(0.0F, -0.9F * lower, 0.25F * lower);
            pose.mulPose(Axis.XP.rotationDegrees(-28.0F * lower));
        }
        RENDERER.render(pose, arms, buffers, null, null, light);

        pose.popPose();
    }
}
