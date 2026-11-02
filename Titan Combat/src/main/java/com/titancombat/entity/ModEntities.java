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

    public static final RegistryObject<EntityType<StrikerTitanFrameEntity>> STRIKER_FRAME_TITAN =
            ENTITY_TYPES.register("striker_frame_titan", () -> EntityType.Builder.of(StrikerTitanFrameEntity::new, MobCategory.MISC)
                    .sized(TitanClass.STRIKER_FRAME.getWidth(), TitanClass.STRIKER_FRAME.getHeight()).clientTrackingRange(16).updateInterval(2).build("striker_frame_titan"));

    public static final RegistryObject<EntityType<VanguardTitanFrameEntity>> VANGUARD_FRAME_TITAN =
            ENTITY_TYPES.register("vanguard_frame_titan", () -> EntityType.Builder.of(VanguardTitanFrameEntity::new, MobCategory.MISC)
                    .sized(TitanClass.VANGUARD_FRAME.getWidth(), TitanClass.VANGUARD_FRAME.getHeight()).clientTrackingRange(16).updateInterval(2).build("vanguard_frame_titan"));

    public static final RegistryObject<EntityType<ColossusTitanFrameEntity>> COLOSSUS_FRAME_TITAN =
            ENTITY_TYPES.register("colossus_frame_titan", () -> EntityType.Builder.of(ColossusTitanFrameEntity::new, MobCategory.MISC)
                    .sized(TitanClass.COLOSSUS_FRAME.getWidth(), TitanClass.COLOSSUS_FRAME.getHeight()).clientTrackingRange(16).updateInterval(2).build("colossus_frame_titan"));

    public static final RegistryObject<EntityType<TerrainTitanFrameEntity>> TERRAIN_FRAME_TITAN =
            ENTITY_TYPES.register("terrain_frame_titan", () -> EntityType.Builder.of(TerrainTitanFrameEntity::new, MobCategory.MISC)
                    .sized(TitanClass.TERRAIN_FRAME.getWidth(), TitanClass.TERRAIN_FRAME.getHeight()).clientTrackingRange(16).updateInterval(2).build("terrain_frame_titan"));

    public static final RegistryObject<EntityType<CyclopsTitanFrameEntity>> CYCLOPS_FRAME_TITAN =
            ENTITY_TYPES.register("cyclops_frame_titan", () -> EntityType.Builder.of(CyclopsTitanFrameEntity::new, MobCategory.MISC)
                    .sized(TitanClass.CYCLOPS_FRAME.getWidth(), TitanClass.CYCLOPS_FRAME.getHeight()).clientTrackingRange(16).updateInterval(2).build("cyclops_frame_titan"));

    public static final RegistryObject<EntityType<SpiderTitanFrameEntity>> SPIDER_FRAME_TITAN =
            ENTITY_TYPES.register("spider_frame_titan", () -> EntityType.Builder.of(SpiderTitanFrameEntity::new, MobCategory.MISC)
                    .sized(TitanClass.SPIDER_FRAME.getWidth(), TitanClass.SPIDER_FRAME.getHeight()).clientTrackingRange(16).updateInterval(2).build("spider_frame_titan"));

    public static final RegistryObject<EntityType<TitanEnergyBlastEntity>> ENERGY_BLAST =
            ENTITY_TYPES.register("energy_blast", () -> EntityType.Builder.<TitanEnergyBlastEntity>of(TitanEnergyBlastEntity::new, MobCategory.MISC)
                    .sized(0.5F, 0.5F).clientTrackingRange(8).updateInterval(1).build("energy_blast"));

    public static final RegistryObject<EntityType<TitanBulletEntity>> TITAN_BULLET =
            ENTITY_TYPES.register("titan_bullet", () -> EntityType.Builder.<TitanBulletEntity>of(TitanBulletEntity::new, MobCategory.MISC)
                    .sized(0.6F, 0.6F).clientTrackingRange(16).updateInterval(1).build("titan_bullet"));

    public static final RegistryObject<EntityType<TitanCasingEntity>> TITAN_CASING =
            ENTITY_TYPES.register("titan_casing", () -> EntityType.Builder.<TitanCasingEntity>of(TitanCasingEntity::new, MobCategory.MISC)
                    .sized(0.35F, 0.35F).clientTrackingRange(8).updateInterval(1).build("titan_casing"));

    public static final RegistryObject<EntityType<TitanSmokeShellEntity>> TITAN_SMOKE_SHELL =
            ENTITY_TYPES.register("titan_smoke_shell", () -> EntityType.Builder.<TitanSmokeShellEntity>of(TitanSmokeShellEntity::new, MobCategory.MISC)
                    .sized(0.8F, 0.8F).clientTrackingRange(16).updateInterval(1).build("titan_smoke_shell"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanHaulerTruckEntity>> HAULER_TRUCK =
            ENTITY_TYPES.register("hauler_truck", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanHaulerTruckEntity::new, MobCategory.MISC)
                    .sized(3.8F, 3.2F).clientTrackingRange(16).updateInterval(2).build("hauler_truck"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanCargoBargeEntity>> CARGO_BARGE =
            ENTITY_TYPES.register("cargo_barge", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanCargoBargeEntity::new, MobCategory.MISC)
                    .sized(5.2F, 2.8F).clientTrackingRange(16).updateInterval(2).build("cargo_barge"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanSkyCraneDroneEntity>> SKYCRANE_DRONE =
            ENTITY_TYPES.register("skycrane_drone", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanSkyCraneDroneEntity::new, MobCategory.MISC)
                    .sized(5.0F, 3.5F).clientTrackingRange(16).updateInterval(2).build("skycrane_drone"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanOceanCarrierEntity>> OCEAN_CARRIER =
            ENTITY_TYPES.register("ocean_carrier", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanOceanCarrierEntity::new, MobCategory.MISC)
                    .sized(8.0F, 4.0F).clientTrackingRange(16).updateInterval(2).build("ocean_carrier"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanTacticalTruckEntity>> TACTICAL_TRUCK =
            ENTITY_TYPES.register("tactical_truck", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanTacticalTruckEntity::new, MobCategory.MISC)
                    .sized(3.2F, 2.6F).clientTrackingRange(16).updateInterval(2).build("tactical_truck"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanChinookTransporterEntity>> CHINOOK_TRANSPORTER =
            ENTITY_TYPES.register("chinook_transporter", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanChinookTransporterEntity::new, MobCategory.MISC)
                    .sized(7.5F, 4.2F).clientTrackingRange(16).updateInterval(2).build("chinook_transporter"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanV22OspreyEntity>> V22_OSPREY =
            ENTITY_TYPES.register("v22_osprey", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanV22OspreyEntity::new, MobCategory.MISC)
                    .sized(6.5F, 3.8F).clientTrackingRange(16).updateInterval(2).build("v22_osprey"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanArmoredApcEntity>> ARMORED_APC =
            ENTITY_TYPES.register("armored_apc", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanArmoredApcEntity::new, MobCategory.MISC)
                    .sized(3.8F, 2.8F).clientTrackingRange(16).updateInterval(2).build("armored_apc"));

    public static final RegistryObject<EntityType<com.titancombat.entity.transport.TitanMobileSuitTrailerEntity>> MOBILE_SUIT_TRAILER =
            ENTITY_TYPES.register("mobile_suit_trailer", () -> EntityType.Builder.of(com.titancombat.entity.transport.TitanMobileSuitTrailerEntity::new, MobCategory.MISC)
                    .sized(6.8F, 3.4F).clientTrackingRange(16).updateInterval(2).build("mobile_suit_trailer"));

    public static void register(IEventBus eventBus) {
        ENTITY_TYPES.register(eventBus);
    }
}
