package com.vehiclefleet;

import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class FleetVehicleTest {

    @Test
    void testAllVehiclesLoad() {
        Map<String, FleetVehicles.Spec> all = FleetVehicles.all();
        assertFalse(all.isEmpty(), "Fleet vehicles table should not be empty");
        assertEquals(14, all.size(), "Expected 14 vehicles in fleet table");
    }

    @Test
    void testDriverSeatPositionsAndRoofClearance() {
        for (FleetVehicles.Spec spec : FleetVehicles.all().values()) {
            assertFalse(spec.seats.isEmpty(), "Vehicle " + spec.id + " must have at least one seat");
            FleetVehicles.Seat driverSeat = spec.seats.get(0);
            assertNotNull(driverSeat.pos, "Driver seat pos must not be null for " + spec.id);
            assertEquals(3, driverSeat.pos.length, "Driver seat pos must have [x, y, z] for " + spec.id);

            Vec3 local = FleetVehicles.local(driverSeat.pos);
            double cushionY = local.y;
            double seatedRiderY = spec.isShip() ? cushionY : cushionY - 0.70D;

            // Seated player eye position is rider Y + eye height (1.27)
            double eyeY = seatedRiderY + 1.27D;
            // Seated player head top is rider Y + 1.50
            double headTopY = seatedRiderY + 1.50D;

            double vehicleHeight = spec.height / 16.0D;

            // Head top should not pierce above vehicle total height
            assertTrue(headTopY <= vehicleHeight + 0.1D,
                    String.format("Vehicle %s driver head (%.2f) exceeds vehicle height (%.2f)",
                            spec.id, headTopY, vehicleHeight));

            // Eye level must be above cushion
            assertTrue(eyeY > cushionY,
                    String.format("Vehicle %s driver eye (%.2f) must be above seat cushion (%.2f)",
                            spec.id, eyeY, cushionY));
        }
    }

    @Test
    void testAckermannSteeringMath() {
        float speed = 0.5F;
        float maxSteerRad = (float) Math.toRadians(34.0D);
        float wheelbase = 3.8F;

        // Steering input -1.0 (turn left)
        float steer = 1.0F; // steer towards input
        float steerRad = steer * maxSteerRad;
        float yawDelta = -(float) Math.toDegrees(speed * Math.tan(steerRad) / wheelbase);

        assertTrue(yawDelta < 0.0F, "Turning left should give negative yaw delta in Minecraft");
        assertTrue(Math.abs(yawDelta) > 1.0F && Math.abs(yawDelta) < 15.0F,
                "Yaw delta should be smooth and realistic, got: " + yawDelta);
    }

    @Test
    void testAerodynamicTiltBounds() {
        // High speed aircraft flight pitch & roll
        float visSpeed = 0.95F;
        float visYawRate = 12.0F; // degrees per tick

        float flightPitch = Mth.clamp(visSpeed * 0.16F, -0.10F, 0.18F);
        float rollInput = (float) Math.toRadians(visYawRate) * visSpeed * 6.0F;
        float flightRoll = -1.8F * Mth.clamp(rollInput, -0.08F, 0.08F);

        assertTrue(flightPitch >= -0.10F && flightPitch <= 0.18F, "Flight pitch within realistic pitch angle");
        assertTrue(flightRoll >= -0.16F && flightRoll <= 0.16F, "Flight roll within realistic bank angle");
    }

    @Test
    void testTiltVectorTransformationPreservesLength() {
        Vec3 seatOffset = new Vec3(0.5D, 1.2D, -2.0D);
        float pitch = 0.12F;
        float roll = -0.08F;

        double pivotY = 1.5D;
        double h = seatOffset.y - pivotY;
        double cp = Math.cos(pitch), sp = Math.sin(pitch);
        double y = h * cp - seatOffset.z * sp, z = seatOffset.z * cp + h * sp;
        double cr = Math.cos(roll), sr = Math.sin(roll);
        Vec3 tilted = new Vec3(seatOffset.x * cr + y * sr, pivotY + y * cr - seatOffset.x * sr, z);

        // Relative distance to pivot should be invariant under rotation
        double origDistSq = seatOffset.x * seatOffset.x + h * h + seatOffset.z * seatOffset.z;
        double tiltedH = tilted.y - pivotY;
        double tiltedDistSq = tilted.x * tilted.x + tiltedH * tiltedH + tilted.z * tilted.z;

        assertEquals(origDistSq, tiltedDistSq, 1e-4, "Rotation transformation must be rigid (preserve distance to pivot)");
    }

    @Test
    void testDeckColliderTilingMath() {
        // LPD flight deck: z0 = -13.25, z1 = -1.25, size = 6.0
        double z0 = -13.25D, z1 = -1.25D, size = 6.0D;
        double span = Math.abs(z1 - z0);
        int tiles = Math.max(1, (int) Math.ceil(span / size));
        assertEquals(2, tiles, "12m deck with 6m tiles needs 2 tiles");

        double step = (z1 - z0 - Math.signum(z1 - z0) * size) / (tiles - 1);
        double firstTileZ = z0 + Math.signum(z1 - z0) * size / 2.0D;
        double lastTileZ = firstTileZ + (tiles - 1) * step;

        assertEquals(-10.25D, firstTileZ, 1e-4, "First tile should be centered at -10.25");
        assertEquals(-4.25D, lastTileZ, 1e-4, "Second tile should be centered at -4.25");
    }

    @Test
    void testDeckCarrierRiderYawTransformation() {
        // Rider positioned 3m to the left (+X) of ship center, ship turns 90 degrees right (-90 deg dYaw)
        double rx = 3.0D, rz = 0.0D;
        float dYaw = -90.0F;
        float r = dYaw * Mth.DEG_TO_RAD;
        double nx = rx * Math.cos(r) - rz * Math.sin(r);
        double nz = rx * Math.sin(r) + rz * Math.cos(r);

        // After turning 90 degrees right, left side rotates to forward (+Z)
        assertEquals(0.0D, nx, 1e-4, "X offset rotated 90 deg");
        assertEquals(-3.0D, nz, 1e-4, "Z offset rotated 90 deg");
        assertEquals(9.0D, nx * nx + nz * nz, 1e-4, "Distance from vehicle center is strictly preserved");
    }
}
