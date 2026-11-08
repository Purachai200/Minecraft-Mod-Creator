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
import net.minecraft.world.entity.Mob;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;

import java.util.HashMap;
import java.util.Map;
import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * TITAN_AUTOTEST=navy: patrol boat, frigate, sky carrier and LCAC drive with real keys; a no-AI pig left on each deck must ride along,
 * the sky carrier must hang where it is left, and every hull gets a camo shot. Logs "[autotest] CHECK <name> ... : PASS|FAIL".
 */
final class NavyAutoTest {
    private static final Map<Integer, Consumer<Minecraft>> STEPS = new HashMap<>();
    private static final Map<String, Integer> IDS = new HashMap<>();
    private static int clock = 0, at = 0;
    private static volatile boolean serverBusy = false;
    private static double bx, by, bz, y0;
    private static double[] mark = new double[3];

    private NavyAutoTest() {}

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

    private static void pig(ServerLevel l, String key, Entity ship, double dy, double dz) {
        Mob p = spawn(l, key, EntityType.PIG, ship.getX(), ship.getY() + dy, ship.getZ() + dz, 0.0F);
        p.setNoAi(true);
    }

    private static boolean onDeck(ServerLevel l, String pigKey, String shipKey, double minAbove) {
        Entity p = get(l, pigKey), s = get(l, shipKey);
        if (p != null && s != null) TitanCombatMod.LOGGER.info("[autotest] {} pig=({},{},{}) ship=({},{},{}) alive={} water={}", shipKey,
                (int) p.getX(), (int) p.getY(), (int) p.getZ(), (int) s.getX(), (int) s.getY(), (int) s.getZ(), p.isAlive(), p.isInWater());
        return p != null && s != null && p.isAlive() && Math.hypot(p.getX() - s.getX(), p.getZ() - s.getZ()) < 14.0D && p.getY() > s.getY() + minAbove;
    }

    /** Ride {@code key}, hold the keys for {@code ticks}, then {@code verify}. */
    private static void drive(String key, int ticks, boolean up, Consumer<Minecraft> verify) {
        then(10, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.SURVIVAL);
            p.startRiding(get(l, key), true);
        }));
        then(10, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            Entity v = mc.player.getVehicle();
            mark = new double[]{v.getX(), v.getY(), v.getZ()};
            mc.options.keyUp.setDown(true);
            if (up) mc.options.keyJump.setDown(true);
        });
        then(ticks, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.keyJump.setDown(false);
            verify.accept(mc);
        });
    }

    private static double moved(Minecraft mc) {
        Entity v = mc.player.getVehicle();
        return Math.hypot(v.getX() - mark[0], v.getZ() - mark[2]);
    }

    private static void build() {
        then(40, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.CREATIVE);
            l.setDayTime(6000L);
            bx = Math.floor(p.getX()); by = Math.floor(p.getY()); bz = Math.floor(p.getZ());
            y0 = by + 1.0D;
            ClientAutoTest.tBaseX = bx; ClientAutoTest.tBaseY = by; ClientAutoTest.tBaseZ = bz;
            for (Entity e : l.getAllEntities()) {
                if (e instanceof BaseTransportVehicleEntity || e instanceof DeckColliderEntity) e.discard();
            }
            for (int dx = -70; dx <= 70; dx++) {
                for (int dz = -20; dz <= 140; dz++) {
                    for (int dy = 1; dy <= 40; dy++) l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), Blocks.AIR.defaultBlockState(), 2);
                    for (int dy = -6; dy <= 0; dy++) l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), dy == -6 ? Blocks.SAND.defaultBlockState() : Blocks.WATER.defaultBlockState(), 2);
                }
            }
            p.teleportTo(l, bx, by + 1, bz - 10, 0, 0);
            spawn(l, "boat", ModEntities.PATROL_BOAT.get(), bx - 40, by + 0.5D, bz, 0.0F);
            spawn(l, "frigate", ModEntities.PATROL_FRIGATE.get(), bx - 15, by + 0.5D, bz, 0.0F);
            spawn(l, "lcac", ModEntities.LCAC_HOVERCRAFT.get(), bx + 15, by + 0.5D, bz, 0.0F);
            spawn(l, "sky", ModEntities.SKY_CARRIER.get(), bx + 45, by + 14, bz + 40, 0.0F);
        }));
        then(60, mc -> server(mc, (p, l) -> { // let the deck tiles spawn and the hulls settle
            pig(l, "pig_boat", get(l, "boat"), 1.45D, -2.0D);
            pig(l, "pig_frigate", get(l, "frigate"), 2.7D, -9.0D);
            pig(l, "pig_lcac", get(l, "lcac"), 1.45D, -2.0D);
            pig(l, "pig_sky", get(l, "sky"), 3.35D, -8.0D);
            for (String k : new String[]{"boat", "frigate", "lcac", "sky"}) {
                var deck = l.getEntitiesOfClass(DeckColliderEntity.class, get(l, k).getBoundingBox().inflate(30.0D), t -> t.getParent() == get(l, k));
                check("deck_tiles_" + k, !deck.isEmpty(), deck.size() + " tiles");
            }
        }));
        then(60, mc -> server(mc, (p, l) -> {
            check("pig_rests_boat", onDeck(l, "pig_boat", "boat", 1.0D), "");
            check("pig_rests_frigate", onDeck(l, "pig_frigate", "frigate", 2.0D), "");
            check("pig_rests_lcac", onDeck(l, "pig_lcac", "lcac", 0.8D), "");
            check("pig_rests_sky", onDeck(l, "pig_sky", "sky", 2.5D), "");
            Entity s = get(l, "sky");
            mark = new double[]{s.getX(), s.getY(), s.getZ()};
        }));

        // ---- sky carrier unmanned: hangs where it is, no sinking
        then(100, mc -> server(mc, (p, l) -> {
            Entity s = get(l, "sky");
            check("sky_hangs_when_abandoned", Math.abs(s.getY() - mark[1]) < 0.3D && !s.onGround(), String.format("y %.2f -> %.2f", mark[1], s.getY()));
            check("sky_pig_stays_aboard", onDeck(l, "pig_sky", "sky", 2.5D), "");
        }));

        // ---- drive each vessel; the pig must follow
        drive("boat", 60, false, mc -> {
            check("boat_sails", moved(mc) > 6, String.format("moved %.1f", moved(mc)));
            server(mc, (p, l) -> check("pig_follows_boat", onDeck(l, "pig_boat", "boat", 1.0D), ""));
        });
        drive("frigate", 90, false, mc -> {
            check("frigate_sails", moved(mc) > 6, String.format("moved %.1f", moved(mc)));
            server(mc, (p, l) -> check("pig_follows_frigate", onDeck(l, "pig_frigate", "frigate", 2.0D), ""));
        });
        drive("lcac", 60, false, mc -> {
            check("lcac_hovers_along", moved(mc) > 6, String.format("moved %.1f", moved(mc)));
            server(mc, (p, l) -> check("pig_follows_lcac", onDeck(l, "pig_lcac", "lcac", 0.8D), ""));
        });
        drive("sky", 40, true, mc -> {
            check("sky_climbs", mc.player.getVehicle().getY() - mark[1] > 3.0D, String.format("y %.1f", mc.player.getVehicle().getY()));
            mark = new double[]{mc.player.getVehicle().getX(), mc.player.getVehicle().getY(), mc.player.getVehicle().getZ()};
        });
        then(60, mc -> server(mc, (p, l) -> { // hands off the controls while still aboard: hovers
            Entity s = get(l, "sky");
            check("sky_hovers_when_idle", Math.abs(s.getY() - mark[1]) < 1.5D, String.format("y %.2f -> %.2f", mark[1], s.getY()));
            mark = new double[]{s.getX(), s.getY(), s.getZ()};
        }));
        drive("sky", 80, false, mc -> {
            check("sky_flies_forward", moved(mc) > 5, String.format("moved %.1f", moved(mc)));
            server(mc, (p, l) -> check("pig_follows_sky", onDeck(l, "pig_sky", "sky", 2.5D), ""));
        });

        // ---- camo + screenshots
        then(10, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.SPECTATOR);
            int c = 1;
            for (String k : new String[]{"boat", "frigate", "lcac", "sky"}) ((BaseTransportVehicleEntity) get(l, k)).setCamo(c++);
            mark = new double[]{get(l, "boat").getX(), get(l, "boat").getY(), get(l, "boat").getZ()};
        }));
        for (String k : new String[]{"boat", "frigate", "lcac", "sky"}) {
            then(10, mc -> {
                Entity e = mc.level.getEntities((Entity) null, mc.player.getBoundingBox().inflate(300.0D), x -> x instanceof BaseTransportVehicleEntity v
                        && v.getType() == switch (k) {
                            case "boat" -> ModEntities.PATROL_BOAT.get();
                            case "frigate" -> ModEntities.PATROL_FRIGATE.get();
                            case "lcac" -> ModEntities.LCAC_HOVERCRAFT.get();
                            default -> ModEntities.SKY_CARRIER.get();
                        }).stream().findFirst().orElse(null);
                if (e != null) ClientAutoTest.aimCameraAt(mc, e.getX(), e.getY() + 2, e.getZ(), k.equals("sky") ? 110 : k.equals("frigate") ? 30 : 11, 14, 125);
            });
            then(25, mc -> ClientAutoTest.shot(mc, "navy_" + k + "_camo"));
        }
        then(10, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] navy done");
            mc.stop();
        });
    }
}
