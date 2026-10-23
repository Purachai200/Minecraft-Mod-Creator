package com.youjosenki.flight.compat.curios;

import com.youjosenki.flight.item.ModItems;
import net.minecraftforge.fml.ModList;

public class CuriosCompat {
    public static final String CURIOS_MODID = "curios";

    public static boolean isCuriosLoaded() {
        return ModList.get().isLoaded(CURIOS_MODID);
    }

    public static void registerRenderer() {
        if (isCuriosLoaded()) {
            CuriosClientCompat.register();
        }
    }

    private static class CuriosClientCompat {
        private static void register() {
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.ELENIUM_TYPE95_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.ELENIUM_TYPE97_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.REPUBLIC_TYPE101_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.FEDERATION_TYPE82_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.ALLIED_TYPE1923_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.COMMONWEALTH_MK2_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.ENTENTE_SKIRIG_FLIGHT_UNIT.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.TACTICAL_COMBAT_JETPACK.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.HEAVY_INDUSTRIAL_ROCKET_PACK.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.SHADOW_RECON_WINGS.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.ELENIUM_TYPE95_EXO.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.TITAN_SIEGE_FRAME.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
            top.theillusivec4.curios.api.client.CuriosRendererRegistry.register(
                ModItems.VALKYRIE_THRUST_BOOTS.get(),
                com.youjosenki.flight.client.renderer.FlightUnitCurioRenderer::new
            );
        }
    }
}
