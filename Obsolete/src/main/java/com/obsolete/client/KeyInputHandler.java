package com.obsolete.client;

import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.network.ExoframeAimC2SPacket;
import com.obsolete.network.ExoframeCrouchC2SPacket;
import com.obsolete.network.ExoframeEmoteC2SPacket;
import com.obsolete.network.ExoframeFlightC2SPacket;
import com.obsolete.network.ExoframeOpenMenuC2SPacket;
import com.obsolete.network.ExoframeFireC2SPacket;
import com.obsolete.network.ExoframeMeleeC2SPacket;
import com.obsolete.network.ModNetworking;
import com.obsolete.item.ModItems;
import com.obsolete.item.ExoframeRocketLauncherItem;
import com.obsolete.item.ExoframeRPG7Item;
import net.minecraft.client.Minecraft;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = ObsoleteMod.MODID, value = Dist.CLIENT)
public class KeyInputHandler {
    private static boolean lastCrouchState = false;
    private static boolean lastAimState = false;
    private static boolean lastFlightState = false;
    private static boolean lastBoostState = false;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        Minecraft mcStart = Minecraft.getInstance();
        if (event.phase == TickEvent.Phase.START) {
            // Inventory key while piloting opens the exoframe loadout (like a horse). START runs before vanilla's
            // keybind handling in the same tick, so consuming the click here stops the player inventory opening.
            if (mcStart.player != null && mcStart.screen == null && mcStart.player.getVehicle() instanceof ExoframeEntity) {
                boolean pressed = false;
                while (mcStart.options.keyInventory.consumeClick()) {
                    pressed = true;
                }
                if (pressed) {
                    ModNetworking.sendToServer(new ExoframeOpenMenuC2SPacket());
                }
            }
            return;
        }

        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && mc.player.getVehicle() instanceof ExoframeEntity exoframe) {
            // Mech Crouch Hold / Toggle
            boolean crouchDown = ModKeyMappings.KEY_MECH_CROUCH.isDown();
            if (crouchDown != lastCrouchState) {
                lastCrouchState = crouchDown;
                ModNetworking.sendToServer(new ExoframeCrouchC2SPacket(crouchDown));
            }

            // Right-Click ADS / Shoulder Aim Lock (ประทับเตรียมยิง)
            boolean aimDown = mc.options.keyUse.isDown();
            if (aimDown != lastAimState) {
                lastAimState = aimDown;
                exoframe.setAiming(aimDown);
                ModNetworking.sendToServer(new ExoframeAimC2SPacket(aimDown));
            }

            // Fire Weapon Keybind
            while (ModKeyMappings.KEY_FIRE_WEAPON.consumeClick()) {
                ModNetworking.sendToServer(new ExoframeFireC2SPacket());
            }

            // Dedicated Quick Melee Punch / Bash Keybind (F key)
            while (ModKeyMappings.KEY_MECH_MELEE.consumeClick()) {
                ModNetworking.sendToServer(new ExoframeMeleeC2SPacket());
            }

            for (int i = 0; i < ModKeyMappings.KEY_EMOTES.length; i++) {
                while (ModKeyMappings.KEY_EMOTES[i].consumeClick()) {
                    ModNetworking.sendToServer(new ExoframeEmoteC2SPacket(ExoframeEntity.EMOTES[i]));
                }
            }

            // Flight booster toggle & boost controls
            if (exoframe.hasFlightBooster()) {
                boolean jumpPressed = mc.options.keyJump.isDown();
                boolean sprintPressed = mc.options.keySprint.isDown();

                boolean flying = exoframe.isFlying();
                if (!flying && !exoframe.onGround() && jumpPressed) {
                    flying = true;
                    exoframe.setFlying(true);
                } else if (flying && exoframe.onGround() && !jumpPressed) {
                    flying = false;
                    exoframe.setFlying(false);
                }

                boolean boosting = flying && sprintPressed;
                exoframe.setFlightBoosting(boosting);

                if (flying != lastFlightState || boosting != lastBoostState) {
                    lastFlightState = flying;
                    lastBoostState = boosting;
                    ModNetworking.sendToServer(new ExoframeFlightC2SPacket(flying, boosting));
                }
            } else if (lastFlightState) {
                lastFlightState = false;
                lastBoostState = false;
                exoframe.setFlying(false);
                exoframe.setFlightBoosting(false);
                ModNetworking.sendToServer(new ExoframeFlightC2SPacket(false, false));
            }
        } else {
            lastCrouchState = false;
            lastAimState = false;
            lastFlightState = false;
            lastBoostState = false;
        }
    }

    /**
     * Intercepts left-click attack & right-click interaction while riding the Exoframe.
     */
    @SubscribeEvent
    public static void onInteractionKey(InputEvent.InteractionKeyMappingTriggered event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && mc.player.getVehicle() instanceof ExoframeEntity exoframe) {
            if (event.isPickBlock()) {
                // Middle-click quick melee smash
                event.setCanceled(true);
                ModNetworking.sendToServer(new ExoframeMeleeC2SPacket());
                return;
            }

            if (event.isAttack()) {
                event.setCanceled(true);
                event.setSwingHand(false);

                ItemStack weapon = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
                ItemStack util = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
                boolean hasShoulderWeapon = util.is(ModItems.MODULE_SHOULDER_MISSILE.get())
                        || util.is(ModItems.MODULE_TWIN_MANPADS.get())
                        || util.getItem() instanceof ExoframeRocketLauncherItem
                        || util.getItem() instanceof ExoframeRPG7Item;

                if (weapon.isEmpty() && !hasShoulderWeapon) {
                    ModNetworking.sendToServer(new ExoframeMeleeC2SPacket());
                } else {
                    ModNetworking.sendToServer(new ExoframeFireC2SPacket());
                }
            } else if (event.isUseItem()) {
                // Prevent vanilla item interaction/eating/block placing while piloting combat vehicle
                event.setCanceled(true);
                event.setSwingHand(false);
            }
        }
    }

    /**
     * Tactical ADS optical zoom when aiming the exoframe weapon.
     */
    @SubscribeEvent
    public static void onComputeFov(ViewportEvent.ComputeFov event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && mc.player.getVehicle() instanceof ExoframeEntity exoframe) {
            if (exoframe.isAiming()) {
                event.setFOV(event.getFOV() * 0.82D); // 18% ADS optical focus zoom
            }
        }
    }
}
