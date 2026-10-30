package com.obsolete.network;

import com.obsolete.ObsoleteMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

public class ModNetworking {
    private static final String PROTOCOL_VERSION = "1";
    public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(ObsoleteMod.MODID, "main"),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    private static int packetId = 0;
    private static int id() {
        return packetId++;
    }

    public static void register() {
        INSTANCE.messageBuilder(ExoframeFireC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExoframeFireC2SPacket::new)
                .encoder(ExoframeFireC2SPacket::toBytes)
                .consumerMainThread(ExoframeFireC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExoframeMeleeC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExoframeMeleeC2SPacket::new)
                .encoder(ExoframeMeleeC2SPacket::toBytes)
                .consumerMainThread(ExoframeMeleeC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExoframeCrouchC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExoframeCrouchC2SPacket::new)
                .encoder(ExoframeCrouchC2SPacket::toBytes)
                .consumerMainThread(ExoframeCrouchC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExoframeAimC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExoframeAimC2SPacket::new)
                .encoder(ExoframeAimC2SPacket::toBytes)
                .consumerMainThread(ExoframeAimC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExoframeInventorySyncS2CPacket.class, id(), NetworkDirection.PLAY_TO_CLIENT)
                .decoder(ExoframeInventorySyncS2CPacket::new)
                .encoder(ExoframeInventorySyncS2CPacket::toBytes)
                .consumerMainThread(ExoframeInventorySyncS2CPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExoframeEmoteC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExoframeEmoteC2SPacket::new)
                .encoder(ExoframeEmoteC2SPacket::toBytes)
                .consumerMainThread(ExoframeEmoteC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(ExoframeOpenMenuC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ExoframeOpenMenuC2SPacket::new)
                .encoder(ExoframeOpenMenuC2SPacket::toBytes)
                .consumerMainThread(ExoframeOpenMenuC2SPacket::handle)
                .add();
    }

    public static <MSG> void sendToServer(MSG message) {
        INSTANCE.sendToServer(message);
    }

    public static <MSG> void sendToPlayer(MSG message, ServerPlayer player) {
        INSTANCE.send(PacketDistributor.PLAYER.with(() -> player), message);
    }

    public static <MSG> void sendToTracking(MSG message, Entity entity) {
        INSTANCE.send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> entity), message);
    }
}
