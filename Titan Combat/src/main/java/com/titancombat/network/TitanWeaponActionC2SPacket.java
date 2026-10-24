package com.titancombat.network;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Pilot weapon handling that isn't the trigger: reload, holster/draw. */
public class TitanWeaponActionC2SPacket {
    public static final byte RELOAD = 0;
    public static final byte TOGGLE_LOWERED = 1;
    public static final byte SALUTE = 2;
    public static final byte FLIGHT_START = 3;
    public static final byte FLIGHT_STOP = 4;

    private final byte action;

    public TitanWeaponActionC2SPacket(byte action) {
        this.action = action;
    }

    public TitanWeaponActionC2SPacket(FriendlyByteBuf buf) {
        this.action = buf.readByte();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeByte(this.action);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof BaseTitanEntity titan) {
                switch (this.action) {
                    case RELOAD -> titan.startReload(player);
                    case TOGGLE_LOWERED -> titan.toggleWeaponLowered(player);
                    case SALUTE -> titan.triggerSalute(player);
                    case FLIGHT_START -> titan.setFlightThrust(true);
                    case FLIGHT_STOP -> titan.setFlightThrust(false);
                    default -> {}
                }
            }
        });
        return true;
    }
}
