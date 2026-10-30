package com.obsolete.entity;

import com.obsolete.ObsoleteMod;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, ObsoleteMod.MODID);

    public static final RegistryObject<EntityType<ExoframeEntity>> EXOFRAME =
            ENTITIES.register("exoframe", () ->
                    EntityType.Builder.of(ExoframeEntity::new, MobCategory.MISC)
                            .sized(1.2F * ExoframeEntity.MODEL_SCALE, 2.2F * ExoframeEntity.MODEL_SCALE)
                            .clientTrackingRange(16)
                            .updateInterval(1)
                            .fireImmune()
                            .build("exoframe"));

    public static final RegistryObject<EntityType<ExoframeBulletEntity>> BULLET =
            ENTITIES.register("exoframe_bullet", () ->
                    EntityType.Builder.<ExoframeBulletEntity>of(ExoframeBulletEntity::new, MobCategory.MISC)
                            .sized(0.3F, 0.3F)
                            .clientTrackingRange(8)
                            .updateInterval(1)
                            .build("exoframe_bullet"));

    public static final RegistryObject<EntityType<ExoframeRocketEntity>> ROCKET =
            ENTITIES.register("exoframe_rocket", () ->
                    EntityType.Builder.<ExoframeRocketEntity>of(ExoframeRocketEntity::new, MobCategory.MISC)
                            .sized(0.4F, 0.4F)
                            .clientTrackingRange(10)
                            .updateInterval(1)
                            .build("exoframe_rocket"));

    public static void register(IEventBus bus) {
        ENTITIES.register(bus);
    }
}
