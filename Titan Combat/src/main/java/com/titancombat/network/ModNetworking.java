package com.titancombat.network;

import com.titancombat.TitanCombatMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

public class ModNetworking {
    private static final String PROTOCOL_VERSION = "3";
    public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(TitanCombatMod.MODID, "main"),
            () -> PROTOCOL_VERSION,
            PROTOCOL_VERSION::equals,
            PROTOCOL_VERSION::equals
    );

    private static int packetId = 0;
    private static int id() {
        return packetId++;
    }

    public static void register() {
        INSTANCE.messageBuilder(MechControlC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(MechControlC2SPacket::new)
                .encoder(MechControlC2SPacket::toBytes)
                .consumerMainThread(MechControlC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(com.titancombat.assembly.AssembleVehicleC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(com.titancombat.assembly.AssembleVehicleC2SPacket::new)
                .encoder(com.titancombat.assembly.AssembleVehicleC2SPacket::toBytes)
                .consumerMainThread(com.titancombat.assembly.AssembleVehicleC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(TitanWeaponActionC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(TitanWeaponActionC2SPacket::new)
                .encoder(TitanWeaponActionC2SPacket::toBytes)
                .consumerMainThread(TitanWeaponActionC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(ArtilleryTargetC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(ArtilleryTargetC2SPacket::new)
                .encoder(ArtilleryTargetC2SPacket::toBytes)
                .consumerMainThread(ArtilleryTargetC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(TitanFireC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(TitanFireC2SPacket::new)
                .encoder(TitanFireC2SPacket::toBytes)
                .consumerMainThread(TitanFireC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(MechEjectC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(MechEjectC2SPacket::new)
                .encoder(MechEjectC2SPacket::toBytes)
                .consumerMainThread(MechEjectC2SPacket::handle)
                .add();

        INSTANCE.messageBuilder(OpenTitanInventoryC2SPacket.class, id(), NetworkDirection.PLAY_TO_SERVER)
                .decoder(OpenTitanInventoryC2SPacket::new)
                .encoder(OpenTitanInventoryC2SPacket::toBytes)
                .consumerMainThread(OpenTitanInventoryC2SPacket::handle)
                .add();
    }

    public static <MSG> void sendToServer(MSG message) {
        INSTANCE.sendToServer(message);
    }

    public static <MSG> void sendToPlayer(MSG message, ServerPlayer player) {
        INSTANCE.send(PacketDistributor.PLAYER.with(() -> player), message);
    }
}
