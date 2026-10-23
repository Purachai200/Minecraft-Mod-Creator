package com.youjosenki.flight.network;

import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

public class ToggleFlightC2SPacket {
    private final int mode; // 0 = toggle, 1 = force enable, 2 = force disable

    public ToggleFlightC2SPacket() {
        this(0);
    }

    public ToggleFlightC2SPacket(int mode) {
        this.mode = mode;
    }

    public ToggleFlightC2SPacket(FriendlyByteBuf buf) {
        this.mode = buf.readByte();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeByte(this.mode);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null) return;

            ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
            String unitName = (unit != null && !unit.isEmpty()) ? unit.getHoverName().getString() : "Flight Unit";

            if (EleniumFlightUnitItem.hasEnergizedFlightUnit(player)) {
                boolean currentlyFlying = player.getAbilities().flying;
                boolean shouldFly = (mode == 1) ? true : (mode == 2 ? false : !currentlyFlying);

                // Update server flight state cleanly
                player.getAbilities().mayfly = true;
                player.getAbilities().flying = shouldFly;

                if (shouldFly) {
                    player.setOnGround(false);
                    player.setPos(player.getX(), player.getY() + 0.15, player.getZ());
                    Vec3 v = player.getDeltaMovement();
                    player.setDeltaMovement(v.x, Math.max(v.y, 0.20), v.z);
                    player.fallDistance = 0.0F;

                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 0.6F, 1.8F);
                    player.displayClientMessage(Component.translatable("message.youjosenki.flight_on", unitName), true);
                } else {
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.BEACON_DEACTIVATE, SoundSource.PLAYERS, 0.5F, 1.6F);
                    player.displayClientMessage(Component.translatable("message.youjosenki.flight_off", unitName), true);
                }

                player.onUpdateAbilities();
            } else {
                player.displayClientMessage(Component.translatable("message.youjosenki.no_energy", unitName), true);
            }
        });
        return true;
    }
}
