package com.youjoarms.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

public class ModEntities {
    public static final DeferredRegister<EntityType<?>> ENTITIES =
            DeferredRegister.create(ForgeRegistries.ENTITY_TYPES, "youjoarms");

    public static final RegistryObject<EntityType<ArtilleryShellEntity>> ARTILLERY_SHELL =
            ENTITIES.register("artillery_shell", () ->
                    EntityType.Builder.<ArtilleryShellEntity>of(ArtilleryShellEntity::new, MobCategory.MISC)
                            .sized(0.4F, 0.4F)
                            .clientTrackingRange(64)
                            .updateInterval(1)
                            .build("artillery_shell")
            );

    public static final RegistryObject<EntityType<FormulaZoneEntity>> FORMULA_ZONE =
            ENTITIES.register("formula_zone", () ->
                    EntityType.Builder.<FormulaZoneEntity>of(FormulaZoneEntity::new, MobCategory.MISC)
                            .sized(0.5F, 0.5F)
                            .clientTrackingRange(160)
                            .updateInterval(1)
                            .build("formula_zone")
            );
}
