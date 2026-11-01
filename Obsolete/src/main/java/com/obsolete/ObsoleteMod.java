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

        net.minecraftforge.fml.ModLoadingContext.get().registerConfig(net.minecraftforge.fml.config.ModConfig.Type.CLIENT, com.obsolete.client.ExoframeClientConfig.SPEC);

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
        if (event.getEntityBeingMounted() instanceof ExoframeEntity exoframe) {
            if (event.isMounting() && event.getEntityMounting() instanceof Player) {
                if (!exoframe.level().isClientSide) {
                    exoframe.level().playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_COCKPIT_CLOSE.get(), net.minecraft.sounds.SoundSource.PLAYERS, 1.4F, 1.0F);
                    exoframe.level().playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_PILOT_MOUNT.get(), net.minecraft.sounds.SoundSource.PLAYERS, 1.2F, 1.0F);
                }
            } else if (event.isDismounting() && event.getEntityMounting() instanceof Player player) {
                // Realistic vehicle safety interlock: cannot dismount while airborne/flying or moving at speed
                if (exoframe.isFlying() && !exoframe.isDying()) {
                    event.setCanceled(true);
                    player.displayClientMessage(Component.translatable("message.obsolete.cannot_dismount_while_flying"), true);
                } else if (exoframe.getDeltaMovement().horizontalDistanceSqr() > 0.008D && !exoframe.isMechCrouching() && !exoframe.isDying()) {
                    event.setCanceled(true);
                    player.displayClientMessage(Component.translatable("message.obsolete.must_stop_to_dismount"), true);
                } else if (!exoframe.level().isClientSide) {
                    exoframe.level().playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_COCKPIT_OPEN.get(), net.minecraft.sounds.SoundSource.PLAYERS, 1.4F, 1.0F);
                    exoframe.level().playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_PILOT_DISMOUNT.get(), net.minecraft.sounds.SoundSource.PLAYERS, 1.2F, 1.0F);
                }
            }
        }
    }

    @SubscribeEvent
    public void onStartTracking(net.minecraftforge.event.entity.player.PlayerEvent.StartTracking event) {
        if (event.getTarget() instanceof ExoframeEntity exoframe && event.getEntity() instanceof net.minecraft.server.level.ServerPlayer player) {
            int slots = exoframe.getModularInventory().getSlots();
            for (int i = 0; i < slots; i++) {
                net.minecraft.world.item.ItemStack stack = exoframe.getModularInventory().getStackInSlot(i);
                if (!stack.isEmpty()) {
                    com.obsolete.network.ModNetworking.sendToPlayer(
                            new com.obsolete.network.ExoframeInventorySyncS2CPacket(exoframe.getId(), i, stack), player);
                }
            }
        }
    }
}
