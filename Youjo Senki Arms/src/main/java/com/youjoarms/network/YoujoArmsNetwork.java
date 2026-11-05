package com.youjoarms.network;

import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

public class YoujoArmsNetwork {
    private static final String PROTOCOL_VERSION = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation("youjoarms", "main"),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    private static int packetId = 0;

    public static void register() {
        CHANNEL.registerMessage(
                packetId++,
                PacketSyncMageDataS2C.class,
                PacketSyncMageDataS2C::toBytes,
                PacketSyncMageDataS2C::new,
                PacketSyncMageDataS2C::handle
        );

        CHANNEL.registerMessage(
                packetId++,
                PacketCastKeyC2S.class,
                PacketCastKeyC2S::toBytes,
                PacketCastKeyC2S::new,
                PacketCastKeyC2S::handle
        );
    }
}
