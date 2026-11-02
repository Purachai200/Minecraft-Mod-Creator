package com.titancombat.client;

import com.mojang.blaze3d.platform.InputConstants;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.network.MechControlC2SPacket;
import com.titancombat.network.MechEjectC2SPacket;
import com.titancombat.network.ModNetworking;
import com.titancombat.network.TitanWeaponActionC2SPacket;
import com.titancombat.network.TitanFireC2SPacket;
import net.minecraft.client.CameraType;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.event.TickEvent;
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

    public static final KeyMapping KEY_RELOAD = new KeyMapping(
            "key.titancombat.reload",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_R,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_HOLSTER = new KeyMapping(
            "key.titancombat.holster",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_H,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_SALUTE = new KeyMapping(
            "key.titancombat.salute",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_J,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_RANGE_UP = new KeyMapping(
            "key.titancombat.range_up",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_UP,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_RANGE_DOWN = new KeyMapping(
            "key.titancombat.range_down",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_DOWN,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_RELEASE_CARGO = new KeyMapping(
            "key.titancombat.release_cargo",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_B,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_DESCEND = new KeyMapping(
            "key.titancombat.descend",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_LEFT_ALT,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_MARK_TARGET = new KeyMapping(
            "key.titancombat.mark_target",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_N,
            KEY_CATEGORY_TITAN
    );

    // The howitzer is a back skill module (the titan keeps its hand weapon), so it has its own keys.
    public static final KeyMapping KEY_TACTICAL_MAP = new KeyMapping(
            "key.titancombat.tactical_map",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_K,
            KEY_CATEGORY_TITAN
    );

    public static final KeyMapping KEY_FIRE_HOWITZER = new KeyMapping(
            "key.titancombat.fire_howitzer",
            InputConstants.Type.KEYSYM,
            GLFW.GLFW_KEY_L,
            KEY_CATEGORY_TITAN
    );

    private static final long KNEEL_DEBOUNCE_MS = 1500L; // stand-up / kneel clip length
    private static long lastKneelPressMs = 0L;
    private static long lastEjectPressMs = 0L;

    @SubscribeEvent
    public static void onKeyInput(InputEvent.Key event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || !(mc.player.getVehicle() instanceof BaseMechEntity)) {
            return;
        }

        // 1. Instant Rocket Dash on Spacebar tap (when not using continuous flight equipment)
        if (mc.options.keyJump.consumeClick()) {
            boolean hasFlight = mc.player.getVehicle() instanceof BaseTitanEntity titan && titan.hasFlightModule();
            if (!hasFlight) {
                float forward = mc.player.zza;
                float strafe = mc.player.xxa;
                // Space alone fires the jump jets; Space + a direction dashes that way.
                ModNetworking.sendToServer(new MechControlC2SPacket(forward, strafe, true, false, false, false, false, false));
            }
        }

        // 2. Toggle Kneel / Park Mode (debounced: holding Z must not toggle repeatedly)
        if (KEY_KNEEL.consumeClick()) {
            while (KEY_KNEEL.consumeClick()) { /* drop key-repeat clicks */ }
            long now = System.currentTimeMillis();
            if (now - lastKneelPressMs >= KNEEL_DEBOUNCE_MS && event.getAction() != GLFW.GLFW_REPEAT) {
                lastKneelPressMs = now;
                ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, false, false, false, false, true));
            }
        }

        // 3. Dismount Lock Alert: If player taps Shift while Titan is standing
        if (event.getAction() == GLFW.GLFW_PRESS && mc.options.keyShift.matches(event.getKey(), event.getScanCode())) {
            if (mc.player.getVehicle() instanceof BaseTitanEntity titan && !titan.isSitting()) {
                mc.player.displayClientMessage(Component.translatable("message.titancombat.must_kneel_first"), true);
                mc.player.playSound(SoundEvents.NOTE_BLOCK_BASS.get(), 1.0F, 0.6F);
            }
        }

        if (KEY_RELOAD.consumeClick()) {
            ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELOAD));
        }

        while (KEY_RANGE_UP.consumeClick()) {
            ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RANGE_UP));
        }
        while (KEY_RANGE_DOWN.consumeClick()) {
            ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RANGE_DOWN));
        }

        if (KEY_HOLSTER.consumeClick()) {
            ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.TOGGLE_LOWERED));
        }

        if (KEY_EJECT.consumeClick()) {
            // Eject destroys the titan: outside a critical state it needs a second press to confirm.
            boolean critical = mc.player.getVehicle() instanceof BaseMechEntity mech
                    && (mech.getMechState() == com.titancombat.entity.MechState.DOOMED || mech.getHealth() <= mech.getMaxHealth() * 0.2F);
            long now = System.currentTimeMillis();
            if (critical || now - lastEjectPressMs < 1500L) {
                lastEjectPressMs = 0L;
                ModNetworking.sendToServer(new MechEjectC2SPacket());
            } else {
                lastEjectPressMs = now;
                mc.player.displayClientMessage(Component.translatable("message.titancombat.eject_confirm",
                        KEY_EJECT.getKey().getDisplayName()), true);
                mc.player.playSound(SoundEvents.NOTE_BLOCK_PLING.get(), 1.0F, 0.5F);
            }
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

        if (KEY_SALUTE.consumeClick()) {
            ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.SALUTE));
        }

    }

    private static boolean lastFlightThrust = false;

    /** Held triggers fire continuously (the server gates the actual rate of fire per weapon). */
    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        boolean piloting = mc.player != null && mc.player.getVehicle() instanceof BaseMechEntity;
        BaseTitanEntity.clientSprintHeld = piloting && mc.options.keySprint.isDown();
        BaseTitanEntity.clientJumpHeld = piloting && mc.options.keyJump.isDown();

        boolean flightThrust = piloting && mc.player.getVehicle() instanceof BaseTitanEntity titan
                && titan.hasFlightModule() && mc.options.keyJump.isDown();
        if (flightThrust != lastFlightThrust) {
            lastFlightThrust = flightThrust;
            ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(
                    flightThrust ? TitanWeaponActionC2SPacket.FLIGHT_START : TitanWeaponActionC2SPacket.FLIGHT_STOP));
        }

        com.titancombat.entity.transport.TitanSkyCraneDroneEntity.clientDescendHeld = KEY_DESCEND.isDown();

        // Transport drivers: release / hot-drop the carried titan.
        if (mc.player != null && mc.player.getVehicle() instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity) {
            while (KEY_RELEASE_CARGO.consumeClick()) {
                ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELEASE_CARGO));
            }
        }

        // Open Titan Customization / Cockpit Bay via 'E' (keyInventory) when looking at a Titan or Riding
        if (mc.player != null && mc.screen == null && mc.options.keyInventory.consumeClick()) {
            if (mc.player.isPassenger() && mc.player.getVehicle() instanceof BaseTitanEntity) {
                mc.player.sendOpenInventory();
            } else if (mc.hitResult instanceof net.minecraft.world.phys.EntityHitResult eHit
                    && eHit.getEntity() instanceof BaseTitanEntity targetTitan
                    && mc.player.distanceToSqr(targetTitan) <= 49.0D) {
                ModNetworking.sendToServer(new com.titancombat.network.OpenTitanInventoryC2SPacket(targetTitan.getId()));
            } else {
                mc.setScreen(new net.minecraft.client.gui.screens.inventory.InventoryScreen(mc.player));
            }
        }

        if (!piloting || mc.screen != null) return;

        // Back weapon fire control (Howitzer / Rocket Launcher Pod)
        if (mc.player.getVehicle() instanceof BaseTitanEntity t && (t.hasHowitzer() || t.hasRocketPod())) {
            if (t.hasHowitzer()) {
                while (KEY_MARK_TARGET.consumeClick()) {
                    net.minecraft.world.phys.Vec3 p = crosshairTarget(mc, 320.0D);
                    ModNetworking.sendToServer(new com.titancombat.network.ArtilleryTargetC2SPacket(
                            net.minecraft.util.Mth.floor(p.x), true, net.minecraft.util.Mth.floor(p.y), net.minecraft.util.Mth.floor(p.z)));
                }
            }
            while (KEY_FIRE_HOWITZER.consumeClick()) {
                ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.FIRE_HOWITZER));
            }
            if (t.hasHowitzer() && KEY_TACTICAL_MAP.consumeClick()) {
                mc.setScreen(new com.titancombat.client.gui.ArtilleryMapScreen(t));
                return;
            }
        }
        net.minecraft.core.BlockPos target = mc.player.getVehicle() instanceof BaseTitanEntity t2
                && t2.hasHowitzer() ? t2.getArtilleryTarget() : null;
        if (target != null && mc.level.getGameTime() % 3 == 0) {
            net.minecraft.world.phys.Vec3 hit = net.minecraft.world.phys.Vec3.atBottomCenterOf(target).add(0.0D, 1.0D, 0.0D);
            for (int i = 0; i < 8; i++) {
                double a = i * Math.PI / 4;
                mc.level.addParticle(net.minecraft.core.particles.ParticleTypes.END_ROD,
                        hit.x + Math.cos(a) * 3.0D, hit.y + 0.2D, hit.z + Math.sin(a) * 3.0D, 0, 0.02D, 0);
            }
            mc.level.addParticle(net.minecraft.core.particles.ParticleTypes.FLAME, hit.x, hit.y + 0.3D, hit.z, 0, 0.05D, 0);
        }

        if (mc.options.keyAttack.isDown() || KEY_FIRE.isDown()) {
            ModNetworking.sendToServer(new TitanFireC2SPacket(crosshairTarget(mc)));
        }
    }

    /**
     * World point under the crosshair, ray-cast from the actual camera look vector (so third person
     * and recoiling/shaking cameras aim exactly where the reticle is, not where the pilot's entity eyes point).
     */
    private static net.minecraft.world.phys.Vec3 crosshairTarget(Minecraft mc) {
        return crosshairTarget(mc, 160.0D);
    }

    private static net.minecraft.world.phys.Vec3 crosshairTarget(Minecraft mc, double range) {
        org.joml.Vector3f look = mc.gameRenderer.getMainCamera().getLookVector();
        net.minecraft.world.phys.Vec3 dir = new net.minecraft.world.phys.Vec3(look.x(), look.y(), look.z());
        net.minecraft.world.phys.Vec3 cam = mc.gameRenderer.getMainCamera().getPosition();
        net.minecraft.world.entity.Entity titan = mc.player.getVehicle();
        net.minecraft.world.phys.Vec3 from = cam;
        if (mc.options.getCameraType() != CameraType.FIRST_PERSON && titan != null) {
            double distToTitan = titan.position().subtract(cam).dot(dir);
            from = cam.add(dir.scale(Math.max(0.0D, distToTitan + 3.0D)));
        }
        net.minecraft.world.phys.Vec3 to = from.add(dir.scale(range));
        net.minecraft.world.phys.BlockHitResult block = mc.level.clip(new net.minecraft.world.level.ClipContext(from, to,
                net.minecraft.world.level.ClipContext.Block.COLLIDER, net.minecraft.world.level.ClipContext.Fluid.NONE, mc.player));
        if (block.getType() != net.minecraft.world.phys.HitResult.Type.MISS) to = block.getLocation();
        net.minecraft.world.phys.EntityHitResult hit = net.minecraft.world.entity.projectile.ProjectileUtil.getEntityHitResult(
                mc.player, from, to, new net.minecraft.world.phys.AABB(from, to).inflate(1.0D),
                e -> e != titan && e != mc.player && e.isPickable() && !e.isSpectator(), from.distanceToSqr(to));
        return hit != null ? hit.getLocation() : to;
    }

    @SubscribeEvent
    public static void onInteraction(InputEvent.InteractionKeyMappingTriggered event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return;

        if (mc.player.getVehicle() instanceof BaseMechEntity) {
            // Left click naturally fires the heavy titan weapon when in cockpit!
            if (event.isAttack()) {
                // Firing is handled every tick in onClientTick while the button is held.
                event.setCanceled(true);
                event.setSwingHand(false);
            }
        } else if (mc.player.getVehicle() instanceof com.titancombat.entity.transport.TitanSkyCraneDroneEntity) {
            if (event.isAttack()) {
                // Left click performs Combat Hot-Drop from the Sky-Crane Drone
                event.setCanceled(true);
                event.setSwingHand(false);
                ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, true));
            }
        }
    }

    @SubscribeEvent
    public static void onRenderGuiOverlayPre(RenderGuiOverlayEvent.Pre event) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player != null && (mc.player.getVehicle() instanceof BaseMechEntity || mc.player.getVehicle() instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity)) {
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
        event.register(KEY_RELOAD);
        event.register(KEY_HOLSTER);
        event.register(KEY_SALUTE);
        event.register(KEY_RANGE_UP);
        event.register(KEY_RANGE_DOWN);
        event.register(KEY_RELEASE_CARGO);
        event.register(KEY_DESCEND);
        event.register(KEY_MARK_TARGET);
        event.register(KEY_TACTICAL_MAP);
        event.register(KEY_FIRE_HOWITZER);
    }
}
