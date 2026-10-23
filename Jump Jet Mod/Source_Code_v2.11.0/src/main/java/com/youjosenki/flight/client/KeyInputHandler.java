package com.youjosenki.flight.client;

import com.youjosenki.flight.client.telemetry.ClientFlightTelemetry;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import com.youjosenki.flight.network.FlightBoostC2SPacket;
import com.youjosenki.flight.network.ModNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "youjosenki", value = Dist.CLIENT)
public class KeyInputHandler {
    private static boolean clientWasFlying = false;
    private static boolean sprintKeyWasDown = false;
    private static int clientBoostCooldown = 0;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || player.isSpectator()) return;

        // Pre-travel ceiling and water clamp (START phase)
        if (event.phase == TickEvent.Phase.START) {
            ItemStack main = EleniumFlightUnitItem.getEquippedMainUnit(player);
            if (main != null && main.getItem() instanceof EleniumFlightUnitItem mainItem) {
                // Scuba rig blocks jumping and flight on land
                if (mainItem.getFlightDesign() == com.youjosenki.flight.client.model.FlightUnitModel.FlightDesign.TACTICAL_SCUBA) {
                    if (player.getAbilities().flying) player.getAbilities().flying = false;
                    player.getAbilities().mayfly = false;
                    if (player.onGround() && !player.isInWater() && player.getDeltaMovement().y > 0.08) {
                        player.setDeltaMovement(player.getDeltaMovement().x, 0.01, player.getDeltaMovement().z);
                    }
                }
            }

            ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
            if (unit != null && EleniumFlightUnitItem.isItemEnergized(unit) && unit.getItem() instanceof EleniumFlightUnitItem item) {
                if (!item.isWaterproof() && player.isInWater()) {
                    if (player.getAbilities().flying) {
                        player.getAbilities().flying = false;
                    }
                    player.getAbilities().mayfly = false;
                    return;
                }
                if (player.getAbilities().flying && !player.onGround() && player.getY() >= item.getServiceCeiling()) {
                    Vec3 vel = player.getDeltaMovement();
                    if (vel.y > 0) {
                        player.setDeltaMovement(vel.x * 0.95, Math.min(vel.y * 0.20, 0.035), vel.z * 0.95);
                    }
                }
            }
            return;
        }

        if (event.phase != TickEvent.Phase.END) return;

        if (clientBoostCooldown > 0) {
            clientBoostCooldown--;
        }

        ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
        if (unit != null && EleniumFlightUnitItem.isItemEnergized(unit) && unit.getItem() instanceof EleniumFlightUnitItem item) {
            // Water Stall check on Client (END phase)
            if (!item.isWaterproof() && player.isInWater()) {
                if (player.getAbilities().flying) {
                    player.getAbilities().flying = false;
                }
                player.getAbilities().mayfly = false;
                clientWasFlying = false;
                sprintKeyWasDown = false;
                return;
            }

            // Guarantee client LocalPlayer knows mayfly is enabled (allows instant double-tap space jump!)
            if (!player.getAbilities().mayfly) {
                player.getAbilities().mayfly = true;
            }

            if (player.getAbilities().flying) {
                if (!clientWasFlying) {
                    clientWasFlying = true;
                    // Client-side crisp anime takeoff audio cue
                    mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.TRIDENT_RIPTIDE_1, 1.30F, 0.35F));
                }

                // Ctrl Key Boost Trigger (Dash Surge)
                boolean sprintKeyDown = mc.options.keySprint.isDown();
                if (sprintKeyDown && !sprintKeyWasDown && clientBoostCooldown <= 0) {
                    if (!ClientFlightTelemetry.overheated) {
                        clientBoostCooldown = 12;
                        ModNetworking.sendToServer(new FlightBoostC2SPacket());
                        // Instant client-side sonic whip cue
                        mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.TRIDENT_RIPTIDE_3, 1.40F, 0.45F));
                    }
                }
                sprintKeyWasDown = sprintKeyDown;

                // Service Ceiling Dynamics (Active Flight only):
                // Thin air above ceiling reduces upward climb velocity and flight speed
                int ceiling = item.getServiceCeiling();
                if (!player.onGround() && player.getY() >= ceiling) {
                    Vec3 vel = player.getDeltaMovement();
                    if (vel.y > 0) {
                        player.setDeltaMovement(vel.x * 0.90, Math.min(vel.y * 0.20, 0.035), vel.z * 0.90);
                    }
                    player.getAbilities().setFlyingSpeed(item.getBaseFlightSpeed() * 0.40F);
                } else {
                    // Effective flight speed considering sprint and rain weather drag
                    float targetSpeed = item.getEffectiveFlightSpeed(player, player.isSprinting());
                    player.getAbilities().setFlyingSpeed(targetSpeed);
                }

                // High-speed turning inertia penalty (เวลาบินไว เลี้ยวยากขึ้น)
                Vec3 vel = player.getDeltaMovement();
                double speed = vel.length();
                if (speed > 0.40 && (player.isSprinting() || speed > 0.65)) {
                    Vec3 look = player.getLookAngle();
                    // Turn rate scales down at higher speeds (0.16 - 0.30)
                    double turnRate = Math.max(0.16, 0.45 - (speed - 0.40) * 0.30);
                    Vec3 targetVel = look.scale(speed);
                    vel = vel.lerp(targetVel, turnRate);
                    player.setDeltaMovement(vel);
                }

                // Transonic flight safety limiter: Prevents exceeding human survivability (~104 km/h / Mach 1.0)
                if (speed > 1.45) {
                    player.setDeltaMovement(vel.scale(1.45 / speed));
                }
            } else {
                clientWasFlying = false;
                sprintKeyWasDown = false;
            }
        } else {
            clientWasFlying = false;
            sprintKeyWasDown = false;
        }
    }
}
