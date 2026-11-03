package com.titancombat.client;

import com.mojang.blaze3d.platform.NativeImage;
import com.titancombat.TitanCombatMod;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.resources.ResourceLocation;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * Builds camouflaged copies of a vehicle texture on first use: only the painted hull texels (light, unsaturated)
 * take the pattern, so glass, tyres, hazard stripes and markings stay as they were, and panel lines/grime survive
 * because the camo colour is scaled by each texel's own brightness.
 */
public final class CamoTextures {
    /** Index matches BaseTransportVehicleEntity camo id; 0 = factory paint. */
    public static final String[] NAMES = {"Factory", "Woodland", "Desert", "Arctic", "Urban"};
    private static final int[][][] PALETTES = {
            {},
            {{74, 86, 52}, {44, 54, 34}, {98, 84, 58}, {24, 26, 22}},      // woodland
            {{196, 172, 128}, {168, 136, 92}, {214, 196, 160}, {130, 104, 72}}, // desert
            {{236, 238, 240}, {200, 206, 212}, {150, 158, 166}, {236, 238, 240}}, // arctic
            {{120, 124, 130}, {80, 84, 90}, {168, 170, 174}, {44, 46, 50}},   // urban
    };
    private static final Map<String, ResourceLocation> CACHE = new HashMap<>();

    private CamoTextures() {}

    public static ResourceLocation get(ResourceLocation base, int camo) {
        if (camo <= 0 || camo >= PALETTES.length) return base;
        String key = base.getPath() + "#" + camo;
        ResourceLocation cached = CACHE.get(key);
        if (cached != null) return cached;
        ResourceLocation out = base; // fall back to factory paint if anything goes wrong
        try (InputStream in = Minecraft.getInstance().getResourceManager().open(base)) {
            NativeImage img = NativeImage.read(in);
            paint(img, PALETTES[camo], camo);
            out = new ResourceLocation(TitanCombatMod.MODID, "camo/" + base.getPath().replace('/', '_').replace(".png", "") + "_" + camo);
            Minecraft.getInstance().getTextureManager().register(out, new DynamicTexture(img));
        } catch (Exception e) {
            TitanCombatMod.LOGGER.warn("Camo texture failed for {}: {}", base, e.toString());
        }
        CACHE.put(key, out);
        return out;
    }

    private static void paint(NativeImage img, int[][] pal, int seed) {
        int w = img.getWidth(), h = img.getHeight();
        float blob = w / 20.0F; // blob size scales with texture resolution
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                int abgr = img.getPixelRGBA(x, y); // NativeImage stores ABGR
                int a = (abgr >>> 24) & 0xFF, b = (abgr >> 16) & 0xFF, g = (abgr >> 8) & 0xFF, r = abgr & 0xFF;
                int max = Math.max(r, Math.max(g, b)), min = Math.min(r, Math.min(g, b));
                if (a < 250 || max - min > 40 || max < 85) continue; // not hull paint
                float lum = (r * 0.3F + g * 0.59F + b * 0.11F) / 185.0F; // ~1 on the light factory grey
                float n = noise(x / blob, y / blob, seed) * 0.65F + noise(x / (blob * 0.45F), y / (blob * 0.45F), seed + 7) * 0.35F;
                int[] c = pal[Math.min(pal.length - 1, (int) (n * pal.length))];
                img.setPixelRGBA(x, y, (a << 24) | (clamp(c[2] * lum) << 16) | (clamp(c[1] * lum) << 8) | clamp(c[0] * lum));
            }
        }
    }

    private static int clamp(float v) {
        return Math.max(0, Math.min(255, (int) v));
    }

    /** Smooth value noise in [0,1). */
    static float noise(float x, float y, int seed) {
        int xi = (int) Math.floor(x), yi = (int) Math.floor(y);
        float fx = x - xi, fy = y - yi;
        fx = fx * fx * (3 - 2 * fx);
        fy = fy * fy * (3 - 2 * fy);
        float a = hash(xi, yi, seed), b = hash(xi + 1, yi, seed), c = hash(xi, yi + 1, seed), d = hash(xi + 1, yi + 1, seed);
        float v = a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy;
        return Math.min(0.9999F, Math.max(0.0F, v));
    }

    private static float hash(int x, int y, int seed) {
        int h = x * 374761393 + y * 668265263 + seed * 982451653;
        h = (h ^ (h >>> 13)) * 1274126177;
        return ((h ^ (h >>> 16)) & 0xFFFF) / 65536.0F;
    }
}
