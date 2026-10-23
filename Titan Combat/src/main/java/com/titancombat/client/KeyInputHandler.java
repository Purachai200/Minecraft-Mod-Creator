package com.titancombat.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.network.MechControlC2SPacket;
import com.titancombat.network.MechEjectC2SPacket;
import com.titancombat.network.ModNetworking;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, value = Dist.CLIENT)
public class KeyInputHandler {
    public static final String KEY_CATEGORY_TITAN = "key.category.titancombat";

    public static final KeyMapping KEY_EJECT = new KeyMapping(
            "key.titancombat.eject",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_X,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_FIRE = new KeyMapping(
            "key.titancombat.fire",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_G,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_MELEE = new KeyMapping(
            "key.titancombat.melee",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_F,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_DEFENSE = new KeyMapping(
            "key.titancombat.defense",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_C,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_CORE = new KeyMapping(
            "key.titancombat.core",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_V,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_KNEEL = new KeyMapping(
            "key.titancombat.kneel",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_Z,
            KEY_CATEGORY_TITAN
    );

    @SubscribeEvent
    public static void onKeyInput(InputEvent.Key event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || !(mc.player.getVehicle() instanceof BaseMechEntity)) {
            return;
        }

        // 1. Instant Rocket Dash on Spacebar tap
        if (mc.options.keyJump.consumeClick()) {
            float forward = mc.player.zza;
            float strafe = mc.player.xxa;
            if (Math.abs(forward) < 0.1F && Math.abs(strafe) < 0.1F) {
                forward = 1.0F; // Default forward dash
            }
            ModNetworking.sendToServer(new MechControlC2SPacket(forward, strafe, true, false, false, false, false, false));
        }

        // 2. Toggle Kneel / Park Mode
        if (KEY_KNEEL.consumeClick()) {
            ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, false, false, false, false, true));
        }

        // 3. Dismount Lock Alert: If player taps Shift while Titan is standing
        if (event.getAction() == GLFW.GLFW_PRESS && mc.options.keyShift.matches(event.getKey(), event.getScanCode())) {
            if (mc.player.getVehicle() instanceof BaseTitanEntity titan && !titan.isSitting()) {
                mc.player.displayClientMessage(Component.translatable("message.titancombat.must_kneel_first"), true);
                mc.player.playSound(SoundEvents.NOTE_BLOCK_BASS.get(), 1.0F, 0.6F);
            }
        }

        if (KEY_EJECT.consumeClick()) {
            ModNetworking.sendToServer(new MechEjectC2SPacket());
        }

        if (KEY_DEFENSE.consumeClick()) {
            ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, false, true, false, false, false));
        }

        if (KEY_CORE.consumeClick()) {
            ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, false, false, true, false, false));
        }

        if (KEY_MELEE.consumeClick()) {
            ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, false, false, false, true, false));
        }

        if (KEY_FIRE.isDown()) {
            ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, true, false, false, false, false));
        }
    }

    @SubscribeEvent
    public static void onInteraction(InputEvent.InteractionKeyMappingTriggered event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && mc.player.getVehicle() instanceof BaseMechEntity) {
            // Left click naturally fires the heavy titan weapon when in cockpit!
            if (event.isAttack()) {
                event.setCanceled(true);
                event.setSwingHand(false);
                ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, true, false, false, false, false));
            }
        }
    }

    @SubscribeEvent
    public static void onRenderGuiOverlayPre(RenderGuiOverlayEvent.Pre event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && mc.player.getVehicle() instanceof BaseMechEntity) {
            ResourceLocation id = event.getOverlay().id();
            String path = id.getPath();

            // Suppress horse / animal mount health, jump bar, and biological survival icons
            if (path.equals("mount_health") || path.equals("jump_bar") || path.contains("mount")
                    || path.equals("player_health") || path.equals("food_level") || path.equals("armor_level") || path.equals("air_level")) {
                event.setCanceled(true);
            }
        }
    }

    public static void registerKeys(RegisterKeyMappingsEvent event) {
        event.register(KEY_EJECT);
        event.register(KEY_FIRE);
        event.register(KEY_MELEE);
        event.register(KEY_DEFENSE);
        event.register(KEY_CORE);
        event.register(KEY_KNEEL);
    }
}
