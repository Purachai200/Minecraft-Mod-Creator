package com.youjosenki.flight.client;

import com.youjosenki.flight.YoujoSenkiMod;
import com.youjosenki.flight.client.gui.FlightHudOverlay;
import com.youjosenki.flight.client.model.FlightUnitModel;
import com.youjosenki.flight.compat.curios.CuriosCompat;
import com.youjosenki.flight.item.ModItems;
import net.minecraft.world.item.DyeableLeatherItem;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterColorHandlersEvent;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid = YoujoSenkiMod.MODID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public class ClientSetup {

    @SubscribeEvent
    public static void registerLayerDefinitions(EntityRenderersEvent.RegisterLayerDefinitions event) {
        event.registerLayerDefinition(FlightUnitModel.LAYER_LOCATION, FlightUnitModel::createBodyLayer);
    }

    @SubscribeEvent
    public static void registerGuiOverlays(RegisterGuiOverlaysEvent event) {
        event.registerAbove(VanillaGuiOverlay.PLAYER_HEALTH.id(), "flight_hud", FlightHudOverlay.HUD_OVERLAY);
    }

    @SubscribeEvent
    public static void onClientSetup(FMLClientSetupEvent event) {
        event.enqueueWork(() -> {
            CuriosCompat.registerRenderer();
        });
    }

    @SubscribeEvent
    public static void registerItemColors(RegisterColorHandlersEvent.Item event) {
        // Dynamic color tinting for dyed flight units in inventory & hand
        event.register((stack, tintIndex) -> {
            if (tintIndex == 0 && stack.getItem() instanceof DyeableLeatherItem dyeable) {
                return dyeable.getColor(stack);
            }
            return -1;
        },
        ModItems.ELENIUM_TYPE95_FLIGHT_UNIT.get(),
        ModItems.ELENIUM_TYPE97_FLIGHT_UNIT.get(),
        ModItems.REPUBLIC_TYPE101_FLIGHT_UNIT.get(),
        ModItems.FEDERATION_TYPE82_FLIGHT_UNIT.get(),
        ModItems.ALLIED_TYPE1923_FLIGHT_UNIT.get(),
        ModItems.COMMONWEALTH_MK2_FLIGHT_UNIT.get(),
        ModItems.ENTENTE_SKIRIG_FLIGHT_UNIT.get(),
        ModItems.TACTICAL_COMBAT_JETPACK.get(),
        ModItems.HEAVY_INDUSTRIAL_ROCKET_PACK.get(),
        ModItems.SHADOW_RECON_WINGS.get(),
        ModItems.ELENIUM_TYPE95_EXO.get(),
        ModItems.TITAN_SIEGE_FRAME.get(),
        ModItems.VALKYRIE_THRUST_BOOTS.get()
        );
    }
}
