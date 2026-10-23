package com.titancombat;

import com.titancombat.block.ModBlocks;
import com.titancombat.block.entity.ModBlockEntities;
import com.titancombat.entity.*;
import com.titancombat.item.ModCreativeTabs;
import com.titancombat.item.ModItems;
import com.titancombat.network.ModNetworking;
import com.titancombat.sound.ModSounds;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import software.bernie.geckolib.GeckoLib;

@Mod(TitanCombatMod.MODID)
public class TitanCombatMod {
    public static final String MODID = "titancombat";
    public static final Logger LOGGER = LogManager.getLogger();

    public TitanCombatMod() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        GeckoLib.initialize();

        ModBlocks.register(modEventBus);
        ModBlockEntities.register(modEventBus);
        ModEntities.register(modEventBus);
        ModItems.register(modEventBus);
        ModSounds.register(modEventBus);
        ModCreativeTabs.register(modEventBus);
        com.titancombat.gui.ModMenuTypes.register(modEventBus);

        modEventBus.addListener(this::commonSetup);
        modEventBus.addListener(this::entityAttributes);

        MinecraftForge.EVENT_BUS.register(this);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        event.enqueueWork(ModNetworking::register);
        LOGGER.info("Titan Combat: Systems, Blocks, Sounds & Networking initialized successfully.");
    }

    private void entityAttributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.AEGIS_STRIKER.get(), BaseMechEntity.createAttributes().build());
        event.put(ModEntities.ION_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.ION).build());
        event.put(ModEntities.SCORCH_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.SCORCH).build());
        event.put(ModEntities.RONIN_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.RONIN).build());
        event.put(ModEntities.TONE_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.TONE).build());
        event.put(ModEntities.LEGION_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.LEGION).build());
        event.put(ModEntities.MONARCH_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.MONARCH).build());
        event.put(ModEntities.NORTHSTAR_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.NORTHSTAR).build());
    }

    @SubscribeEvent
    public void onEntityDismount(net.minecraftforge.event.entity.EntityMountEvent event) {
        if (event.isDismounting() && event.getEntityBeingMounted() instanceof BaseTitanEntity titan) {
            if (titan.isAlive() && !titan.isSitting() && !titan.isEmergencyEjecting()) {
                event.setCanceled(true);
                if (event.getEntityMounting() instanceof net.minecraft.world.entity.player.Player player) {
                    player.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.titancombat.must_kneel_first"), true);
                }
            }
        }
    }
}
