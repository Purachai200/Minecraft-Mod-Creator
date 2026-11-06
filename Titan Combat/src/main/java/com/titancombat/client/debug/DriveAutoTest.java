package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.transport.*;
import net.minecraft.client.CameraType;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.BiConsumer;
import java.util.function.Consumer;
import java.util.function.Supplier;

/**
 * TITAN_AUTOTEST=drive: drives the new vehicles with real key presses (LCAC, repair truck, C-130 take-off/turn/landing),
 * clamps and releases a Titan on every transport, and checks the Obsolete Exoframe Shift-dock when Obsolete is loaded.
 */
final class DriveAutoTest {
    private static final Map<Integer, Consumer<Minecraft>> STEPS = new HashMap<>();
    private static final Map<String, Integer> IDS = new HashMap<>();
    private static int clock = 0, at = 0;
    private static volatile boolean serverBusy = false;
    private static double bx, by, bz;
    private static Vec3 startPos;
    private static float startYaw;

    private DriveAutoTest() {}

    static void run(Minecraft mc) {
        if (STEPS.isEmpty()) build();
        if (serverBusy) return;
        Consumer<Minecraft> step = STEPS.get(++clock);
        if (step != null) step.accept(mc);
    }

    /** Appends a step {@code delay} ticks after the previous one. */
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

    private static final Map<String, Entity> REFS = new HashMap<>();

    private static Entity get(ServerLevel l, String key) {
        return l.getEntity(IDS.getOrDefault(key, -1));
    }

    private static String why(String key) {
        Entity e = REFS.get(key);
        return e == null ? "never spawned" : "removed=" + e.getRemovalReason() + (e instanceof net.minecraft.world.entity.LivingEntity le ? " hp=" + le.getHealth() + " dead=" + le.isDeadOrDying() : "")
                + String.format(" at %.1f,%.1f,%.1f", e.getX(), e.getY(), e.getZ());
    }

    private static <T extends Entity> T spawn(ServerLevel l, String key, EntityType<T> type, double x, double y, double z, float yaw) {
        T e = type.create(l);
        e.moveTo(x, y, z, yaw, 0.0F);
        l.addFreshEntity(e);
        IDS.put(key, e.getId());
        REFS.put(key, e);
        return e;
    }

    private static Entity vehicle(Minecraft mc) {
        return mc.player.getVehicle();
    }

    /** Board {@code key}, hold {@code keys} for {@code ticks}, and run {@code verify} on the client with start pose recorded. */
    private static void drive(String key, int ticks, List<Supplier<KeyMapping>> keys, Consumer<Minecraft> verify) {
        then(10, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.SURVIVAL);
            p.startRiding(get(l, key), true);
        }));
        then(10, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            startPos = vehicle(mc).position();
            startYaw = vehicle(mc).getYRot();
            keys.forEach(k -> k.get().setDown(true));
        });
        then(ticks, mc -> {
            keys.forEach(k -> k.get().setDown(false));
            verify.accept(mc);
        });
    }

    private static double moved(Minecraft mc) {
        Vec3 d = vehicle(mc).position().subtract(startPos);
        return Math.sqrt(d.x * d.x + d.z * d.z);
    }

    private static void build() {
        Supplier<KeyMapping> W = () -> Minecraft.getInstance().options.keyUp;
        Supplier<KeyMapping> A = () -> Minecraft.getInstance().options.keyLeft;
        Supplier<KeyMapping> JUMP = () -> Minecraft.getInstance().options.keyJump;
        Supplier<KeyMapping> DESCEND = () -> com.titancombat.client.KeyInputHandler.KEY_DESCEND;

        then(40, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.CREATIVE);
            l.setDayTime(6000L);
            bx = Math.floor(p.getX()); by = Math.floor(p.getY()); bz = Math.floor(p.getZ());
            ClientAutoTest.tBaseX = bx; ClientAutoTest.tBaseY = by; ClientAutoTest.tBaseZ = bz;
            for (Entity e : l.getAllEntities()) {
                if (e instanceof BaseTransportVehicleEntity || e instanceof com.titancombat.entity.BaseTitanEntity || e instanceof DeckColliderEntity) e.discard();
            }
            // Long runway (land, -X) and open sea (+X) with a beach between
            for (int dx = -150; dx <= 60; dx++) {
                for (int dz = -40; dz <= 40; dz++) {
                    for (int dy = 1; dy <= 25; dy++) l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), Blocks.AIR.defaultBlockState(), 2);
                    boolean sea = dx >= 0;
                    for (int dy = -4; dy <= 0; dy++) {
                        var st = sea ? (dy == -4 ? Blocks.SAND.defaultBlockState() : Blocks.WATER.defaultBlockState())
                                : (dy == 0 ? (dx > -8 ? Blocks.SAND.defaultBlockState() : Blocks.STONE.defaultBlockState()) : Blocks.DIRT.defaultBlockState());
                        l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), st, 2);
                    }
                }
            }
            double g = by + 1.0D;
            spawn(l, "lcac", ModEntities.LCAC_HOVERCRAFT.get(), bx + 30, by + 0.5D, bz, 90.0F); // facing -X, toward the beach
            spawn(l, "repair", ModEntities.REPAIR_TRUCK.get(), bx - 40, g, bz + 20, 90.0F);
            spawn(l, "c130", ModEntities.C130_HERCULES.get(), bx - 20, g, bz - 15, 90.0F);
        }));

        // ---- LCAC: water cruise, turn, then run up onto the beach
        drive("lcac", 60, List.of(W), mc -> check("lcac_water_cruise", moved(mc) > 6, String.format("moved %.1f", moved(mc))));
        drive("lcac", 40, List.of(W, A), mc -> check("lcac_turns", Math.abs(vehicle(mc).getYRot() - startYaw) > 20, String.format("yaw %.0f -> %.0f", startYaw, vehicle(mc).getYRot())));
        then(1, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            spawn(l, "lcac2", ModEntities.LCAC_HOVERCRAFT.get(), bx + 12, by + 0.5D, bz + 10, 90.0F); // 12 blocks out, bow to the beach
        }));
        drive("lcac2", 120, List.of(W), mc -> {
            Entity v = vehicle(mc);
            boolean ashore = v.getX() < bx - 1 && v.getY() >= by + 0.9D;
            check("lcac_drives_onto_beach", ashore, String.format("x=%.1f (shore at %.0f) y=%.2f ground=%.0f", v.getX(), bx, v.getY(), by + 1));
        });

        // ---- repair truck: drive and steer on land
        drive("repair", 60, List.of(W), mc -> check("repair_truck_drives", moved(mc) > 5, String.format("moved %.1f", moved(mc))));
        drive("repair", 40, List.of(W, A), mc -> check("repair_truck_turns", Math.abs(vehicle(mc).getYRot() - startYaw) > 20, String.format("yaw %.0f -> %.0f", startYaw, vehicle(mc).getYRot())));

        // ---- C-130: take-off roll, climb, bank, descend and land
        drive("c130", 140, List.of(W), mc -> check("c130_takeoff_roll", moved(mc) > 30 && vehicle(mc).onGround(), String.format("rolled %.1f", moved(mc))));
        then(1, mc -> {
            startPos = vehicle(mc).position();
            mc.options.keyUp.setDown(true);
            mc.options.keyJump.setDown(true);
        });
        then(40, mc -> {
            mc.options.keyJump.setDown(false);
            double climb = vehicle(mc).getY() - startPos.y;
            check("c130_takes_off", climb > 5, String.format("climbed %.1f", climb));
            startYaw = vehicle(mc).getYRot();
            mc.options.keyLeft.setDown(true);
        });
        then(40, mc -> {
            mc.options.keyLeft.setDown(false);
            mc.options.keyUp.setDown(false);
            check("c130_banks", Math.abs(vehicle(mc).getYRot() - startYaw) > 30, String.format("yaw %.0f -> %.0f", startYaw, vehicle(mc).getYRot()));
            ClientAutoTest.shot(mc, "c130_in_flight");
            // Approach: put the aircraft 12 blocks over the near end of the runway, heading down it
            Entity v = vehicle(mc);
            v.moveTo(bx - 20, by + 13, bz - 15, 90.0F, 0.0F);
            int id = v.getId();
            ClientAutoTest.server2(mc, (p, l) -> l.getEntity(id).moveTo(bx - 20, by + 13, bz - 15, 90.0F, 0.0F)); // server too, or it rejects the jump
            mc.options.keyDown.setDown(true); // throttle back on final
            com.titancombat.client.KeyInputHandler.KEY_DESCEND.setDown(true);
        });
        then(70, mc -> {
            com.titancombat.client.KeyInputHandler.KEY_DESCEND.setDown(false);
            mc.options.keyDown.setDown(false);
            Entity v = vehicle(mc);
            if (v == null) { // the pilot has been seen dropping out on the approach; report it instead of ending the suite
                check("c130_lands", false, "pilot no longer aboard");
                return;
            }
            check("c130_lands", v.onGround() && Math.abs(v.getY() - (by + 1)) < 1.0D && v.isAlive(), String.format("y=%.1f ground=%.0f x=%.0f", v.getY(), by + 1, v.getX() - bx));
        });

        // ---- cargo clamp on every transport: hold position, ride with it, release cleanly
        record Hold(String name, Supplier<EntityType<? extends BaseTransportVehicleEntity>> type, boolean sling, boolean sea) {}
        List<Hold> all = new ArrayList<>(List.of(
                new Hold("hauler_truck", ModEntities.HAULER_TRUCK::get, false, false),
                new Hold("tactical_truck", ModEntities.TACTICAL_TRUCK::get, false, false),
                new Hold("armored_apc", ModEntities.ARMORED_APC::get, false, false),
                new Hold("mobile_suit_trailer", ModEntities.MOBILE_SUIT_TRAILER::get, false, false),
                new Hold("repair_truck", ModEntities.REPAIR_TRUCK::get, false, false),
                new Hold("c130_hercules", ModEntities.C130_HERCULES::get, false, false),
                new Hold("skycrane_drone", ModEntities.SKYCRANE_DRONE::get, true, false),
                new Hold("chinook_transporter", ModEntities.CHINOOK_TRANSPORTER::get, true, false),
                new Hold("v22_osprey", ModEntities.V22_OSPREY::get, true, false),
                new Hold("cargo_barge", ModEntities.CARGO_BARGE::get, false, true),
                new Hold("lcac_hovercraft", ModEntities.LCAC_HOVERCRAFT::get, false, true),
                new Hold("ocean_carrier", ModEntities.OCEAN_CARRIER::get, false, true)));
        then(10, mc -> {
            mc.player.stopRiding();
            server(mc, (p, l) -> {
                p.stopRiding();
                p.teleportTo(l, bx - 15, by + 3, bz, 0, 0); // back inside simulation distance of the lineup
                for (int i = 0; i < all.size(); i++) {
                    Hold h = all.get(i);
                    double x = h.sea() ? bx + 10 + (i - 9) * 14 : bx - 20 - i * 8, y = h.sling() ? by + 15 : (h.sea() ? by + 0.5D : by + 1);
                    var v = spawn(l, h.name(), h.type().get(), x, y, bz + (h.sea() ? 20 : -5), 0.0F);
                    if (h.sling()) v.setNoGravity(true);
                    var titan = spawn(l, h.name() + "_titan", ModEntities.ION_TITAN.get(), x + 3, by + 1, bz - 5, 0.0F);
                    check("clamp_" + h.name(), v.lockCargoToDeck(titan, null) && titan.getVehicle() == v, titan.getVehicle());
                }
            });
        });
        then(20, mc -> server(mc, (p, l) -> {
            for (Hold h : all) {
                var v = get(l, h.name());
                var t = get(l, h.name() + "_titan");
                if (v == null || t == null) {
                    check("held_" + h.name(), false, "vehicle: " + why(h.name()) + " | titan: " + why(h.name() + "_titan"));
                    continue;
                }
                double horiz = Math.hypot(t.getX() - v.getX(), t.getZ() - v.getZ());
                boolean placed = h.sling() ? t.getY() + t.getBbHeight() <= v.getY() + 0.1D : t.getY() >= v.getY() - 0.1D;
                boolean moved = Math.abs(t.getX() - (v.getX() + 3)) > 0.3D || Math.abs(t.getZ() - (bz - 5)) > 0.3D; // left its spawn spot
                check("held_" + h.name(), t.getVehicle() == v && placed && moved && horiz < Math.max(4.0D, v.getBbWidth()),
                        String.format("titanY=%.2f vehicleY=%.2f top=%.2f horiz=%.1f", t.getY(), v.getY(), t.getY() + t.getBbHeight(), horiz));
                IDS.put(h.name() + "_dz", (int) ((t.getZ() - v.getZ()) * 100));
                v.setDeltaMovement(Vec3.ZERO);
                v.moveTo(v.getX() + 3.0D, v.getY(), v.getZ(), v.getYRot(), 0.0F); // the load must follow the vehicle
            }
        }));
        then(5, mc -> server(mc, (p, l) -> {
            for (Hold h : all) {
                var v = get(l, h.name());
                var t = get(l, h.name() + "_titan");
                if (v == null || t == null) continue;
                check("follows_" + h.name(), Math.abs((t.getX() - v.getX()) - 0.0D) < 16 && t.getVehicle() == v, String.format("dx=%.2f", t.getX() - v.getX()));
                ((BaseTransportVehicleEntity) v).releaseMountedTitans(null);
                check("release_" + h.name(), !t.isPassenger() && !((BaseTransportVehicleEntity) v).hasCargo(), t.getVehicle());
            }
        }));
        then(10, mc -> {
            ClientAutoTest.aimCameraAt(mc, bx - 90, by + 2, bz - 5, 40, 25, 180);
        });
        then(20, mc -> ClientAutoTest.shot(mc, "cargo_released_lineup"));

        // ---- Obsolete Exoframe: Shift-dismount beside a Chinook docks the Exoframe onto it
        then(10, mc -> server(mc, (p, l) -> {
            EntityType<?> exoType = BuiltInRegistries.ENTITY_TYPE.get(new ResourceLocation("obsolete", "exoframe"));
            boolean loaded = BuiltInRegistries.ENTITY_TYPE.containsKey(new ResourceLocation("obsolete", "exoframe"));
            check("obsolete_loaded", loaded, exoType);
            if (!loaded) return;
            p.setGameMode(GameType.SURVIVAL);
            var heli = spawn(l, "exo_heli", ModEntities.CHINOOK_TRANSPORTER.get(), bx - 60, by + 1, bz + 25, 0.0F);
            Entity exo = exoType.create(l);
            exo.moveTo(bx - 60, by + 1, bz + 31, 180.0F, 0.0F);
            l.addFreshEntity(exo);
            IDS.put("exo", exo.getId());
            p.startRiding(exo, true);
        }));
        then(20, mc -> mc.options.keyShift.setDown(true)); // the real input: pilot holds Shift to hop out
        then(6, mc -> mc.options.keyShift.setDown(false));
        then(10, mc -> server(mc, (p, l) -> {
            var exo = get(l, "exo");
            if (exo == null) return;
            check("pilot_left_exo", p.getVehicle() == null, p.getVehicle());
            check("exo_docked_to_chinook", exo.getVehicle() == get(l, "exo_heli"), exo.getVehicle());
        }));
        then(5, mc -> ClientAutoTest.aimCameraAt(mc, bx - 60, by + 2, bz + 25, 14, 15, 120));
        then(20, mc -> ClientAutoTest.shot(mc, "exo_on_chinook_sling"));

        // ---- Exo dock is deliberate: holding the wrench, or looking away, Shift just gets the pilot out
        Consumer<Minecraft> boardFreshExo = mc -> server(mc, (p, l) -> {
            EntityType<?> exoType = BuiltInRegistries.ENTITY_TYPE.get(new ResourceLocation("obsolete", "exoframe"));
            if (!BuiltInRegistries.ENTITY_TYPE.containsKey(new ResourceLocation("obsolete", "exoframe"))) return;
            p.stopRiding();
            var apc = spawn(l, "dock_apc", ModEntities.ARMORED_APC.get(), bx - 40, by + 1, bz + 25, 0.0F);
            Entity exo = exoType.create(l);
            exo.moveTo(bx - 40, by + 1, bz + 29, 180.0F, 0.0F);
            l.addFreshEntity(exo);
            IDS.put("exo2", exo.getId());
            p.startRiding(exo, true);
        });
        then(10, boardFreshExo);
        then(10, mc -> {
            mc.player.setYRot(0.0F); // facing +Z, away from the APC at -Z
            mc.player.setXRot(0.0F);
            mc.options.keyShift.setDown(true);
        });
        then(6, mc -> mc.options.keyShift.setDown(false));
        then(10, mc -> server(mc, (p, l) -> {
            var exo = get(l, "exo2");
            if (exo != null) check("no_dock_when_looking_away", exo.getVehicle() == null && p.getVehicle() == null, exo.getVehicle());
            if (exo != null) exo.discard();
        }));
        then(10, boardFreshExo);
        then(10, mc -> server(mc, (p, l) -> {
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new net.minecraft.world.item.ItemStack(com.titancombat.item.ModItems.VEHICLE_WRENCH.get()));
        }));
        then(5, mc -> {
            mc.player.setYRot(180.0F); // looking straight at the APC
            mc.player.setXRot(15.0F);
            mc.options.keyShift.setDown(true);
        });
        then(6, mc -> mc.options.keyShift.setDown(false));
        then(10, mc -> server(mc, (p, l) -> {
            var exo = get(l, "exo2");
            if (exo != null) check("no_dock_when_holding_wrench", exo.getVehicle() == null && p.getVehicle() == null, exo.getVehicle());
            if (exo != null) exo.discard();
        }));
        // ---- Wrench on foot: Shift + right-click packs the vehicle into the inventory, never boards it
        then(5, mc -> server(mc, (p, l) -> {
            var apc = get(l, "dock_apc");
            p.stopRiding();
            p.getInventory().clearContent();
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new net.minecraft.world.item.ItemStack(com.titancombat.item.ModItems.VEHICLE_WRENCH.get()));
            p.teleportTo(l, apc.getX(), apc.getY(), apc.getZ() + 3.0D, 180.0F, 10.0F);
            p.setShiftKeyDown(true);
            p.interactOn(apc, net.minecraft.world.InteractionHand.MAIN_HAND); // the same call a real right-click makes
            p.setShiftKeyDown(false);
            boolean packed = p.getInventory().contains(new net.minecraft.world.item.ItemStack(com.titancombat.item.ModItems.ARMORED_APC.get()));
            check("wrench_packs_vehicle", packed && !apc.isAlive() && p.getVehicle() == null, "packed=" + packed + " alive=" + apc.isAlive() + " riding=" + p.getVehicle());
        }));
        then(10, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] Completed drive test suite");
            mc.stop();
        });
    }
}
