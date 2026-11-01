package com.obsolete.client;

import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Handles client-side Forge bus events.
 * Suppresses vanilla player survival HUD (hearts, food, armor, bubbles) when inside an Exoframe,
 * and applies realistic cockpit camera recoil / footstep shake.
 */
@Mod.EventBusSubscriber(modid = ObsoleteMod.MODID, bus = Mod.EventBusSubscriber.Bus.FORGE, value = Dist.CLIENT)
public class ClientForgeEvents {

    @SubscribeEvent
    public static void onRenderGuiOverlayPre(RenderGuiOverlayEvent.Pre event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && mc.player.getVehicle() instanceof ExoframeEntity) {
            String overlayId = event.getOverlay().id().toString();
            if (overlayId.equals(VanillaGuiOverlay.PLAYER_HEALTH.id().toString())
                    || overlayId.equals(VanillaGuiOverlay.FOOD_LEVEL.id().toString())
                    || overlayId.equals(VanillaGuiOverlay.ARMOR_LEVEL.id().toString())
                    || overlayId.equals(VanillaGuiOverlay.AIR_LEVEL.id().toString())
                    || overlayId.equals(VanillaGuiOverlay.EXPERIENCE_BAR.id().toString())
                    || overlayId.equals(VanillaGuiOverlay.MOUNT_HEALTH.id().toString())) {
                event.setCanceled(true);
            }
        }
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase == TickEvent.Phase.END) {
            CameraShakeManager.clientTick();
        }
    }

    @SubscribeEvent
    public static void onComputeCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        float intensity = CameraShakeManager.getShakeIntensity();
        if (intensity > 0.005f) {
            long time = System.currentTimeMillis();
            float yawOffset = (float) Math.sin(time * 0.035) * intensity * 0.5f;
            float pitchOffset = (float) Math.cos(time * 0.045) * intensity * 0.8f;
            float rollOffset = (float) Math.sin(time * 0.055) * intensity * 0.4f;
            event.setYaw(event.getYaw() + yawOffset);
            event.setPitch(event.getPitch() + pitchOffset);
            event.setRoll(event.getRoll() + rollOffset);
        }
    }
}
