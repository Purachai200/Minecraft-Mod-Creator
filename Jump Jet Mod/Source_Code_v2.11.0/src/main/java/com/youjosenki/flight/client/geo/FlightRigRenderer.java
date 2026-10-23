package com.youjosenki.flight.client.geo;

import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.world.entity.EquipmentSlot;
import software.bernie.geckolib.core.object.Color;
import software.bernie.geckolib.renderer.GeoArmorRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

/**
 * GeckoLib renderer for every flight rig. Driven from the Curios renderer rather than the vanilla armor
 * layer, so it shows every bone regardless of slot, tints the base layer with the dye colour, and draws
 * elenium_flight_unit_glowmask.png fullbright for cores, crystals and nav lights.
 */
public class FlightRigRenderer extends GeoArmorRenderer<EleniumFlightUnitItem> {
    public FlightRigRenderer() {
        super(new FlightRigGeoModel());
        addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }

    @Override
    protected void applyBoneVisibilityBySlot(EquipmentSlot slot) {
        setAllVisible(true);
    }

    @Override
    public Color getRenderColor(EleniumFlightUnitItem item, float partialTick, int packedLight) {
        return Color.ofOpaque(item.getColor(getCurrentStack()));
    }
}
