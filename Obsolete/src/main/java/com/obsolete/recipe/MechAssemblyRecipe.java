package com.obsolete.recipe;

import net.minecraft.core.NonNullList;
import net.minecraft.core.RegistryAccess;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Container;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

public class MechAssemblyRecipe implements Recipe<Container> {
    private final ResourceLocation id;
    private final NonNullList<Ingredient> ingredients;
    private final ItemStack output;
    private final int assembleTime;

    public MechAssemblyRecipe(ResourceLocation id, NonNullList<Ingredient> ingredients, ItemStack output, int assembleTime) {
        this.id = id;
        this.ingredients = ingredients;
        this.output = output;
        this.assembleTime = assembleTime;
    }

    @Override
    public boolean matches(@NotNull Container container, @NotNull Level level) {
        // Container has 4 input slots (0, 1, 2, 3)
        List<ItemStack> inputs = new ArrayList<>();
        for (int i = 0; i < 4; i++) {
            ItemStack stack = container.getItem(i);
            if (!stack.isEmpty()) {
                inputs.add(stack);
            }
        }

        if (inputs.size() != ingredients.size()) {
            return false;
        }

        boolean[] matched = new boolean[inputs.size()];
        for (Ingredient ingredient : ingredients) {
            boolean found = false;
            for (int i = 0; i < inputs.size(); i++) {
                if (!matched[i] && ingredient.test(inputs.get(i))) {
                    matched[i] = true;
                    found = true;
                    break;
                }
            }
            if (!found) {
                return false;
            }
        }
        return true;
    }

    @Override
    public @NotNull ItemStack assemble(@NotNull Container container, @NotNull RegistryAccess registryAccess) {
        return output.copy();
    }

    @Override
    public boolean canCraftInDimensions(int width, int height) {
        return true;
    }

    @Override
    public @NotNull ItemStack getResultItem(@NotNull RegistryAccess registryAccess) {
        return output;
    }

    @Override
    public @NotNull ResourceLocation getId() {
        return id;
    }

    @Override
    public @NotNull RecipeSerializer<?> getSerializer() {
        return ModRecipeTypes.MECH_ASSEMBLY_SERIALIZER.get();
    }

    @Override
    public @NotNull RecipeType<?> getType() {
        return ModRecipeTypes.MECH_ASSEMBLY.get();
    }

    @Override
    public @NotNull NonNullList<Ingredient> getIngredients() {
        return ingredients;
    }

    public int getAssembleTime() {
        return assembleTime;
    }
}
