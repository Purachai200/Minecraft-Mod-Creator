package com.titancombat.entity.transport.collision;

import com.google.gson.*;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class VehicleCollisionManager {
    private static final Gson GSON = new Gson();
    private static final Map<String, VehicleCollisionData> COLLISION_CACHE = new HashMap<>();
    private static final Map<String, List<Vec3>> LIGHTS_CACHE = new HashMap<>();
    private static final Map<String, Map<String, AABB>> DECKS_CACHE = new HashMap<>();

    public static synchronized VehicleCollisionData getCollision(String vehicleId) {
        if (COLLISION_CACHE.containsKey(vehicleId)) return COLLISION_CACHE.get(vehicleId);
        VehicleCollisionData data = loadCollision(vehicleId);
        COLLISION_CACHE.put(vehicleId, data);
        return data;
    }

    public static synchronized List<Vec3> getLights(String vehicleId) {
        if (LIGHTS_CACHE.containsKey(vehicleId)) return LIGHTS_CACHE.get(vehicleId);
        List<Vec3> lights = loadLights(vehicleId);
        LIGHTS_CACHE.put(vehicleId, lights);
        return lights;
    }

    public static synchronized Map<String, AABB> getDecks(String vehicleId) {
        ensureDecksLoaded();
        return DECKS_CACHE.getOrDefault(vehicleId, Collections.emptyMap());
    }

    private static synchronized void ensureDecksLoaded() {
        if (!DECKS_CACHE.isEmpty()) return;
        try (InputStream in = VehicleCollisionManager.class.getResourceAsStream("/data/titancombat/vehicle_collision/decks.json")) {
            if (in == null) return;
            JsonObject obj = GSON.fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
            for (Map.Entry<String, JsonElement> e : obj.entrySet()) {
                String vid = e.getKey().replace("`", "").trim();
                Map<String, AABB> map = new HashMap<>();
                JsonObject decksObj = e.getValue().getAsJsonObject();
                for (Map.Entry<String, JsonElement> d : decksObj.entrySet()) {
                    String dName = d.getKey().replace("`", "").trim();
                    JsonArray arr = d.getValue().getAsJsonArray();
                    JsonArray a = arr.get(0).getAsJsonArray();
                    JsonArray b = arr.get(1).getAsJsonArray();
                    double ax = a.get(0).getAsDouble() / 16.0D, ay = a.get(1).getAsDouble() / 16.0D, az = a.get(2).getAsDouble() / 16.0D;
                    double bx = b.get(0).getAsDouble() / 16.0D, by = b.get(1).getAsDouble() / 16.0D, bz = b.get(2).getAsDouble() / 16.0D;
                    double minX = Math.min(ax, bx), maxX = Math.max(ax, bx);
                    double minY = Math.min(ay, by), maxY = Math.max(ay, by);
                    double minZ = Math.min(-az, -bz), maxZ = Math.max(-az, -bz);
                    map.put(dName, new AABB(minX, minY, minZ, maxX, maxY, maxZ));
                }
                DECKS_CACHE.put(vid, map);
            }
        } catch (Exception ex) {
            // shortcut: fallback if file not found
        }
    }

    public static boolean isInsideInterior(String vehicleId, Vec3 localPos) {
        Map<String, AABB> decks = getDecks(vehicleId);
        for (Map.Entry<String, AABB> entry : decks.entrySet()) {
            String name = entry.getKey().toLowerCase(Locale.ROOT);
            if (name.contains("lower_deck") || name.contains("tier") || name.contains("bridge")
                    || name.contains("hangar") || name.contains("cabin") || name.contains("interior")
                    || name.contains("crew") || name.contains("pilothouse")) {
                AABB b = entry.getValue();
                if (localPos.x >= b.minX - 0.2D && localPos.x <= b.maxX + 0.2D
                        && localPos.z >= b.minZ - 0.2D && localPos.z <= b.maxZ + 0.2D
                        && localPos.y >= b.minY - 0.2D && localPos.y <= b.minY + 2.5D) {
                    return true;
                }
            }
        }
        return false;
    }

    private static VehicleCollisionData loadCollision(String vehicleId) {
        String path = "/data/titancombat/vehicle_collision/" + vehicleId + ".json";
        try (InputStream in = VehicleCollisionManager.class.getResourceAsStream(path)) {
            if (in == null) return new VehicleCollisionData(Collections.emptyList(), Collections.emptyMap());
            JsonObject root = GSON.fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
            List<AABB> staticList = new ArrayList<>();
            if (root.has("static")) {
                for (JsonElement el : root.getAsJsonArray("static")) {
                    JsonArray b = el.getAsJsonArray();
                    staticList.add(boxFromPx(b.get(0).getAsDouble(), b.get(1).getAsDouble(), b.get(2).getAsDouble(),
                            b.get(3).getAsDouble(), b.get(4).getAsDouble(), b.get(5).getAsDouble()));
                }
            }
            Map<String, List<AABB>> dynMap = new HashMap<>();
            if (root.has("dynamic")) {
                JsonObject dynObj = root.getAsJsonObject("dynamic");
                for (Map.Entry<String, JsonElement> e : dynObj.entrySet()) {
                    List<AABB> dBoxes = new ArrayList<>();
                    for (JsonElement el : e.getValue().getAsJsonArray()) {
                        JsonArray b = el.getAsJsonArray();
                        dBoxes.add(boxFromPx(b.get(0).getAsDouble(), b.get(1).getAsDouble(), b.get(2).getAsDouble(),
                            b.get(3).getAsDouble(), b.get(4).getAsDouble(), b.get(5).getAsDouble()));
                    }
                    dynMap.put(e.getKey(), dBoxes);
                }
            }
            return new VehicleCollisionData(staticList, dynMap);
        } catch (Exception e) {
            return new VehicleCollisionData(Collections.emptyList(), Collections.emptyMap());
        }
    }

    private static List<Vec3> loadLights(String vehicleId) {
        String path = "/data/titancombat/vehicle_lights/" + vehicleId + ".json";
        try (InputStream in = VehicleCollisionManager.class.getResourceAsStream(path)) {
            if (in == null) return Collections.emptyList();
            JsonObject root = GSON.fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
            List<Vec3> lamps = new ArrayList<>();
            if (root.has("lamps")) {
                for (JsonElement el : root.getAsJsonArray("lamps")) {
                    JsonArray a = el.getAsJsonArray();
                    lamps.add(new Vec3(a.get(0).getAsDouble() / 16.0D, a.get(1).getAsDouble() / 16.0D, -a.get(2).getAsDouble() / 16.0D));
                }
            }
            return lamps;
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private static AABB boxFromPx(double x0, double y0, double z0, double x1, double y1, double z1) {
        return new AABB(x0 / 16.0D, y0 / 16.0D, -z1 / 16.0D, x1 / 16.0D, y1 / 16.0D, -z0 / 16.0D);
    }

    public static boolean runSelfTest() {
        AABB floor = boxFromPx(-100, -5, -100, 100, 0, 100);
        AABB wall = boxFromPx(-100, 0, 10, 100, 40, 12);
        VehicleCollisionData sWall = new VehicleCollisionData(List.of(floor, wall), Collections.emptyMap());
        Map<String, Vec3> rWall = sWall.reach(new Vec3(0, 0, 0), 3.0D / 16.0D, 400000);
        if (rWall.values().stream().anyMatch(v -> -v.z * 16.0D > 20.0D)) {
            throw new AssertionError("wall did not block");
        }

        AABB riser12 = boxFromPx(-100, 0, 10, 100, 12, 100);
        VehicleCollisionData sRiser = new VehicleCollisionData(List.of(floor, riser12), Collections.emptyMap());
        Map<String, Vec3> rRiser = sRiser.reach(new Vec3(0, 0, 0), 3.0D / 16.0D, 400000);
        if (rRiser.values().stream().anyMatch(v -> -v.z * 16.0D > 20.0D)) {
            throw new AssertionError("12 px riser should block");
        }

        List<AABB> stairs = new ArrayList<>();
        stairs.add(floor);
        for (int i = 0; i < 6; i++) {
            stairs.add(boxFromPx(-100, 0, 10 + 6 * i, 100, 4.5D * (i + 1), 16 + 6 * i));
        }
        VehicleCollisionData sStairs = new VehicleCollisionData(stairs, Collections.emptyMap());
        Map<String, Vec3> rStairs = sStairs.reach(new Vec3(0, 0, 0), 3.0D / 16.0D, 400000);
        if (rStairs.values().stream().noneMatch(v -> v.y * 16.0D >= 27.0D)) {
            throw new AssertionError("4.5 px risers should be climbable");
        }

        AABB d1 = boxFromPx(-100, 0, 10, -7, 40, 12);
        AABB d2 = boxFromPx(7, 0, 10, 100, 40, 12);
        VehicleCollisionData sDoor = new VehicleCollisionData(List.of(floor, d1, d2), Collections.emptyMap());
        Map<String, Vec3> rDoor = sDoor.reach(new Vec3(0, 0, 0), 3.0D / 16.0D, 400000);
        if (rDoor.values().stream().noneMatch(v -> -v.z * 16.0D > 20.0D)) {
            throw new AssertionError("14 px door should pass the player");
        }

        AABB n1 = boxFromPx(-100, 0, 10, -4, 40, 12);
        AABB n2 = boxFromPx(4, 0, 10, 100, 40, 12);
        VehicleCollisionData sNarrow = new VehicleCollisionData(List.of(floor, n1, n2), Collections.emptyMap());
        Map<String, Vec3> rNarrow = sNarrow.reach(new Vec3(0, 0, 0), 3.0D / 16.0D, 400000);
        if (rNarrow.values().stream().anyMatch(v -> -v.z * 16.0D > 20.0D)) {
            throw new AssertionError("8 px gap must not pass a 9.6 px player");
        }

        return true;
    }

    public static WalkTestResult runWalkTest(String vehicleId) {
        VehicleCollisionData col = getCollision(vehicleId);
        Map<String, AABB> decks = getDecks(vehicleId);
        if (col.getStaticBoxes().isEmpty() || decks.isEmpty()) {
            return new WalkTestResult(vehicleId, null, 0, Collections.emptyMap(), List.of("collision or deck data missing"));
        }

        Vec3 start = null;
        for (AABB deck : decks.values()) {
            double xStep = 4.0D / 16.0D, zStep = 4.0D / 16.0D;
            double marginX = 6.0D / 16.0D, marginZ = 6.0D / 16.0D;
            double x0 = deck.minX + marginX, x1 = deck.maxX - marginX;
            double z0 = deck.minZ + marginZ, z1 = deck.maxZ - marginZ;
            List<Double> xs = new ArrayList<>();
            if (x0 <= x1) {
                for (double x = x0; x <= x1 + 1e-5; x += xStep) xs.add(x);
            } else {
                xs.add((deck.minX + deck.maxX) / 2.0D);
            }
            List<Double> zs = new ArrayList<>();
            if (z0 <= z1) {
                for (double z = z0; z <= z1 + 1e-5; z += zStep) zs.add(z);
            } else {
                zs.add((deck.minZ + deck.maxZ) / 2.0D);
            }

            for (double x : xs) {
                for (double z : zs) {
                    List<Double> ys = col.standYs(x, z, deck.minY);
                    for (double y : ys) {
                        if (Math.abs(y - deck.minY) < 0.05D) {
                            start = new Vec3(x, y, z);
                            break;
                        }
                    }
                    if (start != null) break;
                }
                if (start != null) break;
            }
            if (start != null) break;
        }

        if (start == null) {
            return new WalkTestResult(vehicleId, null, 0, Collections.emptyMap(), List.of("no standing spot found on any deck"));
        }

        double step = 3.0D / 16.0D;
        Map<String, Vec3> seen = col.reach(start, step, 400000);

        Map<Long, List<Double>> cells = new HashMap<>();
        for (Vec3 v : seen.values()) {
            int ix = (int) Math.round(v.x / step);
            int iz = (int) Math.round(v.z / step);
            long k = VehicleCollisionData.gridKey(ix, iz);
            cells.computeIfAbsent(k, key -> new ArrayList<>()).add(v.y);
        }

        double tol = 2.5D / 16.0D;
        List<String> problems = new ArrayList<>();
        Map<String, Integer> coverage = new HashMap<>();

        for (Map.Entry<String, AABB> entry : decks.entrySet()) {
            String name = entry.getKey();
            if (name.contains("roof") || name.contains("zone") || name.contains("open") || name.contains("envelope")) continue;
            AABB deck = entry.getValue();
            int points = 0, hit = 0;
            double xStep = 4.0D / 16.0D, zStep = 4.0D / 16.0D;
            double xStart = deck.minX + 2.0D / 16.0D;
            double zStart = deck.minZ + 2.0D / 16.0D;

            for (double x = xStart; x <= deck.maxX - 0.01D; x += xStep) {
                for (double z = zStart; z <= deck.maxZ - 0.01D; z += zStep) {
                    points++;
                    int ix = (int) Math.round(x / step);
                    int iz = (int) Math.round(z / step);
                    boolean ok = false;
                    for (int dx = -1; dx <= 1 && !ok; dx++) {
                        for (int dz = -1; dz <= 1 && !ok; dz++) {
                            List<Double> ys = cells.get(VehicleCollisionData.gridKey(ix + dx, iz + dz));
                            if (ys != null) {
                                for (double yy : ys) {
                                    if (Math.abs(yy - deck.minY) <= tol) {
                                        ok = true;
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    if (ok) hit++;
                }
            }
            int pct = points > 0 ? (int) Math.round(100.0D * hit / points) : 0;
            coverage.put(name, pct);
            if (pct == 0) {
                problems.add("deck '" + name + "' unreachable from entry");
            }
        }

        return new WalkTestResult(vehicleId, start, seen.size(), coverage, problems);
    }

    public record WalkTestResult(String vehicleId, Vec3 entry, int reachableStates, Map<String, Integer> coveragePct, List<String> problems) {}
}
