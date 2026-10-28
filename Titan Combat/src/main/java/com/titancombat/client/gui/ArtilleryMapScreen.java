package com.titancombat.client.gui;

import com.mojang.blaze3d.platform.NativeImage;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.Howitzer;
import com.titancombat.network.ArtilleryTargetC2SPacket;
import com.titancombat.network.ModNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.texture.DynamicTexture;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.MapColor;

/**
 * Howitzer tactical map: a blue top-down plot of the loaded terrain around the titan (north up). Left-click a
 * point inside the range rings to designate the target, right-click to designate and fire once the gun is
 * laid; unloaded ground is dark and can't be picked
 * (the world hasn't generated or loaded it, so there is nothing to aim at). The server re-checks range.
 */
public class ArtilleryMapScreen extends Screen {
    /** World radius shown on the map, a little past the howitzer's maximum range. */
    private static final int RADIUS = Howitzer.MAX_RANGE + 16;
    private static final int BLOCKS_PER_PIXEL = 2;
    private static final int IMAGE = RADIUS * 2 / BLOCKS_PER_PIXEL;
    private static final ResourceLocation MAP = new ResourceLocation(TitanCombatMod.MODID, "artillery_map");
    private static final int CYAN = 0x6FE3FF, DIM = 0x3A7A90, RED = 0xFF5A4A, AMBER = 0xFFB000, GREEN = 0x7CFF9A;

    private final BaseTitanEntity titan;
    private final double originX, originZ;  // map centre (titan position when opened)
    private final boolean[] loaded = new boolean[IMAGE * IMAGE];
    private DynamicTexture texture;
    private int mapX, mapY, mapSize;

    public ArtilleryMapScreen(BaseTitanEntity titan) {
        super(Component.translatable("gui.titancombat.artillery_map"));
        this.titan = titan;
        this.originX = titan.getX();
        this.originZ = titan.getZ();
    }

    @Override
    protected void init() {
        mapSize = Math.min(this.width - 40, this.height - 100);
        mapX = (this.width - mapSize) / 2;
        mapY = 30;
        if (texture == null) {
            texture = new DynamicTexture(plot(Minecraft.getInstance().level));
            Minecraft.getInstance().getTextureManager().register(MAP, texture);
        }
        addRenderableWidget(Button.builder(Component.translatable("gui.titancombat.artillery_map.coords"),
                b -> Minecraft.getInstance().setScreen(new ArtilleryFireControlScreen(titan)))
                .bounds(this.width / 2 - 104, mapY + mapSize + 16, 100, 18).build());
        addRenderableWidget(Button.builder(Component.translatable("gui.done"), b -> onClose())
                .bounds(this.width / 2 + 4, mapY + mapSize + 16, 100, 18).build());
    }

    /** Terrain from the client's loaded chunks, shaded into a blue tactical palette with 8-block contours. */
    private NativeImage plot(Level level) {
        NativeImage img = new NativeImage(IMAGE, IMAGE, false);
        int[] heights = new int[IMAGE * IMAGE];
        for (int py = 0; py < IMAGE; py++) {
            for (int px = 0; px < IMAGE; px++) {
                int x = Mth.floor(originX) - RADIUS + px * BLOCKS_PER_PIXEL;
                int z = Mth.floor(originZ) - RADIUS + py * BLOCKS_PER_PIXEL;
                int i = py * IMAGE + px;
                if (!level.hasChunk(x >> 4, z >> 4)) {
                    img.setPixelRGBA(px, py, abgr(6, 14, 22));
                    continue;
                }
                loaded[i] = true;
                // Clients only receive the WORLD_SURFACE and MOTION_BLOCKING heightmaps (NO_LEAVES reads flat).
                int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, x, z);
                heights[i] = top;
                BlockPos pos = new BlockPos(x, top - 1, z);
                MapColor color = level.getBlockState(pos).getMapColor(level, pos);
                int rgb = color.col;
                float lum = (0.3F * (rgb >> 16 & 255) + 0.59F * (rgb >> 8 & 255) + 0.11F * (rgb & 255)) / 255.0F;
                float shade = 0.35F + 0.65F * lum;
                if (color == MapColor.WATER) shade = 0.18F;
                img.setPixelRGBA(px, py, abgr((int) (12 + 40 * shade), (int) (40 + 120 * shade), (int) (70 + 150 * shade)));
            }
        }
        for (int py = 1; py < IMAGE; py++) {
            for (int px = 1; px < IMAGE; px++) {
                int i = py * IMAGE + px;
                if (!loaded[i] || !loaded[i - 1] || !loaded[i - IMAGE]) continue;
                boolean contour = heights[i] >> 3 != heights[i - 1] >> 3 || heights[i] >> 3 != heights[i - IMAGE] >> 3;
                boolean grid = (Mth.floor(originX) - RADIUS + px * BLOCKS_PER_PIXEL) % 32 == 0
                        || (Mth.floor(originZ) - RADIUS + py * BLOCKS_PER_PIXEL) % 32 == 0;
                if (contour) img.setPixelRGBA(px, py, abgr(110, 230, 255));
                else if (grid) img.setPixelRGBA(px, py, abgr(30, 90, 120));
            }
        }
        return img;
    }

    private static int abgr(int r, int g, int b) {
        return 0xFF000000 | Mth.clamp(b, 0, 255) << 16 | Mth.clamp(g, 0, 255) << 8 | Mth.clamp(r, 0, 255);
    }

    private double worldX(double mx) { return originX - RADIUS + (mx - mapX) / mapSize * RADIUS * 2; }
    private double worldZ(double my) { return originZ - RADIUS + (my - mapY) / mapSize * RADIUS * 2; }
    private int screenX(double wx) { return mapX + (int) Math.round((wx - originX + RADIUS) / (RADIUS * 2) * mapSize); }
    private int screenY(double wz) { return mapY + (int) Math.round((wz - originZ + RADIUS) / (RADIUS * 2) * mapSize); }

    private boolean onMap(double mx, double my) {
        return mx >= mapX && my >= mapY && mx < mapX + mapSize && my < mapY + mapSize;
    }

    private boolean isLoaded(double wx, double wz) {
        int px = Mth.floor((wx - Mth.floor(originX) + RADIUS) / BLOCKS_PER_PIXEL);
        int py = Mth.floor((wz - Mth.floor(originZ) + RADIUS) / BLOCKS_PER_PIXEL);
        return px >= 0 && py >= 0 && px < IMAGE && py < IMAGE && loaded[py * IMAGE + px];
    }

    private double rangeTo(double wx, double wz) {
        return Math.sqrt(Mth.square(wx - titan.getX()) + Mth.square(wz - titan.getZ()));
    }

    @Override
    public boolean mouseClicked(double mx, double my, int button) {
        // Left click designates the target; right click designates it and fires as soon as the gun is laid.
        if ((button == 0 || button == 1) && onMap(mx, my)) {
            double wx = worldX(mx), wz = worldZ(my), range = rangeTo(wx, wz);
            if (isLoaded(wx, wz) && range >= Howitzer.MIN_RANGE && range <= Howitzer.MAX_RANGE) {
                ModNetworking.sendToServer(new ArtilleryTargetC2SPacket(Mth.floor(wx), false, 0, Mth.floor(wz), button == 1));
                Minecraft.getInstance().getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(
                        net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK, 1.6F));
            }
            return true;
        }
        return super.mouseClicked(mx, my, button);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        g.fill(0, 0, this.width, this.height, 0xE0040A12);
        g.drawCenteredString(this.font, this.title, this.width / 2, 10, CYAN);
        g.blit(MAP, mapX, mapY, mapSize, mapSize, 0, 0, IMAGE, IMAGE, IMAGE, IMAGE);
        frame(g, mapX - 1, mapY - 1, mapSize + 2, CYAN);

        int cx = screenX(titan.getX()), cy = screenY(titan.getZ());
        ring(g, cx, cy, Howitzer.MAX_RANGE, CYAN);
        ring(g, cx, cy, Howitzer.MIN_RANGE, RED);
        // Titan: dot and heading tick
        g.fill(cx - 2, cy - 2, cx + 3, cy + 3, 0xFFFFFFFF);
        float yaw = titan.getYRot() * Mth.DEG_TO_RAD;
        for (int k = 3; k < 12; k++) {
            int hx = cx + Math.round(-Mth.sin(yaw) * k), hy = cy + Math.round(Mth.cos(yaw) * k);
            g.fill(hx, hy, hx + 1, hy + 1, 0xFFFFFFFF);
        }
        g.drawString(this.font, "N", mapX + mapSize / 2 - 2, mapY + 3, CYAN);

        BlockPos t = titan.getArtilleryTarget();
        if (t != null) {
            int tx = screenX(t.getX() + 0.5D), ty = screenY(t.getZ() + 0.5D);
            int col = titan.getArtilleryLaying() > 0 ? AMBER : GREEN;  // amber while the gun is still laying
            g.fill(tx - 5, ty, tx + 6, ty + 1, 0xFF000000 | col);
            g.fill(tx, ty - 5, tx + 1, ty + 6, 0xFF000000 | col);
            frame(g, tx - 3, ty - 3, 7, col);
        }

        if (onMap(mouseX, mouseY)) {
            double wx = worldX(mouseX), wz = worldZ(mouseY), range = rangeTo(wx, wz);
            boolean loadedHere = isLoaded(wx, wz);
            boolean inRange = range >= Howitzer.MIN_RANGE && range <= Howitzer.MAX_RANGE;
            int col = loadedHere && inRange ? GREEN : RED;
            g.fill(mouseX - 6, mouseY, mouseX + 7, mouseY + 1, 0xA0000000 | col);
            g.fill(mouseX, mouseY - 6, mouseX + 1, mouseY + 7, 0xA0000000 | col);
            String info = Mth.floor(wx) + ", " + Mth.floor(wz) + "  " + (int) range + " m";
            if (!loadedHere) info += "  " + Component.translatable("gui.titancombat.artillery_map.no_data").getString();
            else if (!inRange) info += "  " + Component.translatable("gui.titancombat.artillery_map.out_of_range").getString();
            g.drawString(this.font, info, mouseX + 8, mouseY + 8, col);
        }
        String status = titan.getHowitzerReload() > 0 ? "gui.titancombat.artillery_map.reloading"
                : titan.getArtilleryLaying() > 0 ? "gui.titancombat.artillery_map.laying"
                : t != null ? "gui.titancombat.artillery_map.locked" : "gui.titancombat.artillery_map.no_target";
        g.drawCenteredString(this.font, Component.translatable(status, titan.getHowitzerRounds(), Howitzer.ROUNDS_PER_RACK),
                this.width / 2, mapY + mapSize + 4, titan.getArtilleryLaying() > 0 || titan.getHowitzerReload() > 0 ? AMBER : GREEN);
        g.drawCenteredString(this.font, Component.translatable("gui.titancombat.artillery_map.hint"), this.width / 2, mapY + mapSize + 38, DIM);
        g.drawCenteredString(this.font, Component.translatable("gui.titancombat.artillery_map.hint2",
                Howitzer.MIN_RANGE, Howitzer.MAX_RANGE), this.width / 2, mapY + mapSize + 48, DIM);
        super.render(g, mouseX, mouseY, partial);
    }

    private static void frame(GuiGraphics g, int x, int y, int size, int rgb) {
        int c = 0xFF000000 | rgb;
        g.fill(x, y, x + size, y + 1, c);
        g.fill(x, y + size - 1, x + size, y + size, c);
        g.fill(x, y, x + 1, y + size, c);
        g.fill(x + size - 1, y, x + size, y + size, c);
    }

    private void ring(GuiGraphics g, int cx, int cy, int worldRadius, int rgb) {
        float r = worldRadius / (float) (RADIUS * 2) * mapSize;
        int steps = Math.max(48, (int) (r * 4));
        for (int k = 0; k < steps; k++) {
            float a = k * Mth.TWO_PI / steps;
            int x = cx + Math.round(Mth.cos(a) * r), y = cy + Math.round(Mth.sin(a) * r);
            g.fill(x, y, x + 1, y + 1, 0xFF000000 | rgb);
        }
    }

    @Override
    public void removed() {
        if (texture != null) {
            Minecraft.getInstance().getTextureManager().release(MAP);
            texture = null;
        }
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
