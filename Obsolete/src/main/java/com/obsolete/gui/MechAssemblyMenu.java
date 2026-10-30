package com.obsolete.gui;

import com.obsolete.block.entity.MechAssemblyStationBlockEntity;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import org.jetbrains.annotations.NotNull;

public class MechAssemblyMenu extends AbstractContainerMenu {
    private final Container container;
    private final ContainerData data;

    // Client-side constructor
    public MechAssemblyMenu(int containerId, Inventory playerInventory, FriendlyByteBuf buf) {
        this(containerId, playerInventory, new SimpleContainer(MechAssemblyStationBlockEntity.TOTAL_SLOTS), new SimpleContainerData(2));
    }

    // Server-side constructor
    public MechAssemblyMenu(int containerId, Inventory playerInventory, Container container, ContainerData data) {
        super(ModMenuTypes.MECH_ASSEMBLY_MENU.get(), containerId);
        checkContainerSize(container, MechAssemblyStationBlockEntity.TOTAL_SLOTS);
        this.container = container;
        this.data = data;

        // 4 Input component slots in a 2x2 grid
        this.addSlot(new Slot(container, 0, 44, 26));
        this.addSlot(new Slot(container, 1, 64, 26));
        this.addSlot(new Slot(container, 2, 44, 46));
        this.addSlot(new Slot(container, 3, 64, 46));

        // 1 Output assembly slot
        this.addSlot(new Slot(container, 4, 124, 36) {
            @Override
            public boolean mayPlace(@NotNull ItemStack stack) {
                return false;
            }
        });

        // Player Inventory
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                this.addSlot(new Slot(playerInventory, col + row * 9 + 9, 8 + col * 18, 84 + row * 18));
            }
        }

        // Player Hotbar
        for (int col = 0; col < 9; ++col) {
            this.addSlot(new Slot(playerInventory, col, 8 + col * 18, 142));
        }

        this.addDataSlots(data);
    }

    public boolean isCrafting() {
        return data.get(0) > 0;
    }

    public int getScaledProgress() {
        int progress = this.data.get(0);
        int maxProgress = this.data.get(1);
        int progressArrowSize = 24; // Pixel width of progress bar
        return maxProgress != 0 && progress != 0 ? progress * progressArrowSize / maxProgress : 0;
    }

    @Override
    public boolean stillValid(@NotNull Player player) {
        return this.container.stillValid(player);
    }

    @Override
    public @NotNull ItemStack quickMoveStack(@NotNull Player player, int index) {
        ItemStack itemstack = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot != null && slot.hasItem()) {
            ItemStack itemstack1 = slot.getItem();
            itemstack = itemstack1.copy();

            if (index == 4) {
                // Take from output to player inventory
                if (!this.moveItemStackTo(itemstack1, 5, 41, true)) {
                    return ItemStack.EMPTY;
                }
                slot.onQuickCraft(itemstack1, itemstack);
            } else if (index < 4) {
                // Move from inputs to player inventory
                if (!this.moveItemStackTo(itemstack1, 5, 41, false)) {
                    return ItemStack.EMPTY;
                }
            } else {
                // Move from player inventory to inputs
                if (!this.moveItemStackTo(itemstack1, 0, 4, false)) {
                    return ItemStack.EMPTY;
                }
            }

            if (itemstack1.isEmpty()) {
                slot.setByPlayer(ItemStack.EMPTY);
            } else {
                slot.setChanged();
            }

            if (itemstack1.getCount() == itemstack.getCount()) {
                return ItemStack.EMPTY;
            }

            slot.onTake(player, itemstack1);
        }
        return itemstack;
    }
}
