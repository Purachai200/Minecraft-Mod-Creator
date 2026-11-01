package com.obsolete.client;

public class CameraShakeManager {
    private static float shakeIntensity = 0.0f;
    private static int shakeTicks = 0;

    public static void addShake(float intensity, int ticks) {
        if (!ExoframeClientConfig.ENABLE_CAMERA_SHAKE.get()) return;
        float mult = ExoframeClientConfig.CAMERA_SHAKE_INTENSITY.get().floatValue();
        shakeIntensity = Math.min(2.5f, shakeIntensity + intensity * mult);
        shakeTicks = Math.max(shakeTicks, ticks);
    }

    public static float getShakeIntensity() {
        return shakeIntensity;
    }

    public static void clientTick() {
        if (shakeTicks > 0) {
            shakeTicks--;
            shakeIntensity *= 0.82f;
            if (shakeTicks <= 0 || shakeIntensity < 0.005f) {
                shakeIntensity = 0.0f;
                shakeTicks = 0;
            }
        }
    }
}
