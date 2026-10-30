package com.obsolete.gui;

import com.obsolete.ObsoleteMod;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.MenuType;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.network.IContainerFactory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModMenuTypes {
    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(ForgeRegistries.MENU_TYPES, ObsoleteMod.MODID);

    public static final RegistryObject<MenuType<ExoframeMenu>> EXOFRAME_MENU =
            registerMenuType("exoframe_menu", ExoframeMenu::new);

    public static final RegistryObject<MenuType<MechAssemblyMenu>> MECH_ASSEMBLY_MENU =
            registerMenuType("mech_assembly_menu", MechAssemblyMenu::new);

    private static <T extends AbstractContainerMenu> RegistryObject<MenuType<T>> registerMenuType(String name, IContainerFactory<T> factory) {
        return MENUS.register(name, () -> IForgeMenuType.create(factory));
    }

    public static void register(IEventBus bus) {
        MENUS.register(bus);
    }
}
