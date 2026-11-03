package com.titancombat.assembly;

import com.titancombat.block.ModBlocks;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** Client asks the bay at {@code pos} to build blueprint {@code index}; the server re-checks distance and parts. */
public class AssembleVehicleC2SPacket {
    private final BlockPos pos;
    private final int index;

    public AssembleVehicleC2SPacket(BlockPos pos, int index) {
        this.pos = pos;
        this.index = index;
    }

    public AssembleVehicleC2SPacket(FriendlyByteBuf buf) {
        this.pos = buf.readBlockPos();
        this.index = buf.readVarInt();
    }

    public void toBytes(FriendlyByteBuf buf) {
        buf.writeBlockPos(this.pos);
        buf.writeVarInt(this.index);
    }

    public boolean handle(Supplier<NetworkEvent.Context> supplier) {
        NetworkEvent.Context context = supplier.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player == null || this.index < 0 || this.index >= VehicleBlueprints.ALL.size()) return;
            if (player.distanceToSqr(this.pos.getCenter()) > 64.0D || !player.level().getBlockState(this.pos).is(ModBlocks.VEHICLE_ASSEMBLY_BAY.get())) return;
            VehicleBlueprints.Blueprint bp = VehicleBlueprints.ALL.get(this.index);
            if (!VehicleBlueprints.canAfford(player, bp)) {
                player.displayClientMessage(Component.literal("§c[ASSEMBLY] Missing components for this vehicle."), true);
                return;
            }
            VehicleBlueprints.consume(player, bp);
            ItemStack out = new ItemStack(bp.result().get());
            if (!player.getInventory().add(out)) player.drop(out, false);
            player.level().playSound(null, this.pos, SoundEvents.ANVIL_USE, SoundSource.BLOCKS, 1.0F, 0.8F);
            player.level().playSound(null, this.pos, SoundEvents.PISTON_EXTEND, SoundSource.BLOCKS, 1.0F, 0.7F);
            player.displayClientMessage(Component.literal("§a[ASSEMBLY] " + out.getHoverName().getString() + " assembled and ready to deploy."), true);
        });
        return true;
    }
}
