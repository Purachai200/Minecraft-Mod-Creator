package com.obsolete.energy;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.energy.IEnergyStorage;

public class ItemEnergyStorage implements IEnergyStorage {
    public static final String ENERGY_KEY = "Energy";
    private final ItemStack stack;
    private final int capacity;
    private final int maxReceive;
    private final int maxExtract;

    public ItemEnergyStorage(ItemStack stack, int capacity, int maxReceive, int maxExtract) {
        this.stack = stack;
        this.capacity = capacity;
        this.maxReceive = maxReceive;
        this.maxExtract = maxExtract;
    }

    @Override
    public int receiveEnergy(int maxReceive, boolean simulate) {
        if (!canReceive()) return 0;
        int stored = getEnergyStored();
        int received = Math.min(capacity - stored, Math.min(this.maxReceive, maxReceive));
        if (!simulate && received > 0) {
            setEnergyStored(stored + received);
        }
        return received;
    }

    @Override
    public int extractEnergy(int maxExtract, boolean simulate) {
        if (!canExtract()) return 0;
        int stored = getEnergyStored();
        int extracted = Math.min(stored, Math.min(this.maxExtract, maxExtract));
        if (!simulate && extracted > 0) {
            setEnergyStored(stored - extracted);
        }
        return extracted;
    }

    @Override
    public int getEnergyStored() {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(ENERGY_KEY)) {
            // Freshly spawned items start fully charged
            return capacity;
        }
        return Math.min(capacity, tag.getInt(ENERGY_KEY));
    }

    public void setEnergyStored(int energy) {
        CompoundTag tag = stack.getOrCreateTag();
        tag.putInt(ENERGY_KEY, Math.max(0, Math.min(capacity, energy)));
    }

    @Override
    public int getMaxEnergyStored() {
        return capacity;
    }

    @Override
    public boolean canExtract() {
        return maxExtract > 0;
    }

    @Override
    public boolean canReceive() {
        return maxReceive > 0;
    }
}
