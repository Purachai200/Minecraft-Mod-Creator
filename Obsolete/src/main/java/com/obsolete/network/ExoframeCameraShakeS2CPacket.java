package com.obsolete.network;

import com.obsolete.client.CameraShakeManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeCameraShakeS2CPacket {
    private final float intensity;
    private final int ticks;

    public ExoframeCameraShakeS2CPacket(float intensity, int ticks) {
        this.intensity = intensity;
        this.ticks = ticks;
    }

    public ExoframeCameraShakeS2CPacket(FriendlyByteBuf buf) {
        this.intensity = buf.readFloat();
        this.ticks = buf.readInt();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeFloat(this.intensity);
        buf.writeInt(this.ticks);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> CameraShakeManager.addShake(this.intensity, this.ticks));
        });
        return true;
    }
}
