package com.obsolete.client;

import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Handles client-side Forge bus events.
 * Suppresses vanilla player survival HUD (hearts, food, armor, bubbles) when inside an Exoframe,
 * handing over complete telemetry to the Exoframe HUD overlay.
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
}
