package com.obsolete.entity.inventory;

import com.obsolete.item.ExoframeFlightBoosterItem;
import com.obsolete.item.ExoframeAmmoItem;
import com.obsolete.item.ExoframeArmorItem;
import com.obsolete.item.ExoframeWeaponItem;
import com.obsolete.item.ExoframeRocketLauncherItem;
import com.obsolete.item.ExoframeRPG7Item;
import com.obsolete.registry.ExoframeVariantRegistry;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.Container;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;

public class ExoframeInventory extends ItemStackHandler implements Container {
    public static final int SLOT_COUNT = 7;
    private final Runnable changeListener;

    public ExoframeInventory(Runnable changeListener) {
        super(SLOT_COUNT);
        this.changeListener = changeListener;
    }

    @Override
    public boolean isItemValid(int slot, @NotNull ItemStack stack) {
        if (stack.isEmpty()) return true;
        ExoframeArmorSlot armorSlot = ExoframeArmorSlot.byIndex(slot);
        switch (armorSlot) {
            case HEAD:
                return stack.getItem() instanceof ExoframeArmorItem armor && armor.getTargetSlot() == ExoframeArmorSlot.HEAD;
            case CHEST:
                return stack.getItem() instanceof ExoframeArmorItem armor && armor.getTargetSlot() == ExoframeArmorSlot.CHEST;
            case ARMS:
                return stack.getItem() instanceof ExoframeArmorItem armor && armor.getTargetSlot() == ExoframeArmorSlot.ARMS;
            case LEGS:
                return stack.getItem() instanceof ExoframeArmorItem armor && armor.getTargetSlot() == ExoframeArmorSlot.LEGS;
            case UTILITY:
                return stack.getItem() instanceof ExoframeAmmoItem
                        || stack.is(com.obsolete.item.ModItems.MODULE_ACTIVE_CLOAK.get())
                        || stack.is(com.obsolete.item.ModItems.MODULE_USMC_COMMS.get())
                        || stack.is(com.obsolete.item.ModItems.MODULE_CERBERUS_PACKS.get())
                        || stack.is(com.obsolete.item.ModItems.MODULE_SHOULDER_MISSILE.get())
                        || stack.getItem() instanceof ExoframeRocketLauncherItem
                        || stack.getItem() instanceof ExoframeRPG7Item
                        || !(stack.getItem() instanceof ExoframeArmorItem) && !(stack.getItem() instanceof ExoframeWeaponItem) && !(stack.getItem() instanceof ExoframeFlightBoosterItem) && !isHandTool(stack);
            case MAIN_WEAPON:
                return stack.getItem() instanceof ExoframeWeaponItem || isHandTool(stack);
            case BACK:
                return stack.getItem() instanceof ExoframeFlightBoosterItem
                        || stack.is(com.obsolete.item.ModItems.MODULE_FLIGHT_BOOSTER.get())
                        || stack.is(com.obsolete.item.ModItems.MODULE_VTOL_WINGS.get())
                        || stack.is(com.obsolete.item.ModItems.MODULE_DRONE_LIFTER.get())
                        || stack.is(com.obsolete.item.ModItems.MODULE_ACTIVE_CLOAK.get())
                        || stack.getItem().getClass().getName().contains("FlightUnitItem")
                        || stack.getItem().getDescriptionId().contains("flight_unit");
            default:
                return false;
        }
    }

    /** Plain items the registry lists as right-hand tools (stun baton, fishing rod); the riot shield stays a utility item. */
    private static boolean isHandTool(ItemStack stack) {
        var data = ExoframeVariantRegistry.getWeaponData(stack.getItem());
        return data != null && !data.isShield();
    }

    @Override
    protected void onContentsChanged(int slot) {
        super.onContentsChanged(slot);
        if (changeListener != null) {
            changeListener.run();
        }
    }

    // Container interface implementation for Menus
    @Override
    public int getContainerSize() {
        return getSlots();
    }

    @Override
    public boolean isEmpty() {
        for (int i = 0; i < getSlots(); i++) {
            if (!getStackInSlot(i).isEmpty()) return false;
        }
        return true;
    }

    @Override
    public @NotNull ItemStack getItem(int slot) {
        return getStackInSlot(slot);
    }

    @Override
    public @NotNull ItemStack removeItem(int slot, int amount) {
        return extractItem(slot, amount, false);
    }

    @Override
    public @NotNull ItemStack removeItemNoUpdate(int slot) {
        ItemStack stack = getStackInSlot(slot);
        if (stack.isEmpty()) return ItemStack.EMPTY;
        setStackInSlot(slot, ItemStack.EMPTY);
        return stack;
    }

    @Override
    public void setItem(int slot, @NotNull ItemStack stack) {
        setStackInSlot(slot, stack);
    }

    @Override
    public void setChanged() {
        if (changeListener != null) changeListener.run();
    }

    @Override
    public boolean stillValid(@NotNull Player player) {
        return true;
    }

    @Override
    public void clearContent() {
        for (int i = 0; i < getSlots(); i++) {
            setStackInSlot(i, ItemStack.EMPTY);
        }
    }

    public void saveToNbt(CompoundTag tag) {
        tag.put("ModularInventory", serializeNBT());
    }

    public void loadFromNbt(CompoundTag tag) {
        if (tag.contains("ModularInventory")) {
            deserializeNBT(tag.getCompound("ModularInventory"));
            if (this.stacks.size() < SLOT_COUNT) {
                setSize(SLOT_COUNT);
            }
        }
    }
}
