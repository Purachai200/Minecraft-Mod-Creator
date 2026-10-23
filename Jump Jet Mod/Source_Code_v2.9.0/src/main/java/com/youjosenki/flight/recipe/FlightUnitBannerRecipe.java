package com.youjosenki.flight.recipe;

import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.core.RegistryAccess;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.inventory.CraftingContainer;
import net.minecraft.world.item.BannerItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.CraftingBookCategory;
import net.minecraft.world.item.crafting.CustomRecipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.NotNull;

public class FlightUnitBannerRecipe extends CustomRecipe {
    public FlightUnitBannerRecipe(ResourceLocation id, CraftingBookCategory category) {
        super(id, category);
    }

    @Override
    public boolean matches(@NotNull CraftingContainer container, @NotNull Level level) {
        ItemStack flightUnit = ItemStack.EMPTY;
        ItemStack banner = ItemStack.EMPTY;

        for (int i = 0; i < container.getContainerSize(); i++) {
            ItemStack stack = container.getItem(i);
            if (!stack.isEmpty()) {
                if (stack.getItem() instanceof BannerItem) {
                    if (!banner.isEmpty()) return false;
                    banner = stack;
                } else if (stack.getItem() instanceof EleniumFlightUnitItem) {
                    if (!flightUnit.isEmpty()) return false;
                    flightUnit = stack;
                } else {
                    return false;
                }
            }
        }

        return !flightUnit.isEmpty() && !banner.isEmpty();
    }

    @Override
    public @NotNull ItemStack assemble(@NotNull CraftingContainer container, @NotNull RegistryAccess registryAccess) {
        ItemStack flightUnit = ItemStack.EMPTY;
        ItemStack banner = ItemStack.EMPTY;

        for (int i = 0; i < container.getContainerSize(); i++) {
            ItemStack stack = container.getItem(i);
            if (!stack.isEmpty()) {
                if (stack.getItem() instanceof BannerItem) {
                    banner = stack;
                } else if (stack.getItem() instanceof EleniumFlightUnitItem) {
                    flightUnit = stack;
                }
            }
        }

        if (flightUnit.isEmpty() || banner.isEmpty()) {
            return ItemStack.EMPTY;
        }

        // Clone flight unit with 1 count, preserving all capabilities, NBT, energy, dye color
        ItemStack result = flightUnit.copyWithCount(1);

        // Copy banner data exactly like vanilla ShieldDecorationRecipe
        CompoundTag bannerTag = banner.getTagElement("BlockEntityTag");
        CompoundTag newBlockEntityTag = bannerTag != null ? bannerTag.copy() : new CompoundTag();
        newBlockEntityTag.putInt("Base", ((BannerItem) banner.getItem()).getColor().getId());
        result.addTagElement("BlockEntityTag", newBlockEntityTag);

        return result;
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return width * height >= 2;
    }

    @Override
    public @NotNull RecipeSerializer<?> getSerializer() {
        return ModRecipes.FLIGHT_UNIT_BANNER_SERIALIZER.get();
    }
}
