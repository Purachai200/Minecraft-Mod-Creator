package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.NetworkHooks;

import java.util.function.Supplier;

/** Pilot pressed the inventory key while riding: open the exoframe's modular loadout screen. */
public class ExoframeOpenMenuC2SPacket {
    public ExoframeOpenMenuC2SPacket() {
    }

    public ExoframeOpenMenuC2SPacket(FriendlyByteBuf buf) {
    }

    public void toBytes(FriendlyByteBuf buf) {
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof ExoframeEntity exoframe && !exoframe.isDying()) {
                NetworkHooks.openScreen(player, exoframe, buf -> buf.writeInt(exoframe.getId()));
            }
        });
        return true;
    }
}
