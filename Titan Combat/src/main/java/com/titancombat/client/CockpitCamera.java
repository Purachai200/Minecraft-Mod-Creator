package com.titancombat.client;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.client.Camera;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderPlayerEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.util.ObfuscationReflectionHelper;

import java.lang.reflect.Method;

/**
 * Camera behaviour while piloting: impact shake (trauma model), weapon recoil kick, a third-person
 * camera pulled far enough back to frame a 7-block titan, and hiding the pilot's body inside the
 * sealed cockpit.
 */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, value = Dist.CLIENT)
public final class CockpitCamera {
    private static final double THIRD_PERSON_EXTRA_DISTANCE = 7.0D;

    private static float trauma = 0.0F;
    private static float recoil = 0.0F;
    private static float recoilPrev = 0.0F;

    private static Method cameraMove;
    private static Method cameraMaxZoom;
    private static boolean reflectionFailed = false;

    private CockpitCamera() {}

    public static void addTrauma(float amount) {
        trauma = Math.min(1.0F, trauma + amount);
    }

    public static void addRecoil(float degrees) {
        recoil = Math.min(6.0F, recoil + degrees);
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        trauma = Math.max(0.0F, trauma - 0.045F);
        recoilPrev = recoil;
        recoil *= 0.62F;
    }

    @SubscribeEvent
    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null) return;

        float time = (float) (player.tickCount + event.getPartialTick());
        float shake = trauma * trauma;
        if (shake > 0.0001F) {
            event.setPitch(event.getPitch() + shake * 4.0F * noise(time * 1.9F, 1.3F));
            event.setYaw(event.getYaw() + shake * 2.5F * noise(time * 1.7F, 7.1F));
            event.setRoll(event.getRoll() + shake * 3.0F * noise(time * 2.3F, 3.7F));
        }

        boolean inTitan = player.getVehicle() instanceof BaseTitanEntity;
        boolean inTransport = player.getVehicle() instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity;
        if (!inTitan && !inTransport) return;

        if (inTitan) {
            float kick = recoilPrev + (recoil - recoilPrev) * (float) event.getPartialTick();
            event.setPitch(event.getPitch() - kick);
        }

        if (mc.options.getCameraType() != CameraType.FIRST_PERSON) {
            pullBack(event.getCamera(), mc.options.getCameraType() == CameraType.THIRD_PERSON_FRONT);
        }
    }

    /** Vanilla stops the 3rd-person camera 4 blocks out, inside the titan's back; push it further. */
    private static void pullBack(Camera camera, boolean front) {
        if (reflectionFailed) return;
        try {
            if (cameraMove == null) {
                cameraMove = ObfuscationReflectionHelper.findMethod(Camera.class, "m_90568_", double.class, double.class, double.class);
                cameraMaxZoom = ObfuscationReflectionHelper.findMethod(Camera.class, "m_90566_", double.class);
            }
            double extra = (double) cameraMaxZoom.invoke(camera, THIRD_PERSON_EXTRA_DISTANCE);
            cameraMove.invoke(camera, -extra, 0.0D, 0.0D);
        } catch (Exception e) {
            reflectionFailed = true;
            TitanCombatMod.LOGGER.warn("Titan third-person camera offset unavailable", e);
        }
    }

    /** The pilot sits sealed inside the hull; don't draw them floating through the armour. */
    @SubscribeEvent
    public static void onRenderPlayer(RenderPlayerEvent.Pre event) {
        if (event.getEntity().getVehicle() instanceof BaseTitanEntity) {
            event.setCanceled(true);
        }
    }

    private static float noise(float t, float seed) {
        return (float) (Math.sin(t + seed) * 0.6D + Math.sin(t * 2.7D + seed * 1.9D) * 0.4D);
    }
}
