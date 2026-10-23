package com.youjosenki.flight.energy;

import com.youjosenki.flight.Config;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.energy.IEnergyStorage;

public class ItemEnergyStorage implements IEnergyStorage {
    public static final String ENERGY_KEY = "Energy";
    private final ItemStack stack;
    private final int capacity;
    private final int maxReceive;
    private final int maxExtract;

    public ItemEnergyStorage(ItemStack stack) {
        int cap = Config.COMMON.maxEnergy.get();
        if (stack.getItem() instanceof EleniumFlightUnitItem item) {
            cap = item.getMaxEnergyCapacity();
        }
        this.stack = stack;
        this.capacity = cap;
        this.maxReceive = Config.COMMON.maxReceive.get();
        this.maxExtract = Config.COMMON.sprintEnergyCost.get() * 2;
    }

    public ItemEnergyStorage(ItemStack stack, int capacity, int maxReceive, int maxExtract) {
        this.stack = stack;
        this.capacity = capacity;
        this.maxReceive = maxReceive;
        this.maxExtract = maxExtract;
    }

    @Override
    public int receiveEnergy(int maxReceive, boolean simulate) {
        if (!canReceive()) return 0;

        int energyStored = getEnergyStored();
        int energyReceived = Math.min(capacity - energyStored, Math.min(this.maxReceive, maxReceive));
        if (!simulate && energyReceived > 0) {
            setEnergyStored(energyStored + energyReceived);
        }
        return energyReceived;
    }

    @Override
    public int extractEnergy(int maxExtract, boolean simulate) {
        if (!canExtract()) return 0;

        int energyStored = getEnergyStored();
        int energyExtracted = Math.min(energyStored, maxExtract);
        if (!simulate && energyExtracted > 0) {
            setEnergyStored(energyStored - energyExtracted);
        }
        return energyExtracted;
    }

    @Override
    public int getEnergyStored() {
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains(ENERGY_KEY)) {
            return capacity;
        }
        return tag.getInt(ENERGY_KEY);
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
        return true;
    }

    @Override
    public boolean canReceive() {
        return maxReceive > 0;
    }
}
