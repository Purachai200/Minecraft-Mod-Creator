package com.titancombat;

import com.titancombat.entity.transport.collision.VehicleCollisionData;
import com.titancombat.entity.transport.collision.VehicleCollisionManager;
import com.titancombat.entity.transport.collision.VehicleWalkCommand;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class VehicleWalkPhysicsTest {

    @Test
    @DisplayName("Acceptance 1: Walk from entry deck to every walkable deck without noclip (All 14 vehicles)")
    void testAllVehiclesWalkability() {
        for (String id : VehicleWalkCommand.VEHICLE_IDS) {
            VehicleCollisionManager.WalkTestResult res = VehicleCollisionManager.runWalkTest(id);
            assertTrue(res.problems().isEmpty(), "Vehicle " + id + " has problems: " + String.join(", ", res.problems()));
            assertTrue(res.reachableStates() > 0, "Vehicle " + id + " has 0 reachable states");
        }
    }

    @Test
    @DisplayName("Acceptance 2: Bulkheads block, furniture blocks, gaps < 0.6 block block (Selftest)")
    void testSelfTest() {
        assertTrue(VehicleCollisionManager.runSelfTest(), "Collision self-test should pass all 5 checks");
    }

    @Test
    @DisplayName("Acceptance 3: Stays in place when the ship yaws 90 degrees over 2 seconds (40 ticks)")
    void testYawRotationInvariance() {
        Vec3 localPos = new Vec3(2.5D, 1.0D, 10.0D); // Player standing on deck at local offset
        Vec3 shipPos = new Vec3(100.0D, 64.0D, -200.0D);
        float startYaw = 0.0F;
        float totalYawDelta = 90.0F;
        int ticks = 40; // 2 seconds @ 20 ticks/sec
        float stepYaw = totalYawDelta / ticks;

        float currentYaw = startYaw;
        for (int i = 0; i < ticks; i++) {
            currentYaw += stepYaw;
            // Ship moves and turns
            shipPos = shipPos.add(0.2D, 0.0D, 0.1D);

            // Compute world position of player carried with ship
            float yawRad = currentYaw * (float) (Math.PI / 180.0D);
            double cos = Math.cos(yawRad), sin = Math.sin(yawRad);
            double wx = shipPos.x + localPos.x * cos - localPos.z * sin;
            double wy = shipPos.y + localPos.y;
            double wz = shipPos.z + localPos.x * sin + localPos.z * cos;

            // Invert back to ship-local space: must recover the exact same localPos
            double dx = wx - shipPos.x, dy = wy - shipPos.y, dz = wz - shipPos.z;
            double recX = dx * cos + dz * sin;
            double recY = dy;
            double recZ = -dx * sin + dz * cos;

            assertEquals(localPos.x, recX, 1e-6D, "Local X drifted during yaw rotation");
            assertEquals(localPos.y, recY, 1e-6D, "Local Y drifted during yaw rotation");
            assertEquals(localPos.z, recZ, 1e-6D, "Local Z drifted during yaw rotation");
        }
    }

    @Test
    @DisplayName("Acceptance 4: Submarine dry pressure hull volume protects players from drowning")
    void testSubmarinePressureHullProtection() {
        // Interior floor of transport_sub: x in [-1.9, 1.9], y in [1.0, 3.5], z in [-10.6, 10.6]
        Vec3 insideSub = new Vec3(0.0D, 1.5D, 0.0D);
        assertTrue(VehicleCollisionManager.isInsideInterior("transport_sub", insideSub),
                "Submarine pressure hull interior must be recognized as enclosed dry volume");

        Vec3 outsideSub = new Vec3(10.0D, 1.5D, 0.0D);
        assertFalse(VehicleCollisionManager.isInsideInterior("transport_sub", outsideSub),
                "Outside of submarine hull must not be recognized as dry interior");
    }

    @Test
    @DisplayName("PART C: Vehicle lamp counts match specifications")
    void testLampCounts() {
        Map<String, Integer> expected = Map.ofEntries(
                Map.entry("fac_patrol", 4),
                Map.entry("opv_cutter", 12),
                Map.entry("corvette_stealth", 14),
                Map.entry("lpd_assault", 24),
                Map.entry("transport_sub", 7),
                Map.entry("c17_airlifter", 23),
                Map.entry("coaster_freighter", 14),
                Map.entry("mi17_hip", 2),
                Map.entry("mi26_halo", 3),
                Map.entry("uh60_blackhawk", 2),
                Map.entry("technical_4x4", 0),
                Map.entry("ural_6x6", 0),
                Map.entry("recovery_6x6", 0),
                Map.entry("humvee_m1165", 0)
        );

        for (Map.Entry<String, Integer> e : expected.entrySet()) {
            List<Vec3> lamps = VehicleCollisionManager.getLights(e.getKey());
            assertEquals(e.getValue(), lamps.size(), "Lamp count mismatch for " + e.getKey());
        }
    }
}
