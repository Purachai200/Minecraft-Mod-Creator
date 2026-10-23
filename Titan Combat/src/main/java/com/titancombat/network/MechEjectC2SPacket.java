package com.titancombat.network;

import com.titancombat.entity.BaseMechEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class MechEjectC2SPacket {

    public MechEjectC2SPacket() {}

    public MechEjectC2SPacket(FriendlyByteBuf buf) {}

    public void toBytes(FriendlyByteBuf buf) {}

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof BaseMechEntity mech) {
                mech.ejectPilot();
            }
        });
        return true;
    }
}
