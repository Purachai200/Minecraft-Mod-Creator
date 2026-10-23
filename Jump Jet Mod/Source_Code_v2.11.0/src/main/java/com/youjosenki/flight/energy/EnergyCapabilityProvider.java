package com.youjosenki.flight.energy;

import com.youjosenki.flight.compat.curios.CuriosCompat;
import com.youjosenki.flight.compat.curios.FlightUnitCurio;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.capabilities.ICapabilitySerializable;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.energy.IEnergyStorage;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class EnergyCapabilityProvider implements ICapabilitySerializable<CompoundTag> {
    private final ItemStack stack;
    private final ItemEnergyStorage energyStorage;
    private final LazyOptional<IEnergyStorage> energyHolder;
    private final Object curioHolder;

    public EnergyCapabilityProvider(ItemStack stack) {
        this.stack = stack;
        this.energyStorage = new ItemEnergyStorage(stack);
        this.energyHolder = LazyOptional.of(() -> this.energyStorage);

        if (CuriosCompat.isCuriosLoaded() && stack.getItem() instanceof EleniumFlightUnitItem item) {
            this.curioHolder = CuriosIntegration.createCurioHolder(stack, item);
        } else {
            this.curioHolder = null;
        }
    }

    @Override
    public @NotNull <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
        if (cap == ForgeCapabilities.ENERGY) {
            return energyHolder.cast();
        }
        if (CuriosCompat.isCuriosLoaded() && curioHolder != null) {
            LazyOptional<T> curioCap = CuriosIntegration.getCurioCapability(cap, curioHolder);
            if (curioCap != null && curioCap.isPresent()) {
                return curioCap;
            }
        }
        return LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        CompoundTag tag = new CompoundTag();
        tag.putInt(ItemEnergyStorage.ENERGY_KEY, energyStorage.getEnergyStored());
        return tag;
    }

    @Override
    public void deserializeNBT(CompoundTag nbt) {
        if (nbt != null && nbt.contains(ItemEnergyStorage.ENERGY_KEY)) {
            energyStorage.setEnergyStored(nbt.getInt(ItemEnergyStorage.ENERGY_KEY));
        }
    }

    private static class CuriosIntegration {
        static LazyOptional<top.theillusivec4.curios.api.type.capability.ICurio> createCurioHolder(ItemStack stack, EleniumFlightUnitItem item) {
            return LazyOptional.of(() -> new FlightUnitCurio(stack, item));
        }

        @SuppressWarnings("unchecked")
        static <T> LazyOptional<T> getCurioCapability(Capability<T> cap, Object curioHolder) {
            if (cap == top.theillusivec4.curios.api.CuriosCapability.ITEM) {
                return ((LazyOptional<top.theillusivec4.curios.api.type.capability.ICurio>) curioHolder).cast();
            }
            return LazyOptional.empty();
        }
    }
}
