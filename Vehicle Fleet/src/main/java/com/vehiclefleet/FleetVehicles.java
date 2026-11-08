package com.vehiclefleet;

import com.google.gson.Gson;
import net.minecraft.world.phys.Vec3;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Vehicle table written by scripts/gen_fleet.py (data/vehiclefleet/vehicles.json). Positions are model px: +X left, +Y up, nose -Z. */
public final class FleetVehicles {
    public static final class Seat { public String name; public double[] pos; }
    public static final class Cargo { public String name; public double[] pos; public String type; }
    public static final class Clips { public String idle, move, open, sling, beacon, radar; }
    public static final class Spec {
        public String id, name, kind, payload;
        public int tier, seat_capacity;
        public List<Seat> seats = new ArrayList<>();
        public List<Cargo> cargo = new ArrayList<>();
        public double half_width, height, draft, speed;
        public double[] length = new double[2];
        public int[] rgb = new int[3];
        public Clips clips = new Clips();

        public boolean isAir() { return "air".equals(kind); }
        public boolean isGround() { return "ground".equals(kind); }
        public boolean isShip() { return "ship".equals(kind); }
    }

    private static final Map<String, Spec> BY_ID = new LinkedHashMap<>();

    private FleetVehicles() {}

    public static synchronized Map<String, Spec> all() {
        if (BY_ID.isEmpty()) {
            try (InputStream in = FleetVehicles.class.getResourceAsStream("/data/vehiclefleet/vehicles.json")) {
                Spec[] specs = new Gson().fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), Spec[].class);
                for (Spec s : specs) BY_ID.put(s.id, s);
            } catch (Exception e) {
                throw new IllegalStateException("vehicles.json missing or invalid", e);
            }
        }
        return BY_ID;
    }

    public static Spec get(String id) { return all().get(id); }

    /** Model px -> vehicle-local blocks (+X left, +Z toward the nose). */
    public static Vec3 local(double[] px) { return new Vec3(px[0] / 16.0D, px[1] / 16.0D, -px[2] / 16.0D); }
}
