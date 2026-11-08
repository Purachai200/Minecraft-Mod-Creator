package com.vehiclefleet.physics;

import com.google.gson.*;
import com.vehiclefleet.VehicleFleetMod;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Loads data/vehiclefleet/vehicle_collision/<id>.json and vehicle_lights/<id>.json (model px, +X left, nose -Z) into vehicle-local blocks (nose +Z). */
public final class Collisions {
    private static final Gson GSON = new Gson();
    private static final Map<String, VehicleCollisionData> COLLISION = new HashMap<>();
    private static final Map<String, List<Vec3>> LIGHTS = new HashMap<>();

    private Collisions() {}

    public static synchronized VehicleCollisionData get(String id) {
        return COLLISION.computeIfAbsent(id, Collisions::loadCollision);
    }

    public static synchronized List<Vec3> lights(String id) {
        return LIGHTS.computeIfAbsent(id, Collisions::loadLights);
    }

    public static AABB box(double x0, double y0, double z0, double x1, double y1, double z1) {
        return new AABB(x0 / 16.0D, y0 / 16.0D, -z1 / 16.0D, x1 / 16.0D, y1 / 16.0D, -z0 / 16.0D);
    }

    private static JsonObject read(String path) {
        try (InputStream in = Collisions.class.getResourceAsStream(path)) {
            if (in == null) return null;
            return GSON.fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
        } catch (Exception e) {
            VehicleFleetMod.LOGGER.error("Could not read {}", path, e);
            return null;
        }
    }

    private static List<AABB> boxes(JsonArray arr) {
        List<AABB> out = new ArrayList<>();
        for (JsonElement el : arr) {
            JsonArray b = el.getAsJsonArray();
            out.add(box(b.get(0).getAsDouble(), b.get(1).getAsDouble(), b.get(2).getAsDouble(), b.get(3).getAsDouble(), b.get(4).getAsDouble(), b.get(5).getAsDouble()));
        }
        return out;
    }

    private static VehicleCollisionData loadCollision(String id) {
        JsonObject root = read("/data/vehiclefleet/vehicle_collision/" + id + ".json");
        if (root == null) return new VehicleCollisionData(new ArrayList<>(), new HashMap<>());
        Map<String, List<AABB>> dyn = new HashMap<>();
        if (root.has("dynamic")) for (Map.Entry<String, JsonElement> e : root.getAsJsonObject("dynamic").entrySet()) dyn.put(e.getKey(), boxes(e.getValue().getAsJsonArray()));
        return new VehicleCollisionData(boxes(root.getAsJsonArray("static")), dyn);
    }

    private static List<Vec3> loadLights(String id) {
        JsonObject root = read("/data/vehiclefleet/vehicle_lights/" + id + ".json");
        List<Vec3> out = new ArrayList<>();
        if (root != null && root.has("lamps")) for (JsonElement el : root.getAsJsonArray("lamps")) {
            JsonArray a = el.getAsJsonArray();
            out.add(new Vec3(a.get(0).getAsDouble() / 16.0D, a.get(1).getAsDouble() / 16.0D, -a.get(2).getAsDouble() / 16.0D));
        }
        return out;
    }
}
