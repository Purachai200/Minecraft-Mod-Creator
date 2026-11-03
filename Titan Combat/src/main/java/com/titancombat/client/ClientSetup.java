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
import net.minecraftforge.client.event.RegisterColorHandlersEvent;
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
        event.registerEntityRenderer(ModEntities.STRIKER_FRAME_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.VANGUARD_FRAME_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.COLOSSUS_FRAME_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.TERRAIN_FRAME_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.CYCLOPS_FRAME_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.SPIDER_FRAME_TITAN.get(), TitanRenderer::new);
        event.registerEntityRenderer(ModEntities.ENERGY_BLAST.get(), ThrownItemRenderer::new);
        event.registerEntityRenderer(ModEntities.TITAN_BULLET.get(), com.titancombat.client.renderer.TitanBulletRenderer::new);
        event.registerEntityRenderer(ModEntities.TITAN_CASING.get(), com.titancombat.client.renderer.TitanCasingRenderer::new);
        event.registerEntityRenderer(ModEntities.TITAN_SMOKE_SHELL.get(), com.titancombat.client.renderer.TitanSmokeShellRenderer::new);
        event.registerEntityRenderer(ModEntities.HAULER_TRUCK.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.DECK_COLLIDER.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
        event.registerEntityRenderer(ModEntities.CARGO_BARGE.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.SKYCRANE_DRONE.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.OCEAN_CARRIER.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.TACTICAL_TRUCK.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.CHINOOK_TRANSPORTER.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.V22_OSPREY.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.ARMORED_APC.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.LCAC_HOVERCRAFT.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.C130_HERCULES.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.REPAIR_TRUCK.get(), TransportVehicleRenderer::new);
        event.registerEntityRenderer(ModEntities.MOBILE_SUIT_TRAILER.get(), TransportVehicleRenderer::new);
    }

    @SubscribeEvent
    public static void registerLayerDefinitions(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(AegisStrikerModel.LAYER_LOCATION, AegisStrikerModel::createBodyLayer);
    }

    @SubscribeEvent
    public static void registerGuiOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAboveAll("mech_cockpit_hud", MechCockpitHudOverlay.HUD_COCKPIT);
        event.registerAboveAll("transport_vehicle_hud", com.titancombat.client.gui.TransportVehicleHudOverlay.HUD_TRANSPORT);
    }

    @SubscribeEvent
    public static void registerKeyMappings(RegisterKeyMappingsEvent event) {
        KeyInputHandler.registerKeys(event);
    }

    @SubscribeEvent
    public static void registerItemColors(RegisterColorHandlersEvent.Item event) {
        event.register((stack, tintIndex) -> {
            if (tintIndex == 0) {
                return com.titancombat.item.TitanArmorItem.getTheme(stack).getPrimaryColor();
            }
            return 0xFFFFFF;
        }, com.titancombat.item.ModItems.TITAN_ARMOR_HEAD.get(),
           com.titancombat.item.ModItems.TITAN_ARMOR_CHEST.get(),
           com.titancombat.item.ModItems.TITAN_ARMOR_ARMS.get(),
           com.titancombat.item.ModItems.TITAN_ARMOR_LEGS.get());
    }
}
