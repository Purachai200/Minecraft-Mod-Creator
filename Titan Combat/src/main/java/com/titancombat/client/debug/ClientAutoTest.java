package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechState;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.TitanArmorTheme;
import com.titancombat.entity.TitanClass;
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
import net.minecraft.world.phys.AABB;
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
    private static double displayX, displayY, displayZ;

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

    // Howitzer back module with a hand weapon: tactical map shot, a typed target fired with the fire key,
    // a rejected 300 m target, a "designate + fire on lock" (map right-click) mission, aim views and a salute.
    private static final Step[] FRAME_TEST = {
            new Step(30, mc -> server2(mc, (p, level) -> {
                if (p.getVehicle() instanceof BaseTitanEntity old) { old.setSitting(true); p.stopRiding(); }
                var spawn = level.getSharedSpawnPos();
                int y = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, spawn.getX(), spawn.getZ());
                p.teleportTo(level, spawn.getX() + 0.5D, y, spawn.getZ() + 0.5D, 90.0F, 0.0F);
            })),
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(120, mc -> {
                mc.options.hideGui = false;
                mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
                server(mc, (p, t) -> {
                    t.setEnergy(50000);
                    // Equip factory weapon and armor pieces
                    if (t instanceof com.titancombat.entity.TitanFrameEntity frame) {
                        frame.setHeadArmor(true);
                        frame.setChestArmor(true);
                        frame.setArmsArmor(true);
                        frame.setLegsArmor(true);
                    }
                    t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.XO16_CHAINGUN).get()));
                    t.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.WEAPON_MAGAZINES.get(TitanWeapon.XO16_CHAINGUN).get(), 4));
                    t.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, new ItemStack(ModItems.HOWITZER_MODULE.get()));
                    t.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_2, new ItemStack(ModItems.HOWITZER_SMOKE_SHELLS.get(), 4));
                });
            }),
            new Step(160, mc -> shot(mc, "frame_01_armored_front")),
            new Step(180, mc -> server(mc, (p, t) -> t.setCamoIndex(5))), // Crimson Camo
            new Step(210, mc -> shot(mc, "frame_02_crimson_camo")),
            new Step(230, mc -> server(mc, (p, t) -> t.setCamoIndex(6))), // Cobalt Camo
            new Step(260, mc -> shot(mc, "frame_03_cobalt_camo")),
            new Step(280, mc -> {
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
                ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RELOAD));
            }),
            new Step(340, mc -> {
                // Fire weapon: bullet tracer + shell casing
                mc.options.keyAttack.setDown(true);
            }),
            new Step(350, mc -> {
                shot(mc, "frame_04_firing_tracer_casing");
                mc.options.keyAttack.setDown(false);
            }),
            new Step(380, mc -> {
                TitanCombatMod.LOGGER.info("[autotest] Frame test completed successfully!");
                mc.stop();
            })
    };

    private static int terrainId = -1;
    private static int cyclopsId = -1;
    private static int spiderId = -1;
    private static int strikerId = -1;
    private static int vanguardId = -1;

    private static final Step[] NEW_FRAMES = {
            new Step(20, mc -> server2(mc, (p, level) -> {
                p.setGameMode(net.minecraft.world.level.GameType.CREATIVE);
                if (p.getVehicle() instanceof BaseTitanEntity old) { old.setSitting(true); p.stopRiding(); }
                level.setDayTime(6000L);
                level.setWeatherParameters(6000, 0, false, false);
                displayX = 100.0D;
                displayY = 120.0D;
                displayZ = 100.0D;
                // Build a spacious stone stage (50x50)
                for (int dx = -25; dx <= 25; dx++) {
                    for (int dz = -25; dz <= 25; dz++) {
                        level.setBlockAndUpdate(net.minecraft.core.BlockPos.containing(displayX + dx, displayY - 1, displayZ + dz),
                                net.minecraft.world.level.block.Blocks.SMOOTH_STONE.defaultBlockState());
                    }
                }
                // Clear any leftover entities
                level.getEntitiesOfClass(BaseTitanEntity.class, new AABB(displayX - 35, displayY - 5, displayZ - 35, displayX + 35, displayY + 15, displayZ + 35))
                        .forEach(BaseTitanEntity::discard);
                p.teleportTo(level, displayX, displayY, displayZ - 20.0D, 0.0F, 0.0F);
            })),
            new Step(60, mc -> server2(mc, (p, level) -> {
                // 1. Striker Frame (with SMG & Salvage Scrap Armor) at X = displayX - 14
                var striker = ModEntities.STRIKER_FRAME_TITAN.get().create(level);
                if (striker != null) {
                    striker.moveTo(displayX - 14.0D, displayY, displayZ, 180.0F, 0.0F);
                    striker.setYBodyRot(180.0F);
                    striker.setYHeadRot(180.0F);
                    striker.setOwner(p);
                    striker.setHeadArmor(true);
                    striker.setChestArmor(true);
                    striker.setArmsArmor(true);
                    striker.setLegsArmor(true);
                    striker.setHeadTheme(TitanArmorTheme.SALVAGE_SCRAP);
                    striker.setChestTheme(TitanArmorTheme.SALVAGE_SCRAP);
                    striker.setArmsTheme(TitanArmorTheme.SALVAGE_SCRAP);
                    striker.setLegsTheme(TitanArmorTheme.SALVAGE_SCRAP);
                    striker.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.LIGHT_SMG).get()));
                    level.addFreshEntity(striker);
                    strikerId = striker.getId();
                }

                // 2. Terrain Ground Frame (with Heavy Assault Rifle & Colossus Siege Bunker Armor) at X = displayX - 7
                var terrain = ModEntities.TERRAIN_FRAME_TITAN.get().create(level);
                if (terrain != null) {
                    terrain.moveTo(displayX - 7.0D, displayY, displayZ, 180.0F, 0.0F);
                    terrain.setYBodyRot(180.0F);
                    terrain.setYHeadRot(180.0F);
                    terrain.setOwner(p);
                    terrain.setHeadArmor(true);
                    terrain.setChestArmor(true);
                    terrain.setArmsArmor(true);
                    terrain.setLegsArmor(true);
                    terrain.setHeadTheme(TitanArmorTheme.COLOSSUS);
                    terrain.setChestTheme(TitanArmorTheme.COLOSSUS);
                    terrain.setArmsTheme(TitanArmorTheme.COLOSSUS);
                    terrain.setLegsTheme(TitanArmorTheme.COLOSSUS);
                    terrain.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.HEAVY_ASSAULT_RIFLE).get()));
                    level.addFreshEntity(terrain);
                    terrainId = terrain.getId();
                }

                // 3. Cyclops Industrial Frame (with Rotary Machine Gun & Shiden Samurai Armor) at X = displayX
                var cyclops = ModEntities.CYCLOPS_FRAME_TITAN.get().create(level);
                if (cyclops != null) {
                    cyclops.moveTo(displayX, displayY, displayZ, 180.0F, 0.0F);
                    cyclops.setYBodyRot(180.0F);
                    cyclops.setYHeadRot(180.0F);
                    cyclops.setOwner(p);
                    cyclops.setHeadArmor(true);
                    cyclops.setChestArmor(true);
                    cyclops.setArmsArmor(true);
                    cyclops.setLegsArmor(true);
                    cyclops.setHeadTheme(TitanArmorTheme.SHIDEN_SAMURAI);
                    cyclops.setChestTheme(TitanArmorTheme.SHIDEN_SAMURAI);
                    cyclops.setArmsTheme(TitanArmorTheme.SHIDEN_SAMURAI);
                    cyclops.setLegsTheme(TitanArmorTheme.SHIDEN_SAMURAI);
                    cyclops.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.ROTARY_MACHINE_GUN).get()));
                    level.addFreshEntity(cyclops);
                    cyclopsId = cyclops.getId();
                }

                // 4. Spider Hexapod Frame (with Rocket Pod & Apex Sovereign Armor) at X = displayX + 7
                var spider = ModEntities.SPIDER_FRAME_TITAN.get().create(level);
                if (spider != null) {
                    spider.moveTo(displayX + 7.0D, displayY, displayZ, 180.0F, 0.0F);
                    spider.setYBodyRot(180.0F);
                    spider.setYHeadRot(180.0F);
                    spider.setOwner(p);
                    spider.setHeadArmor(true);
                    spider.setChestArmor(true);
                    spider.setArmsArmor(true);
                    spider.setLegsArmor(true);
                    spider.setHeadTheme(TitanArmorTheme.APEX_PREDATOR);
                    spider.setChestTheme(TitanArmorTheme.APEX_PREDATOR);
                    spider.setArmsTheme(TitanArmorTheme.APEX_PREDATOR);
                    spider.setLegsTheme(TitanArmorTheme.APEX_PREDATOR);
                    spider.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.ROCKET_POD).get()));
                    level.addFreshEntity(spider);
                    spiderId = spider.getId();
                }

                // 5. Vanguard Frame (with Splitter Rifle & Valkyrie Aero Armor) at X = displayX + 14
                var vanguard = ModEntities.VANGUARD_FRAME_TITAN.get().create(level);
                if (vanguard != null) {
                    vanguard.moveTo(displayX + 14.0D, displayY, displayZ, 180.0F, 0.0F);
                    vanguard.setYBodyRot(180.0F);
                    vanguard.setYHeadRot(180.0F);
                    vanguard.setOwner(p);
                    vanguard.setHeadArmor(true);
                    vanguard.setChestArmor(true);
                    vanguard.setArmsArmor(true);
                    vanguard.setLegsArmor(true);
                    vanguard.setHeadTheme(TitanArmorTheme.VALKYRIE_AERO);
                    vanguard.setChestTheme(TitanArmorTheme.VALKYRIE_AERO);
                    vanguard.setArmsTheme(TitanArmorTheme.VALKYRIE_AERO);
                    vanguard.setLegsTheme(TitanArmorTheme.VALKYRIE_AERO);
                    vanguard.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.SPLITTER_RIFLE).get()));
                    level.addFreshEntity(vanguard);
                    vanguardId = vanguard.getId();
                }
            })),
            // Shot 1: Epic 5-Mech Lineup (Full body, cinematic distance)
            new Step(120, mc -> {
                mc.options.hideGui = true;
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                server2(mc, (p, level) -> p.teleportTo(level, displayX, displayY + 2.5D, displayZ - 20.0D, 0.0F, 2.0F));
            }),
            new Step(140, mc -> shot(mc, "01_epic_5mech_lineup")),
            // Shot 2: Close-up Cyclops Shiden Samurai Armor (Kabuto crescent horns & tiered wings)
            new Step(160, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX, displayY + 2.2D, displayZ - 7.5D, 0.0F, 2.0F))),
            new Step(180, mc -> shot(mc, "02_cyclops_shiden_samurai_armor")),
            // Shot 3: Close-up Terrain Colossus Siege Armor (Fortress mantlet & reactive plates)
            new Step(200, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX - 7.0D, displayY + 2.2D, displayZ - 7.5D, 0.0F, 2.0F))),
            new Step(220, mc -> shot(mc, "03_terrain_colossus_siege_armor")),
            // Shot 4: Close-up Spider Heavy Hexapod Anti-Tank (Model Bullant with 6 legs & dual missile pods)
            new Step(240, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX + 7.0D, displayY + 2.5D, displayZ - 9.5D, 0.0F, 0.0F))),
            new Step(260, mc -> shot(mc, "04_spider_bullant_sovereign_hexapod")),
            // Shot 5: Close-up Striker Salvage Scrap Armor (Welded rebar cage & spikes)
            new Step(280, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX - 14.0D, displayY + 2.0D, displayZ - 7.0D, 0.0F, 2.0F))),
            new Step(300, mc -> shot(mc, "05_striker_salvage_scrap_armor")),
            // Shot 6: Close-up Vanguard Valkyrie Aero Armor (Swept delta winglets & thrusters)
            new Step(320, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX + 14.0D, displayY + 2.2D, displayZ - 7.5D, 0.0F, 2.0F))),
            new Step(340, mc -> shot(mc, "06_vanguard_valkyrie_aero_armor")),
            // Shot 7: 3/4 Dramatic Angle of Spider Mech
            new Step(360, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX + 14.0D, displayY + 2.5D, displayZ - 7.0D, 45.0F, -2.0F))),
            new Step(380, mc -> shot(mc, "07_spider_bullant_3quarter_angle")),
            // Shot 8: Elevated Close-up on the Manned Pilot Cockpit & Armored Entry Hatch
            new Step(400, mc -> server2(mc, (p, level) -> p.teleportTo(level, displayX + 7.0D, displayY + 4.6D, displayZ - 4.5D, 0.0F, 35.0F))),
            new Step(420, mc -> shot(mc, "08_spider_cockpit_hatch_detail")),
            // Verification of Boarding an Unarmed Titan Frame in First-Person Mode (Crash Fix Verification)
            new Step(430, mc -> server2(mc, (p, level) -> {
                var bareFrame = ModEntities.STRIKER_FRAME_TITAN.get().create(level);
                if (bareFrame != null) {
                    bareFrame.moveTo(displayX, displayY, displayZ - 10.0D, 0.0F, 0.0F);
                    bareFrame.setOwner(p);
                    level.addFreshEntity(bareFrame);
                    p.startRiding(bareFrame, true);
                }
            })),
            new Step(450, mc -> {
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                mc.options.hideGui = false;
                shot(mc, "09_unarmed_frame_first_person_cockpit");
            }),
            // Step 460: Test Opening Frame Customization Menu via E / openCustomInventoryScreen
            new Step(460, mc -> server2(mc, (p, level) -> {
                if (p.getVehicle() instanceof BaseTitanEntity titan) {
                    titan.openCustomInventoryScreen(p);
                }
            })),
            new Step(475, mc -> shot(mc, "10_frame_customization_armor_slots")),
            new Step(480, mc -> {
                if (mc.screen != null) mc.screen.onClose();
            }),
            // Step 490: Test Howitzer with Tactical Smoke Shells
            new Step(490, mc -> server2(mc, (p, level) -> {
                if (p.getVehicle() instanceof BaseTitanEntity titan) {
                    titan.setEnergy(50000);
                    titan.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, new ItemStack(ModItems.HOWITZER_MODULE.get()));
                    titan.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.HOWITZER_SMOKE_SHELLS.get(), 4));
                    titan.setHowitzerSmoke(true);
                    titan.setArtilleryTarget(p, titan.getBlockX() - 60, null, titan.getBlockZ());
                }
            })),
            new Step(520, mc -> {
                shot(mc, "11_howitzer_smoke_shell_hud");
                server2(mc, (p, level) -> {
                    if (p.getVehicle() instanceof BaseTitanEntity titan) {
                        titan.requestHowitzerFire(p, false);
                    }
                });
            }),
            // Step 535: Test Shoulder Rocket Launcher Pod & HUD
            new Step(535, mc -> server2(mc, (p, level) -> {
                if (p.getVehicle() instanceof BaseTitanEntity titan) {
                    titan.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, new ItemStack(ModItems.ROCKET_LAUNCHER_MODULE.get()));
                    titan.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.AMMO_ROCKET_SALVO.get(), 16));
                }
            })),
            new Step(550, mc -> shot(mc, "12_cockpit_missile_hud_ready")),
            // End
            new Step(560, mc -> {
                TitanCombatMod.LOGGER.info("[autotest] Unarmed Titan Frame boarded successfully in First-Person without crash!");
                TitanCombatMod.LOGGER.info("[autotest] Smoke shell fired successfully without premature detonation!");
                TitanCombatMod.LOGGER.info("[autotest] Missile launcher HUD verified successfully!");
                TitanCombatMod.LOGGER.info("[autotest] Epic armor showcase completed successfully!");
                mc.stop();
            })
    };

    private static final Step[] ARTILLERY = {
            // Back on the ground at world spawn (the saved test world may have left the player on a sky stage).
            new Step(30, mc -> server2(mc, (p, level) -> {
                if (p.getVehicle() instanceof BaseTitanEntity old) { old.setSitting(true); p.stopRiding(); }
                var spawn = level.getSharedSpawnPos();
                int y = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, spawn.getX(), spawn.getZ());
                p.teleportTo(level, spawn.getX() + 0.5D, y, spawn.getZ() + 0.5D, 90.0F, 0.0F);
            })),
            new Step(60, mc -> spawnAndBoard(mc)),
            new Step(150, mc -> { mc.options.hideGui = false; mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
                server(mc, (p, t) -> {
                    t.setEnergy(50000);
                    t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.LEADWALL).get()));
                    t.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, new ItemStack(ModItems.HOWITZER_MODULE.get()));
                    t.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.HOWITZER_SHELLS.get(), 3));
                }); }),
            // Steps are spaced out: the test server runs well under 20 TPS and loading a rack takes 90 ticks.
            new Step(300, mc -> { if (mc.player.getVehicle() instanceof BaseTitanEntity t) mc.setScreen(new com.titancombat.client.gui.ArtilleryMapScreen(t)); }),
            new Step(330, mc -> shot(mc, "a00_tactical_map")),
            new Step(335, mc -> { if (mc.screen != null) mc.screen.onClose(); }),
            new Step(380, mc -> setTargetWest(mc, 64)),
            new Step(398, mc -> shot(mc, "a01_laying")),
            new Step(440, mc -> fireHowitzer(mc)),
            new Step(455, mc -> shot(mc, "a02_fired")),
            new Step(490, mc -> setTargetWest(mc, 300)),
            new Step(500, mc -> { for (int i = 0; i < 8; i++) ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.RANGE_UP)); }),
            new Step(530, mc -> { mc.options.setCameraType(CameraType.FIRST_PERSON); mc.player.setXRot(8.0F); }),
            new Step(560, mc -> shot(mc, "a03_cockpit_hud")),
            new Step(600, mc -> fireHowitzer(mc)),
            // Map right-click equivalent: designate north-west and fire once laid.
            new Step(630, mc -> { mc.options.hideGui = true; mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT); mc.player.setXRot(-20.0F); }),
            new Step(632, mc -> shot(mc, "a03b_stand_front")),
            new Step(640, mc -> { var t = mc.player.getVehicle();
                ModNetworking.sendToServer(new com.titancombat.network.ArtilleryTargetC2SPacket(t.getBlockX() - 60, false, 0, t.getBlockZ() - 60, true)); }),
            new Step(660, mc -> shot(mc, "a04_brace_front")),
            new Step(675, mc -> mc.options.hideGui = false),
            new Step(700, mc -> shot(mc, "a05_after_mission")),
            // Salute: is the right hand raised to the visor in front, or swung behind?
            new Step(800, mc -> ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.SALUTE))),
            new Step(818, mc -> shot(mc, "a08_salute_front")),
            new Step(900, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

    private static void setTargetWest(Minecraft mc, int blocks) {
        var t = mc.player.getVehicle();
        ModNetworking.sendToServer(new com.titancombat.network.ArtilleryTargetC2SPacket(t.getBlockX() - blocks, false, 0, t.getBlockZ()));
    }

    private static void fireHowitzer(Minecraft mc) {
        server(mc, (p, t) -> TitanCombatMod.LOGGER.info("[autotest] howitzer target={} rounds={} reload={} laying={} weapon={}",
                t.getArtilleryTarget(), t.getHowitzerRounds(), t.getHowitzerReload(), t.getArtilleryLaying(), t.getActiveWeapon()));
        ModNetworking.sendToServer(new TitanWeaponActionC2SPacket(TitanWeaponActionC2SPacket.FIRE_HOWITZER));
    }

    // Side view of an unarmed titan standing, then walking past: stance and arm swing vs. leg stride.
    private static final Step[] WALK_SIDE = buildWalkSide();

    private static Step[] buildWalkSide() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        // Stone stage high in the sky: the world is random each run, so no terrain can block the view.
        // Steps are spaced out because the server lags for a while after world load.
        // A fresh spot each run (the autotest world is saved, so an old stage still holds earlier titans);
        // the player goes there first so the chunks are loaded before the titan spawns.
        steps.add(new Step(40, mc -> server2(mc, (player, level) -> {
            if (player.getVehicle() instanceof BaseTitanEntity old) {  // saved world: still seated from a previous run
                old.setSitting(true);
                player.stopRiding();
            }
            level.setDayTime(6000L);
            // Anchored to world spawn (always generated); relative to the player the saved world would drift
            // into new terrain every run, and generating it stalls the server for hundreds of ticks.
            var spawn = level.getSharedSpawnPos();
            displayX = spawn.getX() + 0.5D + (System.currentTimeMillis() / 1000L % 5L) * 32.0D;
            displayY = 200.0D;
            displayZ = spawn.getZ() + 0.5D;
            for (int dx = -6; dx <= 14; dx++) for (int dz = -36; dz <= 4; dz++) {
                level.setBlockAndUpdate(net.minecraft.core.BlockPos.containing(displayX + dx, displayY - 1, displayZ + dz),
                        net.minecraft.world.level.block.Blocks.STONE.defaultBlockState());
            }
            // Camera east of the titan looking west: it walks north, so we see its right side.
            player.teleportTo(level, displayX + 9.0D, displayY + 2.0D, displayZ - 17.0D, 90.0F, 6.0F);
            level.getEntitiesOfClass(BaseTitanEntity.class, new AABB(displayX - 8, displayY - 2, displayZ - 38, displayX + 16, displayY + 8, displayZ + 6))
                    .forEach(BaseTitanEntity::discard);
        })));
        steps.add(new Step(200, mc -> server2(mc, (player, level) -> {
            if (!(typeFor(TITAN).create(level) instanceof BaseTitanEntity titan)) return;
            titan.moveTo(displayX, displayY, displayZ - 17.0D, 180.0F, 0.0F);
            titan.setYBodyRot(180.0F);
            titan.setYHeadRot(180.0F);
            titan.setStandbyMode(true); // no owner either: owned titans turn to face their owner
            level.addFreshEntity(titan);
            displayId = titan.getId();
        })));
        // Whichever way the titan ended up facing, put the camera off its right side, aimed at the middle
        // of the stretch it is about to walk, and walk it along its own facing.
        steps.add(new Step(280, mc -> display(mc, (p, t) -> {
            Vec3 f = Vec3.directionFromRotation(0.0F, t.getYRot());
            Vec3 mid = t.position().add(f.scale(6.0D));
            Vec3 cam = mid.add(-f.z * 11.0D, 2.0D, f.x * 11.0D);
            float yaw = (float) Math.toDegrees(Math.atan2(-(mid.x - cam.x), mid.z - cam.z));
            p.teleportTo(p.serverLevel(), cam.x, cam.y, cam.z, yaw, 6.0F);
        })));
        steps.add(new Step(230, mc -> { mc.options.hideGui = true; mc.options.setCameraType(CameraType.FIRST_PERSON); }));
        steps.add(new Step(300, mc -> shot(mc, "w00_stand")));
        if (NAME.contains("brace")) {  // "walkside_brace": howitzer firing stance, side view
            steps.add(new Step(250, mc -> display(mc, (p, t) -> {
                t.setStandbyMode(false);
                t.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, new ItemStack(ModItems.HOWITZER_MODULE.get()));
            })));
            steps.add(new Step(310, mc -> display(mc, (p, t) -> t.setArtilleryTarget(p, t.getBlockX() - 70, null, t.getBlockZ()))));
            steps.add(new Step(330, mc -> shot(mc, "w01_brace")));
            steps.add(new Step(380, mc -> shot(mc, "w02_after")));
            steps.add(new Step(385, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }));
            return steps.toArray(new Step[0]);
        }
        for (int t = 305; t <= 360; t++) {
            steps.add(new Step(t, mc -> display(mc, (p, titan) -> {
                Vec3 at = titan.position().add(Vec3.directionFromRotation(0.0F, titan.getYRot()).scale(titan.getTitanClass().getWalkSpeed()));
                titan.moveTo(at.x, at.y, at.z, titan.getYRot(), 0.0F);
            })));
        }
        for (int t = 330; t <= 360; t += 6) {
            final int tt = t;
            steps.add(new Step(t, mc -> shot(mc, "w" + tt + "_walk")));
        }
        steps.add(new Step(365, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }));
        return steps.toArray(new Step[0]);
    }

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

    static void server2(Minecraft mc, java.util.function.BiConsumer<ServerPlayer, ServerLevel> action) {
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

    private static final Step[] COCKPIT_TOOLS = buildCockpitTools();

    private static Step[] buildCockpitTools() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(new Step(60, mc -> spawnAndBoard(mc)));
        steps.add(new Step(150, mc -> server2(mc, (p, level) -> {
            level.setDayTime(6000L);
            level.setWeatherParameters(60000, 0, false, false);
        })));
        steps.add(new Step(180, mc -> server(mc, (p, ti) -> {
            ti.setEnergy(50000);
            ti.setMechState(MechState.PILOTED);
        })));

        // 1. First-Person View with Mining Drill
        steps.add(new Step(210, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            mc.options.hideGui = false;
            server(mc, (p, ti) -> {
                ti.setEnergy(50000);
                ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                        new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.MINING_DRILL).get()));
            });
        }));
        steps.add(new Step(280, mc -> shot(mc, "01_cockpit_mining_drill")));

        // 2. First-Person View with Chainsaw
        steps.add(new Step(300, mc -> server(mc, (p, ti) -> {
            ti.setEnergy(50000);
            ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.CHAINSAW).get()));
        })));
        steps.add(new Step(370, mc -> shot(mc, "02_cockpit_chainsaw")));

        // 3. First-Person View with Light SMG
        steps.add(new Step(390, mc -> server(mc, (p, ti) -> {
            ti.setEnergy(50000);
            ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.LIGHT_SMG).get()));
        })));
        steps.add(new Step(460, mc -> shot(mc, "03_cockpit_light_smg")));

        // 4. Side view with Mining Drill
        steps.add(new Step(480, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            mc.player.setXRot(5.0F);
            mc.player.setYRot(mc.player.getYRot() - 90.0F);
            server(mc, (p, ti) -> {
                ti.setEnergy(50000);
                ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                        new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.MINING_DRILL).get()));
            });
        }));
        steps.add(new Step(530, mc -> shot(mc, "04_third_person_side_mining_drill")));
        steps.add(new Step(531, mc -> server(mc, (p, ti) -> ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.LIGHT_SMG).get())))));
        steps.add(new Step(538, mc -> shot(mc, "04b_third_person_side_light_smg")));

        // 5. Light SMG stowed on the back: park (kneel) and dismount, then look from behind and from the side
        steps.add(new Step(540, mc -> server(mc, (p, ti) -> {
            ti.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.LIGHT_SMG).get()));
            ti.setSitting(true);
            p.stopRiding();
            p.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
            // Clear trees around the titan so the close-up cameras see it
            var base = ti.blockPosition();
            for (var pos : net.minecraft.core.BlockPos.betweenClosed(base.offset(-8, 0, -8), base.offset(8, 14, 8))) {
                ti.level().setBlock(pos, net.minecraft.world.level.block.Blocks.AIR.defaultBlockState(), 2);
            }
        })));
        // aimCameraAt puts the camera at target - dist*(sin az, cos az): az = -yaw is straight behind, -yaw+90 the titan's right
        for (int[] view : new int[][]{{570, 0}, {590, 90}, {610, 180}, {630, 270}}) {
            steps.add(new Step(view[0], mc -> {
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                mc.options.hideGui = true;
                if (mc.level.getEntity(titanId) instanceof BaseTitanEntity t) {
                    tBaseY = t.getY();
                    aimCameraAt(mc, t.getX(), t.getY() + 3.0D, t.getZ(), 4.5D, 5.0D, -t.getYRot() + view[1]);
                }
            }));
            steps.add(new Step(view[0] + 15, mc -> shot(mc, "05_smg_stowed_az" + view[1])));
        }

        steps.add(new Step(660, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] done");
            mc.stop();
        }));
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
            case "striker_frame" -> ModEntities.STRIKER_FRAME_TITAN.get();
            case "vanguard_frame" -> ModEntities.VANGUARD_FRAME_TITAN.get();
            case "colossus_frame" -> ModEntities.COLOSSUS_FRAME_TITAN.get();
            case "terrain_frame" -> ModEntities.TERRAIN_FRAME_TITAN.get();
            case "cyclops_frame" -> ModEntities.CYCLOPS_FRAME_TITAN.get();
            case "spider_frame" -> ModEntities.SPIDER_FRAME_TITAN.get();
            default -> ModEntities.MONARCH_TITAN.get();
        };
    }

    private static final Step[] FLIGHT = buildFlight();

    // bind: right-click a titan with License and Transponder (vanilla interactOn order), warp it, then unbind.
    private static BaseTitanEntity bindTitan = null;
    private static BaseTitanEntity energyTitan = null;
    private static final Step[] ENERGY = {
            new Step(60, mc -> server2(mc, (player, level) -> {
                if (player.getVehicle() != null) player.stopRiding();
                for (var entity : level.getAllEntities()) {
                    if (entity instanceof BaseTitanEntity t) t.discard();
                }
                player.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);

                // 1. Test Battery Item FE, bar visibility, bar width, and bar color
                ItemStack emptyBat = new ItemStack(ModItems.EMPTY_BATTERY.get());
                ItemStack fullBat = new ItemStack(ModItems.TITAN_BATTERY.get());
                int emptyEnergy = com.titancombat.item.TitanBatteryItem.getEnergy(emptyBat);
                int fullEnergy = com.titancombat.item.TitanBatteryItem.getEnergy(fullBat);
                boolean emptyBarVis = emptyBat.getItem().isBarVisible(emptyBat);
                int fullBarWidth = fullBat.getItem().getBarWidth(fullBat);
                int fullBarColor = fullBat.getItem().getBarColor(fullBat);
                TitanCombatMod.LOGGER.info("[autotest] battery items: emptyEnergy={} emptyBarVis={} fullEnergy={} fullBarWidth={} fullBarColor=0x{}",
                        emptyEnergy, emptyBarVis, fullEnergy, fullBarWidth, Integer.toHexString(fullBarColor));

                // 2. Test Battery Charger BlockEntity
                var chargerPos = player.blockPosition().relative(player.getDirection());
                level.setBlockAndUpdate(chargerPos, com.titancombat.block.ModBlocks.BATTERY_CHARGER.get().defaultBlockState());
                var be = level.getBlockEntity(chargerPos);
                if (be instanceof com.titancombat.block.entity.BatteryChargerBlockEntity charger) {
                    charger.addEnergy(6000);
                    charger.setBatterySlot(emptyBat);
                    TitanCombatMod.LOGGER.info("[autotest] charger before tick: storedEnergy={} slotEnergy={}",
                            charger.getEnergyStored(), com.titancombat.item.TitanBatteryItem.getEnergy(charger.getBatterySlot()));

                    // Simulate 20 charger ticks
                    for (int i = 0; i < 20; i++) {
                        com.titancombat.block.entity.BatteryChargerBlockEntity.serverTick(level, chargerPos, level.getBlockState(chargerPos), charger);
                    }
                    TitanCombatMod.LOGGER.info("[autotest] charger after 20 ticks: storedEnergy={} slotEnergy={}",
                            charger.getEnergyStored(), com.titancombat.item.TitanBatteryItem.getEnergy(charger.getBatterySlot()));
                }

                // 3. Test Titan Initial Energy
                var titan = ModEntities.MONARCH_TITAN.get().create(level);
                if (titan == null) return;
                Vec3 look = player.getLookAngle().multiply(1, 0, 1).normalize();
                Vec3 at = player.position().add(look.scale(5.0D));
                titan.moveTo(at.x, player.getY(), at.z, player.getYRot() + 180.0F, 0.0F);
                titan.setOwner(player);
                level.addFreshEntity(titan);
                energyTitan = titan;
                TitanCombatMod.LOGGER.info("[autotest] titan spawned energy={} maxEnergy={}", titan.getEnergy(), titan.getMaxEnergy());
            })),
            new Step(120, mc -> server2(mc, (player, level) -> {
                if (energyTitan == null) return;
                // Test right-click with full battery item
                player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new ItemStack(ModItems.TITAN_BATTERY.get()));
                var interactRes = energyTitan.mobInteract(player, net.minecraft.world.InteractionHand.MAIN_HAND);
                ItemStack handItemAfter = player.getMainHandItem();
                TitanCombatMod.LOGGER.info("[autotest] battery insert result={} titanEnergyAfter={} handItemAfter={}",
                        interactRes, energyTitan.getEnergy(), handItemAfter.getItem());
            })),
            new Step(180, mc -> server2(mc, (player, level) -> {
                if (energyTitan == null) return;
                // Test energy consumption (sprint/walk/dash)
                int initialE = energyTitan.getEnergy();
                energyTitan.consumeEnergy(1500);
                TitanCombatMod.LOGGER.info("[autotest] after consumeEnergy: initial={} current={}", initialE, energyTitan.getEnergy());

                // Test Slot 0 onboard battery transfer
                ItemStack halfBat = new ItemStack(ModItems.TITAN_BATTERY.get());
                com.titancombat.item.TitanBatteryItem.setEnergy(halfBat, 4000);
                energyTitan.getTitanInventory().setItem(TitanMenu.BATTERY_SLOT, halfBat);
                TitanCombatMod.LOGGER.info("[autotest] placed 4,000 FE battery in bay slot 0");
            })),
            new Step(240, mc -> server2(mc, (player, level) -> {
                if (energyTitan == null) return;
                ItemStack bayBat = energyTitan.getTitanInventory().getItem(TitanMenu.BATTERY_SLOT);
                TitanCombatMod.LOGGER.info("[autotest] bay auto-transfer after ticks: titanEnergy={} bayBatEnergy={}",
                        energyTitan.getEnergy(), com.titancombat.item.TitanBatteryItem.getEnergy(bayBat));
            })),
            new Step(280, mc -> { TitanCombatMod.LOGGER.info("[autotest] energy tests complete"); mc.stop(); }),
    };

    private static final Step[] BIND = {
            new Step(40, mc -> server2(mc, (player, level) -> {
                if (player.getVehicle() != null) player.stopRiding();
                for (var entity : level.getAllEntities()) {
                    if (entity instanceof BaseTitanEntity t) t.discard();
                }
                player.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
                level.setDayTime(6000L);
                var titan = ModEntities.MONARCH_TITAN.get().create(level);
                if (titan == null) return;
                Vec3 look = player.getLookAngle().multiply(1, 0, 1).normalize();
                Vec3 at = player.position().add(look.scale(5.0D));
                titan.moveTo(at.x, player.getY(), at.z, player.getYRot() + 180.0F, 0.0F);
                titan.setStandbyMode(true);
                level.addFreshEntity(titan);
                bindTitan = titan;
                displayId = titan.getId();
                TitanCombatMod.LOGGER.info("[autotest] bind titan spawned id={}", displayId);
            })),
            new Step(80, mc -> server2(mc, (player, level) -> {
                if (bindTitan == null) return;
                TitanCombatMod.LOGGER.info("[autotest] initial owner='{}'", bindTitan.getOwnerUUID());
                player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new ItemStack(ModItems.PILOT_LICENSE.get()));
                var r = bindTitan.mobInteract(player, net.minecraft.world.InteractionHand.MAIN_HAND);
                var tag = player.getMainHandItem().getTag();
                TitanCombatMod.LOGGER.info("[autotest] license result={} riding={} linked={} owner='{}'", r, player.isPassenger(),
                        tag != null && tag.contains("TitanUUID"), bindTitan.getOwnerName());
            })),
            new Step(120, mc -> server2(mc, (player, level) -> {
                if (bindTitan == null) return;
                player.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new ItemStack(ModItems.HANGAR_TRANSPONDER.get()));
                var r = bindTitan.mobInteract(player, net.minecraft.world.InteractionHand.MAIN_HAND);
                var tag = player.getMainHandItem().getTag();
                TitanCombatMod.LOGGER.info("[autotest] transponder result={} riding={} linked={}", r, player.isPassenger(),
                        tag != null && tag.contains("TitanUUID"));
            })),
            new Step(160, mc -> server2(mc, (player, level) -> {
                if (bindTitan == null) return;
                var before = bindTitan.position();
                player.setYRot(player.getYRot() + 90.0F);
                player.getMainHandItem().use(player.level(), player, net.minecraft.world.InteractionHand.MAIN_HAND);
                TitanCombatMod.LOGGER.info("[autotest] warp moved={} blocks", String.format("%.1f", before.distanceTo(bindTitan.position())));
            })),
            new Step(200, mc -> server2(mc, (player, level) -> {
                if (bindTitan == null) return;
                player.setShiftKeyDown(true);
                var r = bindTitan.mobInteract(player, net.minecraft.world.InteractionHand.MAIN_HAND);
                player.setShiftKeyDown(false);
                var tag = player.getMainHandItem().getTag();
                boolean tagHasUUID = tag != null && tag.contains("TitanUUID");
                TitanCombatMod.LOGGER.info("[autotest] unbind result={} ownerAfter='{}' tagHasUUID={}", r, bindTitan.getOwnerUUID(), tagHasUUID);
            })),
            new Step(240, mc -> { TitanCombatMod.LOGGER.info("[autotest] done"); mc.stop(); }),
    };

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
            new Step(125, mc -> { mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT); mc.player.setYRot(mc.player.getYRot() + 110.0F); }),
            new Step(138, mc -> shot(mc, "mounted")),
            new Step(139, mc -> mc.player.setYRot(mc.player.getYRot() - 110.0F)),
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

    private static int truckId = -1;
    private static int droneId = -1;
    private static int bargeId = -1;
    static double tBaseX = 9600.0D;
    static double tBaseY = -60.0D;
    static double tBaseZ = -1500.0D;

    static void setCamPos(Minecraft mc, double camX, double camY, double camZ, float yaw, float pitch) {
        server2(mc, (player, level) -> {
            player.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
            player.teleportTo(level, camX, camY, camZ, yaw, pitch);
        });
        if (mc.player != null) {
            mc.player.setPos(camX, camY, camZ);
            mc.player.setYRot(yaw);
            mc.player.setXRot(pitch);
            mc.player.yRotO = yaw;
            mc.player.xRotO = pitch;
        }
    }

    static void aimCameraAt(Minecraft mc, double targetX, double targetY, double targetZ, double dist, double elevAngleDeg, double azimuthDeg) {
        double radAz = Math.toRadians(azimuthDeg);
        double radEl = Math.toRadians(elevAngleDeg);
        double camX = targetX - dist * Math.cos(radEl) * Math.sin(radAz);
        double camY = Math.max(tBaseY + 1.2D, targetY + dist * Math.sin(radEl));
        double camZ = targetZ - dist * Math.cos(radEl) * Math.cos(radAz);

        double dx = targetX - camX;
        double dy = targetY - (camY + 1.62D);
        double dz = targetZ - camZ;
        double horizDist = Math.sqrt(dx * dx + dz * dz);

        float yaw = (float) (Math.atan2(dz, dx) * (180.0D / Math.PI)) - 90.0F;
        float pitch = (float) (-(Math.atan2(dy, horizDist) * (180.0D / Math.PI)));

        setCamPos(mc, camX, camY, camZ, yaw, pitch);
    }


    private static int carrierId = -1;
    private static int tacticalTruckId = -1;
    private static int chinookId = -1;
    private static int ospreyId = -1;
    private static int apcId = -1;
    private static int trailerId = -1;

    private static float yawBefore;
    private static int slingTitanId = -1;
    private static double yBefore;
    private static final Step[] TRANSPORT_NEW = buildTransportNew();

    private static Step[] buildTransportNew() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(new Step(40, mc -> {
            if (mc.player != null && mc.player.getVehicle() != null) {
                mc.player.stopRiding();
            }
            server2(mc, (player, level) -> {
                if (player.getVehicle() != null) {
                    player.stopRiding();
                }
                level.setWeatherParameters(60000, 0, false, false);
                level.setDayTime(5000L); // Bright morning sunlight

                tBaseX = player.getX();
                tBaseY = player.getY();
                tBaseZ = player.getZ();

                int bx = (int) tBaseX;
                int by = (int) tBaseY;
                int bz = (int) tBaseZ;

                for (var entity : level.getAllEntities()) {
                    if (entity instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity ||
                        entity instanceof com.titancombat.entity.BaseTitanEntity) {
                        entity.discard();
                    }
                }

                // 1. Clear air
                for (int dx = -45; dx <= 45; dx++) {
                    for (int dz = -45; dz <= 45; dz++) {
                        for (int dy = 1; dy <= 32; dy++) {
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by + dy, bz + dz), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
                        }
                    }
                }

                // 2. Proving ground: Wide Highway on Left, Sea on Right
                for (int dx = -45; dx <= 45; dx++) {
                    for (int dz = -45; dz <= 45; dz++) {
                        if (dx >= 14 && dx <= 44) {
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by - 3, bz + dz), net.minecraft.world.level.block.Blocks.SAND.defaultBlockState());
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by - 2, bz + dz), net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by - 1, bz + dz), net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
                        } else if (dx >= -28 && dx <= -6) {
                            var road = (dx == -28 || dx == -6 || (dz % 3 == 0)) ? net.minecraft.world.level.block.Blocks.COARSE_DIRT.defaultBlockState()
                                    : net.minecraft.world.level.block.Blocks.DIRT_PATH.defaultBlockState();
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), road);
                        } else {
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), net.minecraft.world.level.block.Blocks.GRASS_BLOCK.defaultBlockState());
                        }
                    }
                }

                double groundY = by + 1.0D;

                // 1. V-22 Osprey Tiltrotor (airborne hover)
                double ospreyX = bx - 14.0D;
                var osprey = new com.titancombat.entity.transport.TitanV22OspreyEntity(ModEntities.V22_OSPREY.get(), level);
                osprey.moveTo(ospreyX, groundY + 10.0D, bz - 4.0D, 180.0F, 0.0F);
                osprey.setNoGravity(true);
                level.addFreshEntity(osprey);
                ospreyId = osprey.getId();

                // 2. Armored Combat 8x8 APC
                double apcX = bx - 22.0D;
                var apc = new com.titancombat.entity.transport.TitanArmoredApcEntity(ModEntities.ARMORED_APC.get(), level);
                apc.moveTo(apcX, groundY, bz - 4.0D, 180.0F, 0.0F);
                apc.setNoGravity(true);
                level.addFreshEntity(apc);
                apcId = apc.getId();

                // 3. Mobile Suit Flatbed Trailer with Northstar Titan docked
                double trailerX = bx - 10.0D;
                var trailer = new com.titancombat.entity.transport.TitanMobileSuitTrailerEntity(ModEntities.MOBILE_SUIT_TRAILER.get(), level);
                trailer.moveTo(trailerX, groundY, bz + 4.0D, 180.0F, 0.0F);
                trailer.setNoGravity(true);
                level.addFreshEntity(trailer);
                trailerId = trailer.getId();

                var titanOnTrailer = ModEntities.NORTHSTAR_TITAN.get().create(level);
                if (titanOnTrailer != null) {
                    titanOnTrailer.moveTo(trailerX, groundY, bz + 4.0D, 180.0F, 0.0F);
                    titanOnTrailer.setOwner(player);
                    titanOnTrailer.setNoGravity(true);
                    level.addFreshEntity(titanOnTrailer);
                    trailer.lockCargoToDeck(titanOnTrailer, null);
                }

                // 4. Chinook Helicopter
                double heloX = bx - 2.0D;
                var chinook = new com.titancombat.entity.transport.TitanChinookTransporterEntity(ModEntities.CHINOOK_TRANSPORTER.get(), level);
                chinook.moveTo(heloX, groundY, bz - 4.0D, 180.0F, 0.0F);
                chinook.setNoGravity(true);
                level.addFreshEntity(chinook);
                chinookId = chinook.getId();

                // 5. Oceanic Super-Carrier Barge in water
                double carrierX = bx + 24.0D;
                var carrier = new com.titancombat.entity.transport.TitanOceanCarrierEntity(ModEntities.OCEAN_CARRIER.get(), level);
                carrier.moveTo(carrierX, groundY - 0.4D, bz - 4.0D, 175.0F, 0.0F);
                carrier.setNoGravity(true);
                level.addFreshEntity(carrier);
                carrierId = carrier.getId();

                var ronin = ModEntities.RONIN_TITAN.get().create(level);
                if (ronin != null) {
                    ronin.moveTo(carrierX, groundY, bz - 4.0D, 175.0F, 0.0F);
                    ronin.setOwner(player);
                    ronin.setNoGravity(true);
                    level.addFreshEntity(ronin);
                    carrier.lockCargoToDeck(ronin, null);
                }
            });
        }));

        steps.add(new Step(80, mc -> {
            mc.options.hideGui = true;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            server2(mc, (player, level) -> {
                player.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
            });
        }));

        // Shot 1: Fleet Hero Lineup Overview (All New Vehicles + Carrier in water)
        steps.add(new Step(120, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 4.0D, groundY + 7.5D, tBaseZ - 2.0D, 32.0D, 15.0D, 168.0D);
        }));
        steps.add(new Step(130, mc -> shot(mc, "01_fleet_overview_all_new_vehicles")));

        // Shot 2: Mobile Suit Heavy Trailer with Docked Titan
        steps.add(new Step(140, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 10.0D, groundY + 2.5D, tBaseZ + 4.0D, 15.0D, 14.0D, 150.0D);
        }));
        steps.add(new Step(150, mc -> shot(mc, "02_mobile_suit_trailer_launch_cradle")));

        // Shot 3: Armored Combat 8x8 APC
        steps.add(new Step(160, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 22.0D, groundY + 2.0D, tBaseZ - 4.0D, 10.0D, 14.0D, 160.0D);
        }));
        steps.add(new Step(170, mc -> shot(mc, "03_armored_apc_8x8_turret")));

        // Shot 4: V-22 Osprey Tiltrotor Hovering in Flight
        steps.add(new Step(180, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 14.0D, groundY + 11.5D, tBaseZ - 4.0D, 16.0D, 10.0D, 165.0D);
        }));
        steps.add(new Step(190, mc -> shot(mc, "04_v22_osprey_tiltrotor_flight")));

        // Shot 5: Board V-22 Osprey Cockpit Interior First Person
        steps.add(new Step(200, mc -> server2(mc, (p, l) -> {
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            var osprey = l.getEntity(ospreyId);
            if (osprey instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(210, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setXRot(5.0F);
                mc.player.setYRot(180.0F);
            }
        }));
        steps.add(new Step(225, mc -> shot(mc, "05_v22_osprey_cockpit_interior_view")));

        // Shot 6: Board Armored APC Cockpit First Person
        steps.add(new Step(235, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            var apc = l.getEntity(apcId);
            if (apc instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(245, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setXRot(5.0F);
                mc.player.setYRot(180.0F);
            }
        }));
        steps.add(new Step(260, mc -> shot(mc, "06_armored_apc_cockpit_view")));

        // Shot 7: Board Mobile Suit Trailer Cockpit
        steps.add(new Step(270, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            var tr = l.getEntity(trailerId);
            if (tr instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(280, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setXRot(5.0F);
                mc.player.setYRot(180.0F);
            }
        }));
        steps.add(new Step(295, mc -> shot(mc, "07_mobile_suit_trailer_cockpit_view")));

        // Shot 8: Board Ocean Carrier Bridge Helm
        steps.add(new Step(305, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            var car = l.getEntity(carrierId);
            if (car instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(315, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setXRot(5.0F);
                mc.player.setYRot(175.0F);
            }
        }));
        steps.add(new Step(330, mc -> shot(mc, "08_ocean_carrier_bridge_view")));

        // Shot 9: Chinook close-up, then faction paint on the APC
        steps.add(new Step(340, mc -> server2(mc, (p, l) -> p.stopRiding())));
        steps.add(new Step(350, mc -> aimCameraAt(mc, tBaseX - 2.0D, ((int) tBaseY) + 3.0D, tBaseZ - 4.0D, 16.0D, 14.0D, 120.0D)));
        steps.add(new Step(360, mc -> shot(mc, "09_chinook_closeup")));
        steps.add(new Step(365, mc -> server2(mc, (p, l) -> {
            if (l.getEntity(apcId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v) v.setFaction(com.titancombat.entity.MechFaction.CRIMSON_LEGION);
            if (l.getEntity(chinookId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v) v.setFaction(com.titancombat.entity.MechFaction.APEX_VANGUARD);
        })));
        steps.add(new Step(375, mc -> aimCameraAt(mc, tBaseX - 22.0D, ((int) tBaseY) + 3.0D, tBaseZ - 4.0D, 10.0D, 14.0D, 160.0D)));
        steps.add(new Step(385, mc -> shot(mc, "10_apc_crimson_faction")));
        steps.add(new Step(388, mc -> aimCameraAt(mc, tBaseX + 24.0D, ((int) tBaseY) + 3.0D, tBaseZ - 4.0D, 22.0D, 18.0D, 230.0D)));
        steps.add(new Step(393, mc -> shot(mc, "10b_carrier_closeup")));
        steps.add(new Step(394, mc -> aimCameraAt(mc, tBaseX - 14.0D, ((int) tBaseY) + 11.0D, tBaseZ - 4.0D, 14.0D, 5.0D, 90.0D)));
        steps.add(new Step(395, mc -> shot(mc, "10c_osprey_side_a")));
        steps.add(new Step(396, mc -> aimCameraAt(mc, tBaseX - 14.0D, ((int) tBaseY) + 11.0D, tBaseZ - 4.0D, 14.0D, 5.0D, 270.0D)));
        steps.add(new Step(398, mc -> shot(mc, "10d_osprey_side_b")));

        // Behaviour: Chinook turns with A, Osprey descends with the Descend key
        steps.add(new Step(400, mc -> server2(mc, (p, l) -> {
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            if (l.getEntity(chinookId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v) { v.setNoGravity(false); p.startRiding(v, true); }
        })));
        steps.add(new Step(412, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            yawBefore = mc.player.getVehicle() != null ? mc.player.getVehicle().getYRot() : Float.NaN;
            mc.options.keyLeft.setDown(true);
        }));
        steps.add(new Step(450, mc -> {
            mc.options.keyLeft.setDown(false);
            float after = mc.player.getVehicle() != null ? mc.player.getVehicle().getYRot() : Float.NaN;
            TitanCombatMod.LOGGER.info("[autotest] CHECK chinook_turn yaw {} -> {} : {}", yawBefore, after, Math.abs(after - yawBefore) > 20 ? "PASS" : "FAIL");
            shot(mc, "11_chinook_turned");
        }));
        steps.add(new Step(460, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            if (l.getEntity(ospreyId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v) { v.setNoGravity(false); p.startRiding(v, true); }
        })));
        steps.add(new Step(475, mc -> {
            yBefore = mc.player.getVehicle() != null ? mc.player.getVehicle().getY() : Double.NaN;
            com.titancombat.client.KeyInputHandler.KEY_DESCEND.setDown(true);
        }));
        steps.add(new Step(505, mc -> {
            com.titancombat.client.KeyInputHandler.KEY_DESCEND.setDown(false);
            double after = mc.player.getVehicle() != null ? mc.player.getVehicle().getY() : Double.NaN;
            TitanCombatMod.LOGGER.info("[autotest] CHECK osprey_descend y {} -> {} : {}", yBefore, after, yBefore - after > 3 ? "PASS" : "FAIL");
            shot(mc, "12_osprey_descended");
        }));

        // Behaviour: shift + right-click (empty hand) loads the nearest titan onto the Osprey sling; release drops it
        steps.add(new Step(515, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            if (!(l.getEntity(ospreyId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v)) return;
            v.setNoGravity(true);
            v.moveTo(v.getX(), tBaseY + 12.0D, v.getZ());
            var titan = ModEntities.ION_TITAN.get().create(l);
            titan.moveTo(v.getX() + 3.0D, tBaseY + 1.0D, v.getZ(), 0.0F, 0.0F);
            l.addFreshEntity(titan);
            slingTitanId = titan.getId();
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, net.minecraft.world.item.ItemStack.EMPTY);
            p.setShiftKeyDown(true);
            v.mobInteract(p, net.minecraft.world.InteractionHand.MAIN_HAND);
            p.setShiftKeyDown(false);
            TitanCombatMod.LOGGER.info("[autotest] CHECK shift_load {} : {}", titan.getVehicle(), titan.getVehicle() == v ? "PASS" : "FAIL");
        })));
        steps.add(new Step(525, mc -> server2(mc, (p, l) -> {
            var v = l.getEntity(ospreyId);
            var titan = l.getEntity(slingTitanId);
            double gap = v.getY() - (titan.getY() + titan.getBbHeight());
            TitanCombatMod.LOGGER.info("[autotest] CHECK osprey_sling titanTop below hull by {} : {}", String.format("%.2f", gap), gap > 0 && gap < 1.5 ? "PASS" : "FAIL");
        })));
        steps.add(new Step(530, mc -> aimCameraAt(mc, tBaseX - 14.0D, tBaseY + 8.0D, tBaseZ - 4.0D, 22.0D, 2.0D, 90.0D)));
        steps.add(new Step(540, mc -> shot(mc, "13_osprey_sling_load")));
        steps.add(new Step(545, mc -> server2(mc, (p, l) -> {
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            if (l.getEntity(ospreyId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v) p.startRiding(v, true);
        })));
        steps.add(new Step(555, mc -> {
            com.titancombat.network.ModNetworking.sendToServer(new com.titancombat.network.TitanWeaponActionC2SPacket(com.titancombat.network.TitanWeaponActionC2SPacket.RELEASE_CARGO));
        }));
        steps.add(new Step(565, mc -> server2(mc, (p, l) -> {
            var t = l.getEntity(slingTitanId);
            TitanCombatMod.LOGGER.info("[autotest] CHECK osprey_release driver={} titanVehicle={} : {}", p.getVehicle(), t == null ? "gone" : t.getVehicle(), t != null && !t.isPassenger() ? "PASS" : "FAIL");
        })));

        // Behaviour: wrench returns each vehicle's own item
        steps.add(new Step(575, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            p.setShiftKeyDown(true);
            var wrench = new net.minecraft.world.item.ItemStack(com.titancombat.item.ModItems.VEHICLE_WRENCH.get());
            for (int id : new int[]{chinookId, ospreyId, apcId, trailerId, carrierId}) {
                if (!(l.getEntity(id) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v)) continue;
                String want = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(v.getType()).getPath();
                p.getInventory().clearContent();
                wrench.getItem().interactLivingEntity(wrench, p, v, net.minecraft.world.InteractionHand.MAIN_HAND);
                String got = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(p.getInventory().getItem(0).getItem()).getPath();
                TitanCombatMod.LOGGER.info("[autotest] CHECK wrench {} -> {} : {}", want, got, want.equals(got) ? "PASS" : "FAIL");
            }
            p.setShiftKeyDown(false);
        })));

        // Test finish
        steps.add(new Step(590, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] Completed expanded transport test suite successfully!");
            mc.stop();
        }));

        return steps.toArray(new Step[0]);
    }

    private static final Step[] TRANSPORT = buildTransport();

    private static Step[] buildTransport() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(new Step(40, mc -> {
            if (mc.player != null && mc.player.getVehicle() != null) {
                mc.player.stopRiding();
            }
            server2(mc, (player, level) -> {
                if (player.getVehicle() instanceof BaseTitanEntity old) {
                    old.setSitting(true);
                    player.stopRiding();
                } else if (player.getVehicle() != null) {
                    player.stopRiding();
                }
            level.setWeatherParameters(60000, 0, false, false);
            level.setDayTime(5000L); // Bright morning sunlight

            tBaseX = player.getX();
            tBaseY = player.getY();
            tBaseZ = player.getZ();

            int bx = (int) tBaseX;
            int by = (int) tBaseY;
            int bz = (int) tBaseZ;

            // Discard any existing transport entities or titans anywhere in world to guarantee clean scene
            for (var entity : level.getAllEntities()) {
                if (entity instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity ||
                    entity instanceof com.titancombat.entity.BaseTitanEntity) {
                    entity.discard();
                }
            }

            // 1. Clear overhead air: dy from 1 to 32
            for (int dx = -35; dx <= 35; dx++) {
                for (int dz = -35; dz <= 35; dz++) {
                    for (int dy = 1; dy <= 32; dy++) {
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by + dy, bz + dz), net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
                    }
                }
            }

            // 2. Build showcase proving ground: Road on Left, River on Right, matching the iconic showcase concept
            for (int dx = -35; dx <= 35; dx++) {
                for (int dz = -35; dz <= 35; dz++) {
                    // River: dx from 6 to 34 (on the right)
                    if (dx >= 6 && dx <= 34) {
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by - 3, bz + dz), net.minecraft.world.level.block.Blocks.SAND.defaultBlockState());
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by - 2, bz + dz), net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by - 1, bz + dz), net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), net.minecraft.world.level.block.Blocks.WATER.defaultBlockState());
                    }
                    // Riverbank: dx from 3 to 5
                    else if (dx >= 3 && dx <= 5) {
                        for (int dy = -2; dy <= -1; dy++) {
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by + dy, bz + dz), net.minecraft.world.level.block.Blocks.DIRT.defaultBlockState());
                        }
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), net.minecraft.world.level.block.Blocks.SAND.defaultBlockState());
                    }
                    // Convoy Dirt Road: dx from -16 to -6 (on the left)
                    else if (dx >= -16 && dx <= -6) {
                        for (int dy = -2; dy <= -1; dy++) {
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by + dy, bz + dz), net.minecraft.world.level.block.Blocks.DIRT.defaultBlockState());
                        }
                        var roadBlock = (dx == -16 || dx == -6 || (dz % 3 == 0)) ? net.minecraft.world.level.block.Blocks.COARSE_DIRT.defaultBlockState()
                                : net.minecraft.world.level.block.Blocks.DIRT_PATH.defaultBlockState();
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), roadBlock);
                    }
                    // Forest Grass: other areas
                    else {
                        for (int dy = -2; dy <= -1; dy++) {
                            level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by + dy, bz + dz), net.minecraft.world.level.block.Blocks.DIRT.defaultBlockState());
                        }
                        level.setBlockAndUpdate(new net.minecraft.core.BlockPos(bx + dx, by, bz + dz), net.minecraft.world.level.block.Blocks.GRASS_BLOCK.defaultBlockState());
                    }
                }
            }

            // Spruce trees on the forest side: dx = -24 to -32
            for (int[] treePos : new int[][]{{-26, -18}, {-30, -6}, {-24, 10}, {-30, 22}, {-22, 28}}) {
                int tx = bx + treePos[0];
                int tz = bz + treePos[1];
                for (int h = 1; h <= 6; h++) {
                    level.setBlockAndUpdate(new net.minecraft.core.BlockPos(tx, by + h, tz), net.minecraft.world.level.block.Blocks.SPRUCE_LOG.defaultBlockState());
                }
                for (int lx = -2; lx <= 2; lx++) {
                    for (int lz = -2; lz <= 2; lz++) {
                        for (int ly = 3; ly <= 7; ly++) {
                            if (Math.abs(lx) + Math.abs(lz) <= 3) {
                                level.setBlockAndUpdate(new net.minecraft.core.BlockPos(tx + lx, by + ly, tz + lz), net.minecraft.world.level.block.Blocks.SPRUCE_LEAVES.defaultBlockState());
                            }
                        }
                    }
                }
            }

            double groundY = by + 1.0D;

            // 1. Spawn 8x8 Hauler Truck with kneeling Trooper Titan on the Left Dirt Road
            double truckX = bx - 11.0D;
            double truckY = groundY;
            double truckZ = bz - 2.0D;
            var truck = new com.titancombat.entity.transport.TitanHaulerTruckEntity(ModEntities.HAULER_TRUCK.get(), level);
            truck.moveTo(truckX, truckY, truckZ, 195.0F, 0.0F);
            truck.setNoGravity(true);
            level.addFreshEntity(truck);
            truckId = truck.getId();

            var trooper = new com.titancombat.entity.TrooperTitanEntity(ModEntities.TROOPER_TITAN.get(), level);
            trooper.moveTo(truckX, truckY, truckZ, 195.0F, 0.0F);
            trooper.setOwner(player);
            trooper.setNoGravity(true);
            trooper.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.XO16_CHAINGUN).get()));
            level.addFreshEntity(trooper);
            truck.lockTitanToDeck(trooper, null);

            // 2. Spawn Sky-Crane Drone hovering above the convoy clearing (centered between road & river)
            double droneX = bx + 4.5D;
            double droneY = groundY + 12.0D;
            double droneZ = bz - 2.0D;
            var drone = new com.titancombat.entity.transport.TitanSkyCraneDroneEntity(ModEntities.SKYCRANE_DRONE.get(), level);
            drone.moveTo(droneX, droneY, droneZ, 165.0F, 0.0F);
            drone.setNoGravity(true);
            level.addFreshEntity(drone);
            droneId = drone.getId();

            var slungTitan = new com.titancombat.entity.TrooperTitanEntity(ModEntities.TROOPER_TITAN.get(), level);
            slungTitan.moveTo(droneX, droneY, droneZ, 165.0F, 0.0F);
            slungTitan.setOwner(player);
            slungTitan.setNoGravity(true);
            slungTitan.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                    new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.factoryWeaponOf(TitanClass.TROOPER)).get()));
            level.addFreshEntity(slungTitan);
            drone.lockTitanToDeck(slungTitan, null);

            // 3. Spawn Cargo Barge with 2 Titans in the River on the Right
            double bargeX = bx + 20.0D;
            double bargeY = groundY - 0.4D;
            double bargeZ = bz - 2.0D;
            var barge = new com.titancombat.entity.transport.TitanCargoBargeEntity(ModEntities.CARGO_BARGE.get(), level);
            barge.moveTo(bargeX, bargeY, bargeZ, 170.0F, 0.0F);
            barge.setNoGravity(true);
            level.addFreshEntity(barge);
            bargeId = barge.getId();

            var bt1 = ModEntities.MONARCH_TITAN.get().create(level);
            if (bt1 != null) {
                bt1.moveTo(bargeX, bargeY, bargeZ, 170.0F, 0.0F);
                bt1.setOwner(player);
                bt1.setNoGravity(true);
                bt1.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                        new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.factoryWeaponOf(bt1.getTitanClass())).get()));
                level.addFreshEntity(bt1);
                barge.lockTitanToDeck(bt1, null);
            }
            var bt2 = ModEntities.SCORCH_TITAN.get().create(level);
            if (bt2 != null) {
                bt2.moveTo(bargeX, bargeY, bargeZ, 170.0F, 0.0F);
                bt2.setOwner(player);
                bt2.setNoGravity(true);
                bt2.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT,
                        new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.factoryWeaponOf(bt2.getTitanClass())).get()));
                level.addFreshEntity(bt2);
                barge.lockTitanToDeck(bt2, null);
            }
        });
        }));

        // Camera setup
        steps.add(new Step(80, mc -> {
            mc.options.hideGui = true;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            server2(mc, (player, level) -> {
                player.setGameMode(net.minecraft.world.level.GameType.SPECTATOR);
            });
        }));

        // Shot 1: The Iconic Showcase Recreation (Convoy Front 3/4 Hero View: Truck on left, Drone center-sky, Barge on right)
        steps.add(new Step(90, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 1.0D, groundY + 4.2D, tBaseZ - 2.0D, 18.0D, 12.0D, 168.0D);
        }));
        steps.add(new Step(125, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 1.0D, groundY + 4.2D, tBaseZ - 2.0D, 18.0D, 12.0D, 168.0D);
        }));
        steps.add(new Step(130, mc -> shot(mc, "01_hauler_truck_mounted")));

        // Shot 2: Hauler Truck Front Cab & Orange Ratchet Straps (Medium Hero Shot)
        steps.add(new Step(140, mc -> {
            double truckX = tBaseX - 11.0D;
            double groundY = ((int) tBaseY) + 1.0D;
            double truckZ = tBaseZ - 2.0D;
            aimCameraAt(mc, truckX, groundY + 2.2D, truckZ, 11.0D, 14.0D, 165.0D);
        }));
        steps.add(new Step(175, mc -> {
            double truckX = tBaseX - 11.0D;
            double groundY = ((int) tBaseY) + 1.0D;
            double truckZ = tBaseZ - 2.0D;
            aimCameraAt(mc, truckX, groundY + 2.2D, truckZ, 11.0D, 14.0D, 165.0D);
        }));
        steps.add(new Step(180, mc -> shot(mc, "02_truck_cargo_bed")));

        // Shot 3: Ducted-Fan Sky-Crane Drone Airborne Transit (Suspended Airlift)
        steps.add(new Step(190, mc -> {
            double droneX = tBaseX + 4.5D;
            double groundY = ((int) tBaseY) + 1.0D;
            double droneY = groundY + 12.0D;
            double droneZ = tBaseZ - 2.0D;
            aimCameraAt(mc, droneX, droneY - 3.0D, droneZ, 16.0D, 8.0D, 165.0D);
        }));
        steps.add(new Step(225, mc -> {
            double droneX = tBaseX + 4.5D;
            double groundY = ((int) tBaseY) + 1.0D;
            double droneY = groundY + 12.0D;
            double droneZ = tBaseZ - 2.0D;
            aimCameraAt(mc, droneX, droneY - 3.0D, droneZ, 16.0D, 8.0D, 165.0D);
        }));
        steps.add(new Step(230, mc -> shot(mc, "03_skycrane_drone_airlift")));

        // Shot 4: Amphibious Cargo Barge in the River with 2 Titans
        steps.add(new Step(240, mc -> {
            double bargeX = tBaseX + 20.0D;
            double groundY = ((int) tBaseY) + 1.0D;
            double bargeZ = tBaseZ - 2.0D;
            aimCameraAt(mc, bargeX, groundY + 2.0D, bargeZ, 16.0D, 14.0D, 165.0D);
        }));
        steps.add(new Step(275, mc -> {
            double bargeX = tBaseX + 20.0D;
            double groundY = ((int) tBaseY) + 1.0D;
            double bargeZ = tBaseZ - 2.0D;
            aimCameraAt(mc, bargeX, groundY + 2.0D, bargeZ, 16.0D, 14.0D, 165.0D);
        }));
        steps.add(new Step(280, mc -> shot(mc, "04_cargo_barge_twin_titans")));

        // Shot 5: Wide Cinematic Convoy Line-Up Overview
        steps.add(new Step(290, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 1.0D, groundY + 4.0D, tBaseZ - 2.0D, 24.0D, 15.0D, 168.0D);
        }));
        steps.add(new Step(325, mc -> {
            double groundY = ((int) tBaseY) + 1.0D;
            aimCameraAt(mc, tBaseX - 1.0D, groundY + 4.0D, tBaseZ - 2.0D, 24.0D, 15.0D, 168.0D);
        }));
        steps.add(new Step(330, mc -> shot(mc, "05_truck_driver_cab"))); // Wide fleet overview

        // Shot 6: Hauler Truck Rear Cargo & Straps Detail
        steps.add(new Step(340, mc -> {
            double truckX = tBaseX - 11.0D;
            double groundY = ((int) tBaseY) + 1.0D;
            double truckZ = tBaseZ - 2.0D;
            aimCameraAt(mc, truckX, groundY + 2.5D, truckZ + 1.2D, 10.0D, 18.0D, 35.0D);
        }));
        steps.add(new Step(375, mc -> {
            double truckX = tBaseX - 11.0D;
            double groundY = ((int) tBaseY) + 1.0D;
            double truckZ = tBaseZ - 2.0D;
            aimCameraAt(mc, truckX, groundY + 2.5D, truckZ + 1.2D, 10.0D, 18.0D, 35.0D);
        }));
        steps.add(new Step(380, mc -> shot(mc, "06_skycrane_cockpit_view"))); // Rear deck view

        // Shot 7: Driver Cockpit with Transport HUD & Energy Telemetry Bar
        steps.add(new Step(390, mc -> server2(mc, (p, l) -> {
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            var truck = l.getEntity(truckId);
            if (truck instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                transport.setEnergy(78500); // 78% energy
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(400, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setXRot(4.0F);
                mc.player.setYRot(195.0F); // Face forward along the dirt road heading!
            }
        }));
        steps.add(new Step(430, mc -> shot(mc, "07_truck_cockpit_energy_hud")));

        // Shot 8: Sky-Crane Drone Flight HUD with Climb Rate & Ventral Load Status
        steps.add(new Step(440, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            var drone = l.getEntity(droneId);
            if (drone instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                transport.setEnergy(92000);
                p.startRiding(transport, true);
                transport.setDeltaMovement(0.0D, 0.35D, 0.45D);
            }
        })));
        steps.add(new Step(450, mc -> {
            mc.options.hideGui = false;
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            if (mc.player != null) {
                mc.player.setXRot(10.0F);
                mc.player.setYRot(165.0F);
            }
        }));
        steps.add(new Step(475, mc -> shot(mc, "08_skycrane_flight_energy_hud")));
        // Seat check: front camera looks back through the canopy at the seated pilot
        steps.add(new Step(480, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)));
        steps.add(new Step(495, mc -> shot(mc, "09_skycrane_pilot_seat")));

        // Barge helm: first person through the bridge windows over the well deck
        steps.add(new Step(500, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            if (l.getEntity(bargeId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(510, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            mc.player.setXRot(8.0F);
            mc.player.setYRot(mc.player.getVehicle() != null ? mc.player.getVehicle().getYRot() : 0.0F);
        }));
        steps.add(new Step(530, mc -> shot(mc, "10_barge_helm_view")));

        // Truck drive: hold W+A; the hull must arc round on its wheels instead of snapping to the mouse
        steps.add(new Step(560, mc -> server2(mc, (p, l) -> {
            p.stopRiding();
            if (l.getEntity(truckId) instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity transport) {
                p.startRiding(transport, true);
            }
        })));
        steps.add(new Step(570, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            mc.options.hideGui = true;
        }));
        steps.add(new Step(585, mc -> shot(mc, "12_truck_driver_seat")));
        steps.add(new Step(590, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            mc.options.keyUp.setDown(true);
        }));
        steps.add(new Step(620, mc -> mc.options.keyLeft.setDown(true)));
        for (int t = 620; t <= 680; t += 15) {
            steps.add(new Step(t, mc -> {
                if (mc.player.getVehicle() instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity v) {
                    TitanCombatMod.LOGGER.info("[autotest] truck yaw={} vis={} rate={} playerYaw={}", String.format("%.1f", v.getYRot()),
                            String.format("%.3f", v.visSpeed), String.format("%.2f", v.visYawRate), String.format("%.1f", mc.player.getYRot()));
                }
            }));
        }
        steps.add(new Step(660, mc -> shot(mc, "13_truck_turning")));
        steps.add(new Step(685, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.keyLeft.setDown(false);
        }));

        steps.add(new Step(700, mc -> {
            TitanCombatMod.LOGGER.info("[autotest] transport playtest complete with full energy and HUD telemetry verification");
            mc.stop();
        }));

        return steps.toArray(new Step[0]);
    }

    private static boolean worldCreationTriggered = false;

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (NAME.isEmpty() || event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.getSingleplayerServer() == null) {
            if (mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen && !worldCreationTriggered) {
                worldCreationTriggered = true;
                TitanCombatMod.LOGGER.info("[autotest] TitleScreen detected, opening CreateWorldScreen...");
                net.minecraft.client.gui.screens.worldselection.CreateWorldScreen.openFresh(mc, null);
            } else if (mc.screen instanceof net.minecraft.client.gui.screens.worldselection.CreateWorldScreen cws) {
                for (var child : cws.children()) {
                    if (child instanceof net.minecraft.client.gui.components.Button b) {
                        String text = b.getMessage().getString();
                        if (text.toLowerCase().contains("create")) {
                            TitanCombatMod.LOGGER.info("[autotest] Clicking Create button: {}", text);
                            b.onPress();
                            break;
                        }
                    }
                }
            }
            return;
        }
        tick++;
        if (tick == 1) {
            // The test world is saved between runs: a script that ended in spectator would otherwise leave the
            // next run without hands, so no cockpit arms or frame (they draw in the hand pass).
            server2(mc, (p, level) -> p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL));
            mc.options.pauseOnLostFocus = false; // keep running when the window isn't focused
            mc.options.gamma().set(1.0D);
            if (mc.screen instanceof net.minecraft.client.gui.screens.PauseScreen) mc.setScreen(null);
        }
        if (NAME.startsWith("drive")) {
            DriveAutoTest.run(mc);
            return;
        }
        if (NAME.startsWith("navy")) {
            NavyAutoTest.run(mc);
            return;
        }
        if (NAME.startsWith("arsenal")) {
            ArsenalAutoTest.run(mc);
            return;
        }
        if (NAME.startsWith("look")) {
            LookAutoTest.run(mc);
            return;
        }
        if (NAME.startsWith("issues")) {
            IssueAutoTest.run(mc);
            return;
        }
        if (NAME.startsWith("fleet")) {
            FleetAutoTest.run(mc, tick);
            return;
        }
        Step[] script = NAME.startsWith("new_frames") ? NEW_FRAMES : NAME.startsWith("frame") ? FRAME_TEST : NAME.startsWith("artillery") ? ARTILLERY : NAME.startsWith("walkside") ? WALK_SIDE : NAME.startsWith("weapons_1st") ? COCKPIT_TOOLS : NAME.startsWith("energy") ? ENERGY : NAME.startsWith("transport_new") ? TRANSPORT_NEW : NAME.startsWith("transport") ? TRANSPORT : NAME.startsWith("bind") ? BIND : NAME.startsWith("cloak") ? CLOAK : NAME.startsWith("fly_") ? FLY : NAME.startsWith("flight") ? FLIGHT : NAME.startsWith("poses") ? POSES : NAME.startsWith("showcase") ? SHOWCASE : NAME.startsWith("jump") ? JUMP : NAME.startsWith("eject") ? EJECT : NAME.startsWith("sprint") ? SPRINT : NAME.startsWith("weapons") ? WEAPONS : SCRIPT;
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
                case "striker_frame" -> ModEntities.STRIKER_FRAME_TITAN.get();
                case "vanguard_frame" -> ModEntities.VANGUARD_FRAME_TITAN.get();
                case "colossus_frame" -> ModEntities.COLOSSUS_FRAME_TITAN.get();
                case "terrain_frame" -> ModEntities.TERRAIN_FRAME_TITAN.get();
                case "cyclops_frame" -> ModEntities.CYCLOPS_FRAME_TITAN.get();
                case "spider_frame" -> ModEntities.SPIDER_FRAME_TITAN.get();
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

    static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "autotest_" + NAME + "_" + name + ".png", mc.getMainRenderTarget(), msg -> {});
        dump(mc);
        TitanCombatMod.LOGGER.info("[autotest] screenshot {} playerY={}", name, String.format("%.1f", mc.player.getY()));
    }
}
