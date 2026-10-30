package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeEmoteC2SPacket {
    private final String emote;

    public ExoframeEmoteC2SPacket(String emote) {
        this.emote = emote;
    }

    public ExoframeEmoteC2SPacket(FriendlyByteBuf buf) {
        this.emote = buf.readUtf(16);
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeUtf(emote, 16);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof ExoframeEntity exoframe) {
                exoframe.playEmote(emote);
            }
        });
        return true;
    }
}
