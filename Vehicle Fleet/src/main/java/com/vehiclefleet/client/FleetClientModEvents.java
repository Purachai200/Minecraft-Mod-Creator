package com.vehiclefleet.client;

import com.vehiclefleet.VehicleFleetMod;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = VehicleFleetMod.MODID, value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class FleetClientModEvents {
    private FleetClientModEvents() {}

    @SubscribeEvent
    public static void renderers(EntityRenderersEvent.RegisterRenderers e) {
        VehicleFleetMod.TYPES.values().forEach(t -> e.registerEntityRenderer(t.get(), FleetRenderer::new));
        e.registerEntityRenderer(VehicleFleetMod.DECK_COLLIDER.get(), net.minecraft.client.renderer.entity.NoopRenderer::new);
    }

    @SubscribeEvent
    public static void keys(RegisterKeyMappingsEvent e) {
        e.register(FleetKeys.CLIMB);
        e.register(FleetKeys.DESCEND);
        e.register(FleetKeys.SEAT);
        e.register(FleetKeys.OPEN);
        e.register(FleetKeys.LIGHTS);
        e.register(FleetKeys.RELEASE);
        e.register(FleetKeys.HORN);
    }
}
