package com.youjosenki.flight.network;

import com.youjosenki.flight.telemetry.FlightStateManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class FlightBoostC2SPacket {

    public FlightBoostC2SPacket() {}

    public FlightBoostC2SPacket(FriendlyByteBuf buf) {}

    public void toBytes(FriendlyByteBuf buf) {}

    public void handle(Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null && !player.isSpectator()) {
                FlightStateManager.handlePlayerBoost(player);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
