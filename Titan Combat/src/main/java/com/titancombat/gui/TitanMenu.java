package com.titancombat.gui;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.item.TitanAmmoItem;
import com.titancombat.item.TitanBatteryItem;
import com.titancombat.item.TitanMagazineItem;
import com.titancombat.item.TitanWeaponItem;
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
    public static final int CONTAINER_SIZE = 18;
    public static final int BATTERY_SLOT = 0;
    public static final int AMMO_SLOT_1 = 1;
    public static final int AMMO_SLOT_2 = 2;
    public static final int CARGO_START = 3;
    public static final int CARGO_END = 11;
    /** Weapon module slot: any titan weapon item; empty = the chassis' factory weapon. */
    public static final int WEAPON_SLOT = 12;
    /** Flight equipment / jetpack module slot. */
    public static final int FLIGHT_SLOT = 13;
    /** Modular Frame Armor Slots */
    public static final int ARMOR_HEAD_SLOT = 14;
    public static final int ARMOR_CHEST_SLOT = 15;
    public static final int ARMOR_ARMS_SLOT = 16;
    public static final int ARMOR_LEGS_SLOT = 17;

    // Slot layout (GUI-local pixels, item area top-left) - must match TitanScreen's 300x222 panel
    public static final int BATTERY_X = 140;
    public static final int BATTERY_Y = 59;
    public static final int FLIGHT_X = 138;
    public static final int FLIGHT_Y = 100;
    public static final int AMMO_X = 88;
    public static final int AMMO_Y = 100;
    public static final int CARGO_X = 168;
    public static final int CARGO_Y = 68;
    public static final int INV_X = 69;
    public static final int INV_Y = 141;
    public static final int HOTBAR_Y = 199;
    public static final int WEAPON_X = 232;
    public static final int WEAPON_Y = 68;
    public static final int ARMOR_HEAD_X = 22;
    public static final int ARMOR_HEAD_Y = 137;
    public static final int ARMOR_CHEST_X = 22;
    public static final int ARMOR_CHEST_Y = 157;
    public static final int ARMOR_ARMS_X = 22;
    public static final int ARMOR_ARMS_Y = 177;
    public static final int ARMOR_LEGS_X = 22;
    public static final int ARMOR_LEGS_Y = 197;

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
        this.addSlot(new Slot(this.container, BATTERY_SLOT, BATTERY_X, BATTERY_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof TitanBatteryItem;
            }
        });

        // Slot 1 & 2: Munitions Bay Slots
        this.addSlot(new Slot(this.container, AMMO_SLOT_1, AMMO_X, AMMO_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return isMunition(stack);
            }
        });
        this.addSlot(new Slot(this.container, AMMO_SLOT_2, AMMO_X + 18, AMMO_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return isMunition(stack);
            }
        });

        // Slots 3..11: General Cargo Bay (9 slots: 3x3 grid)
        for (int i = 0; i < 9; i++) {
            this.addSlot(new Slot(this.container, CARGO_START + i, CARGO_X + (i % 3) * 18, CARGO_Y + (i / 3) * 18));
        }

        // Slot 12: Weapon module
        this.addSlot(new Slot(this.container, WEAPON_SLOT, WEAPON_X, WEAPON_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof TitanWeaponItem;
            }

            @Override
            public int getMaxStackSize() {
                return 1;
            }
        });

        // Slot 13: Flight equipment / jetpack module slot
        this.addSlot(new Slot(this.container, FLIGHT_SLOT, FLIGHT_X, FLIGHT_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return isBackModule(stack);
            }

            @Override
            public int getMaxStackSize() {
                return 1;
            }
        });

        // Slot 14: Head Armor Slot
        this.addSlot(new Slot(this.container, ARMOR_HEAD_SLOT, ARMOR_HEAD_X, ARMOR_HEAD_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof com.titancombat.item.TitanArmorItem tai && tai.getArmorSlot() == com.titancombat.item.TitanArmorItem.ArmorSlot.HEAD;
            }

            @Override
            public int getMaxStackSize() {
                return 1;
            }

            @Override
            public void setChanged() {
                super.setChanged();
                if (titan instanceof com.titancombat.entity.TitanFrameEntity frame) {
                    frame.syncArmorFromInventory();
                }
            }
        });

        // Slot 15: Chest Armor Slot
        this.addSlot(new Slot(this.container, ARMOR_CHEST_SLOT, ARMOR_CHEST_X, ARMOR_CHEST_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof com.titancombat.item.TitanArmorItem tai && tai.getArmorSlot() == com.titancombat.item.TitanArmorItem.ArmorSlot.CHEST;
            }

            @Override
            public int getMaxStackSize() {
                return 1;
            }

            @Override
            public void setChanged() {
                super.setChanged();
                if (titan instanceof com.titancombat.entity.TitanFrameEntity frame) {
                    frame.syncArmorFromInventory();
                }
            }
        });

        // Slot 16: Arms Armor Slot
        this.addSlot(new Slot(this.container, ARMOR_ARMS_SLOT, ARMOR_ARMS_X, ARMOR_ARMS_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof com.titancombat.item.TitanArmorItem tai && tai.getArmorSlot() == com.titancombat.item.TitanArmorItem.ArmorSlot.ARMS;
            }

            @Override
            public int getMaxStackSize() {
                return 1;
            }

            @Override
            public void setChanged() {
                super.setChanged();
                if (titan instanceof com.titancombat.entity.TitanFrameEntity frame) {
                    frame.syncArmorFromInventory();
                }
            }
        });

        // Slot 17: Legs Armor Slot
        this.addSlot(new Slot(this.container, ARMOR_LEGS_SLOT, ARMOR_LEGS_X, ARMOR_LEGS_Y) {
            @Override
            public boolean mayPlace(ItemStack stack) {
                return stack.getItem() instanceof com.titancombat.item.TitanArmorItem tai && tai.getArmorSlot() == com.titancombat.item.TitanArmorItem.ArmorSlot.LEGS;
            }

            @Override
            public int getMaxStackSize() {
                return 1;
            }

            @Override
            public void setChanged() {
                super.setChanged();
                if (titan instanceof com.titancombat.entity.TitanFrameEntity frame) {
                    frame.syncArmorFromInventory();
                }
            }
        });

        // Player Main Inventory (3 rows of 9)
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                this.addSlot(new Slot(playerInventory, col + row * 9 + 9, INV_X + col * 18, INV_Y + row * 18));
            }
        }

        // Player Hotbar (9 slots)
        for (int col = 0; col < 9; ++col) {
            this.addSlot(new Slot(playerInventory, col, INV_X + col * 18, HOTBAR_Y));
        }
    }

    public static boolean isMunition(ItemStack stack) {
        return stack.getItem() instanceof TitanAmmoItem || stack.getItem() instanceof TitanMagazineItem
                || stack.is(com.titancombat.item.ModItems.HOWITZER_SHELLS.get())
                || stack.is(com.titancombat.item.ModItems.HOWITZER_SMOKE_SHELLS.get())
                || stack.is(com.titancombat.item.ModItems.AMMO_ROCKET_SALVO.get());
    }

    /** Back equipment slot: flight module, howitzer, rocket launcher pod, or core modules. */
    public static boolean isBackModule(ItemStack stack) {
        return stack.getItem() instanceof com.titancombat.item.TitanFlightModuleItem
                || stack.getItem() instanceof com.titancombat.item.HowitzerModuleItem
                || stack.getItem() instanceof com.titancombat.item.RocketLauncherModuleItem
                || stack.getItem() instanceof com.titancombat.item.TitanCoreModuleItem;
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
                } else if (slotStack.getItem() instanceof TitanWeaponItem) {
                    if (!this.moveItemStackTo(slotStack, WEAPON_SLOT, WEAPON_SLOT + 1, false)) {
                        if (!this.moveItemStackTo(slotStack, CARGO_START, CARGO_END + 1, false)) {
                            return ItemStack.EMPTY;
                        }
                    }
                } else if (isBackModule(slotStack)) {
                    if (!this.moveItemStackTo(slotStack, FLIGHT_SLOT, FLIGHT_SLOT + 1, false)) {
                        if (!this.moveItemStackTo(slotStack, CARGO_START, CARGO_END + 1, false)) {
                            return ItemStack.EMPTY;
                        }
                    }
                } else if (slotStack.getItem() instanceof com.titancombat.item.TitanArmorItem tai) {
                    int targetSlot = switch (tai.getArmorSlot()) {
                        case HEAD -> ARMOR_HEAD_SLOT;
                        case CHEST -> ARMOR_CHEST_SLOT;
                        case ARMS -> ARMOR_ARMS_SLOT;
                        case LEGS -> ARMOR_LEGS_SLOT;
                    };
                    if (!this.moveItemStackTo(slotStack, targetSlot, targetSlot + 1, false)) {
                        if (!this.moveItemStackTo(slotStack, CARGO_START, CARGO_END + 1, false)) {
                            return ItemStack.EMPTY;
                        }
                    }
                } else if (isMunition(slotStack)) {
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
