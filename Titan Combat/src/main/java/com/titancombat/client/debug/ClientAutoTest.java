package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechState;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.TitanWeapon;
import com.titancombat.gui.TitanMenu;
import com.titancombat.item.ModItems;
import com.titancombat.network.MechControlC2SPacket;
import com.titancombat.network.ModNetworking;
import com.titancombat.network.TitanWeaponActionC2SPacket;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.function.Consumer;

/**
 * Dev-only scripted playtest. Inactive unless the JVM is started with -Dtitancombat.autotest=<name>
 * (build.gradle sets it from the TITAN_AUTOTEST env var for runClient). Spawns a titan next to the
 * player, boards it and runs a fixed script, saving screenshots to run/screenshots/autotest_*.png
 * and logging titan state.
 */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, value = Dist.CLIENT)
public final class ClientAutoTest {
    private static final String NAME = System.getProperty("titancombat.autotest", "");
    private static final String TITAN = System.getProperty("titancombat.autotest.titan", "monarch");
    private static int tick = -1;
    private static int titanId = -1;

    private record Step(int at, Consumer<Minecraft> action) {}

    private static final Step[] SCRIPT = {
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(140, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)),
            new Step(200, mc -> shot(mc, "01_unarmed_front")),
            new Step(205, mc -> server(mc, (p, t) -> {
                t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.PREDATOR_CANNON).get()));
                t.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.PREDATOR_CANNON).get(), 4));
            })),
            new Step(215, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELOAD))),
            new Step(250, mc -> shot(mc, "02_armed_reloading")),
            new Step(320, mc -> shot(mc, "03_armed_ready")),
            new Step(325, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.TOGGLE_LOWERED))),
            new Step(360, mc -> shot(mc, "04_lowered_front")),
            new Step(361, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK)),
            new Step(380, mc -> shot(mc, "05_lowered_back")),
            new Step(385, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.TOGGLE_LOWERED))),
            // Z pressed three times in a row: only the first should count
            new Step(420, mc -> kneel()),
            new Step(422, mc -> kneel()),
            new Step(424, mc -> kneel()),
            new Step(470, mc -> { dump(mc); mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT); }),
            new Step(490, mc -> shot(mc, "06_parked_front")),
            new Step(495, mc -> kneel()),
            new Step(560, mc -> { dump(mc); shot(mc, "07_stood_up"); }),
            new Step(565, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK)),
            new Step(580, mc -> ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, true, false))),
            new Step(588, mc -> shot(mc, "08_jump_air")),
            new Step(640, mc -> shot(mc, "09_landed")),
            new Step(650, mc -> server(mc, (p, t) -> t.openCustomInventoryScreen(p))),
            new Step(680, mc -> shot(mc, "10_bay")),
            new Step(690, mc -> { if (mc.screen != null) mc.screen.onClose(); mc.options.setCameraType(CameraType.FIRST_PERSON); }),
            new Step(730, mc -> shot(mc, "11_cockpit")),
            new Step(735, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.TOGGLE_LOWERED))),
            new Step(770, mc -> shot(mc, "12_cockpit_lowered")),
            new Step(790, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

    /** Side-view pose check on an unpiloted "display" titan placed in front of the player. */
    private static final Step[] POSES = {
            new Step(60, mc -> spawnDisplay(mc)),
            new Step(140, mc -> placeDisplay(mc)),
            new Step(200, mc -> shot(mc, "p01_unarmed")),
            new Step(125, mc -> display(mc, (p, t) -> t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.factoryWeaponOf(t.getTitanClass())).get())))),
            new Step(160, mc -> shot(mc, "p02_armed")),
            new Step(165, mc -> display(mc, (p, t) -> t.toggleWeaponLowered(p))),
            new Step(200, mc -> shot(mc, "p03_lowered")),
            new Step(205, mc -> display(mc, (p, t) -> t.toggleWeaponLowered(p))),
            new Step(210, mc -> display(mc, (p, t) -> t.setSitting(true))),
            new Step(270, mc -> shot(mc, "p04_parked")),
            new Step(275, mc -> display(mc, (p, t) -> t.toggleKneel())),
            new Step(345, mc -> shot(mc, "p05_stood")),
            new Step(330, mc -> display(mc, (p, t) -> t.setXRot(35.0F))),
            new Step(340, mc -> shot(mc, "p05b_look_down")),
            new Step(345, mc -> display(mc, (p, t) -> t.setXRot(0.0F))),
            new Step(350, mc -> display(mc, (p, t) -> t.performJump())),
            new Step(358, mc -> shot(mc, "p06_jump")),
            new Step(400, mc -> shot(mc, "p07_landed")),
            // one-block step under the titan's right foot
            new Step(402, mc -> display(mc, (p, t) -> {
                for (int dx = -2; dx <= 2; dx++) for (int dz = 1; dz <= 3; dz++) {
                    p.serverLevel().setBlockAndUpdate(net.minecraft.core.BlockPos.containing(t.getX() + dx, t.getY(), t.getZ() + dz),
                            net.minecraft.world.level.block.Blocks.STONE.defaultBlockState());
                }
                t.moveTo(t.getX(), t.getY() + 1.0D, t.getZ() + 0.4D, -90.0F, 0.0F);
            })),
            new Step(440, mc -> shot(mc, "p08_uneven")),
            new Step(450, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };
    private static int displayId = -1;

    // ---------------------------------------------------------------- showcase (CurseForge screenshots)
    private static final String[] ROSTER = {"ion", "scorch", "ronin", "tone", "legion", "monarch", "northstar"};
    private static final int[] rosterIds = new int[ROSTER.length];
    private static double baseX, baseY, baseZ;

    private static final Step[] SHOWCASE = {
            new Step(40, mc -> spawnRoster(mc)),
            new Step(45, mc -> { mc.options.hideGui = true; mc.options.setCameraType(CameraType.FIRST_PERSON); }),
            // warm-up: stand near the line so its chunks load and the models bake
            new Step(50, mc -> cam(mc, 21, 30, 0.2, 180, -9, 6000)),
            // 1. line-up in daylight, low angle from the front
            new Step(220, mc -> cam(mc, 21, 26, 0.0, 180, -12, 6000)),
            new Step(260, mc -> shot(mc, "s01_lineup")),
            // 2. hero shot: Ion, low and close, looking up
            new Step(265, mc -> cam(mc, 3.5, 7.5, -0.6, 155, -30, 6000)),
            new Step(305, mc -> shot(mc, "s02_ion_hero")),
            // 3. Legion behind its Defense Matrix barrier
            new Step(310, mc -> { roster(mc, 4, t -> t.setDefenseActive(true)); cam(mc, 28 + 3, 9, 0.5, 165, -16, 6000); }),
            new Step(350, mc -> shot(mc, "s03_legion_barrier")),
            // 4. Northstar firing its jump jets
            new Step(355, mc -> cam(mc, 42 - 9, 4, 0.5, 245, -18, 6000)),
            new Step(390, mc -> roster(mc, 6, BaseTitanEntity::performJump)),
            new Step(396, mc -> shot(mc, "s04_northstar_jump")),
            // 5. Scorch parked, hatch open, waiting for its pilot
            new Step(440, mc -> { roster(mc, 1, t -> t.setSitting(true)); cam(mc, 7 + 3, 8, 0.3, 160, -14, 6000); }),
            new Step(510, mc -> shot(mc, "s05_scorch_parked")),
            // 6. golden-hour line-up, diagonal
            new Step(515, mc -> { roster(mc, 1, t -> t.setSitting(false)); roster(mc, 4, t -> t.setDefenseActive(false)); cam(mc, -7, 13, 0.3, 215, -8, 11800); }),
            new Step(590, mc -> shot(mc, "s06_golden_hour")),
            // 7. cockpit: piloting Ion, HUD on, looking down the line
            new Step(595, mc -> { mc.options.hideGui = false; boardRoster(mc, 0); }),
            new Step(600, mc -> server2(mc, (p, l) -> l.setDayTime(6000L))),
            new Step(700, mc -> { mc.player.setYRot(-70.0F); mc.player.setXRot(6.0F); }),
            new Step(760, mc -> shot(mc, "s07_cockpit")),
            new Step(765, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK)),
            new Step(800, mc -> shot(mc, "s08_third_person")),
            new Step(805, mc -> server(mc, (p, t) -> t.openCustomInventoryScreen(p))),
            new Step(840, mc -> shot(mc, "s09_bay")),
            new Step(850, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

    private static void server2(Minecraft mc, java.util.function.BiConsumer<ServerPlayer, ServerLevel> action) {
        var server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player != null) action.accept(player, player.serverLevel());
        });
    }

    private static void spawnRoster(Minecraft mc) {
        server2(mc, (player, level) -> {
            if (player.getVehicle() instanceof BaseTitanEntity old) {
                old.setSitting(true);
                player.stopRiding();
            }
            baseX = player.getX() + 400; baseY = player.getY(); baseZ = player.getZ();
            level.setWeatherParameters(6000, 0, false, false);
            for (int i = 0; i < ROSTER.length; i++) {
                if (!(typeFor(ROSTER[i]).create(level) instanceof BaseTitanEntity t)) continue;
                t.moveTo(baseX + i * 7, baseY, baseZ, 0.0F, 0.0F);
                t.setYBodyRot(0.0F);
                t.setYHeadRot(0.0F);
                t.setOwner(player);
                t.setCamoIndex(i % 3 == 0 ? 0 : i);
                t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                        new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.factoryWeaponOf(t.getTitanClass())).get()));
                level.addFreshEntity(t);
                rosterIds[i] = t.getId();
            }
        });
    }

    private static void roster(Minecraft mc, int index, Consumer<BaseTitanEntity> action) {
        server2(mc, (p, level) -> {
            if (level.getEntity(rosterIds[index]) instanceof BaseTitanEntity t) action.accept(t);
        });
    }

    private static void boardRoster(Minecraft mc, int index) {
        server2(mc, (p, level) -> {
            if (level.getEntity(rosterIds[index]) instanceof BaseTitanEntity t) {
                p.teleportTo(level, t.getX(), t.getY(), t.getZ() + 3, 0, 0);
                p.startRiding(t, true);
                t.setMechState(MechState.PILOTED);
            }
        });
        mc.options.setCameraType(CameraType.FIRST_PERSON);
    }

    /** Put the camera (the player's eyes, on foot) at an offset from the line-up's first titan. */
    private static void cam(Minecraft mc, double dx, double dz, double dy, float yaw, float pitch, long time) {
        server2(mc, (p, level) -> {
            level.setDayTime(time);
            p.teleportTo(level, baseX + dx, baseY + dy, baseZ + dz, yaw, pitch);
        });
    }

    /** Piloted jump, filmed from the side by moving the pilot's titan past a fixed spectator angle. */
    private static final Step[] JUMP = {
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(150, mc -> { mc.options.hideGui = true; mc.options.setCameraType(CameraType.THIRD_PERSON_BACK); mc.player.setYRot(mc.player.getYRot() + 90.0F); }),
            new Step(200, mc -> shot(mc, "j00_ground")),
            new Step(205, mc -> ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, true, false))),
            new Step(208, mc -> shot(mc, "j01_takeoff")),
            new Step(214, mc -> shot(mc, "j02_rising")),
            new Step(222, mc -> shot(mc, "j03_apex")),
            new Step(230, mc -> shot(mc, "j04_falling")),
            new Step(236, mc -> shot(mc, "j05_touchdown")),
            new Step(240, mc -> shot(mc, "j06_after")),
            new Step(250, mc -> shot(mc, "j07_settled")),
            new Step(260, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

    private static final Step[] EJECT = {
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(150, mc -> { mc.options.hideGui = true; mc.options.setCameraType(CameraType.THIRD_PERSON_BACK); }),
            new Step(200, mc -> shot(mc, "e00_piloting")),
            new Step(205, mc -> ModNetworking.sendToServer(new com.titancombat.network.MechEjectC2SPacket())),
            new Step(208, mc -> shot(mc, "e01_blowout")),
            new Step(214, mc -> { mc.player.setXRot(70.0F); shot(mc, "e02_launch"); }),
            new Step(228, mc -> shot(mc, "e03_high")),
            new Step(256, mc -> shot(mc, "e04_boom")),
            new Step(300, mc -> shot(mc, "e05_after")),
            new Step(420, mc -> { TitanCombatMod.LOGGER.info("[autotest] pilot y={} hp={} landed={}", mc.player.getY(), mc.player.getHealth(), mc.player.onGround()); mc.stop(); }),
    };

    private static final Step[] SPRINT = buildSprint();

    private static Step[] buildSprint() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(new Step(60, mc -> spawnAndBoard(mc)));
        steps.add(new Step(150, mc -> { mc.options.hideGui = true; mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            server(mc, (p, t) -> t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.LEADWALL).get()))); }));
        steps.add(new Step(190, mc -> { mc.player.setXRot(12.0F); }));
        steps.add(new Step(198, mc -> shot(mc, "r00_idle")));
        steps.add(new Step(200, mc -> { mc.options.keyUp.setDown(true); }));
        steps.add(new Step(260, mc -> shot(mc, "r01_walk")));
        steps.add(new Step(265, mc -> { mc.options.keySprint.setDown(true); }));
        for (int t = 270; t <= 400; t += 5) {
            final int tt = t;
            steps.add(new Step(t, mc -> motion(mc, tt)));
        }
        steps.add(new Step(268, mc -> shot(mc, "r02_sprint_start")));
        steps.add(new Step(272, mc -> shot(mc, "r03_sprint_4t")));
        steps.add(new Step(278, mc -> shot(mc, "r04_sprint_10t")));
        steps.add(new Step(300, mc -> shot(mc, "r05_sprint")));
        steps.add(new Step(331, mc -> shot(mc, "r06_sprint")));
        steps.add(new Step(405, mc -> { mc.options.keySprint.setDown(false); mc.options.keyUp.setDown(false); }));
        steps.add(new Step(440, mc -> shot(mc, "r07_stop")));
        steps.add(new Step(450, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }));
        return steps.toArray(new Step[0]);
    }

    private static void motion(Minecraft mc, int tick) {
        if (!(mc.player.getVehicle() instanceof BaseTitanEntity t)) return;
        TitanCombatMod.LOGGER.info("[autotest] t={} gait={} speed={} ground={} y={} yRot={} body={} head={} leanF={} leanS={} lift={} vel={} sprintKey={} zza={}",
                tick, t.getGait(), String.format("%.2f", t.getDeltaMovement().horizontalDistance() * 20), t.onGround(),
                String.format("%.2f", t.getY()), String.format("%.1f", t.getYRot()), String.format("%.1f", t.yBodyRot), String.format("%.1f", t.yHeadRot),
                String.format("%.1f", t.getLeanForward(1)), String.format("%.1f", t.getLeanSide(1)), String.format("%.2f", t.getStepOffset(1)),
                t.getDeltaMovement(), BaseTitanEntity.clientSprintHeld, mc.player.zza);
    }

    private static final Step[] WEAPONS = buildWeapons();

    private static Step[] buildWeapons() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(new Step(60, mc -> spawnDisplay(mc)));
        steps.add(new Step(140, mc -> placeDisplay(mc)));
        steps.add(new Step(145, mc -> mc.options.hideGui = true));
        steps.add(new Step(220, mc -> shot(mc, "w0_unarmed")));
        int t = 225;
        for (TitanWeapon w : TitanWeapon.values()) {
            final TitanWeapon weapon = w;
            steps.add(new Step(t, mc -> display(mc, (p, d) -> d.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(weapon).get())))));
            steps.add(new Step(t + 30, mc -> {
                shot(mc, "w" + (weapon.ordinal() + 1) + "_" + weapon.getId());
                var e = mc.level.getEntity(displayId);
                var srv = mc.getSingleplayerServer().overworld().getEntity(displayId);
                TitanCombatMod.LOGGER.info("[autotest] display client={} weapon={} | server={} weapon={} slot={}",
                        e, e instanceof BaseTitanEntity bt ? bt.getActiveWeapon() : "-", srv, srv instanceof BaseTitanEntity st ? st.getActiveWeapon() : "-",
                        srv instanceof BaseTitanEntity st2 ? st2.getTitanInventory().getItem(TitanMenu.WEAPON_SLOT) : "-");
            }));
            t += 35;
        }
        // aim check: pilot a titan with the explosive 40mm tracker at a wall 25 blocks out
        final int a = t + 10;
        steps.add(new Step(a, mc -> spawnAndBoard(mc)));
        steps.add(new Step(a + 40, mc -> { mc.options.hideGui = false; mc.options.setCameraType(CameraType.FIRST_PERSON); server(mc, (p, ti) -> {
            ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.TRACKER_CANNON).get()));
            ti.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.TRACKER_CANNON).get(), 8));
            float yawRad = p.getYRot() * ((float) Math.PI / 180.0F);
            double fx = -Math.sin(yawRad), fz = Math.cos(yawRad), rx = -Math.cos(yawRad), rz = -Math.sin(yawRad);
            for (int side = -6; side <= 6; side++) for (int up = 0; up <= 12; up++) {
                p.serverLevel().setBlockAndUpdate(net.minecraft.core.BlockPos.containing(ti.getX() + fx * 25 + rx * side, ti.getY() + up, ti.getZ() + fz * 25 + rz * side),
                        net.minecraft.world.level.block.Blocks.WHITE_CONCRETE.defaultBlockState());
            }
        }); }));
        steps.add(new Step(a + 60, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELOAD))));
        steps.add(new Step(a + 140, mc -> { mc.player.setXRot(-8.0F); shot(mc, "a0_aim_first"); }));
        steps.add(new Step(a + 141, mc -> mc.options.keyAttack.setDown(true)));
        steps.add(new Step(a + 152, mc -> mc.options.keyAttack.setDown(false)));
        steps.add(new Step(a + 158, mc -> shot(mc, "a1_hit_first")));
        steps.add(new Step(a + 162, mc -> shot(mc, "a2_hit_first_late")));
        steps.add(new Step(a + 200, mc -> { mc.options.setCameraType(CameraType.THIRD_PERSON_BACK); mc.player.setXRot(2.0F); mc.player.setYRot(mc.player.getYRot() + 8.0F); }));
        steps.add(new Step(a + 220, mc -> shot(mc, "a3_aim_third")));
        steps.add(new Step(a + 221, mc -> mc.options.keyAttack.setDown(true)));
        steps.add(new Step(a + 232, mc -> mc.options.keyAttack.setDown(false)));
        steps.add(new Step(a + 238, mc -> shot(mc, "a4_hit_third")));
        steps.add(new Step(a + 242, mc -> shot(mc, "a5_hit_third_late")));
        steps.add(new Step(a + 260, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }));
        return steps.toArray(new Step[0]);
    }

    private ClientAutoTest() {}

    private static void display(Minecraft mc, java.util.function.BiConsumer<ServerPlayer, BaseTitanEntity> action) {
        var server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player != null && player.serverLevel().getEntity(displayId) instanceof BaseTitanEntity t) action.accept(player, t);
        });
    }

    private static double displayX, displayY, displayZ;

    /** Move the player to a fresh spot first; the titan is spawned once that chunk has loaded. */
    private static void spawnDisplay(Minecraft mc) {
        server2(mc, (player, level) -> {
            if (player.getVehicle() instanceof BaseTitanEntity old) {
                old.setSitting(true);
                player.stopRiding();
            }
            level.setDayTime(6000L);
            level.setWeatherParameters(60000, 0, false, false);
            displayX = Math.floor(player.getX()) + 200.5D;
            displayY = player.getY();
            displayZ = Math.floor(player.getZ()) + 0.5D;
            player.teleportTo(level, displayX, displayY, displayZ, 180.0F, -8.0F);
        });
    }

    private static void placeDisplay(Minecraft mc) {
        server2(mc, (player, level) -> {
            double x = displayX, z = displayZ;
            // Clear a corridor so terrain or village houses can't block the view.
            for (int dx = -8; dx <= 8; dx++) for (int dz = -20; dz <= 3; dz++) for (int dy = 0; dy <= 14; dy++) {
                level.setBlockAndUpdate(net.minecraft.core.BlockPos.containing(x + dx, displayY + dy, z + dz),
                        net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
            }
            if (!(typeFor(TITAN).create(level) instanceof BaseTitanEntity titan)) return;
            // Player looks north from 14 blocks south; the titan faces east, so we see its right side.
            titan.moveTo(x, displayY, z - 14, -90.0F, 0.0F);
            titan.setYBodyRot(-90.0F);
            titan.setYHeadRot(-90.0F);
            titan.setOwner(player);
            titan.setStandbyMode(true);
            boolean added = level.addFreshEntity(titan);
            displayId = titan.getId();
            TitanCombatMod.LOGGER.info("[autotest] display titan added={} id={}", added, displayId);
        });
    }

    private static EntityType<?> typeFor(String id) {
        return switch (id) {
            case "ion" -> ModEntities.ION_TITAN.get();
            case "ronin" -> ModEntities.RONIN_TITAN.get();
            case "northstar" -> ModEntities.NORTHSTAR_TITAN.get();
            case "legion" -> ModEntities.LEGION_TITAN.get();
            case "scorch" -> ModEntities.SCORCH_TITAN.get();
            case "tone" -> ModEntities.TONE_TITAN.get();
            case "trooper" -> ModEntities.TROOPER_TITAN.get();
            case "scout" -> ModEntities.SCOUT_TITAN.get();
            case "shade" -> ModEntities.SHADE_TITAN.get();
            default -> ModEntities.MONARCH_TITAN.get();
        };
    }

    private static final Step[] FLIGHT = buildFlight();

    // cloak: board a Shade, engage the cloak (Defense key), screenshot it, fire to break it.
    private static final Step[] CLOAK = {
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(140, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK)),
            new Step(180, mc -> shot(mc, "c1_visible")),
            new Step(185, mc -> ModNetworking.sendToServer(new com.titancombat.network.MechControlC2SPacket(0, 0, false, false, true, false, false, false))),
            new Step(220, mc -> { shot(mc, "c2_cloaked"); TitanCombatMod.LOGGER.info("[autotest] cloak invisible={}", mc.player.getVehicle().isInvisible()); }),
            new Step(225, mc -> server(mc, (p, t) -> t.firePrimaryWeapon(p))),
            new Step(260, mc -> { shot(mc, "c3_broken"); TitanCombatMod.LOGGER.info("[autotest] after fire invisible={}", mc.player.getVehicle().isInvisible()); }),
            new Step(270, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

    // fly_<module id>: install that flight module, hold jump for 3 s, log the climb.
    private static final Step[] FLY = {
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(120, mc -> server(mc, (p, t) -> t.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, new ItemStack(ModItems.FLIGHT_MODULES.get(
                    com.titancombat.entity.TitanFlightModule.byId(NAME.substring(NAME.indexOf('_') + 1))).get())))),
            new Step(140, mc -> server(mc, (p, t) -> TitanCombatMod.LOGGER.info("[autotest] fly start module={} y={}", t.getFlightModule(), t.getY()))),
            new Step(141, mc -> mc.options.keyJump.setDown(true)),
            new Step(200, mc -> TitanCombatMod.LOGGER.info("[autotest] fly 3s y={} vy={}", mc.player.getVehicle().getY(), mc.player.getVehicle().getDeltaMovement().y)),
            new Step(201, mc -> mc.options.keyJump.setDown(false)),
            new Step(260, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

    private static Step[] buildFlight() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(new Step(60, mc -> spawnDisplay(mc)));
        steps.add(new Step(140, mc -> placeDisplay(mc)));
        steps.add(new Step(145, mc -> mc.options.hideGui = true));

        // 1. Unarmed natural arms posture (arms relaxed at sides, not holding invisible rifle)
        steps.add(new Step(200, mc -> shot(mc, "01_unarmed_relaxed_arms")));

        // 2. Armed weapon holding
        steps.add(new Step(210, mc -> display(mc, (p, d) -> d.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.XO16_CHAINGUN).get())))));
        steps.add(new Step(240, mc -> shot(mc, "02_armed_ready")));

        // 3. Lowered gun posture (both arms lower naturally at the hip, natural carry)
        steps.add(new Step(250, mc -> display(mc, (p, d) -> d.toggleWeaponLowered(p))));
        steps.add(new Step(280, mc -> shot(mc, "03_lowered_hip_carry")));

        // 4. Military Salute Emote (front hero view showcasing military attention and salute)
        steps.add(new Step(290, mc -> display(mc, (p, d) -> {
            d.setYRot(12.0F); d.setYBodyRot(12.0F); d.setYHeadRot(12.0F);
            d.toggleWeaponLowered(p);
            d.triggerSalute(p);
            p.teleportTo(p.serverLevel(), d.getX() + 1.2D, d.getY() + 1.2D, d.getZ() + 8.5D, 188.0F, -4.0F);
        })));
        steps.add(new Step(315, mc -> shot(mc, "04_military_salute")));

        // 5. Equip Drone Lifter via Equipment Bay Slot (turn 125 degrees so back equipment is directly featured)
        steps.add(new Step(335, mc -> display(mc, (p, d) -> {
            d.setYRot(125.0F); d.setYBodyRot(125.0F); d.setYHeadRot(125.0F);
            p.teleportTo(p.serverLevel(), displayX, displayY, displayZ, 180.0F, -8.0F);
        })));
        steps.add(new Step(340, mc -> display(mc, (p, d) -> d.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT,
                new ItemStack(ModItems.FLIGHT_MODULES.get(com.titancombat.entity.TitanFlightModule.DRONE_LIFTER).get())))));
        steps.add(new Step(360, mc -> shot(mc, "05_drone_lifter_equipped")));

        // 6. Equip Rocket Jetpack via Equipment Bay Slot
        steps.add(new Step(370, mc -> display(mc, (p, d) -> d.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT,
                new ItemStack(ModItems.FLIGHT_MODULES.get(com.titancombat.entity.TitanFlightModule.ROCKET_JETPACK).get())))));
        steps.add(new Step(390, mc -> shot(mc, "06_rocket_jetpack_equipped")));

        // 7. Equip VTOL Glide Wings via Equipment Bay Slot
        steps.add(new Step(400, mc -> display(mc, (p, d) -> d.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT,
                new ItemStack(ModItems.FLIGHT_MODULES.get(com.titancombat.entity.TitanFlightModule.VTOL_GLIDE).get())))));
        steps.add(new Step(420, mc -> shot(mc, "07_vtol_glide_equipped")));

        // 8. Board and test actual flight, thrust, fuel and hovering
        steps.add(new Step(440, mc -> spawnAndBoard(mc)));
        steps.add(new Step(470, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            mc.player.setXRot(18.0F);
            server(mc, (p, ti) -> {
                p.serverLevel().setWeatherParameters(60000, 0, false, false);
                p.serverLevel().setDayTime(6000L);
                ti.setFlightModule(com.titancombat.entity.TitanFlightModule.DRONE_LIFTER);
                ti.setFlightThrust(true);
                ti.setDeltaMovement(0, 0.45D, 0);
            });
        }));
        steps.add(new Step(500, mc -> shot(mc, "08_drone_hover_airborne")));

        // 9. Rocket Jetpack high altitude thrust
        steps.add(new Step(510, mc -> server(mc, (p, ti) -> {
            ti.setFlightModule(com.titancombat.entity.TitanFlightModule.ROCKET_JETPACK);
            ti.setFlightThrust(true);
            ti.setDeltaMovement(0, 0.65D, 0.3D);
        })));
        steps.add(new Step(535, mc -> shot(mc, "09_rocket_boost_ascent")));

        // 10. VTOL Glide cruise
        steps.add(new Step(545, mc -> server(mc, (p, ti) -> {
            ti.setFlightModule(com.titancombat.entity.TitanFlightModule.VTOL_GLIDE);
            ti.setFlightThrust(true);
            ti.setDeltaMovement(0, 0.1D, 0.8D);
        })));
        steps.add(new Step(570, mc -> shot(mc, "10_vtol_cruise_glide")));

        // 11. Crosshair aim test in cockpit
        steps.add(new Step(580, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            server(mc, (p, ti) -> {
                ti.setFlightThrust(false);
                ti.moveTo(ti.getX(), p.getY(), ti.getZ(), p.getYRot(), 0.0F);
                ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.TRACKER_CANNON).get()));
                ti.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.TRACKER_CANNON).get(), 4));
            });
        }));
        steps.add(new Step(610, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELOAD))));
        steps.add(new Step(640, mc -> shot(mc, "11_cockpit_hud_aim")));
        steps.add(new Step(655, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }));

        return steps.toArray(new Step[0]);
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (NAME.isEmpty() || event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.getSingleplayerServer() == null) return;
        tick++;
        if (tick == 1) {
            mc.options.pauseOnLostFocus = false; // keep running when the window isn't focused
            if (mc.screen instanceof net.minecraft.client.gui.screens.PauseScreen) mc.setScreen(null);
        }
        Step[] script = NAME.startsWith("cloak") ? CLOAK : NAME.startsWith("fly_") ? FLY : NAME.startsWith("flight") ? FLIGHT : NAME.startsWith("poses") ? POSES : NAME.startsWith("showcase") ? SHOWCASE : NAME.startsWith("jump") ? JUMP : NAME.startsWith("eject") ? EJECT : NAME.startsWith("sprint") ? SPRINT : NAME.startsWith("weapons") ? WEAPONS : SCRIPT;
        for (Step step : script) {
            if (step.at() == tick) step.action().accept(mc);
        }
    }

    private static void kneel() {
        ModNetworking.sendToServer(new MechControlC2SPacket(0, 0, false, false, false, false, false, true));
    }

    private static void server(Minecraft mc, java.util.function.BiConsumer<ServerPlayer, BaseTitanEntity> action) {
        var server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player != null && player.getVehicle() instanceof BaseTitanEntity titan) action.accept(player, titan);
        });
    }

    private static void spawnAndBoard(Minecraft mc) {
        var server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player == null) return;
            ServerLevel level = player.serverLevel();
            if (player.getVehicle() instanceof BaseTitanEntity old) {
                old.setSitting(true); // parked, so the dismount guard lets the pilot out
                player.stopRiding();
            }
            EntityType<?> type = switch (TITAN) {
                case "ion" -> ModEntities.ION_TITAN.get();
                case "ronin" -> ModEntities.RONIN_TITAN.get();
                case "northstar" -> ModEntities.NORTHSTAR_TITAN.get();
                case "legion" -> ModEntities.LEGION_TITAN.get();
                case "scorch" -> ModEntities.SCORCH_TITAN.get();
                case "tone" -> ModEntities.TONE_TITAN.get();
                case "trooper" -> ModEntities.TROOPER_TITAN.get();
                case "scout" -> ModEntities.SCOUT_TITAN.get();
            case "shade" -> ModEntities.SHADE_TITAN.get();
                default -> ModEntities.MONARCH_TITAN.get();
            };
            if (!(type.create(level) instanceof BaseTitanEntity titan)) return;
            Vec3 look = player.getLookAngle().multiply(1, 0, 1).normalize();
            Vec3 at = player.position().add(look.scale(30.0D)); // away from earlier test titans
            titan.moveTo(at.x, player.getY(), at.z, player.getYRot(), 0.0F);
            titan.setOwner(player);
            level.addFreshEntity(titan);
            player.startRiding(titan, true);
            titan.setMechState(MechState.PILOTED);
            level.setDayTime(6000L);
            titanId = titan.getId();
            TitanCombatMod.LOGGER.info("[autotest] boarded {} id={}", TITAN, titanId);
        });
    }

    private static void dump(Minecraft mc) {
        if (!(mc.player.getVehicle() instanceof BaseTitanEntity t)) {
            TitanCombatMod.LOGGER.info("[autotest] not riding a titan");
            return;
        }
        TitanCombatMod.LOGGER.info("[autotest] titan {} y={} step={} state={} sit={} kneel={} gait={} ground={} weapon={} mag={} reload={} lowered={} stowed={}",
                t.getTitanClass(), String.format("%.2f", t.getY()), String.format("%.2f", t.getStepOffset(1)), t.getMechState(), t.isSitting(), t.isKneeling(), t.getGait(), t.onGround(),
                t.getActiveWeapon(), t.getMagazine(), t.getReloadTicks(), t.isWeaponLowered(), t.isWeaponStowed());
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "autotest_" + NAME + "_" + name + ".png", mc.getMainRenderTarget(), msg -> {});
        dump(mc);
        TitanCombatMod.LOGGER.info("[autotest] screenshot {} playerY={}", name, String.format("%.1f", mc.player.getY()));
    }
}
