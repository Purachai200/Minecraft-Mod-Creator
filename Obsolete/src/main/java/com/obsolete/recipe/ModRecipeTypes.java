package com.obsolete.recipe;

import com.obsolete.ObsoleteMod;
import net.minecraft.world.item.crafting.RecipeSerializer;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModRecipeTypes {
    public static final DeferredRegister<RecipeType<?>> RECIPE_TYPES =
            DeferredRegister.create(ForgeRegistries.RECIPE_TYPES, ObsoleteMod.MODID);

    public static final DeferredRegister<RecipeSerializer<?>> RECIPE_SERIALIZERS =
            DeferredRegister.create(ForgeRegistries.RECIPE_SERIALIZERS, ObsoleteMod.MODID);

    public static final RegistryObject<RecipeType<MechAssemblyRecipe>> MECH_ASSEMBLY =
            RECIPE_TYPES.register("mech_assembly", () -> RecipeType.simple(new net.minecraft.resources.ResourceLocation(ObsoleteMod.MODID, "mech_assembly")));

    public static final RegistryObject<RecipeSerializer<MechAssemblyRecipe>> MECH_ASSEMBLY_SERIALIZER =
            RECIPE_SERIALIZERS.register("mech_assembly", MechAssemblyRecipeSerializer::new);

    public static void register(IEventBus bus) {
        RECIPE_TYPES.register(bus);
        RECIPE_SERIALIZERS.register(bus);
    }
}
