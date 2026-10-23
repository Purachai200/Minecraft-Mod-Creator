package com.youjosenki.flight.client.gui;

import com.youjosenki.flight.client.model.FlightUnitModel;
import com.youjosenki.flight.client.telemetry.ClientFlightTelemetry;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.energy.IEnergyStorage;

public class FlightHudOverlay implements IGuiOverlay {
    public static final FlightHudOverlay HUD_OVERLAY = new FlightHudOverlay();

    @Override
    public void render(ForgeGui gui, GuiGraphics guiGraphics, float partialTick, int screenWidth, int screenHeight) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer player = mc.player;
        if (player == null || mc.options.hideGui) return;

        ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
        if (unit == null || !(unit.getItem() instanceof EleniumFlightUnitItem item)) return;

        // Only display when player has an energized flight unit equipped
        if (!EleniumFlightUnitItem.isItemEnergized(unit)) return;

        Font font = mc.font;
        int currentY = (int) player.getY();
        int ceiling = item.getServiceCeiling();
        double speedKmh = player.getDeltaMovement().length() * 20.0 * 3.6; // blocks/tick -> km/h
        // Transonic speed of sound calibration (~105 km/h = Mach 1.0, capped at Mach 1.05 max)
        double mach = Math.min(1.05, speedKmh / 105.0);

        // Environmental status indicators
        boolean inWater = player.isInWater();
        boolean inRain = player.level().isRainingAt(player.blockPosition());
        boolean isFlooded = inWater && !item.isWaterproof();

        float heat = ClientFlightTelemetry.heat;
        boolean overheated = ClientFlightTelemetry.overheated;

        // Energy capability extraction
        IEnergyStorage energy = unit.getCapability(ForgeCapabilities.ENERGY).orElse(null);
        int storedEnergy = energy != null ? energy.getEnergyStored() : 0;
        int maxEnergy = energy != null ? energy.getMaxEnergyStored() : item.getMaxEnergyCapacity();
        double energyPercent = maxEnergy > 0 ? ((double) storedEnergy / maxEnergy) * 100.0 : 0.0;

        // Professional Systematic Avionics Panel dimensions (264 x 38 px)
        // Sits cleanly above actionbar/hotbar without blocking gun aiming crosshair
        int panelW = 264;
        int panelH = 38;
        int panelX = screenWidth / 2 - panelW / 2;
        int panelY = screenHeight - 108;

        // Dispatch based on Avionics Generation
        switch (item.getHudGeneration()) {
            case VINTAGE_ANALOG -> renderVintageAnalogHud(guiGraphics, font, player, item, panelX, panelY, panelW, panelH, speedKmh, mach, currentY, ceiling, heat, overheated, inWater, inRain, isFlooded, storedEnergy, maxEnergy, energyPercent);
            case MILITARY_STANDARD -> renderMilitaryStandardHud(guiGraphics, font, player, item, panelX, panelY, panelW, panelH, speedKmh, mach, currentY, ceiling, heat, overheated, inWater, inRain, isFlooded, storedEnergy, maxEnergy, energyPercent);
            case ADVANCED_DIGITAL -> renderAdvancedDigitalHud(guiGraphics, font, player, item, panelX, panelY, panelW, panelH, speedKmh, mach, currentY, ceiling, heat, overheated, inWater, inRain, isFlooded, storedEnergy, maxEnergy, energyPercent);
        }
    }

    private static String getModelChip(FlightUnitModel.FlightDesign design) {
        return switch (design) {
            case MAGE_UNIT -> "MAGE-RIG";
            case BACK_JETPACK -> "JETPACK-MK1";
            case TACTICAL_WINGS -> "DELTA-WING";
            case HEAVY_ROCKET -> "TITAN-HEAVY";
            case TWIN_DRIVE_EXO -> "TYP-95-EXO";
            case SIEGE_ARTILLERY -> "JUGGERNAUT";
            case THRUST_BOOTS -> "VALKYRIE-BOOTS";
            case HYDRO_SKIMMER -> "HYDRO-SKIM";
            case TACTICAL_SCUBA -> "SCUBA-RIG";
            case URBAN_EXO_LEGS -> "URBAN-EXO";
            case DIVING_MASK -> "SCUBA-MASK";
        };
    }

    // =========================================================================
    // GENERATION 1: VINTAGE MECHANICAL AVIONICS (WW1 / Imperial Aerial Mage)
    // Dark walnut slate, brushed brass frame, copper needles, steam manometer,
    // barometric mercury tube, incandescent filament power bar.
    // =========================================================================
    private void renderVintageAnalogHud(GuiGraphics guiGraphics, Font font, LocalPlayer player, EleniumFlightUnitItem item,
                                        int panelX, int panelY, int panelW, int panelH,
                                        double speedKmh, double mach, int currentY, int ceiling,
                                        float heat, boolean overheated, boolean inWater, boolean inRain, boolean isFlooded,
                                        int storedEnergy, int maxEnergy, double energyPercent) {
        // 1. Dark oiled walnut slate background
        int bgColor = isFlooded ? 0xDD2A0A06 : (overheated ? 0xDD350E06 : 0xDC1A130D);
        guiGraphics.fill(panelX, panelY, panelX + panelW, panelY + panelH, bgColor);

        // Brushed bronze & brass double border
        int frameBorder = isFlooded ? 0xFFFF3333 : (overheated ? 0xFFFF5722 : 0xFF8D6E63);
        guiGraphics.hLine(panelX, panelX + panelW - 1, panelY, frameBorder);
        guiGraphics.hLine(panelX, panelX + panelW - 1, panelY + panelH - 1, frameBorder);
        guiGraphics.vLine(panelX, panelY, panelY + panelH - 1, frameBorder);
        guiGraphics.vLine(panelX + panelW - 1, panelY, panelY + panelH - 1, frameBorder);

        // Mechanical brass corner rivets
        drawRivet(guiGraphics, panelX + 3, panelY + 3);
        drawRivet(guiGraphics, panelX + panelW - 4, panelY + 3);
        drawRivet(guiGraphics, panelX + 3, panelY + panelH - 4);
        drawRivet(guiGraphics, panelX + panelW - 4, panelY + panelH - 4);

        // Cast-iron section ribs
        int ribColor = 0x608D6E63;
        guiGraphics.vLine(panelX + 88, panelY + 11, panelY + 25, ribColor);
        guiGraphics.vLine(panelX + 176, panelY + 11, panelY + 25, ribColor);

        // --- ROW 1: HEADER TELEMETRY ---
        // Left: Model Tag Chip
        String modelTag = "[" + getModelChip(item.getFlightDesign()) + "]";
        guiGraphics.drawString(font, modelTag, panelX + 8, panelY + 2, 0xFFFFB74D, false);

        // Center: System Annunciator
        String statusMsg;
        int statusColor;
        boolean strained = currentY >= ceiling && player.getAbilities().flying && !player.onGround();
        if (isFlooded) {
            statusMsg = "⚠ BOILER FLOODED ⚠";
            statusColor = 0xFFFF5252;
        } else if (overheated) {
            statusMsg = "⚠ BOILER BLOWOUT ⚠";
            statusColor = 0xFFFF3D00;
        } else if (strained) {
            statusMsg = "▲ ALT STRAIN ▲";
            statusColor = 0xFFFFAB00;
        } else if (ClientFlightTelemetry.boostStep == 3) {
            statusMsg = "⚡ MAX SURGE ⚡";
            statusColor = 0xFFFFE082;
        } else if (ClientFlightTelemetry.boostStep == 2) {
            statusMsg = "⚡ STEAM BURST ⚡";
            statusColor = 0xFFFFB74D;
        } else if (player.isSprinting() && player.getAbilities().flying) {
            statusMsg = "▶ HIGH CRUISE ◀";
            statusColor = 0xFFFFB74D;
        } else if (player.getAbilities().flying) {
            statusMsg = "◆ LEVEL FLIGHT ◆";
            statusColor = 0xFFBCAAA4;
        } else {
            statusMsg = "✦ IDLE PROPULSION ✦";
            statusColor = 0xFF8D6E63;
        }
        int statusW = font.width(statusMsg);
        guiGraphics.drawString(font, statusMsg, panelX + panelW / 2 - statusW / 2, panelY + 2, statusColor, false);

        // Right: Certification Chip
        String certTag = item.isWaterproof() ? "[SEALED]" : (inRain ? "[RAIN -15%]" : "[OPEN-AIR]");
        int certColor = item.isWaterproof() ? 0xFF80DEEA : (inRain ? 0xFFFFCC80 : 0xFFB0BEC5);
        int certW = font.width(certTag);
        guiGraphics.drawString(font, certTag, panelX + panelW - 8 - certW, panelY + 2, certColor, false);

        // --- ROW 2: MAIN INSTRUMENTS ---
        // Bay 1: Mechanical Speed & Mach Indicator (80px width)
        int spdX1 = panelX + 7;
        int spdX2 = panelX + 85;
        int spdY = panelY + 20;
        int spdW = spdX2 - spdX1;
        String spdStr = (int) speedKmh + " KPH";
        String machStr = String.format("M%.2f", mach);
        guiGraphics.drawString(font, spdStr, spdX1 + 1, panelY + 11, 0xFFFFB74D, false);
        guiGraphics.drawString(font, machStr, spdX2 - font.width(machStr) - 1, panelY + 11, mach >= 0.90 ? 0xFFFF7043 : 0xFFFFE082, false);

        // Speed Track & Ticks
        guiGraphics.fill(spdX1, spdY, spdX2, spdY + 4, 0xFF140D07);
        guiGraphics.fill(spdX1 + 20, spdY - 1, spdX1 + 21, spdY + 5, 0xFF5D4037);
        guiGraphics.fill(spdX1 + 40, spdY - 1, spdX1 + 41, spdY + 5, 0xFF5D4037);
        guiGraphics.fill(spdX1 + 60, spdY - 1, spdX1 + 61, spdY + 5, 0xFF5D4037);
        guiGraphics.fill(spdX1 + 72, spdY - 1, spdX1 + 73, spdY + 5, 0xFFB71C1C); // Sound barrier threshold mark

        int spdFill = (int) (Math.min(1.0, speedKmh / 105.0) * spdW);
        if (spdFill > 0) {
            int copper = mach >= 0.90 ? 0xFFFF7043 : (mach >= 0.70 ? 0xFFFFB74D : 0xFFD87D2A);
            guiGraphics.fill(spdX1, spdY + 1, spdX1 + spdFill, spdY + 3, copper);
        }
        int curX = spdX1 + spdFill;
        guiGraphics.fill(curX - 1, spdY - 1, curX + 1, spdY + 5, 0xFFFFE082);

        // Bay 2: Boiler Manometer & Pressure Chamber (84px width)
        int bay2X1 = panelX + 91;
        int bay2X2 = panelX + 173;
        int bay2W = bay2X2 - bay2X1;
        String boilerTitle = overheated ? "BLOWOUT" : (heat >= 75 ? "PRESS CRIT" : "BOILER " + (int) heat + "%");
        int bTitleColor = overheated ? 0xFFFF1744 : (heat >= 75 ? 0xFFFF5722 : (heat >= 50 ? 0xFFFFB74D : 0xFF81C784));
        int bTitleW = font.width(boilerTitle);
        guiGraphics.drawString(font, boilerTitle, bay2X1 + (bay2W - bTitleW) / 2, panelY + 11, bTitleColor, false);

        // Manometer Pressure Mercury Tube
        int heatY = panelY + 20;
        guiGraphics.fill(bay2X1, heatY, bay2X2, heatY + 4, 0xFF140D07);
        // Safety zone colors behind glass tube
        guiGraphics.fill(bay2X1, heatY, bay2X1 + 30, heatY + 4, 0x3033691E);
        guiGraphics.fill(bay2X1 + 30, heatY, bay2X1 + 55, heatY + 4, 0x30F57F17);
        guiGraphics.fill(bay2X1 + 55, heatY, bay2X2, heatY + 4, 0x40B71C1C);

        int heatFill = (int) (Math.min(1.0, Math.max(0.0, heat / 100.0)) * bay2W);
        if (overheated && (player.tickCount / 3) % 2 == 0) {
            guiGraphics.fill(bay2X1, heatY + 1, bay2X2, heatY + 3, 0xFFFF1744);
        } else if (heatFill > 0) {
            int merc = heat >= 75 ? 0xFFFF3D00 : (heat >= 50 ? 0xFFFF9800 : 0xFFFFD54F);
            guiGraphics.fill(bay2X1, heatY + 1, bay2X1 + heatFill, heatY + 3, merc);
        }
        int heatCurX = bay2X1 + heatFill;
        guiGraphics.fill(heatCurX - 1, heatY - 1, heatCurX + 1, heatY + 5, 0xFFFFE082);

        // Bay 3: Barometric Altimeter (80px width)
        int altX1 = panelX + 179;
        int altX2 = panelX + 257;
        int altW = altX2 - altX1;
        String altStr = "ALT " + currentY + "m";
        String ceilStr = "/" + ceiling + "m";
        guiGraphics.drawString(font, altStr, altX1 + 1, panelY + 11, strained ? 0xFFFF7043 : 0xFFFFB74D, false);
        guiGraphics.drawString(font, ceilStr, altX2 - font.width(ceilStr) - 1, panelY + 11, 0xFFBCAAA4, false);

        int altY = panelY + 20;
        guiGraphics.fill(altX1, altY, altX2, altY + 4, 0xFF140D07);
        // Ceiling hazard block in rightmost 6px
        guiGraphics.fill(altX2 - 6, altY, altX2, altY + 4, 0x60C62828);
        guiGraphics.fill(altX1 + 20, altY - 1, altX1 + 21, altY + 5, 0xFF5D4037);
        guiGraphics.fill(altX1 + 40, altY - 1, altX1 + 41, altY + 5, 0xFF5D4037);
        guiGraphics.fill(altX1 + 60, altY - 1, altX1 + 61, altY + 5, 0xFF5D4037);

        int altFill = (int) (Math.min(1.0, Math.max(0.0, (double) currentY / ceiling)) * altW);
        if (altFill > 0) {
            int baro = currentY >= ceiling ? 0xFFFF5722 : 0xFFCFD8DC;
            guiGraphics.fill(altX1, altY + 1, altX1 + altFill, altY + 3, baro);
        }
        int altCurX = altX1 + altFill;
        guiGraphics.fill(altCurX - 1, altY - 1, altCurX + 1, altY + 5, 0xFFFFE082);

        // --- ROW 3: FOOTER POWER TUBE ---
        int pwrX1 = panelX + 7;
        int pwrX2 = panelX + panelW - 7;
        int pwrW = pwrX2 - pwrX1;
        int pwrY = panelY + 28;

        // Background track
        guiGraphics.fill(pwrX1, pwrY, pwrX2, pwrY + 3, 0xFF140D07);
        int pwrFill = (int) (Math.min(1.0, Math.max(0.0, energyPercent / 100.0)) * pwrW);
        if (pwrFill > 0) {
            int filament = energyPercent > 50 ? 0xFFFFB74D : (energyPercent > 20 ? 0xFFFF9800 : 0xFFFF3D00);
            guiGraphics.fill(pwrX1, pwrY, pwrX1 + pwrFill, pwrY + 3, filament);
        }
        String pwrStr = "PWR " + (storedEnergy / 1000) + "k / " + (maxEnergy / 1000) + "k FE [" + (int) energyPercent + "%]";
        int pwrStrW = font.width(pwrStr);
        guiGraphics.drawString(font, pwrStr, panelX + panelW / 2 - pwrStrW / 2, panelY + 29, 0xFFE0E0E0, true);
    }

    // =========================================================================
    // GENERATION 2: MILITARY AVIONICS HUD (Cold War / Modern Jet CRT)
    // Phosphor green night-vision glass, corner brackets, FPV boresight,
    // discrete LED thermal matrix, Mach tape, ceiling alert hatch.
    // =========================================================================
    private void renderMilitaryStandardHud(GuiGraphics guiGraphics, Font font, LocalPlayer player, EleniumFlightUnitItem item,
                                           int panelX, int panelY, int panelW, int panelH,
                                           double speedKmh, double mach, int currentY, int ceiling,
                                           float heat, boolean overheated, boolean inWater, boolean inRain, boolean isFlooded,
                                           int storedEnergy, int maxEnergy, double energyPercent) {
        // 1. Phosphor green CRT cockpit glass
        int bgColor = isFlooded ? 0xDD2A0808 : (overheated ? 0xDD240606 : 0xD006160B);
        guiGraphics.fill(panelX, panelY, panelX + panelW, panelY + panelH, bgColor);

        // Phosphor green frame
        int frameBorder = isFlooded ? 0xFFFF2222 : (overheated ? 0xFFFF1744 : 0x5500E676);
        guiGraphics.hLine(panelX, panelX + panelW - 1, panelY, frameBorder);
        guiGraphics.hLine(panelX, panelX + panelW - 1, panelY + panelH - 1, frameBorder);
        guiGraphics.vLine(panelX, panelY, panelY + panelH - 1, frameBorder);
        guiGraphics.vLine(panelX + panelW - 1, panelY, panelY + panelH - 1, frameBorder);

        // Tactical reticle brackets at 4 corners
        int bracketColor = isFlooded ? 0xFFFF4444 : (overheated ? 0xFFFF1744 : 0xFF00E676);
        drawReticleBracket(guiGraphics, panelX, panelY, bracketColor, true, true);
        drawReticleBracket(guiGraphics, panelX + panelW - 6, panelY, bracketColor, false, true);
        drawReticleBracket(guiGraphics, panelX, panelY + panelH - 6, bracketColor, true, false);
        drawReticleBracket(guiGraphics, panelX + panelW - 6, panelY + panelH - 6, bracketColor, false, false);

        // Section Hairline Dividers
        int dividerColor = 0x3500E676;
        guiGraphics.vLine(panelX + 88, panelY + 11, panelY + 25, dividerColor);
        guiGraphics.vLine(panelX + 176, panelY + 11, panelY + 25, dividerColor);

        // --- ROW 1: HEADER TELEMETRY ---
        String modelTag = "[" + getModelChip(item.getFlightDesign()) + "]";
        guiGraphics.drawString(font, modelTag, panelX + 8, panelY + 2, 0xFF00E676, false);

        String statusMsg;
        int statusColor;
        boolean strained = currentY >= ceiling && player.getAbilities().flying && !player.onGround();
        if (isFlooded) {
            statusMsg = "⚠ THRUSTER STALL ⚠";
            statusColor = 0xFFFF4444;
        } else if (overheated) {
            statusMsg = "⚠ THERMAL CUTOFF ⚠";
            statusColor = 0xFFFF1744;
        } else if (strained) {
            statusMsg = "▲ ALT LIMIT REACHED ▲";
            statusColor = 0xFFFFB300;
        } else if (ClientFlightTelemetry.boostStep == 3) {
            statusMsg = "⚡ BOOST MAX x3 ⚡";
            statusColor = 0xFF76FF03;
        } else if (ClientFlightTelemetry.boostStep == 2) {
            statusMsg = "⚡ BOOST ACTIVE x2 ⚡";
            statusColor = 0xFF00E676;
        } else if (player.isSprinting() && player.getAbilities().flying) {
            statusMsg = "▶ INTERCEPT SPRINT ◀";
            statusColor = 0xFF00E676;
        } else if (player.getAbilities().flying) {
            statusMsg = "◆ FLIGHT PATH LOCK ◆";
            statusColor = 0xFF69F0AE;
        } else {
            statusMsg = "✦ SYSTEM ARMED ✦";
            statusColor = 0xAA00E676;
        }
        int statusW = font.width(statusMsg);
        guiGraphics.drawString(font, statusMsg, panelX + panelW / 2 - statusW / 2, panelY + 2, statusColor, false);

        String certTag = item.isWaterproof() ? "[SEALED]" : (inRain ? "[RAIN -15%]" : "[STD-ATMO]");
        int certColor = item.isWaterproof() ? 0xFF69F0AE : (inRain ? 0xFFFFB300 : 0xAA00E676);
        int certW = font.width(certTag);
        guiGraphics.drawString(font, certTag, panelX + panelW - 8 - certW, panelY + 2, certColor, false);

        // --- ROW 2: MAIN INSTRUMENTS ---
        // Bay 1: Tactical Airspeed & Mach Tape
        int spdX1 = panelX + 7;
        int spdX2 = panelX + 85;
        int spdY = panelY + 20;
        int spdW = spdX2 - spdX1;
        String spdStr = (int) speedKmh + " KPH";
        String machStr = String.format("M%.2f", mach);
        guiGraphics.drawString(font, spdStr, spdX1 + 1, panelY + 11, 0xFF00E676, false);
        guiGraphics.drawString(font, machStr, spdX2 - font.width(machStr) - 1, panelY + 11, mach >= 0.90 ? 0xFFFFB300 : 0xFF69F0AE, false);

        guiGraphics.fill(spdX1, spdY, spdX2, spdY + 4, 0x9000180B);
        guiGraphics.fill(spdX1 + 20, spdY - 1, spdX1 + 21, spdY + 5, 0x7000E676);
        guiGraphics.fill(spdX1 + 40, spdY - 1, spdX1 + 41, spdY + 5, 0x7000E676);
        guiGraphics.fill(spdX1 + 60, spdY - 1, spdX1 + 61, spdY + 5, 0x7000E676);
        guiGraphics.fill(spdX1 + 72, spdY - 1, spdX1 + 73, spdY + 5, 0xFFFF1744); // Mach 1 barrier tick

        int spdFill = (int) (Math.min(1.0, speedKmh / 105.0) * spdW);
        if (spdFill > 0) {
            int color = mach >= 0.90 ? 0xFFFFB300 : 0xFF00E676;
            guiGraphics.fill(spdX1, spdY + 1, spdX1 + spdFill, spdY + 3, color);
        }
        int curX = spdX1 + spdFill;
        guiGraphics.fill(curX - 1, spdY - 1, curX + 1, spdY + 5, 0xFFFFFFFF);

        // Bay 2: Central Flight Director / Boresight & 5-Segment LED Thermal Matrix
        int bay2X1 = panelX + 91;
        int bay2X2 = panelX + 173;
        int bay2W = bay2X2 - bay2X1;
        String coreTitle = overheated ? "!OVERHEAT!" : (heat >= 75 ? "CORE [CRIT]" : "CORE " + (int) heat + "%");
        int coreColor = overheated ? 0xFFFF1744 : (heat >= 75 ? 0xFFFF9100 : 0xFF00E676);
        int coreW = font.width(coreTitle);
        guiGraphics.drawString(font, coreTitle, bay2X1 + (bay2W - coreW) / 2, panelY + 11, coreColor, false);

        // 5-Segment CRT Matrix
        int heatY = panelY + 20;
        int segW = 12;
        int segGap = 2;
        int segStartX = bay2X1 + 7;
        for (int i = 0; i < 5; i++) {
            int sx1 = segStartX + i * (segW + segGap);
            int sx2 = sx1 + segW;
            guiGraphics.fill(sx1, heatY, sx2, heatY + 4, 0x9000180B);
            guiGraphics.fill(sx1 - 1, heatY - 1, sx2 + 1, heatY + 5, 0x3000E676);

            if (overheated) {
                if ((player.tickCount / 3) % 2 == 0) {
                    guiGraphics.fill(sx1, heatY + 1, sx2, heatY + 3, 0xFFFF1744);
                }
            } else if (heat >= (i * 20.0F) + 5.0F) {
                int segCol = switch (i) {
                    case 0, 1 -> 0xFF00E676;
                    case 2 -> 0xFFFFEA00;
                    case 3 -> 0xFFFF9100;
                    default -> 0xFFFF1744;
                };
                guiGraphics.fill(sx1, heatY + 1, sx2, heatY + 3, segCol);
            }
        }

        // Bay 3: Tactical Altitude Tape & Ceiling Alarm
        int altX1 = panelX + 179;
        int altX2 = panelX + 257;
        int altW = altX2 - altX1;
        String altStr = "ALT " + currentY + "m";
        String ceilStr = "/" + ceiling + "m";
        guiGraphics.drawString(font, altStr, altX1 + 1, panelY + 11, strained ? 0xFFFF1744 : 0xFF00E676, false);
        guiGraphics.drawString(font, ceilStr, altX2 - font.width(ceilStr) - 1, panelY + 11, 0xAA00E676, false);

        int altY = panelY + 20;
        guiGraphics.fill(altX1, altY, altX2, altY + 4, 0x9000180B);
        guiGraphics.fill(altX2 - 7, altY, altX2, altY + 4, 0x70FF2222);
        guiGraphics.fill(altX1 + 20, altY - 1, altX1 + 21, altY + 5, 0x7000E676);
        guiGraphics.fill(altX1 + 40, altY - 1, altX1 + 41, altY + 5, 0x7000E676);
        guiGraphics.fill(altX1 + 60, altY - 1, altX1 + 61, altY + 5, 0x7000E676);

        int altFill = (int) (Math.min(1.0, Math.max(0.0, (double) currentY / ceiling)) * altW);
        if (altFill > 0) {
            int altCol = currentY >= ceiling ? 0xFFFF1744 : (currentY >= ceiling - 15 ? 0xFFFFAB00 : 0xFF00E676);
            guiGraphics.fill(altX1, altY + 1, altX1 + altFill, altY + 3, altCol);
        }
        int altCurX = altX1 + altFill;
        guiGraphics.fill(altCurX - 1, altY - 1, altCurX + 1, altY + 5, 0xFFFFFFFF);

        // --- ROW 3: FOOTER POWER TAPE ---
        int pwrX1 = panelX + 7;
        int pwrX2 = panelX + panelW - 7;
        int pwrW = pwrX2 - pwrX1;
        int pwrY = panelY + 28;

        guiGraphics.fill(pwrX1, pwrY, pwrX2, pwrY + 3, 0x9000180B);
        int pwrFill = (int) (Math.min(1.0, Math.max(0.0, energyPercent / 100.0)) * pwrW);
        if (pwrFill > 0) {
            int pwrCol = energyPercent > 50 ? 0xFF00E676 : (energyPercent > 20 ? 0xFFFFD600 : 0xFFFF1744);
            guiGraphics.fill(pwrX1, pwrY, pwrX1 + pwrFill, pwrY + 3, pwrCol);
        }
        String pwrStr = "PWR " + (storedEnergy / 1000) + "k / " + (maxEnergy / 1000) + "k FE [" + (int) energyPercent + "%]";
        int pwrStrW = font.width(pwrStr);
        guiGraphics.drawString(font, pwrStr, panelX + panelW / 2 - pwrStrW / 2, panelY + 29, 0xFFFFFFFF, true);
    }

    // =========================================================================
    // GENERATION 3: ADVANCED HOLOGRAPHIC DIGITAL HUD (Cyberpunk / 6th-Gen)
    // Deep cyan glassmorphism, double chevrons, laser vernier scales,
    // Quantum Nexus core matrix, dynamic Mach decimal telemetry.
    // =========================================================================
    private void renderAdvancedDigitalHud(GuiGraphics guiGraphics, Font font, LocalPlayer player, EleniumFlightUnitItem item,
                                          int panelX, int panelY, int panelW, int panelH,
                                          double speedKmh, double mach, int currentY, int ceiling,
                                          float heat, boolean overheated, boolean inWater, boolean inRain, boolean isFlooded,
                                          int storedEnergy, int maxEnergy, double energyPercent) {
        // 1. Holographic deep cyan glass slate
        int bgColor = isFlooded ? 0xDD2A0404 : (overheated ? 0xDD240303 : 0xDC020C18);
        guiGraphics.fill(panelX, panelY, panelX + panelW, panelY + panelH, bgColor);

        // Neon cyan laser border
        int frameBorder = isFlooded ? 0xFFFF1744 : (overheated ? 0xFFFF007F : 0x8000E5FF);
        guiGraphics.hLine(panelX, panelX + panelW - 1, panelY, frameBorder);
        guiGraphics.hLine(panelX, panelX + panelW - 1, panelY + panelH - 1, frameBorder);
        guiGraphics.vLine(panelX, panelY, panelY + panelH - 1, frameBorder);
        guiGraphics.vLine(panelX + panelW - 1, panelY, panelY + panelH - 1, frameBorder);

        // Hi-tech double chevrons at 4 corners » «
        int chevronColor = isFlooded ? 0xFFFF2222 : (overheated ? 0xFFFF1744 : 0xFF00E5FF);
        drawDoubleChevron(guiGraphics, panelX, panelY, chevronColor, true, true);
        drawDoubleChevron(guiGraphics, panelX + panelW - 8, panelY, chevronColor, false, true);
        drawDoubleChevron(guiGraphics, panelX, panelY + panelH - 8, chevronColor, true, false);
        drawDoubleChevron(guiGraphics, panelX + panelW - 8, panelY + panelH - 8, chevronColor, false, false);

        // Neon Grid Hairline Dividers
        int dividerColor = 0x5000E5FF;
        guiGraphics.vLine(panelX + 88, panelY + 11, panelY + 25, dividerColor);
        guiGraphics.vLine(panelX + 176, panelY + 11, panelY + 25, dividerColor);

        // --- ROW 1: HEADER TELEMETRY ---
        String modelTag = "[" + getModelChip(item.getFlightDesign()) + "]";
        guiGraphics.drawString(font, modelTag, panelX + 8, panelY + 2, 0xFF00E5FF, false);

        String statusMsg;
        int statusColor;
        boolean strained = currentY >= ceiling && player.getAbilities().flying && !player.onGround();
        if (isFlooded) {
            statusMsg = "⚠ HYDRO-LOCK SHUTDOWN ⚠";
            statusColor = 0xFFFF1744;
        } else if (overheated) {
            statusMsg = "⚠ CORE OVERHEAT SCRAM ⚠";
            statusColor = 0xFFFF007F;
        } else if (strained) {
            statusMsg = "▲ CEILING OVERSTRESS ▲";
            statusColor = 0xFFFFB000;
        } else if (ClientFlightTelemetry.boostStep == 3) {
            statusMsg = "⚡ HYPERSONIC BURST x3 ⚡";
            statusColor = 0xFFFF007F;
        } else if (ClientFlightTelemetry.boostStep == 2) {
            statusMsg = "⚡ QUANTUM PULSE x2 ⚡";
            statusColor = 0xFF18FFFF;
        } else if (player.isSprinting() && player.getAbilities().flying) {
            statusMsg = "▶ VECTOR THRUST ◀";
            statusColor = 0xFF00E5FF;
        } else if (player.getAbilities().flying) {
            statusMsg = "◆ GRAV-LOCK CRUISE ◆";
            statusColor = 0xFF80D8FF;
        } else {
            statusMsg = "✦ SYSTEM SYNC READY ✦";
            statusColor = 0xAA00E5FF;
        }
        int statusW = font.width(statusMsg);
        guiGraphics.drawString(font, statusMsg, panelX + panelW / 2 - statusW / 2, panelY + 2, statusColor, false);

        String certTag = item.isWaterproof() ? "[SUBMERSIBLE]" : (inRain ? "[RAIN -15%]" : "[ALL-WEATHER]");
        int certColor = item.isWaterproof() ? 0xFF00E5FF : (inRain ? 0xFFFFB000 : 0xFF80D8FF);
        int certW = font.width(certTag);
        guiGraphics.drawString(font, certTag, panelX + panelW - 8 - certW, panelY + 2, certColor, false);

        // --- ROW 2: MAIN INSTRUMENTS ---
        // Bay 1: Holographic Mach & Airspeed Vernier Scale
        int spdX1 = panelX + 7;
        int spdX2 = panelX + 85;
        int spdY = panelY + 20;
        int spdW = spdX2 - spdX1;
        String spdStr = (int) speedKmh + " KPH";
        String machStr = String.format("M%.2f", mach);
        guiGraphics.drawString(font, spdStr, spdX1 + 1, panelY + 11, 0xFF00E5FF, false);
        guiGraphics.drawString(font, machStr, spdX2 - font.width(machStr) - 1, panelY + 11, mach >= 0.90 ? 0xFFFF007F : 0xFF18FFFF, false);

        guiGraphics.fill(spdX1, spdY, spdX2, spdY + 4, 0x90001428);
        guiGraphics.fill(spdX1 + 20, spdY - 1, spdX1 + 21, spdY + 5, 0x8000E5FF);
        guiGraphics.fill(spdX1 + 40, spdY - 1, spdX1 + 41, spdY + 5, 0x8000E5FF);
        guiGraphics.fill(spdX1 + 60, spdY - 1, spdX1 + 61, spdY + 5, 0x8000E5FF);
        guiGraphics.fill(spdX1 + 72, spdY - 1, spdX1 + 73, spdY + 5, 0xFFFF007F); // Transonic boundary notch

        int spdFill = (int) (Math.min(1.0, speedKmh / 105.0) * spdW);
        if (spdFill > 0) {
            int laserCol = mach >= 0.90 ? 0xFFFF007F : (mach >= 0.70 ? 0xFF00B0FF : 0xFF00E5FF);
            guiGraphics.fill(spdX1, spdY + 1, spdX1 + spdFill, spdY + 3, laserCol);
        }
        int curX = spdX1 + spdFill;
        guiGraphics.fill(curX - 1, spdY - 1, curX + 1, spdY + 5, 0xFFFFFFFF);
        guiGraphics.fill(curX, spdY - 2, curX, spdY + 6, 0xFF00E5FF);

        // Bay 2: Quantum Nexus Core Matrix & Kinetic Capacitors
        int bay2X1 = panelX + 91;
        int bay2X2 = panelX + 173;
        int bay2W = bay2X2 - bay2X1;
        String nexusTitle = overheated ? "!OVERHEAT!" : (heat >= 75 ? "NEXUS [CRIT]" : "NEXUS " + (int) heat + "%");
        int nexusColor = overheated ? 0xFFFF007F : (heat >= 75 ? 0xFFFF9100 : 0xFF00E5FF);
        int nexusW = font.width(nexusTitle);
        guiGraphics.drawString(font, nexusTitle, bay2X1 + (bay2W - nexusW) / 2, panelY + 11, nexusColor, false);

        int heatY = panelY + 20;
        int segW = 12;
        int segGap = 2;
        int segStartX = bay2X1 + 7;
        for (int i = 0; i < 5; i++) {
            int sx1 = segStartX + i * (segW + segGap);
            int sx2 = sx1 + segW;
            guiGraphics.fill(sx1, heatY, sx2, heatY + 4, 0x90001428);
            guiGraphics.fill(sx1 - 1, heatY - 1, sx2 + 1, heatY + 5, 0x4000E5FF);

            if (overheated) {
                if ((player.tickCount / 3) % 2 == 0) {
                    guiGraphics.fill(sx1, heatY + 1, sx2, heatY + 3, 0xFFFF007F);
                }
            } else if (heat >= (i * 20.0F) + 5.0F) {
                int segCol = switch (i) {
                    case 0, 1 -> 0xFF00E5FF;
                    case 2 -> 0xFF18FFFF;
                    case 3 -> 0xFFFFD600;
                    default -> 0xFFFF007F;
                };
                guiGraphics.fill(sx1, heatY + 1, sx2, heatY + 3, segCol);
            }
        }

        // Bay 3: Digital Altitude Ribbon & Ceiling Barrier
        int altX1 = panelX + 179;
        int altX2 = panelX + 257;
        int altW = altX2 - altX1;
        String altStr = "ALT " + currentY + "m";
        String ceilStr = "LIM " + ceiling + "m";
        guiGraphics.drawString(font, altStr, altX1 + 1, panelY + 11, strained ? 0xFFFF007F : 0xFF00E5FF, false);
        guiGraphics.drawString(font, ceilStr, altX2 - font.width(ceilStr) - 1, panelY + 11, 0xAA00E5FF, false);

        int altY = panelY + 20;
        guiGraphics.fill(altX1, altY, altX2, altY + 4, 0x90001428);
        guiGraphics.fill(altX2 - 7, altY, altX2, altY + 4, 0x80FF007F);
        guiGraphics.fill(altX1 + 20, altY - 1, altX1 + 21, altY + 5, 0x8000E5FF);
        guiGraphics.fill(altX1 + 40, altY - 1, altX1 + 41, altY + 5, 0x8000E5FF);
        guiGraphics.fill(altX1 + 60, altY - 1, altX1 + 61, altY + 5, 0x8000E5FF);

        int altFill = (int) (Math.min(1.0, Math.max(0.0, (double) currentY / ceiling)) * altW);
        if (altFill > 0) {
            int altCol = currentY >= ceiling ? 0xFFFF007F : (currentY >= ceiling - 15 ? 0xFFFFB000 : 0xFF00E5FF);
            guiGraphics.fill(altX1, altY + 1, altX1 + altFill, altY + 3, altCol);
        }
        int altCurX = altX1 + altFill;
        guiGraphics.fill(altCurX - 1, altY - 1, altCurX + 1, altY + 5, 0xFFFFFFFF);
        guiGraphics.fill(altCurX, altY - 2, altCurX, altY + 6, 0xFF00E5FF);

        // --- ROW 3: FOOTER QUANTUM PLASMA ENERGY RAIL ---
        int pwrX1 = panelX + 7;
        int pwrX2 = panelX + panelW - 7;
        int pwrW = pwrX2 - pwrX1;
        int pwrY = panelY + 28;

        guiGraphics.fill(pwrX1, pwrY, pwrX2, pwrY + 3, 0x90001428);
        int pwrFill = (int) (Math.min(1.0, Math.max(0.0, energyPercent / 100.0)) * pwrW);
        if (pwrFill > 0) {
            int pwrCol = energyPercent > 50 ? 0xFF00E5FF : (energyPercent > 20 ? 0xFF18FFFF : 0xFFFF007F);
            guiGraphics.fill(pwrX1, pwrY, pwrX1 + pwrFill, pwrY + 3, pwrCol);
        }
        String pwrStr = "PLASMA " + (storedEnergy / 1000) + "k / " + (maxEnergy / 1000) + "k FE [" + (int) energyPercent + "%]";
        int pwrStrW = font.width(pwrStr);
        guiGraphics.drawString(font, pwrStr, panelX + panelW / 2 - pwrStrW / 2, panelY + 29, 0xFFFFFFFF, true);
    }

    // --- GRAPHICAL HELPERS ---
    private static void drawRivet(GuiGraphics g, int x, int y) {
        g.fill(x - 1, y - 1, x + 2, y + 2, 0xFFD7CCC8);
        g.fill(x, y, x + 2, y + 2, 0xFF4E342E);
    }

    private static void drawReticleBracket(GuiGraphics g, int x, int y, int color, boolean left, boolean top) {
        if (left && top) {
            g.hLine(x, x + 5, y, color);
            g.vLine(x, y, y + 5, color);
        } else if (!left && top) {
            g.hLine(x, x + 5, y, color);
            g.vLine(x + 5, y, y + 5, color);
        } else if (left && !top) {
            g.hLine(x, x + 5, y + 5, color);
            g.vLine(x, y, y + 5, color);
        } else {
            g.hLine(x, x + 5, y + 5, color);
            g.vLine(x + 5, y, y + 5, color);
        }
    }

    private static void drawDoubleChevron(GuiGraphics g, int x, int y, int color, boolean left, boolean top) {
        drawReticleBracket(g, x, y, color, left, top);
        int ox = left ? x + 2 : x - 2;
        int oy = top ? y + 2 : y - 2;
        drawReticleBracket(g, ox, oy, color, left, top);
    }
}
