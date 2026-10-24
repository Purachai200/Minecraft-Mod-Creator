package com.titancombat.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.resources.ResourceLocation;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

/**
 * Tiny allocation-free drawing helpers for the holographic cockpit HUD and the cockpit bay screen.
 * All colours are passed as 0xRRGGBB plus a separate alpha that is multiplied with {@link #alpha}.
 */
final class HudDraw {

    private HudDraw() {}

    /** Global alpha multiplier (used for boot fade-ins, power-down dimming, per-panel intros). */
    static float alpha = 1.0F;

    private static final Matrix4f SHEAR = new Matrix4f();
    private static final Quaternionf ROT = new Quaternionf();

    static int col(int rgb, float a) {
        a *= alpha;
        if (a <= 0.0F) return 0;
        if (a > 1.0F) a = 1.0F;
        return ((int) (a * 255.0F) << 24) | (rgb & 0xFFFFFF);
    }

    static void rect(GuiGraphics g, int x1, int y1, int x2, int y2, int rgb, float a) {
        int c = col(rgb, a);
        if ((c >>> 24) == 0) return;
        g.fill(x1, y1, x2, y2, c);
    }

    /**
     * Parallelogram leaning right ("/"): bottom edge spans x..x+w, top edge is shifted right by k*h.
     */
    static void slant(GuiGraphics g, float x, float y, float w, float h, float k, int rgb, float a) {
        int c = col(rgb, a);
        if ((c >>> 24) == 0 || w <= 0) return;
        PoseStack pose = g.pose();
        pose.pushPose();
        pose.translate(x + k * h, y, 0.0F);
        SHEAR.identity().m10(-k);
        pose.mulPoseMatrix(SHEAR);
        // fill() only takes ints: scale x so fractional widths stay smooth
        pose.scale(w / 64.0F, h / 64.0F, 1.0F);
        g.fill(0, 0, 64, 64, c);
        pose.popPose();
    }

    static void rotate(PoseStack pose, float radians) {
        ROT.rotationZ(radians);
        pose.mulPose(ROT);
    }

    static void text(GuiGraphics g, Font font, String s, int x, int y, int rgb, float a, boolean shadow) {
        int c = col(rgb, a);
        if ((c >>> 24) < 6) return; // the font renderer treats alpha < 4 as opaque
        g.drawString(font, s, x, y, c, shadow);
    }

    static void textRight(GuiGraphics g, Font font, String s, int xRight, int y, int rgb, float a, boolean shadow) {
        text(g, font, s, xRight - font.width(s), y, rgb, a, shadow);
    }

    static void textCenter(GuiGraphics g, Font font, String s, int cx, int y, int rgb, float a, boolean shadow) {
        text(g, font, s, cx - font.width(s) / 2, y, rgb, a, shadow);
    }

    /** align: 0 = left, 0.5 = centre, 1 = right. */
    static void textScaled(GuiGraphics g, Font font, String s, float x, float y, float scale, float align,
                           int rgb, float a, boolean shadow) {
        int c = col(rgb, a);
        if ((c >>> 24) < 6) return;
        PoseStack pose = g.pose();
        pose.pushPose();
        pose.translate(x, y, 0.0F);
        pose.scale(scale, scale, 1.0F);
        g.drawString(font, s, (int) (-font.width(s) * align), 0, c, shadow);
        pose.popPose();
    }

    /** Tinted blit of a white texture region. */
    static void tex(GuiGraphics g, ResourceLocation loc, int x, int y, int w, int h, float u, float v,
                    int uw, int vh, int tw, int th, int rgb, float a) {
        float aa = a * alpha;
        if (aa <= 0.01F) return;
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.setShaderColor(((rgb >> 16) & 0xFF) / 255.0F, ((rgb >> 8) & 0xFF) / 255.0F, (rgb & 0xFF) / 255.0F,
                Math.min(1.0F, aa));
        g.blit(loc, x, y, w, h, u, v, uw, vh, tw, th);
        RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 1.0F);
    }

    /** 1px rectangle outline. */
    static void frame(GuiGraphics g, int x1, int y1, int x2, int y2, int rgb, float a) {
        rect(g, x1, y1, x2, y1 + 1, rgb, a);
        rect(g, x1, y2 - 1, x2, y2, rgb, a);
        rect(g, x1, y1 + 1, x1 + 1, y2 - 1, rgb, a);
        rect(g, x2 - 1, y1 + 1, x2, y2 - 1, rgb, a);
    }

    /** Four L-shaped corner brackets around a rectangle. */
    static void corners(GuiGraphics g, int x1, int y1, int x2, int y2, int len, int rgb, float a) {
        rect(g, x1, y1, x1 + len, y1 + 1, rgb, a);
        rect(g, x1, y1, x1 + 1, y1 + len, rgb, a);
        rect(g, x2 - len, y1, x2, y1 + 1, rgb, a);
        rect(g, x2 - 1, y1, x2, y1 + len, rgb, a);
        rect(g, x1, y2 - 1, x1 + len, y2, rgb, a);
        rect(g, x1, y2 - len, x1 + 1, y2, rgb, a);
        rect(g, x2 - len, y2 - 1, x2, y2, rgb, a);
        rect(g, x2 - 1, y2 - len, x2, y2, rgb, a);
    }

    static float clamp01(float v) {
        return v < 0.0F ? 0.0F : (v > 1.0F ? 1.0F : v);
    }

    static float smooth(float v) {
        v = clamp01(v);
        return v * v * (3.0F - 2.0F * v);
    }

    /** Cheap deterministic hash noise in [0,1). */
    static float noise(int n) {
        n = (n << 13) ^ n;
        n = n * (n * n * 15731 + 789221) + 1376312589;
        return (n & 0x7FFFFFFF) / 2147483648.0F;
    }
}
