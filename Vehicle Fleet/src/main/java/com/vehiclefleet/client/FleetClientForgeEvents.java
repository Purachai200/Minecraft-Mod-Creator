package com.vehiclefleet.client;

import com.vehiclefleet.VehicleFleetMod;
import com.vehiclefleet.entity.FleetVehicleEntity;
import com.vehiclefleet.net.FleetNet;
import net.minecraft.client.Camera;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.util.ObfuscationReflectionHelper;

import java.lang.reflect.Method;

/** Sends held-key input while riding, one-shot actions, pulls back 3rd-person camera, and runs aboard physics. */
@Mod.EventBusSubscriber(modid = VehicleFleetMod.MODID, value = Dist.CLIENT)
public final class FleetClientForgeEvents {
    private static byte lastFlags;
    private static Method cameraMove;
    private static Method cameraMaxZoom;
    private static boolean reflectionFailed = false;

    private FleetClientForgeEvents() {}

    @SubscribeEvent
    public static void tick(TickEvent.ClientTickEvent e) {
        if (e.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer p = mc.player;
        if (p == null || mc.level == null) return;
        byte flags = 0;
        if (p.getVehicle() instanceof FleetVehicleEntity v && mc.screen == null) {
            if (FleetKeys.CLIMB.isDown() || mc.options.keyJump.isDown()) flags |= 1;
            if (FleetKeys.DESCEND.isDown() || mc.options.keyShift.isDown()) flags |= 2;
            v.setInput(p, flags);
        }
        if (flags != lastFlags) {
            lastFlags = flags;
            FleetNet.CHANNEL.sendToServer(new FleetNet.Input(flags));
        }
        while (FleetKeys.SEAT.consumeClick()) FleetNet.CHANNEL.sendToServer(new FleetNet.Action(FleetNet.ACT_SEAT));
        while (FleetKeys.OPEN.consumeClick()) FleetNet.CHANNEL.sendToServer(new FleetNet.Action(FleetNet.ACT_OPEN));
        while (FleetKeys.LIGHTS.consumeClick()) FleetNet.CHANNEL.sendToServer(new FleetNet.Action(FleetNet.ACT_LIGHTS));
        while (FleetKeys.RELEASE.consumeClick()) FleetNet.CHANNEL.sendToServer(new FleetNet.Action(FleetNet.ACT_RELEASE));
        while (FleetKeys.HORN.consumeClick()) FleetNet.CHANNEL.sendToServer(new FleetNet.Action(FleetNet.ACT_HORN));
        if (!mc.isPaused()) AboardHandler.tick(mc, p);
    }

    @SubscribeEvent
    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || !(player.getVehicle() instanceof FleetVehicleEntity vehicle)) return;

        if (mc.options.getCameraType() != CameraType.FIRST_PERSON) {
            pullBack(event.getCamera(), Math.max(4.0D, vehicle.spec.half_width / 8.0D + 2.5D));
        }
    }

    private static void pullBack(Camera camera, double distance) {
        if (reflectionFailed) return;
        try {
            if (cameraMove == null) {
                cameraMove = ObfuscationReflectionHelper.findMethod(Camera.class, "m_90568_", double.class, double.class, double.class);
                cameraMaxZoom = ObfuscationReflectionHelper.findMethod(Camera.class, "m_90566_", double.class);
            }
            double extra = (double) cameraMaxZoom.invoke(camera, distance);
            cameraMove.invoke(camera, -extra, 0.0D, 0.0D);
        } catch (Exception e) {
            reflectionFailed = true;
        }
    }
}
