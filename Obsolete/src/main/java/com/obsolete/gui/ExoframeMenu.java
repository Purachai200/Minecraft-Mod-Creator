package com.obsolete.gui;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.entity.inventory.ExoframeInventory;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.items.SlotItemHandler;
import org.jetbrains.annotations.NotNull;

public class ExoframeMenu extends AbstractContainerMenu {
    private final ExoframeEntity exoframe;
    private final ExoframeInventory exoframeInventory;

    // Client-side constructor
    public ExoframeMenu(int containerId, Inventory playerInventory, FriendlyByteBuf buf) {
        this(containerId, playerInventory, getEntityFromBuf(playerInventory, buf));
    }

    private static ExoframeEntity getEntityFromBuf(Inventory playerInventory, FriendlyByteBuf buf) {
        int entityId = buf.readInt();
        Entity entity = playerInventory.player.level().getEntity(entityId);
        if (entity instanceof ExoframeEntity exo) {
            return exo;
        }
        throw new IllegalStateException("Entity for ExoframeMenu is not an ExoframeEntity: id=" + entityId);
    }

    // Server-side constructor
    public ExoframeMenu(int containerId, Inventory playerInventory, ExoframeEntity exoframe) {
        super(ModMenuTypes.EXOFRAME_MENU.get(), containerId);
        this.exoframe = exoframe;
        this.exoframeInventory = exoframe.getModularInventory();

        // 7 Specialized Mech Slots:
        // Slot 0: Head
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.HEAD.getIndex(), 80, 18, ExoframeArmorSlot.HEAD));
        // Slot 1: Chest
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.CHEST.getIndex(), 80, 38, ExoframeArmorSlot.CHEST));
        // Slot 2: Arms
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.ARMS.getIndex(), 56, 38, ExoframeArmorSlot.ARMS));
        // Slot 3: Legs
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.LEGS.getIndex(), 80, 60, ExoframeArmorSlot.LEGS));
        // Slot 4: Utility
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.UTILITY.getIndex(), 104, 38, ExoframeArmorSlot.UTILITY));
        // Slot 5: Main Weapon
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.MAIN_WEAPON.getIndex(), 130, 38, ExoframeArmorSlot.MAIN_WEAPON));
        // Slot 6: Back (Flight Booster)
        this.addSlot(new ExoframeCustomSlot(exoframeInventory, ExoframeArmorSlot.BACK.getIndex(), 104, 18, ExoframeArmorSlot.BACK));

        // Player Inventory
        int startX = 8;
        int startY = 88;
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                this.addSlot(new Slot(playerInventory, col + row * 9 + 9, startX + col * 18, startY + row * 18));
            }
        }

        // Player Hotbar
        int hotbarY = 146;
        for (int col = 0; col < 9; ++col) {
            this.addSlot(new Slot(playerInventory, col, startX + col * 18, hotbarY));
        }
    }

    public ExoframeEntity getExoframe() {
        return exoframe;
    }

    @Override
    public boolean stillValid(@NotNull Player player) {
        return exoframe.isAlive() && (player.getVehicle() == exoframe || exoframe.distanceTo(player) < 8.0F);
    }

    @Override
    public @NotNull ItemStack quickMoveStack(@NotNull Player player, int index) {
        ItemStack itemstack = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot != null && slot.hasItem()) {
            ItemStack itemstack1 = slot.getItem();
            itemstack = itemstack1.copy();

            if (index < ExoframeInventory.SLOT_COUNT) {
                // Moving from mech to player inventory
                if (!this.moveItemStackTo(itemstack1, ExoframeInventory.SLOT_COUNT, this.slots.size(), true)) {
                    return ItemStack.EMPTY;
                }
            } else {
                // Moving from player to mech
                boolean moved = false;
                for (int mechSlot = 0; mechSlot < ExoframeInventory.SLOT_COUNT; mechSlot++) {
                    if (exoframeInventory.isItemValid(mechSlot, itemstack1)) {
                        if (this.moveItemStackTo(itemstack1, mechSlot, mechSlot + 1, false)) {
                            moved = true;
                            break;
                        }
                    }
                }
                if (!moved) {
                    if (index < ExoframeInventory.SLOT_COUNT + 27) {
                        if (!this.moveItemStackTo(itemstack1, ExoframeInventory.SLOT_COUNT + 27, this.slots.size(), false)) {
                            return ItemStack.EMPTY;
                        }
                    } else if (!this.moveItemStackTo(itemstack1, ExoframeInventory.SLOT_COUNT, ExoframeInventory.SLOT_COUNT + 27, false)) {
                        return ItemStack.EMPTY;
                    }
                }
            }

            if (itemstack1.isEmpty()) {
                slot.setByPlayer(ItemStack.EMPTY);
            } else {
                slot.setChanged();
            }
        }
        return itemstack;
    }

    public static class ExoframeCustomSlot extends SlotItemHandler {
        private final ExoframeArmorSlot armorSlot;

        public ExoframeCustomSlot(ExoframeInventory itemHandler, int index, int xPosition, int yPosition, ExoframeArmorSlot armorSlot) {
            super(itemHandler, index, xPosition, yPosition);
            this.armorSlot = armorSlot;
        }

        @Override
        public boolean mayPlace(@NotNull ItemStack stack) {
            return getItemHandler().isItemValid(getSlotIndex(), stack);
        }

        public ExoframeArmorSlot getArmorSlot() {
            return armorSlot;
        }
    }
}
