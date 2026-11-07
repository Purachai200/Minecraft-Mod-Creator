package com.youjoarms.network;

import com.youjoarms.capability.PlayerMageProvider;
import com.youjoarms.formula.FormulaType;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;

import java.util.function.Supplier;

public class PacketCastKeyC2S {
    private final boolean pressed;
    private final boolean cycleFormula;

    public PacketCastKeyC2S(boolean pressed, boolean cycleFormula) {
        this.pressed = pressed;
        this.cycleFormula = cycleFormula;
    }

    public PacketCastKeyC2S(FriendlyByteBuf buf) {
        this.pressed = buf.readBoolean();
        this.cycleFormula = buf.readBoolean();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeBoolean(pressed);
        buf.writeBoolean(cycleFormula);
    }

    public void handle(Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        ctx.enqueueWork(() -> {
            ServerPlayer player = ctx.getSender();
            // releasing is always allowed; starting a charge or cycling needs one of our guns in hand
            if (player != null && ((!pressed && !cycleFormula) || com.youjoarms.mana.GunMana.isOurs(player.getMainHandItem()))) {
                player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
                    if (cycleFormula) {
                        cap.setSelectedFormula(cap.getSelectedFormula().next());
                    } else {
                        cap.setCharging(pressed);
                    }
                    // Sync to all tracking clients (and self) so magic circles render for everyone
                    PacketSyncMageDataS2C packet = new PacketSyncMageDataS2C(player, cap);
                    YoujoArmsNetwork.CHANNEL.send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> player), packet);
                });
            }
        });
        ctx.setPacketHandled(true);
    }
}
