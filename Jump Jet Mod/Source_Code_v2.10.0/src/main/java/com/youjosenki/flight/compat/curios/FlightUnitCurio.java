package com.youjosenki.flight.compat.curios;

import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurio;

public class FlightUnitCurio implements ICurio {
    private final ItemStack stack;
    private final EleniumFlightUnitItem item;

    public FlightUnitCurio(ItemStack stack, EleniumFlightUnitItem item) {
        this.stack = stack;
        this.item = item;
    }

    @Override
    public ItemStack getStack() {
        return stack;
    }

    @Override
    public boolean canEquipFromUse(SlotContext slotContext) {
        return true;
    }

    @Override
    public void curioTick(SlotContext slotContext) {
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            item.handleFlight(player, stack);
        }
    }

    @Override
    public void onEquip(SlotContext slotContext, ItemStack prevStack) {
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            item.onEquipUnit(player, stack);
        }
    }

    @Override
    public void onUnequip(SlotContext slotContext, ItemStack newStack) {
        if (newStack.getItem() instanceof EleniumFlightUnitItem) {
            return;
        }
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            item.onUnequipUnit(player);
        }
    }
}
