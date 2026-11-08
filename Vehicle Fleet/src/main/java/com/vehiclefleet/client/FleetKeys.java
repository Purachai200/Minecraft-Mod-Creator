package com.vehiclefleet.client;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import org.lwjgl.glfw.GLFW;

public final class FleetKeys {
    public static final String CATEGORY = "key.categories.vehiclefleet";
    public static final KeyMapping CLIMB = new KeyMapping("key.vehiclefleet.climb", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_SPACE, CATEGORY);
    public static final KeyMapping DESCEND = new KeyMapping("key.vehiclefleet.descend", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_C, CATEGORY);
    public static final KeyMapping SEAT = new KeyMapping("key.vehiclefleet.seat", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_V, CATEGORY);
    public static final KeyMapping OPEN = new KeyMapping("key.vehiclefleet.open", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_B, CATEGORY);
    public static final KeyMapping LIGHTS = new KeyMapping("key.vehiclefleet.lights", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_H, CATEGORY);
    public static final KeyMapping RELEASE = new KeyMapping("key.vehiclefleet.release", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_X, CATEGORY);
    public static final KeyMapping HORN = new KeyMapping("key.vehiclefleet.horn", InputConstants.Type.KEYSYM, GLFW.GLFW_KEY_R, CATEGORY);

    private FleetKeys() {}
}
