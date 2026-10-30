package com.obsolete.block.entity;

import com.obsolete.gui.MechAssemblyMenu;
import com.obsolete.recipe.MechAssemblyRecipe;
import com.obsolete.recipe.ModRecipeTypes;
import com.obsolete.sound.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.IItemHandler;
import net.minecraftforge.items.wrapper.InvWrapper;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.util.Optional;

public class MechAssemblyStationBlockEntity extends BlockEntity implements Container, MenuProvider {
    public static final int INPUT_SLOTS = 4;
    public static final int OUTPUT_SLOT = 4;
    public static final int TOTAL_SLOTS = 5;

    private final NonNullList<ItemStack> items = NonNullList.withSize(TOTAL_SLOTS, ItemStack.EMPTY);
    private int progress = 0;
    private int maxProgress = 100;

    protected final ContainerData dataAccess = new ContainerData() {
        @Override
        public int get(int index) {
            return switch (index) {
                case 0 -> progress;
                case 1 -> maxProgress;
                default -> 0;
            };
        }

        @Override
        public void set(int index, int value) {
            switch (index) {
                case 0 -> progress = value;
                case 1 -> maxProgress = value;
            }
        }

        @Override
        public int getCount() {
            return 2;
        }
    };

    private LazyOptional<IItemHandler> itemHandler = LazyOptional.of(() -> new InvWrapper(this));

    public MechAssemblyStationBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.MECH_ASSEMBLY_STATION.get(), pos, state);
    }

    public static void tick(Level level, BlockPos pos, BlockState state, MechAssemblyStationBlockEntity blockEntity) {
        if (level.isClientSide) return;

        Optional<MechAssemblyRecipe> match = level.getRecipeManager()
                .getRecipeFor(ModRecipeTypes.MECH_ASSEMBLY.get(), blockEntity, level);

        if (match.isPresent()) {
            MechAssemblyRecipe recipe = match.get();
            blockEntity.maxProgress = recipe.getAssembleTime();

            if (blockEntity.canOutput(recipe.getResultItem(level.registryAccess()))) {
                blockEntity.progress++;
                if (blockEntity.progress >= blockEntity.maxProgress) {
                    blockEntity.craftItem(recipe);
                    blockEntity.progress = 0;
                    level.playSound(null, pos, ModSounds.ASSEMBLY_PROCESS.get(), SoundSource.BLOCKS, 1.2F, 1.0F);
                }
                setChanged(level, pos, state);
                return;
            }
        }

        if (blockEntity.progress != 0) {
            blockEntity.progress = 0;
            setChanged(level, pos, state);
        }
    }

    private boolean canOutput(ItemStack result) {
        ItemStack outputSlot = items.get(OUTPUT_SLOT);
        if (outputSlot.isEmpty()) return true;
        if (!ItemStack.isSameItemSameTags(outputSlot, result)) return false;
        return outputSlot.getCount() + result.getCount() <= outputSlot.getMaxStackSize();
    }

    private void craftItem(MechAssemblyRecipe recipe) {
        Level level = this.getLevel();
        if (level == null) return;

        ItemStack result = recipe.assemble(this, level.registryAccess());
        ItemStack currentOutput = items.get(OUTPUT_SLOT);

        if (currentOutput.isEmpty()) {
            items.set(OUTPUT_SLOT, result);
        } else if (ItemStack.isSameItemSameTags(currentOutput, result)) {
            currentOutput.grow(result.getCount());
        }

        // Consume 1 from each input
        for (int i = 0; i < INPUT_SLOTS; i++) {
            ItemStack stack = items.get(i);
            if (!stack.isEmpty()) {
                stack.shrink(1);
            }
        }
    }

    @Override
    public int getContainerSize() {
        return TOTAL_SLOTS;
    }

    @Override
    public boolean isEmpty() {
        for (ItemStack item : items) {
            if (!item.isEmpty()) return false;
        }
        return true;
    }

    @Override
    public @NotNull ItemStack getItem(int slot) {
        return items.get(slot);
    }

    @Override
    public @NotNull ItemStack removeItem(int slot, int amount) {
        ItemStack res = ContainerHelper.removeItem(items, slot, amount);
        if (!res.isEmpty()) setChanged();
        return res;
    }

    @Override
    public @NotNull ItemStack removeItemNoUpdate(int slot) {
        return ContainerHelper.takeItem(items, slot);
    }

    @Override
    public void setItem(int slot, @NotNull ItemStack stack) {
        items.set(slot, stack);
        if (stack.getCount() > getMaxStackSize()) {
            stack.setCount(getMaxStackSize());
        }
        setChanged();
    }

    @Override
    public boolean stillValid(@NotNull Player player) {
        return Container.stillValidBlockEntity(this, player);
    }

    @Override
    public void clearContent() {
        items.clear();
        setChanged();
    }

    @Override
    public @NotNull Component getDisplayName() {
        return Component.translatable("container.obsolete.mech_assembly_station");
    }

    @Nullable
    @Override
    public AbstractContainerMenu createMenu(int containerId, @NotNull Inventory playerInventory, @NotNull Player player) {
        return new MechAssemblyMenu(containerId, playerInventory, this, this.dataAccess);
    }

    @Override
    public @NotNull <T> LazyOptional<T> getCapability(@NotNull Capability<T> cap, @Nullable Direction side) {
        if (cap == ForgeCapabilities.ITEM_HANDLER) {
            return itemHandler.cast();
        }
        return super.getCapability(cap, side);
    }

    @Override
    public void invalidateCaps() {
        super.invalidateCaps();
        itemHandler.invalidate();
    }

    @Override
    protected void saveAdditional(@NotNull CompoundTag tag) {
        super.saveAdditional(tag);
        ContainerHelper.saveAllItems(tag, items);
        tag.putInt("Progress", progress);
        tag.putInt("MaxProgress", maxProgress);
    }

    @Override
    public void load(@NotNull CompoundTag tag) {
        super.load(tag);
        items.clear();
        ContainerHelper.loadAllItems(tag, items);
        progress = tag.getInt("Progress");
        maxProgress = tag.getInt("MaxProgress");
    }
}
