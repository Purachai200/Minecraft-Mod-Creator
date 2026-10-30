package com.obsolete.network;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.client.Minecraft;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ExoframeInventorySyncS2CPacket {
    private final int entityId;
    private final int slot;
    private final ItemStack stack;

    public ExoframeInventorySyncS2CPacket(int entityId, int slot, ItemStack stack) {
        this.entityId = entityId;
        this.slot = slot;
        this.stack = stack;
    }

    public ExoframeInventorySyncS2CPacket(FriendlyByteBuf buf) {
        this.entityId = buf.readInt();
        this.slot = buf.readInt();
        this.stack = buf.readItem();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeInt(entityId);
        buf.writeInt(slot);
        buf.writeItem(stack);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> () -> {
            if (Minecraft.getInstance().level != null) {
                Entity entity = Minecraft.getInstance().level.getEntity(entityId);
                if (entity instanceof ExoframeEntity exoframe) {
                    exoframe.getModularInventory().setStackInSlot(slot, stack);
                }
            }
        }));
        return true;
    }
}
