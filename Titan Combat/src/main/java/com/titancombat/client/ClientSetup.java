package com.titancombat.client;

import com.titancombat.TitanCombatMod;
import com.titancombat.client.gui.MechCockpitHudOverlay;
import com.titancombat.client.gui.TitanScreen;
import com.titancombat.client.model.AegisStrikerModel;
import com.titancombat.client.renderer.AegisStrikerRenderer;
import com.titancombat.client.renderer.TitanRenderer;
import com.titancombat.client.renderer.TransportVehicleRenderer;
import com.titancombat.entity.ModEntities;
import com.titancombat.gui.ModMenuTypes;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientSetup {

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            MenuScreens.register(ModMenuTypes.TITAN_MENU.get(), TitanScreen::new);
        });
    }

    @SubscribeEvent
    public static void registerEntityRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.AEGIS_STRIKER.get(), AegisStrikerRenderer::new);
        event.registerEntityRenderer(ModEntities.ION_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.SCORCH_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.RONIN_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.TONE_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.LEGION_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.MONARCH_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.NORTHSTAR_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.TROOPER_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.SCOUT_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.SHADE_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.ENERGY_BLAST.get(), ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.HAULER_TRUCK.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.CARGO_BARGE.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.SKYCRANE_DRONE.get(), TransportVehicleRenderer::new);
    }

    @SubscribeEvent
    public static void registerLayerDefinitions(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(AegisStrikerModel.LAYER_LOCATION, AegisStrikerModel::createBodyLayer);
    }

    @SubscribeEvent
    public static void registerGuiOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAboveAll("mech_cockpit_hud", MechCockpitHudOverlay.HUD_COCKPIT);
    }

    @SubscribeEvent
    public static void registerKeyMappings(RegisterKeyMappingsEvent event) {
        KeyInputHandler.registerKeys(event);
    }
}
