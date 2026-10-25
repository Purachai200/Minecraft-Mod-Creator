package com.titancombat.entity;

import com.titancombat.TitanCombatMod;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, TitanCombatMod.MODID);

    public static final RegistryObject<EntityType<AegisStrikerEntity>> AEGIS_STRIKER =
            ENTITY_TYPES.register("aegis_striker", () -> EntityType.Builder.of(AegisStrikerEntity::new, MobCategory.MISC)
                    .sized(2.4F, 4.2F).clientTrackingRange(12).updateInterval(2).build("aegis_striker"));

    public static final RegistryObject<EntityType<IonTitanEntity>> ION_TITAN =
            ENTITY_TYPES.register("ion_titan", () -> EntityType.Builder.of(IonTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.ION.getWidth(), TitanClass.ION.getHeight()).clientTrackingRange(16).updateInterval(2).build("ion_titan"));

    public static final RegistryObject<EntityType<ScorchTitanEntity>> SCORCH_TITAN =
            ENTITY_TYPES.register("scorch_titan", () -> EntityType.Builder.of(ScorchTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.SCORCH.getWidth(), TitanClass.SCORCH.getHeight()).clientTrackingRange(16).updateInterval(2).build("scorch_titan"));

    public static final RegistryObject<EntityType<RoninTitanEntity>> RONIN_TITAN =
            ENTITY_TYPES.register("ronin_titan", () -> EntityType.Builder.of(RoninTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.RONIN.getWidth(), TitanClass.RONIN.getHeight()).clientTrackingRange(16).updateInterval(2).build("ronin_titan"));

    public static final RegistryObject<EntityType<ToneTitanEntity>> TONE_TITAN =
            ENTITY_TYPES.register("tone_titan", () -> EntityType.Builder.of(ToneTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.TONE.getWidth(), TitanClass.TONE.getHeight()).clientTrackingRange(16).updateInterval(2).build("tone_titan"));

    public static final RegistryObject<EntityType<LegionTitanEntity>> LEGION_TITAN =
            ENTITY_TYPES.register("legion_titan", () -> EntityType.Builder.of(LegionTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.LEGION.getWidth(), TitanClass.LEGION.getHeight()).clientTrackingRange(16).updateInterval(2).build("legion_titan"));

    public static final RegistryObject<EntityType<MonarchTitanEntity>> MONARCH_TITAN =
            ENTITY_TYPES.register("monarch_titan", () -> EntityType.Builder.of(MonarchTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.MONARCH.getWidth(), TitanClass.MONARCH.getHeight()).clientTrackingRange(16).updateInterval(2).build("monarch_titan"));

    public static final RegistryObject<EntityType<NorthstarTitanEntity>> NORTHSTAR_TITAN =
            ENTITY_TYPES.register("northstar_titan", () -> EntityType.Builder.of(NorthstarTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.NORTHSTAR.getWidth(), TitanClass.NORTHSTAR.getHeight()).clientTrackingRange(16).updateInterval(2).build("northstar_titan"));

    public static final RegistryObject<EntityType<TrooperTitanEntity>> TROOPER_TITAN =
            ENTITY_TYPES.register("trooper_titan", () -> EntityType.Builder.of(TrooperTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.TROOPER.getWidth(), TitanClass.TROOPER.getHeight()).clientTrackingRange(16).updateInterval(2).build("trooper_titan"));
    public static final RegistryObject<EntityType<ScoutTitanEntity>> SCOUT_TITAN =
            ENTITY_TYPES.register("scout_titan", () -> EntityType.Builder.of(ScoutTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.SCOUT.getWidth(), TitanClass.SCOUT.getHeight()).clientTrackingRange(16).updateInterval(2).build("scout_titan"));
    public static final RegistryObject<EntityType<ShadeTitanEntity>> SHADE_TITAN =
            ENTITY_TYPES.register("shade_titan", () -> EntityType.Builder.of(ShadeTitanEntity::new, MobCategory.MISC)
                    .sized(TitanClass.SHADE.getWidth(), TitanClass.SHADE.getHeight()).clientTrackingRange(16).updateInterval(2).build("shade_titan"));

    public static final RegistryObject<EntityType<TitanEnergyBlastEntity>> ENERGY_BLAST =
            ENTITY_TYPES.register("energy_blast", () -> EntityType.Builder.<TitanEnergyBlastEntity>of(TitanEnergyBlastEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(8).updateInterval(1).build("energy_blast"));

    public static void register(IEventBus eventBus) {
        ENTITY_TYPES.register(eventBus);
    }
}
