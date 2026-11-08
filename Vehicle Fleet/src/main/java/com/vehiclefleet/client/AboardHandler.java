package com.vehiclefleet.client;

import com.vehiclefleet.entity.FleetVehicleEntity;
import com.vehiclefleet.physics.VehicleCollisionData;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;

/**
 * Walking on and inside moving vehicles (client side, once per tick after every entity has ticked).
 * Vanilla has already moved the player by its own input and gravity; we take that movement as a delta in the vehicle frame,
 * resolve it against the vehicle's collision boxes (floors, walls, stairs), and write the result back through the vehicle's
 * current pose, which also carries the player along with the hull. The server trusts the position; it only refills air and
 * cancels fall damage (FleetVehicleEntity.tickAboard).
 */
public final class AboardHandler {
    private static FleetVehicleEntity aboard;
    private static Vec3 prevLocal, prevWorld;

    private AboardHandler() {}

    public static void tick(Minecraft mc, LocalPlayer p) {
        if (p.isPassenger() || p.isSpectator() || p.getAbilities().flying || p.isSleeping()) { aboard = null; return; }
        if (aboard != null && (aboard.isRemoved() || aboard.level() != p.level())) aboard = null;
        if (aboard == null) { board(mc, p); return; }

        VehicleCollisionData col = aboard.collision();
        Vec3 dWorld = p.position().subtract(prevWorld);
        if (p.isInWater()) dWorld = new Vec3(dWorld.x * 1.25D, dWorld.y, dWorld.z * 1.25D);          // cancel vanilla water drag below a ship's waterline
        Vec3 dLocal = aboard.worldDeltaToLocal(dWorld);
        Vec3 now = col.resolveMove(prevLocal, dLocal, !aboard.isOpen());
        if (!aboard.inHull(now) || now.y < aboard.hull().minY - 1.5D) { aboard = null; return; }

        Vec3 w = aboard.toWorld(now);
        p.setPos(w.x, w.y, w.z);
        p.xo = p.xOld = prevWorld.x; p.yo = p.yOld = prevWorld.y; p.zo = p.zOld = prevWorld.z;
        Double top = col.standY(now.x, now.z, now.y);
        boolean grounded = top != null && Math.abs(top - now.y) < 0.03D;
        p.setOnGround(grounded);
        p.fallDistance = 0.0F;
        p.setSwimming(false);
        Vec3 dm = p.getDeltaMovement();
        if (grounded && dm.y < 0.0D) p.setDeltaMovement(dm.x, 0.0D, dm.z);
        prevLocal = now;
        prevWorld = w;
    }

    private static void board(Minecraft mc, LocalPlayer p) {
        for (Entity e : mc.level.entitiesForRendering()) {
            if (!(e instanceof FleetVehicleEntity v) || v.distanceToSqr(p) > 90000.0D) continue;
            Vec3 l = v.toLocal(p.position());
            if (!v.inHull(l)) continue;
            Double top = v.collision().standY(l.x, l.z, l.y);
            if (top == null || l.y - top > 0.1D || p.getDeltaMovement().y > 0.3D) continue;
            aboard = v;
            prevLocal = new Vec3(l.x, top, l.z);
            prevWorld = v.toWorld(prevLocal);
            return;
        }
    }
}
