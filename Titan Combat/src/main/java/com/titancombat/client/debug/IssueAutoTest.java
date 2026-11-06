package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.transport.*;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;
import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * TITAN_AUTOTEST=issues: player-report regressions. Hovercraft parked with a pilot and no input stays put,
 * the pilot stays inside a pitching Chinook / C-130, the carrier deck walks freely and never culls,
 * players stand in the C-130 bay and ride along, plus look-around shots of the C-130 and Trooper models.
 */
final class IssueAutoTest {
    private static final Map<Integer, Consumer<Minecraft>> STEPS = new HashMap<>();
    private static final Map<String, Integer> IDS = new HashMap<>();
    private static int clock = 0, at = 0;
    private static volatile boolean serverBusy = false;
    private static double bx, by, bz;
    private static Vec3 mark;
    private static float markYaw;

    private IssueAutoTest() {}

    static void run(Minecraft mc) {
        if (STEPS.isEmpty()) build();
        if (serverBusy) return;
        Consumer<Minecraft> step = STEPS.get(++clock);
        if (step != null) step.accept(mc);
    }

    private static void then(int delay, Consumer<Minecraft> action) {
        at += delay;
        STEPS.put(at, action);
    }

    private static void server(Minecraft mc, BiConsumer<ServerPlayer, ServerLevel> a) {
        serverBusy = true;
        ClientAutoTest.server2(mc, (p, l) -> {
            try {
                a.accept(p, l);
            } catch (Throwable t) {
                TitanCombatMod.LOGGER.error("[autotest] step failed", t);
            } finally {
                serverBusy = false;
            }
        });
    }

    private static void check(String name, boolean pass, Object detail) {
        TitanCombatMod.LOGGER.info("[autotest] CHECK {} {} : {}", name, detail, pass ? "PASS" : "FAIL");
    }

    private static Entity get(ServerLevel l, String key) {
        return l.getEntity(IDS.getOrDefault(key, -1));
    }

    private static <T extends Entity> T spawn(ServerLevel l, String key, EntityType<T> type, double x, double y, double z, float yaw) {
        T e = type.create(l);
        e.moveTo(x, y, z, yaw, 0.0F);
        l.addFreshEntity(e);
        IDS.put(key, e.getId());
        return e;
    }

    private static void board(String key) {
        then(10, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.SURVIVAL);
            p.startRiding(get(l, key), true);
        }));
    }

    /** Pilot sits in {@code key} with hands off for {@code ticks}: the hull must not turn or wander. */
    private static void parked(String name, String key, int ticks) {
        board(key);
        then(10, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            mark = mc.player.getVehicle().position();
            markYaw = mc.player.getVehicle().getYRot();
        });
        then(ticks, mc -> {
            Entity v = mc.player.getVehicle();
            double drift = v.position().subtract(mark).horizontalDistance();
            float turn = Math.abs(net.minecraft.util.Mth.wrapDegrees(v.getYRot() - markYaw));
            check(name, drift < 0.5D && turn < 2.0F && Math.abs(v.getY() - mark.y) < 0.6D,
                    String.format("drift %.2f turn %.1f dy %.2f", drift, turn, v.getY() - mark.y));
        });
    }

    /** Pilot's eye must stay under the hull's roof while the fuselage pitches nose-down in forward flight. */
    private static void pilotInside(String name, String key, int climbTicks, int cruiseTicks) {
        board(key);
        then(10, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            mc.options.keyUp.setDown(true);
            mc.options.keyJump.setDown(true);
        });
        then(climbTicks, mc -> mc.options.keyJump.setDown(false));
        then(cruiseTicks, mc -> {
            BaseTransportVehicleEntity v = (BaseTransportVehicleEntity) mc.player.getVehicle();
            float pitch = v.getHullPitch();
            Vec3 seat = v.seatWorldPos(mc.player);
            check(name, mc.player.position().distanceTo(seat) < 0.3D && Math.abs(pitch) > 0.02F,
                    String.format("pitch %.3f rad, player-to-tilted-seat %.2f", pitch, mc.player.position().distanceTo(seat)));
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
        });
        then(4, mc -> ClientAutoTest.shot(mc, name));
        then(2, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.setCameraType(CameraType.FIRST_PERSON);
        });
        then(4, mc -> ClientAutoTest.shot(mc, name + "_1st"));
    }

    /** Camera shot of a point given as an offset from the arena origin (resolved when the step runs: the origin is set at run time). */
    private static void look(String name, double x, double y, double z, double dist, double elev, double az) {
        then(2, mc -> ClientAutoTest.aimCameraAt(mc, bx + x, by + y, bz + z, dist, elev, az));
        then(25, mc -> ClientAutoTest.shot(mc, name));
    }

    private static void build() {
        then(20, mc -> {
            if (mc.player.isDeadOrDying()) mc.player.respawn(); // a run that died mid-air saves a dead player
        });
        then(40, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.CREATIVE);
            l.setDayTime(6000L);
            bx = Math.floor(p.getX()); by = Math.floor(p.getY()); bz = Math.floor(p.getZ());
            ClientAutoTest.tBaseX = bx; ClientAutoTest.tBaseY = by; ClientAutoTest.tBaseZ = bz;
            for (Entity e : l.getAllEntities()) {
                if (e instanceof BaseTransportVehicleEntity || e instanceof com.titancombat.entity.BaseTitanEntity || e instanceof DeckColliderEntity) e.discard();
            }
            // Land (-X) and open sea (+X)
            for (int dx = -100; dx <= 70; dx++) {
                for (int dz = -40; dz <= 40; dz++) {
                    for (int dy = 1; dy <= 30; dy++) l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), Blocks.AIR.defaultBlockState(), 2);
                    boolean sea = dx >= 0;
                    for (int dy = -6; dy <= 0; dy++) {
                        var st = sea ? (dy == -6 ? Blocks.SAND.defaultBlockState() : Blocks.WATER.defaultBlockState())
                                : (dy == 0 ? Blocks.STONE.defaultBlockState() : Blocks.DIRT.defaultBlockState());
                        l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), st, 2);
                    }
                }
            }
            double g = by + 1.0D;
            spawn(l, "lcac_land", ModEntities.LCAC_HOVERCRAFT.get(), bx - 20, g, bz - 20, 90.0F);
            spawn(l, "lcac_sea", ModEntities.LCAC_HOVERCRAFT.get(), bx + 15, by + 0.5D, bz - 25, 90.0F);
            spawn(l, "carrier", ModEntities.OCEAN_CARRIER.get(), bx + 40, by + 0.5D, bz, 30.0F); // diagonal heading: tiles overlap most
            spawn(l, "chinook", ModEntities.CHINOOK_TRANSPORTER.get(), bx - 40, g, bz + 20, 90.0F);
            spawn(l, "c130", ModEntities.C130_HERCULES.get(), bx - 30, g, bz - 5, 90.0F);
            spawn(l, "c130_show", ModEntities.C130_HERCULES.get(), bx - 55, g, bz + 25, 90.0F);
            var trooper = spawn(l, "trooper", ModEntities.TROOPER_TITAN.get(), bx - 45, g, bz - 25, 180.0F);
            trooper.setNoAi(true);
            trooper.getTitanInventory().setItem(com.titancombat.gui.TitanMenu.WEAPON_SLOT, new net.minecraft.world.item.ItemStack(
                    com.titancombat.item.ModItems.WEAPON_MODULES.get(com.titancombat.entity.TitanWeapon.ROTARY_MACHINE_GUN).get()));
        }));

        // ---- 4. hovercraft with a pilot and no input: on land and afloat
        parked("lcac_parked_on_land", "lcac_land", 80);
        parked("lcac_parked_afloat", "lcac_sea", 80);
        // drive: throttle, then a held turn, then let go of everything; it must settle, not keep spinning
        then(1, mc -> mc.options.keyUp.setDown(true));
        for (int i = 0; i < 16; i++) {
            final int k = i;
            then(10, mc -> {
                if (k == 4) mc.options.keyLeft.setDown(true);
                if (k == 8) { mc.options.keyLeft.setDown(false); mc.options.keyUp.setDown(false); }
                Entity v = mc.player.getVehicle();
                Vec3 m = v.getDeltaMovement();
                double slip = m.horizontalDistance() < 0.05D ? 0.0D
                        : net.minecraft.util.Mth.wrapDegrees(Math.toDegrees(Math.atan2(-m.x, m.z)) - v.getYRot());
                TitanCombatMod.LOGGER.info("[autotest] lcac t={} yaw={} speed={} slip={} y={} water={}", k * 10,
                        String.format("%.1f", v.getYRot()), String.format("%.2f", m.horizontalDistance()), String.format("%.0f", slip),
                        String.format("%.2f", v.getY()), v.isInWater());
                if (k == 12) markYaw = v.getYRot();
                if (k == 15) check("lcac_settles_after_release", Math.abs(net.minecraft.util.Mth.wrapDegrees(v.getYRot() - markYaw)) < 3.0F,
                        String.format("still turned %.1f deg in the last 30 ticks", net.minecraft.util.Mth.wrapDegrees(v.getYRot() - markYaw)));
            });
        }

        // ---- 2. pilot stays seated inside pitching aircraft
        pilotInside("chinook_pilot_seated", "chinook", 30, 40);
        then(5, mc -> server(mc, (p, l) -> {
            p.setGameMode(GameType.CREATIVE);
            p.stopRiding();
            var v = get(l, "chinook");
            v.discard();
        }));
        board("c130");
        then(5, mc -> mc.options.keyUp.setDown(true));
        then(110, mc -> mc.options.keyJump.setDown(true)); // take-off roll first
        then(25, mc -> mc.options.keyJump.setDown(false));
        then(20, mc -> {
            BaseTransportVehicleEntity v = (BaseTransportVehicleEntity) mc.player.getVehicle();
            check("c130_pilot_seated", mc.player.position().distanceTo(v.seatWorldPos(mc.player)) < 0.3D,
                    String.format("pitch %.3f rad, player-to-tilted-seat %.2f", v.getHullPitch(), mc.player.position().distanceTo(v.seatWorldPos(mc.player))));
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
        });
        then(4, mc -> ClientAutoTest.shot(mc, "c130_pilot_seated"));
        then(2, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            server(mc, (p, l) -> { p.setGameMode(GameType.CREATIVE); p.stopRiding(); get(l, "c130").discard(); }); // creative: no fatal fall from altitude
        });

        // ---- 3. carrier deck: walk the length of it across tile seams, then look around from the deck
        then(10, mc -> server(mc, (p, l) -> p.setGameMode(GameType.CREATIVE))); // no fall damage when hopping out mid-air
        then(5, mc -> mc.player.stopRiding());
        then(10, mc -> server(mc, (p, l) -> {
            var c = get(l, "carrier");
            p.setGameMode(GameType.SURVIVAL);
            p.resetFallDistance(); // still falling from the C-130 test
            p.setDeltaMovement(Vec3.ZERO);
            double yaw = Math.toRadians(c.getYRot());
            // stern of the deck, facing the bow
            p.teleportTo(l, c.getX() + Math.sin(yaw) * 16, c.getY() + TitanOceanCarrierEntity.DECK_TOP_Y + 0.2D, c.getZ() - Math.cos(yaw) * 16, c.getYRot(), 0.0F);
        }));
        then(30, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] deck start: client {} dead={} vehicle={} mode={}", mc.player.position(), mc.player.isDeadOrDying(),
                    mc.player.getVehicle(), mc.gameMode.getPlayerMode());
            server(mc, (p, l) -> TitanCombatMod.LOGGER.info("[autotest] deck start: server {} dead={} carrier={}", p.position(), p.isDeadOrDying(), get(l, "carrier")));
            mark = mc.player.position();
            mc.options.keyUp.setDown(true);
        });
        then(80, mc -> {
            mc.options.keyUp.setDown(false);
            double walked = mc.player.position().subtract(mark).horizontalDistance();
            check("carrier_deck_walk", walked > 13.0D, String.format("walked %.1f in 80 ticks (free walking ~17)", walked));
            Entity c = mc.level.getEntity(mc.player.level().getEntitiesOfClass(TitanOceanCarrierEntity.class, mc.player.getBoundingBox().inflate(40)).get(0).getId());
            double deck = c.getY() + TitanOceanCarrierEntity.DECK_TOP_Y;
            check("carrier_still_on_deck", Math.abs(mc.player.getY() - deck) < 0.6D, String.format("y=%.2f deck=%.2f", mc.player.getY(), deck));
            // stood on the deck, looking away from the hull's centre: the hull must still be drawn
            mc.player.setYRot(c.getYRot() + 60.0F);
            mc.player.setXRot(60.0F);
        });
        then(5, mc -> ClientAutoTest.shot(mc, "carrier_look_down_from_deck"));
        then(2, mc -> { mc.player.setYRot(mc.player.getYRot() + 120.0F); mc.player.setXRot(45.0F); });
        then(5, mc -> ClientAutoTest.shot(mc, "carrier_look_down_back"));

        // ---- 1. C-130: model look-around, then stand in the bay and ride along
        look("c130_front_left", -55, 3, +25, 26, 15, 135);
        look("c130_rear_right", -55, 3, +25, 26, 20, 315);
        look("c130_top", -55, 3, +25, 30, 70, 200);
        look("c130_side", -55, 3, +25, 28, 3, 180);
        then(5, mc -> server(mc, (p, l) -> {
            var c = (BaseTransportVehicleEntity) get(l, "c130_show");
            p.setGameMode(GameType.SURVIVAL);
            // directly above the middle of the cargo bay, to drop in onto the floor
            p.teleportTo(l, c.getX(), c.getY() + 8.0D, c.getZ(), c.getYRot(), 0.0F);
        }));
        then(40, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            double rel = p.getY() - c.getY();
            check("c130_walkable", rel > 0.5D && p.onGround(), String.format("player stands %.2f above the C-130 origin, onGround=%s", rel, p.onGround()));
            IDS.put("c130_rel", (int) Math.round(rel * 100));
        }));
        for (int i = 0; i < 12; i++) { // taxi 6 blocks at 0.5 blocks/tick: the rider must come along
            then(1, mc -> server(mc, (p, l) -> {
                var c = get(l, "c130_show");
                c.setPos(c.getX() - 0.5D, c.getY(), c.getZ());
            }));
        }
        then(10, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            check("c130_carries_rider", Math.abs(p.getX() - c.getX()) < 1.0D && p.getY() - c.getY() > 0.5D,
                    String.format("dx=%.2f rel y=%.2f", p.getX() - c.getX(), p.getY() - c.getY()));
        }));

        // inside the cargo bay: stand on the floor and taxi again
        then(2, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            float yaw = c.getYRot() * net.minecraft.util.Mth.DEG_TO_RAD;
            double lz = 4.0D; // forward bay
            p.teleportTo(l, c.getX() - lz * Math.sin(yaw), c.getY() + 1.2D, c.getZ() + lz * Math.cos(yaw), c.getYRot(), 0.0F);
        }));
        then(30, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            IDS.put("bay_dx", (int) Math.round((p.getX() - c.getX()) * 100));
            check("c130_bay_floor", Math.abs(p.getY() - c.getY() - 0.875D) < 0.1D && p.onGround(), String.format("rel y=%.2f", p.getY() - c.getY()));
        }));
        for (int i = 0; i < 12; i++) {
            then(1, mc -> server(mc, (p, l) -> {
                var c = get(l, "c130_show");
                c.setPos(c.getX() - 0.5D, c.getY(), c.getZ());
            }));
        }
        then(10, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            double drift = (p.getX() - c.getX()) - IDS.get("bay_dx") / 100.0D;
            check("c130_bay_carries_rider", Math.abs(drift) < 1.0D, String.format("rider fell behind by %.2f", drift));
        }));
        then(2, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            float yaw = c.getYRot() * net.minecraft.util.Mth.DEG_TO_RAD;
            double lx = 9.0D; // over the left wing, middle panel
            p.teleportTo(l, c.getX() + lx * Math.cos(yaw), c.getY() + 8.0D, c.getZ() + lx * Math.sin(yaw), c.getYRot(), 0.0F);
        }));
        then(40, mc -> server(mc, (p, l) -> {
            var c = get(l, "c130_show");
            double rel = p.getY() - c.getY();
            check("c130_wing_walkable", Math.abs(rel - 6.25D) < 0.1D && p.onGround(), String.format("player stands %.2f above the origin (wing top 6.25)", rel));
        }));

        // ---- 5. Trooper
        look("trooper_front", -45, 3, -25, 12, 10, 0);
        look("trooper_front_left", -45, 3, -25, 12, 12, 35);
        look("trooper_side", -45, 3, -25, 12, 5, 90);
        look("trooper_back", -45, 3, -25, 12, 15, 210);

        then(10, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] Completed issues test suite");
            mc.stop();
        });
    }
}
