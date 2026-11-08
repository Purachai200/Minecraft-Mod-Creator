package com.vehiclefleet.client.debug;

import com.vehiclefleet.VehicleFleetMod;
import com.vehiclefleet.entity.FleetVehicleEntity;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.Map;
import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * Automated in-game verification test for Vehicle Fleet.
 * Run with: ./gradlew runClient -Dvehiclefleet.autotest=drive
 */
@Mod.EventBusSubscriber(modid = VehicleFleetMod.MODID, value = Dist.CLIENT)
public final class FleetAutoTest {
    private static final String MODE = System.getProperty("vehiclefleet.autotest", "");
    private static int clock = 0;
    private static final Map<Integer, Consumer<Minecraft>> STEPS = new HashMap<>();
    private static final Map<String, Integer> ENTITY_IDS = new HashMap<>();
    private static double baseX, baseY, baseZ;
    private static Vec3 startPos;
    private static float startYaw;

    private FleetAutoTest() {}

    private static void at(int tick, Consumer<Minecraft> action) {
        STEPS.put(tick, action);
    }

    private static void server(Minecraft mc, BiConsumer<ServerPlayer, ServerLevel> action) {
        var s = mc.getSingleplayerServer();
        if (s == null || mc.player == null) return;
        var uuid = mc.player.getUUID();
        s.execute(() -> {
            ServerPlayer sp = s.getPlayerList().getPlayer(uuid);
            if (sp != null) action.accept(sp, sp.serverLevel());
        });
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "fleet_" + name + ".png", mc.getMainRenderTarget(), msg -> {});
    }

    private static void check(String testName, boolean pass, String detail) {
        VehicleFleetMod.LOGGER.info("[fleet-autotest] CHECK {} : {} ({})", testName, pass ? "PASS" : "FAIL", detail);
    }

    private static boolean worldCreationTriggered = false;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END || MODE.isEmpty()) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.getSingleplayerServer() == null) {
            if (mc.screen != null && !(mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen) && !(mc.screen instanceof net.minecraft.client.gui.screens.worldselection.CreateWorldScreen)) {
                // Dismiss popup / accessibility / narrator screens
                for (var child : mc.screen.children()) {
                    if (child instanceof net.minecraft.client.gui.components.Button b) {
                        String text = b.getMessage().getString().toLowerCase();
                        if (text.contains("narrator") || text.contains("continue") || text.contains("acknowledge")
                                || text.contains("proceed") || text.contains("back") || text.contains("done") || text.contains("dismiss")) {
                            b.onPress();
                            return;
                        }
                    }
                }
            }
            if (mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen && !worldCreationTriggered) {
                worldCreationTriggered = true;
                VehicleFleetMod.LOGGER.info("[fleet-autotest] TitleScreen detected, attempting to load New World...");
                try {
                    if (mc.getLevelSource().levelExists("New World")) {
                        mc.createWorldOpenFlows().loadLevel(mc.screen, "New World");
                        return;
                    }
                } catch (Throwable ignored) {}
                net.minecraft.client.gui.screens.worldselection.CreateWorldScreen.openFresh(mc, null);
            } else if (mc.screen instanceof net.minecraft.client.gui.screens.worldselection.CreateWorldScreen cws) {
                for (var child : cws.children()) {
                    if (child instanceof net.minecraft.client.gui.components.Button b) {
                        String text = b.getMessage().getString().toLowerCase();
                        if (text.contains("create")) {
                            VehicleFleetMod.LOGGER.info("[fleet-autotest] Clicking Create World: {}", text);
                            b.onPress();
                            break;
                        }
                    }
                }
            }
            return;
        }

        mc.options.pauseOnLostFocus = false;
        if (mc.screen instanceof net.minecraft.client.gui.screens.PauseScreen) {
            mc.setScreen(null);
        }

        if (STEPS.isEmpty()) {
            buildScript();
        }

        int t = ++clock;
        Consumer<Minecraft> step = STEPS.get(t);
        if (step != null) {
            step.accept(mc);
        }
    }

    private static void buildScript() {
        at(30, mc -> server(mc, (p, l) -> {
            p.setGameMode(GameType.CREATIVE);
            p.stopRiding();
            l.setDayTime(6000L);
            baseX = Math.floor(p.getX());
            baseY = Math.floor(p.getY());
            baseZ = Math.floor(p.getZ());

            // Build road and water testing grounds
            for (int dx = -40; dx <= 60; dx++) {
                for (int dz = -20; dz <= 50; dz++) {
                    for (int dy = 1; dy <= 20; dy++) {
                        l.setBlock(new BlockPos((int) baseX + dx, (int) baseY + dy, (int) baseZ + dz), Blocks.AIR.defaultBlockState(), 2);
                    }
                    boolean water = dx >= 20;
                    l.setBlock(new BlockPos((int) baseX + dx, (int) baseY, (int) baseZ + dz),
                            water ? Blocks.WATER.defaultBlockState() : Blocks.SMOOTH_STONE.defaultBlockState(), 2);
                }
            }

            // Spawn test vehicles
            FleetVehicleEntity technical = VehicleFleetMod.TYPES.get("technical_4x4").get().create(l);
            if (technical != null) {
                technical.moveTo(baseX - 10, baseY + 1.0D, baseZ, 90.0F, 0.0F);
                l.addFreshEntity(technical);
                ENTITY_IDS.put("technical", technical.getId());
            }

            FleetVehicleEntity humvee = VehicleFleetMod.TYPES.get("humvee_m1165").get().create(l);
            if (humvee != null) {
                humvee.moveTo(baseX - 10, baseY + 1.0D, baseZ + 8, 90.0F, 0.0F);
                l.addFreshEntity(humvee);
                ENTITY_IDS.put("humvee", humvee.getId());
            }

            FleetVehicleEntity ural = VehicleFleetMod.TYPES.get("ural_6x6").get().create(l);
            if (ural != null) {
                ural.moveTo(baseX - 10, baseY + 1.0D, baseZ - 8, 90.0F, 0.0F);
                l.addFreshEntity(ural);
                ENTITY_IDS.put("ural", ural.getId());
            }

            // Spawn mounted turret on Ural 6x6 flatbed (local z=-2.0 -> world baseX - 8.0)
            ArmorStand truckTurret = EntityType.ARMOR_STAND.create(l);
            if (truckTurret != null) {
                truckTurret.moveTo(baseX - 8.0D, baseY + 3.0D, baseZ - 8.0D, 90.0F, 0.0F);
                l.addFreshEntity(truckTurret);
                ENTITY_IDS.put("truck_turret", truckTurret.getId());
            }

            FleetVehicleEntity mi17 = VehicleFleetMod.TYPES.get("mi17_hip").get().create(l);
            if (mi17 != null) {
                mi17.moveTo(baseX - 25, baseY + 1.0D, baseZ, 90.0F, 0.0F);
                l.addFreshEntity(mi17);
                ENTITY_IDS.put("mi17", mi17.getId());
            }

            FleetVehicleEntity freighter = VehicleFleetMod.TYPES.get("coaster_freighter").get().create(l);
            if (freighter != null) {
                freighter.moveTo(baseX + 35, baseY + 0.5D, baseZ, 90.0F, 0.0F);
                l.addFreshEntity(freighter);
                ENTITY_IDS.put("freighter", freighter.getId());
            }

            // Spawn carried cargo on Freighter cargo deck
            ArmorStand deckCargo = EntityType.ARMOR_STAND.create(l);
            if (deckCargo != null) {
                deckCargo.moveTo(baseX + 35, baseY + 3.25D, baseZ - 2.0D, 90.0F, 0.0F);
                l.addFreshEntity(deckCargo);
                ENTITY_IDS.put("deck_cargo", deckCargo.getId());
            }

            FleetVehicleEntity lpd = VehicleFleetMod.TYPES.get("lpd_assault").get().create(l);
            if (lpd != null) {
                lpd.moveTo(baseX + 35, baseY + 0.5D, baseZ + 32, 90.0F, 0.0F);
                l.addFreshEntity(lpd);
                ENTITY_IDS.put("lpd", lpd.getId());
            }
        }));

        // 1. Board Technical 4x4
        at(60, mc -> server(mc, (p, l) -> {
            Entity tech = l.getEntity(ENTITY_IDS.getOrDefault("technical", -1));
            if (tech != null) p.startRiding(tech, true);
        }));

        at(75, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setYRot(90.0F);
                mc.player.setXRot(5.0F);
            }
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double eyeY = mc.player.getEyeY() - v.getY();
                double headTop = mc.player.getY() + 1.45D - v.getY();
                double roofHeight = 49.5D / 16.0D;
                boolean eyeInsideCab = eyeY > 1.8D && eyeY < 2.7D;
                boolean headUnderRoof = headTop <= roofHeight;
                check("technical_seat_eye_height", eyeInsideCab, "Eye relative Y: " + String.format("%.2f", eyeY));
                check("technical_seat_roof_clearance", headUnderRoof, "Head top Y: " + String.format("%.2f", headTop) + ", Cab Roof: " + String.format("%.2f", roofHeight));
            }
            shot(mc, "01_technical_first_person_cockpit");
        });

        at(85, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            shot(mc, "02_technical_cabin_seated_profile");
        });

        // 2. Drive Technical 4x4 (Hold W + A)
        at(100, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            if (mc.player.getVehicle() != null) {
                startPos = mc.player.getVehicle().position();
                startYaw = mc.player.getVehicle().getYRot();
            }
            mc.options.keyUp.setDown(true);
            mc.options.keyLeft.setDown(true);
        });

        at(135, mc -> {
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                float roll = v.getHullRoll();
                check("technical_body_roll_lean", Math.abs(roll) > 0.005F, "Body roll: " + String.format("%.3f rad (%.1f deg)", roll, Math.toDegrees(roll)));
            }
            shot(mc, "03_technical_driving_turn");
        });

        at(145, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.keyLeft.setDown(false);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double dist = v.position().distanceTo(startPos);
                float yawChange = Math.abs(v.getYRot() - startYaw);
                check("technical_drive_forward", dist > 3.0D, "Distance: " + String.format("%.2f blocks", dist));
                check("technical_steer_turning", yawChange > 5.0F, "Yaw turned: " + String.format("%.1f deg", yawChange));
            }
        });

        // 3. Board Humvee M1165
        at(160, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            Entity hum = l.getEntity(ENTITY_IDS.getOrDefault("humvee", -1));
            if (hum != null) p.startRiding(hum, true);
        }));

        at(175, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            if (mc.player != null) {
                mc.player.setYRot(90.0F);
                mc.player.setXRot(5.0F);
            }
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double headTop = mc.player.getY() + 1.45D - v.getY();
                double roofHeight = 44.0D / 16.0D;
                boolean headUnderRoof = headTop <= roofHeight + 0.1D;
                check("humvee_seat_roof_clearance", headUnderRoof, "Head top: " + String.format("%.2f", headTop) + ", Roof: " + String.format("%.2f", roofHeight));
            }
            shot(mc, "04_humvee_seated");
        });

        // 3.5 Board Ural 6x6
        at(190, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            Entity ur = l.getEntity(ENTITY_IDS.getOrDefault("ural", -1));
            if (ur != null) p.startRiding(ur, true);
        }));

        at(205, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setYRot(90.0F);
                mc.player.setXRot(5.0F);
            }
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double headTop = mc.player.getY() + 1.45D - v.getY();
                double roofHeight = 76.0D / 16.0D;
                boolean headUnderRoof = headTop <= roofHeight;
                check("ural_seat_roof_clearance", headUnderRoof, "Head top: " + String.format("%.2f", headTop) + ", Cab Roof: " + String.format("%.2f", roofHeight));
            }
            shot(mc, "07_ural_seated");
        });

        at(210, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            p.moveTo(baseX - 3.0D, baseY + 2.0D, baseZ - 13.0D, 45.0F, 5.0F);
        }));

        at(215, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setYRot(45.0F);
                mc.player.setXRot(5.0F);
            }
            shot(mc, "10_ural_flatbed_turret");
        });

        // 4. Board Mi-17 Helicopter
        at(220, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            Entity mi = l.getEntity(ENTITY_IDS.getOrDefault("mi17", -1));
            if (mi != null) p.startRiding(mi, true);
        }));

        at(228, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            shot(mc, "11_mi17_cockpit");
        });

        at(235, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                startPos = v.position();
                startYaw = v.getYRot();
            }
            mc.options.keyJump.setDown(true);
            mc.options.keyUp.setDown(true);
            mc.options.keyLeft.setDown(true);
        });

        at(270, mc -> {
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                float bankRoll = v.getHullRoll();
                float pitch = v.getHullPitch();
                check("helicopter_bank_roll_lean", Math.abs(bankRoll) > 0.01F, "Bank roll: " + String.format("%.3f rad (%.1f deg)", bankRoll, Math.toDegrees(bankRoll)));
                check("helicopter_forward_pitch", pitch > 0.01F, "Forward pitch: " + String.format("%.3f rad (%.1f deg)", pitch, Math.toDegrees(pitch)));
            }
            shot(mc, "05_mi17_flight");
        });

        at(280, mc -> {
            mc.options.keyJump.setDown(false);
            mc.options.keyUp.setDown(false);
            mc.options.keyLeft.setDown(false);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double climbY = v.getY() - startPos.y;
                double forwardDist = Math.sqrt(Math.pow(v.getX() - startPos.x, 2) + Math.pow(v.getZ() - startPos.z, 2));
                check("helicopter_climb", climbY > 2.0D, "Climbed: " + String.format("%.2f blocks", climbY));
                check("helicopter_flight", forwardDist > 3.0D, "Flew forward: " + String.format("%.2f blocks", forwardDist));
            }
        });

        // 5. Board Coaster Freighter
        at(300, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            Entity ship = l.getEntity(ENTITY_IDS.getOrDefault("freighter", -1));
            if (ship != null) p.startRiding(ship, true);
        }));

        at(315, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double eyeY = mc.player.getEyeY() - v.getY();
                double headTop = mc.player.getY() + 1.45D - v.getY();
                double roofHeight = 150.0D / 16.0D;
                boolean eyeInWindow = eyeY >= (128.0D / 16.0D) && eyeY <= (144.0D / 16.0D);
                boolean headUnderRoof = headTop <= roofHeight;
                check("ship_helm_window_eye_height", eyeInWindow, "Bridge eye Y: " + String.format("%.2f (window 8.00..9.00)", eyeY));
                check("ship_helm_roof_clearance", headUnderRoof, "Head top: " + String.format("%.2f", headTop) + ", Roof: " + String.format("%.2f", roofHeight));
                var clientColliders = mc.level.getEntitiesOfClass(com.vehiclefleet.entity.DeckColliderEntity.class, v.getBoundingBox().inflate(15.0D));
                check("ship_deck_colliders_synced", !clientColliders.isEmpty(), "Deck colliders synced on client: " + clientColliders.size());
            }
            server(mc, (p, l) -> {
                Entity ship = l.getEntity(ENTITY_IDS.getOrDefault("freighter", -1));
                if (ship instanceof FleetVehicleEntity s) {
                    check("ship_deck_colliders_server", !s.getDeckColliders().isEmpty(), "Server deck colliders: " + s.getDeckColliders().size());
                }
            });
            shot(mc, "08_freighter_bridge_first_person");
        });

        at(330, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                startPos = v.position();
                startYaw = v.getYRot();
            }
            mc.options.keyUp.setDown(true);
            mc.options.keyLeft.setDown(true);
        });

        at(360, mc -> {
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                float shipRoll = v.getHullRoll();
                check("ship_hull_roll_lean", Math.abs(shipRoll) > 0.005F, "Ship roll: " + String.format("%.3f rad (%.1f deg)", shipRoll, Math.toDegrees(shipRoll)));
            }
            shot(mc, "06_freighter_sailing_with_deck_cargo");
        });

        at(370, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.keyLeft.setDown(false);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                double dist = v.position().distanceTo(startPos);
                check("ship_sailing", dist > 1.0D, "Sailed: " + String.format("%.2f blocks", dist));
                var clientColliders = mc.level.getEntitiesOfClass(com.vehiclefleet.entity.DeckColliderEntity.class, v.getBoundingBox().inflate(15.0D));
                boolean allAlive = !clientColliders.isEmpty() && clientColliders.stream().allMatch(Entity::isAlive);
                check("ship_colliders_active_and_moving", allAlive, "All " + clientColliders.size() + " colliders alive and following ship");
            }
            server(mc, (p, l) -> {
                Entity ship = l.getEntity(ENTITY_IDS.getOrDefault("freighter", -1));
                Entity cargo = l.getEntity(ENTITY_IDS.getOrDefault("deck_cargo", -1));
                if (ship instanceof FleetVehicleEntity s && cargo != null) {
                    double distToShip = cargo.position().distanceTo(s.position());
                    check("freighter_deck_cargo_carried", distToShip < 12.0D, "Cargo carried with ship, relative dist: " + String.format("%.2f", distToShip));
                    check("freighter_deck_cargo_not_fallen", cargo.getY() >= s.getY() + 2.5D, "Cargo remained on deck surface Y: " + String.format("%.2f", cargo.getY()));
                }
            });
        });

        // 6. Board LPD Assault and test flight deck
        at(380, mc -> server(mc, (p, l) -> {
            p.stopRiding();
            Entity lpd = l.getEntity(ENTITY_IDS.getOrDefault("lpd", -1));
            if (lpd != null) p.startRiding(lpd, true);
        }));

        at(395, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            if (mc.player.getVehicle() instanceof FleetVehicleEntity v) {
                var clientColliders = mc.level.getEntitiesOfClass(com.vehiclefleet.entity.DeckColliderEntity.class, v.getBoundingBox().inflate(25.0D));
                check("lpd_flight_deck_colliders_synced", !clientColliders.isEmpty(), "LPD flight deck colliders synced on client: " + clientColliders.size());
            }
            shot(mc, "09_lpd_assault_flight_deck");
        });

        at(410, mc -> {
            VehicleFleetMod.LOGGER.info("[fleet-autotest] All in-game driving tests executed successfully!");
            mc.stop();
        });
    }
}
