package com.youjoarms.capability;

import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.common.capabilities.*;
import net.minecraftforge.common.util.INBTSerializable;
import net.minecraftforge.common.util.LazyOptional;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class PlayerMageProvider implements ICapabilityProvider, INBTSerializable<CompoundTag> {
    public static final Capability<PlayerMageData> MAGE_DATA = CapabilityManager.get(new CapabilityToken<>() {});

    private final PlayerMageData backend = new PlayerMageData();
    private final LazyOptional<PlayerMageData> optional = LazyOptional.of(() -> backend);

    @Override
    public @NotNull <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
        if (cap == MAGE_DATA) {
            return optional.cast();
        }
        return LazyOptional.empty();
    }

    @Override
    public CompoundTag serializeNBT() {
        return backend.serializeNBT();
    }

    @Override
    public void deserializeNBT(CompoundTag nbt) {
        backend.deserializeNBT(nbt);
    }
}
