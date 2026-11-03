package com.obsolete.compat;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;

import java.lang.reflect.Method;
import java.util.Comparator;

/**
 * Optional Titan Combat link: when a pilot hops out of the Exoframe with Shift right next to a Titan Combat
 * transport (helicopter, truck, ship...), the Exoframe is clamped onto that vehicle as cargo.
 * Reflection only, so Obsolete still runs without Titan Combat installed.
 */
public final class TitanCombatDock {
    private static final String VEHICLE_CLASS = "com.titancombat.entity.transport.BaseTransportVehicleEntity";
    public static final double RANGE = 8.0D;

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
        Entity vehicle = level.getEntitiesOfClass(Entity.class, exoframe.getBoundingBox().inflate(RANGE), vehicleClass::isInstance)
                .stream().min(Comparator.comparingDouble(v -> v.distanceToSqr(exoframe))).orElse(null);
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
