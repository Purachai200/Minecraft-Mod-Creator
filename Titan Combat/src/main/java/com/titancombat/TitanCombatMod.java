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
        net.minecraftforge.fml.ModLoadingContext.get().registerConfig(net.minecraftforge.fml.config.ModConfig.Type.SERVER, TitanConfig.SPEC);

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
        event.put(ModEntities.TROOPER_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.TROOPER).build());
        event.put(ModEntities.SCOUT_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.SCOUT).build());
        event.put(ModEntities.SHADE_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.SHADE).build());
        event.put(ModEntities.BULWARK_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.BULWARK).build());
        event.put(ModEntities.EXO_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.EXO_FRAME).build());
        event.put(ModEntities.TITAN_EXO_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.TITAN_EXO).build());
        event.put(ModEntities.STRIKER_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.STRIKER_FRAME).build());
        event.put(ModEntities.VANGUARD_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.VANGUARD_FRAME).build());
        event.put(ModEntities.COLOSSUS_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.COLOSSUS_FRAME).build());
        event.put(ModEntities.TERRAIN_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.TERRAIN_FRAME).build());
        event.put(ModEntities.CYCLOPS_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.CYCLOPS_FRAME).build());
        event.put(ModEntities.SPIDER_FRAME_TITAN.get(), BaseTitanEntity.createTitanAttributes(TitanClass.SPIDER_FRAME).build());
        event.put(ModEntities.HAULER_TRUCK.get(), com.titancombat.entity.transport.TitanHaulerTruckEntity.createHaulerAttributes().build());
        event.put(ModEntities.CARGO_BARGE.get(), com.titancombat.entity.transport.TitanCargoBargeEntity.createBargeAttributes().build());
        event.put(ModEntities.SKYCRANE_DRONE.get(), com.titancombat.entity.transport.TitanSkyCraneDroneEntity.createDroneAttributes().build());
        event.put(ModEntities.OCEAN_CARRIER.get(), com.titancombat.entity.transport.TitanOceanCarrierEntity.createOceanCarrierAttributes().build());
        event.put(ModEntities.TACTICAL_TRUCK.get(), com.titancombat.entity.transport.TitanTacticalTruckEntity.createTacticalTruckAttributes().build());
        event.put(ModEntities.CHINOOK_TRANSPORTER.get(), com.titancombat.entity.transport.TitanChinookTransporterEntity.createChinookAttributes().build());
        event.put(ModEntities.V22_OSPREY.get(), com.titancombat.entity.transport.TitanV22OspreyEntity.createV22OspreyAttributes().build());
        event.put(ModEntities.ARMORED_APC.get(), com.titancombat.entity.transport.TitanArmoredApcEntity.createArmoredApcAttributes().build());
        event.put(ModEntities.LCAC_HOVERCRAFT.get(), com.titancombat.entity.transport.TitanLcacHovercraftEntity.createLcacAttributes().build());
        event.put(ModEntities.PATROL_BOAT.get(), com.titancombat.entity.transport.TitanPatrolBoatEntity.createAttributes().build());
        event.put(ModEntities.PATROL_FRIGATE.get(), com.titancombat.entity.transport.TitanPatrolFrigateEntity.createAttributes().build());
        event.put(ModEntities.SKY_CARRIER.get(), com.titancombat.entity.transport.TitanSkyCarrierEntity.createAttributes().build());
        event.put(ModEntities.C130_HERCULES.get(), com.titancombat.entity.transport.TitanC130HerculesEntity.createC130Attributes().build());
        event.put(ModEntities.REPAIR_TRUCK.get(), com.titancombat.entity.transport.TitanRepairTruckEntity.createRepairTruckAttributes().build());
        event.put(ModEntities.MOBILE_SUIT_TRAILER.get(), com.titancombat.entity.transport.TitanMobileSuitTrailerEntity.createMobileSuitTrailerAttributes().build());
    }

    @SubscribeEvent
    public void onEntityDismount(net.minecraftforge.event.entity.EntityMountEvent event) {
        // Server decides; the client must follow its passenger updates or the two desync (e.g. on eject).
        if (event.getLevel().isClientSide()) return;
        if (event.isDismounting() && event.getEntityBeingMounted() instanceof BaseTitanEntity titan) {
            if (titan.isAlive() && !titan.isSitting() && !titan.isEmergencyEjecting()) {
                event.setCanceled(true);
                if (event.getEntityMounting() instanceof net.minecraft.world.entity.player.Player player) {
                    player.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.titancombat.must_kneel_first"), true);
                }
            }
        }
    }

    @SubscribeEvent
    public void onRegisterCommands(net.minecraftforge.event.RegisterCommandsEvent event) {
        com.titancombat.entity.transport.collision.VehicleWalkCommand.register(event.getDispatcher());
    }
}
