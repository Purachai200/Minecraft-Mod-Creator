package com.titancombat.gui;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.item.TitanAmmoItem;
import com.titancombat.item.TitanBatteryItem;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

public class TitanMenu extends AbstractContainerMenu {
    public static final int CONTAINER_SIZE = 12;
    public static final int BATTERY_SLOT = 0;
    public static final int AMMO_SLOT_1 = 1;
    public static final int AMMO_SLOT_2 = 2;
    public static final int CARGO_START = 3;
    public static final int CARGO_END = 11;

    private final BaseTitanEntity titan;
    private final Container container;

    public TitanMenu(int containerId, Inventory playerInventory, FriendlyByteBuf extraData) {
        this(containerId, playerInventory, getTitanFromBuf(playerInventory, extraData));
    }

    private static BaseTitanEntity getTitanFromBuf(Inventory playerInventory, FriendlyByteBuf extraData) {
        if (extraData != null) {
            int entityId = extraData.readInt();
            Entity entity = playerInventory.player.level().getEntity(entityId);
            if (entity instanceof BaseTitanEntity bte) {
                return bte;
            }
        }
        return null;
    }

    public TitanMenu(int containerId, Inventory playerInventory, BaseTitanEntity titan) {
        super(ModMenuTypes.TITAN_MENU.get(), containerId);
        this.titan = titan;
        this.container = titan != null ? titan.getTitanInventory() : new SimpleContainer(CONTAINER_SIZE);

        checkContainerSize(this.container, CONTAINER_SIZE);
        this.container.startOpen(playerInventory.player);

        // Slot 0: Battery Bay Slot
        this.addSlot(new Slot(this.container, BATTERY_SLOT, 18, 20) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof TitanBatteryItem;
            }
        });

        // Slot 1 & 2: Munitions Bay Slots
        this.addSlot(new Slot(this.container, AMMO_SLOT_1, 54, 20) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof TitanAmmoItem;
            }
        });
        this.addSlot(new Slot(this.container, AMMO_SLOT_2, 72, 20) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof TitanAmmoItem;
            }
        });

        // Slots 3..11: General Cargo Bay (9 slots: 1 row of 9)
        for (int i = 0; i < 9; i++) {
            this.addSlot(new Slot(this.container, CARGO_START + i, 8 + i * 18, 52));
        }

        // Player Main Inventory (3 rows of 9)
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                this.addSlot(new Slot(playerInventory, col + row * 9 + 9, 8 + col * 18, 84 + row * 18));
            }
        }

        // Player Hotbar (9 slots)
        for (int col = 0; col < 9; ++col) {
            this.addSlot(new Slot(playerInventory, col, 8 + col * 18, 142));
        }
    }

    public BaseTitanEntity getTitan() {
        return this.titan;
    }

    @Override
    public boolean stillValid(Player player) {
        if (this.titan != null && !this.titan.isAlive()) return false;
        return this.container.stillValid(player);
    }

    @Override
    public void removed(Player player) {
        super.removed(player);
        this.container.stopOpen(player);
    }

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        ItemStack itemstack = ItemStack.EMPTY;
        Slot slot = this.slots.get(index);
        if (slot != null && slot.hasItem()) {
            ItemStack slotStack = slot.getItem();
            itemstack = slotStack.copy();

            if (index < CONTAINER_SIZE) {
                // Moving from Titan container into player inventory
                if (!this.moveItemStackTo(slotStack, CONTAINER_SIZE, this.slots.size(), true)) {
                    return ItemStack.EMPTY;
                }
            } else {
                // Moving from player inventory into Titan container
                if (slotStack.getItem() instanceof TitanBatteryItem) {
                    if (!this.moveItemStackTo(slotStack, BATTERY_SLOT, BATTERY_SLOT + 1, false)) {
                        if (!this.moveItemStackTo(slotStack, CARGO_START, CARGO_END + 1, false)) {
                            return ItemStack.EMPTY;
                        }
                    }
                } else if (slotStack.getItem() instanceof TitanAmmoItem) {
                    if (!this.moveItemStackTo(slotStack, AMMO_SLOT_1, AMMO_SLOT_2 + 1, false)) {
                        if (!this.moveItemStackTo(slotStack, CARGO_START, CARGO_END + 1, false)) {
                            return ItemStack.EMPTY;
                        }
                    }
                } else {
                    if (!this.moveItemStackTo(slotStack, CARGO_START, CARGO_END + 1, false)) {
                        return ItemStack.EMPTY;
                    }
                }
            }

            if (slotStack.isEmpty()) {
                slot.setByPlayer(ItemStack.EMPTY);
            } else {
                slot.setChanged();
            }
        }
        return itemstack;
    }
}
