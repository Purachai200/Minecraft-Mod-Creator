package com.obsolete.energy;

import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.energy.IEnergyStorage;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class EnergyCapabilityProvider implements ICapabilityProvider {
    private final ItemStack stack;
    private final ItemEnergyStorage energyStorage;
    private final LazyOptional<IEnergyStorage> lazyOptional;

    public EnergyCapabilityProvider(ItemStack stack, int capacity, int maxReceive, int maxExtract) {
        this.stack = stack;
        this.energyStorage = new ItemEnergyStorage(stack, capacity, maxReceive, maxExtract);
        this.lazyOptional = LazyOptional.of(() -> energyStorage);
    }

    @Override
    public @NotNull <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
        if (cap == ForgeCapabilities.ENERGY) {
            return lazyOptional.cast();
        }
        return LazyOptional.empty();
    }
}
