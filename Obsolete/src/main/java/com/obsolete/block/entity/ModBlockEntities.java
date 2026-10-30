package com.obsolete.block.entity;

import com.obsolete.ObsoleteMod;
import com.obsolete.block.ModBlocks;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES, ObsoleteMod.MODID);

    public static final RegistryObject<BlockEntityType<MechAssemblyStationBlockEntity>> MECH_ASSEMBLY_STATION =
            BLOCK_ENTITIES.register("mech_assembly_station", () ->
                    BlockEntityType.Builder.of(MechAssemblyStationBlockEntity::new, ModBlocks.MECH_ASSEMBLY_STATION.get())
                            .build(null));

    public static void register(IEventBus bus) {
        BLOCK_ENTITIES.register(bus);
    }
}
