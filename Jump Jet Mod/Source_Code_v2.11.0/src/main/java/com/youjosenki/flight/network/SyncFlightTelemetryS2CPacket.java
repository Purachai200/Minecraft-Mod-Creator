package com.youjosenki.flight.network;

import com.youjosenki.flight.client.telemetry.ClientFlightTelemetry;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class SyncFlightTelemetryS2CPacket {
    private final float heat;
    private final boolean overheated;
    private final int serviceCeiling;
    private final int boostStep;

    public SyncFlightTelemetryS2CPacket(float heat, boolean overheated, int serviceCeiling, int boostStep) {
        this.heat = heat;
        this.overheated = overheated;
        this.serviceCeiling = serviceCeiling;
        this.boostStep = boostStep;
    }

    public SyncFlightTelemetryS2CPacket(FriendlyByteBuf buf) {
        this.heat = buf.readFloat();
        this.overheated = buf.readBoolean();
        this.serviceCeiling = buf.readInt();
        this.boostStep = buf.readInt();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeFloat(heat);
        buf.writeBoolean(overheated);
        buf.writeInt(serviceCeiling);
        buf.writeInt(boostStep);
    }

    public void handle(Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> {
                ClientFlightTelemetry.heat = this.heat;
                ClientFlightTelemetry.overheated = this.overheated;
                ClientFlightTelemetry.serviceCeiling = this.serviceCeiling;
                ClientFlightTelemetry.boostStep = this.boostStep;
            });
        });
        ctx.get().setPacketHandled(true);
    }
}
