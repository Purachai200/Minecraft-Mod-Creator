package com.obsolete.recipe;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import net.minecraft.core.NonNullList;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.GsonHelper;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.ShapedRecipe;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class MechAssemblyRecipeSerializer implements RecipeSerializer<MechAssemblyRecipe> {

    @Override
    public @NotNull MechAssemblyRecipe fromJson(@NotNull ResourceLocation recipeId, @NotNull JsonObject json) {
        JsonArray ingredientsJson = GsonHelper.getAsJsonArray(json, "ingredients");
        NonNullList<Ingredient> ingredients = NonNullList.create();
        for (int i = 0; i < ingredientsJson.size(); i++) {
            ingredients.add(Ingredient.fromJson(ingredientsJson.get(i)));
        }

        ItemStack output = ShapedRecipe.itemStackFromJson(GsonHelper.getAsJsonObject(json, "result"));
        int assembleTime = GsonHelper.getAsInt(json, "assemble_time", 100);

        return new MechAssemblyRecipe(recipeId, ingredients, output, assembleTime);
    }

    @Override
    public @Nullable MechAssemblyRecipe fromNetwork(@NotNull ResourceLocation recipeId, @NotNull FriendlyByteBuf buf) {
        int count = buf.readVarInt();
        NonNullList<Ingredient> ingredients = NonNullList.withSize(count, Ingredient.EMPTY);
        for (int i = 0; i < count; i++) {
            ingredients.set(i, Ingredient.fromNetwork(buf));
        }
        ItemStack output = buf.readItem();
        int assembleTime = buf.readVarInt();
        return new MechAssemblyRecipe(recipeId, ingredients, output, assembleTime);
    }

    @Override
    public void toNetwork(@NotNull FriendlyByteBuf buf, @NotNull MechAssemblyRecipe recipe) {
        buf.writeVarInt(recipe.getIngredients().size());
        for (Ingredient ingredient : recipe.getIngredients()) {
            ingredient.toNetwork(buf);
        }
        buf.writeItem(recipe.getResultItem(null));
        buf.writeVarInt(recipe.getAssembleTime());
    }
}
