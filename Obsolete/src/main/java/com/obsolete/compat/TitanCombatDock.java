package com.obsolete.compat;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;

import java.lang.reflect.Method;
import java.util.Comparator;

/**
 * Optional Titan Combat link: when a pilot hops out of the Exoframe with Shift while looking at a Titan Combat
 * transport (helicopter, truck, ship...) within 4 blocks of its hull, the Exoframe is clamped onto it as cargo.
 * Reflection only, so Obsolete still runs without Titan Combat installed.
 */
public final class TitanCombatDock {
    private static final String VEHICLE_CLASS = "com.titancombat.entity.transport.BaseTransportVehicleEntity";
    /** How far the pilot may look to pick a vehicle, and how close the Exoframe must stand to its hull. */
    public static final double LOOK_RANGE = 12.0D;
    public static final double HULL_RANGE = 4.0D;

    private static boolean checked;
    private static Class<?> vehicleClass;
    private static Method canMountCargo, lockCargoToDeck;

    private TitanCombatDock() {}

    private static boolean init() {
        if (!checked) {
            checked = true;
            try {
                vehicleClass = Class.forName(VEHICLE_CLASS);
                canMountCargo = vehicleClass.getMethod("canMountCargo", Entity.class);
                lockCargoToDeck = vehicleClass.getMethod("lockCargoToDeck", Entity.class, Player.class);
            } catch (Throwable ignored) {
                vehicleClass = null; // Titan Combat not installed
            }
        }
        return vehicleClass != null;
    }

    /** Called server-side as the pilot leaves; returns true if a vehicle took the Exoframe. */
    public static boolean tryDock(Entity exoframe, Player pilot) {
        if (!init() || exoframe.isPassenger() || !(exoframe.level() instanceof ServerLevel level)) return false;
        // Holding anything (e.g. the Vehicle Wrench to pack the vehicle up) means Shift is for that item, not for docking
        if (!pilot.getMainHandItem().isEmpty()) return false;
        // Only dock when the pilot is deliberately looking at a vehicle right beside them; a plain Shift-out next to
        // a parked truck must not grab the Exoframe.
        net.minecraft.world.phys.Vec3 eye = pilot.getEyePosition();
        net.minecraft.world.phys.Vec3 end = eye.add(pilot.getViewVector(1.0F).scale(LOOK_RANGE));
        Entity vehicle = level.getEntitiesOfClass(Entity.class, exoframe.getBoundingBox().inflate(LOOK_RANGE), vehicleClass::isInstance).stream()
                .filter(v -> v.getBoundingBox().inflate(0.5D).clip(eye, end).isPresent())
                .filter(v -> v.getBoundingBox().inflate(HULL_RANGE).intersects(exoframe.getBoundingBox()))
                .min(Comparator.comparingDouble(v -> v.distanceToSqr(exoframe))).orElse(null);
        if (vehicle == null) return false;
        try {
            if (!(boolean) canMountCargo.invoke(vehicle, exoframe)) {
                pilot.displayClientMessage(Component.literal("§c[Exoframe] Transport cargo bay is full."), true);
                return false;
            }
            // Defer one tick: we're inside the pilot's dismount, so don't start a new ride mid-way
            level.getServer().execute(() -> {
                try {
                    lockCargoToDeck.invoke(vehicle, exoframe, pilot);
                } catch (Throwable ignored) {}
            });
            return true;
        } catch (Throwable e) {
            return false;
        }
    }
}
