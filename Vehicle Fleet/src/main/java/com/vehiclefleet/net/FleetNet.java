package com.vehiclefleet.net;

import com.vehiclefleet.VehicleFleetMod;
import com.vehiclefleet.entity.FleetVehicleEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

import java.util.function.Supplier;

public final class FleetNet {
    public static final int ACT_SEAT = 0, ACT_OPEN = 1, ACT_LIGHTS = 2, ACT_RELEASE = 3, ACT_HORN = 4;
    private static final String PROTOCOL = "1";
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(new ResourceLocation(VehicleFleetMod.MODID, "main"), () -> PROTOCOL, PROTOCOL::equals, PROTOCOL::equals);

    private FleetNet() {}

    public static void register() {
        CHANNEL.registerMessage(0, Input.class, Input::write, Input::new, Input::handle);
        CHANNEL.registerMessage(1, Action.class, Action::write, Action::new, Action::handle);
    }

    /** Held-key state while riding: bit 1 = climb, bit 2 = descend. */
    public static final class Input {
        public final byte flags;

        public Input(byte flags) { this.flags = flags; }

        Input(FriendlyByteBuf b) { this.flags = b.readByte(); }

        void write(FriendlyByteBuf b) { b.writeByte(flags); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            ctx.get().enqueueWork(() -> {
                ServerPlayer p = ctx.get().getSender();
                if (p != null && p.getVehicle() instanceof FleetVehicleEntity v) v.setInput(p, flags);
            });
            ctx.get().setPacketHandled(true);
        }
    }

    /** One-shot actions: seat switch, open/close ramp or doors, lights, release cargo. */
    public static final class Action {
        public final int id;

        public Action(int id) { this.id = id; }

        Action(FriendlyByteBuf b) { this.id = b.readVarInt(); }

        void write(FriendlyByteBuf b) { b.writeVarInt(id); }

        void handle(Supplier<NetworkEvent.Context> ctx) {
            ctx.get().enqueueWork(() -> {
                ServerPlayer p = ctx.get().getSender();
                if (p != null) FleetVehicleEntity.handleAction(p, id);
            });
            ctx.get().setPacketHandled(true);
        }
    }
}
