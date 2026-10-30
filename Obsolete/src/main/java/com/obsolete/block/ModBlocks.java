package com.obsolete.block;

import com.obsolete.ObsoleteMod;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModBlocks {
    public static final DeferredRegister<Block> BLOCKS =
            DeferredRegister.create(ForgeRegistries.BLOCKS, ObsoleteMod.MODID);

    public static final RegistryObject<Block> MECH_ASSEMBLY_STATION =
            BLOCKS.register("mech_assembly_station", () ->
                    new MechAssemblyStationBlock(BlockBehaviour.Properties.of()
                            .strength(3.5F, 8.0F)
                            .requiresCorrectToolForDrops()
                            .sound(SoundType.NETHERITE_BLOCK)
                            .noOcclusion()));

    public static void register(IEventBus bus) {
        BLOCKS.register(bus);
    }
}
