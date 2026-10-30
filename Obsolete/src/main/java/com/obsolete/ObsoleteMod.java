package com.obsolete;

import com.obsolete.block.ModBlocks;
import com.obsolete.block.entity.ModBlockEntities;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.ModEntities;
import com.obsolete.gui.ModMenuTypes;
import com.obsolete.item.ModCreativeTabs;
import com.obsolete.item.ModItems;
import com.obsolete.network.ModNetworking;
import com.obsolete.recipe.ModRecipeTypes;
import com.obsolete.sound.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.entity.EntityAttributeCreationEvent;
import net.minecraftforge.event.entity.EntityMountEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import software.bernie.geckolib.GeckoLib;

@Mod(ObsoleteMod.MODID)
public class ObsoleteMod {
    public static final String MODID = "obsolete";
    public static final Logger LOGGER = LogManager.getLogger();

    public ObsoleteMod() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        GeckoLib.initialize();

        ModBlocks.register(modEventBus);
        ModBlockEntities.register(modEventBus);
        ModEntities.register(modEventBus);
        ModItems.register(modEventBus);
        ModSounds.register(modEventBus);
        ModCreativeTabs.register(modEventBus);
        ModMenuTypes.register(modEventBus);
        ModRecipeTypes.register(modEventBus);

        modEventBus.addListener(this::commonSetup);
        modEventBus.addListener(this::entityAttributes);

        MinecraftForge.EVENT_BUS.register(this);
        LOGGER.info("OBSOLETE: Exoframe Warfare mod constructed successfully.");
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        event.enqueueWork(ModNetworking::register);
        LOGGER.info("OBSOLETE: Networking, Packets & Components registered.");
    }

    private void entityAttributes(EntityAttributeCreationEvent event) {
        event.put(ModEntities.EXOFRAME.get(), ExoframeEntity.createAttributes().build());
    }

    @SubscribeEvent
    public void onEntityMount(EntityMountEvent event) {
        if (event.isDismounting() && event.getEntityBeingMounted() instanceof ExoframeEntity exoframe) {
            if (event.getEntityMounting() instanceof Player player) {
                // Realistic vehicle safety interlock: cannot dismount while moving at speed unless stopped or crouched
                if (exoframe.getDeltaMovement().horizontalDistanceSqr() > 0.008D && !exoframe.isMechCrouching() && !exoframe.isDying()) {
                    event.setCanceled(true);
                    player.displayClientMessage(Component.translatable("message.obsolete.must_stop_to_dismount"), true);
                }
            }
        }
    }
}
