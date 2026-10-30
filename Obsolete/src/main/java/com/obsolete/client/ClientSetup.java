package com.obsolete.client;

import com.obsolete.ObsoleteMod;
import com.obsolete.client.gui.ExoframeHudOverlay;
import com.obsolete.client.gui.ExoframeScreen;
import com.obsolete.client.gui.MechAssemblyScreen;
import com.obsolete.client.renderer.ExoframeBulletRenderer;
import com.obsolete.client.renderer.ExoframeRenderer;
import com.obsolete.client.renderer.ExoframeRocketRenderer;
import com.obsolete.entity.ModEntities;
import com.obsolete.gui.ModMenuTypes;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid = ObsoleteMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientSetup {

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            MenuScreens.register(ModMenuTypes.EXOFRAME_MENU.get(), ExoframeScreen::new);
            MenuScreens.register(ModMenuTypes.MECH_ASSEMBLY_MENU.get(), MechAssemblyScreen::new);
        });
    }

    @SubscribeEvent
    public static void registerRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.EXOFRAME.get(), ExoframeRenderer::new);
        event.registerEntityRenderer(ModEntities.BULLET.get(), ExoframeBulletRenderer::new);
        event.registerEntityRenderer(ModEntities.ROCKET.get(), ExoframeRocketRenderer::new);
    }

    @SubscribeEvent
    public static void registerKeyMappings(RegisterKeyMappingsEvent event) {
        ModKeyMappings.register(event);
    }

    @SubscribeEvent
    public static void registerOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAbove(VanillaGuiOverlay.CROSSHAIR.id(), "exoframe_hud", ExoframeHudOverlay.HUD_EXOFRAME);
    }
}
