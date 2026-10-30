package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeAimC2SPacket {
    private final boolean aiming;

    public ExoframeAimC2SPacket(boolean aiming) {
        this.aiming = aiming;
    }

    public ExoframeAimC2SPacket(FriendlyByteBuf buf) {
        this.aiming = buf.readBoolean();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeBoolean(aiming);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof ExoframeEntity exoframe) {
                exoframe.setAiming(aiming);
            }
        });
        return true;
    }
}
