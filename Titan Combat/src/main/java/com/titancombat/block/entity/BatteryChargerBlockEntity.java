package com.titancombat.block.entity;

import com.titancombat.item.ModItems;
import com.titancombat.item.TitanBatteryItem;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.energy.EnergyStorage;
import net.minecraftforge.energy.IEnergyStorage;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class BatteryChargerBlockEntity extends BlockEntity {
    public static final int MAX_ENERGY = 500000;
    public static final int MAX_RECEIVE = 10000;

    private ItemStack batterySlot = ItemStack.EMPTY;
    private int batteryProgress = 0;

    private final CustomEnergyStorage energyStorage = new CustomEnergyStorage(MAX_ENERGY, MAX_RECEIVE);
    private final LazyOptional<IEnergyStorage> energyOptional = LazyOptional.of(() -> energyStorage);

    public BatteryChargerBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.BATTERY_CHARGER.get(), pos, state);
    }

    public static void serverTick(Level level, BlockPos pos, BlockState state, BatteryChargerBlockEntity entity) {
        if (!entity.batterySlot.isEmpty() && entity.batterySlot.getItem() instanceof TitanBatteryItem) {
            int currentEnergy = TitanBatteryItem.getEnergy(entity.batterySlot);
            int batCapacity = TitanBatteryItem.getCapacity(entity.batterySlot);
            if (currentEnergy < batCapacity && entity.energyStorage.getEnergyStored() > 0) {
                int needed = batCapacity - currentEnergy;
                int toTransfer = Math.min(500, Math.min(entity.energyStorage.getEnergyStored(), needed));
                entity.energyStorage.consumeEnergy(toTransfer);
                int newEnergy = currentEnergy + toTransfer;
                entity.batteryProgress = newEnergy;

                TitanBatteryItem.setEnergy(entity.batterySlot, newEnergy);
                if (newEnergy >= batCapacity) {
                    level.playSound(null, pos, SoundEvents.PLAYER_LEVELUP, SoundSource.BLOCKS, 1.0F, 1.2F);
                }
                entity.setChanged();
                level.sendBlockUpdated(pos, state, state, 3);
            }
        }
    }

    public ItemStack getBatterySlot() {
        return batterySlot;
    }

    public void setBatterySlot(ItemStack stack) {
        this.batterySlot = stack;
        this.batteryProgress = stack.isEmpty() ? 0 : TitanBatteryItem.getEnergy(stack);
        setChanged();
        if (this.level != null && !this.level.isClientSide) {
            this.level.sendBlockUpdated(this.worldPosition, getBlockState(), getBlockState(), 3);
        }
    }

    public int getBatteryProgress() {
        return batteryProgress;
    }

    public int getEnergyStored() {
        return energyStorage.getEnergyStored();
    }

    public int getMaxEnergyStored() {
        return energyStorage.getMaxEnergyStored();
    }

    public void addEnergy(int amount) {
        energyStorage.addEnergy(amount);
        setChanged();
        if (this.level != null && !this.level.isClientSide) {
            this.level.sendBlockUpdated(this.worldPosition, getBlockState(), getBlockState(), 3);
        }
    }

    @Override
    public @NotNull <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
        if (cap == ForgeCapabilities.ENERGY) {
            return energyOptional.cast();
        }
        return super.getCapability(cap, side);
    }

    @Override
    public void invalidateCaps() {
        super.invalidateCaps();
        energyOptional.invalidate();
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt("Energy", this.energyStorage.getEnergyStored());
        tag.putInt("BatteryProgress", this.batteryProgress);
        if (!this.batterySlot.isEmpty()) {
            CompoundTag itemTag = new CompoundTag();
            this.batterySlot.save(itemTag);
            tag.put("BatterySlot", itemTag);
        }
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        this.energyStorage.setEnergy(tag.getInt("Energy"));
        this.batteryProgress = tag.getInt("BatteryProgress");
        if (tag.contains("BatterySlot")) {
            this.batterySlot = ItemStack.of(tag.getCompound("BatterySlot"));
        } else {
            this.batterySlot = ItemStack.EMPTY;
        }
    }

    @Override
    public CompoundTag getUpdateTag() {
        CompoundTag tag = super.getUpdateTag();
        saveAdditional(tag);
        return tag;
    }

    @Nullable
    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }

    public static class CustomEnergyStorage extends EnergyStorage {
        public CustomEnergyStorage(int capacity, int maxReceive) {
            super(capacity, maxReceive, 0);
        }

        public void addEnergy(int amount) {
            this.energy = Math.min(this.capacity, this.energy + amount);
        }

        public void setEnergy(int amount) {
            this.energy = Math.max(0, Math.min(this.capacity, amount));
        }

        public void consumeEnergy(int amount) {
            this.energy = Math.max(0, this.energy - amount);
        }
    }
}
