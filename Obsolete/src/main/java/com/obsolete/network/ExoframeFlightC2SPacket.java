package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeFlightC2SPacket {
    private final boolean flying;
    private final boolean boosting;

    public ExoframeFlightC2SPacket(boolean flying, boolean boosting) {
        this.flying = flying;
        this.boosting = boosting;
    }

    public ExoframeFlightC2SPacket(FriendlyByteBuf buf) {
        this.flying = buf.readBoolean();
        this.boosting = buf.readBoolean();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeBoolean(flying);
        buf.writeBoolean(boosting);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof ExoframeEntity exoframe) {
                if (exoframe.hasFlightBooster()) {
                    exoframe.setFlying(flying);
                    exoframe.setFlightBoosting(boosting);
                } else {
                    exoframe.setFlying(false);
                    exoframe.setFlightBoosting(false);
                }
            }
        });
        return true;
    }
}
