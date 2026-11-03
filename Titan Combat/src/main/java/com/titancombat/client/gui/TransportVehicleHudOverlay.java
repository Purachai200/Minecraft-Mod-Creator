package com.titancombat.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import com.titancombat.entity.transport.TitanCargoBargeEntity;
import com.titancombat.entity.transport.TitanHaulerTruckEntity;
import com.titancombat.entity.transport.TitanSkyCraneDroneEntity;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

import java.util.ArrayList;
import java.util.List;

import static com.titancombat.client.gui.HudDraw.*;

/**
 * Military Tactical Holographic Cockpit HUD for Transport Vehicles:
 * Matches Titan Combat's Titanfall-style cockpit visual language with holographic brackets,
 * heading compass tape, dynamic slanted telemetry bars, and first-person tactical steering reticle.
 */
public class TransportVehicleHudOverlay {

    // Palette (matching MechCockpitHudOverlay)
    private static final int CYAN = 0x00E5FF;
    private static final int ICE = 0xD8FBFF;
    private static final int WHITE = 0xFFFFFF;
    private static final int DIM = 0x7FB8C8;
    private static final int AMBER = 0xFFB300;
    private static final int RED = 0xFF2A44;
    private static final int GREEN = 0x00E676;

    private static final String[] CARDINALS = {"S", "SW", "W", "NW", "N", "NE", "E", "SE"};

    public static final IGuiOverlay HUD_TRANSPORT = (gui, guiGraphics, partialTick, width, height) -> {
        render(guiGraphics, width, height);
    };

    public static void render(GuiGraphics g, int W, int H) {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || !(player.getVehicle() instanceof BaseTransportVehicleEntity vehicle)) {
            return;
        }

        Font font = mc.font;
        boolean firstPerson = mc.options.getCameraType() == CameraType.FIRST_PERSON;
        float now = player.tickCount + mc.getFrameTime();

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        alpha = 1.0F;

        // ---------------------------------------------------------------------
        // 1. Telemetry Calculations
        // ---------------------------------------------------------------------
        double hSpeedBps = vehicle.getDeltaMovement().horizontalDistance() * 20.0D;
        double speedKmh = hSpeedBps * 3.6D;
        double alt = vehicle.getY();
        double verticalMps = vehicle.getDeltaMovement().y * 20.0D;

        // Energy FE Telemetry
        int energy = vehicle.getEnergy();
        int maxEnergy = vehicle.getMaxEnergy();
        float energyRatio = clamp01((float) energy / (float) Math.max(1, maxEnergy));
        int energyPct = Math.round(energyRatio * 100.0F);

        // Structural Integrity
        float health = vehicle.getHealth();
        float maxHealth = vehicle.getMaxHealth();
        float hpRatio = clamp01(health / Math.max(1.0F, maxHealth));
        int hpPct = Math.round(hpRatio * 100.0F);

        // Docked Mechs Inspection
        List<String> dockedTitanNames = new ArrayList<>();
        for (Entity p : vehicle.getPassengers()) {
            if (p instanceof BaseTitanEntity titan) {
                dockedTitanNames.add(titan.getTitanClass().getDisplayName().toUpperCase() + " TITAN");
            } else if (p instanceof BaseMechEntity mech) {
                dockedTitanNames.add(mech.getName().getString().toUpperCase());
            }
        }

        int cx = W / 2;
        int cy = H / 2;
        float heading = (vehicle.getYRot() % 360.0F + 360.0F) % 360.0F;

        // ---------------------------------------------------------------------
        // 2. Top-Center Holographic Heading Tape
        // ---------------------------------------------------------------------
        drawCompass(g, font, cx, vehicle, heading);

        // ---------------------------------------------------------------------
        // 3. Center Tactical Steering Reticle (First-Person Only)
        // ---------------------------------------------------------------------
        if (firstPerson) {
            drawTacticalReticle(g, cx, cy, vehicle, player);
        }

        // ---------------------------------------------------------------------
        // 4. Bottom-Left Console: Chassis Hull & Payload Bay Status
        // ---------------------------------------------------------------------
        int x0 = 16;
        int base = H - 16;
        drawPayloadConsole(g, font, x0, base, vehicle, dockedTitanNames, hpRatio, hpPct);

        // ---------------------------------------------------------------------
        // 5. Bottom-Right Console: Velocity Speedometer & FE Power Core
        // ---------------------------------------------------------------------
        int xr = W - 16;
        drawPropulsionConsole(g, font, xr, base, vehicle, speedKmh, hSpeedBps, alt, verticalMps, energy, energyRatio, energyPct);

        // ---------------------------------------------------------------------
        // 6. Caution / Low Energy Warning Banner
        // ---------------------------------------------------------------------
        if (energyPct < 20) {
            float blink = 0.5F + 0.5F * Mth.sin(now * 0.45F);
            textCenter(g, font, "⚠ CAUTION: REACTOR ENERGY DEPLETED (< 20%) ⚠", cx, cy + 28, RED, blink, true);
        }

        RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
        RenderSystem.disableBlend();
    }

    // =========================================================================
    // TOP NAVIGATION & COMPASS TAPE
    // =========================================================================
    private static void drawCompass(GuiGraphics g, Font font, int cx, BaseTransportVehicleEntity vehicle, float heading) {
        String title;
        String role;
        if (vehicle instanceof TitanSkyCraneDroneEntity) {
            title = "SKY-CRANE VTOL DRONE";
            role = "HOT-DROP AIRLIFT";
        } else if (vehicle instanceof TitanCargoBargeEntity) {
            title = "AMPHIBIOUS CARGO BARGE";
            role = "SHORE ASSAULT";
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanOceanCarrierEntity) {
            title = "SUPER-CARRIER BARGE";
            role = "OCEANIC LOGISTICS";
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanTacticalTruckEntity) {
            title = "TACTICAL TECHNICAL 4x4";
            role = "RAPID RESPONSE";
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanChinookTransporterEntity) {
            title = "CH-47 CHINOOK";
            role = "HEAVY TANDEM AIRLIFT";
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanV22OspreyEntity) {
            title = "V-22 OSPREY TILTROTOR";
            role = "VTOL TROOP & AIRLIFT";
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanArmoredApcEntity) {
            title = "ARMORED 8x8 COMBAT APC";
            role = "AMPHIBIOUS IFV";
        } else if (vehicle instanceof com.titancombat.entity.transport.TitanMobileSuitTrailerEntity) {
            title = "MOBILE SUIT HEAVY TRANSPORTER";
            role = "STRATEGIC LAUNCH CRADLE";
        } else {
            title = "8x8 HEAVY HAULER TRUCK";
            role = "OVERLAND LOGISTICS";
        }

        // Vehicle Designation Sub-Header
        textCenter(g, font, title + "  //  " + role, cx, 5, ICE, 0.85F, true);

        // Compass Tape
        final int tapeW = 140;
        final float ppd = 1.2F;
        final int tapeY = 17;

        rect(g, cx - tapeW / 2, tapeY, cx + tapeW / 2, tapeY + 1, CYAN, 0.28F);
        textCenter(g, font, "▼", cx, tapeY - 4, CYAN, 0.95F, false);

        int startDeg = Mth.floor((heading - 45.0F) / 5.0F) * 5;
        for (int d = startDeg; d <= heading + 45.0F; d += 5) {
            float dx = (d - heading) * ppd;
            if (Math.abs(dx) > (tapeW / 2.0F - 4.0F)) continue;

            int normD = (d % 360 + 360) % 360;
            int px = (int) (cx + dx);

            if (normD % 45 == 0) {
                String card = CARDINALS[normD / 45];
                rect(g, px, tapeY, px + 1, tapeY + 4, CYAN, 0.85F);
                textCenter(g, font, card, px, tapeY + 6, CYAN, 0.95F, true);
            } else if (normD % 15 == 0) {
                rect(g, px, tapeY, px + 1, tapeY + 3, ICE, 0.55F);
            } else {
                rect(g, px, tapeY, px + 1, tapeY + 2, DIM, 0.35F);
            }
        }
    }

    // =========================================================================
    // CENTER TACTICAL RETICLE (FIRST-PERSON VIEW)
    // =========================================================================
    private static void drawTacticalReticle(GuiGraphics g, int cx, int cy, BaseTransportVehicleEntity vehicle, Player player) {
        // Center Target Dot
        rect(g, cx - 1, cy - 1, cx + 2, cy + 2, ICE, 0.85F);

        // Slanted Holographic Brackets
        slant(g, cx - 20, cy - 6, 2, 12, 0.2F, CYAN, 0.65F);
        slant(g, cx + 18, cy - 6, 2, 12, -0.2F, CYAN, 0.65F);

        // Dynamic Steering Deflection Pip
        float strafe = player.xxa;
        float steerX = cx - strafe * 12.0F;
        rect(g, (int) steerX - 2, cy + 10, (int) steerX + 3, cy + 12, GREEN, 0.85F);
        rect(g, cx, cy + 8, cx + 1, cy + 14, DIM, 0.30F); // zero reference mark

        // Drone: Attitude Reference Ladder Ticks
        if (vehicle instanceof TitanSkyCraneDroneEntity) {
            rect(g, cx - 36, cy - 12, cx - 24, cy - 11, CYAN, 0.35F);
            rect(g, cx + 25, cy - 12, cx + 37, cy - 11, CYAN, 0.35F);
            rect(g, cx - 36, cy + 12, cx - 24, cy + 13, CYAN, 0.35F);
            rect(g, cx + 25, cy + 12, cx + 37, cy + 13, CYAN, 0.35F);
        }
    }

    // =========================================================================
    // BOTTOM-LEFT CONSOLE: HULL & PAYLOAD BAYS
    // =========================================================================
    private static void drawPayloadConsole(GuiGraphics g, Font font, int x0, int base, BaseTransportVehicleEntity vehicle,
                                           List<String> dockedTitans, float hpRatio, int hpPct) {
        // Holographic Outer Bracket
        rect(g, x0 - 6, base - 50, x0 - 5, base + 2, CYAN, 0.35F);
        rect(g, x0 - 6, base + 2, x0 + 18, base + 3, CYAN, 0.35F);
        rect(g, x0 - 6, base - 50, x0 - 2, base - 49, CYAN, 0.35F);

        // Header Title
        text(g, font, "PAYLOAD // HULL", x0, base - 52, CYAN, 0.70F, false);

        // Hull Slanted Segmented Bar
        final int segs = 10;
        final float segW = 8.5F;
        int hpColor = hpRatio > 0.5F ? GREEN : (hpRatio > 0.25F ? AMBER : RED);
        for (int i = 0; i < segs; i++) {
            float sx = x0 + i * (segW + 1.5F);
            float fill = clamp01((hpRatio - (float) i / segs) * segs);
            slant(g, sx, base - 42, segW, 5, 0.5F, CYAN, 0.14F);
            if (fill > 0) slant(g, sx, base - 42, segW * fill, 5, 0.5F, hpColor, 0.90F);
        }
        text(g, font, hpPct + "%", x0 + 104, base - 43, hpColor, 0.95F, true);
        float prop = vehicle.getPropulsionDamage();
        if (prop > 0.0F) {
            String part = vehicle.isAircraft() ? "ROTORS" : "RUNNING GEAR";
            text(g, font, prop >= 1.0F ? part + ": DESTROYED" : part + ": " + Math.round(prop * 100) + "% DMG", x0, base - 61, prop > 0.5F ? RED : AMBER, 0.70F, true);
        }

        // Payload Bay Status
        if (vehicle instanceof TitanCargoBargeEntity) {
            String b1 = dockedTitans.size() > 0 ? "B1: " + dockedTitans.get(0) : "B1: EMPTY";
            int c1 = dockedTitans.size() > 0 ? GREEN : DIM;
            text(g, font, b1, x0, base - 30, c1, 0.90F, true);

            String b2 = dockedTitans.size() > 1 ? "B2: " + dockedTitans.get(1) : "B2: EMPTY";
            int c2 = dockedTitans.size() > 1 ? GREEN : DIM;
            text(g, font, b2, x0, base - 19, c2, 0.90F, true);
        } else if (vehicle instanceof TitanSkyCraneDroneEntity) {
            boolean loaded = !dockedTitans.isEmpty();
            String st = loaded ? "HOIST: " + dockedTitans.get(0) : "HOIST: EMPTY [STOWED]";
            int c = loaded ? GREEN : DIM;
            text(g, font, st, x0, base - 30, c, 0.95F, true);
            text(g, font, loaded ? "READY FOR COMBAT HOT-DROP" : "HOVER OVER MECH TO SLING", x0, base - 19, ICE, 0.75F, false);
        } else {
            boolean loaded = !dockedTitans.isEmpty();
            String st = loaded ? "BED: " + dockedTitans.get(0) : "BED: EMPTY [READY]";
            int c = loaded ? GREEN : DIM;
            text(g, font, st, x0, base - 30, c, 0.95F, true);
            text(g, font, loaded ? "4x TIE-DOWN STRAPS SECURED" : "DRIVE NEAR TITAN TO DOCK", x0, base - 19, ICE, 0.75F, false);
        }

        // Sub-hint
        text(g, font, "[" + com.titancombat.client.KeyInputHandler.KEY_RELEASE_CARGO.getTranslatedKeyMessage().getString().toUpperCase()
                + "] Release", x0, base - 7, DIM, 0.65F, false);
    }

    // =========================================================================
    // BOTTOM-RIGHT CONSOLE: PROPULSION & ENERGY CORE
    // =========================================================================
    private static void drawPropulsionConsole(GuiGraphics g, Font font, int xr, int base, BaseTransportVehicleEntity vehicle,
                                              double speedKmh, double hSpeedBps, double alt, double verticalMps,
                                              int energy, float energyRatio, int energyPct) {
        // Holographic Outer Bracket
        rect(g, xr + 5, base - 50, xr + 6, base + 2, CYAN, 0.35F);
        rect(g, xr - 18, base + 2, xr + 6, base + 3, CYAN, 0.35F);
        rect(g, xr + 2, base - 50, xr + 6, base - 49, CYAN, 0.35F);

        // Header Title
        textRight(g, font, "PROPULSION // FE CORE", xr, base - 53, CYAN, 0.70F, false);

        // Digital Speedometer Readout (Placed cleanly beneath header with zero overlap)
        String spdNum = String.format("%04.1f", speedKmh);
        int numW = Math.round(font.width(spdNum) * 1.4F);
        int numX = xr - numW - 28;
        textScaled(g, font, spdNum, numX, base - 43, 1.4F, 1.0F, WHITE, 0.95F, true);
        text(g, font, "KM/H", xr - 24, base - 43, CYAN, 0.80F, true);
        text(g, font, String.format("%.1f m/s", hSpeedBps), xr - 24, base - 34, DIM, 0.65F, false);

        // Slanted Velocity Bar (10 segments)
        final int segs = 10;
        final float segW = 7.5F;
        float maxSpeedKmh = vehicle instanceof TitanSkyCraneDroneEntity ? 83.0F : vehicle instanceof TitanCargoBargeEntity ? 86.0F : 58.0F;
        float spdRatio = clamp01((float) speedKmh / maxSpeedKmh);
        int spdColor = spdRatio > 0.85F ? AMBER : CYAN;
        for (int i = 0; i < segs; i++) {
            float sx = (xr - 95) + i * (segW + 1.5F);
            float fill = clamp01((spdRatio - (float) i / segs) * segs);
            slant(g, sx, base - 25, segW, 4, 0.5F, CYAN, 0.14F);
            if (fill > 0) slant(g, sx, base - 25, segW * fill, 4, 0.5F, spdColor, 0.85F);
        }

        // Altitude & VSI / Terrain
        String altStr = String.format("ALT: %.1f m", alt);
        if (vehicle instanceof TitanSkyCraneDroneEntity) {
            String arr = verticalMps > 0.2D ? "▲" : (verticalMps < -0.2D ? "▼" : "━");
            altStr += String.format("  VSI: %+.1f %s", verticalMps, arr);
        }
        textRight(g, font, altStr, xr, base - 19, ICE, 0.85F, false);

        // FE Energy Power Core Bar (10 segments)
        int energyColor = energyRatio > 0.5F ? GREEN : (energyRatio > 0.2F ? AMBER : RED);
        for (int i = 0; i < segs; i++) {
            float sx = (xr - 95) + i * (segW + 1.5F);
            float fill = clamp01((energyRatio - (float) i / segs) * segs);
            slant(g, sx, base - 10, segW, 5, 0.5F, CYAN, 0.14F);
            if (fill > 0) slant(g, sx, base - 10, segW * fill, 5, 0.5F, energyColor, 0.90F);
        }
        textRight(g, font, "PWR: " + energyPct + "%", xr, base - 11, energyColor, 0.95F, true);

        // Control Hint
        String hint = vehicle instanceof TitanSkyCraneDroneEntity
                ? "[SPACE] Climb  [" + com.titancombat.client.KeyInputHandler.KEY_DESCEND.getTranslatedKeyMessage().getString().toUpperCase()
                        + "] Descend  [L-CLICK] Drop"
                : "[W/A/S/D] Steer";
        textRight(g, font, hint, xr, base - 2, DIM, 0.65F, false);
    }
}
