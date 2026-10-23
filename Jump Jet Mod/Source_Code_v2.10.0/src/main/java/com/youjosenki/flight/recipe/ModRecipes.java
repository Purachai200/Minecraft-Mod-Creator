package com.youjosenki.flight.recipe;

import com.youjosenki.flight.YoujoSenkiMod;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.SimpleCraftingRecipeSerializer;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModRecipes {
    public static final DeferredRegister<RecipeSerializer<?>> RECIPE_SERIALIZERS =
            DeferredRegister.create(ForgeRegistries.RECIPE_SERIALIZERS, YoujoSenkiMod.MODID);

    public static final RegistryObject<RecipeSerializer<FlightUnitBannerRecipe>> FLIGHT_UNIT_BANNER_SERIALIZER =
            RECIPE_SERIALIZERS.register("flight_unit_banner", () -> new SimpleCraftingRecipeSerializer<>(FlightUnitBannerRecipe::new));
}
