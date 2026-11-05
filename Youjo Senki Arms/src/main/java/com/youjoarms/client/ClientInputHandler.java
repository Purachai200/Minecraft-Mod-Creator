package com.youjoarms.client;

import com.tacz.guns.api.item.IGun;
import com.youjoarms.network.PacketCastKeyC2S;
import com.youjoarms.network.YoujoArmsNetwork;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

public class ClientInputHandler {

    private static boolean wasCastKeyDown = false;

    @Mod.EventBusSubscriber(modid = "youjoarms", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static class ModClientEvents {
        @SubscribeEvent
        public static void onRegisterKeyMappings(RegisterKeyMappingsEvent event) {
            event.register(KeyBindings.CAST_KEY);
            event.register(KeyBindings.CYCLE_KEY);
        }
    }

    @Mod.EventBusSubscriber(modid = "youjoarms", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
    public static class ForgeClientEvents {
        @SubscribeEvent
        public static void onClientTick(TickEvent.ClientTickEvent event) {
            if (event.phase != TickEvent.Phase.END) return;

            Minecraft mc = Minecraft.getInstance();
            Player player = mc.player;
            if (player == null) return;

            ItemStack held = player.getMainHandItem();
            IGun gun = IGun.getIGunOrNull(held);

            // Handle Formula cycle key (press once)
            while (KeyBindings.CYCLE_KEY.consumeClick()) {
                if (gun != null) {
                    YoujoArmsNetwork.CHANNEL.sendToServer(new PacketCastKeyC2S(false, true));
                }
            }

            // Handle Cast key (held state)
            boolean isCastKeyDown = KeyBindings.CAST_KEY.isDown();
            if (isCastKeyDown != wasCastKeyDown) {
                wasCastKeyDown = isCastKeyDown;
                if (gun != null) {
                    YoujoArmsNetwork.CHANNEL.sendToServer(new PacketCastKeyC2S(isCastKeyDown, false));
                } else if (!isCastKeyDown) {
                    // Release charge if no longer holding gun
                    YoujoArmsNetwork.CHANNEL.sendToServer(new PacketCastKeyC2S(false, false));
                }
            }
        }
    }
}
