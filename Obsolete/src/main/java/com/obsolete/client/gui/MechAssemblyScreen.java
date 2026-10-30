package com.obsolete.client.gui;

import com.obsolete.gui.MechAssemblyMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

public class MechAssemblyScreen extends AbstractContainerScreen<MechAssemblyMenu> {

    public MechAssemblyScreen(MechAssemblyMenu menu, Inventory playerInventory, Component title) {
        super(menu, playerInventory, title);
        this.imageWidth = 176;
        this.imageHeight = 166;
        this.inventoryLabelY = 72;
    }

    @Override
    protected void renderBg(GuiGraphics guiGraphics, float partialTick, int mouseX, int mouseY) {
        int left = this.leftPos;
        int top = this.topPos;

        // Industrial Dark Chassis
        guiGraphics.fill(left, top, left + imageWidth, top + imageHeight, 0xFF22262B);
        guiGraphics.renderOutline(left, top, imageWidth, imageHeight, 0xFF4A5560);

        // Header Title Bar
        guiGraphics.fill(left + 2, top + 2, left + imageWidth - 2, top + 14, 0xFF313840);

        // 4 Input component slots in 2x2
        drawSlot(guiGraphics, left + 44, top + 26, 0xFF2D88C4);
        drawSlot(guiGraphics, left + 64, top + 26, 0xFF2D88C4);
        drawSlot(guiGraphics, left + 44, top + 46, 0xFF2D88C4);
        drawSlot(guiGraphics, left + 64, top + 46, 0xFF2D88C4);

        // Assembly Arrow Progress Bar
        int arrowX = left + 88;
        int arrowY = top + 39;
        guiGraphics.fill(arrowX, arrowY, arrowX + 26, arrowY + 10, 0xFF14181B);
        if (this.menu.isCrafting()) {
            int progress = this.menu.getScaledProgress();
            guiGraphics.fill(arrowX, arrowY, arrowX + Math.min(26, progress), arrowY + 10, 0xFF00FFCC);
        }

        // 1 Output Slot (Gold bordered)
        drawSlot(guiGraphics, left + 124, top + 36, 0xFFFFB300);

        // Player Inventory slots
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                drawSlot(guiGraphics, left + 8 + col * 18, top + 84 + row * 18, 0xFF3E4750);
            }
        }
        for (int col = 0; col < 9; ++col) {
            drawSlot(guiGraphics, left + 8 + col * 18, top + 142, 0xFF3E4750);
        }
    }

    private void drawSlot(GuiGraphics g, int x, int y, int borderColor) {
        g.fill(x - 1, y - 1, x + 17, y + 17, borderColor);
        g.fill(x, y, x + 16, y + 16, 0xFF14181B);
    }

    @Override
    protected void renderLabels(GuiGraphics guiGraphics, int mouseX, int mouseY) {
        guiGraphics.drawString(this.font, this.title, 8, 4, 0x00FFCC, false);
        guiGraphics.drawString(this.font, this.playerInventoryTitle, 8, this.inventoryLabelY, 0x999999, false);
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics);
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        this.renderTooltip(guiGraphics, mouseX, mouseY);
    }
}
