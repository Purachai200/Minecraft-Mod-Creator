package com.youjosenki.flight.client;

import com.youjosenki.flight.YoujoSenkiMod;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Trauma-based camera shake + FOV punch for the local pilot: hard kick on boost, heavy thud on
 * touchdown scaled by rig mass, and a light rumble while sprint-flying or hovering low.
 * Honours the vanilla "Distortion Effects" and "FOV Effects" accessibility sliders.
 */
@Mod.EventBusSubscriber(modid = YoujoSenkiMod.MODID, value = Dist.CLIENT)
public class CinematicCamera {
    private static float trauma;
    private static float fovKick;
    private static boolean wasFlying;
    private static double lastSpeed;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        LocalPlayer player = Minecraft.getInstance().player;
        if (player == null || Minecraft.getInstance().isPaused()) return;

        trauma *= 0.86F;
        fovKick *= 0.84F;
        ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
        if (unit == null || !(unit.getItem() instanceof EleniumFlightUnitItem item)) {
            wasFlying = false;
            return;
        }
        float thrust = item.getThrustClass();
        boolean flying = player.getAbilities().flying;
        double dx = player.getX() - player.xo, dy = player.getY() - player.yo, dz = player.getZ() - player.zo;
        double speed = Math.sqrt(dx * dx + dy * dy + dz * dz);

        if (wasFlying && !flying && player.onGround()) {
            trauma = Math.min(1.0F, trauma + 0.35F + 0.2F * thrust);  // touchdown
        } else if (flying && speed - lastSpeed > 0.2) {
            trauma = Math.min(1.0F, trauma + 0.3F);                    // boost pulse
            fovKick = Math.min(0.25F, fovKick + 0.08F * item.getBoostMultiplier());
        } else if (flying && player.isSprinting()) {
            trauma = Math.max(trauma, 0.12F);                          // airframe buffeting
        } else if (flying && player.getY() - player.level().getHeight(
                net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING, player.getBlockX(), player.getBlockZ()) < 3.0) {
            trauma = Math.max(trauma, 0.05F * thrust);                 // ground-effect rumble
        }
        wasFlying = flying;
        lastSpeed = speed;
    }

    @SubscribeEvent
    public static void onCameraAngles(ViewportEvent.ComputeCameraAngles event) {
        if (trauma < 0.01F) return;
        float scale = Minecraft.getInstance().options.screenEffectScale().get().floatValue();
        float shake = trauma * trauma * scale;
        float t = (float) ((Minecraft.getInstance().player != null ? Minecraft.getInstance().player.tickCount : 0) + event.getPartialTick());
        // Layered sines read as smooth noise; each axis gets its own frequencies
        event.setYaw(event.getYaw() + 3.0F * shake * (Mth.sin(t * 2.1F) + 0.5F * Mth.sin(t * 5.3F)));
        event.setPitch(event.getPitch() + 3.0F * shake * (Mth.sin(t * 2.7F + 1.3F) + 0.5F * Mth.sin(t * 6.1F)));
        event.setRoll(event.getRoll() + 5.0F * shake * (Mth.sin(t * 1.7F + 2.1F) + 0.5F * Mth.sin(t * 4.3F)));
    }

    @SubscribeEvent
    public static void onFov(ViewportEvent.ComputeFov event) {
        if (fovKick < 0.005F) return;
        float scale = Minecraft.getInstance().options.fovEffectScale().get().floatValue();
        event.setFOV(event.getFOV() * (1.0 + fovKick * scale));
    }
}
