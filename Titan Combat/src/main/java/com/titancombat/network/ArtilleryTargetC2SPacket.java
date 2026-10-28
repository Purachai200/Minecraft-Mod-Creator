package com.titancombat.network;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * Pilot sets the howitzer's target: a rangefinder mark, a map click or typed coordinates (no y = on the
 * ground there). With `fire`, the howitzer fires by itself once it has laid onto the new target.
 */
public class ArtilleryTargetC2SPacket {
    private final int x, z;
    private final boolean hasY;
    private final int y;
    private final boolean fire;

    public ArtilleryTargetC2SPacket(int x, boolean hasY, int y, int z) {
        this(x, hasY, y, z, false);
    }

    public ArtilleryTargetC2SPacket(int x, boolean hasY, int y, int z, boolean fire) {
        this.x = x;
        this.hasY = hasY;
        this.y = y;
        this.z = z;
        this.fire = fire;
    }

    public ArtilleryTargetC2SPacket(FriendlyByteBuf buf) {
        this(buf.readInt(), buf.readBoolean(), buf.readInt(), buf.readInt(), buf.readBoolean());
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeInt(x);
        buf.writeBoolean(hasY);
        buf.writeInt(y);
        buf.writeInt(z);
        buf.writeBoolean(fire);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            // Range and build-height checks happen in setArtilleryTarget.
            if (player != null && player.getVehicle() instanceof BaseTitanEntity titan && titan.hasHowitzer()
                    && titan.setArtilleryTarget(player, x, hasY ? y : null, z) && fire) {
                titan.requestHowitzerFire(player, true);
            }
        });
        return true;
    }
}
