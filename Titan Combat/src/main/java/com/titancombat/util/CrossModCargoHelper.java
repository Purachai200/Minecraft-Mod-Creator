package com.titancombat.util;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import java.lang.reflect.Method;

/**
 * Utility helper to safely interact with entities from other mods (such as Obsolete Exoframes)
 * without hard compile-time or runtime crash dependencies.
 */
public class CrossModCargoHelper {

    private static final String OBSOLETE_EXOFRAME_CLASS = "com.obsolete.entity.ExoframeEntity";
    private static Class<?> exoframeClass = null;
    private static Method setCrouchingMethod = null;
    private static boolean checked = false;

    private static void init() {
        if (checked) return;
        checked = true;
        try {
            exoframeClass = Class.forName(OBSOLETE_EXOFRAME_CLASS);
            setCrouchingMethod = exoframeClass.getMethod("setCrouching", boolean.class);
        } catch (Throwable ignored) {
            exoframeClass = null;
            setCrouchingMethod = null;
        }
    }

    public static boolean isExoframe(Entity entity) {
        init();
        return exoframeClass != null && exoframeClass.isInstance(entity);
    }

    public static boolean isCargoEligible(Entity entity) {
        if (entity instanceof com.titancombat.entity.BaseTitanEntity) return true;
        if (entity instanceof com.titancombat.entity.BaseMechEntity) return true;
        return isExoframe(entity);
    }

    public static void setExoframeTransportLock(Entity entity, boolean lock) {
        init();
        if (isExoframe(entity)) {
            try {
                if (setCrouchingMethod != null) {
                    setCrouchingMethod.invoke(entity, lock);
                }
            } catch (Throwable ignored) {}
            entity.setDeltaMovement(Vec3.ZERO);
            entity.fallDistance = 0.0F;
        }
    }

    public static void repairAndChargeCargo(Entity cargo, int energyAvailable, java.util.function.Consumer<Integer> energyDeductor) {
        if (cargo instanceof com.titancombat.entity.BaseTitanEntity titan) {
            // 1. Repair Titan HP if damaged
            if (titan.getHealth() < titan.getMaxHealth() && energyAvailable >= 50) {
                titan.heal(2.0F);
                energyDeductor.accept(50);
            }
            // 2. Charge Titan Energy battery
            int titanEnergy = titan.getEnergy();
            int maxTitanEnergy = titan.getMaxEnergy();
            if (titanEnergy < maxTitanEnergy && energyAvailable >= 200) {
                int toAdd = Math.min(200, maxTitanEnergy - titanEnergy);
                titan.setEnergy(titanEnergy + toAdd);
                energyDeductor.accept(toAdd);
            }
        } else if (isExoframe(cargo) && cargo instanceof LivingEntity living) {
            // Repair Obsolete Exoframe HP
            if (living.getHealth() < living.getMaxHealth() && energyAvailable >= 50) {
                living.heal(2.0F);
                energyDeductor.accept(50);
            }
        }
    }
}
