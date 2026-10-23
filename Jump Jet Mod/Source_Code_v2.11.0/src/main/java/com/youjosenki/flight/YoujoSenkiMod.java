package com.youjosenki.flight;

import com.youjosenki.flight.compat.curios.CuriosCompat;
import com.youjosenki.flight.item.ModCreativeTabs;
import com.youjosenki.flight.item.ModItems;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.InterModComms;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.event.lifecycle.InterModEnqueueEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import top.theillusivec4.curios.api.SlotTypeMessage;
import top.theillusivec4.curios.api.SlotTypePreset;

@Mod(YoujoSenkiMod.MODID)
public class YoujoSenkiMod {
    public static final String MODID = "youjosenki";
    public static final Logger LOGGER = LogManager.getLogger(MODID);

    public YoujoSenkiMod() {
        IEventBus modEventBus = FMLJavaModLoadingContext.get().getModEventBus();

        // Register Config
        ModLoadingContext.get().registerConfig(ModConfig.Type.COMMON, Config.COMMON_SPEC);

        // Register Deferred Registers
        ModItems.ITEMS.register(modEventBus);
        ModCreativeTabs.CREATIVE_MODE_TABS.register(modEventBus);
        com.youjosenki.flight.recipe.ModRecipes.RECIPE_SERIALIZERS.register(modEventBus);

        // Lifecycle Events
        modEventBus.addListener(this::commonSetup);
        modEventBus.addListener(this::enqueueIMC);

        LOGGER.info("Youjo Senki: Aerial Mage Equipment mod initialized successfully!");
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            com.youjosenki.flight.network.ModNetworking.register();

            // Cauldron washing interaction: Right click a water cauldron to wash off faction banner or dye!
            for (net.minecraftforge.registries.RegistryObject<net.minecraft.world.item.Item> entry : ModItems.ITEMS.getEntries()) {
                net.minecraft.world.item.Item item = entry.get();
                net.minecraft.core.cauldron.CauldronInteraction.WATER.put(item, (state, level, pos, player, hand, stack) -> {
                    boolean hasBanner = stack.getTagElement("BlockEntityTag") != null;
                    boolean hasColor = stack.getTagElement(net.minecraft.world.item.DyeableLeatherItem.TAG_DISPLAY) != null &&
                            stack.getTagElement(net.minecraft.world.item.DyeableLeatherItem.TAG_DISPLAY).contains(net.minecraft.world.item.DyeableLeatherItem.TAG_COLOR);

                    if (!hasBanner && !hasColor) {
                        return net.minecraft.world.InteractionResult.PASS;
                    }

                    if (!level.isClientSide) {
                        if (hasBanner) {
                            stack.removeTagKey("BlockEntityTag");
                            player.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.youjosenki.banner_removed"), true);
                        } else {
                            if (stack.getItem() instanceof net.minecraft.world.item.DyeableLeatherItem dyeable) {
                                dyeable.clearColor(stack);
                                player.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.youjosenki.dye_removed"), true);
                            }
                        }
                        net.minecraft.world.level.block.LayeredCauldronBlock.lowerFillLevel(state, level, pos);
                    }
                    return net.minecraft.world.InteractionResult.sidedSuccess(level.isClientSide);
                });
            }
        });
    }

    private void enqueueIMC(final InterModEnqueueEvent event) {
        if (CuriosCompat.isCuriosLoaded()) {
            // Ensure Belt and Body slots are available in Curios
            InterModComms.sendTo(CuriosCompat.CURIOS_MODID, SlotTypeMessage.REGISTER_TYPE,
                    () -> SlotTypePreset.BELT.getMessageBuilder().build());
            InterModComms.sendTo(CuriosCompat.CURIOS_MODID, SlotTypeMessage.REGISTER_TYPE,
                    () -> SlotTypePreset.BODY.getMessageBuilder().build());
        }
    }
}
