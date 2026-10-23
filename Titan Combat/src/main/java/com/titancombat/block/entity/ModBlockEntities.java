package com.titancombat.block.entity;

import com.titancombat.TitanCombatMod;
import com.titancombat.block.ModBlocks;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, TitanCombatMod.MODID);

    public static final RegistryObject<BlockEntityType<BatteryChargerBlockEntity>> BATTERY_CHARGER =
            BLOCK_ENTITIES.register("battery_charger", () ->
                    BlockEntityType.Builder.of(BatteryChargerBlockEntity::new, ModBlocks.BATTERY_CHARGER.get()).build(null));

    public static void register(IEventBus eventBus) {
        BLOCK_ENTITIES.register(eventBus);
    }
}
