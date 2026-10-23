package com.titancombat.gui;

import com.titancombat.TitanCombatMod;
import net.minecraft.world.inventory.MenuType;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModMenuTypes {
    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(ForgeRegistries.MENU_TYPES, TitanCombatMod.MODID);

    public static final RegistryObject<MenuType<TitanMenu>> TITAN_MENU =
            MENUS.register("titan_menu", () -> IForgeMenuType.create(TitanMenu::new));

    public static void register(IEventBus eventBus) {
        MENUS.register(eventBus);
    }
}
