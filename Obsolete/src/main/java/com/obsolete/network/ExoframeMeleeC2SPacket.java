package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeMeleeC2SPacket {
    public ExoframeMeleeC2SPacket() {
    }

    public ExoframeMeleeC2SPacket(FriendlyByteBuf buf) {
    }

    public void toBytes(FriendlyByteBuf buf) {
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof ExoframeEntity exoframe) {
                exoframe.performMeleeAttack(player);
            }
        });
        return true;
    }
}
