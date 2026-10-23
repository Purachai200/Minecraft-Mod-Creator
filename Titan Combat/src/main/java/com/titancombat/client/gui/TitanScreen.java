package com.titancombat.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.gui.TitanMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

public class TitanScreen extends AbstractContainerScreen<TitanMenu> {

    public TitanScreen(TitanMenu menu, Inventory playerInventory, Component title) {
        super(menu, playerInventory, title);
        this.imageWidth = 176;
        this.imageHeight = 166;
        this.inventoryLabelY = 72;
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics);
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        this.renderTooltip(guiGraphics, mouseX, mouseY);
    }

    @Override
    protected void renderBg(GuiGraphics guiGraphics, float partialTick, int mouseX, int mouseY) {
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();

        int x = this.leftPos;
        int y = this.topPos;

        // High-tech dark armored panel background
        guiGraphics.fill(x, y, x + this.imageWidth, y + this.imageHeight, 0xFA0B111A);

        // Futuristic neon cyan border framing
        guiGraphics.fill(x, y, x + this.imageWidth, y + 2, 0xFF00E5FF);
        guiGraphics.fill(x, y + this.imageHeight - 2, x + this.imageWidth, y + this.imageHeight, 0xFF00E5FF);
        guiGraphics.fill(x, y, x + 2, y + this.imageHeight, 0xFF00E5FF);
        guiGraphics.fill(x + this.imageWidth - 2, y, x + this.imageWidth, y + this.imageHeight, 0xFF00E5FF);

        // Header banner
        guiGraphics.fill(x + 2, y + 2, x + this.imageWidth - 2, y + 14, 0xEE142030);

        // Battery Slot Box (x=17, y=19) - Neon Amber Border
        guiGraphics.fill(x + 17, y + 19, x + 35, y + 37, 0x88FF9100);
        guiGraphics.fill(x + 18, y + 20, x + 34, y + 36, 0xFF05080E);

        // Ammo Slot Boxes (x=53, y=19 and x=71, y=19) - Neon Cyan Border
        guiGraphics.fill(x + 53, y + 19, x + 89, y + 37, 0x8800E5FF);
        guiGraphics.fill(x + 54, y + 20, x + 70, y + 36, 0xFF05080E);
        guiGraphics.fill(x + 72, y + 20, x + 88, y + 36, 0xFF05080E);

        // Cargo Bay Slots (x=7 to x=169, y=51 to y=69)
        for (int i = 0; i < 9; i++) {
            int sx = x + 7 + i * 18;
            int sy = y + 51;
            guiGraphics.fill(sx, sy, sx + 18, sy + 18, 0x55304050);
            guiGraphics.fill(sx + 1, sy + 1, sx + 17, sy + 17, 0xFF05080E);
        }

        // Player Inventory Slots (3 rows of 9)
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 9; col++) {
                int sx = x + 7 + col * 18;
                int sy = y + 83 + row * 18;
                guiGraphics.fill(sx, sy, sx + 18, sy + 18, 0x44203040);
                guiGraphics.fill(sx + 1, sy + 1, sx + 17, sy + 17, 0xFF070B10);
            }
        }

        // Hotbar Slots (1 row of 9)
        for (int col = 0; col < 9; col++) {
            int sx = x + 7 + col * 18;
            int sy = y + 141;
            guiGraphics.fill(sx, sy, sx + 18, sy + 18, 0x5500E5FF);
            guiGraphics.fill(sx + 1, sy + 1, sx + 17, sy + 17, 0xFF070B10);
        }

        // Telemetry readout on top right
        BaseTitanEntity titan = this.menu.getTitan();
        if (titan != null) {
            String hpStr = (int) titan.getHealth() + " / " + (int) titan.getMaxHealth() + " HP";
            guiGraphics.drawString(this.font, hpStr, x + this.imageWidth - this.font.width(hpStr) - 8, y + 20, 0xFF00E676, false);
            String shieldStr = (int) titan.getShield() + " SHIELD";
            guiGraphics.drawString(this.font, shieldStr, x + this.imageWidth - this.font.width(shieldStr) - 8, y + 30, 0xFF00B0FF, false);
        }

        RenderSystem.disableBlend();
    }

    @Override
    protected void renderLabels(GuiGraphics guiGraphics, int mouseX, int mouseY) {
        // Title
        guiGraphics.drawString(this.font, this.title, 6, 4, 0xFF00E5FF, false);

        // Section labels
        guiGraphics.drawString(this.font, "CORE", 16, 38, 0xFFFFAB00, false);
        guiGraphics.drawString(this.font, "MUNITIONS", 52, 38, 0xFF80D8FF, false);
        guiGraphics.drawString(this.font, "CARGO BAY", 6, 42, 0xFFAAAAAA, false);
        guiGraphics.drawString(this.font, "PILOT INVENTORY", 6, this.inventoryLabelY, 0xFF888888, false);
    }
}
