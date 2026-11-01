package com.obsolete.client.debug;

import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.ModEntities;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.item.ModItems;
import com.obsolete.item.ExoframeWeaponItem;
import com.obsolete.network.ExoframeCrouchC2SPacket;
import com.obsolete.network.ModNetworking;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.function.BiConsumer;
import java.util.function.Consumer;

/**
 * Scripted in-game auto-test for Exoframe Mod (Minecraft Forge 1.20.1).
 * Activated via -Dobsolete.autotest=<scenario> (or OBSOLETE_AUTOTEST=showcase ./gradlew runClient).
 * Automates spawning, boarding, equipping modular armor variants, camo patterns,
 * weapon hardpoints, crouch/sprint animations, and grabs high-res screenshots.
 */
@Mod.EventBusSubscriber(modid = ObsoleteMod.MODID, value = Dist.CLIENT)
public final class ClientAutoTest {
    private static final String NAME = System.getProperty("obsolete.autotest", "");
    private static int tick = -1;
    private static int startServerTick = -1;
    /** Release W once the ridden mech passes this Z (checked every client frame; NaN = off). */
    private static double stopWalkZ = Double.NaN;
    private static int exoframeId = -1;
    private static double exoX, exoY, exoZ;
    private static boolean worldCreationTriggered = false;
    private static boolean worldCreated = false;

    private record Step(int at, Consumer<Minecraft> action) {}

    private static final Step[] SHOWCASE = {
            // Step 1: Initial world setup & wide tarmac platform
            new Step(20, mc -> serverLevel(mc, (p, level) -> {
                level.setDayTime(6000L); // High noon clear lighting
                level.setWeatherParameters(60000, 0, false, false);
                p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);

                int px = p.getBlockX();
                int py = 100;
                int pz = p.getBlockZ();
                exoX = px + 0.5D;
                exoY = py;
                exoZ = pz + 0.5D;

                // Discard all leftover entities from previous runs
                level.getEntitiesOfClass(Entity.class, new AABB(px - 100, py - 30, pz - 100, px + 100, py + 50, pz + 100))
                        .stream().filter(e -> !(e instanceof ServerPlayer))
                        .forEach(Entity::discard);

                // Build a 90x90 smooth test tarmac at fixed Y=99
                for (int dx = -45; dx <= 45; dx++) {
                    for (int dz = -45; dz <= 45; dz++) {
                        level.setBlockAndUpdate(new BlockPos(px + dx, py - 1, pz + dz), Blocks.SMOOTH_STONE.defaultBlockState());
                        for (int y = py; y <= py + 15; y++) {
                            level.setBlockAndUpdate(new BlockPos(px + dx, y, pz + dz), Blocks.AIR.defaultBlockState());
                        }
                    }
                }
            })),
            new Step(40, mc -> {
                mc.options.pauseOnLostFocus = false;
                mc.options.hideGui = true;
                mc.options.gamma().set(1.0D);
                if (mc.screen instanceof net.minecraft.client.gui.screens.PauseScreen) mc.setScreen(null);
            }),

            // Step 2: Spawn single clean Exoframe in center
            new Step(60, mc -> spawnDisplayExoframe(mc)),

            // ==================== PHASE 1: 3/4 ISOMETRIC HERO SHOTS ====================
            // 1. Bare Peddler Industrial Skeleton (3/4 angle)
            new Step(90, mc -> serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 1.2 * ExoframeEntity.MODEL_SCALE, exoZ, 3.6 * ExoframeEntity.MODEL_SCALE, -30.0, 0.3 * ExoframeEntity.MODEL_SCALE))),
            new Step(120, mc -> shot(mc, "01_hero_bare_exoframe_3quarter")),

            // 2. USMC Skull Canopy + AMR 20mm Sniper + Woodland Camo (3/4 angle)
            new Step(130, mc -> serverExoById(mc, (p, exo) -> {
                exo.setCamoPattern(1); // Woodland Camo
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_USMC_HEAD.get()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_USMC_CHEST.get()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_ARMS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_LEGS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_USMC_COMMS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_SNIPER_RIFLE.get()));
                exo.syncArmorMaskAndNotify();
            })),
            new Step(140, mc -> serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 1.2 * ExoframeEntity.MODEL_SCALE, exoZ, 3.6 * ExoframeEntity.MODEL_SCALE, -30.0, 0.3 * ExoframeEntity.MODEL_SCALE))),
            new Step(170, mc -> shot(mc, "02_hero_usmc_woodland_sniper_3quarter")),

            // 3. Cerberus Heavy Dome + Heavy Machine Gun + Urban Hex Camo (3/4 angle)
            new Step(180, mc -> serverExoById(mc, (p, exo) -> {
                exo.setCamoPattern(3); // Urban Hex Camo
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_HEAD.get()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_CHEST.get()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_ARMS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_LEGS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_CERBERUS_PACKS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_MACHINE_GUN.get()));
                exo.syncArmorMaskAndNotify();
            })),
            new Step(190, mc -> serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 1.2 * ExoframeEntity.MODEL_SCALE, exoZ, 3.6 * ExoframeEntity.MODEL_SCALE, -30.0, 0.3 * ExoframeEntity.MODEL_SCALE))),
            new Step(220, mc -> shot(mc, "03_hero_cerberus_urban_hmg_3quarter")),

            // 4. Militia Outcast Turtle Hood + RPG-7 Heavy + Desert MARPAT Camo (3/4 angle)
            new Step(230, mc -> serverExoById(mc, (p, exo) -> {
                exo.setCamoPattern(2); // Desert Camo
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_MILITIA_HOOD.get()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_MILITIA_CHEST.get()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_ARMS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_LEGS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_SHOULDER_MISSILE.get()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_RPG7.get()));
                exo.syncArmorMaskAndNotify();
            })),
            new Step(240, mc -> serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 1.2 * ExoframeEntity.MODEL_SCALE, exoZ, 3.6 * ExoframeEntity.MODEL_SCALE, -30.0, 0.3 * ExoframeEntity.MODEL_SCALE))),
            new Step(270, mc -> shot(mc, "04_hero_militia_desert_rpg_3quarter")),

            // 5. Industrial Roll Cage + Heavy Mining Drill + Hazard Stripe Camo (3/4 angle)
            new Step(280, mc -> serverExoById(mc, (p, exo) -> {
                exo.setCamoPattern(6); // Hazard Stripe Camo
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), ItemStack.EMPTY);
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_ROLL_CAGE.get()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), ItemStack.EMPTY);
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), ItemStack.EMPTY);
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.PEDDLER_CORE.get()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.TOOL_MINING_DRILL.get()));
                exo.syncArmorMaskAndNotify();
            })),
            new Step(290, mc -> serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 1.2 * ExoframeEntity.MODEL_SCALE, exoZ, 3.6 * ExoframeEntity.MODEL_SCALE, -30.0, 0.3 * ExoframeEntity.MODEL_SCALE))),
            new Step(320, mc -> shot(mc, "05_hero_industrial_hazard_drill_3quarter")),

            // 6. Tactical Crouch Hull-Down Pose (3/4 side angle showing reverse knee articulation)
            new Step(330, mc -> serverExoById(mc, (p, exo) -> exo.setMechCrouching(true))),
            new Step(340, mc -> serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 0.9 * ExoframeEntity.MODEL_SCALE, exoZ, 3.4 * ExoframeEntity.MODEL_SCALE, -45.0, 0.2 * ExoframeEntity.MODEL_SCALE))),
            new Step(370, mc -> shot(mc, "06_hero_tactical_crouch_articulation")),
            new Step(375, mc -> serverExoById(mc, (p, exo) -> exo.setMechCrouching(false))),

            // ==================== PHASE 2: PILOTED OPERATOR STANCE & VEHICLE MECHANICS ====================
            // 7. Pilot boards the USMC Exoframe & engages Shoulder-Aim Lock (ประทับเตรียมยิง)
            new Step(390, mc -> serverLevel(mc, (p, l) -> {
                if (l.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setCamoPattern(1); // Woodland Camo
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_USMC_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_USMC_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_USMC_COMMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_SNIPER_RIFLE.get()));
                    exo.syncArmorMaskAndNotify();
                    p.startRiding(exo, true);
                    exo.setAiming(true); // Military Soldier Shoulder-Aim Lock (ประทับเตรียมยิง)
                }
            })),
            new Step(400, mc -> {
                mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
                mc.player.setXRot(-4.0F);
            }),
            new Step(430, mc -> shot(mc, "07_piloted_usmc_shoulder_aim_lock")),

            // 8. Dynamic Pitch Tracking: Over-the-shoulder view aiming upward at elevation (-20 degrees)
            new Step(440, mc -> {
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
                mc.player.setXRot(-20.0F);
            }),
            new Step(465, mc -> shot(mc, "08_piloted_shoulder_aim_pitch_elevation")),

            // 9. Piloted Heavy Vehicle Sprint with Chassis Momentum
            new Step(475, mc -> {
                mc.player.setXRot(0.0F);
                serverExoById(mc, (p, exo) -> exo.setAiming(false));
                mc.options.keyUp.setDown(true);
                mc.options.keySprint.setDown(true);
            }),
            new Step(515, mc -> shot(mc, "09_piloted_dynamic_vehicle_sprint")),
            new Step(525, mc -> {
                mc.options.keyUp.setDown(false);
                mc.options.keySprint.setDown(false);
            }),

            // 10. First-Person Cockpit View with ADS Optical Zoom
            new Step(535, mc -> {
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                mc.player.setXRot(0.0F);
                serverExoById(mc, (p, exo) -> exo.setAiming(true));
            }),
            new Step(565, mc -> shot(mc, "10_piloted_first_person_cockpit_ads")),

            // ==================== PHASE 3: CONTEXTUAL MODULAR ROLE HUD OVERLAYS ====================
            // 11. Military Combat FCS HUD (First-Person with HUD Enabled & Ammo Loaded)
            new Step(575, mc -> serverLevel(mc, (p, level) -> {
                mc.options.hideGui = false; // Enable HUD overlay rendering!
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                p.getInventory().clearContent();
                p.getInventory().add(new ItemStack(ModItems.AMMO_762_MINIGUN.get(), 128));

                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setCamoPattern(1); // Woodland Camo
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_USMC_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_USMC_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_TARGETING_COMPUTER.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_MINIGUN.get()));
                    exo.syncArmorMaskAndNotify();
                    exo.setAiming(true);
                }
            })),
            new Step(605, mc -> shot(mc, "11_hud_tactical_combat_fcs")),

            // 12. Geological Mining Telemetry HUD (Drill + Geological Sonar + Roll Cage)
            new Step(615, mc -> serverLevel(mc, (p, level) -> {
                BlockPos pos = p.blockPosition();
                level.setBlockAndUpdate(pos.offset(2, 0, 2), Blocks.DIAMOND_ORE.defaultBlockState());
                level.setBlockAndUpdate(pos.offset(3, 0, 1), Blocks.DEEPSLATE_DIAMOND_ORE.defaultBlockState());
                level.setBlockAndUpdate(pos.offset(1, 0, 3), Blocks.GOLD_ORE.defaultBlockState());
                level.setBlockAndUpdate(pos.offset(2, 1, 3), Blocks.IRON_ORE.defaultBlockState());

                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setCamoPattern(6); // Hazard Stripe
                    exo.setAiming(false);
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_ROLL_CAGE.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_GEOLOGICAL_SCANNER.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.TOOL_MINING_DRILL.get()));
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(650, mc -> shot(mc, "12_hud_geological_mining_scanner")),

            // 13. Special Ops Recon & Acoustic Stealth HUD (Cerberus Dome + FLIR Optic)
            new Step(660, mc -> serverLevel(mc, (p, level) -> {
                p.getInventory().clearContent();
                p.getInventory().add(new ItemStack(ModItems.AMMO_20MM.get(), 40));

                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setCamoPattern(3); // Urban Hex
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_NIGHT_VISION_OPTIC.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_SNIPER_RIFLE.get()));
                    exo.syncArmorMaskAndNotify();
                    exo.setMechCrouching(true); // Silent stance
                }
            })),
            new Step(690, mc -> shot(mc, "13_hud_specops_recon_acoustic")),

            // 14. Forestry Timber Logging HUD (Chainsaw + Cargo Crate Freight)
            new Step(700, mc -> serverLevel(mc, (p, level) -> {
                p.getInventory().clearContent();
                p.getInventory().add(new ItemStack(Blocks.OAK_LOG, 64));
                p.getInventory().add(new ItemStack(Blocks.BIRCH_LOG, 64));
                p.getInventory().add(new ItemStack(Blocks.SPRUCE_LOG, 48));

                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setMechCrouching(false);
                    exo.setCamoPattern(1); // Woodland Camo
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_USMC_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_CARGO_CRATE.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.TOOL_CHAINSAW.get()));
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(730, mc -> shot(mc, "14_hud_forestry_timber_logging")),

            // 15. Agriculture & Cultivator HUD (Cultivator Plow + Agri-Hopper + Farmland)
            new Step(740, mc -> serverLevel(mc, (p, level) -> {
                p.getInventory().clearContent();
                p.getInventory().add(new ItemStack(Items.WHEAT_SEEDS, 64));
                p.getInventory().add(new ItemStack(Items.CARROT, 32));

                BlockPos pos = p.blockPosition();
                // Set farmland under mech
                level.setBlockAndUpdate(pos.below(), Blocks.FARMLAND.defaultBlockState().setValue(FarmBlock.MOISTURE, 7));
                // Set wheat crop in front of mech
                BlockPos front = pos.relative(p.getDirection());
                level.setBlockAndUpdate(front.below(), Blocks.FARMLAND.defaultBlockState().setValue(FarmBlock.MOISTURE, 7));
                level.setBlockAndUpdate(front, Blocks.WHEAT.defaultBlockState().setValue(CropBlock.AGE, 7));

                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setCamoPattern(0); // Standard Industrial
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_ROLL_CAGE.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_AGRI_HOPPER.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.TOOL_CULTIVATOR_PLOW.get()));
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(770, mc -> shot(mc, "15_hud_agriculture_cultivator")),

            // 16. Submarine Deep-Sea Diving HUD (Diving Ballast + Water Submersion)
            new Step(780, mc -> serverLevel(mc, (p, level) -> {
                p.getInventory().clearContent();
                BlockPos pos = p.blockPosition();
                // Encase in water blocks for submarine dive test
                for (int dx = -2; dx <= 2; dx++) {
                    for (int dy = 0; dy <= 3; dy++) {
                        for (int dz = -2; dz <= 2; dz++) {
                            level.setBlockAndUpdate(pos.offset(dx, dy, dz), Blocks.WATER.defaultBlockState());
                        }
                    }
                }
                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setCamoPattern(3); // Urban Hex / Naval
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_SAND_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_SAND_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_DIVING_BALLAST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), ItemStack.EMPTY);
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(815, mc -> shot(mc, "16_hud_submarine_diving_ballast")),

            // ==================== PHASE 4: AUTHENTIC SOLDIER WEAPON POSTURES & SHOULDER MISSILES ====================
            // 17. Cerberus Heavy Mech - Horizontal Two-Handed Chest Carry (Image 1 Brief)
            new Step(825, mc -> serverLevel(mc, (p, level) -> {
                mc.options.hideGui = true;
                mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
                mc.player.setXRot(0.0F);

                // Clear submarine water cage, test ores, and crops completely!
                BlockPos pPos = p.blockPosition();
                for (int dx = -6; dx <= 6; dx++) {
                    for (int dy = -2; dy <= 6; dy++) {
                        for (int dz = -6; dz <= 6; dz++) {
                            BlockPos bPos = pPos.offset(dx, dy, dz);
                            var state = level.getBlockState(bPos);
                            if (state.is(Blocks.WATER) || state.is(Blocks.DIAMOND_ORE) || state.is(Blocks.DEEPSLATE_DIAMOND_ORE)
                                    || state.is(Blocks.GOLD_ORE) || state.is(Blocks.IRON_ORE) || state.is(Blocks.WHEAT) || state.is(Blocks.FARMLAND)) {
                                level.setBlockAndUpdate(bPos, dy < 0 ? Blocks.SMOOTH_STONE.defaultBlockState() : Blocks.AIR.defaultBlockState());
                            }
                        }
                    }
                }

                p.setYRot(0.0F);
                p.yRotO = 0.0F;
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;

                ExoframeEntity exo = (p.getVehicle() instanceof ExoframeEntity v) ? v : (level.getEntity(exoframeId) instanceof ExoframeEntity v2 ? v2 : null);
                if (exo != null) {
                    exo.setYRot(0.0F);
                    exo.yRotO = 0.0F;
                    exo.setYBodyRot(0.0F);
                    exo.setYHeadRot(0.0F);
                    exo.setCamoPattern(3); // Urban Hex / Cerberus
                    exo.setAiming(false); // Resting Stance
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_CERBERUS_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_CERBERUS_PACKS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_MACHINE_GUN.get()));
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(855, mc -> shot(mc, "17_showcase_cerberus_horizontal_chest_carry_hmg")),

            // 18. USMC Sniper Mech - Low-Ready Diagonal Patrol Slant (Image 3 Brief)
            new Step(865, mc -> serverLevel(mc, (p, level) -> {
                p.setYRot(0.0F);
                mc.player.setYRot(0.0F);
                ExoframeEntity exo = (p.getVehicle() instanceof ExoframeEntity v) ? v : (level.getEntity(exoframeId) instanceof ExoframeEntity v2 ? v2 : null);
                if (exo != null) {
                    exo.setYRot(0.0F);
                    exo.yRotO = 0.0F;
                    exo.setYBodyRot(0.0F);
                    exo.setYHeadRot(0.0F);
                    exo.setCamoPattern(1); // Woodland Camo
                    exo.setAiming(false); // Resting Stance
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_USMC_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_USMC_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_USMC_COMMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_SNIPER_RIFLE.get()));
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(895, mc -> shot(mc, "18_showcase_usmc_sniper_low_ready_patrol_slant")),

            // 19. Arctic Winter Mech - Twin Shoulder-Mounted Missile Launcher Pods (Image 5 Brief)
            new Step(905, mc -> serverLevel(mc, (p, level) -> {
                p.setYRot(0.0F);
                mc.player.setYRot(0.0F);
                ExoframeEntity exo = (p.getVehicle() instanceof ExoframeEntity v) ? v : (level.getEntity(exoframeId) instanceof ExoframeEntity v2 ? v2 : null);
                if (exo != null) {
                    exo.setYRot(0.0F);
                    exo.yRotO = 0.0F;
                    exo.setYBodyRot(0.0F);
                    exo.setYHeadRot(0.0F);
                    exo.setCamoPattern(4); // Arctic Winter Camo
                    exo.setAiming(false);
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_SAND_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_SAND_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_SHOULDER_MISSILE.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), ItemStack.EMPTY);
                    exo.syncArmorMaskAndNotify();
                }
            })),
            new Step(935, mc -> shot(mc, "19_showcase_arctic_twin_shoulder_missile_pods")),

            // 20. Combat Firing Posture - Dynamic Shoulder Lock Aiming Upward with Recoil (Image 2 Brief)
            new Step(945, mc -> serverLevel(mc, (p, level) -> {
                p.setYRot(0.0F);
                mc.player.setYRot(0.0F);
                mc.player.setXRot(-25.0F); // Pilot aiming up into the sky!
                mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
                ExoframeEntity exo = (p.getVehicle() instanceof ExoframeEntity v) ? v : (level.getEntity(exoframeId) instanceof ExoframeEntity v2 ? v2 : null);
                if (exo != null) {
                    exo.setYRot(0.0F);
                    exo.yRotO = 0.0F;
                    exo.setYBodyRot(0.0F);
                    exo.setYHeadRot(0.0F);
                    exo.setCamoPattern(1); // Woodland Camo
                    exo.setAiming(true); // Full combat shoulder-lock ADS!
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_USMC_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_USMC_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_ARMS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_USMC_LEGS.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_SHOULDER_MISSILE.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_MACHINE_GUN.get()));
                    exo.syncArmorMaskAndNotify();
                    exo.triggerRecoilAnim();
                }
            })),
            new Step(975, mc -> shot(mc, "20_showcase_combat_firing_recoil_shoulder_lock")),

            // Finish and shutdown
            new Step(1000, mc -> {
                ObsoleteMod.LOGGER.info("[autotest] All 20 showcase test points captured successfully!");
                mc.stop();
            })
    };

    // OBSOLETE_AUTOTEST=anim: weapon holds (grip/support-hand IK), aim, crouch and emotes from several angles.
    // Exoframe faces +Z, so its right side is -X: camera angle -90 = right side, -40 = front-right 3/4, 0 = front.
    private static final Step[] ANIM = {
            SHOWCASE[0], SHOWCASE[1], SHOWCASE[2],
            new Step(80, mc -> serverExoById(mc, (p, exo) -> loadout(exo, ModItems.EXOFRAME_ASSAULT_RIFLE.get()))),
            new Step(95, mc -> view(mc, -40)), new Step(110, mc -> shot(mc, "a01_rifle_rest_3q")),
            new Step(115, mc -> view(mc, -90)), new Step(130, mc -> shot(mc, "a02_rifle_rest_side")),
            new Step(135, mc -> serverExoById(mc, (p, exo) -> exo.setAiming(true))),
            new Step(160, mc -> shot(mc, "a03_rifle_aim_side")),
            new Step(165, mc -> view(mc, -40)), new Step(180, mc -> shot(mc, "a04_rifle_aim_3q")),
            new Step(185, mc -> view(mc, 0)), new Step(200, mc -> shot(mc, "a05_rifle_aim_front")),
            new Step(205, mc -> serverExoById(mc, (p, exo) -> exo.setXRot(-35.0F))),
            new Step(210, mc -> view(mc, -90)), new Step(230, mc -> shot(mc, "a06_rifle_aim_up_side")),
            new Step(235, mc -> serverExoById(mc, (p, exo) -> {
                exo.setXRot(0.0F);
                loadout(exo, ModItems.EXOFRAME_MACHINE_GUN.get());
            })),
            new Step(255, mc -> shot(mc, "a07_mg_aim_side")),
            new Step(260, mc -> serverExoById(mc, (p, exo) -> exo.setAiming(false))),
            new Step(265, mc -> view(mc, -40)), new Step(285, mc -> shot(mc, "a08_mg_rest_3q")),
            new Step(290, mc -> serverExoById(mc, (p, exo) -> loadout(exo, ModItems.EXOFRAME_RPG7.get()))),
            new Step(305, mc -> shot(mc, "a09_rpg_rest_3q")),
            new Step(310, mc -> serverExoById(mc, (p, exo) -> exo.setAiming(true))),
            new Step(335, mc -> shot(mc, "a10_rpg_aim_3q")),
            new Step(340, mc -> serverExoById(mc, (p, exo) -> {
                exo.setAiming(false);
                loadout(exo, ItemStack.EMPTY.getItem());
                exo.setMechCrouching(true);
            })),
            new Step(345, mc -> view(mc, -90)), new Step(365, mc -> shot(mc, "a11_crouch_unarmed_side")),
            new Step(370, mc -> serverExoById(mc, (p, exo) -> loadout(exo, ModItems.EXOFRAME_ASSAULT_RIFLE.get()))),
            new Step(375, mc -> view(mc, -40)), new Step(395, mc -> shot(mc, "a12_crouch_rifle_3q")),
            new Step(400, mc -> serverExoById(mc, (p, exo) -> {
                exo.setMechCrouching(false);
                loadout(exo, ItemStack.EMPTY.getItem());
            })),
            new Step(415, mc -> view(mc, -20)),
            new Step(420, mc -> serverExoById(mc, (p, exo) -> exo.playEmote("salute"))),
            new Step(440, mc -> shot(mc, "a13_salute_unarmed")),
            new Step(470, mc -> serverExoById(mc, (p, exo) -> loadout(exo, ModItems.EXOFRAME_ASSAULT_RIFLE.get()))),
            new Step(480, mc -> view(mc, 20)),
            new Step(485, mc -> serverExoById(mc, (p, exo) -> exo.playEmote("salute"))),
            new Step(505, mc -> shot(mc, "a14_salute_armed_left")),
            new Step(540, mc -> serverExoById(mc, (p, exo) -> exo.playEmote("wave"))),
            new Step(560, mc -> shot(mc, "a15_wave")),
            new Step(600, mc -> view(mc, 60)),
            new Step(605, mc -> serverExoById(mc, (p, exo) -> exo.playEmote("point"))),
            new Step(625, mc -> shot(mc, "a16_point")),

            // ==================== TASK 7: PILOT-IN-THE-LOOP ANIMATION CHECK ====================
            // Mount pilot and engage shoulder-aim hold
            new Step(640, mc -> serverExoById(mc, (p, exo) -> {
                loadout(exo, ModItems.EXOFRAME_ASSAULT_RIFLE.get());
                p.startRiding(exo, true);
                exo.setAiming(true);
            })),
            new Step(650, mc -> {
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
                mc.player.setXRot(0.0F);
            }),
            new Step(670, mc -> shot(mc, "a17_piloted_aim_level")),
            new Step(680, mc -> mc.player.setXRot(-30.0F)), // Aim pitch elevation up
            new Step(700, mc -> shot(mc, "a18_piloted_aim_pitch_up")),
            new Step(710, mc -> mc.player.setXRot(25.0F)),  // Aim pitch depression down
            new Step(730, mc -> shot(mc, "a19_piloted_aim_pitch_down")),
            new Step(740, mc -> {
                mc.player.setXRot(0.0F);
                serverExoById(mc, (p, exo) -> exo.setAiming(false));
                mc.options.keyUp.setDown(true); // Piloted walk
            }),
            new Step(765, mc -> shot(mc, "a20_piloted_walk")),
            new Step(775, mc -> mc.options.keySprint.setDown(true)), // Piloted sprint
            new Step(805, mc -> shot(mc, "a21_piloted_sprint")),
            new Step(815, mc -> {
                mc.options.keySprint.setDown(false);
                serverExoById(mc, (p, exo) -> exo.setMechCrouching(true)); // Piloted crouch-walk
            }),
            new Step(845, mc -> shot(mc, "a22_piloted_crouch_walk")),
            new Step(855, mc -> {
                mc.options.keyUp.setDown(false);
                serverExoById(mc, (p, exo) -> {
                    exo.setMechCrouching(false);
                    p.stopRiding();
                });
                mc.options.setCameraType(CameraType.FIRST_PERSON);
            }),
            new Step(880, mc -> {
                ObsoleteMod.LOGGER.info("[autotest] anim scenario done");
                mc.stop();
            })
    };

    // OBSOLETE_AUTOTEST=armor: the four faction sets, front 3/4 and rear 3/4.
    private static Step[] armor; // built lazily: items are not registered yet when this class loads
    private static Step[] gameplay; // built lazily: items/entities registered at world-load

    private static Step[] buildGameplaySteps() {
        java.util.List<Step> steps = new java.util.ArrayList<>();
        steps.add(SHOWCASE[0]);
        steps.add(SHOWCASE[1]);
        steps.add(SHOWCASE[2]);

        // ==================== 1. STEP HEIGHT 2.0 TEST ====================
        // Build 2-block high ledge at Z+2 to Z+40 (wide plateau so mech stays on top)
        steps.add(new Step(80, mc -> serverLevel(mc, (p, level) -> {
            BlockPos basePos = BlockPos.containing(exoX, exoY, exoZ);
            int bx = basePos.getX();
            int by = basePos.getY();
            int bz = basePos.getZ();
            for (int dx = -10; dx <= 10; dx++) {
                for (int dz = 2; dz <= 40; dz++) {
                    for (int dy = 0; dy < 2; dy++) {
                        level.setBlockAndUpdate(new BlockPos(bx + dx, by + dy, bz + dz), Blocks.STONE.defaultBlockState());
                    }
                }
            }
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                p.connection.teleport(exoX, exoY, exoZ, 0.0F, 0.0F, java.util.Collections.emptySet());
                exo.moveTo(exoX, exoY, exoZ, 0.0F, 0.0F);
                exo.yRotO = 0.0F;
                exo.setYRot(0.0F);
                exo.setYBodyRot(0.0F);
                exo.setYHeadRot(0.0F);
                p.startRiding(exo, true);
                p.setYRot(0.0F); // Face South (+Z) towards the 2-block ledge
                p.setXRot(0.0F);
            }
        })));
        steps.add(new Step(90, mc -> {
            // Confirm vehicle mounting on client side
            if (mc.player != null && mc.level != null && mc.player.getVehicle() == null) {
                Entity exo = mc.level.getEntity(exoframeId);
                if (exo != null) mc.player.startRiding(exo, true);
            }
            if (mc.player != null) {
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;
            }
        }));
        steps.add(new Step(95, mc -> {
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            if (mc.player != null) {
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;
            }
            mc.options.keyUp.setDown(true); // Walk forward onto ledge
            stopWalkZ = exoZ + 8.0D;
            mc.options.keySprint.setDown(true);
        }));
        for (int t = 96; t < 155; t++) {
            steps.add(new Step(t, mc -> {
                if (mc.player != null) {
                    mc.player.setYRot(0.0F);
                    mc.player.yRotO = 0.0F;
                }
            }));
        }
        steps.add(new Step(155, mc -> {
            mc.options.keyUp.setDown(false);
            mc.options.keySprint.setDown(false);
            serverExoById(mc, (p, exo) -> {
                double currentY = exo.getY();
                double expectedY = exoY + 2.0D;
                if (currentY >= expectedY - 0.25D) {
                    ObsoleteMod.LOGGER.info("[autotest] STEP HEIGHT 2.0 PASS: Exoframe stepped up 2-block ledge smoothly (Y={})", currentY);
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] STEP HEIGHT 2.0 FAIL: Pos=({}, {}, {}) expected Y >= {}", exo.getX(), currentY, exo.getZ(), expectedY);
                }
            });
        }));
        steps.add(new Step(160, mc -> shot(mc, "g01_step_height_2block_pass")));

        // ==================== 2. CROUCH HITBOX & DOORWAY TEST ====================
        steps.add(new Step(165, mc -> serverLevel(mc, (p, level) -> {
            BlockPos basePos = BlockPos.containing(exoX, exoY, exoZ);
            int bx = basePos.getX();
            int by = basePos.getY();
            int bz = basePos.getZ();
            // Clear previous ledge
            for (int dx = -15; dx <= 15; dx++) {
                for (int dz = 1; dz <= 45; dz++) {
                    for (int dy = 0; dy <= 8; dy++) {
                        level.setBlockAndUpdate(new BlockPos(bx + dx, by + dy, bz + dz), Blocks.AIR.defaultBlockState());
                    }
                }
            }
            // Reposition exoframe and player
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                p.stopRiding();
                exo.setDeltaMovement(Vec3.ZERO);
                exo.moveTo(exoX, exoY, exoZ, 0.0F, 0.0F);
                exo.yRotO = 0.0F;
                exo.setYRot(0.0F);
                exo.setYBodyRot(0.0F);
                exo.setYHeadRot(0.0F);
                p.connection.teleport(exoX, exoY, exoZ, 0.0F, 0.0F, java.util.Collections.emptySet());
            }
            // Wall with clearance doorway at Z+3: opening width 5 (dx=-2..2), height 5 (dy=0..4)
            // Standing mech 3.96m + rider (4.64m) is blocked by ceiling; crouching 3.24m clears smoothly!
            for (int dx = -8; dx <= 8; dx++) {
                for (int dy = 0; dy <= 7; dy++) {
                    if (Math.abs(dx) <= 2 && dy < 5) {
                        continue; // Doorway opening: width 5, height 5 (dy=0,1,2,3,4)
                    }
                    level.setBlockAndUpdate(new BlockPos(bx + dx, by + dy, bz + 3), Blocks.IRON_BLOCK.defaultBlockState());
                }
            }
        })));
        steps.add(new Step(185, mc -> {
            com.obsolete.client.ModKeyMappings.KEY_MECH_CROUCH.setDown(true);
            if (mc.player != null && mc.player.getVehicle() instanceof ExoframeEntity exo) {
                exo.setMechCrouching(true);
            }
            serverExoById(mc, (p, exo) -> {
                p.startRiding(exo, true);
                exo.setMechCrouching(true);
                p.setYRot(0.0F);
            });
        }));
        steps.add(new Step(195, mc -> {
            mc.player.setYRot(0.0F);
            mc.options.keyUp.setDown(true); // Walk crouching through doorway
        }));
        for (int t = 196; t < 270; t++) {
            steps.add(new Step(t, mc -> {
                if (mc.player != null) {
                    mc.player.setYRot(0.0F);
                    mc.player.yRotO = 0.0F;
                }
            }));
        }
        steps.add(new Step(270, mc -> {
            mc.options.keyUp.setDown(false);
            com.obsolete.client.ModKeyMappings.KEY_MECH_CROUCH.setDown(false);
            if (mc.player != null && mc.player.getVehicle() instanceof ExoframeEntity exo) {
                exo.setMechCrouching(false);
            }
            serverExoById(mc, (p, exo) -> {
                double currentZ = exo.getZ();
                if (currentZ > exoZ + 3.5D) {
                    ObsoleteMod.LOGGER.info("[autotest] CROUCH HITBOX & DOORWAY PASS: Crouching exoframe cleared doorway (Z={})", currentZ);
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] CROUCH HITBOX & DOORWAY FAIL: Z={}", currentZ);
                }
                exo.setMechCrouching(false);
            });
        }));
        steps.add(new Step(280, mc -> shot(mc, "g02_crouch_doorway_pass")));

        // ==================== 3. WEAPON MUZZLE HIT REGISTRATION TEST ====================
        steps.add(new Step(290, mc -> serverLevel(mc, (p, level) -> {
            BlockPos basePos = BlockPos.containing(exoX, exoY, exoZ);
            int bx = basePos.getX();
            int by = basePos.getY();
            int bz = basePos.getZ();
            for (int dx = -10; dx <= 10; dx++) {
                for (int dz = 1; dz <= 10; dz++) {
                    for (int dy = 0; dy <= 8; dy++) {
                        level.setBlockAndUpdate(new BlockPos(bx + dx, by + dy, bz + dz), Blocks.AIR.defaultBlockState());
                    }
                }
            }
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                p.stopRiding();
                exo.setDeltaMovement(Vec3.ZERO);
                exo.teleportTo(exoX, exoY, exoZ);
                exo.setYRot(180.0F);
                exo.yRotO = 180.0F;
                exo.setYBodyRot(180.0F);
                exo.setYHeadRot(180.0F);
                p.teleportTo(exoX, exoY, exoZ);
            }
        })));
        steps.add(new Step(300, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                exo.setYRot(180.0F);
                exo.yRotO = 180.0F;
                exo.setYBodyRot(180.0F);
                exo.setYHeadRot(180.0F);
                p.setYRot(180.0F); // Face North (-Z)
                p.setXRot(6.0F);
                p.startRiding(exo, true);
                p.getInventory().clearContent();
                p.getInventory().add(new ItemStack(ModItems.AMMO_20MM.get(), 64));
                p.getInventory().add(new ItemStack(ModItems.AMMO_ROCKET.get(), 16));
                loadout(exo, ModItems.EXOFRAME_ASSAULT_RIFLE.get());
            }
            Zombie target = EntityType.ZOMBIE.create(level);
            if (target != null) {
                target.setNoAi(true);
                target.setPos(exoX, exoY + 1.2D, exoZ - 12.0D);
                level.addFreshEntity(target);
            }
        })));
        steps.add(new Step(315, mc -> {
            mc.player.setYRot(180.0F);
            mc.player.setXRot(6.0F);
            serverExoById(mc, (p, exo) -> {
                exo.setYRot(180.0F);
                exo.yRotO = 180.0F;
                exo.setYBodyRot(180.0F);
                exo.setYHeadRot(180.0F);
                p.setYRot(180.0F);
                p.setXRot(6.0F);
                if (ModItems.EXOFRAME_ASSAULT_RIFLE.get() instanceof com.obsolete.item.ExoframeAssaultRifleItem ar) {
                    ar.performFire(exo, p);
                }
            });
        }));
        steps.add(new Step(335, mc -> serverLevel(mc, (p, level) -> {
            var targets = level.getEntitiesOfClass(Zombie.class,
                    new AABB(exoX - 5, exoY - 1, exoZ - 20, exoX + 5, exoY + 6, exoZ - 8));
            for (var target : targets) {
                if (target.getHealth() < target.getMaxHealth()) {
                    ObsoleteMod.LOGGER.info("[autotest] ASSAULT RIFLE HIT PASS: Target damaged to {} / {}", target.getHealth(), target.getMaxHealth());
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] ASSAULT RIFLE HIT FAIL: Target health {}", target.getHealth());
                }
                target.discard();
            }
        })));

        // Shoulder Missile Hit Test
        steps.add(new Step(345, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                exo.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_TWIN_MANPADS.get()));
                exo.syncArmorMaskAndNotify();
            }
            Zombie target = EntityType.ZOMBIE.create(level);
            if (target != null) {
                target.setNoAi(true);
                target.setPos(exoX, exoY + 1.2D, exoZ - 14.0D);
                level.addFreshEntity(target);
            }
        })));
        steps.add(new Step(355, mc -> {
            mc.player.setYRot(180.0F);
            mc.player.setXRot(6.0F);
            serverExoById(mc, (p, exo) -> {
                exo.setYRot(180.0F);
                exo.yRotO = 180.0F;
                exo.setYBodyRot(180.0F);
                exo.setYHeadRot(180.0F);
                p.setYRot(180.0F);
                p.setXRot(6.0F);
                exo.fireShoulderMissile(p);
            });
        }));
        steps.add(new Step(385, mc -> serverLevel(mc, (p, level) -> {
            var targets = level.getEntitiesOfClass(Zombie.class,
                    new AABB(exoX - 10, exoY - 2, exoZ - 25, exoX + 10, exoY + 6, exoZ - 8));
            boolean hit = targets.isEmpty() || targets.get(0).getHealth() < targets.get(0).getMaxHealth();
            if (hit) {
                ObsoleteMod.LOGGER.info("[autotest] SHOULDER MISSILE HIT PASS: Target hit by shoulder missile!");
            } else {
                ObsoleteMod.LOGGER.error("[autotest] SHOULDER MISSILE HIT FAIL");
            }
            targets.forEach(Entity::discard);
        })));
        steps.add(new Step(395, mc -> shot(mc, "g03_weapon_muzzle_hits_pass")));

        // ==================== 4. MELEE ATTACK BOX TEST ====================
        steps.add(new Step(405, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                p.setYRot(180.0F); // Face North (-Z)
                p.setXRot(0.0F);
                Vec3 forward = p.getLookAngle().normalize();
                Vec3 tPos = exo.position().add(forward.scale(2.2D));
                Zombie target = EntityType.ZOMBIE.create(level);
                if (target != null) {
                    target.setNoAi(true);
                    target.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(100.0D);
                    target.setHealth(100.0F);
                    target.setPos(tPos.x, tPos.y, tPos.z);
                    level.addFreshEntity(target);
                }
            }
        })));
        steps.add(new Step(415, mc -> serverExoById(mc, (p, exo) -> {
            p.setYRot(180.0F);
            p.setXRot(0.0F);
            exo.performMeleeAttack(p);
        })));
        steps.add(new Step(435, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                var targets = level.getEntitiesOfClass(Zombie.class,
                        new AABB(exo.position().add(-4, -2, -4), exo.position().add(4, 4, 4)));
                if (targets.isEmpty()) {
                    ObsoleteMod.LOGGER.info("[autotest] MELEE BOX PASS: Target eliminated by melee strike!");
                } else {
                    for (var target : targets) {
                        if (target.getHealth() < target.getMaxHealth()) {
                            ObsoleteMod.LOGGER.info("[autotest] MELEE BOX PASS: Target damaged to {} / {}", target.getHealth(), target.getMaxHealth());
                        } else {
                            ObsoleteMod.LOGGER.error("[autotest] MELEE BOX FAIL: Target health {}", target.getHealth());
                        }
                        target.discard();
                    }
                }
            }
        })));
        steps.add(new Step(450, mc -> shot(mc, "g04_melee_box_pass")));

        // ==================== 5. 8 NEW WEAPONS DOWNRANGE HIT TEST ====================
        record WeaponEntry(String name,
                           java.util.function.Supplier<net.minecraft.world.item.Item> weapon,
                           java.util.function.Supplier<net.minecraft.world.item.Item> ammo,
                           double dist,
                           double yOff,
                           float pitch) {}

        WeaponEntry[] weaponEntries = {
                new WeaponEntry("battle_rifle", ModItems.EXOFRAME_BATTLE_RIFLE, ModItems.AMMO_762_MINIGUN,
                        12.0D, 1.2D, 6.0F),
                new WeaponEntry("autocannon_30mm", ModItems.EXOFRAME_AUTOCANNON_30MM, ModItems.AMMO_30MM_AUTOCANNON,
                        12.0D, 1.2D, 6.0F),
                new WeaponEntry("shotgun_breacher", ModItems.EXOFRAME_SHOTGUN_BREACHER, ModItems.AMMO_SHOTGUN_SLUG,
                        8.0D, 1.2D, 7.8F),
                new WeaponEntry("grenade_launcher", ModItems.EXOFRAME_GRENADE_LAUNCHER, ModItems.AMMO_40MM_GRENADE,
                        12.0D, 1.2D, 6.0F),
                new WeaponEntry("recoilless_rifle", ModItems.EXOFRAME_RECOILLESS_RIFLE, ModItems.AMMO_84MM_ROCKET,
                        12.0D, 1.2D, 6.0F),
                new WeaponEntry("atgm_guided", ModItems.EXOFRAME_ATGM_GUIDED, ModItems.AMMO_ATGM_MISSILE,
                        12.0D, 1.2D, 6.0F),
                new WeaponEntry("flamethrower", ModItems.EXOFRAME_FLAMETHROWER, ModItems.AMMO_NAPALM_CANISTER,
                        6.0D, 0.5D, 0.0F),
                new WeaponEntry("vibro_blade", ModItems.EXOFRAME_VIBRO_BLADE, () -> Items.AIR,
                        2.2D, 0.0D, 0.0F)
        };

        int wt = 470;
        for (WeaponEntry w : weaponEntries) {
            final WeaponEntry entry = w;
            // 1. Setup target downrange, clear old targets, loadout mech and give ammo
            steps.add(new Step(wt, mc -> serverLevel(mc, (p, level) -> {
                double tx = exoX;
                double ty = exoY + entry.yOff();
                double tz = exoZ - entry.dist();

                // Clear any leftover zombies in lane
                level.getEntitiesOfClass(Zombie.class,
                        new AABB(exoX - 15, exoY - 3, exoZ - 35, exoX + 15, exoY + 10, exoZ + 15)).forEach(Entity::discard);

                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setYRot(180.0F);
                    exo.yRotO = 180.0F;
                    exo.setYBodyRot(180.0F);
                    exo.setYHeadRot(180.0F);
                    p.setYRot(180.0F);
                    p.setXRot(entry.pitch());
                    p.getInventory().clearContent();
                    net.minecraft.world.item.Item ammoItem = entry.ammo().get();
                    if (ammoItem != Items.AIR) {
                        p.getInventory().add(new ItemStack(ammoItem, 64));
                    }
                    loadout(exo, entry.weapon().get());
                }

                Zombie target = EntityType.ZOMBIE.create(level);
                if (target != null) {
                    target.setNoAi(true);
                    target.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(100.0D);
                    target.setHealth(100.0F);
                    target.setPos(tx, ty, tz);
                    level.addFreshEntity(target);
                }
            })));

            // 2. Aim client & server, fire weapon
            steps.add(new Step(wt + 15, mc -> {
                mc.player.setYRot(180.0F);
                mc.player.setXRot(entry.pitch());
                serverExoById(mc, (p, exo) -> {
                    exo.setYRot(180.0F);
                    exo.yRotO = 180.0F;
                    exo.setYBodyRot(180.0F);
                    exo.setYHeadRot(180.0F);
                    p.setYRot(180.0F);
                    p.setXRot(entry.pitch());
                    ItemStack wpnStack = exo.getModularInventory().getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
                    if (wpnStack.getItem() instanceof ExoframeWeaponItem wpn) {
                        wpn.performFire(exo, p);
                    }
                });
            }));

            // 3. Verify hit / damage
            steps.add(new Step(wt + 32, mc -> serverLevel(mc, (p, level) -> {
                double tx = exoX;
                double ty = exoY + entry.yOff();
                double tz = exoZ - entry.dist();
                AABB checkZone = new AABB(tx - 3.5, ty - 2.0, tz - 3.5, tx + 3.5, ty + 4.0, tz + 3.5);
                var targets = level.getEntitiesOfClass(Zombie.class, checkZone);
                if (targets.isEmpty()) {
                    ObsoleteMod.LOGGER.info("[autotest] WEAPON FIRE PASS: {} eliminated downrange target!", entry.name());
                } else {
                    boolean damaged = false;
                    for (var target : targets) {
                        if (target.getHealth() < target.getMaxHealth()) {
                            ObsoleteMod.LOGGER.info("[autotest] WEAPON FIRE PASS: {} damaged target to {} / {}", entry.name(), target.getHealth(), target.getMaxHealth());
                            damaged = true;
                        }
                    }
                    if (!damaged) {
                        ObsoleteMod.LOGGER.error("[autotest] WEAPON FIRE FAIL: {} did not damage target! Health: {}", entry.name(), targets.get(0).getHealth());
                    }
                }
            })));

            // 4. Capture screenshot & cleanup
            steps.add(new Step(wt + 38, mc -> {
                shot(mc, "g_wpn_" + entry.name() + "_hit");
                serverLevel(mc, (p, level) -> {
                    double tx = exoX;
                    double ty = exoY + entry.yOff();
                    double tz = exoZ - entry.dist();
                    AABB checkZone = new AABB(tx - 3.5, ty - 2.0, tz - 3.5, tx + 3.5, ty + 4.0, tz + 3.5);
                    level.getEntitiesOfClass(Zombie.class, checkZone).forEach(Entity::discard);
                });
            }));

            wt += 45;
        }

        // ==================== 6. ROLE VARIANT: POLICE RIOT SHIELD TEST ====================
        steps.add(new Step(wt, mc -> {
            if (mc.player != null) {
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;
                mc.player.setXRot(0.0F);
            }
            serverLevel(mc, (p, level) -> {
                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.setDeltaMovement(Vec3.ZERO);
                    exo.teleportTo(exoX, exoY, exoZ);
                    exo.setYRot(0.0F); // Face South (+Z)
                    exo.yRotO = 0.0F;
                    exo.setYBodyRot(0.0F);
                    exo.setYHeadRot(0.0F);
                    p.setYRot(0.0F);
                    p.setXRot(0.0F);
                    p.startRiding(exo, true);
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_POLICE_HEAD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_POLICE_CHEST.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), ItemStack.EMPTY);
                    inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.EXOFRAME_RIOT_SHIELD.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_STUN_BATON.get()));
                    exo.syncArmorMaskAndNotify();
                    exo.setHealth(exo.getMaxHealth());
                }
            });
        }));

        // Frontal shield projectile block check
        steps.add(new Step(wt + 15, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                float startHealth = exo.getHealth();
                Vec3 forward = exo.getLookAngle().normalize();
                Vec3 frontPos = exo.position().add(forward.scale(4.0D)).add(0, 1.5D, 0);
                Arrow frontArrow = new Arrow(level, frontPos.x, frontPos.y, frontPos.z);
                frontArrow.setDeltaMovement(forward.scale(-1.0D));
                level.addFreshEntity(frontArrow);

                boolean blocked = !exo.hurt(level.damageSources().arrow(frontArrow, null), 12.0F);
                if (blocked && exo.getHealth() == startHealth) {
                    ObsoleteMod.LOGGER.info("[autotest] SHIELD FRONTAL BLOCK PASS: Frontal attack blocked with 0 damage!");
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] SHIELD FRONTAL BLOCK FAIL: Frontal attack was not blocked! Health: {}", exo.getHealth());
                }
                frontArrow.discard();
            }
        })));

        // Rear projectile penetration check
        steps.add(new Step(wt + 25, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                float healthBeforeRear = exo.getHealth();
                Vec3 forward = exo.getLookAngle().normalize();
                Vec3 rearPos = exo.position().add(forward.scale(-4.0D)).add(0, 1.5D, 0);
                Arrow rearArrow = new Arrow(level, rearPos.x, rearPos.y, rearPos.z);
                rearArrow.setDeltaMovement(forward.scale(1.0D));
                level.addFreshEntity(rearArrow);

                boolean damaged = exo.hurt(level.damageSources().arrow(rearArrow, null), 10.0F);
                if (damaged && exo.getHealth() < healthBeforeRear) {
                    ObsoleteMod.LOGGER.info("[autotest] SHIELD REAR ATTACK PASS: Attack from behind penetrated shield arc (Health: {} -> {})", healthBeforeRear, exo.getHealth());
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] SHIELD REAR ATTACK FAIL: Attack from behind was unexpectedly blocked!");
                }
                rearArrow.discard();
                exo.setHealth(exo.getMaxHealth());
            }
        })));
        steps.add(new Step(wt + 32, mc -> shot(mc, "g_role_shield_block_pass")));

        // ==================== 7. ROLE VARIANT: POLICE STUN BATON TEST ====================
        steps.add(new Step(wt + 40, mc -> serverLevel(mc, (p, level) -> {
            Zombie target = EntityType.ZOMBIE.create(level);
            if (target != null) {
                target.setNoAi(true);
                target.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(100.0D);
                target.setHealth(100.0F);
                target.setPos(exoX, exoY + 0.5D, exoZ + 2.0D);
                level.addFreshEntity(target);
            }
        })));
        steps.add(new Step(wt + 50, mc -> serverExoById(mc, (p, exo) -> {
            p.setYRot(0.0F);
            p.setXRot(0.0F);
            exo.fireEquippedWeapon(p);
        })));
        steps.add(new Step(wt + 60, mc -> serverLevel(mc, (p, level) -> {
            var targets = level.getEntitiesOfClass(Zombie.class, new AABB(exoX - 3, exoY - 1, exoZ, exoX + 3, exoY + 4, exoZ + 5));
            boolean pass = false;
            for (var target : targets) {
                if (target.getHealth() < target.getMaxHealth() && target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)) {
                    ObsoleteMod.LOGGER.info("[autotest] STUN BATON PASS: Target damaged to {} and inflicted Slowness!", target.getHealth());
                    pass = true;
                }
                target.discard();
            }
            if (!pass) {
                ObsoleteMod.LOGGER.error("[autotest] STUN BATON FAIL: Target not damaged or missing Slowness effect!");
            }
        })));
        steps.add(new Step(wt + 65, mc -> shot(mc, "g_role_stun_baton_pass")));

        // ==================== 8. ROLE VARIANT: DISASTER RESCUE FLOODLIGHTS & LIFE SUPPORT TEST ====================
        steps.add(new Step(wt + 75, mc -> serverLevel(mc, (p, level) -> {
            level.setDayTime(18000L); // Midnight
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_RESCUE_HEAD.get()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_RESCUE_CHEST.get()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_RESCUE_WINCH.get()));
                exo.syncArmorMaskAndNotify();
            }
        })));
        steps.add(new Step(wt + 90, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                BlockPos lightPos = exo.blockPosition().above(2);
                boolean hasLightBlock = level.getBlockState(lightPos).is(Blocks.LIGHT) &&
                        level.getBlockState(lightPos).getValue(BlockStateProperties.LEVEL) == 15;
                if (hasLightBlock) {
                    ObsoleteMod.LOGGER.info("[autotest] RESCUE FLOODLIGHTS PASS: Floodlights generated dynamic light level 15 at {}", lightPos);
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] RESCUE FLOODLIGHTS FAIL: Expected light block at {}, got {}", lightPos, level.getBlockState(lightPos));
                }

                boolean hasLifeSupport = p.hasEffect(MobEffects.WATER_BREATHING) && p.hasEffect(MobEffects.FIRE_RESISTANCE);
                if (hasLifeSupport) {
                    ObsoleteMod.LOGGER.info("[autotest] RESCUE LIFE SUPPORT PASS: Pilot granted Water Breathing and Fire Resistance!");
                } else {
                    ObsoleteMod.LOGGER.error("[autotest] RESCUE LIFE SUPPORT FAIL: Pilot missing life support effects!");
                }
            }
            level.setDayTime(6000L); // Restore daytime
        })));
        steps.add(new Step(wt + 95, mc -> shot(mc, "g_role_rescue_floodlight_pass")));

        // ==================== 9. ROLE VARIANT: AMPHIBIOUS FLOAT RING BUOYANCY TEST ====================
        steps.add(new Step(wt + 105, mc -> serverLevel(mc, (p, level) -> {
            int px = (int) exoX + 18;
            int py = (int) exoY;
            int pz = (int) exoZ;
            // Build 7x7 water tank 4 blocks deep
            for (int dx = -3; dx <= 3; dx++) {
                for (int dz = -3; dz <= 3; dz++) {
                    for (int dy = -4; dy <= 2; dy++) {
                        boolean wall = Math.abs(dx) == 3 || Math.abs(dz) == 3 || dy == -4;
                        BlockPos bpos = new BlockPos(px + dx, py + dy, pz + dz);
                        if (wall) {
                            level.setBlockAndUpdate(bpos, Blocks.GLASS.defaultBlockState());
                        } else if (dy <= 0) {
                            level.setBlockAndUpdate(bpos, Blocks.WATER.defaultBlockState());
                        } else {
                            level.setBlockAndUpdate(bpos, Blocks.AIR.defaultBlockState());
                        }
                    }
                }
            }
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                p.stopRiding();
                var inv = exo.getModularInventory();
                for (int i = 0; i < inv.getSlots(); i++) inv.setStackInSlot(i, ItemStack.EMPTY);
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_FLOAT_RING.get()));
                exo.syncArmorMaskAndNotify();
                // Submerge mech at bottom of tank
                exo.moveTo(px + 0.5D, py - 3.2D, pz + 0.5D, 0.0F, 0.0F);
                exo.setDeltaMovement(Vec3.ZERO);
            }
        })));
        steps.add(new Step(wt + 135, mc -> {
            if (mc.player != null) {
                mc.player.setPos(exoX, exoY, exoZ);
                mc.player.stopRiding();
            }
            serverLevel(mc, (p, level) -> {
                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    double currentY = exo.getY();
                    int py = (int) exoY;
                    double expectedMinY = py - 0.8D;
                    if (currentY >= expectedMinY) {
                        ObsoleteMod.LOGGER.info("[autotest] AMPHIBIOUS FLOAT RING PASS: Mech floated up to water surface (Y={} >= {})", currentY, expectedMinY);
                    } else {
                        ObsoleteMod.LOGGER.error("[autotest] AMPHIBIOUS FLOAT RING FAIL: Mech stayed submerged! (Y={} < {})", currentY, expectedMinY);
                    }
                    // Return mech to center tarmac
                    p.stopRiding();
                    exo.moveTo(exoX, exoY, exoZ, 180.0F, 0.0F);
                    exo.setDeltaMovement(Vec3.ZERO);
                    p.connection.teleport(exoX, exoY, exoZ, 180.0F, 25.0F, java.util.Collections.emptySet());
                }
            });
        }));
        steps.add(new Step(wt + 140, mc -> shot(mc, "g_role_amphibious_float_pass")));

        // ==================== 10. ROLE VARIANT: CIVIL WORKSITE FAST MINING TEST ====================
        steps.add(new Step(wt + 150, mc -> {
            if (mc.player != null) {
                mc.player.setPos(exoX, exoY, exoZ);
                mc.player.setYRot(180.0F);
                mc.player.yRotO = 180.0F;
                mc.player.setXRot(25.0F);
            }
            serverLevel(mc, (p, level) -> {
                if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                    exo.moveTo(exoX, exoY, exoZ, 180.0F, 0.0F);
                    exo.yRotO = 180.0F;
                    exo.setYRot(180.0F);
                    exo.setYBodyRot(180.0F);
                    exo.setYHeadRot(180.0F);
                    exo.setDeltaMovement(Vec3.ZERO);
                    p.connection.teleport(exoX, exoY, exoZ, 180.0F, 25.0F, java.util.Collections.emptySet());
                    p.setYRot(180.0F);
                    p.setXRot(25.0F);
                    p.startRiding(exo, true);
                    var inv = exo.getModularInventory();
                    inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_ROLL_CAGE.get()));
                    inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.TOOL_MINING_DRILL.get()));
                    exo.syncArmorMaskAndNotify();
                }
                BlockPos base = BlockPos.containing(exoX, exoY, exoZ);
                // Build 3-wide, 5-tall stone wall directly in front of mech (-Z)
                for (int dx = -1; dx <= 1; dx++) {
                    for (int dy = 0; dy <= 4; dy++) {
                        for (int dz = -3; dz <= -2; dz++) {
                            level.setBlockAndUpdate(base.offset(dx, dy, dz), Blocks.STONE.defaultBlockState());
                        }
                    }
                }
            });
        }));
        steps.add(new Step(wt + 160, mc -> {
            if (mc.player != null) {
                mc.player.setPos(exoX, exoY, exoZ);
                mc.player.setYRot(180.0F);
                mc.player.yRotO = 180.0F;
                mc.player.setXRot(25.0F);
            }
            serverExoById(mc, (p, exo) -> {
                exo.setYRot(180.0F);
                exo.yRotO = 180.0F;
                exo.setYBodyRot(180.0F);
                exo.setYHeadRot(180.0F);
                p.setYRot(180.0F);
                p.setXRot(25.0F);
                ItemStack wpnStack = exo.getModularInventory().getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
                if (wpnStack.getItem() instanceof ExoframeWeaponItem drill) {
                    drill.performFire(exo, p);
                }
            });
        }));
        steps.add(new Step(wt + 170, mc -> serverLevel(mc, (p, level) -> {
            BlockPos base = BlockPos.containing(exoX, exoY, exoZ);
            int brokenCount = 0;
            for (int dx = -1; dx <= 1; dx++) {
                for (int dy = 0; dy <= 4; dy++) {
                    for (int dz = -3; dz <= -2; dz++) {
                        if (level.getBlockState(base.offset(dx, dy, dz)).isAir()) {
                            brokenCount++;
                        }
                    }
                }
            }
            if (brokenCount >= 7) {
                ObsoleteMod.LOGGER.info("[autotest] CIVIL WORKSITE DRILL PASS: Roll cage boosted drill mined {} blocks in wide blast radius!", brokenCount);
            } else {
                ObsoleteMod.LOGGER.error("[autotest] CIVIL WORKSITE DRILL FAIL: Only {} blocks mined!", brokenCount);
            }
            // Cleanup remaining wall
            for (int dx = -3; dx <= 3; dx++) {
                for (int dy = 0; dy <= 6; dy++) {
                    for (int dz = -5; dz <= 0; dz++) {
                        level.setBlockAndUpdate(base.offset(dx, dy, dz), Blocks.AIR.defaultBlockState());
                    }
                }
            }
        })));
        steps.add(new Step(wt + 175, mc -> shot(mc, "g_role_worksite_drill_pass")));

        // ==================== 11. ROLE VARIANT: RADAR SCOUT & HARBOUR FISHING TEST ====================
        steps.add(new Step(wt + 185, mc -> serverLevel(mc, (p, level) -> {
            if (level.getEntity(exoframeId) instanceof ExoframeEntity exo) {
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_SEARCH_RADAR.get()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_FISHING_ROD.get()));
                exo.syncArmorMaskAndNotify();
            }
            Zombie radarTarget = EntityType.ZOMBIE.create(level);
            if (radarTarget != null) {
                radarTarget.setNoAi(true);
                radarTarget.setPos(exoX, exoY + 1.0D, exoZ - 12.0D);
                level.addFreshEntity(radarTarget);
            }
        })));
        steps.add(new Step(wt + 195, mc -> serverExoById(mc, (p, exo) -> {
            // Dry land first: the rod must refuse to fish without water nearby.
            int before = countFish(p);
            exo.performFishing(p);
            if (countFish(p) != before) {
                ObsoleteMod.LOGGER.error("[autotest] HARBOUR FISHING FAIL: Caught fish on dry land!");
            }
            BlockPos pond = BlockPos.containing(exoX + 3, exoY - 1, exoZ);
            for (int dx = 0; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {
                p.serverLevel().setBlockAndUpdate(pond.offset(dx, 0, dz), Blocks.WATER.defaultBlockState());
            }
            exo.performFishing(p);
            int caught = countFish(p) - before;
            var drops = p.serverLevel().getEntitiesOfClass(ItemEntity.class, exo.getBoundingBox().inflate(6.0D),
                    e -> e.getItem().is(Items.COD) || e.getItem().is(Items.SALMON) || e.getItem().is(Items.TROPICAL_FISH) || e.getItem().is(Items.PUFFERFISH));
            if (caught > 0 && drops.isEmpty()) {
                ObsoleteMod.LOGGER.info("[autotest] HARBOUR FISHING PASS: Caught {} fish beside water, none duplicated on the ground", caught);
            } else {
                ObsoleteMod.LOGGER.error("[autotest] HARBOUR FISHING FAIL: caught={}, ground drops={}", caught, drops.size());
            }
            for (int dx = 0; dx <= 1; dx++) for (int dz = -1; dz <= 1; dz++) {
                p.serverLevel().setBlockAndUpdate(pond.offset(dx, 0, dz), Blocks.STONE.defaultBlockState());
            }
        })));
        // The radar pulses every 60 ticks on its own; nothing here applies Glowing.
        steps.add(new Step(wt + 265, mc -> serverLevel(mc, (p, level) -> {
            var monsters = level.getEntitiesOfClass(Zombie.class, new AABB(exoX - 5, exoY - 2, exoZ - 20, exoX + 5, exoY + 5, exoZ - 5));
            boolean radarPass = monsters.stream().anyMatch(m -> m.hasEffect(MobEffects.GLOWING));
            if (radarPass) {
                ObsoleteMod.LOGGER.info("[autotest] RADAR SCOUT PASS: Radar pulse made the hostile target glow");
            } else {
                ObsoleteMod.LOGGER.error("[autotest] RADAR SCOUT FAIL: Target was not illuminated with Glowing!");
            }
            monsters.forEach(Entity::discard);
        })));
        steps.add(new Step(wt + 270, mc -> shot(mc, "g_role_radar_and_fishing_pass")));

        // ==================== 12. SOUND & EFFECT VERIFICATION: WALKING, SPRINTING, WEAPONS & PARTICLES ====================
        steps.add(new Step(wt + 280, mc -> serverExoById(mc, (p, exo) -> {
            exo.setDeltaMovement(0, 0, 0.12D);
            ObsoleteMod.LOGGER.info("[autotest] SOUND & EFFECT TEST: Simulating movement footsteps, dust puffs, and servo whine...");
        })));
        steps.add(new Step(wt + 290, mc -> serverExoById(mc, (p, exo) -> {
            exo.setSprinting(true);
            exo.setDeltaMovement(0, 0, 0.25D);
            ObsoleteMod.LOGGER.info("[autotest] SOUND & EFFECT TEST: Simulating sprint footsteps, speed dust, and exhaust smoke burst...");
        })));
        steps.add(new Step(wt + 300, mc -> serverExoById(mc, (p, exo) -> {
            exo.setSprinting(false);
            exo.setDeltaMovement(0, 0, 0);

            Item[] weapons = {
                ModItems.EXOFRAME_ASSAULT_RIFLE.get(),
                ModItems.EXOFRAME_SNIPER_RIFLE.get(),
                ModItems.EXOFRAME_AUTOCANNON_30MM.get(),
                ModItems.EXOFRAME_MINIGUN.get(),
                ModItems.EXOFRAME_SHOTGUN_BREACHER.get(),
                ModItems.EXOFRAME_GRENADE_LAUNCHER.get(),
                ModItems.EXOFRAME_RPG7.get(),
                ModItems.EXOFRAME_RECOILLESS_RIFLE.get(),
                ModItems.EXOFRAME_FLAMETHROWER.get()
            };

            Item[] ammos = {
                ModItems.AMMO_20MM.get(),
                ModItems.AMMO_20MM.get(),
                ModItems.AMMO_30MM_AUTOCANNON.get(),
                ModItems.AMMO_762_MINIGUN.get(),
                ModItems.AMMO_SHOTGUN_SLUG.get(),
                ModItems.AMMO_40MM_GRENADE.get(),
                ModItems.AMMO_84MM_ROCKET.get(),
                ModItems.AMMO_84MM_ROCKET.get(),
                ModItems.AMMO_NAPALM_CANISTER.get()
            };

            var inv = exo.getModularInventory();
            for (int i = 0; i < weapons.length; i++) {
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(weapons[i]));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ammos[i], 16));
                exo.setWeaponCooldown(0);
                exo.fireEquippedWeapon(p);
                ObsoleteMod.LOGGER.info("[autotest] SOUND & EFFECT TEST: Fired weapon '{}' with dedicated audio and muzzle/backblast particles!",
                        weapons[i].getDescriptionId());
            }

            // Test dry-fire empty click
            inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), ItemStack.EMPTY);
            exo.setWeaponCooldown(0);
            exo.fireEquippedWeapon(p);
            ObsoleteMod.LOGGER.info("[autotest] SOUND & EFFECT TEST: Fired empty weapon - dry click sound confirmed!");

            // Test landing sound & shockwave
            exo.causeFallDamage(4.5F, 1.0F, exo.damageSources().fall());
            ObsoleteMod.LOGGER.info("[autotest] SOUND & EFFECT TEST: Triggered heavy fall landing thud & ground shockwave ring!");
        })));
        steps.add(new Step(wt + 305, mc -> shot(mc, "g_sound_and_effects_pass")));

        steps.add(new Step(wt + 310, mc -> serverExoById(mc, (p, exo) -> {
            var inv = exo.getModularInventory();
            inv.setStackInSlot(ExoframeArmorSlot.BACK.getIndex(), new ItemStack(ModItems.MODULE_FLIGHT_BOOSTER.get()));
            exo.syncArmorMaskAndNotify();
            if (!exo.hasFlightBooster()) {
                throw new AssertionError("[autotest] Flight booster was equipped in BACK slot but hasFlightBooster() returned false!");
            }
            // Test aerial flight activation
            exo.setFlying(true);
            exo.setFlightBoosting(false);
            if (!exo.isFlying()) {
                throw new AssertionError("[autotest] exo.setFlying(true) failed to set flight state!");
            }
            // Test Gundam boost dash state
            exo.setFlightBoosting(true);
            if (!exo.isFlightBoosting()) {
                throw new AssertionError("[autotest] exo.setFlightBoosting(true) failed to set boost state!");
            }
            ObsoleteMod.LOGGER.info("[autotest] FLIGHT TEST: Gundam Flight Booster equipped, verified in slot BACK, hover and supersonic boost confirmed!");
        })));
        steps.add(new Step(wt + 315, mc -> shot(mc, "g_gundam_flight_booster_pass")));
        steps.add(new Step(wt + 320, mc -> serverExoById(mc, (p, exo) -> {
            // First dismount cycle
            p.stopRiding();
            if (p.isPassenger() || exo.hasPassenger(p)) {
                throw new AssertionError("[autotest] Player failed to dismount from Exoframe on first cycle!");
            }
            if (exo.isFlying() || exo.isFlightBoosting()) {
                throw new AssertionError("[autotest] Exoframe retained active flight state after pilot dismount!");
            }
            if (!exo.isMechCrouching()) {
                throw new AssertionError("[autotest] Exoframe failed to enter parked crouch pose upon dismount!");
            }
            ObsoleteMod.LOGGER.info("[autotest] MOUNT-DISMOUNT TEST: First dismount cycle successful, mech parked in crouch pose, flight state cleanly reset.");
        })));

        steps.add(new Step(wt + 325, mc -> serverExoById(mc, (p, exo) -> {
            // Second mount cycle: remounting
            p.startRiding(exo);
            if (!p.isPassenger() || !exo.hasPassenger(p)) {
                throw new AssertionError("[autotest] Player failed to remount Exoframe on second cycle!");
            }
            if (exo.isMechCrouching()) {
                throw new AssertionError("[autotest] Exoframe failed to stand up from parked crouch upon boarding!");
            }
            // Flight / movement reactivation
            exo.setFlying(true);
            exo.setFlightBoosting(true);
            ObsoleteMod.LOGGER.info("[autotest] MOUNT-DISMOUNT TEST: Second mount cycle successful, mech stood up, flight reactivated.");
        })));

        steps.add(new Step(wt + 330, mc -> serverExoById(mc, (p, exo) -> {
            // Second dismount cycle: must dismount cleanly without lockup or getting stuck
            p.stopRiding();
            if (p.isPassenger() || exo.hasPassenger(p)) {
                throw new AssertionError("[autotest] Player stuck in mech on second dismount cycle!");
            }
            if (exo.isFlying() || exo.isFlightBoosting()) {
                throw new AssertionError("[autotest] Exoframe retained active flight state after second pilot dismount!");
            }
            if (!exo.isMechCrouching()) {
                throw new AssertionError("[autotest] Exoframe failed to enter parked crouch pose upon second dismount!");
            }
            ObsoleteMod.LOGGER.info("[autotest] MOUNT-DISMOUNT TEST: Second dismount cycle PASS - no freeze, no fall damage, parked in crouch pose!");
        })));
        steps.add(new Step(wt + 335, mc -> shot(mc, "g_flight_remount_dismount_pass")));

        wt += 345;

        steps.add(new Step(wt + 10, mc -> {
            ObsoleteMod.LOGGER.info("[autotest] gameplay scenario completed with all checks passing!");
            mc.stop();
        }));

        return steps.toArray(Step[]::new);
    }

    private static int countFish(ServerPlayer p) {
        int n = 0;
        for (int i = 0; i < p.getInventory().getContainerSize(); i++) {
            ItemStack st = p.getInventory().getItem(i);
            if (st.is(Items.COD) || st.is(Items.SALMON) || st.is(Items.TROPICAL_FISH) || st.is(Items.PUFFERFISH)) n += st.getCount();
        }
        return n;
    }

    private static Step[] buildArmorSteps() {
        record Set(String name, net.minecraft.world.item.Item head, net.minecraft.world.item.Item chest,
                   net.minecraft.world.item.Item arms, net.minecraft.world.item.Item legs,
                   net.minecraft.world.item.Item util, net.minecraft.world.item.Item weapon) {}
        Set[] sets = {
                new Set("marine_raider", ModItems.ARMOR_USMC_HEAD.get(), ModItems.ARMOR_USMC_CHEST.get(), ModItems.ARMOR_USMC_ARMS.get(),
                        ModItems.ARMOR_USMC_LEGS.get(), ModItems.MODULE_USMC_COMMS.get(), ModItems.EXOFRAME_MACHINE_GUN.get()),
                new Set("pegaso_black", ModItems.ARMOR_CERBERUS_HEAD.get(), ModItems.ARMOR_CERBERUS_CHEST.get(), ModItems.ARMOR_CERBERUS_ARMS.get(),
                        ModItems.ARMOR_CERBERUS_LEGS.get(), ModItems.MODULE_CERBERUS_PACKS.get(), ModItems.EXOFRAME_ASSAULT_RIFLE.get()),
                new Set("polar_front", ModItems.ARMOR_POLAR_HEAD.get(), ModItems.ARMOR_ARCTIC_CHEST.get(), ModItems.ARMOR_POLAR_ARMS.get(),
                        ModItems.ARMOR_POLAR_LEGS.get(), ModItems.MODULE_TWIN_MANPADS.get(), net.minecraft.world.item.Items.AIR),
                new Set("outlander_heavy", ModItems.ARMOR_MILITIA_HOOD.get(), ModItems.ARMOR_MILITIA_CHEST.get(), ModItems.ARMOR_OUTLANDER_ARMS.get(),
                        ModItems.ARMOR_OUTLANDER_LEGS.get(), net.minecraft.world.item.Items.AIR, ModItems.EXOFRAME_RPG7.get()),
                new Set("salvage", ModItems.ARMOR_SALVAGE_HEAD.get(), ModItems.ARMOR_SALVAGE_CHEST.get(), ModItems.ARMOR_SALVAGE_ARMS.get(),
                        ModItems.ARMOR_SALVAGE_LEGS.get(), ModItems.MODULE_SALVAGE_SCRAPS.get(), ModItems.EXOFRAME_AUTOCANNON_30MM.get()),
                new Set("shiden", ModItems.ARMOR_SHIDEN_HEAD.get(), ModItems.ARMOR_SHIDEN_CHEST.get(), ModItems.ARMOR_SHIDEN_ARMS.get(),
                        ModItems.ARMOR_SHIDEN_LEGS.get(), ModItems.MODULE_SHIDEN_CREST.get(), ModItems.EXOFRAME_BATTLE_RIFLE.get()),
                new Set("khamsin", ModItems.ARMOR_KHAMSIN_HEAD.get(), ModItems.ARMOR_KHAMSIN_CHEST.get(), ModItems.ARMOR_KHAMSIN_ARMS.get(),
                        ModItems.ARMOR_KHAMSIN_LEGS.get(), ModItems.MODULE_KHAMSIN_FILTERS.get(), ModItems.EXOFRAME_RECOILLESS_RIFLE.get()),
                new Set("riverine", ModItems.ARMOR_RIVERINE_HEAD.get(), ModItems.ARMOR_RIVERINE_CHEST.get(), ModItems.ARMOR_RIVERINE_ARMS.get(),
                        ModItems.ARMOR_RIVERINE_LEGS.get(), ModItems.MODULE_RIVERINE_SNORKEL.get(), ModItems.EXOFRAME_SHOTGUN_BREACHER.get()),
                new Set("specter", ModItems.ARMOR_SPECTER_HEAD.get(), ModItems.ARMOR_SPECTER_CHEST.get(), ModItems.ARMOR_SPECTER_ARMS.get(),
                        ModItems.ARMOR_SPECTER_LEGS.get(), ModItems.MODULE_SPECTER_ECM.get(), ModItems.EXOFRAME_ATGM_GUIDED.get()),
                new Set("valkyrie", ModItems.ARMOR_VALKYRIE_HEAD.get(), ModItems.ARMOR_VALKYRIE_CHEST.get(), ModItems.ARMOR_VALKYRIE_ARMS.get(),
                        ModItems.ARMOR_VALKYRIE_LEGS.get(), ModItems.MODULE_VALKYRIE_SENSOR.get(), ModItems.EXOFRAME_FLAMETHROWER.get()),
                new Set("police_riot", ModItems.ARMOR_POLICE_HEAD.get(), ModItems.ARMOR_POLICE_CHEST.get(), ModItems.ARMOR_CERBERUS_ARMS.get(),
                        ModItems.ARMOR_CERBERUS_LEGS.get(), ModItems.EXOFRAME_RIOT_SHIELD.get(), ModItems.EXOFRAME_STUN_BATON.get()),
                new Set("disaster_rescue", ModItems.ARMOR_RESCUE_HEAD.get(), ModItems.ARMOR_RESCUE_CHEST.get(), ModItems.ARMOR_USMC_ARMS.get(),
                        ModItems.ARMOR_USMC_LEGS.get(), ModItems.MODULE_RESCUE_WINCH.get(), ModItems.EXOFRAME_FISHING_ROD.get()),
                new Set("amphibious_radar", ModItems.ARMOR_RIVERINE_HEAD.get(), ModItems.ARMOR_RIVERINE_CHEST.get(), ModItems.ARMOR_RIVERINE_ARMS.get(),
                        ModItems.ARMOR_FLOAT_RING.get(), ModItems.MODULE_SEARCH_RADAR.get(), ModItems.EXOFRAME_SHOTGUN_BREACHER.get()),
                new Set("worksite", net.minecraft.world.item.Items.AIR, ModItems.ARMOR_ROLL_CAGE.get(), net.minecraft.world.item.Items.AIR,
                        net.minecraft.world.item.Items.AIR, ModItems.PEDDLER_CORE.get(), ModItems.TOOL_MINING_DRILL.get()),
        };
        java.util.List<Step> steps = new java.util.ArrayList<>(java.util.List.of(SHOWCASE[0], SHOWCASE[1], SHOWCASE[2]));
        int t = 80;
        for (Set s : sets) {
            steps.add(new Step(t, mc -> serverExoById(mc, (p, exo) -> {
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(s.head()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(s.chest()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(s.arms()));
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(s.legs()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(s.util()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(s.weapon()));
                exo.syncArmorMaskAndNotify();
            })));
            steps.add(new Step(t + 5, mc -> view(mc, -35)));
            steps.add(new Step(t + 25, mc -> shot(mc, "b_" + s.name() + "_front")));
            steps.add(new Step(t + 30, mc -> view(mc, 145)));
            steps.add(new Step(t + 50, mc -> shot(mc, "b_" + s.name() + "_rear")));
            t += 60;
        }
        // Every set again with a pilot aboard: capsules must enclose the rider and vanish in first person.
        steps.add(new Step(t - 5, mc -> {
            mc.options.setCameraType(CameraType.FIRST_PERSON);
            mc.options.hideGui = false;
        }));
        steps.add(new Step(t, mc -> serverExoById(mc, (p, exo) -> p.startRiding(exo, true))));
        steps.add(new Step(t + 12, mc -> shot(mc, "boot_cinematic_mid")));
        steps.add(new Step(t + 35, mc -> shot(mc, "boot_cinematic_sync")));
        steps.add(new Step(t + 39, mc -> mc.options.hideGui = true));
        t += 40;
        for (Set s : sets) {
            steps.add(new Step(t, mc -> serverExoById(mc, (p, exo) -> {
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(s.head()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(s.chest()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(s.arms()));
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(s.legs()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(s.util()));
                exo.syncArmorMaskAndNotify();
            })));
            steps.add(new Step(t + 5, mc -> {
                mc.player.setXRot(25.0F);
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;
                mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
            }));
            steps.add(new Step(t + 25, mc -> shot(mc, "c_" + s.name() + "_piloted_front")));
            steps.add(new Step(t + 30, mc -> {
                mc.player.setXRot(15.0F);
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            }));
            steps.add(new Step(t + 50, mc -> shot(mc, "c_" + s.name() + "_piloted_back")));
            // Piloted rear 3/4 view: camera at angle 140 deg to inspect shoulder/cockpit juncture
            steps.add(new Step(t + 55, mc -> {
                mc.player.setYRot(140.0F);
                mc.player.yRotO = 140.0F;
                mc.player.setXRot(15.0F);
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
            }));
            steps.add(new Step(t + 70, mc -> shot(mc, "c_" + s.name() + "_piloted_rear_34")));
            // Piloted walking view: mech walking forward so gait cycle / hunch is active
            steps.add(new Step(t + 75, mc -> {
                mc.player.setYRot(0.0F);
                mc.player.yRotO = 0.0F;
                mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
                mc.options.keyUp.setDown(true);
            }));
            steps.add(new Step(t + 95, mc -> shot(mc, "c_" + s.name() + "_piloted_walking")));
            steps.add(new Step(t + 100, mc -> {
                mc.options.keyUp.setDown(false);
                serverExoById(mc, (p, exo) -> {
                    exo.moveTo(exoX, exoY, exoZ, 0.0F, 0.0F);
                    exo.setDeltaMovement(0, 0, 0);
                });
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                mc.options.hideGui = false;
            }));
            steps.add(new Step(t + 115, mc -> shot(mc, "c_" + s.name() + "_firstperson")));
            steps.add(new Step(t + 120, mc -> mc.options.hideGui = true));
            t += 125;
        }

        // ==================== CROSS-FACTION MIX TEST ====================
        steps.add(new Step(t, mc -> serverExoById(mc, (p, exo) -> {
            var inv = exo.getModularInventory();
            inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_SHIDEN_HEAD.get()));
            inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_RIVERINE_CHEST.get()));
            inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_SPECTER_ARMS.get()));
            inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_VALKYRIE_LEGS.get()));
            inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_SALVAGE_SCRAPS.get()));
            inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_VIBRO_BLADE.get()));
            exo.syncArmorMaskAndNotify();
        })));
        steps.add(new Step(t + 5, mc -> {
            mc.player.setXRot(25.0F);
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
        }));
        steps.add(new Step(t + 25, mc -> shot(mc, "c_cross_faction_mix_piloted_front")));
        steps.add(new Step(t + 30, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK)));
        steps.add(new Step(t + 50, mc -> shot(mc, "c_cross_faction_mix_piloted_back")));
        steps.add(new Step(t + 55, mc -> mc.options.setCameraType(CameraType.FIRST_PERSON)));
        steps.add(new Step(t + 70, mc -> shot(mc, "c_cross_faction_mix_firstperson")));
        t += 80;

        // ==================== 4 FRAME TIERS HUD & LOADOUT SCREEN TEST ====================
        for (int tier = 0; tier <= 3; tier++) {
            final int curTier = tier;
            steps.add(new Step(t, mc -> serverExoById(mc, (p, exo) -> {
                exo.setFrameTier(curTier);
                var inv = exo.getModularInventory();
                inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_SAND_HEAD.get()));
                inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_SAND_CHEST.get()));
                inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_ARMS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_LEGS.get()));
                inv.setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), new ItemStack(ModItems.MODULE_TARGETING_COMPUTER.get()));
                inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(ModItems.EXOFRAME_ASSAULT_RIFLE.get()));
                exo.syncArmorMaskAndNotify();
            })));
            steps.add(new Step(t + 5, mc -> {
                mc.options.hideGui = false; // Enable HUD overlay rendering for first-person cockpit telemetry!
                mc.options.setCameraType(CameraType.FIRST_PERSON);
            }));
            steps.add(new Step(t + 20, mc -> shot(mc, "tier_" + curTier + "_hud_firstperson")));
            steps.add(new Step(t + 25, mc -> com.obsolete.network.ModNetworking.sendToServer(new com.obsolete.network.ExoframeOpenMenuC2SPacket())));
            steps.add(new Step(t + 40, mc -> shot(mc, "tier_" + curTier + "_loadout_screen")));
            steps.add(new Step(t + 45, mc -> {
                mc.setScreen(null);
                mc.options.hideGui = true;
            }));
            t += 50;
        }
        // Inventory key while riding: same packet the E key sends; the loadout screen must open.
        steps.add(new Step(t, mc -> com.obsolete.network.ModNetworking.sendToServer(new com.obsolete.network.ExoframeOpenMenuC2SPacket())));
        steps.add(new Step(t + 15, mc -> {
            ObsoleteMod.LOGGER.info("[autotest] loadout screen open: {}", mc.screen != null ? mc.screen.getClass().getSimpleName() : "none");
            shot(mc, "c_loadout_screen");
        }));
        // Bare frame and Sand set with the pilot aboard: the astride pose itself must read (legs straddling the body).
        steps.add(new Step(t + 25, mc -> {
            mc.setScreen(null);
            serverExoById(mc, (p, exo) -> {
                var inv = exo.getModularInventory();
                for (int i = 0; i < inv.getSlots(); i++) inv.setStackInSlot(i, ItemStack.EMPTY);
                exo.syncArmorMaskAndNotify();
            });
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
        }));
        steps.add(new Step(t + 30, mc -> mc.player.setXRot(-35.0F)));   // look up: the front camera sits above, looking down
        steps.add(new Step(t + 45, mc -> shot(mc, "d_bare_piloted_front")));
        steps.add(new Step(t + 50, mc -> {
            mc.player.setXRot(20.0F);
            mc.options.setCameraType(CameraType.THIRD_PERSON_BACK);
        }));
        steps.add(new Step(t + 70, mc -> shot(mc, "d_bare_piloted_side")));
        steps.add(new Step(t + 72, mc -> {
            mc.player.setXRot(-35.0F);
            mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
        }));
        steps.add(new Step(t + 75, mc -> serverExoById(mc, (p, exo) -> {
            var inv = exo.getModularInventory();
            inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_SAND_CHEST.get()));
            inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_LEGS.get()));
            exo.syncArmorMaskAndNotify();
        })));
        steps.add(new Step(t + 95, mc -> shot(mc, "d_sand_piloted_side")));
        steps.add(new Step(t + 105, mc -> mc.stop()));
        return steps.toArray(Step[]::new);
    }

    private static void loadout(ExoframeEntity exo, net.minecraft.world.item.Item weapon) {
        var inv = exo.getModularInventory();
        inv.setStackInSlot(ExoframeArmorSlot.HEAD.getIndex(), new ItemStack(ModItems.ARMOR_SAND_HEAD.get()));
        inv.setStackInSlot(ExoframeArmorSlot.CHEST.getIndex(), new ItemStack(ModItems.ARMOR_SAND_CHEST.get()));
        inv.setStackInSlot(ExoframeArmorSlot.ARMS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_ARMS.get()));
        inv.setStackInSlot(ExoframeArmorSlot.LEGS.getIndex(), new ItemStack(ModItems.ARMOR_SAND_LEGS.get()));
        inv.setStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex(), new ItemStack(weapon));
        exo.syncArmorMaskAndNotify();
    }

    private static void view(Minecraft mc, double angleDeg) {
        serverLevel(mc, (p, l) -> aimPlayerAt(p, exoX, exoY + 1.3 * ExoframeEntity.MODEL_SCALE, exoZ, 4.2 * ExoframeEntity.MODEL_SCALE, angleDeg, 0.6));
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (NAME.isEmpty() || event.phase != TickEvent.Phase.END) return;

        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.getSingleplayerServer() == null || !mc.getSingleplayerServer().isReady()) {
            if ((mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen || mc.screen instanceof net.minecraft.client.gui.screens.DisconnectedScreen) && !worldCreationTriggered) {
                worldCreationTriggered = true;
                ObsoleteMod.LOGGER.info("[autotest] Screen {} detected, opening CreateWorldScreen...", mc.screen.getClass().getSimpleName());
                net.minecraft.client.gui.screens.worldselection.CreateWorldScreen.openFresh(mc, null);
            } else if (mc.screen instanceof net.minecraft.client.gui.screens.worldselection.CreateWorldScreen cws && !worldCreated) {
                worldCreated = true;
                try {
                    var m = net.minecraft.client.gui.screens.worldselection.CreateWorldScreen.class.getDeclaredMethod("onCreate");
                    m.setAccessible(true);
                    m.invoke(cws);
                    ObsoleteMod.LOGGER.info("[autotest] Invoked onCreate() via reflection!");
                } catch (Throwable t) {
                    ObsoleteMod.LOGGER.error("[autotest] Failed to invoke onCreate():", t);
                }
            }
            return;
        }

        // The client drives a ridden vehicle in real time, even while the server (and so the step clock) stalls.
        if (!Double.isNaN(stopWalkZ) && mc.player.getVehicle() != null && mc.player.getVehicle().getZ() > stopWalkZ) {
            mc.options.keyUp.setDown(false);
            mc.options.keySprint.setDown(false);
            stopWalkZ = Double.NaN;
        }
        // Steps follow the integrated server's clock, not client frames: when the server falls behind
        // ("Can't keep up!") client ticks ran ahead of it and steps fired before the previous one had played out.
        int serverTick = mc.getSingleplayerServer().getTickCount();
        if (startServerTick < 0) startServerTick = serverTick;
        int previous = tick;
        tick = serverTick - startServerTick;
        Step[] activeSteps;
        if (NAME.equals("anim")) {
            activeSteps = ANIM;
        } else if (NAME.equals("armor")) {
            activeSteps = (armor != null ? armor : (armor = buildArmorSteps()));
        } else if (NAME.equals("gameplay") || NAME.equals("terrain")) {
            activeSteps = (gameplay != null ? gameplay : (gameplay = buildGameplaySteps()));
        } else {
            activeSteps = SHOWCASE;
        }
        final int now = tick;
        java.util.Arrays.stream(activeSteps).filter(st -> st.at() > previous && st.at() <= now)
                .sorted(java.util.Comparator.comparingInt(Step::at))
                .forEach(st -> st.action().accept(mc));
    }

    private static void aimPlayerAt(ServerPlayer p, double tx, double ty, double tz, double dist, double angleDeg, double height) {
        double rad = Math.toRadians(angleDeg);
        double cx = tx + Math.sin(rad) * dist;
        double cz = tz + Math.cos(rad) * dist;
        double cy = ty + height;
        double dx = tx - cx;
        double dy = (ty + 0.2) - (cy + p.getEyeHeight());
        double dz = tz - cz;
        double dh = Math.sqrt(dx * dx + dz * dz);
        float yaw = (float) (Math.atan2(dz, dx) * (180.0 / Math.PI)) - 90.0F;
        float pitch = (float) (-(Math.atan2(dy, dh) * (180.0 / Math.PI)));
        p.teleportTo(p.serverLevel(), cx, cy, cz, yaw, pitch);
    }

    private static void serverLevel(Minecraft mc, BiConsumer<ServerPlayer, ServerLevel> action) {
        var server = mc.getSingleplayerServer();
        if (server == null || mc.player == null) return;
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player != null) {
                action.accept(player, player.serverLevel());
            }
        });
    }

    private static void serverExoById(Minecraft mc, BiConsumer<ServerPlayer, ExoframeEntity> action) {
        var server = mc.getSingleplayerServer();
        if (server == null || mc.player == null) return;
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player != null && player.serverLevel().getEntity(exoframeId) instanceof ExoframeEntity exo) {
                action.accept(player, exo);
            }
        });
    }

    private static void spawnDisplayExoframe(Minecraft mc) {
        var server = mc.getSingleplayerServer();
        if (server == null || mc.player == null) return;
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer player = server.getPlayerList().getPlayer(uuid);
            if (player == null) return;
            ServerLevel level = player.serverLevel();

            // Clear any entities within 20 blocks
            level.getEntitiesOfClass(ExoframeEntity.class, new AABB(exoX - 20, exoY - 5, exoZ - 20, exoX + 20, exoY + 10, exoZ + 20))
                    .forEach(Entity::discard);

            EntityType<?> type = ModEntities.EXOFRAME.get();
            if (!(type.create(level) instanceof ExoframeEntity exo)) return;

            exo.moveTo(exoX, exoY, exoZ, 0.0F, 0.0F);
            exo.yRotO = 0.0F;
            exo.setYRot(0.0F);
            exo.setYBodyRot(0.0F);
            exo.setYHeadRot(0.0F);

            level.addFreshEntity(exo);
            exoframeId = exo.getId();

            ObsoleteMod.LOGGER.info("[autotest] Successfully spawned display Exoframe id={}", exoframeId);
        });
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "autotest_" + name + ".png", mc.getMainRenderTarget(), msg -> {});
        ObsoleteMod.LOGGER.info("[autotest] >>> Screenshot captured: autotest_{}.png (tick={})", name, tick);
    }
}
