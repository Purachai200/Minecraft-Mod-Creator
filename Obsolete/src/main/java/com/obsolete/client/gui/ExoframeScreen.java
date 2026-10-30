package com.obsolete.client.gui;

import com.mojang.blaze3d.systems.RenderSystem;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.gui.ExoframeMenu;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;

public class ExoframeScreen extends AbstractContainerScreen<ExoframeMenu> {

    public ExoframeScreen(ExoframeMenu menu, Inventory playerInventory, Component title) {
        super(menu, playerInventory, title);
        this.imageWidth = 176;
        this.imageHeight = 170;
        this.inventoryLabelY = 76;
    }

    @Override
    protected void renderBg(GuiGraphics guiGraphics, float partialTick, int mouseX, int mouseY) {
        int left = this.leftPos;
        int top = this.topPos;

        ExoframeEntity exoframe = this.menu.getExoframe();
        int tier = exoframe != null ? exoframe.getFrameTier() : 1;

        int panelBg = tier == 0 ? 0xFF241812 : (tier == 3 ? 0xFF0E1022 : (tier == 2 ? 0xFF0C1814 : 0xFF181C20));
        int borderCol = tier == 0 ? 0xFFAA5522 : (tier == 3 ? 0xFF00FFFF : (tier == 2 ? 0xFF00FF88 : 0xFF38444C));
        int headerBg = tier == 0 ? 0xFF3D2518 : (tier == 3 ? 0xFF1C1E3C : (tier == 2 ? 0xFF142B20 : 0xFF2A343D));
        int previewBorder = tier == 0 ? 0xFFFF9900 : (tier == 3 ? 0xFFFFCC00 : (tier == 2 ? 0xFF00FF88 : 0xFF00AAFF));

        // Dark industrial background panel
        guiGraphics.fill(left, top, left + imageWidth, top + imageHeight, panelBg);
        // Border outline
        guiGraphics.fill(left, top, left + imageWidth, top + 2, borderCol);
        guiGraphics.fill(left, top + imageHeight - 2, left + imageWidth, top + imageHeight, borderCol);
        guiGraphics.fill(left, top, left + 2, top + imageHeight, borderCol);
        guiGraphics.fill(left + imageWidth - 2, top, left + imageWidth, top + imageHeight, borderCol);

        // Header banner
        guiGraphics.fill(left + 2, top + 2, left + imageWidth - 2, top + 15, headerBg);

        // 3D Mech Preview Bay on Left
        int previewX = left + 28;
        int previewY = top + 74;
        guiGraphics.fill(left + 8, top + 18, left + 48, top + 78, 0xFF0E1215);
        guiGraphics.renderOutline(left + 8, top + 18, 40, 60, previewBorder);

        if (exoframe != null) {
            InventoryScreen.renderEntityInInventoryFollowsMouse(
                    guiGraphics, previewX, previewY, 18,
                    (float) previewX - mouseX, (float) (previewY - 30) - mouseY, exoframe);
        }

        // Draw frames for the 6 modular mech slots
        int fHead = tier == 0 ? 0xFFDD7722 : (tier == 3 ? 0xFFFFCC00 : 0xFFE0B020);
        int fChest = tier == 0 ? 0xFFCC5511 : (tier == 3 ? 0xFF00FFFF : 0xFF20C0E0);
        int fArms = tier == 0 ? 0xFF995522 : (tier == 3 ? 0xFF00FF88 : 0xFF60E020);
        int fLegs = tier == 0 ? 0xFF884411 : (tier == 3 ? 0xFF00FF88 : 0xFF60E020);
        int fUtil = tier == 0 ? 0xFFBB6622 : (tier == 3 ? 0xFFDD44FF : 0xFFE08020);
        int fWpn = tier == 0 ? 0xFFDD3311 : (tier == 3 ? 0xFFFF3366 : 0xFFE02020);

        drawSlotFrame(guiGraphics, left + 80, top + 18, fHead);  // Head
        drawSlotFrame(guiGraphics, left + 80, top + 38, fChest); // Chest
        drawSlotFrame(guiGraphics, left + 56, top + 38, fArms);  // Arms
        drawSlotFrame(guiGraphics, left + 80, top + 60, fLegs);  // Legs
        drawSlotFrame(guiGraphics, left + 104, top + 38, fUtil); // Utility
        drawSlotFrame(guiGraphics, left + 130, top + 38, fWpn);  // Weapon

        // Draw Player Inventory slot backgrounds
        int invFrameCol = tier == 0 ? 0xFF4A3225 : (tier == 3 ? 0xFF242646 : (tier == 2 ? 0xFF1C342A : 0xFF323B44));
        for (int row = 0; row < 3; ++row) {
            for (int col = 0; col < 9; ++col) {
                drawSlotFrame(guiGraphics, left + 8 + col * 18, top + 88 + row * 18, invFrameCol);
            }
        }
        for (int col = 0; col < 9; ++col) {
            drawSlotFrame(guiGraphics, left + 8 + col * 18, top + 146, invFrameCol);
        }
    }

    private void drawSlotFrame(GuiGraphics g, int x, int y, int borderColor) {
        g.fill(x - 1, y - 1, x + 17, y + 17, borderColor);
        g.fill(x, y, x + 16, y + 16, 0xFF14181B);
    }

    @Override
    protected void renderLabels(GuiGraphics guiGraphics, int mouseX, int mouseY) {
        ExoframeEntity exoframe = this.menu.getExoframe();
        int tier = exoframe != null ? exoframe.getFrameTier() : 1;

        String title = tier == 0 ? "SCRAP WORKSHOP // T-0"
                : (tier == 3 ? "QUANTUM SPEC-OPS // T-3"
                : (tier == 2 ? "ADVANCED ARMORED BAY // T-2"
                : "MIL-SPEC MODULAR BAY // T-1"));
        int titleCol = tier == 0 ? 0xFFFFCC00 : (tier == 3 ? 0xFF00FFFF : (tier == 2 ? 0xFF00FF88 : 0xFF00E0FF));

        guiGraphics.drawString(this.font, title, 10, 5, titleCol, false);
        guiGraphics.drawString(this.font, Component.translatable("gui.obsolete.inv"), 8, this.inventoryLabelY, 0xAAAAAA, false);

        // Labels for slots
        guiGraphics.drawString(this.font, "H", 85, 23, 0x888888, false);
        guiGraphics.drawString(this.font, "C", 85, 43, 0x888888, false);
        guiGraphics.drawString(this.font, "A", 61, 43, 0x888888, false);
        guiGraphics.drawString(this.font, "L", 85, 65, 0x888888, false);
        guiGraphics.drawString(this.font, "U", 109, 43, 0x888888, false);
        guiGraphics.drawString(this.font, "W", 135, 43, 0x888888, false);

        // Tier 2 & 3: Per-slot armor stat percentage readout
        if (tier >= 2 && exoframe != null) {
            float def = 0.0F;
            for (com.obsolete.entity.inventory.ExoframeArmorSlot slot : com.obsolete.entity.inventory.ExoframeArmorSlot.values()) {
                if (slot != com.obsolete.entity.inventory.ExoframeArmorSlot.MAIN_WEAPON && slot != com.obsolete.entity.inventory.ExoframeArmorSlot.UTILITY) {
                    net.minecraft.world.item.ItemStack s = exoframe.getModularInventory().getStackInSlot(slot.getIndex());
                    if (s.getItem() instanceof com.obsolete.item.ExoframeArmorItem armor) {
                        def += armor.getDamageReduction();
                    }
                }
            }
            String stat = String.format("DEF: %.0f%%", def * 100);
            guiGraphics.drawString(this.font, stat, 120, 5, tier == 3 ? 0xFFFFCC00 : 0xFF00FF88, false);
        }
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics);
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        this.renderTooltip(guiGraphics, mouseX, mouseY);
    }
}
