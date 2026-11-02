package com.titancombat.network;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class OpenTitanInventoryC2SPacket {
    private final int entityId;

    public OpenTitanInventoryC2SPacket(int entityId) {
        this.entityId = entityId;
    }

    public OpenTitanInventoryC2SPacket(FriendlyByteBuf buf) {
        this.entityId = buf.readInt();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeInt(this.entityId);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null) {
                Entity entity = player.level().getEntity(this.entityId);
                if (entity instanceof BaseTitanEntity titan && player.distanceToSqr(titan) <= 64.0D) {
                    titan.openCustomInventoryScreen(player);
                }
            }
        });
        return true;
    }
}
