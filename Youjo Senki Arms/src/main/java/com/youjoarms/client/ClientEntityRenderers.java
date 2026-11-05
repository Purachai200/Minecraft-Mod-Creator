package com.youjoarms.client;

import com.youjoarms.entity.ModEntities;
import net.minecraft.client.renderer.entity.NoopRenderer;
import net.minecraft.client.renderer.entity.ThrownItemRenderer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.EntityRenderersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Without these the client crashes the first time a shell or zone spawns. Zones are drawn by MagicCircleRenderer. */
@Mod.EventBusSubscriber(modid = "youjoarms", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
public final class ClientEntityRenderers {
    @SubscribeEvent
    public static void register(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(ModEntities.ARTILLERY_SHELL.get(), ctx -> new ThrownItemRenderer<>(ctx, 1.0F, true));
        event.registerEntityRenderer(ModEntities.FORMULA_ZONE.get(), NoopRenderer::new);
    }
}
