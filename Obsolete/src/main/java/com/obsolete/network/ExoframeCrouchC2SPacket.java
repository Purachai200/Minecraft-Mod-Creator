package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeCrouchC2SPacket {
    private final boolean crouching;

    public ExoframeCrouchC2SPacket(boolean crouching) {
        this.crouching = crouching;
    }

    public ExoframeCrouchC2SPacket(FriendlyByteBuf buf) {
        this.crouching = buf.readBoolean();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeBoolean(crouching);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof ExoframeEntity exoframe) {
                exoframe.setMechCrouching(crouching);
            }
        });
        return true;
    }
}
