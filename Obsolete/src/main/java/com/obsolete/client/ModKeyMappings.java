package com.obsolete.client;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import org.lwjgl.glfw.GLFW;

public class ModKeyMappings {
    public static final String KEY_CATEGORY = "key.category.obsolete";

    public static final KeyMapping KEY_FIRE_WEAPON = new KeyMapping(
            "key.obsolete.fire",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_G,
            KEY_CATEGORY
    );

    public static final KeyMapping KEY_MECH_CROUCH = new KeyMapping(
            "key.obsolete.crouch",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_C,
            KEY_CATEGORY
    );

    // Same order as ExoframeEntity.EMOTES
    public static final KeyMapping[] KEY_EMOTES = {
            new KeyMapping("key.obsolete.emote.salute", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, KEY_CATEGORY),
            new KeyMapping("key.obsolete.emote.wave", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_B, KEY_CATEGORY),
            new KeyMapping("key.obsolete.emote.point", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_N, KEY_CATEGORY),
            new KeyMapping("key.obsolete.emote.scan", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_H, KEY_CATEGORY),
    };

    public static void register(RegisterKeyMappingsEvent event) {
        event.register(KEY_FIRE_WEAPON);
        event.register(KEY_MECH_CROUCH);
        for (KeyMapping key : KEY_EMOTES) {
            event.register(key);
        }
    }
}
