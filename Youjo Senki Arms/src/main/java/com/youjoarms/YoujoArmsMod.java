package com.youjoarms;

import com.tacz.guns.api.resource.ResourceManager;
import com.youjoarms.capability.PlayerMageData;
import com.youjoarms.config.YoujoArmsConfig;
import com.youjoarms.entity.ModEntities;
import com.youjoarms.network.YoujoArmsNetwork;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.capabilities.RegisterCapabilitiesEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

@Mod(YoujoArmsMod.MOD_ID)
public class YoujoArmsMod {
    public static final String MOD_ID = "youjoarms";
    public static final Logger LOGGER = LogManager.getLogger();

    public YoujoArmsMod() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        // Register Config
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, YoujoArmsConfig.COMMON_SPEC);

        // Register Entities
        ModEntities.ENTITIES.register(modEventBus);

        // Mod bus listeners
        modEventBus.addListener(this::setup);
        modEventBus.addListener(this::registerCapabilities);

        // Register TACZ Gun Pack inside jar to TACZ Resource Manager
        try {
            ResourceManager.registerExportResource(YoujoArmsMod.class, "/tacz_youjoarms");  // leading slash: absolute classpath path
            LOGGER.info("[YoujoArms] Registered tacz_youjoarms gun pack to TACZ ResourceManager");
        } catch (Throwable t) {
            LOGGER.error("[YoujoArms] Failed to register gun pack to TACZ: ", t);
        }

        MinecraftForge.EVENT_BUS.register(this);
    }

    private void setup(final FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            YoujoArmsNetwork.register();
            LOGGER.info("[YoujoArms] Common setup initialized.");
        });
    }

    private void registerCapabilities(RegisterCapabilitiesEvent event) {
        event.register(PlayerMageData.class);
    }
}
