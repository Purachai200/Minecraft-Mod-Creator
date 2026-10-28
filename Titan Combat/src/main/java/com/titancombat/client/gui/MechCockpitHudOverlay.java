package com.titancombat.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseMechEntity;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.MechState;
import com.titancombat.entity.TitanClass;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.client.gui.overlay.ForgeGui;
import net.minecraftforge.client.gui.overlay.IGuiOverlay;

import static com.titancombat.client.gui.CockpitHudState.*;
import static com.titancombat.client.gui.HudDraw.*;

/**
 * Titanfall-style holographic cockpit HUD.
 * <p>
 * Layout (first person):
 * <pre>
 *  [radar]                 [ compass tape / heading ]
 *
 *                               (class reticle)                [control legend, first ~6 s]
 *                           [critical / eject / parked]
 *  CLASS  role                   [ core status ]                       WEAPON NAME
 *  //// shield ////               [dash][dash][dash]                  24 /24
 *  [hull segments....]       CORE [//////////////] %               ||||||||||||||
 *  HULL 87%  [DEFENSE MATRIX]
 * </pre>
 * Third person shows only the hull/shield block and the reticle. All per-tick work (scans, picks,
 * strings) lives in {@link CockpitHudState}; this class only draws.
 */
public class MechCockpitHudOverlay {

    private static final ResourceLocation RETICLES =
            new ResourceLocation(TitanCombatMod.MODID, "textures/gui/hud_reticles.png");
    private static final ResourceLocation RADAR =
            new ResourceLocation(TitanCombatMod.MODID, "textures/gui/hud_radar.png");
    private static final ResourceLocation VIGNETTE =
            new ResourceLocation(TitanCombatMod.MODID, "textures/gui/hud_vignette.png");

    // Palette
    static final int CYAN = 0x00E5FF;
    static final int ICE = 0xD8FBFF;
    static final int WHITE = 0xFFFFFF;
    static final int DIM = 0x7FB8C8;
    static final int SHIELD = 0x40C4FF;
    static final int AMBER = 0xFFB300;
    static final int RED = 0xFF2A44;
    static final int GREEN = 0x00E676;
    static final int GOLD = 0xFFD54F;
    static final int BLACK = 0x000000;

    private static final String[] TAPE_LABEL = new String[360];
    private static final String[] CHECK_LABELS = {"REACTOR CORE", "WEAPON SYSTEMS", "SHIELD EMITTERS", "MOTOR CONTROL"};
    private static final String BOOT_HEADER = "TITAN OS v7.3  //  COLD BOOT";
    private static final String BOOT_LINK = "NEURAL LINK ESTABLISHED";
    private static final String BOOT_PROTOCOL = "PROTOCOL 3:  PROTECT THE PILOT";
    private static final String BOOT_SYNC = "SYNC";

    static {
        String[] card = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        for (int d = 0; d < 360; d++) {
            if (d % 45 == 0) TAPE_LABEL[d] = card[d / 45];
            else if (d % 30 == 0) TAPE_LABEL[d] = Integer.toString(d);
        }
    }

    public static final IGuiOverlay HUD_COCKPIT = (ForgeGui gui, GuiGraphics guiGraphics, float partialTick, int screenWidth, int screenHeight) ->
            render(guiGraphics, partialTick, screenWidth, screenHeight);

    private static void render(GuiGraphics g, float pt, int W, int H) {
        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || !(player.getVehicle() instanceof BaseMechEntity mech)) return;
        if (mech.getId() != boardedVehicleId) return; // state not initialised yet (first tick after mounting)

        Font font = mc.font;
        boolean firstPerson = mc.options.getCameraType() == CameraType.FIRST_PERSON;
        float now = clientTicks + pt;
        float t = now - boardTick;
        boolean boot = firstPerson && bootCinematic && t < BOOT_TICKS + 2;
        boolean sitting = mech instanceof BaseTitanEntity titan && titan.isSitting();

        float maxHealth = Math.max(1.0F, mech.getMaxHealth());
        float hp = clamp01(mech.getHealth() / maxHealth);
        boolean doomed = mech.getMechState() == MechState.DOOMED;
        boolean critical = hp < 0.25F || doomed;
        int cx = W / 2;
        int cy = H / 2;

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        // ---------------------------------------------------------------- power level (parking dims systems)
        float sinceSit = now - sitChangeTick;
        float power;
        if (sitting) {
            power = 1.0F - 0.6F * smooth(sinceSit / 14.0F);
        } else {
            power = 0.4F + 0.6F * smooth(sinceSit / 10.0F);
        }
        if (sinceSit < 14.0F && noise((int) (now * 1.7F)) > 0.6F) power *= 0.35F; // power-state flicker
        if (mech.getEnergy() <= 0) power *= 0.4F; // Dims cockpit HUD when power is depleted

        alpha = 1.0F;

        // ---------------------------------------------------------------- full-screen tints
        drawScreenEffects(g, W, H, now, mech, critical, firstPerson);

        // ---------------------------------------------------------------- HUD blocks
        float bootFlick = boot ? bootFlicker(t) : 1.0F;
        if (firstPerson) {
            alpha = power * intro(boot, t, 36) * bootFlick;
            float heading = Mth.wrapDegrees(player.getViewYRot(pt) + 180.0F);
            if (heading < 0) heading += 360.0F;
            drawCompass(g, font, cx, heading);

            alpha = power * intro(boot, t, 40) * bootFlick;
            drawRadar(g, font, 12, 12, player.getViewYRot(pt), now);
        }

        alpha = power * intro(boot, t, 42) * bootFlick;
        slideX(g, boot, t, 42, -24);
        drawHullPanel(g, font, 16, H, mech, hp, maxHealth, now);
        g.pose().popPose();

        if (firstPerson) {
            alpha = power * intro(boot, t, 46) * bootFlick;
            slideY(g, boot, t, 46, 20);
            drawCoreAndDash(g, font, cx, H, mech, now);
            g.pose().popPose();

            alpha = power * intro(boot, t, 44) * bootFlick;
            slideX(g, boot, t, 44, 24);
            drawWeapon(g, font, W, H, now);
            g.pose().popPose();
        }

        if (!sitting) {
            alpha = intro(boot, t, 30) * bootFlick;
            drawReticle(g, font, cx, cy, now, mech);
        }

        alpha = 1.0F;
        if (critical) drawCritical(g, font, cx, cy, now, doomed);
        if (sitting || sinceSit < 14.0F) drawParked(g, font, cx, cy, now, sitting, sinceSit, critical);
        if (mech.getEnergy() <= 0) drawReactorDepletedWarning(g, font, cx, cy, now);

        if (firstPerson) drawHints(g, font, W, H, t);
        if (boot) drawBoot(g, font, W, H, t);

        alpha = 1.0F;
        RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
        RenderSystem.disableBlend();
    }

    // =================================================================== helpers
    private static float intro(boolean boot, float t, float start) {
        if (!boot) return 1.0F;
        float p = smooth((t - start) / 10.0F);
        // short holographic flicker as each block powers on
        if (p > 0.0F && p < 0.6F && noise((int) (t * 3.0F) + (int) start) > 0.55F) p *= 0.3F;
        return p;
    }

    private static float bootFlicker(float t) {
        if (t < 24.0F && noise((int) (t * 2.0F) * 31) > 0.82F) return 0.4F;
        return 1.0F;
    }

    private static void slideX(GuiGraphics g, boolean boot, float t, float start, float dist) {
        g.pose().pushPose();
        if (boot) g.pose().translate(dist * (1.0F - smooth((t - start) / 12.0F)), 0.0F, 0.0F);
    }

    private static void slideY(GuiGraphics g, boolean boot, float t, float start, float dist) {
        g.pose().pushPose();
        if (boot) g.pose().translate(0.0F, dist * (1.0F - smooth((t - start) / 12.0F)), 0.0F);
    }

    // =================================================================== screen effects
    private static void drawScreenEffects(GuiGraphics g, int W, int H, float now, BaseMechEntity mech,
                                          boolean critical, boolean firstPerson) {
        float sinceHit = now - damageTick;
        if (sinceHit < 10.0F) {
            tex(g, VIGNETTE, 0, 0, W, H, 0, 0, 128, 128, 128, 128, RED, 0.45F * (1.0F - sinceHit / 10.0F));
        }
        if (critical) {
            float pulse = 0.5F + 0.5F * Mth.sin(now * 0.35F);
            tex(g, VIGNETTE, 0, 0, W, H, 0, 0, 128, 128, 128, 128, RED, 0.30F + 0.30F * pulse);
        }
        if (!firstPerson) return;
        if (mech.isDefenseActive()) {
            tex(g, VIGNETTE, 0, 0, W, H, 0, 0, 128, 128, 128, 128, CYAN, 0.16F + 0.04F * Mth.sin(now * 0.2F));
        }
        if (mech.isOverdriveActive()) {
            tex(g, VIGNETTE, 0, 0, W, H, 0, 0, 128, 128, 128, 128, GOLD, 0.14F + 0.06F * Mth.sin(now * 0.5F));
        }
    }

    // =================================================================== compass tape (top centre)
    private static void drawCompass(GuiGraphics g, Font font, int cx, float heading) {
        if (alpha <= 0.01F) return;
        final int half = 92;
        final float ppd = 1.5F;
        final int base = 20;

        rect(g, cx - half, base, cx + half, base + 1, CYAN, 0.22F);

        int start = Mth.floor((heading - 62.0F) / 5.0F) * 5;
        for (int d = start; d <= heading + 62.0F; d += 5) {
            float dx = (d - heading) * ppd;
            if (dx < -half || dx > half) continue;
            float f = dx / half;
            float fade = 1.0F - f * f;
            int dd = Math.floorMod(d, 360);
            int len = dd % 45 == 0 ? 6 : (dd % 15 == 0 ? 4 : 2);
            int x = Math.round(cx + dx);
            rect(g, x, base - len, x + 1, base, dd % 45 == 0 ? WHITE : CYAN, 0.85F * fade);
            String label = TAPE_LABEL[dd];
            if (label != null && Math.abs(dx) > 9) {
                boolean cardinal = dd % 45 == 0;
                textCenter(g, font, label, x + 1, 4, cardinal ? WHITE : DIM, (cardinal ? 0.95F : 0.6F) * fade, false);
            }
        }

        // centre caret + heading readout
        rect(g, cx, base - 9, cx + 1, base + 2, WHITE, 0.95F);
        rect(g, cx - 1, base + 2, cx + 2, base + 3, WHITE, 0.95F);
        rect(g, cx - 2, base + 3, cx + 3, base + 4, WHITE, 0.95F);
        int hd = Math.floorMod(Math.round(heading), 360);
        String hs = DEG3[hd];
        int w = font.width(hs);
        rect(g, cx - w / 2 - 4, base + 5, cx + w / 2 + 5, base + 16, BLACK, 0.35F);
        frame(g, cx - w / 2 - 4, base + 5, cx + w / 2 + 5, base + 16, CYAN, 0.5F);
        text(g, font, hs, cx - w / 2 + 1, base + 7, WHITE, 1.0F, false);
    }

    // =================================================================== radar (top left)
    private static void drawRadar(GuiGraphics g, Font font, int x, int y, float yawDeg, float now) {
        if (alpha <= 0.01F) return;
        int cx = x + 32;
        int cy = y + 32;
        tex(g, RADAR, x, y, 64, 64, 128, 0, 128, 128, 256, 128, WHITE, 1.0F);
        tex(g, RADAR, x, y, 64, 64, 0, 0, 128, 128, 256, 128, CYAN, 0.9F);

        // rotating sweep
        PoseStack pose = g.pose();
        pose.pushPose();
        pose.translate(cx + 0.5F, cy + 0.5F, 0.0F);
        rotate(pose, now * 0.10F);
        rect(g, 0, -29, 1, 0, CYAN, 0.35F);
        rotate(pose, -0.08F);
        rect(g, 0, -29, 1, 0, CYAN, 0.15F);
        rotate(pose, -0.08F);
        rect(g, 0, -29, 1, 0, CYAN, 0.06F);
        pose.popPose();

        float yaw = yawDeg * Mth.DEG_TO_RAD;
        float sin = Mth.sin(yaw);
        float cos = Mth.cos(yaw);
        float scale = 29.0F / (float) RADAR_RANGE;
        boolean blink = (int) (now / 6.0F) % 2 == 0;
        for (int i = 0; i < radarCount; i++) {
            float dx = RADAR_DX[i];
            float dz = RADAR_DZ[i];
            // screen right = pilot's right, screen up = forward
            float sx = (-dx * cos - dz * sin) * scale;
            float sy = -(-dx * sin + dz * cos) * scale;
            if (sx * sx + sy * sy > 29.0F * 29.0F) continue;
            int bx = Math.round(cx + sx);
            int by = Math.round(cy + sy);
            switch (RADAR_TYPE[i]) {
                case 3 -> {
                    rect(g, bx - 2, by - 2, bx + 3, by + 3, RED, blink ? 0.95F : 0.6F);
                    rect(g, bx - 1, by - 1, bx + 2, by + 2, BLACK, 0.6F);
                }
                case 2 -> rect(g, bx - 1, by - 1, bx + 2, by + 2, RED, 0.95F);
                case 1 -> rect(g, bx - 1, by - 1, bx + 1, by + 1, SHIELD, 0.95F);
                default -> rect(g, bx, by, bx + 1, by + 1, ICE, 0.55F);
            }
        }

        // own titan chevron
        rect(g, cx, cy - 2, cx + 1, cy + 2, WHITE, 1.0F);
        rect(g, cx - 1, cy, cx + 2, cy + 2, WHITE, 1.0F);

        // north marker on the ring
        int nx = Math.round(cx + sin * 25.0F);
        int ny = Math.round(cy + cos * 25.0F);
        textCenter(g, font, "N", nx + 1, ny - 3, WHITE, 0.8F, false);

        text(g, font, "32M", x + 1, y + 66, DIM, 0.7F, false);
        textRight(g, font, hostileText, x + 64, y + 66, hostileCount > 0 ? RED : GREEN, 0.85F, false);
    }

    // =================================================================== hull / shield (bottom left)
    private static void drawHullPanel(GuiGraphics g, Font font, int x0, int H, BaseMechEntity mech,
                                      float hp, float maxHealth, float now) {
        if (alpha <= 0.01F) return;
        int base = H - 14;
        final int barW = 131;

        // accent bracket
        rect(g, x0 - 6, base - 50, x0 - 5, base - 10, CYAN, 0.35F);
        rect(g, x0 - 6, base - 10, x0 + 18, base - 9, CYAN, 0.35F);
        rect(g, x0 - 6, base - 50, x0 - 2, base - 49, CYAN, 0.35F);

        // class name
        textScaled(g, font, className, x0, base - 52, 1.5F, 0.0F, WHITE, 0.95F, true);
        int nameW = (int) (font.width(className) * 1.5F);
        text(g, font, roleName, x0 + nameW + 6, base - 48, CYAN, 0.55F, false);

        // shield bar
        float maxShield = Math.max(1.0F, mech.getMaxShield());
        float sp = clamp01(mech.getShield() / maxShield);
        int sy = base - 35;
        boolean shieldFlash = now - shieldHitTick < 5.0F;
        boolean broken = sp <= 0.001F;
        int shieldBg = broken && (int) (now / 5.0F) % 2 == 0 ? AMBER : SHIELD;
        slant(g, x0, sy, barW, 3, 0.6F, shieldBg, broken ? 0.35F : 0.16F);
        slant(g, x0, sy, barW * sp, 3, 0.6F, shieldFlash ? WHITE : SHIELD, 0.95F);

        // segmented hull bar with damage trail
        int hy = base - 29;
        final int segs = 12;
        final float segW = 10.0F;
        float trail = clamp01(trailHealth / maxHealth);
        boolean hitFlash = now - damageTick < 6.0F && (int) (now / 2.0F) % 2 == 0;
        int hullColor = hp > 0.5F ? ICE : (hp > 0.25F ? AMBER : RED);
        for (int i = 0; i < segs; i++) {
            float sx = x0 + i * (segW + 1.0F);
            float s0 = (float) i / segs;
            float fill = clamp01((hp - s0) * segs);
            float tr = clamp01((trail - s0) * segs);
            slant(g, sx, hy, segW, 8, 0.5F, hitFlash ? RED : CYAN, hitFlash ? 0.35F : 0.14F);
            if (tr > fill) slant(g, sx, hy, segW * tr, 8, 0.5F, AMBER, 0.75F);
            if (fill > 0) slant(g, sx, hy, segW * fill, 8, 0.5F, hitFlash ? WHITE : hullColor, 0.92F);
        }

        // readout line
        int ty = base - 17;
        text(g, font, "HULL", x0, ty, CYAN, 0.6F, false);
        text(g, font, PCT[Math.round(hp * 100.0F)], x0 + 26, ty, hullColor, 0.95F, false);

        int curEnergy = mech.getEnergy();
        int maxEnergy = Math.max(1, mech.getMaxEnergy());
        float ep = clamp01((float) curEnergy / (float) maxEnergy);
        int epPct = Math.min(100, Math.round(ep * 100.0F));
        boolean lowEnergy = curEnergy <= 0 || ep < 0.20F;
        int energyColor = curEnergy <= 0 ? RED : (ep < 0.25F ? ((int) (now / 4.0F) % 2 == 0 ? RED : AMBER) : (ep < 0.50F ? AMBER : CYAN));

        if (mech.isDefenseActive()) {
            int chipX = x0 + 58;
            float pulse = 0.65F + 0.35F * Mth.sin(now * 0.4F);
            rect(g, chipX - 3, ty - 2, chipX + 83, ty + 9, CYAN, 0.16F);
            frame(g, chipX - 3, ty - 2, chipX + 83, ty + 9, CYAN, 0.6F * pulse);
            text(g, font, "DEFENSE MATRIX", chipX, ty, CYAN, pulse, false);
        } else {
            text(g, font, "PWR", x0 + 58, ty, CYAN, 0.6F, false);
            text(g, font, curEnergy <= 0 ? "OFFLINE" : PCT[epPct], x0 + 78, ty, energyColor, 0.95F, false);
        }

        // Reactor Energy slim bar (ey = base - 7, barW = 131)
        int ey = base - 7;
        slant(g, x0, ey, barW, 4, 0.6F, lowEnergy ? RED : CYAN, curEnergy <= 0 ? 0.3F : 0.16F);
        if (ep > 0) slant(g, x0, ey, barW * ep, 4, 0.6F, energyColor, 0.95F);
    }

    // =================================================================== core + dash (bottom centre)
    private static void drawCoreAndDash(GuiGraphics g, Font font, int cx, int H, BaseMechEntity mech, float now) {
        if (alpha <= 0.01F) return;
        int coreY = H - 18;
        final int segs = 25;
        final float segW = 5.0F;
        final float total = segs * (segW + 1.0F) - 1.0F;
        float x0 = cx - total / 2.0F;

        boolean overdrive = mech.isOverdriveActive();
        float core = mech.getCoreCharge();
        boolean ready = !overdrive && core >= 100.0F;
        float frac = overdrive ? clamp01(mech.getOverdriveTicks() / 200.0F) : clamp01(core / 100.0F);
        float pulse = 0.5F + 0.5F * Mth.sin(now * 0.45F);
        int color = overdrive ? GOLD : (ready ? (pulse > 0.5F ? WHITE : CYAN) : CYAN);

        for (int i = 0; i < segs; i++) {
            float sx = x0 + i * (segW + 1.0F);
            float f = clamp01((frac - (float) i / segs) * segs);
            slant(g, sx, coreY, segW, 5, 0.6F, CYAN, 0.14F);
            if (f > 0) slant(g, sx, coreY, segW * f, 5, 0.6F, color, ready ? 0.7F + 0.3F * pulse : 0.9F);
        }
        textRight(g, font, "CORE", (int) x0 - 5, coreY - 1, overdrive ? GOLD : CYAN, 0.7F, false);
        text(g, font, overdrive ? "" : PCT[Math.min(100, (int) core)], (int) (x0 + total) + 6, coreY - 1,
                ready ? WHITE : ICE, 0.85F, false);

        // dash cells: one per dash (BaseMechEntity.DASH_COST), three cells
        float dash = mech.getDashCharge();
        float cost = BaseMechEntity.DASH_COST;
        int dy = H - 30;
        for (int i = 0; i < 3; i++) {
            float f = clamp01((dash - i * cost) / cost);
            float px = cx - 43 + i * 30;
            slant(g, px, dy, 26, 4, 1.0F, CYAN, 0.16F);
            if (f >= 1.0F) {
                slant(g, px, dy, 26, 4, 1.0F, ICE, 0.95F);
            } else if (f > 0) {
                slant(g, px, dy, 26 * f, 4, 1.0F, CYAN, 0.45F);
            }
        }

        // status line
        if (overdrive) {
            textCenter(g, font, overdriveText, cx, H - 44, GOLD, 0.75F + 0.25F * pulse, true);
        } else if (ready) {
            float sinceReady = now - coreReadyTick;
            float s = sinceReady < 8.0F ? 1.0F + 0.5F * (1.0F - sinceReady / 8.0F) : 1.0F;
            textScaled(g, font, coreReadyText, cx, H - 44 - (s - 1.0F) * 4.0F, s, 0.5F, WHITE, 0.6F + 0.4F * pulse, true);
        }
    }

    // =================================================================== weapon + magazine (bottom right)
    private static void drawWeapon(GuiGraphics g, Font font, int W, int H, float now) {
        if (alpha <= 0.01F) return;
        int xr = W - 16;
        int base = H - 14;

        rect(g, xr + 5, base - 50, xr + 6, base + 3, CYAN, 0.35F);
        rect(g, xr - 18, base + 3, xr + 6, base + 4, CYAN, 0.35F);
        rect(g, xr + 2, base - 50, xr + 6, base - 49, CYAN, 0.35F);

        textRight(g, font, weaponName, xr, base - 52, WHITE, 0.7F, false);
        if (net.minecraft.client.Minecraft.getInstance().player.getVehicle() instanceof com.titancombat.entity.BaseTitanEntity titan
                && titan.hasHowitzer()) {
            drawHowitzer(g, font, titan, xr, base - 62);
        }

        boolean reloading = reloadTicksLeft > 0;
        float dim = weaponLowered ? 0.45F : 1.0F;
        float frac = magazine / (float) magSize;
        boolean empty = !ammoInfinite && magazine <= 0 && activeWeapon != null;
        boolean low = !ammoInfinite && frac < 0.25F;
        boolean blink = (int) (now / 5.0F) % 2 == 0;
        int color = ammoInfinite ? GOLD : (empty ? RED : (low ? AMBER : WHITE));
        float kick = clamp01(1.0F - (now - fireTick) / 4.0F);
        float na = (empty && !reloading ? (blink ? 1.0F : 0.4F) : 0.95F) * dim * (reloading ? 0.4F : 1.0F);
        textScaled(g, font, ammoText, xr - 26, base - 42 - kick, 2.5F + 0.2F * kick, 1.0F, color, na, true);
        if (!ammoInfinite) text(g, font, magSizeText, xr - 23, base - 32, DIM, 0.8F * dim, false);

        // per-round strip sized to the magazine, or the reload progress bar
        final float stripW = 90.0F;
        float tx0 = xr - stripW;
        if (reloading && activeWeapon != null) {
            float p = clamp01(1.0F - reloadTicksLeft / (float) Math.max(1, activeWeapon.getReloadTicks()));
            slant(g, tx0, base - 16, stripW, 5, 0.6F, CYAN, 0.14F);
            slant(g, tx0, base - 16, stripW * p, 5, 0.6F, AMBER, 0.9F);
        } else {
            int n = ammoInfinite ? 30 : magSize;
            int lit = ammoInfinite ? n : magazine;
            float sp = stripW / n;
            float w = Math.max(0.6F, sp * 0.66F);
            for (int i = 0; i < n; i++) {
                boolean on = i < lit;
                slant(g, tx0 + i * sp, base - 16, w, 5, 0.6F, on ? color : CYAN, on ? 0.85F * dim : 0.14F);
            }
        }

        // status line
        int sy = base - 7;
        if (activeWeapon == null) {
            // unarmed: no reload prompt
        } else if (weaponLowered) {
            textRight(g, font, holsteredText, xr, sy, DIM, 0.9F, false);
        } else if (reloading) {
            textRight(g, font, reloadingText, xr, sy, AMBER, 0.65F + 0.35F * Mth.sin(now * 0.5F), false);
        } else if (empty) {
            textRight(g, font, reloadPrompt, xr, sy, RED, blink ? 1.0F : 0.45F, true);
        } else if (activeWeapon != null && !ammoInfinite) {
            textRight(g, font, reserveText, xr, sy, reserveMags > 0 ? DIM : AMBER, 0.85F, false);
        }
    }

    /** Howitzer back module: rounds and gun state, then the target and the solved firing data. */
    private static void drawHowitzer(GuiGraphics g, Font font, com.titancombat.entity.BaseTitanEntity titan, int xr, int y) {
        String fireKey = com.titancombat.client.KeyInputHandler.KEY_FIRE_HOWITZER.getTranslatedKeyMessage().getString().toUpperCase();
        String mapKey = com.titancombat.client.KeyInputHandler.KEY_TACTICAL_MAP.getTranslatedKeyMessage().getString().toUpperCase();
        net.minecraft.core.BlockPos t = titan.getArtilleryTarget();
        net.minecraft.world.phys.Vec3 v = titan.artillerySolution();
        String state = titan.getHowitzerReload() > 0 ? "hud.titancombat.howitzer_reloading"
                : titan.getHowitzerRounds() <= 0 ? "hud.titancombat.howitzer_empty"
                : t == null ? "hud.titancombat.howitzer_ready"
                : titan.getArtilleryLaying() > 0 ? "hud.titancombat.howitzer_laying" : "hud.titancombat.howitzer_locked";
        textRight(g, font, net.minecraft.client.resources.language.I18n.get(state, titan.getHowitzerRounds(),
                com.titancombat.entity.Howitzer.ROUNDS_PER_RACK, fireKey), xr, y, AMBER, 0.95F, false);
        if (t == null || v == null) {
            textRight(g, font, net.minecraft.client.resources.language.I18n.get("hud.titancombat.artillery_no_target", mapKey,
                    com.titancombat.client.KeyInputHandler.KEY_MARK_TARGET.getTranslatedKeyMessage().getString().toUpperCase()),
                    xr, y - 10, AMBER, 0.75F, false);
            return;
        }
        double dx = t.getX() + 0.5D - titan.getX(), dz = t.getZ() + 0.5D - titan.getZ();
        double range = Math.sqrt(dx * dx + dz * dz);
        int bearing = Math.floorMod((int) Math.round(Math.toDegrees(Math.atan2(-dx, dz))) + 180, 360);  // compass heading
        int elevation = (int) Math.round(Math.toDegrees(Math.atan2(v.y, v.horizontalDistance())));
        float tof = com.titancombat.entity.BaseTitanEntity.shellFlightTicks(range) / 20.0F;
        textRight(g, font, net.minecraft.client.resources.language.I18n.get("hud.titancombat.artillery_solution",
                (int) range, bearing, elevation, String.format("%.1f", tof)), xr, y - 10, AMBER, 0.9F, false);
        textRight(g, font, net.minecraft.client.resources.language.I18n.get("hud.titancombat.artillery_target", t.getX(), t.getY(), t.getZ()),
                xr, y - 20, AMBER, 0.9F, false);
    }

    // =================================================================== reticle
    private static void drawReticle(GuiGraphics g, Font font, int cx, int cy, float now, BaseMechEntity mech) {
        if (alpha <= 0.01F) return;
        PoseStack pose = g.pose();

        float bloom = clamp01(1.0F - (now - fireTick) / 7.0F);
        if (lastFiring) bloom = Math.max(bloom, 0.45F);

        // weapon raise / spin-up: reticle opens wide and closes in as the arm comes up
        float raiseP = 1.0F;
        if (activeWeapon != null && weaponRaised && fireTick < raiseStartTick) {
            raiseP = clamp01((now - raiseStartTick) / Math.max(1.0F, activeWeapon.getRaiseTicks()));
        }
        boolean raising = raiseP < 1.0F && !weaponLowered;
        float open = 1.0F - smooth(raiseP);
        float s = 1.0F + 0.3F * bloom + 0.8F * open;
        float baseAlpha = weaponLowered ? 0.25F : 0.92F * (0.45F + 0.55F * raiseP);
        if (reloadTicksLeft > 0) baseAlpha *= 0.55F;
        int color = weaponLowered ? DIM : (targetHostile ? RED : ICE);
        int idx = reticleIndex;
        int u = (idx % 4) * 64;
        int v = (idx / 4) * 64;

        pose.pushPose();
        pose.translate(cx, cy, 0.0F);
        pose.scale(s, s, 1.0F);
        tex(g, RETICLES, -16, -16, 32, 32, u, v, 64, 64, 256, 256, color, baseAlpha);
        pose.popPose();

        if (raising) {
            pose.pushPose();
            pose.translate(cx + 0.5F, cy + 0.5F, 0.0F);
            rotate(pose, now * 0.35F);
            for (int i = 0; i < 3; i++) {
                rect(g, -1, -25, 1, -20, CYAN, 0.85F);
                rotate(pose, Mth.TWO_PI / 3.0F);
            }
            pose.popPose();
            textCenter(g, font, raisingText, cx, cy + 30, CYAN, 0.6F + 0.4F * Mth.sin(now * 0.6F), true);
        }
        if (weaponLowered) return;

        // core ready halo
        if (mech.getCoreCharge() >= 100.0F && !mech.isOverdriveActive()) {
            float p = (now % 30.0F) / 30.0F;
            pose.pushPose();
            pose.translate(cx, cy, 0.0F);
            float rs = 1.0F + p * 0.6F;
            pose.scale(rs, rs, 1.0F);
            tex(g, RETICLES, -16, -16, 32, 32, 128, 128, 64, 64, 256, 256, CYAN, 0.45F * (1.0F - p));
            pose.popPose();
        }

        if (targetHostile) {
            float lp = smooth((now - lockTick) / 6.0F);
            pose.pushPose();
            pose.translate(cx, cy, 0.0F);
            if (weaponChassis == TitanClass.TONE) {
                float ls = 2.2F - 0.9F * lp;
                pose.scale(ls, ls, 1.0F);
                rotate(pose, (1.0F - lp) * Mth.HALF_PI);
                tex(g, RETICLES, -16, -16, 32, 32, 192, 0, 64, 64, 256, 256, RED, 0.5F + 0.5F * lp);
            } else {
                float ls = 1.8F - 0.8F * lp;
                pose.scale(ls, ls, 1.0F);
                tex(g, RETICLES, -16, -16, 32, 32, 64, 128, 64, 64, 256, 256, RED, 0.4F + 0.5F * lp);
            }
            pose.popPose();
            textCenter(g, font, targetLabel, cx, cy + 24, RED, 0.9F, true);
        }

        float sinceHit = now - hitMarkerTick;
        if (sinceHit < 8.0F) {
            tex(g, RETICLES, cx - 16, cy - 16, 32, 32, 0, 128, 64, 64, 256, 256, WHITE, 1.0F - sinceHit / 8.0F);
        }

        if (weaponChassis == TitanClass.NORTHSTAR || weaponChassis == TitanClass.SCORCH) {
            text(g, font, rangeText, cx + 20, cy + 4, targetHostile ? RED : ICE, 0.75F, false);
        }
    }

    // =================================================================== alerts
    private static void drawCritical(GuiGraphics g, Font font, int cx, int cy, float now, boolean doomed) {
        boolean on = (int) (now / 6.0F) % 2 == 0;
        String head = doomed ? "DOOMED" : "HULL CRITICAL";
        textScaled(g, font, head, cx, cy + 38, 1.25F, 0.5F, RED, on ? 1.0F : 0.55F, true);
        int w = font.width(ejectPrompt);
        int bx = cx - w / 2 - 6;
        int by = cy + 52;
        rect(g, bx, by, bx + w + 12, by + 13, RED, 0.22F);
        frame(g, bx, by, bx + w + 12, by + 13, RED, 0.85F);
        text(g, font, ejectPrompt, cx - w / 2, by + 3, WHITE, 1.0F, false);
    }

    private static void drawReactorDepletedWarning(GuiGraphics g, Font font, int cx, int cy, float now) {
        float pulse = 0.6F + 0.4F * Mth.sin(now * 0.35F);
        int y = cy + 42;
        String warn = "⚡ REACTOR DEPLETED - INSERT BATTERY ⚡";
        int w = font.width(warn);
        rect(g, cx - w / 2 - 8, y - 3, cx + w / 2 + 8, y + 12, BLACK, 0.65F);
        frame(g, cx - w / 2 - 8, y - 3, cx + w / 2 + 8, y + 12, RED, pulse);
        textCenter(g, font, warn, cx, y, RED, pulse, true);
    }

    private static void drawParked(GuiGraphics g, Font font, int cx, int cy, float now, boolean sitting,
                                   float sinceSit, boolean critical) {
        int y = critical ? cy + 72 : cy + 30;
        if (sinceSit < 16.0F) {
            String s = sitting ? "SYSTEMS STANDBY" : "SYSTEMS ONLINE";
            float a = 1.0F - smooth((sinceSit - 8.0F) / 8.0F);
            textCenter(g, font, s, cx, y - 14, sitting ? AMBER : CYAN, a, true);
        }
        if (!sitting) return;
        int w = font.width(parkedText);
        int bx = cx - w / 2 - 6;
        rect(g, bx, y - 2, bx + w + 12, y + 10, BLACK, 0.4F);
        corners(g, bx, y - 2, bx + w + 12, y + 10, 4, GREEN, 0.9F);
        text(g, font, parkedText, cx - w / 2, y, GREEN, 0.9F, false);
    }

    private static void drawHints(GuiGraphics g, Font font, int W, int H, float t) {
        float start = bootCinematic ? 52.0F : 0.0F;
        float end = bootCinematic ? HINT_END : HINT_END - 52.0F;
        if (t < start || t > end) return;
        alpha = smooth((t - start) / 8.0F) * (1.0F - smooth((t - (end - 25.0F)) / 25.0F));
        if (alpha <= 0.01F) return;
        int xr = W - 16;
        int y = H / 2 - 62;
        for (int i = 0; i < HINT_KEYS.length; i++) {
            float la = smooth((t - start - i * 1.5F) / 6.0F);
            String label = HINT_LABELS[i];
            String key = HINT_KEYS[i];
            int lw = font.width(label);
            int kw = font.width(key);
            int kx = xr - lw - kw - 12;
            rect(g, kx - 3, y - 1, kx + kw + 3, y + 9, CYAN, 0.18F * la);
            frame(g, kx - 3, y - 1, kx + kw + 3, y + 9, CYAN, 0.6F * la);
            text(g, font, key, kx, y, WHITE, la, false);
            text(g, font, label, xr - lw, y, ICE, 0.75F * la, false);
            y += 11;
        }
        alpha = 1.0F;
    }

    // =================================================================== boot cinematic
    private static void drawBoot(GuiGraphics g, Font font, int W, int H, float t) {
        alpha = 1.0F;

        // dark cockpit, then the visor "opens"
        rect(g, 0, 0, W, H, 0x02060A, 0.85F * (1.0F - smooth((t - 8.0F) / 34.0F)));
        float open = smooth((t - 2.0F) / 14.0F);
        int bar = (int) ((H / 2.0F) * (1.0F - open));
        if (bar > 0) {
            rect(g, 0, 0, W, bar, BLACK, 1.0F);
            rect(g, 0, H - bar, W, H, BLACK, 1.0F);
            rect(g, 0, bar, W, bar + 1, CYAN, 0.6F);
            rect(g, 0, H - bar - 1, W, H - bar, CYAN, 0.6F);
        }

        // scanlines + rolling band
        float sl = 0.09F * (1.0F - smooth((t - 34.0F) / 16.0F));
        if (sl > 0.005F) {
            for (int y = 0; y < H; y += 3) rect(g, 0, y, W, y + 1, CYAN, sl);
            int band = (int) ((t * 9.0F) % (H + 20)) - 10;
            rect(g, 0, band, W, band + 6, CYAN, sl * 0.9F);
        }

        float ta = 1.0F - smooth((t - 50.0F) / 9.0F);
        if (ta <= 0.01F) return;
        alpha = ta * bootFlicker(t);
        int lx = Math.max(20, W / 2 - 104);
        int ly = H / 2 - 58;
        int jitter = t < 22.0F && noise((int) (t * 2.0F)) > 0.8F ? 2 : 0;
        lx += jitter;

        typeLine(g, font, BOOT_HEADER, lx, ly, 4.0F, t, DIM, 1.0F);
        typeLine(g, font, BOOT_LINK, lx, ly + 13, 8.0F, t, CYAN, 1.5F);
        typeLine(g, font, bootChassisLine, lx, ly + 30, 14.0F, t, WHITE, 1.0F);
        typeLine(g, font, bootPilotLine, lx, ly + 40, 18.0F, t, WHITE, 1.0F);

        for (int i = 0; i < CHECK_LABELS.length; i++) {
            float st = 22.0F + i * 3.0F;
            if (t < st) break;
            int y = ly + 56 + i * 10;
            typeLine(g, font, CHECK_LABELS[i], lx + 8, y, st, t, ICE, 1.0F);
            for (int d = 0; d < 14; d++) rect(g, lx + 100 + d * 4, y + 6, lx + 101 + d * 4, y + 7, DIM, 0.5F);
            boolean ok = t >= st + 7.0F;
            if (ok) {
                text(g, font, "OK", lx + 164, y, GREEN, 1.0F, false);
            } else if ((int) (t * 2.0F) % 2 == 0) {
                text(g, font, "..", lx + 164, y, AMBER, 1.0F, false);
            }
        }

        // sync bar
        int sy = ly + 100;
        float sync = smooth((t - 8.0F) / 32.0F);
        text(g, font, BOOT_SYNC, lx, sy, DIM, 0.8F, false);
        slant(g, lx + 28, sy + 2, 150, 4, 0.6F, CYAN, 0.18F);
        slant(g, lx + 28, sy + 2, 150 * sync, 4, 0.6F, CYAN, 0.9F);
        text(g, font, PCT[(int) (sync * 100.0F)], lx + 186, sy, WHITE, 0.9F, false);

        if (t >= 38.0F) {
            float pa = smooth((t - 38.0F) / 5.0F);
            textScaled(g, font, BOOT_PROTOCOL, W / 2.0F, ly + 118, 1.0F, 0.5F, CYAN, pa, true);
        }
        alpha = 1.0F;
    }

    /** Typewriter reveal using a scissor rect (no substring allocation). */
    private static void typeLine(GuiGraphics g, Font font, String s, int x, int y, float start, float t,
                                 int rgb, float scale) {
        if (t < start) return;
        int full = (int) Math.ceil(font.width(s) * scale);
        int shown = Math.min(full, (int) ((t - start) * 18.0F * scale));
        if (shown <= 0) return;
        int h = (int) Math.ceil(9 * scale);
        g.enableScissor(x - 1, y - 1, x + shown, y + h);
        if (scale == 1.0F) {
            text(g, font, s, x, y, rgb, 1.0F, false);
        } else {
            textScaled(g, font, s, x, y, scale, 0.0F, rgb, 1.0F, false);
        }
        g.disableScissor();
        if (shown < full) {
            rect(g, x + shown, y, x + shown + (int) (5 * scale), y + h - 1, rgb, 0.8F); // block cursor
        }
    }
}
