package com.youjosenki.flight.item;

import com.youjosenki.flight.YoujoSenkiMod;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

public class ModCreativeTabs {
    public static final DeferredRegister<CreativeModeTab> CREATIVE_MODE_TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, YoujoSenkiMod.MODID);

    public static final RegistryObject<CreativeModeTab> YOUJO_SENKI_TAB = CREATIVE_MODE_TABS.register("youjo_senki_tab",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.youjosenki"))
                    .icon(() -> {
                        ItemStack iconStack = new ItemStack(ModItems.ELENIUM_TYPE95_FLIGHT_UNIT.get());
                        iconStack.getOrCreateTag().putInt("Energy", 1_000_000);
                        return iconStack;
                    })
                    .displayItems((parameters, output) -> {
                        // 1. Elenium Type 95 (The Empire - Tanya Prototype)
                        ItemStack t95 = new ItemStack(ModItems.ELENIUM_TYPE95_FLIGHT_UNIT.get());
                        t95.getOrCreateTag().putInt("Energy", 1_000_000);
                        output.accept(t95);
                        output.accept(new ItemStack(ModItems.ELENIUM_TYPE95_FLIGHT_UNIT.get()));

                        // 2. Elenium Type 97 (The Empire - 203rd Battalion)
                        ItemStack t97 = new ItemStack(ModItems.ELENIUM_TYPE97_FLIGHT_UNIT.get());
                        t97.getOrCreateTag().putInt("Energy", 500_000);
                        output.accept(t97);
                        output.accept(new ItemStack(ModItems.ELENIUM_TYPE97_FLIGHT_UNIT.get()));

                        // 3. Republic Type 101 (Francois Republic)
                        ItemStack rep101 = new ItemStack(ModItems.REPUBLIC_TYPE101_FLIGHT_UNIT.get());
                        rep101.getOrCreateTag().putInt("Energy", 750_000);
                        output.accept(rep101);
                        output.accept(new ItemStack(ModItems.REPUBLIC_TYPE101_FLIGHT_UNIT.get()));

                        // 4. Federation Type 82 (Russy Federation / Soviet)
                        ItemStack fed82 = new ItemStack(ModItems.FEDERATION_TYPE82_FLIGHT_UNIT.get());
                        fed82.getOrCreateTag().putInt("Energy", 1_500_000);
                        output.accept(fed82);
                        output.accept(new ItemStack(ModItems.FEDERATION_TYPE82_FLIGHT_UNIT.get()));

                        // 5. Unified States Model 1923 "Eagle"
                        ItemStack us1923 = new ItemStack(ModItems.ALLIED_TYPE1923_FLIGHT_UNIT.get());
                        us1923.getOrCreateTag().putInt("Energy", 850_000);
                        output.accept(us1923);
                        output.accept(new ItemStack(ModItems.ALLIED_TYPE1923_FLIGHT_UNIT.get()));

                        // 6. Commonwealth Royal Mark II "Spitfire"
                        ItemStack comMk2 = new ItemStack(ModItems.COMMONWEALTH_MK2_FLIGHT_UNIT.get());
                        comMk2.getOrCreateTag().putInt("Energy", 650_000);
                        output.accept(comMk2);
                        output.accept(new ItemStack(ModItems.COMMONWEALTH_MK2_FLIGHT_UNIT.get()));

                        // 7. Legadonia Entente Alliance Alpine Rig
                        ItemStack entSki = new ItemStack(ModItems.ENTENTE_SKIRIG_FLIGHT_UNIT.get());
                        entSki.getOrCreateTag().putInt("Energy", 600_000);
                        output.accept(entSki);
                        output.accept(new ItemStack(ModItems.ENTENTE_SKIRIG_FLIGHT_UNIT.get()));

                        // 8. Tactical Combat Jetpack (Military Combat forces)
                        ItemStack tacJet = new ItemStack(ModItems.TACTICAL_COMBAT_JETPACK.get());
                        tacJet.getOrCreateTag().putInt("Energy", 800_000);
                        output.accept(tacJet);
                        output.accept(new ItemStack(ModItems.TACTICAL_COMBAT_JETPACK.get()));

                        // 9. Titan Heavy Industrial Rocket Pack (Hazard Armor)
                        ItemStack heavyRoc = new ItemStack(ModItems.HEAVY_INDUSTRIAL_ROCKET_PACK.get());
                        heavyRoc.getOrCreateTag().putInt("Energy", 2_500_000);
                        output.accept(heavyRoc);
                        output.accept(new ItemStack(ModItems.HEAVY_INDUSTRIAL_ROCKET_PACK.get()));

                        // 10. Shadow Recon Apex Delta-Wings (Stealth Recon)
                        ItemStack shadWing = new ItemStack(ModItems.SHADOW_RECON_WINGS.get());
                        shadWing.getOrCreateTag().putInt("Energy", 1_000_000);
                        output.accept(shadWing);
                        output.accept(new ItemStack(ModItems.SHADOW_RECON_WINGS.get()));

                        // 11. Imperial Elenium Type 95 Synchronized Exoskeleton (Dual-Leg Prototype)
                        ItemStack t95Exo = new ItemStack(ModItems.ELENIUM_TYPE95_EXO.get());
                        t95Exo.getOrCreateTag().putInt("Energy", 2_000_000);
                        output.accept(t95Exo);
                        output.accept(new ItemStack(ModItems.ELENIUM_TYPE95_EXO.get()));

                        // 12. Titan Mk-II "Juggernaut" Heavy Siege Rig
                        ItemStack siege = new ItemStack(ModItems.TITAN_SIEGE_FRAME.get());
                        siege.getOrCreateTag().putInt("Energy", 3_500_000);
                        output.accept(siege);
                        output.accept(new ItemStack(ModItems.TITAN_SIEGE_FRAME.get()));

                        // 13. Valkyrie Kinetic Hover-Thrust Boots
                        ItemStack valk = new ItemStack(ModItems.VALKYRIE_THRUST_BOOTS.get());
                        valk.getOrCreateTag().putInt("Energy", 600_000);
                        output.accept(valk);
                        output.accept(new ItemStack(ModItems.VALKYRIE_THRUST_BOOTS.get()));

                        // 14. Aquasurf Hydro-Glider Rig
                        ItemStack aqua = new ItemStack(ModItems.AQUASURF_SKIMMER_UNIT.get());
                        aqua.getOrCreateTag().putInt("Energy", 700_000);
                        output.accept(aqua);
                        output.accept(new ItemStack(ModItems.AQUASURF_SKIMMER_UNIT.get()));

                        // 15. Abyssal Combat Scuba Rig
                        ItemStack scuba = new ItemStack(ModItems.ABYSSAL_SCUBA_RIG.get());
                        scuba.getOrCreateTag().putInt("Energy", 800_000);
                        output.accept(scuba);
                        output.accept(new ItemStack(ModItems.ABYSSAL_SCUBA_RIG.get()));

                        // 16. Abyssal Tactical Diving Mask
                        ItemStack mask = new ItemStack(ModItems.ABYSSAL_DIVING_MASK.get());
                        mask.getOrCreateTag().putInt("Energy", 200_000);
                        output.accept(mask);
                        output.accept(new ItemStack(ModItems.ABYSSAL_DIVING_MASK.get()));

                        // 17. Urban Scout Kinetic Exo-Legs
                        ItemStack urban = new ItemStack(ModItems.URBAN_SCOUT_EXOLEGS.get());
                        urban.getOrCreateTag().putInt("Energy", 300_000);
                        output.accept(urban);
                        output.accept(new ItemStack(ModItems.URBAN_SCOUT_EXOLEGS.get()));
                    })
                    .build());
}
