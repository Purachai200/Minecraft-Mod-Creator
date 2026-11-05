package com.youjoarms.client;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.client.settings.KeyConflictContext;
import org.lwjgl.glfw.GLFW;

public class KeyBindings {
    public static final String KEY_CATEGORY = "key.youjoarms.category";

    public static final KeyMapping CAST_KEY = new KeyMapping(
            "key.youjoarms.cast",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_G,
            KEY_CATEGORY
    );

    public static final KeyMapping CYCLE_KEY = new KeyMapping(
            "key.youjoarms.cycle_formula",
            KeyConflictContext.IN_GAME,
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_V,
            KEY_CATEGORY
    );
}
