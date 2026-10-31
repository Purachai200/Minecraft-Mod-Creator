package com.obsolete.client.gui;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.item.*;
import com.obsolete.registry.ExoframeVariantRegistry;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

/**
 * Contextual Modular Telemetry & Role HUD for OBSOLETE Exoframe mechas.
 * Dynamically reconfigures telemetry widgets, targeting reticle, and sensors
 * based on installed modules across Head, Chest, Arms, Legs, Utility, and Weapon slots.
 */
public class ExoframeHudOverlay {

    // Scanning cache for geological telemetry
    private static long lastScanTick = -1;
    private static int cachedDiamond = 0;
    private static int cachedGold = 0;
    private static int cachedIron = 0;
    private static int cachedDebris = 0;

    public static final IGuiOverlay HUD_EXOFRAME = (ForgeGui gui, GuiGraphics graphics, float partialTick, int width, int height) -> {
        Minecraft mc = Minecraft.getInstance();
        if (mc.options.hideGui || mc.screen != null) {
            return;
        }
        if (mc.player == null || mc.level == null || !(mc.player.getVehicle() instanceof ExoframeEntity exoframe)) {
            return;
        }

        Font font = mc.font;
        int centerX = width / 2;
        int centerY = height / 2;

        // Detect installed equipment
        ItemStack headStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.HEAD.getIndex());
        ItemStack chestStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.CHEST.getIndex());
        ItemStack utilStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        ItemStack weaponStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());

        // Role Detection Flags
        boolean hasMining = weaponStack.getItem() instanceof ExoframeMiningDrillItem
                || utilStack.is(ModItems.MODULE_GEOLOGICAL_SCANNER.get())
                || chestStack.is(ModItems.ARMOR_ROLL_CAGE.get());

        boolean hasSpecOps = utilStack.is(ModItems.MODULE_NIGHT_VISION_OPTIC.get())
                || headStack.is(ModItems.ARMOR_CERBERUS_HEAD.get())
                || utilStack.is(ModItems.MODULE_CERBERUS_PACKS.get());

        boolean hasForestry = weaponStack.getItem() instanceof ExoframeChainsawItem
                || utilStack.is(ModItems.MODULE_CARGO_CRATE.get());

        boolean hasAgri = weaponStack.getItem() instanceof ExoframeCultivatorPlowItem
                || utilStack.is(ModItems.MODULE_AGRI_HOPPER.get());

        boolean hasSubmarine = utilStack.is(ModItems.MODULE_DIVING_BALLAST.get())
                || (exoframe.isInWater() && utilStack.is(ModItems.MODULE_DIVING_BALLAST.get()));

        boolean hasCombat = (weaponStack.getItem() instanceof ExoframeWeaponItem
                && !(weaponStack.getItem() instanceof ExoframeMiningDrillItem)
                && !(weaponStack.getItem() instanceof ExoframeChainsawItem)
                && !(weaponStack.getItem() instanceof ExoframeCultivatorPlowItem))
                || utilStack.is(ModItems.MODULE_TARGETING_COMPUTER.get())
                || utilStack.is(ModItems.MODULE_USMC_COMMS.get());

        // Determine Primary Operational Profile
        int tier = exoframe.getFrameTier();
        String profileName;
        int profileColor;
        int activeRoles = (hasMining ? 1 : 0) + (hasSpecOps ? 1 : 0) + (hasForestry ? 1 : 0)
                + (hasAgri ? 1 : 0) + (hasSubmarine ? 1 : 0) + (hasCombat ? 1 : 0);

        if (tier == 0) {
            profileName = "SCRAP MILITIA // CHASSIS T-0";
            profileColor = 0xFFFF9900;
        } else if (tier == 3) {
            profileName = "QUANTUM SPEC-OPS // TIER-3";
            profileColor = 0xFF00FFFF;
        } else if (tier == 2) {
            profileName = "ADVANCED TACTICAL // TIER-2";
            profileColor = 0xFF00FF88;
        } else if (activeRoles > 1) {
            profileName = "MULTI-ROLE HYBRID";
            profileColor = 0xFF00FFEE;
        } else if (hasMining) {
            profileName = "GEO-MINING // EXCAVATION";
            profileColor = 0xFFFFCC00;
        } else if (hasSpecOps) {
            profileName = "SPEC-OPS // RECON SUITE";
            profileColor = 0xFF00FF66;
        } else if (hasForestry) {
            profileName = "FORESTRY // TIMBER HARVEST";
            profileColor = 0xFFAAFF00;
        } else if (hasAgri) {
            profileName = "AGRI-TECH // CULTIVATOR";
            profileColor = 0xFFFFBB33;
        } else if (hasSubmarine) {
            profileName = "DEEP SUBMERSIBLE // NAVAL";
            profileColor = 0xFF00AAFF;
        } else if (hasCombat) {
            profileName = "COMBAT // TACTICAL FCS";
            profileColor = 0xFFFF5533;
        } else {
            profileName = "MIL-SPEC PATROL // TIER-1";
            profileColor = 0xFF00AAFF;
        }

        // ==================== 0. FIRST-PERSON IN-COCKPIT MONITOR & CAMERA PASS-THROUGH ====================
        if (mc.options.getCameraType().isFirstPerson()) {
            renderCockpitMonitorScreen(graphics, font, width, height, mc, exoframe, headStack, chestStack, utilStack, tier);
        }

        // ==================== 1. TOP CENTER: COMPASS HEADING TAPE ====================
        renderCompassHeadingTape(graphics, font, centerX, 22, mc.player.getYRot(), mc.player.getXRot(), exoframe, tier);

        // ==================== 2. CENTER SCREEN: CROSSHAIR & TARGET LOCK ====================
        renderTargetingFCS(graphics, font, centerX, centerY, mc, exoframe, tier);

        // ==================== 3. BOTTOM-LEFT: CHASSIS & ARMOR DIAGNOSTICS ====================
        renderChassisDiagnostics(graphics, font, 12, height - 76, exoframe, mc.player, profileName, profileColor, utilStack, tier);

        // ==================== 3B. TIER 3 RADAR MINI-MAP WIDGET ====================
        if (tier == 3) {
            renderRadarWidget(graphics, font, width - 45, 45, mc, exoframe);
        }

        // ==================== 4. MODULAR ROLE TELEMETRY PANELS (STACKED ON RIGHT) ====================
        int rightX = width - 180;
        int currentRightY = height - 76;

        // Render each active role widget
        if (hasCombat) {
            renderCombatWidget(graphics, font, rightX, currentRightY, exoframe, mc.player, weaponStack);
            currentRightY -= 68;
        }
        if (hasMining) {
            renderMiningWidget(graphics, font, rightX, currentRightY, exoframe, mc);
            currentRightY -= 68;
        }
        if (hasSpecOps) {
            renderSpecOpsWidget(graphics, font, rightX, currentRightY, exoframe, mc.player, mc);
            currentRightY -= 68;
        }
        if (hasForestry) {
            renderForestryWidget(graphics, font, rightX, currentRightY, exoframe, mc.player, weaponStack);
            currentRightY -= 68;
        }
        if (hasAgri) {
            renderAgriWidget(graphics, font, rightX, currentRightY, exoframe, mc.player);
            currentRightY -= 68;
        }
        if (hasSubmarine) {
            renderSubmarineWidget(graphics, font, rightX, currentRightY, exoframe, mc.player);
            currentRightY -= 68;
        }
    };

    // ==================== TOP COMPASS TAPE ====================
    private static void renderCompassHeadingTape(GuiGraphics g, Font font, int cx, int y, float yaw, float pitch, ExoframeEntity exoframe, int tier) {
        float deg = (yaw % 360.0F + 360.0F) % 360.0F;

        if (tier == 0) {
            // Tier 0: Crude analog/scrap heading display
            int boxW = 120;
            int left = cx - boxW / 2;
            g.fill(left, y, cx + boxW / 2, y + 14, 0xBB2A180E);
            g.renderOutline(left, y, boxW, 14, 0xFFFF9900);
            String card = (deg >= 315 || deg < 45) ? "N" : (deg < 135 ? "E" : (deg < 225 ? "S" : "W"));
            String hdg = String.format("[ HDG: %03.0f° %s ]", deg, card);
            g.drawString(font, hdg, cx - font.width(hdg) / 2, y + 3, 0xFFFFCC00, true);
            String coords = String.format("LOC: %d, %d, %d", exoframe.getBlockX(), exoframe.getBlockY(), exoframe.getBlockZ());
            g.drawString(font, coords, cx - font.width(coords) / 2, y + 17, 0x88FFAA00, true);
            return;
        }

        int tapeWidth = tier == 3 ? 190 : 170;
        int left = cx - tapeWidth / 2;
        int right = cx + tapeWidth / 2;

        int tapeBg = tier == 3 ? 0x99101228 : (tier == 2 ? 0x88081A12 : 0x880E1418);
        int tapeBorder = tier == 3 ? 0xFF00FFFF : (tier == 2 ? 0xFF00FF88 : 0xFF00AAFF);
        int notchCol = tier == 3 ? 0xFFDD44FF : (tier == 2 ? 0xFF00FFCC : 0xFF00FFEE);

        // Semi-transparent tactical header
        g.fill(left, y, right, y + 15, tapeBg);
        g.renderOutline(left, y, tapeWidth, 15, tapeBorder);

        // Draw compass marks
        for (int i = -40; i <= 40; i += 10) {
            float testDeg = (deg + i + 360.0F) % 360.0F;
            int markX = cx + (int) (i * 1.8F);
            if (markX >= left + 8 && markX <= right - 8) {
                int rounded = Math.round(testDeg / 10.0F) * 10;
                String cardinal = switch (rounded % 360) {
                    case 0 -> "N";
                    case 45 -> "NE";
                    case 90 -> "E";
                    case 135 -> "SE";
                    case 180 -> "S";
                    case 225 -> "SW";
                    case 270 -> "W";
                    case 315 -> "NW";
                    default -> null;
                };

                if (cardinal != null) {
                    g.drawString(font, cardinal, markX - font.width(cardinal) / 2, y + 3, notchCol, false);
                } else if (rounded % 30 == 0) {
                    g.fill(markX, y + 8, markX + 1, y + 13, tapeBorder);
                } else {
                    g.fill(markX, y + 10, markX + 1, y + 13, 0x8800AAFF);
                }
            }
        }

        // Center needle
        int needleCol = tier == 3 ? 0xFF00FFFF : (tier == 2 ? 0xFF00FF88 : 0xFFFFCC00);
        g.drawString(font, "▼", cx - 3, y - 4, needleCol, false);

        // Coordinates & Pitch telemetry below tape
        String coords = String.format("LOC: %d, %d, %d | PITCH: %+.0f°",
                exoframe.getBlockX(), exoframe.getBlockY(), exoframe.getBlockZ(), -pitch);
        g.drawString(font, coords, cx - font.width(coords) / 2, y + 18, 0xAAFFFFFF, true);
    }

    // ==================== CENTER TARGETING RETICLE & IFF ====================
    private static void renderTargetingFCS(GuiGraphics g, Font font, int cx, int cy, Minecraft mc, ExoframeEntity exoframe, int tier) {
        if (tier == 0) {
            // Tier 0: Crude iron crosshair lines, no computerized target tracking
            int chCol = exoframe.isAiming() ? 0xFFFF4422 : 0xCCFFAA00;
            g.fill(cx - 8, cy, cx - 2, cy + 1, chCol);
            g.fill(cx + 3, cy, cx + 9, cy + 1, chCol);
            g.fill(cx, cy - 8, cx + 1, cy - 2, chCol);
            g.fill(cx, cy + 3, cx + 1, cy + 9, chCol);
            if (mc.hitResult instanceof BlockHitResult bHit) {
                double dist = mc.player.getEyePosition().distanceTo(bHit.getLocation());
                if (dist <= 40.0D) {
                    String s = String.format("~%.0fm", dist);
                    g.drawString(font, s, cx + 10, cy - 4, 0x88FFAA00, true);
                }
            }
            return;
        }

        // Futuristic brackets around center crosshair
        int bSize = tier == 3 ? 8 : 6;
        int bDist = tier == 3 ? 16 : 14;
        int col = exoframe.isAiming() ? 0xFFFF3333 : (tier == 3 ? 0xDD00FFFF : (tier == 2 ? 0xDD00FF88 : 0xAA00AAFF));

        // Top-Left bracket
        g.fill(cx - bDist, cy - bDist, cx - bDist + bSize, cy - bDist + 1, col);
        g.fill(cx - bDist, cy - bDist, cx - bDist + 1, cy - bDist + bSize, col);
        // Top-Right bracket
        g.fill(cx + bDist - bSize, cy - bDist, cx + bDist, cy - bDist + 1, col);
        g.fill(cx + bDist - 1, cy - bDist, cx + bDist, cy - bDist + bSize, col);
        // Bottom-Left bracket
        g.fill(cx - bDist, cy + bDist - 1, cx - bDist + bSize, cy + bDist, col);
        g.fill(cx - bDist, cy + bDist - bSize, cx - bDist + 1, cy + bDist, col);
        // Bottom-Right bracket
        g.fill(cx + bDist - bSize, cy + bDist - 1, cx + bDist, cy + bDist, col);
        g.fill(cx + bDist - 1, cy + bDist - bSize, cx + bDist, cy + bDist, col);

        // Tier 2 & 3: Screen-edge threat indicators for nearby enemies
        if (tier >= 2 && mc.level != null) {
            Vec3 pos = exoframe.position();
            float playerYaw = mc.player.getYRot();
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e instanceof Monster monster && monster.isAlive()) {
                    double dist = pos.distanceTo(e.position());
                    if (dist <= 24.0D && dist > 2.0D) {
                        double dx = e.getX() - pos.x;
                        double dz = e.getZ() - pos.z;
                        float angleToMob = (float) Math.toDegrees(Math.atan2(dz, dx)) - 90.0F;
                        float diff = Mth.wrapDegrees(angleToMob - playerYaw);
                        if (Math.abs(diff) > 40.0F) {
                            int sideX = diff > 0 ? cx + 115 : cx - 125;
                            g.drawString(font, "<!>", sideX, cy - 4, 0xFFFF3333, true);
                        }
                    }
                }
            }
        }

        // Target Lock & Rangefinder readout
        Entity target = mc.crosshairPickEntity;
        if (target instanceof LivingEntity living) {
            boolean isHostile = target instanceof Monster;
            String iff = isHostile ? "[HOSTILE]" : "[TARGET]";
            int iffCol = isHostile ? 0xFFFF3333 : (tier >= 2 ? 0xFF00FF88 : 0xFF00FF66);

            double dist = mc.player.getEyePosition().distanceTo(target.position());
            String name = target.getType().getDescription().getString();
            float targetHp = living.getHealth();
            float targetMaxHp = living.getMaxHealth();

            String line1 = String.format("%s %s (%.1fm)", iff, name, dist);
            String line2 = String.format("HP: %.0f / %.0f", targetHp, targetMaxHp);

            g.drawString(font, line1, cx - font.width(line1) / 2, cy + 20, iffCol, true);
            g.drawString(font, line2, cx - font.width(line2) / 2, cy + 30, 0xFFFFFF, true);

            // Tier 3: Predictive Lead Reticle
            if (tier == 3) {
                Vec3 vel = living.getDeltaMovement();
                double leadTime = dist / 4.5D;
                int leadX = cx + (int) (vel.x * 24.0D * leadTime);
                int leadY = cy + (int) (-vel.y * 24.0D * leadTime);
                g.renderOutline(leadX - 5, leadY - 5, 10, 10, 0xFFDD44FF);
                g.drawString(font, "LEAD", leadX - 8, leadY - 14, 0xFFDD44FF, true);
            }
        } else if (mc.hitResult instanceof BlockHitResult blockHit && mc.hitResult.getType() == HitResult.Type.BLOCK) {
            double dist = mc.player.getEyePosition().distanceTo(blockHit.getLocation());
            if (dist <= 64.0D) {
                String rng = String.format("RNG: %.1fm", dist);
                g.drawString(font, rng, cx - font.width(rng) / 2, cy + 18, 0x88FFFFFF, true);
            }
        }
    }

    // ==================== BOTTOM-LEFT CHASSIS & ARMOR DIAGNOSTICS ====================
    private static void renderChassisDiagnostics(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Player player, String profile, int profCol, ItemStack utilStack, int tier) {
        int w = 168;
        int h = 72;

        int bgCol = tier == 0 ? 0xDD22140A : (tier == 3 ? 0xDD101228 : (tier == 2 ? 0xDD0A1C14 : 0xDD0A1015));
        int borderCol = tier == 0 ? 0xFFFF9900 : (tier == 3 ? 0xFF00FFFF : (tier == 2 ? 0xFF00FF88 : 0xFF00AAFF));

        // Backdrop
        g.fill(x - 4, y - 4, x + w, y + h, bgCol);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, borderCol);

        // Profile Badge Header
        String stance = exoframe.isAiming() ? "ADS" : (exoframe.isMechCrouching() ? "CROUCH" : (player.isSprinting() ? "SPRINT" : "CRUISE"));
        int stanceCol = exoframe.isAiming() ? 0xFFFF3333 : (exoframe.isMechCrouching() ? 0xFFFFCC00 : (player.isSprinting() ? 0xFF00FFEE : 0xFF00FF66));

        g.drawString(font, profile, x, y, profCol, false);

        // 1. Hull Integrity Bar
        float health = exoframe.getHealth();
        float maxHealth = exoframe.getMaxHealth();
        float healthPct = Math.max(0.0F, Math.min(1.0F, health / maxHealth));

        int barW = 158;
        int barH = 7;
        int barY = y + 12;
        g.fill(x, barY, x + barW, barY + barH, 0xFF222830);

        int hpCol = healthPct > 0.6F ? (tier == 0 ? 0xFFFFCC00 : 0xFF00FF66) : (healthPct > 0.3F ? 0xFFFFCC00 : 0xFFFF3333);
        g.fill(x, barY, x + (int) (barW * healthPct), barY + barH, hpCol);
        String hpText = String.format("HULL: %.0f/%.0f (%.0f%%)", health, maxHealth, healthPct * 100);
        g.drawString(font, hpText, x + 2, barY - 1, 0xFFFFFF, true);

        // 2. Kinematics (Speed km/h + Stance) & Utility Bay Readout
        double speedKmh = Math.sqrt(exoframe.getDeltaMovement().horizontalDistanceSqr()) * 72.0D;
        String speedStr = tier == 0 ? String.format("SPD: %.0f [MANUAL]", speedKmh) : String.format("SPD: %.0f [%s]", speedKmh, stance);
        String utilName = utilStack.isEmpty() ? "BAY: EMPTY" : "BAY: " + utilStack.getHoverName().getString();
        if (font.width(utilName) > 85) {
            utilName = utilName.substring(0, 12) + "...";
        }
        g.drawString(font, speedStr, x, y + 24, stanceCol, false);
        g.drawString(font, utilName, x + 76, y + 24, tier == 0 ? 0xFFFFCC00 : 0xFFAAAAFF, false);

        // 3. Modular Armor Slot Status (H, C, A, L)
        int armorY = y + 36;
        drawArmorSlot(g, font, x, armorY, "H", exoframe, ExoframeArmorSlot.HEAD);
        drawArmorSlot(g, font, x + 40, armorY, "C", exoframe, ExoframeArmorSlot.CHEST);
        drawArmorSlot(g, font, x + 80, armorY, "A", exoframe, ExoframeArmorSlot.ARMS);
        drawArmorSlot(g, font, x + 120, armorY, "L", exoframe, ExoframeArmorSlot.LEGS);

        // Chassis Subsystem status
        String sysText = tier == 0 ? "DIESEL-HYDRAULIC: ANALOG FEED"
                : (tier == 3 ? "QUANTUM BUS: SYNCED // EW: 100%"
                : (tier == 2 ? "FCS MK-II: ONLINE // TEMP: 342°C"
                : "SERVOS: NOMINAL | HYDRAULICS: 100%"));
        g.drawString(font, sysText, x, y + 58, 0x88FFFFFF, false);
    }

    private static void drawArmorSlot(GuiGraphics g, Font font, int x, int y, String label, ExoframeEntity exoframe, ExoframeArmorSlot slot) {
        ItemStack stack = exoframe.getModularInventory().getStackInSlot(slot.getIndex());
        if (stack.getItem() instanceof ExoframeArmorItem) {
            int max = stack.getMaxDamage();
            int cur = max - stack.getDamageValue();
            float pct = (float) cur / (float) max;
            int color = pct > 0.5F ? 0xFF00FF66 : (pct > 0.25F ? 0xFFFFCC00 : 0xFFFF3333);
            g.drawString(font, label + ":" + (int) (pct * 100) + "%", x, y, color, false);
        } else {
            g.drawString(font, label + ":---", x, y, 0xFF556677, false);
        }
    }

    // ==================== ROLE 1: COMBAT FIRE CONTROL SYSTEM ====================
    private static void renderCombatWidget(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Player player, ItemStack weaponStack) {
        int w = 170;
        int h = 60;
        g.fill(x - 4, y - 4, x + w, y + h, 0xDD180E0E);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, 0xFFFF5533);

        g.drawString(font, "FIRE CONTROL SYSTEM // FCS", x, y, 0xFFFF5533, false);

        String wName = weaponStack.isEmpty() ? "MELEE BARE FIST" : weaponStack.getHoverName().getString();
        if (font.width(wName) > 160) wName = wName.substring(0, 22) + "...";
        g.drawString(font, wName, x, y + 12, 0xFFFFFFFF, false);

        int ammoCount = countAmmo(player, exoframe);
        String ammoText = ammoCount > 0 ? "MUNITIONS: " + ammoCount + " RDS" : "MUNITIONS: DEPLETED";
        int ammoCol = ammoCount > 0 ? 0xFFFFCC00 : 0xFFFF2222;
        g.drawString(font, ammoText, x, y + 24, ammoCol, false);

        // Fire Mode
        String mode = exoframe.isAiming() ? "AIM STANCE: PRECISION ADS" : "AIM STANCE: RAPID FIRE";
        g.drawString(font, mode, x, y + 36, 0xAAFFFFFF, false);

        // Small visual ammo level bar
        int barW = 158;
        int barH = 4;
        g.fill(x, y + 48, x + barW, y + 48 + barH, 0xFF331111);
        int fill = Math.min(barW, ammoCount * 2);
        g.fill(x, y + 48, x + fill, y + 48 + barH, 0xFFFF7722);
    }

    // ==================== ROLE 2: GEOLOGICAL PROXIMITY MINING SONAR ====================
    private static void renderMiningWidget(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Minecraft mc) {
        int w = 170;
        int h = 60;
        g.fill(x - 4, y - 4, x + w, y + h, 0xDD0E1818);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, 0xFFFFCC00);

        g.drawString(font, "GEOLOGICAL SONAR // MINING", x, y, 0xFFFFCC00, false);

        // Strata & Depth
        int blockY = exoframe.getBlockY();
        String strata = blockY > 60 ? "SURFACE STRATA" : (blockY >= 0 ? "STONE STRATA" : (blockY >= -55 ? "DEEPSLATE" : "BEDROCK NEAR!"));
        int strataCol = blockY < -55 ? 0xFFFF2222 : 0xFF00FFEE;
        g.drawString(font, String.format("DEPTH: Y=%d [%s]", blockY, strata), x, y + 12, strataCol, false);

        // Scan nearby ores every 10 ticks
        long currentTick = mc.level != null ? mc.level.getGameTime() : 0;
        if (lastScanTick == -1 || currentTick - lastScanTick >= 10) {
            lastScanTick = currentTick;
            scanSurroundingOres(exoframe, mc);
        }

        // Mineral proximity readout
        String oreStr = String.format("💎DIA:%d  🌟GLD:%d  ⚙IRN:%d", cachedDiamond, cachedGold, cachedIron);
        g.drawString(font, oreStr, x, y + 24, 0xFFFFFFFF, false);

        // Ambient Light hazard warning
        int light = mc.level != null ? mc.level.getBrightness(LightLayer.BLOCK, exoframe.blockPosition()) : 15;
        String lightText = light == 0 ? "LIGHT: 0 [MOB HAZARD HIGH]" : String.format("LIGHT: %d [SAFE]", light);
        int lightCol = light == 0 ? 0xFFFF3333 : 0xFF00FF66;
        g.drawString(font, lightText, x, y + 36, lightCol, false);

        // Rotary Torque
        g.drawString(font, "DRILL TORQUE: 100% [READY]", x, y + 47, 0x88FFFFFF, false);
    }

    private static void scanSurroundingOres(ExoframeEntity exoframe, Minecraft mc) {
        if (mc.level == null) return;
        cachedDiamond = 0;
        cachedGold = 0;
        cachedIron = 0;
        cachedDebris = 0;

        BlockPos center = exoframe.blockPosition();
        int r = 6; // 13x13x13 cube
        for (int dx = -r; dx <= r; dx++) {
            for (int dy = -r; dy <= r; dy++) {
                for (int dz = -r; dz <= r; dz++) {
                    BlockState bs = mc.level.getBlockState(center.offset(dx, dy, dz));
                    if (bs.is(BlockTags.DIAMOND_ORES) || bs.is(Blocks.DIAMOND_ORE) || bs.is(Blocks.DEEPSLATE_DIAMOND_ORE)) cachedDiamond++;
                    else if (bs.is(BlockTags.GOLD_ORES) || bs.is(Blocks.GOLD_ORE) || bs.is(Blocks.DEEPSLATE_GOLD_ORE) || bs.is(Blocks.NETHER_GOLD_ORE)) cachedGold++;
                    else if (bs.is(BlockTags.IRON_ORES) || bs.is(Blocks.IRON_ORE) || bs.is(Blocks.DEEPSLATE_IRON_ORE)) cachedIron++;
                    else if (bs.is(Blocks.ANCIENT_DEBRIS)) cachedDebris++;
                }
            }
        }
    }

    // ==================== ROLE 3: SPECIAL OPS RECON & ACOUSTIC STEALTH ====================
    private static void renderSpecOpsWidget(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Player player, Minecraft mc) {
        int w = 170;
        int h = 60;
        g.fill(x - 4, y - 4, x + w, y + h, 0xDD081A10);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, 0xFF00FF66);

        g.drawString(font, "CERBERUS // SPEC-OPS RECON", x, y, 0xFF00FF66, false);
        g.drawString(font, "OPTICS: FLIR THERMAL [ONLINE]", x, y + 12, 0xFF00FFCC, false);

        // Acoustic Footprint Meter
        double speed = Math.sqrt(exoframe.getDeltaMovement().horizontalDistanceSqr());
        String acoustic;
        int acousticCol;
        int noisePct;

        if (speed < 0.005D) {
            acoustic = "NOISE: 0 dB [GHOST // 0m]";
            acousticCol = 0xFF00FFEE;
            noisePct = 5;
        } else if (exoframe.isMechCrouching()) {
            acoustic = "NOISE: 25 dB [SILENT // 3m]";
            acousticCol = 0xFF00FF66;
            noisePct = 25;
        } else if (player.isSprinting()) {
            acoustic = "NOISE: 88 dB [ALERT // 18m]";
            acousticCol = 0xFFFF2222;
            noisePct = 95;
        } else {
            acoustic = "NOISE: 50 dB [NORMAL // 8m]";
            acousticCol = 0xFFFFCC00;
            noisePct = 55;
        }

        g.drawString(font, acoustic, x, y + 24, acousticCol, false);

        // Noise bar
        int barW = 158;
        g.fill(x, y + 36, x + barW, y + 40, 0xFF112211);
        g.fill(x, y + 36, x + (int) (barW * (noisePct / 100.0F)), y + 40, acousticCol);

        g.drawString(font, "SAT-LINK: ENCRYPTED (AES-256)", x, y + 45, 0x66FFFFFF, false);
    }

    // ==================== ROLE 4: FORESTRY & TIMBER LOGGING ====================
    private static void renderForestryWidget(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Player player, ItemStack weaponStack) {
        int w = 170;
        int h = 60;
        g.fill(x - 4, y - 4, x + w, y + h, 0xDD12160A);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, 0xFFAAFF00);

        g.drawString(font, "FORESTRY // TIMBER HARVEST", x, y, 0xFFAAFF00, false);

        // Engine RPM
        double speed = Math.sqrt(exoframe.getDeltaMovement().horizontalDistanceSqr());
        int rpm = speed > 0.01D ? 11800 : 1800;
        g.drawString(font, String.format("SAW RPM: %d [%s]", rpm, rpm > 5000 ? "CUTTING" : "IDLE"), x, y + 12, 0xFFFFFFFF, false);

        // Timber Cargo Counter
        int totalLogs = countLogs(player, exoframe);
        float stacks = totalLogs / 64.0F;
        g.drawString(font, String.format("CARGO: %d LOGS (%.1f STACKS)", totalLogs, stacks), x, y + 24, 0xFFFFCC00, false);

        // Cargo Capacity Bar (assuming 512 log capacity)
        float pct = Math.min(1.0F, totalLogs / 512.0F);
        int barW = 158;
        g.fill(x, y + 36, x + barW, y + 40, 0xFF222811);
        g.fill(x, y + 36, x + (int) (barW * pct), y + 40, 0xFFAAFF00);

        g.drawString(font, "CHAIN TENSION: OPTIMAL", x, y + 45, 0x66FFFFFF, false);
    }

    private static int countLogs(Player player, ExoframeEntity exoframe) {
        int count = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack stack = player.getInventory().getItem(i);
            if (stack.is(ItemTags.LOGS)) {
                count += stack.getCount();
            }
        }
        for (int i = 0; i < exoframe.getModularInventory().getSlots(); i++) {
            ItemStack stack = exoframe.getModularInventory().getStackInSlot(i);
            if (stack.is(ItemTags.LOGS)) {
                count += stack.getCount();
            }
        }
        return count;
    }

    // ==================== ROLE 5: AGRICULTURE & CULTIVATOR ====================
    private static void renderAgriWidget(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Player player) {
        int w = 170;
        int h = 60;
        g.fill(x - 4, y - 4, x + w, y + h, 0xDD181608);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, 0xFFFFBB33);

        g.drawString(font, "AGRI-SYSTEM // CULTIVATOR", x, y, 0xFFFFBB33, false);

        // Soil moisture scanner (block under feet)
        BlockPos below = exoframe.blockPosition().below();
        BlockState belowState = exoframe.level().getBlockState(below);
        String soilText;
        int soilCol;

        if (belowState.getBlock() instanceof FarmBlock) {
            int moisture = belowState.getValue(FarmBlock.MOISTURE);
            soilText = String.format("SOIL: FARMLAND [WET %d/7]", moisture);
            soilCol = moisture >= 4 ? 0xFF00FFEE : 0xFFFFCC00;
        } else if (belowState.is(Blocks.DIRT) || belowState.is(Blocks.GRASS_BLOCK)) {
            soilText = "SOIL: ARABLE DIRT [TILLABLE]";
            soilCol = 0xFF00FF66;
        } else {
            soilText = "SOIL: NON-ARABLE TERRAIN";
            soilCol = 0xFF888888;
        }
        g.drawString(font, soilText, x, y + 12, soilCol, false);

        // Crop Maturity Scanner (in front of mech)
        BlockPos inFront = exoframe.blockPosition().relative(exoframe.getDirection());
        BlockState cropState = exoframe.level().getBlockState(inFront);
        String cropText = "CROP: NONE DETECTED";
        int cropCol = 0x88FFFFFF;

        if (cropState.getBlock() instanceof CropBlock crop) {
            int age = crop.getAge(cropState);
            int maxAge = crop.getMaxAge();
            boolean ready = crop.isMaxAge(cropState);
            cropText = String.format("CROP: %s [%d/%d %s]",
                    cropState.getBlock().getName().getString(), age, maxAge, ready ? "READY" : "GROWING");
            cropCol = ready ? 0xFF00FF66 : 0xFFFFCC00;
        }
        g.drawString(font, cropText, x, y + 24, cropCol, false);

        // Seed Hopper Inventory
        int seedCount = countSeeds(player, exoframe);
        g.drawString(font, String.format("HOPPER: %d SEEDS LOADED", seedCount), x, y + 36, 0xFFFFFFFF, false);
        g.drawString(font, "PLOW: HYDRAULIC 3x3 SWATH", x, y + 47, 0x66FFFFFF, false);
    }

    private static int countSeeds(Player player, ExoframeEntity exoframe) {
        int count = 0;
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack stack = player.getInventory().getItem(i);
            if (stack.is(Items.WHEAT_SEEDS) || stack.is(Items.CARROT)
                    || stack.is(Items.POTATO) || stack.is(Items.BEETROOT_SEEDS)) {
                count += stack.getCount();
            }
        }
        return count;
    }

    // ==================== ROLE 6: SUBMARINE & DEEP DIVING ====================
    private static void renderSubmarineWidget(GuiGraphics g, Font font, int x, int y, ExoframeEntity exoframe, Player player) {
        int w = 170;
        int h = 60;
        g.fill(x - 4, y - 4, x + w, y + h, 0xDD08121A);
        g.renderOutline(x - 4, y - 4, w + 4, h + 4, 0xFF00AAFF);

        g.drawString(font, "DEEP SUBMERSIBLE // NAVAL", x, y, 0xFF00AAFF, false);

        // Submerged Depth (meters below sea level Y=63)
        double depth = Math.max(0.0D, 63.0D - exoframe.getY());
        double pressure = 1.0D + (depth * 0.1D);
        String depthStr = exoframe.isInWater() ? String.format("DEPTH: %.1fm (%.2f ATM)", depth, pressure) : "DEPTH: SURFACED [DRY]";
        g.drawString(font, depthStr, x, y + 12, 0xFF00FFEE, false);

        // Life support O2
        g.drawString(font, "O2 REBREATHER: 100% [NOMINAL]", x, y + 24, 0xFF00FF66, false);

        // Ballast status
        boolean blowing = player.getDeltaMovement().y > 0.01D;
        String ballast = blowing ? "BALLAST: BLOWING [ASCENT]" : "BALLAST: FLOODED [SEABED HEAVY]";
        int ballastCol = blowing ? 0xFFFFCC00 : 0xFF00AAFF;
        g.drawString(font, ballast, x, y + 36, ballastCol, false);

        g.drawString(font, "HYDRO-SONAR: SCANNING SEABED", x, y + 47, 0x66FFFFFF, false);
    }

    // ==================== IN-COCKPIT DIGITAL MONITOR SCREEN & CAMERA PASS-THROUGH ====================
    private static void renderCockpitMonitorScreen(GuiGraphics g, Font font, int width, int height, Minecraft mc, ExoframeEntity exoframe, ItemStack headStack, ItemStack chestStack, ItemStack utilStack, int tier) {
        // 1. Determine Camera Sensor Type & Accent Color based on Armor / Modules
        ExoframeVariantRegistry.SensorProfile profile = ExoframeVariantRegistry.resolveSensorProfile(headStack, chestStack, utilStack, exoframe.isInWater());
        String camName = profile.camName();
        String camSub = profile.camSub();
        int camCol = profile.camColor();
        int borderCol = profile.borderColor();

        long time = mc.level != null ? mc.level.getGameTime() : 0;

        if (tier == 0) {
            // Tier 0: CRT Monitor Raster & Amber Phosphor
            int sweepY = (int) ((time * 4) % height);
            g.fill(0, sweepY, width, sweepY + 4, 0x33FFAA00);
            for (int sy = 0; sy < height; sy += 3) {
                g.fill(0, sy, width, sy + 1, 0x14FFAA00);
            }
            camCol = 0xFFFFCC00;
            borderCol = 0xFFFF9900;
            camName = "CRT-04 // ANALOG CH";
            camSub = "COMPOSITE NTSC PASS-THROUGH";
        } else if (tier == 3) {
            camCol = 0xFF00FFFF;
            borderCol = 0xFF00FFFF;
            camName = "8K QUANTUM AR FEED";
            camSub = "MULTI-BAND SENSOR FUSION";
        } else if (tier == 2) {
            camCol = 0xFF00FF88;
            borderCol = 0xFF00FF88;
            camName = "HD-FLIR THERMAL";
            camSub = "ENHANCED OPTICAL MATRIX";
        }

        // 2. Cockpit Monitor Frame (Outer Bezel & Vignette)
        g.fill(0, 0, width, 3, 0xCC050A0E);
        g.fill(0, height - 3, width, height, 0xCC050A0E);
        g.fill(0, 0, 3, height, 0xCC050A0E);
        g.fill(width - 3, 0, width, height, 0xCC050A0E);

        // Cockpit Monitor Corner Brackets
        int brLen = 40;
        int mX = 6;
        int mY = 6;
        // Top-Left
        g.fill(mX, mY, mX + brLen, mY + 2, borderCol);
        g.fill(mX, mY, mX + 2, mY + brLen, borderCol);
        g.fill(mX + 4, mY + 4, mX + 8, mY + 8, borderCol);
        // Top-Right
        g.fill(width - mX - brLen, mY, width - mX, mY + 2, borderCol);
        g.fill(width - mX - 2, mY, width - mX, mY + brLen, borderCol);
        g.fill(width - mX - 8, mY + 4, width - mX - 4, mY + 8, borderCol);
        // Bottom-Left
        g.fill(mX, height - mY - 2, mX + brLen, height - mY, borderCol);
        g.fill(mX, height - mY - brLen, mX + 2, height - mY, borderCol);
        g.fill(mX + 4, height - mY - 8, mX + 8, height - mY - 4, borderCol);
        // Bottom-Right
        g.fill(width - mX - brLen, height - mY - 2, width - mX, height - mY, borderCol);
        g.fill(width - mX - 2, height - mY - brLen, width - mX, height - mY, borderCol);
        g.fill(width - mX - 8, height - mY - 8, width - mX - 4, height - mY - 4, borderCol);

        // 3. Subtle Digital Scanline Raster (gives authentic in-cockpit monitor texture)
        if (tier != 0) {
            int scanAlpha = 0x07000000;
            for (int sy = 0; sy < height; sy += 4) {
                g.fill(0, sy, width, sy + 1, scanAlpha);
            }
        }

        // 4. Top-Left Camera Channel & Lens Meta
        g.drawString(font, "[CAM: " + camName + "]", mX + 10, mY + 2, camCol, true);
        g.drawString(font, camSub, mX + 10, mY + 11, 0x88FFFFFF, true);

        // 5. Top-Right Live Feed & Optics Telemetry
        boolean blink = (time / 15) % 2 == 0;
        String liveStr = blink ? "● REC [LIVE]" : "○ REC [LIVE]";
        int liveCol = blink ? 0xFFFF3333 : 0x88AA2222;

        String zoomStr = exoframe.isAiming() ? "[2.5x ADS]" : "[1.0x]";
        String rightLine1 = liveStr + " " + zoomStr;
        String fovStr = "LENS: 28mm // F/1.4";

        g.drawString(font, rightLine1, width - mX - font.width(rightLine1) - 10, mY + 2, liveCol, true);
        g.drawString(font, fovStr, width - mX - font.width(fovStr) - 10, mY + 11, 0x88FFFFFF, true);

        // 6. Horizon Ladder Wings (Subtle attitude line)
        int cx = width / 2;
        int cy = height / 2;
        int wingLen = 32;
        int wingDist = 65;
        int wingCol = tier == 3 ? 0x6600FFFF : (tier == 2 ? 0x6600FF88 : 0x6600AAFF);
        // Left horizon wing
        g.fill(cx - wingDist - wingLen, cy, cx - wingDist, cy + 1, wingCol);
        g.fill(cx - wingDist, cy - 3, cx - wingDist + 1, cy + 4, wingCol);
        // Right horizon wing
        g.fill(cx + wingDist, cy, cx + wingDist + wingLen, cy + 1, wingCol);
        g.fill(cx + wingDist, cy - 3, cx + wingDist + 1, cy + 4, wingCol);

        // Pitch Angle readout near left wing
        float pitch = -mc.player.getXRot();
        String pitchStr = String.format("%+.0f°", pitch);
        g.drawString(font, pitchStr, cx - wingDist - font.width(pitchStr) - 4, cy - 4, 0x88FFFFFF, true);
    }

    // ==================== TIER 3: MINI-RADAR SITUATIONAL MAP ====================
    private static void renderRadarWidget(GuiGraphics g, Font font, int rx, int ry, Minecraft mc, ExoframeEntity exoframe) {
        int r = 20;
        g.fill(rx - r, ry - r, rx + r, ry + r, 0xAA080B14);
        g.renderOutline(rx - r, ry - r, r * 2, r * 2, 0xFF00FFFF);

        g.drawString(font, "▲", rx - 3, ry - 4, 0xFF00FFFF, false);

        long time = mc.level != null ? mc.level.getGameTime() : 0;
        double angle = (time * 0.12) % (2 * Math.PI);
        int sx = rx + (int) (Math.cos(angle) * (r - 2));
        int sy = ry + (int) (Math.sin(angle) * (r - 2));
        g.fill(rx, ry, sx, sy, 0x6600FFFF);

        if (mc.level != null) {
            Vec3 pos = exoframe.position();
            float yawRad = (float) Math.toRadians(mc.player.getYRot());
            for (Entity e : mc.level.entitiesForRendering()) {
                if (e != exoframe && e != mc.player && e instanceof LivingEntity living && living.isAlive()) {
                    double dx = e.getX() - pos.x;
                    double dz = e.getZ() - pos.z;
                    double dist = Math.sqrt(dx * dx + dz * dz);
                    if (dist <= 28.0 && dist > 1.0) {
                        double relX = dx * Math.cos(-yawRad) - dz * Math.sin(-yawRad);
                        double relZ = dx * Math.sin(-yawRad) + dz * Math.cos(-yawRad);
                        int bx = rx + (int) (relX * (r - 4) / 28.0);
                        int by = ry + (int) (relZ * (r - 4) / 28.0);
                        int blipCol = (e instanceof Monster) ? 0xFFFF3333 : 0xFF00FF66;
                        g.fill(bx - 1, by - 1, bx + 1, by + 1, blipCol);
                    }
                }
            }
        }
        g.drawString(font, "RADAR", rx - 12, ry + r + 2, 0x8800FFFF, false);
    }

    private static int countAmmo(Player player, ExoframeEntity exoframe) {
        int count = 0;
        ItemStack util = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (util.getItem() instanceof ExoframeAmmoItem) {
            count += util.getCount();
        }
        for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
            ItemStack stack = player.getInventory().getItem(i);
            if (stack.getItem() instanceof ExoframeAmmoItem) {
                count += stack.getCount();
            }
        }
        return count;
    }
}
