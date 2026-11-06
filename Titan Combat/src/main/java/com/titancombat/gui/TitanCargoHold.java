package com.titancombat.gui;

import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.world.Container;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/** The titan's cargo hold (inventory slots HOLD_START..TOTAL_SIZE-1) as a 27-slot container for a vanilla chest screen. */
public class TitanCargoHold implements Container {
    private final BaseTitanEntity titan;

    public TitanCargoHold(BaseTitanEntity titan) {
        this.titan = titan;
    }

    private Container inv() {
        return this.titan.getTitanInventory();
    }

    @Override
    public int getContainerSize() {
        return TitanMenu.HOLD_SIZE;
    }

    @Override
    public boolean isEmpty() {
        for (int i = 0; i < TitanMenu.HOLD_SIZE; i++) {
            if (!getItem(i).isEmpty()) return false;
        }
        return true;
    }

    @Override
    public ItemStack getItem(int slot) {
        return inv().getItem(TitanMenu.HOLD_START + slot);
    }

    @Override
    public ItemStack removeItem(int slot, int amount) {
        return inv().removeItem(TitanMenu.HOLD_START + slot, amount);
    }

    @Override
    public ItemStack removeItemNoUpdate(int slot) {
        return inv().removeItemNoUpdate(TitanMenu.HOLD_START + slot);
    }

    @Override
    public void setItem(int slot, ItemStack stack) {
        inv().setItem(TitanMenu.HOLD_START + slot, stack);
    }

    @Override
    public void setChanged() {
        inv().setChanged();
    }

    @Override
    public boolean stillValid(Player player) {
        return this.titan.isAlive() && player.distanceToSqr(this.titan) <= 64.0D;
    }

    @Override
    public void clearContent() {
        for (int i = 0; i < TitanMenu.HOLD_SIZE; i++) setItem(i, ItemStack.EMPTY);
    }
}
