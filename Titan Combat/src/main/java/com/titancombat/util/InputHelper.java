package com.titancombat.util;

import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.fml.util.ObfuscationReflectionHelper;

import java.lang.reflect.Field;

/**
 * Utility helper to safely access vehicle driver input states across client and server
 * without requiring external physics libraries.
 */
public final class InputHelper {
    private static Field jumpingField;

    static {
        try {
            // SRG name for net.minecraft.world.entity.LivingEntity.jumping is f_20899_
            jumpingField = ObfuscationReflectionHelper.findField(LivingEntity.class, "f_20899_");
            jumpingField.setAccessible(true);
        } catch (Exception e1) {
            try {
                jumpingField = LivingEntity.class.getDeclaredField("jumping");
                jumpingField.setAccessible(true);
            } catch (Exception ignored) {
                jumpingField = null;
            }
        }
    }

    private InputHelper() {}

    /**
     * Checks if the given driver entity is currently pressing the jump / ascend key.
     */
    public static boolean isJumping(LivingEntity entity) {
        if (entity == null) return false;

        // Fast-path for local player on client
        if (entity.level().isClientSide && entity instanceof net.minecraft.client.player.LocalPlayer localPlayer) {
            return localPlayer.input.jumping;
        }

        if (jumpingField != null) {
            try {
                return jumpingField.getBoolean(entity);
            } catch (Exception ignored) {}
        }
        return false;
    }
}
