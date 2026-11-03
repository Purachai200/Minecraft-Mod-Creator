package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.transport.*;
import com.titancombat.item.ModItems;
import com.titancombat.network.ModNetworking;
import com.titancombat.network.TitanWeaponActionC2SPacket;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

/**
 * Scripted check of the fleet expansion (TITAN_AUTOTEST=fleet): assembly bay, component damage and crash,
 * repair truck, C-130 airdrop, LCAC hover, walkable carrier deck with aircraft landing/charging, camo, sounds,
 * plus promo screenshots. Logs "[autotest] CHECK <name> ... : PASS|FAIL".
 */
final class FleetAutoTest {
    private static final Map<Integer, Consumer<Minecraft>> STEPS = new HashMap<>();
    private static final Map<String, Integer> IDS = new HashMap<>();
    private static double bx, by, bz;
    private static float before;

    private FleetAutoTest() {}

    /** Own clock that pauses while the integrated server is still busy with a step (arena building lags it by seconds). */
    private static int clock = 0;
    private static volatile boolean serverBusy = false;

    static void run(Minecraft mc, int ignoredTick) {
        if (STEPS.isEmpty()) build();
        if (serverBusy) return;
        int tick = ++clock;
        Consumer<Minecraft> step = STEPS.get(tick);
        if (step != null) step.accept(mc);
    }

    private static void at(int tick, Consumer<Minecraft> action) {
        STEPS.put(tick, action);
    }

    private static void check(String name, boolean pass, Object detail) {
        TitanCombatMod.LOGGER.info("[autotest] CHECK {} {} : {}", name, detail, pass ? "PASS" : "FAIL");
    }

    @SuppressWarnings("unchecked")
    private static <T extends Entity> T spawn(net.minecraft.server.level.ServerLevel l, String key, EntityType<T> type, double x, double y, double z, float yaw) {
        T e = type.create(l);
        e.moveTo(x, y, z, yaw, 0.0F);
        l.addFreshEntity(e);
        IDS.put(key, e.getId());
        return e;
    }

    private static Entity get(net.minecraft.server.level.ServerLevel l, String key) {
        return l.getEntity(IDS.getOrDefault(key, -1));
    }

    /** Runs on the server thread; the script clock waits until it has run so later steps see its results. */
    private static void server(Minecraft mc, java.util.function.BiConsumer<net.minecraft.server.level.ServerPlayer, net.minecraft.server.level.ServerLevel> a) {
        serverBusy = true;
        ClientAutoTest.server2(mc, (p, l) -> {
            try {
                a.accept(p, l);
            } finally {
                serverBusy = false;
            }
        });
    }

    /** Camera offset from a live entity, looking at it. */
    private static void promoOn(int tick, String name, String key, double cx, double cy, double cz, double ty) {
        at(tick, mc -> {
            Entity e = mc.level.getEntity(IDS.getOrDefault(key, -1));
            if (e == null) return;
            double dx = -cx, dy = ty - cy, dz = -cz;
            float yaw = (float) Math.toDegrees(Math.atan2(dz, dx)) - 90.0F;
            float pitch = (float) -Math.toDegrees(Math.atan2(dy - 1.62D, Math.sqrt(dx * dx + dz * dz)));
            ClientAutoTest.setCamPos(mc, e.getX() + cx, e.getY() + cy, e.getZ() + cz, yaw, pitch);
        });
        at(tick + 20, mc -> ClientAutoTest.shot(mc, name));
    }

    private static void cam(Minecraft mc, double dx, double dy, double dz, double dist, double elev, double az) {
        ClientAutoTest.aimCameraAt(mc, bx + dx, by + dy, bz + dz, dist, elev, az);
    }

    /** Places the spectator camera at base+(cx,cy,cz) looking at base+(tx,ty,tz), then shoots 20 ticks later (chunks and pose settle). */
    private static void promo(int tick, String name, double cx, double cy, double cz, double tx, double ty, double tz) {
        at(tick, mc -> {
            double dx = tx - cx, dy = ty - cy, dz = tz - cz;
            float yaw = (float) Math.toDegrees(Math.atan2(dz, dx)) - 90.0F;
            float pitch = (float) -Math.toDegrees(Math.atan2(dy - 1.62D, Math.sqrt(dx * dx + dz * dz)));
            ClientAutoTest.setCamPos(mc, bx + cx, by + cy, bz + cz, yaw, pitch);
        });
        at(tick + 20, mc -> ClientAutoTest.shot(mc, name));
    }

    private static void build() {
        // ---- arena: sea on +X, beach and land on -X
        at(40, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.CREATIVE);
            l.setWeatherParameters(60000, 0, false, false);
            l.setDayTime(9000L); // afternoon light for promo shots
            bx = Math.floor(p.getX()); by = Math.floor(p.getY()); bz = Math.floor(p.getZ());
            ClientAutoTest.tBaseX = bx; ClientAutoTest.tBaseY = by; ClientAutoTest.tBaseZ = bz;
            for (Entity e : l.getAllEntities()) {
                if (e instanceof BaseTransportVehicleEntity || e instanceof com.titancombat.entity.BaseTitanEntity || e instanceof DeckColliderEntity) e.discard();
            }
            for (int dx = -60; dx <= 60; dx++) {
                for (int dz = -60; dz <= 60; dz++) {
                    for (int dy = 1; dy <= 30; dy++) l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), Blocks.AIR.defaultBlockState(), 2);
                    boolean sea = dx >= 4;
                    for (int dy = -6; dy <= 0; dy++) {
                        var st = sea ? (dy == -6 ? Blocks.SAND.defaultBlockState() : Blocks.WATER.defaultBlockState())
                                : (dy == 0 ? (dx > -6 ? Blocks.SAND.defaultBlockState() : Blocks.GRASS_BLOCK.defaultBlockState()) : Blocks.DIRT.defaultBlockState());
                        l.setBlock(new BlockPos((int) bx + dx, (int) by + dy, (int) bz + dz), st, 2);
                    }
                }
            }
            double g = by + 1.0D;
            spawn(l, "carrier", ModEntities.OCEAN_CARRIER.get(), bx + 34, by - 1.0D, bz, 0.0F);
            spawn(l, "lcac", ModEntities.LCAC_HOVERCRAFT.get(), bx + 12, by + 0.5D, bz - 18, 90.0F);
            spawn(l, "c130", ModEntities.C130_HERCULES.get(), bx - 30, g, bz + 20, 270.0F);
            spawn(l, "repair", ModEntities.REPAIR_TRUCK.get(), bx - 14, g, bz - 14, 200.0F);
            spawn(l, "apc", ModEntities.ARMORED_APC.get(), bx - 18, g, bz - 6, 150.0F);
            spawn(l, "chinook", ModEntities.CHINOOK_TRANSPORTER.get(), bx - 20, g, bz - 30, 30.0F);
            l.setBlock(new BlockPos((int) bx - 6, (int) by + 1, (int) bz + 2), com.titancombat.block.ModBlocks.VEHICLE_ASSEMBLY_BAY.get().defaultBlockState(), 3);
        }));
        at(55, mc -> server(mc, (p, l) -> {
            // Earlier runs' vehicles reload with their chunks after the first sweep; sweep again (keep this run's)
            for (Entity e : l.getAllEntities()) {
                if ((e instanceof BaseTransportVehicleEntity || e instanceof com.titancombat.entity.BaseTitanEntity) && !IDS.containsValue(e.getId())) e.discard();
            }
        }));
        at(60, mc -> {
            mc.options.hideGui = true;
            mc.options.cloudStatus().set(net.minecraft.client.CloudStatus.OFF); // cloud layer sits at y 192 and fogs high cameras
            server(mc, (p, l) -> p.setGameMode(GameType.SPECTATOR));
        });

        // ---- promo: fleet overview and each new vehicle (camera given as world offset from the arena base + look target)
        promo(80, "p01_fleet_overview", -30, 22, -40, 10, 2, 0);
        promoOn(105, "p02_carrier", "carrier", -30, 18, -26, 3);
        promoOn(130, "p03_lcac", "lcac", -10, 6, -10, 1);
        promo(155, "p04_c130", -42, 9, 36, -30, 3, 20);
        promo(180, "p05_repair_truck", -24, 5, -22, -14, 1.5, -14);

        // ---- carrier deck: walk on it, land an Osprey, charge it
        at(205, mc -> server(mc, (p, l) -> {
            var carrier = (TitanOceanCarrierEntity) get(l, "carrier");
            long tiles = l.getEntitiesOfClass(DeckColliderEntity.class, carrier.getBoundingBox().inflate(40), t -> t.getParent() == carrier).size();
            check("carrier_deck_tiles", tiles == 8, tiles + " (4 deck + 4 island)");
            p.setGameMode(GameType.SURVIVAL);
            p.teleportTo(l, carrier.getX(), carrier.getY() + TitanOceanCarrierEntity.DECK_TOP_Y + 2.0D, carrier.getZ() - 6.0D, 0, 0);
            var osprey = spawn(l, "osprey", ModEntities.V22_OSPREY.get(), carrier.getX() - 2.75D, carrier.getY() + TitanOceanCarrierEntity.DECK_TOP_Y + 6.0D, carrier.getZ() + 10.75D, 0.0F);
            osprey.setEnergy(10000);
        }));
        at(240, mc -> server(mc, (p, l) -> {
            var carrier = get(l, "carrier");
            double deck = carrier.getY() + TitanOceanCarrierEntity.DECK_TOP_Y;
            check("player_stands_on_deck", Math.abs(p.getY() - deck) < 0.6D, String.format("playerY=%.2f deck=%.2f", p.getY(), deck));
            p.setGameMode(GameType.SPECTATOR);
        }));
        promo(242, "p06_osprey_on_carrier_deck", 22, 16, -18, 34, 5, 2);

        // ---- component damage: fly the Chinook, shoot its rotors off mid-air, watch it fall
        at(270, mc -> server(mc, (p, l) -> {
            var heli = (BaseTransportVehicleEntity) get(l, "chinook");
            heli.moveTo(heli.getX(), by + 20, heli.getZ());
            p.setGameMode(GameType.SURVIVAL);
            p.startRiding(heli, true);
            var apc = (BaseTransportVehicleEntity) get(l, "apc");
            apc.hurt(l.damageSources().explosion(null, null), 300.0F);
            check("apc_running_gear_damaged", apc.getPropulsionDamage() > 0.3F, apc.getPropulsionDamage());
        }));
        at(280, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK));
        at(281, mc -> mc.options.keyJump.setDown(true)); // hold the hover while the rotors still work
        at(300, mc -> {
            mc.options.keyJump.setDown(false);
            before = (float) mc.player.getVehicle().getY();
            server(mc, (p, l) -> {
                var heli = (BaseTransportVehicleEntity) get(l, "chinook");
                heli.hurt(l.damageSources().explosion(null, null), 200.0F);
                check("rotors_destroyed_by_blast", heli.isPropulsionDestroyed(), heli.getPropulsionDamage());
            });
        });
        at(322, mc -> {
            var v = (BaseTransportVehicleEntity) mc.player.getVehicle();
            check("client_sees_rotors_destroyed", v != null && v.isPropulsionDestroyed(), v == null ? "no vehicle" : v.getPropulsionDamage());
            ClientAutoTest.shot(mc, "d01_chinook_rotors_shot_off");
        });
        at(334, mc -> {
            float y = mc.player.getVehicle() == null ? Float.NaN : (float) mc.player.getVehicle().getY();
            check("wreck_falls", before - y > 3, before + " -> " + y);
        });

        // ---- repair truck: park next to the damaged APC with a driver aboard
        at(336, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.setGameMode(GameType.CREATIVE); // keep the test pilot alive through the wreck's impact blast
            p.setHealth(p.getMaxHealth());
            var osprey = (BaseTransportVehicleEntity) get(l, "osprey");
            double deck = get(l, "carrier").getY() + TitanOceanCarrierEntity.DECK_TOP_Y;
            check("osprey_landed_on_deck", Math.abs(osprey.getY() - deck) < 0.6D && osprey.onGround(), String.format("ospreyY=%.2f deck=%.2f", osprey.getY(), deck));
            check("deck_charges_aircraft", osprey.getEnergy() > 10000, osprey.getEnergy());
        }));
        at(342, mc -> server(mc, (p, l) -> {
            var truck = get(l, "repair");
            var apc = get(l, "apc");
            apc.moveTo(truck.getX() + 5, truck.getY(), truck.getZ(), apc.getYRot(), 0);
            before = ((BaseTransportVehicleEntity) apc).getPropulsionDamage();
            p.startRiding(truck, true);
        }));
        at(420, mc -> server(mc, (p, l) -> {
            var truck = (TitanRepairTruckEntity) get(l, "repair");
            var apc = (BaseTransportVehicleEntity) get(l, "apc");
            check("repair_truck_deploys", truck.isRepairing(), truck.isRepairing());
            check("repair_truck_fixes_apc", apc.getPropulsionDamage() < before, before + " -> " + apc.getPropulsionDamage());
        }));
        at(425, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            ClientAutoTest.shot(mc, "p07_repair_truck_working");
        });

        // ---- C-130 airdrop: load a Titan, fly high, release over the field
        at(440, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            var c130 = (TitanC130HerculesEntity) get(l, "c130");
            var titan = spawn(l, "droptitan", ModEntities.ION_TITAN.get(), c130.getX(), c130.getY(), c130.getZ(), 0);
            c130.lockCargoToDeck(titan, null);
            c130.moveTo(bx - 20, by + 30, bz, 270, 0);
            c130.setNoGravity(true);
            p.setGameMode(GameType.SURVIVAL);
            p.startRiding(c130, true);
        }));
        at(450, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELEASE_CARGO)));
        at(456, mc -> server(mc, (p, l) -> {
            var titan = get(l, "droptitan");
            var c130 = (BaseTransportVehicleEntity) get(l, "c130");
            check("c130_airdrop_released", titan != null && !titan.isPassenger(), titan == null ? "gone" : titan.getVehicle());
            check("c130_ramp_open", c130.isRampOpen(), c130.isRampOpen());
            IDS.put("hp", (int) ((net.minecraft.world.entity.LivingEntity) titan).getHealth());
            p.stopRiding();
            p.setGameMode(GameType.SPECTATOR);
        }));
        promoOn(458, "p08_c130_airdrop", "droptitan", 10, 4, -10, 2);
        at(640, mc -> server(mc, (p, l) -> {
            var titan = (net.minecraft.world.entity.LivingEntity) get(l, "droptitan");
            check("airdrop_lands_safely", titan.onGround() && titan.getHealth() >= IDS.get("hp"), String.format("y=%.1f hp=%.0f", titan.getY(), titan.getHealth()));
        }));

        // ---- LCAC: floats on the cushion over water
        at(650, mc -> server(mc, (p, l) -> {
            var lcac = get(l, "lcac");
            check("lcac_floats", lcac.getY() > by - 0.6D && lcac.getY() < by + 1.6D, String.format("y=%.2f water=%.0f", lcac.getY(), by + 1));
        }));

        // ---- camo layers and assembly bay
        at(660, mc -> server(mc, (p, l) -> {
            int i = 1;
            for (String k : new String[]{"lcac", "c130", "repair", "apc"}) {
                if (get(l, k) instanceof BaseTransportVehicleEntity v) v.setCamo(i++);
            }
            p.getInventory().clearContent();
            p.setGameMode(GameType.SURVIVAL);
            p.teleportTo(l, bx - 5, by + 1, bz + 4, 0, 0);
            p.getInventory().add(new ItemStack(ModItems.CHASSIS_FRAME.get(), 1));
            p.getInventory().add(new ItemStack(ModItems.COCKPIT_MODULE.get(), 1));
            p.getInventory().add(new ItemStack(ModItems.WEAPON_MOUNT.get(), 1));
            p.getInventory().add(new ItemStack(net.minecraft.world.item.Items.IRON_BLOCK, 3));
        }));
        at(670, mc -> ModNetworking.sendToServer(new com.titancombat.assembly.AssembleVehicleC2SPacket(new BlockPos((int) bx - 6, (int) by + 1, (int) bz + 2), 0)));
        at(680, mc -> server(mc, (p, l) -> {
            boolean got = p.getInventory().contains(new ItemStack(ModItems.TACTICAL_TRUCK.get()));
            boolean spent = !p.getInventory().contains(new ItemStack(ModItems.CHASSIS_FRAME.get()));
            check("assembly_bay_builds_truck", got && spent, "got=" + got + " partsSpent=" + spent);
            p.setGameMode(GameType.SPECTATOR);
        }));
        promoOn(683, "p09_camo_patterns", "repair", 10, 6, -12, 1);
        at(705, mc -> {
            mc.options.hideGui = false;
            mc.setScreen(null);
            com.titancombat.client.gui.VehicleAssemblyScreen.open(new BlockPos((int) bx - 6, (int) by + 1, (int) bz + 2));
        });
        at(715, mc -> ClientAutoTest.shot(mc, "p10_assembly_bay_ui"));

        // ---- engine sounds: at least one vehicle loop is playing while driven
        at(720, mc -> {
            mc.setScreen(null);
            server(mc, (p, l) -> {
                p.setGameMode(GameType.SURVIVAL);
                p.startRiding(get(l, "lcac"), true);
            });
        });
        at(780, mc -> {
            boolean playing = com.titancombat.client.VehicleEngineSound.anyPlaying();
            check("engine_loop_playing", playing, playing);
        });
        at(800, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] Completed fleet test suite");
            mc.stop();
        });
    }
}
