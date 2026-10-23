package com.youjosenki.flight.network;

import com.youjosenki.flight.YoujoSenkiMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

public class ModNetworking {
    private static final String PROTOCOL_VERSION = "1.0";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(YoujoSenkiMod.MODID, "main"),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    private static int packetId = 0;
    private static int nextId() {
        return packetId++;
    }

    public static void register() {
        CHANNEL.messageBuilder(ToggleFlightC2SPacket.class, nextId(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ToggleFlightC2SPacket::new)
                .encoder(ToggleFlightC2SPacket::toBytes)
                .consumerMainThread(ToggleFlightC2SPacket::handle)
                .add();

        CHANNEL.messageBuilder(FlightBoostC2SPacket.class, nextId(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(FlightBoostC2SPacket::new)
                .encoder(FlightBoostC2SPacket::toBytes)
                .consumerMainThread(FlightBoostC2SPacket::handle)
                .add();

        CHANNEL.messageBuilder(SyncFlightTelemetryS2CPacket.class, nextId(), NetworkDirection.PLAY_TO_CLIENT)
                .decoder(SyncFlightTelemetryS2CPacket::new)
                .encoder(SyncFlightTelemetryS2CPacket::toBytes)
                .consumerMainThread(SyncFlightTelemetryS2CPacket::handle)
                .add();
    }

    public static <MSG> void sendToServer(MSG message) {
        CHANNEL.sendToServer(message);
    }

    public static <MSG> void sendToPlayer(MSG message, ServerPlayer player) {
        CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), message);
    }
}
