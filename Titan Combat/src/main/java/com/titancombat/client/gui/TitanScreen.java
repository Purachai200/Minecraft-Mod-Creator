package com.titancombat.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import com.titancombat.entity.TitanWeapon;
import com.titancombat.gui.TitanMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;

import java.util.Locale;

import static com.titancombat.client.gui.HudDraw.*;

/**
 * Titan "cockpit bay" screen: live 3D titan feed, system bars and framed slot groups
 * (reactor battery, munitions, cargo) above the pilot's inventory.
 * Panel chrome comes from {@code textures/gui/titan_bay.png} (tools/generate_hud_textures.py);
 * slot frames are drawn in code from the actual {@link Slot} positions so they always line up.
 */
public class TitanScreen extends AbstractContainerScreen<TitanMenu> {

    private static final ResourceLocation BAY_TEXTURE =
            new ResourceLocation(TitanCombatMod.MODID, "textures/gui/titan_bay.png");
    private static final ResourceLocation GHOST_BATTERY =
            new ResourceLocation(TitanCombatMod.MODID, "textures/item/titan_battery.png");
    private static final ResourceLocation GHOST_AMMO =
            new ResourceLocation(TitanCombatMod.MODID, "textures/item/titan_ammo.png");
    private static final ResourceLocation GHOST_WEAPON =
            new ResourceLocation(TitanCombatMod.MODID, "textures/item/weapon_mount.png");
    private static final ResourceLocation GHOST_FLIGHT =
            new ResourceLocation(TitanCombatMod.MODID, "textures/item/flight_module_rocket_jetpack.png");

    private static final int W = 300;
    private static final int H = 222;

    // viewport (inclusive border coords, see generator)
    private static final int VP_X0 = 7, VP_Y0 = 21, VP_X1 = 79, VP_Y1 = 124;

    // group boxes
    private static final int REACTOR_X0 = 83, REACTOR_Y0 = 54, REACTOR_X1 = 161, REACTOR_Y1 = 80;
    private static final int MUNI_X0 = 83, MUNI_Y0 = 84, MUNI_X1 = 161, MUNI_Y1 = 124;
    private static final int CARGO_X0 = 165, CARGO_Y0 = 54, CARGO_X1 = 223, CARGO_Y1 = 124;
    private static final int WEAPON_X0 = 227, WEAPON_Y0 = 54, WEAPON_X1 = 293, WEAPON_Y1 = 124;
    private static final int BAR_SEGS = 26;

    private static final int CYAN = 0x00E5FF;
    private static final int ICE = 0xD8FBFF;
    private static final int DIM = 0x7FB8C8;
    private static final int AMBER = 0xFFB300;
    private static final int RED = 0xFF2A44;
    private static final int GREEN = 0x00E676;
    private static final int SHIELD = 0x40C4FF;
    private static final int GOLD = 0xFFD54F;

    private final Component lblReactor = Component.translatable("gui.titancombat.bay.reactor");
    private final Component lblMunitions = Component.translatable("gui.titancombat.bay.munitions");
    private final Component lblCargo = Component.translatable("gui.titancombat.bay.cargo");
    private final Component lblPilot = Component.translatable("gui.titancombat.bay.pilot_inventory");
    private final Component lblOnline = Component.translatable("gui.titancombat.bay.reactor_online");
    private final Component lblNoCell = Component.translatable("gui.titancombat.bay.reactor_empty");
    private final Component lblWeapon = Component.translatable("gui.titancombat.bay.weapon");
    private final Component lblBay = Component.translatable("gui.titancombat.bay.title");

    private float openTicks;

    public TitanScreen(TitanMenu menu, Inventory playerInventory, Component title) {
        super(menu, playerInventory, title);
        this.imageWidth = W;
        this.imageHeight = H;
        this.inventoryLabelY = 131;
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.openTicks += this.minecraft.getDeltaFrameTime();
        this.renderBackground(guiGraphics);
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        this.renderTooltip(guiGraphics, mouseX, mouseY);
        BaseTitanEntity titan = this.menu.getTitan();
        if (this.hoveredSlot == null && titan != null) {
            int relX = mouseX - this.leftPos;
            int relY = mouseY - this.topPos;
            if (relX >= REACTOR_X0 && relX <= REACTOR_X0 + 54 && relY >= REACTOR_Y0 && relY <= REACTOR_Y1) {
                int curE = titan.getEnergy();
                int maxE = Math.max(1, titan.getMaxEnergy());
                int pct = Math.round((float) curE * 100.0F / (float) maxE);
                guiGraphics.renderTooltip(this.font, java.util.List.of(
                        Component.literal("§6[TITAN FUSION REACTOR]"),
                        Component.literal("§7Core Energy: §b" + String.format("%,d", curE) + " §7/ §b" + String.format("%,d", maxE) + " FE §7(" + pct + "%)"),
                        Component.literal(curE <= 0 ? "§c[DEPLETED] Insert battery to restore power" : "§a[ONLINE] Power distribution normal")
                ), java.util.Optional.empty(), mouseX, mouseY);
            }
        }
    }

    @Override
    protected void renderBg(GuiGraphics g, float partialTick, int mouseX, int mouseY) {
        HudDraw.alpha = 1.0F;
        int x = this.leftPos;
        int y = this.topPos;

        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        g.blit(BAY_TEXTURE, x, y, 0, 0, W, H, 512, 256);

        BaseTitanEntity titan = this.menu.getTitan();

        // ---------------------------------------------------------------- live 3D feed
        if (titan != null) {
            g.enableScissor(x + VP_X0 + 1, y + VP_Y0 + 1, x + VP_X1, y + VP_Y1);
            TitanClass tc = titan.getTitanClass();
            int scale = Math.max(6, Math.round(11.0F * 4.8F / tc.getHeight()));
            int ex = x + (VP_X0 + VP_X1) / 2 + 1;
            int ey = y + VP_Y1 - 8;
            // Force the titan model to draw even when the viewer is sitting inside it in first person.
            com.titancombat.client.renderer.TitanRenderer.forceDraw = true;
            try {
                InventoryScreen.renderEntityInInventoryFollowsMouse(g, ex, ey, scale,
                        (float) ex - mouseX, (float) (ey - 62) - mouseY, titan);
            } finally {
                com.titancombat.client.renderer.TitanRenderer.forceDraw = false;
            }
            g.disableScissor();
        }
        // feed overlay: scanline sweep + LIVE tag
        int sweep = (int) ((this.openTicks * 1.5F) % (VP_Y1 - VP_Y0 - 2));
        rect(g, x + VP_X0 + 1, y + VP_Y0 + 1 + sweep, x + VP_X1, y + VP_Y0 + 2 + sweep, CYAN, 0.12F);
        boolean blink = ((int) (this.openTicks / 10.0F)) % 2 == 0;
        rect(g, x + VP_X0 + 4, y + VP_Y0 + 4, x + VP_X0 + 7, y + VP_Y0 + 7, RED, blink ? 1.0F : 0.35F);

        // ---------------------------------------------------------------- system bars
        if (titan != null) {
            float maxHp = Math.max(1.0F, titan.getMaxHealth());
            float hp = clamp01(titan.getHealth() / maxHp);
            float sp = clamp01(titan.getShield() / Math.max(1.0F, titan.getMaxShield()));
            float core = clamp01(titan.getCoreCharge() / 100.0F);
            int hullColor = hp > 0.5F ? ICE : (hp > 0.25F ? AMBER : RED);
            segBar(g, x + 112, y + 24, hp, BAR_SEGS, hullColor);
            segBar(g, x + 112, y + 34, sp, BAR_SEGS, SHIELD);
            segBar(g, x + 112, y + 44, core, BAR_SEGS, core >= 1.0F ? GOLD : CYAN);
        } else {
            segBar(g, x + 112, y + 24, 0, BAR_SEGS, ICE);
            segBar(g, x + 112, y + 34, 0, BAR_SEGS, SHIELD);
            segBar(g, x + 112, y + 44, 0, BAR_SEGS, CYAN);
        }

        // ---------------------------------------------------------------- group boxes
        groupBox(g, x + REACTOR_X0, y + REACTOR_Y0, x + REACTOR_X1, y + REACTOR_Y1, AMBER);

        // Reactor energy mini-meter
        if (titan != null) {
            int curE = titan.getEnergy();
            int maxE = Math.max(1, titan.getMaxEnergy());
            float eFrac = clamp01((float) curE / (float) maxE);
            int barColor = curE <= 0 ? RED : (eFrac < 0.25F ? AMBER : CYAN);
            rect(g, x + REACTOR_X0 + 5, y + REACTOR_Y0 + 12, x + REACTOR_X0 + 53, y + REACTOR_Y0 + 16, 0x060A0F, 1.0F);
            frame(g, x + REACTOR_X0 + 5, y + REACTOR_Y0 + 12, x + REACTOR_X0 + 53, y + REACTOR_Y0 + 16, 0x1E3A46, 1.0F);
            int fill = Math.round(46.0F * eFrac);
            if (fill > 0) {
                rect(g, x + REACTOR_X0 + 6, y + REACTOR_Y0 + 13, x + REACTOR_X0 + 6 + fill, y + REACTOR_Y0 + 15, barColor, 0.95F);
            }
        }
        groupBox(g, x + MUNI_X0, y + MUNI_Y0, x + MUNI_X1, y + MUNI_Y1, CYAN);
        groupBox(g, x + CARGO_X0, y + CARGO_Y0, x + CARGO_X1, y + CARGO_Y1, DIM);
        groupBox(g, x + WEAPON_X0, y + WEAPON_Y0, x + WEAPON_X1, y + WEAPON_Y1, GOLD);

        // ---------------------------------------------------------------- slot frames (from real slot positions)
        for (int i = 0; i < this.menu.slots.size(); i++) {
            Slot slot = this.menu.slots.get(i);
            int accent;
            if (i == TitanMenu.BATTERY_SLOT) accent = AMBER;
            else if (i == TitanMenu.WEAPON_SLOT) accent = GOLD;
            else if (i == TitanMenu.FLIGHT_SLOT) accent = CYAN;
            else if (i == TitanMenu.AMMO_SLOT_1 || i == TitanMenu.AMMO_SLOT_2) accent = CYAN;
            else if (i < TitanMenu.CONTAINER_SIZE) accent = DIM;
            else if (i >= TitanMenu.CONTAINER_SIZE + 27) accent = CYAN; // hotbar
            else accent = 0x3E6A78;
            slotFrame(g, x + slot.x, y + slot.y, accent, i < TitanMenu.CONTAINER_SIZE + 27 && i >= TitanMenu.CONTAINER_SIZE);
        }

        // ghost icons for empty special slots
        Slot battery = this.menu.slots.get(TitanMenu.BATTERY_SLOT);
        if (!battery.hasItem()) {
            tex(g, GHOST_BATTERY, x + battery.x, y + battery.y, 16, 16, 0, 0, 16, 16, 16, 16, 0x9FB8C0, 0.28F);
        }
        for (int i = TitanMenu.AMMO_SLOT_1; i <= TitanMenu.AMMO_SLOT_2; i++) {
            Slot s = this.menu.slots.get(i);
            if (!s.hasItem()) {
                tex(g, GHOST_AMMO, x + s.x, y + s.y, 16, 16, 0, 0, 16, 16, 16, 16, 0x9FB8C0, 0.28F);
            }
        }

        Slot weaponSlot = this.menu.slots.get(TitanMenu.WEAPON_SLOT);
        if (!weaponSlot.hasItem()) {
            tex(g, GHOST_WEAPON, x + weaponSlot.x, y + weaponSlot.y, 16, 16, 0, 0, 16, 16, 16, 16, 0x9FB8C0, 0.28F);
        }

        Slot flightSlot = this.menu.slots.get(TitanMenu.FLIGHT_SLOT);
        if (!flightSlot.hasItem()) {
            tex(g, GHOST_FLIGHT, x + flightSlot.x, y + flightSlot.y, 16, 16, 0, 0, 16, 16, 16, 16, 0x9FB8C0, 0.28F);
        }

        // pilot hotbar marker
        rect(g, x + TitanMenu.INV_X - 1, y + TitanMenu.HOTBAR_Y - 3, x + TitanMenu.INV_X + 161, y + TitanMenu.HOTBAR_Y - 2, CYAN, 0.25F);

        RenderSystem.disableBlend();
    }

    private static void segBar(GuiGraphics g, int x, int y, float frac, int segs, int color) {
        for (int i = 0; i < segs; i++) {
            float sx = x + i * 6.0F;
            float f = clamp01((frac - (float) i / segs) * segs);
            slant(g, sx, y, 5, 5, 0.5F, CYAN, 0.12F);
            if (f > 0) slant(g, sx, y, 5 * f, 5, 0.5F, color, 0.95F);
        }
    }

    private static void groupBox(GuiGraphics g, int x0, int y0, int x1, int y1, int accent) {
        rect(g, x0, y0, x1, y1, 0x05090D, 0.55F);
        frame(g, x0, y0, x1, y1, 0x1E3A46, 1.0F);
        rect(g, x0, y0, x0 + 16, y0 + 1, accent, 0.95F);
        rect(g, x0, y0, x0 + 1, y0 + 6, accent, 0.95F);
        rect(g, x1 - 6, y1 - 1, x1, y1, accent, 0.7F);
        rect(g, x1 - 1, y1 - 6, x1, y1, accent, 0.7F);
    }

    private static void slotFrame(GuiGraphics g, int sx, int sy, int accent, boolean plain) {
        // 18x18 frame around the 16x16 item area
        rect(g, sx - 1, sy - 1, sx + 17, sy + 17, 0x2A4A56, 1.0F);
        rect(g, sx, sy, sx + 16, sy + 16, 0x060A0F, 1.0F);
        rect(g, sx, sy + 15, sx + 16, sy + 16, 0x0F1C24, 1.0F);
        if (!plain) {
            rect(g, sx - 1, sy - 1, sx + 3, sy, accent, 0.9F);
            rect(g, sx - 1, sy - 1, sx, sy + 3, accent, 0.9F);
            rect(g, sx + 13, sy + 16, sx + 17, sy + 17, accent, 0.9F);
            rect(g, sx + 16, sy + 13, sx + 17, sy + 17, accent, 0.9F);
        }
    }

    @Override
    protected void renderLabels(GuiGraphics g, int mouseX, int mouseY) {
        HudDraw.alpha = 1.0F;
        BaseTitanEntity titan = this.menu.getTitan();

        // header
        String cls = titan != null ? titan.getTitanClass().getDisplayName().toUpperCase(Locale.ROOT) : "TITAN";
        g.drawString(this.font, cls, 12, 5, 0xFF00E5FF, false);
        int cw = this.font.width(cls);
        g.drawString(this.font, "//", 12 + cw + 4, 5, 0xFF3E6A78, false);
        g.drawString(this.font, lblBay, 12 + cw + 16, 5, 0xFFD8FBFF, false);

        if (titan != null) {
            String owner = titan.getOwnerName();
            if (owner.isEmpty()) owner = "---";
            int maxW = W - 12 - (12 + cw + 16 + this.font.width(lblBay)) - 30;
            String o = this.font.plainSubstrByWidth(owner.toUpperCase(Locale.ROOT), Math.max(20, maxW));
            int ow = this.font.width(o);
            g.drawString(this.font, o, W - 10 - ow, 5, 0xFFFFFFFF, false);
            g.drawString(this.font, "PILOT", W - 10 - ow - 30, 5, 0xFF7FB8C8, false);

        }
        g.drawString(this.font, "LIVE", VP_X0 + 10, VP_Y0 + 4, 0xCCFF2A44, false);

        // bar labels + values
        g.drawString(this.font, "HULL", 86, 23, 0xFF7FB8C8, false);
        g.drawString(this.font, "SHLD", 86, 33, 0xFF7FB8C8, false);
        g.drawString(this.font, "CORE", 86, 43, 0xFF7FB8C8, false);
        if (titan != null) {
            rightText(g, CockpitHudState.num(Mth.ceil(titan.getHealth())), 292, 23, 0xFFD8FBFF);
            rightText(g, CockpitHudState.num(Mth.ceil(titan.getShield())), 292, 33, 0xFF40C4FF);
            int core = (int) titan.getCoreCharge();
            rightText(g, CockpitHudState.PCT[Mth.clamp(core, 0, 100)], 292, 43, core >= 100 ? 0xFFFFD54F : 0xFF00E5FF);
        }

        // reactor group
        g.drawString(this.font, lblReactor, REACTOR_X0 + 5, REACTOR_Y0 + 3, 0xFFFFB300, false);
        if (titan != null) {
            int curE = titan.getEnergy();
            int maxE = Math.max(1, titan.getMaxEnergy());
            int pct = Math.round((float) curE * 100.0F / (float) maxE);
            int pwrColor = curE <= 0 ? 0xFFFF2A44 : (pct < 30 ? 0xFFFFB300 : 0xFF00E5FF);
            rightText(g, pct + "%", REACTOR_X0 + 53, REACTOR_Y0 + 3, pwrColor);
        }
        boolean hasCell = this.menu.slots.get(TitanMenu.BATTERY_SLOT).hasItem();
        boolean blink = ((int) (this.openTicks / 8.0F)) % 2 == 0;
        g.drawString(this.font, hasCell ? lblOnline : lblNoCell, REACTOR_X0 + 5, REACTOR_Y0 + 17,
                hasCell ? 0xFF00E676 : (blink ? 0xFFFFB300 : 0x88FFB300), false);

        // munitions group
        g.drawString(this.font, lblMunitions, MUNI_X0 + 5, MUNI_Y0 + 4, 0xFF00E5FF, false);
        TitanWeapon weapon = titan != null ? titan.getActiveWeapon() : null;
        int mags = 0;
        if (weapon != null) {
            for (int i = TitanMenu.AMMO_SLOT_1; i <= TitanMenu.AMMO_SLOT_2; i++) {
                mags += CockpitHudState.magazinesIn(this.menu.slots.get(i).getItem(), weapon);
            }
        }
        g.drawString(this.font, "x" + mags, 88, 90, mags > 0 ? 0xFFFFFFFF : 0xFFFF2A44, false);
        g.drawString(this.font, "MAGS", 103, 90, 0xFF7FB8C8, false);
        g.drawString(this.font, "EQUIP", 133, 90, 0xFF00E5FF, false);

        // weapon group
        g.drawString(this.font, lblWeapon, WEAPON_X0 + 5, WEAPON_Y0 + 4, 0xFFFFD54F, false);
        if (weapon != null && titan != null) {
            int mag = titan.getMagazine();
            int size = weapon.getMagazineSize();
            int sx = TitanMenu.WEAPON_X + 21;
            int magColor = mag <= 0 ? 0xFFFF2A44 : (mag < size * 0.25F ? 0xFFFFB300 : 0xFFFFFFFF);
            g.drawString(this.font, CockpitHudState.num(mag), sx, TitanMenu.WEAPON_Y + 1, magColor, false);
            g.drawString(this.font, "/" + size, sx, TitanMenu.WEAPON_Y + 10, 0xFF7FB8C8, false);

            boolean factory = !this.menu.slots.get(TitanMenu.WEAPON_SLOT).hasItem();
            String name = Component.translatable(weapon.getTranslationKey()).getString().toUpperCase(Locale.ROOT);
            int ny = TitanMenu.WEAPON_Y + 21;
            int maxW = WEAPON_X1 - WEAPON_X0 - 9;
            var lines = this.font.split(Component.literal(name), maxW);
            for (int i = 0; i < Math.min(2, lines.size()); i++) {
                g.drawString(this.font, lines.get(i), WEAPON_X0 + 5, ny + i * 9, factory ? 0xFF7FB8C8 : 0xFFD8FBFF, false);
            }
            String rld = String.format(Locale.ROOT, "RLD %.1fs", weapon.getReloadTicks() / 20.0F);
            g.drawString(this.font, rld, WEAPON_X0 + 5, WEAPON_Y1 - 12, 0xFF7FB8C8, false);
            if (titan.isReloading()) {
                float p = 1.0F - titan.getReloadTicks() / (float) Math.max(1, weapon.getReloadTicks());
                fillBar(g, WEAPON_X0 + 5, WEAPON_Y1 - 3, WEAPON_X1 - WEAPON_X0 - 10, p);
            }
        } else if (titan != null) {
            boolean blinkOn = ((int) (this.openTicks / 10.0F)) % 2 == 0;
            g.drawString(this.font, "NO WEAPON", WEAPON_X0 + 5, TitanMenu.WEAPON_Y + 21, blinkOn ? 0xFFFF2A44 : 0x88FF2A44, false);
            g.drawString(this.font, "INSERT MODULE", WEAPON_X0 + 5, TitanMenu.WEAPON_Y + 30, 0xFF7FB8C8, false);
        }

        // cargo + pilot
        g.drawString(this.font, lblCargo, CARGO_X0 + 5, CARGO_Y0 + 4, 0xFFAFC4CC, false);
        g.drawString(this.font, lblPilot, TitanMenu.INV_X, this.inventoryLabelY, 0xFF7FB8C8, false);
    }

    private static void fillBar(GuiGraphics g, int x, int y, int w, float p) {
        rect(g, x, y, x + w, y + 1, CYAN, 0.2F);
        rect(g, x, y, x + Math.round(w * clamp01(p)), y + 1, AMBER, 0.9F);
    }

    private void rightText(GuiGraphics g, String s, int xr, int y, int color) {
        g.drawString(this.font, s, xr - this.font.width(s), y, color, false);
    }
}
