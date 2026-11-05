package com.youjoarms.network;

import com.youjoarms.capability.PlayerMageData;
import com.youjoarms.capability.PlayerMageProvider;
import com.youjoarms.formula.FormulaType;
import net.minecraft.client.Minecraft;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class PacketSyncMageDataS2C {
    private final int entityId;
    private final int mana;
    private final int formulaId;
    private final boolean charging;
    private final int chargeTicks;
    private final int shieldTicks;

    public PacketSyncMageDataS2C(Player player, PlayerMageData cap) {
        this.entityId = player.getId();
        this.mana = cap.getMana();
        this.formulaId = cap.getSelectedFormula().getId();
        this.charging = cap.isCharging();
        this.chargeTicks = cap.getChargeTicks();
        this.shieldTicks = cap.getShieldTicks();
    }

    public PacketSyncMageDataS2C(FriendlyByteBuf buf) {
        this.entityId = buf.readVarInt();
        this.mana = buf.readVarInt();
        this.formulaId = buf.readVarInt();
        this.charging = buf.readBoolean();
        this.chargeTicks = buf.readVarInt();
        this.shieldTicks = buf.readVarInt();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeVarInt(entityId);
        buf.writeVarInt(mana);
        buf.writeVarInt(formulaId);
        buf.writeBoolean(charging);
        buf.writeVarInt(chargeTicks);
        buf.writeVarInt(shieldTicks);
    }

    public void handle(Supplier<NetworkEvent.Context> ctxSupplier) {
        NetworkEvent.Context ctx = ctxSupplier.get();
        ctx.enqueueWork(() -> {
            if (Minecraft.getInstance().level != null) {
                Entity entity = Minecraft.getInstance().level.getEntity(entityId);
                if (entity instanceof Player player) {
                    player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
                        cap.setMana(mana);
                        cap.setSelectedFormula(FormulaType.byId(formulaId));
                        cap.setCharging(charging);
                        cap.setChargeTicks(chargeTicks);
                        cap.setShieldTicks(shieldTicks);
                    });
                }
            }
        });
        ctx.setPacketHandled(true);
    }
}
