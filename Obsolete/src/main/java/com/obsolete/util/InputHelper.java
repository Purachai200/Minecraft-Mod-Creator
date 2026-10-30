package com.obsolete.util;

import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.fml.util.ObfuscationReflectionHelper;

import java.lang.reflect.Field;

public final class InputHelper {
    private static Field jumpingField;

    static {
        try {
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

    public static boolean isJumping(LivingEntity entity) {
        if (entity == null) return false;

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
