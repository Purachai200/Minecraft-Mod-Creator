package com.titancombat.network;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * Trigger held this tick, with the world point under the pilot's crosshair as the client sees it
 * (from the real camera, first or third person), so rounds land where the reticle points.
 */
public class TitanFireC2SPacket {
    private final Vec3 aim;

    public TitanFireC2SPacket(Vec3 aim) {
        this.aim = aim;
    }

    public TitanFireC2SPacket(FriendlyByteBuf buf) {
        this.aim = new Vec3(buf.readDouble(), buf.readDouble(), buf.readDouble());
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeDouble(aim.x);
        buf.writeDouble(aim.y);
        buf.writeDouble(aim.z);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null && player.getVehicle() instanceof BaseTitanEntity titan) {
                titan.setPilotAim(aim);
                titan.firePrimaryWeapon(player);
            }
        });
        return true;
    }
}
