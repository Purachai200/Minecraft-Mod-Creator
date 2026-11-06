package com.titancombat.network;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class OpenTitanInventoryC2SPacket {
    private final int entityId;
    /** Open the 27-slot cargo hold instead of the bay screen. */
    private final boolean cargoHold;

    public OpenTitanInventoryC2SPacket(int entityId) {
        this(entityId, false);
    }

    public OpenTitanInventoryC2SPacket(int entityId, boolean cargoHold) {
        this.entityId = entityId;
        this.cargoHold = cargoHold;
    }

    public OpenTitanInventoryC2SPacket(FriendlyByteBuf buf) {
        this.entityId = buf.readInt();
        this.cargoHold = buf.readBoolean();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeInt(this.entityId);
        buf.writeBoolean(this.cargoHold);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null) {
                Entity entity = player.level().getEntity(this.entityId);
                if (entity instanceof BaseTitanEntity titan && player.distanceToSqr(titan) <= 64.0D) {
                    if (this.cargoHold) {
                        player.openMenu(new net.minecraft.world.SimpleMenuProvider((id, inv, p) -> net.minecraft.world.inventory.ChestMenu.threeRows(id, inv,
                                new com.titancombat.gui.TitanCargoHold(titan)), net.minecraft.network.chat.Component.translatable("gui.titancombat.bay.cargo_hold")));
                    } else {
                        titan.openCustomInventoryScreen(player);
                    }
                }
            }
        });
        return true;
    }
}
