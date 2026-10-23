package com.titancombat.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.titancombat.client.KeyInputHandler;
import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechFaction;
import com.titancombat.entity.MechState;
import com.titancombat.entity.TitanClass;
import com.titancombat.item.TitanAmmoItem;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

import java.util.ArrayList;
import java.util.List;

public class MechCockpitHudOverlay {

    private static final ResourceLocation COCKPIT_CANOPY =
            new ResourceLocation("titancombat", "textures/gui/cockpit_canopy.png");

    private static final String[] CARDINALS = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
    private static final String[] TITAN_WEAPONS = {
            "SPLITTER RIFLE",   // ION
            "T-203 THERMITE",   // SCORCH
            "LEADWALL SHOTGUN", // RONIN
            "40MM TRACKER",     // TONE
            "PREDATOR CANNON",  // LEGION
            "XO-16 CHAIN GUN",  // MONARCH
            "PLASMA RAILGUN"    // NORTHSTAR
    };

    private static int cachedAmmoCount = 0;
    private static int lastAmmoCheckTick = -1;

    // Tactical Radar Cache (scanned at 4 Hz to avoid GC memory allocation and FPS stutters)
    private static final List<RadarContact> CACHED_CONTACTS = new ArrayList<>();
    private static int lastRadarTick = -1;
    private static int cachedHostileCount = 0;

    private record RadarContact(double dx, double dz, boolean hostile, boolean isPlayer) {}

    public static final IGuiOverlay HUD_COCKPIT = (ForgeGui gui, GuiGraphics guiGraphics, float partialTick, int screenWidth, int screenHeight) -> {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || !(player.getVehicle() instanceof BaseMechEntity mech)) {
            return;
        }

        int centerX = screenWidth / 2;
        int centerY = screenHeight / 2;
        boolean is1stPerson = mc.options.getCameraType() == CameraType.FIRST_PERSON;

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        // ==========================================
        // 1. IMMERSIVE FIRST-PERSON COCKPIT CANOPY
        // ==========================================
        if (is1stPerson) {
            // Authentic Titanfall Cockpit Dashboard & Canopy Enclosure
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 0.92F);
            guiGraphics.blit(COCKPIT_CANOPY, 0, 0, 0, 0, screenWidth, screenHeight, screenWidth, screenHeight);
            RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);

            // Precision combat targeting reticle with dynamic target lock
            Entity lockedTarget = mc.crosshairPickEntity;
            boolean isTargetHostile = lockedTarget instanceof LivingEntity living && living != mech && !mech.isAlliedTo(living);
            int reticleColor = isTargetHostile ? 0xFFFF1744 : 0xAA00E5FF;

            // Reticle brackets flanking center crosshair
            guiGraphics.fill(centerX - 18, centerY - 8, centerX - 16, centerY + 8, reticleColor);
            guiGraphics.fill(centerX - 16, centerY - 8, centerX - 12, centerY - 6, reticleColor);
            guiGraphics.fill(centerX - 16, centerY + 6, centerX - 12, centerY + 8, reticleColor);

            guiGraphics.fill(centerX + 16, centerY - 8, centerX + 18, centerY + 8, reticleColor);
            guiGraphics.fill(centerX + 12, centerY - 8, centerX + 16, centerY - 6, reticleColor);
            guiGraphics.fill(centerX + 12, centerY + 6, centerX + 16, centerY + 8, reticleColor);

            guiGraphics.fill(centerX - 1, centerY - 14, centerX + 1, centerY - 11, reticleColor);
            guiGraphics.fill(centerX - 1, centerY + 11, centerX + 1, centerY + 14, reticleColor);

            // Center aim dot
            guiGraphics.fill(centerX - 1, centerY - 1, centerX + 1, centerY + 1, reticleColor);

            if (isTargetHostile) {
                // Target locked notification
                String lockText = "◆ TARGET LOCKED: " + lockedTarget.getName().getString().toUpperCase() + " ◆";
                int lockW = mc.font.width(lockText);
                guiGraphics.drawString(mc.font, lockText, centerX - (lockW / 2), centerY + 18, 0xFFFF1744, true);

                String distText = String.format("%.1fm", player.distanceTo(lockedTarget));
                int distW = mc.font.width(distText);
                guiGraphics.drawString(mc.font, distText, centerX - (distW / 2), centerY + 28, 0xFFFF8A80, true);
            }
        }

        // ==========================================
        // 2. TOP TACTICAL TELEMETRY & COMPASS
        // ==========================================
        int yaw = (int) (player.getYRot() % 360);
        if (yaw < 0) yaw += 360;
        String cardinal = getCardinal(yaw);
        int pitch = (int) player.getXRot();

        TitanClass titanClass = (mech instanceof BaseTitanEntity titan) ? titan.getTitanClass() : null;
        String titanTitle = (titanClass != null) ? titanClass.getDisplayName().toUpperCase() + " TITAN" : "AEGIS STRIKER";
        String pilotName = (mech instanceof BaseTitanEntity titan && !titan.getOwnerName().isEmpty()) ? titan.getOwnerName() : player.getName().getString();
        MechFaction faction = MechFaction.byId(mech.getFactionId());

        // Header Telemetry Bar
        Component headerText = Component.literal("◆ " + titanTitle + " // PILOT: " + pilotName.toUpperCase() + " // " + faction.getDisplayName().toUpperCase() + " ◆");
        int headerW = mc.font.width(headerText);
        guiGraphics.fill(centerX - (headerW / 2) - 10, 8, centerX + (headerW / 2) + 10, 22, 0xDD080D14);
        guiGraphics.fill(centerX - (headerW / 2) - 10, 8, centerX + (headerW / 2) + 10, 9, 0xFF00E5FF);
        guiGraphics.fill(centerX - (headerW / 2) - 10, 21, centerX + (headerW / 2) + 10, 22, 0x4400E5FF);
        guiGraphics.drawString(mc.font, headerText, centerX - (headerW / 2), 11, 0xFF00E5FF, false);

        // Tactical Compass Readout
        Component compassText = Component.literal("[ HDG: " + String.format("%03d°", yaw) + " " + cardinal + "  |  PITCH: " + String.format("%+03d°", pitch) + "  |  TITAN OS: v1.5.1 ONLINE ]");
        int compassW = mc.font.width(compassText);
        guiGraphics.drawString(mc.font, compassText, centerX - (compassW / 2), 25, 0xAA80D8FF, true);

        // ==========================================
        // 3. TACTICAL 360° PROXIMITY RADAR (Upper Left)
        // ==========================================
        int radarX = 36;
        int radarY = 56;
        int radarR = 20;

        // Container
        guiGraphics.fill(radarX - radarR - 4, radarY - radarR - 12, radarX + radarR + 4, radarY + radarR + 6, 0xEE080D14);
        guiGraphics.fill(radarX - radarR - 4, radarY - radarR - 12, radarX + radarR + 4, radarY - radarR - 11, 0xAA00E5FF);
        guiGraphics.drawString(mc.font, "◆ RADAR 24M", radarX - radarR, radarY - radarR - 9, 0xFF00E5FF, false);

        // Radar background and range ring
        guiGraphics.fill(radarX - radarR, radarY - radarR, radarX + radarR, radarY + radarR, 0x66001824);
        guiGraphics.fill(radarX - 1, radarY - radarR, radarX + 1, radarY + radarR, 0x2200E5FF);
        guiGraphics.fill(radarX - radarR, radarY - 1, radarX + radarR, radarY + 1, 0x2200E5FF);

        // Center pilot dot (Cyan)
        guiGraphics.fill(radarX - 1, radarY - 1, radarX + 2, radarY + 2, 0xFF00E5FF);

        // North indicator tick on radar ring
        guiGraphics.fill(radarX - 1, radarY - radarR, radarX + 1, radarY - radarR + 2, 0xFF00E5FF);

        // Refresh entity radar scan every 5 ticks
        if (player.tickCount - lastRadarTick >= 5 || lastRadarTick == -1) {
            lastRadarTick = player.tickCount;
            CACHED_CONTACTS.clear();
            cachedHostileCount = 0;
            if (mc.level != null) {
                AABB scanBox = mech.getBoundingBox().inflate(24.0D, 10.0D, 24.0D);
                List<LivingEntity> entities = mc.level.getEntitiesOfClass(LivingEntity.class, scanBox,
                        e -> e != mech && e != player && e.isAlive());
                for (LivingEntity target : entities) {
                    double dx = target.getX() - mech.getX();
                    double dz = target.getZ() - mech.getZ();
                    boolean hostile = (target instanceof Monster) || !mech.isAlliedTo(target);
                    if (hostile) cachedHostileCount++;
                    CACHED_CONTACTS.add(new RadarContact(dx, dz, hostile, target instanceof Player));
                }
            }
        }

        // Render Blips rotated by player heading
        double radAngle = -Math.toRadians(player.getYRot());
        double cosA = Math.cos(radAngle);
        double sinA = Math.sin(radAngle);

        for (RadarContact c : CACHED_CONTACTS) {
            double rx = c.dx * cosA - c.dz * sinA;
            double rz = c.dx * sinA + c.dz * cosA;
            double dist = Math.sqrt(rx * rx + rz * rz);
            if (dist <= 24.0D) {
                int bx = radarX + (int) ((rx / 24.0D) * radarR);
                int by = radarY + (int) ((rz / 24.0D) * radarR);
                int blipCol = c.hostile ? 0xFFFF1744 : (c.isPlayer ? 0xFF00E5FF : 0xFF76FF03);
                guiGraphics.fill(bx - 1, by - 1, bx + 1, by + 1, blipCol);
            }
        }

        // Radar Target Count summary
        String threatText = cachedHostileCount > 0 ? "⚠ THREAT: " + cachedHostileCount : "ALL CLEAR";
        int threatCol = cachedHostileCount > 0 ? 0xFFFF1744 : 0xFF00E676;
        guiGraphics.drawString(mc.font, threatText, radarX - radarR, radarY + radarR - 1, threatCol, false);

        // ==========================================
        // 4. LEFT FLANK: CHASSIS INTEGRITY & DEFENSE MATRIX
        // ==========================================
        int leftX = 22;
        int barW = 144;
        int bottomY = screenHeight - 78;

        float health = mech.getHealth();
        float maxHealth = mech.getMaxHealth();
        float healthPct = Math.max(0.0F, Math.min(1.0F, health / maxHealth));

        // Armored Panel Container
        guiGraphics.fill(leftX - 6, bottomY - 14, leftX + barW + 6, bottomY + 44, 0xEE080D14);
        guiGraphics.fill(leftX - 6, bottomY - 14, leftX + barW + 6, bottomY - 13, 0xAA00E5FF);

        // Header Title
        guiGraphics.drawString(mc.font, "◆ HULL INTEGRITY", leftX, bottomY - 10, 0xFFFFFFFF, false);
        String hpNum = (int) health + " / " + (int) maxHealth + " [" + (int)(healthPct * 100) + "%]";
        int hpNumW = mc.font.width(hpNum);
        guiGraphics.drawString(mc.font, hpNum, leftX + barW - hpNumW, bottomY - 10, 0xFFAAAAAA, false);

        // Segmented Hull Bar (10 Armored Composite Plates)
        int hullColor = healthPct > 0.5F ? 0xFF00E676 : (healthPct > 0.2F ? 0xFFFFB300 : 0xFFFF1744);
        int filledSegments = (int) Math.ceil(healthPct * 10.0F);

        int segSpacing = 2;
        int segWidth = (barW - (9 * segSpacing)) / 10;
        for (int i = 0; i < 10; i++) {
            int sx = leftX + i * (segWidth + segSpacing);
            int segColor = (i < filledSegments) ? hullColor : 0x44202830;
            guiGraphics.fill(sx, bottomY + 2, sx + segWidth, bottomY + 9, segColor);
        }

        // Kinetic Shield Bar
        float shield = mech.getShield();
        float maxShield = mech.getMaxShield();
        float shieldPct = Math.max(0.0F, Math.min(1.0F, shield / maxShield));

        guiGraphics.drawString(mc.font, "◆ KINETIC SHIELD: " + (int) shield + " / " + (int) maxShield, leftX, bottomY + 13, 0xFF00B0FF, false);
        guiGraphics.fill(leftX, bottomY + 23, leftX + barW, bottomY + 27, 0x55002040);
        int shieldFill = (int) (barW * shieldPct);
        if (shieldFill > 0) {
            guiGraphics.fill(leftX, bottomY + 23, leftX + shieldFill, bottomY + 27, 0xFF00B0FF);
        }

        // Tactical Defense Matrix Status
        boolean isDefense = mech.isDefenseActive();
        String defKey = KeyInputHandler.KEY_DEFENSE.getKey().getDisplayName().getString();
        String defStatus = isDefense ? "DEFENSE MATRIX: [ENGAGED -80%]" : "DEFENSE MATRIX: [STANDBY] [" + defKey + "]";
        int defColor = isDefense ? 0xFF00E676 : 0x8880D8FF;
        guiGraphics.drawString(mc.font, "◆ " + defStatus, leftX, bottomY + 32, defColor, false);

        // ==========================================
        // 5. RIGHT FLANK: THRUSTER BOOST & WEAPON MUNITIONS
        // ==========================================
        int rightX = screenWidth - barW - 22;

        guiGraphics.fill(rightX - 6, bottomY - 14, rightX + barW + 6, bottomY + 44, 0xEE080D14);
        guiGraphics.fill(rightX - 6, bottomY - 14, rightX + barW + 6, bottomY - 13, 0xAAFF9100);

        // Thruster Dash Meter
        float dash = mech.getDashCharge();
        float dashPct = Math.max(0.0F, Math.min(1.0F, dash / 100.0F));

        guiGraphics.drawString(mc.font, "◆ DASH BOOST", rightX, bottomY - 10, 0xFFFFAB00, false);
        String dashStatus = dash >= 40.0F ? (dash >= 80.0F ? "READY x2" : "READY x1") : "RECHARGING";
        int dashStatusW = mc.font.width(dashStatus);
        int dashStatusColor = dash >= 40.0F ? 0xFF00E676 : 0xFFFF5722;
        guiGraphics.drawString(mc.font, dashStatus, rightX + barW - dashStatusW, bottomY - 10, dashStatusColor, false);

        // Segmented Dash Boost Cells (2 Fuel Cells)
        guiGraphics.fill(rightX, bottomY + 2, rightX + barW, bottomY + 9, 0x55301800);
        int dashFill = (int) (barW * dashPct);
        if (dashFill > 0) {
            guiGraphics.fill(rightX, bottomY + 2, rightX + dashFill, bottomY + 9, 0xFFFF9100);
        }
        guiGraphics.fill(rightX + (barW / 2) - 1, bottomY + 1, rightX + (barW / 2) + 1, bottomY + 10, 0xFF080D14);

        // Weapon Systems & Munitions
        String weaponName = (titanClass != null && titanClass.ordinal() < TITAN_WEAPONS.length)
                ? TITAN_WEAPONS[titanClass.ordinal()] : "PLASMA BLASTER";
        guiGraphics.drawString(mc.font, "◆ " + weaponName, rightX, bottomY + 13, 0xFFFFFFFF, false);

        int ammoCount = countAmmo(player, mech);
        boolean isOverdrive = mech.isOverdriveActive();
        String ammoText = isOverdrive ? "⚡ OVERDRIVE BARRAGE: INF ⚡" : ((ammoCount >= 999) ? "AMMO: INF" : "AMMO: " + ammoCount + " RDS");
        int ammoColor = isOverdrive ? 0xFFFFD700 : ((ammoCount > 10) ? 0xFF00E5FF : (ammoCount > 0 ? 0xFFFFB300 : 0xFFFF1744));
        guiGraphics.drawString(mc.font, ammoText, rightX, bottomY + 23, ammoColor, false);

        String fireKey = KeyInputHandler.KEY_FIRE.getKey().getDisplayName().getString();
        guiGraphics.drawString(mc.font, "◆ TRIGGER: [L-CLICK / " + fireKey + "]", rightX, bottomY + 32, 0x88AAAAAA, false);

        // ==========================================
        // 6. CENTER TITAN CORE OVERDRIVE SYSTEM
        // ==========================================
        int coreBarW = 160;
        int coreX = centerX - (coreBarW / 2);
        int coreY = screenHeight - 48;

        float coreCharge = mech.getCoreCharge();
        int odTicks = mech.getOverdriveTicks();
        String coreKey = KeyInputHandler.KEY_CORE.getKey().getDisplayName().getString();

        if (odTicks > 0) {
            boolean flash = (player.tickCount % 4 < 2);
            int odColor = flash ? 0xFFFFD700 : 0xFFFFAB00;
            String odText = String.format("◆ TITAN CORE OVERDRIVE: %04.1fs ◆", odTicks / 20.0F);
            int odW = mc.font.width(odText);

            guiGraphics.fill(centerX - (odW / 2) - 8, coreY - 4, centerX + (odW / 2) + 8, coreY + 14, 0xEE080D14);
            guiGraphics.fill(centerX - (odW / 2) - 8, coreY - 4, centerX + (odW / 2) + 8, coreY - 3, odColor);
            guiGraphics.drawString(mc.font, odText, centerX - (odW / 2), coreY, odColor, true);
        } else if (coreCharge >= 100.0F) {
            boolean flash = (player.tickCount % 10 < 5);
            int readyColor = flash ? 0xFF00E5FF : 0xFFFFD700;
            String readyText = "◆ CORE OVERDRIVE READY [" + coreKey + "] ◆";
            int readyW = mc.font.width(readyText);

            guiGraphics.fill(centerX - (readyW / 2) - 8, coreY - 4, centerX + (readyW / 2) + 8, coreY + 14, 0xEE080D14);
            guiGraphics.fill(centerX - (readyW / 2) - 8, coreY - 4, centerX + (readyW / 2) + 8, coreY - 3, readyColor);
            guiGraphics.drawString(mc.font, readyText, centerX - (readyW / 2), coreY, readyColor, true);
        } else {
            guiGraphics.fill(coreX - 4, coreY - 2, coreX + coreBarW + 4, coreY + 12, 0x99080D14);
            guiGraphics.fill(coreX, coreY + 4, coreX + coreBarW, coreY + 8, 0x44203040);

            int fillW = (int) (coreBarW * (coreCharge / 100.0F));
            if (fillW > 0) {
                guiGraphics.fill(coreX, coreY + 4, coreX + fillW, coreY + 8, 0xFF00B0FF);
            }
            String chargeText = "CORE REACTOR: " + (int) coreCharge + "%";
            int ctW = mc.font.width(chargeText);
            guiGraphics.drawString(mc.font, chargeText, centerX - (ctW / 2), coreY - 2, 0xAA80D8FF, true);
        }

        // ==========================================
        // 7. EMERGENCY WARNING & CONTROLS FOOTER
        // ==========================================
        boolean isDoomed = mech.getMechState() == MechState.DOOMED || health <= (maxHealth * 0.2F);
        if (isDoomed) {
            boolean flash = (mc.level != null && (mc.level.getGameTime() % 10 < 5));
            int warnColor = flash ? 0xFFFF1744 : 0x88FF1744;
            Component warnText = Component.literal("⚠ WARNING: CRITICAL DAMAGE - DOOMED STATE ⚠");
            Component ejectPrompt = Component.literal("PRESS [" + KeyInputHandler.KEY_EJECT.getKey().getDisplayName().getString() + "] TO EMERGENCY EJECT");

            int w1 = mc.font.width(warnText);
            int w2 = mc.font.width(ejectPrompt);
            guiGraphics.drawString(mc.font, warnText, centerX - (w1 / 2), centerY - 40, warnColor, true);
            guiGraphics.drawString(mc.font, ejectPrompt, centerX - (w2 / 2), centerY - 28, 0xFFFFFFFF, true);
        }

        // Sleek Controls Legend & Kneel/Park Status
        String ejectKey = KeyInputHandler.KEY_EJECT.getKey().getDisplayName().getString();
        String meleeKey = KeyInputHandler.KEY_MELEE.getKey().getDisplayName().getString();
        String kneelKey = KeyInputHandler.KEY_KNEEL.getKey().getDisplayName().getString();

        if (mech instanceof BaseTitanEntity titan && titan.isSitting()) {
            Component parkBanner = Component.literal("◆ TITAN PARKED / SAFE TO DISEMBARK [SHIFT] ◆");
            int parkW = mc.font.width(parkBanner);
            guiGraphics.fill(centerX - (parkW / 2) - 8, screenHeight - 30, centerX + (parkW / 2) + 8, screenHeight - 18, 0xDD081810);
            guiGraphics.fill(centerX - (parkW / 2) - 8, screenHeight - 30, centerX + (parkW / 2) + 8, screenHeight - 29, 0xFF00E676);
            guiGraphics.drawString(mc.font, parkBanner, centerX - (parkW / 2), screenHeight - 27, 0xFF00E676, true);

            Component legend = Component.literal("[" + kneelKey + "] STAND  [SHIFT] DISEMBARK  [E] BAY  [" + ejectKey + "] EJECT");
            int legendW = mc.font.width(legend);
            guiGraphics.drawString(mc.font, legend, centerX - (legendW / 2), screenHeight - 14, 0xFFB9F6CA, true);
        } else {
            Component legend = Component.literal("[SPACE] Dash  [L-CLICK] Fire  [" + meleeKey + "] Melee  [" + defKey + "] Matrix  [" + coreKey + "] Core  [" + kneelKey + "] Kneel  [E] Bay  [" + ejectKey + "] Eject");
            int legendW = mc.font.width(legend);
            guiGraphics.drawString(mc.font, legend, centerX - (legendW / 2), screenHeight - 14, 0x88AAAAAA, true);
        }

        RenderSystem.disableBlend();
    };

    private static String getCardinal(int yaw) {
        int idx = ((yaw + 22) / 45) % 8;
        return CARDINALS[idx];
    }

    private static int countAmmo(Player player, BaseMechEntity mech) {
        if (player.getAbilities().instabuild) return 999;
        if (player.tickCount - lastAmmoCheckTick >= 10 || lastAmmoCheckTick == -1) {
            lastAmmoCheckTick = player.tickCount;
            int count = 0;
            if (mech instanceof BaseTitanEntity titan) {
                for (int i = 0; i < titan.getTitanInventory().getContainerSize(); i++) {
                    ItemStack stack = titan.getTitanInventory().getItem(i);
                    if (stack.getItem() instanceof TitanAmmoItem) {
                        count += stack.getCount();
                    }
                }
            }
            for (int i = 0; i < player.getInventory().getContainerSize(); i++) {
                ItemStack stack = player.getInventory().getItem(i);
                if (stack.getItem() instanceof TitanAmmoItem) {
                    count += stack.getCount();
                }
            }
            cachedAmmoCount = count;
        }
        return cachedAmmoCount;
    }
}
