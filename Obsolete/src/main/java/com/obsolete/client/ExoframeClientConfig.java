package com.obsolete.client;

import net.minecraftforge.common.ForgeConfigSpec;

public class ExoframeClientConfig {
    public static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.BooleanValue ENABLE_CAMERA_SHAKE;
    public static final ForgeConfigSpec.DoubleValue CAMERA_SHAKE_INTENSITY;

    static {
        BUILDER.push("Exoframe Client Visuals");
        ENABLE_CAMERA_SHAKE = BUILDER.comment("Enable subtle camera view shake on heavy footsteps, landing, and heavy weapon firing")
                .define("enableCameraShake", true);
        CAMERA_SHAKE_INTENSITY = BUILDER.comment("Camera shake intensity multiplier (0.0 to 2.0)")
                .defineInRange("cameraShakeIntensity", 1.0D, 0.0D, 2.0D);
        BUILDER.pop();
        SPEC = BUILDER.build();
    }
}
