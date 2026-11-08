package com.vehiclefleet.physics;

import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.*;

/**
 * Port of collision.py's PlayerSolver and reach() to Java.
 * Units: Minecraft blocks (16 px = 1 block).
 * Frame: +X vehicle left, +Y up, +Z vehicle forward (nose).
 */
public class VehicleCollisionData {
    public static final double PLAYER_W = 0.6D;   // 9.6 px
    public static final double PLAYER_H = 1.8D;   // 28.8 px
    public static final double STEP = 0.6D;       // 9.6 px
    public static final double CELL = 1.0D;       // 16.0 px

    private final List<AABB> staticBoxes;
    private final Map<String, List<AABB>> dynamicBoxes;
    private final Map<Long, List<Integer>> grid = new HashMap<>();

    public VehicleCollisionData(List<AABB> staticBoxes, Map<String, List<AABB>> dynamicBoxes) {
        this.staticBoxes = Collections.unmodifiableList(staticBoxes);
        this.dynamicBoxes = Collections.unmodifiableMap(dynamicBoxes);
        for (int i = 0; i < staticBoxes.size(); i++) {
            AABB b = staticBoxes.get(i);
            int minGx = (int) Math.floor(b.minX / CELL);
            int maxGx = (int) Math.floor(b.maxX / CELL);
            int minGz = (int) Math.floor(b.minZ / CELL);
            int maxGz = (int) Math.floor(b.maxZ / CELL);
            for (int gx = minGx; gx <= maxGx; gx++) {
                for (int gz = minGz; gz <= maxGz; gz++) {
                    grid.computeIfAbsent(gridKey(gx, gz), k -> new ArrayList<>()).add(i);
                }
            }
        }
    }

    public static long gridKey(int gx, int gz) {
        return (((long) gx) << 32) | (gz & 0xFFFFFFFFL);
    }

    public List<AABB> getStaticBoxes() {
        return staticBoxes;
    }

    public Map<String, List<AABB>> getDynamicBoxes() {
        return dynamicBoxes;
    }

    public List<AABB> near(double x, double z, double r) {
        Set<Integer> ids = new HashSet<>();
        int minGx = (int) Math.floor((x - r) / CELL);
        int maxGx = (int) Math.floor((x + r) / CELL);
        int minGz = (int) Math.floor((z - r) / CELL);
        int maxGz = (int) Math.floor((z + r) / CELL);
        for (int gx = minGx; gx <= maxGx; gx++) {
            for (int gz = minGz; gz <= maxGz; gz++) {
                List<Integer> list = grid.get(gridKey(gx, gz));
                if (list != null) ids.addAll(list);
            }
        }
        List<AABB> out = new ArrayList<>(ids.size());
        for (int id : ids) out.add(staticBoxes.get(id));
        return out;
    }

    public boolean free(double x, double y, double z, List<AABB> nearBoxes) {
        double h = PLAYER_W / 2.0D - 0.00125D;
        List<AABB> boxes = (nearBoxes != null) ? nearBoxes : near(x, z, PLAYER_W / 2.0D + 0.1D);
        for (AABB b : boxes) {
            if (b.minX < x + h && b.maxX > x - h
                    && b.minZ < z + h && b.maxZ > z - h
                    && b.minY < y + PLAYER_H - 0.00125D && b.maxY > y + 0.00125D) {
                return false;
            }
        }
        return true;
    }

    public List<Double> standYs(double x, double z, double yFrom) {
        List<AABB> nearBoxes = near(x, z, PLAYER_W / 2.0D + 0.1D);
        double h = PLAYER_W / 2.0D;
        Set<Double> topsSet = new HashSet<>();
        for (AABB b : nearBoxes) {
            if (b.minX < x + h - 0.00125D && b.maxX > x - h + 0.00125D
                    && b.minZ < z + h - 0.00125D && b.maxZ > z - h + 0.00125D
                    && Math.abs(b.maxY - yFrom) <= STEP + 1e-6D) {
                topsSet.add(b.maxY);
            }
        }
        List<Double> tops = new ArrayList<>(topsSet);
        tops.sort(Collections.reverseOrder());
        List<Double> valid = new ArrayList<>();
        for (double t : tops) {
            if (free(x, t, z, nearBoxes)) valid.add(t);
        }
        return valid;
    }

    public Double standY(double x, double z, double yFrom) {
        List<Double> r = standYs(x, z, yFrom);
        return r.isEmpty() ? null : r.get(0);
    }

    private static String reachKey(double x, double y, double z, double step) {
        return Math.round(x / step) + "_" + Math.round(z / step) + "_" + Math.round(y * 64.0D);
    }

    public Map<String, Vec3> reach(Vec3 start, double step, int limit) {
        Map<String, Vec3> seen = new HashMap<>();
        Deque<Vec3> queue = new ArrayDeque<>();
        String startKey = reachKey(start.x, start.y, start.z, step);
        seen.put(startKey, start);
        queue.add(start);
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {1, -1}, {-1, 1}, {-1, -1}};
        while (!queue.isEmpty() && seen.size() < limit) {
            Vec3 curr = queue.poll();
            for (int[] d : dirs) {
                double nx = curr.x + d[0] * step;
                double nz = curr.z + d[1] * step;
                for (double ny : standYs(nx, nz, curr.y)) {
                    String k = reachKey(nx, ny, nz, step);
                    if (!seen.containsKey(k)) {
                        Vec3 pos = new Vec3(nx, ny, nz);
                        seen.put(k, pos);
                        queue.add(pos);
                    }
                }
            }
        }
        return seen;
    }

    /** Resolves requested local delta movement against static and active dynamic boxes in Y, X, Z axis order. */
    public Vec3 resolveMove(Vec3 pos, Vec3 delta, boolean includeDynamic) {
        List<AABB> candidates = near(pos.x + delta.x * 0.5D, pos.z + delta.z * 0.5D, Math.max(1.5D, delta.length() + 1.0D));
        if (includeDynamic) {
            for (List<AABB> dList : dynamicBoxes.values()) {
                candidates.addAll(dList);
            }
        }

        AABB box = new AABB(pos.x - 0.3D, pos.y, pos.z - 0.3D, pos.x + 0.3D, pos.y + PLAYER_H, pos.z + 0.3D);
        Vec3 flatMove = sweepMove(box, delta, candidates);

        // Try step-up if horizontal movement was impeded
        if ((flatMove.x != delta.x || flatMove.z != delta.z) && delta.horizontalDistanceSqr() > 1e-6D) {
            AABB stepBox = box.move(0.0D, STEP, 0.0D);
            Vec3 stepHoriz = sweepHorizontal(stepBox, new Vec3(delta.x, 0.0D, delta.z), candidates);
            stepBox = stepBox.move(stepHoriz.x, 0.0D, stepHoriz.z);
            double stepDown = sweepY(stepBox, -STEP - Math.max(0.0D, -delta.y), candidates);
            stepBox = stepBox.move(0.0D, stepDown, 0.0D);

            double flatDist = flatMove.x * flatMove.x + flatMove.z * flatMove.z;
            double stepDist = stepHoriz.x * stepHoriz.x + stepHoriz.z * stepHoriz.z;
            if (stepDist > flatDist && free(stepBox.minX + 0.3D, stepBox.minY, stepBox.minZ + 0.3D, candidates)) {
                return new Vec3(stepBox.minX + 0.3D, stepBox.minY, stepBox.minZ + 0.3D);
            }
        }

        Vec3 res = pos.add(flatMove);
        Double snap = standY(res.x, res.z, res.y);
        if (snap != null && Math.abs(snap - res.y) <= 0.15D) {
            res = new Vec3(res.x, snap, res.z);
        }
        return res;
    }

    private static Vec3 sweepMove(AABB box, Vec3 delta, List<AABB> boxes) {
        double dy = sweepY(box, delta.y, boxes);
        box = box.move(0.0D, dy, 0.0D);
        double dx = sweepX(box, delta.x, boxes);
        box = box.move(dx, 0.0D, 0.0D);
        double dz = sweepZ(box, delta.z, boxes);
        return new Vec3(dx, dy, dz);
    }

    private static Vec3 sweepHorizontal(AABB box, Vec3 delta, List<AABB> boxes) {
        double dx = sweepX(box, delta.x, boxes);
        box = box.move(dx, 0.0D, 0.0D);
        double dz = sweepZ(box, delta.z, boxes);
        return new Vec3(dx, 0.0D, dz);
    }

    private static double sweepY(AABB box, double dy, List<AABB> boxes) {
        if (dy == 0.0D) return 0.0D;
        for (AABB b : boxes) {
            if (box.maxX > b.minX + 0.001D && box.minX < b.maxX - 0.001D && box.maxZ > b.minZ + 0.001D && box.minZ < b.maxZ - 0.001D) {
                if (dy > 0.0D && box.maxY <= b.minY + 0.001D) {
                    dy = Math.min(dy, b.minY - box.maxY);
                } else if (dy < 0.0D && box.minY >= b.maxY - 0.001D) {
                    dy = Math.max(dy, b.maxY - box.minY);
                }
            }
        }
        return dy;
    }

    private static double sweepX(AABB box, double dx, List<AABB> boxes) {
        if (dx == 0.0D) return 0.0D;
        for (AABB b : boxes) {
            if (box.maxY > b.minY + 0.001D && box.minY < b.maxY - 0.001D && box.maxZ > b.minZ + 0.001D && box.minZ < b.maxZ - 0.001D) {
                if (dx > 0.0D && box.maxX <= b.minX + 0.001D) {
                    dx = Math.min(dx, b.minX - box.maxX);
                } else if (dx < 0.0D && box.minX >= b.maxX - 0.001D) {
                    dx = Math.max(dx, b.maxX - box.minX);
                }
            }
        }
        return dx;
    }

    private static double sweepZ(AABB box, double dz, List<AABB> boxes) {
        if (dz == 0.0D) return 0.0D;
        for (AABB b : boxes) {
            if (box.maxX > b.minX + 0.001D && box.minX < b.maxX - 0.001D && box.maxY > b.minY + 0.001D && box.minY < b.maxY - 0.001D) {
                if (dz > 0.0D && box.maxZ <= b.minZ + 0.001D) {
                    dz = Math.min(dz, b.minZ - box.maxZ);
                } else if (dz < 0.0D && box.minZ >= b.maxZ - 0.001D) {
                    dz = Math.max(dz, b.maxZ - box.minZ);
                }
            }
        }
        return dz;
    }
}
