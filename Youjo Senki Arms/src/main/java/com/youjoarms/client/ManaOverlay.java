package com.youjoarms.client;

import com.tacz.guns.api.item.IGun;
import com.youjoarms.capability.PlayerMageProvider;
import com.youjoarms.formula.FormulaType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiOverlayEvent;
import net.minecraftforge.client.gui.overlay.VanillaGuiOverlay;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "youjoarms", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class ManaOverlay {

    @SubscribeEvent
    public static void onRenderGuiOverlay(RenderGuiOverlayEvent.Post event) {
        if (event.getOverlay() != VanillaGuiOverlay.EXPERIENCE_BAR.type()) {
            return;
        }

        Minecraft mc = Minecraft.getInstance();
        Player player = mc.player;
        if (player == null || mc.options.hideGui) return;

        ItemStack heldItem = player.getMainHandItem();
        IGun gun = IGun.getIGunOrNull(heldItem);
        if (gun == null) return;

        // Render only if holding a youjoarms gun or a gun with active mage capability
        player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
            GuiGraphics gui = event.getGuiGraphics();
            Font font = mc.font;

            int width = mc.getWindow().getGuiScaledWidth();
            int height = mc.getWindow().getGuiScaledHeight();

            int barWidth = 90;
            int barHeight = 6;
            int x = width / 2 - barWidth / 2;
            int y = height - 52; // Just above health / exp bar

            int mana = cap.getMana();
            int maxMana = cap.getMaxMana();
            float fillRatio = maxMana > 0 ? (float) mana / maxMana : 0f;
            fillRatio = Math.max(0f, Math.min(1.0f, fillRatio));

            // Background
            gui.fill(x - 1, y - 1, x + barWidth + 1, y + barHeight + 1, 0xCC000000);
            // Mana fill (cyan/blue)
            int filledWidth = (int) (barWidth * fillRatio);
            gui.fill(x, y, x + filledWidth, y + barHeight, 0xFF00B4D8);

            // Charge progress overlay if charging
            if (cap.isCharging() && cap.getSelectedFormula() != FormulaType.NONE) {
                float chargeRatio = cap.getChargeProgress();
                int chargeFilled = (int) (barWidth * chargeRatio);
                gui.fill(x, y, x + chargeFilled, y + barHeight, 0x88FFD700);
            }

            // Mana text
            String manaText = mana + " / " + maxMana + " MP";
            gui.drawString(font, manaText, x + (barWidth - font.width(manaText)) / 2, y - 8, 0x90E0EF, true);

            // Mana Cell charge, shown while a cell sits in the gun
            int tier = com.youjoarms.mana.GunMana.cellTier(heldItem);
            if (tier > 0) {
                int ch = com.youjoarms.mana.GunMana.charge(heldItem);
                String cellText = "Cell " + new String[]{"I", "II", "III", "IV", "V"}[tier - 1] + "  " + ch + "/" + com.youjoarms.mana.GunMana.CHARGE_CAPACITY;
                gui.drawString(font, cellText, x + barWidth + 6, y - 1, ch > 0 ? 0xFFD700 : 0xFF5555, true);
            }

            // Formula name, then one pip per magic circle; pips light up as the circles stack while charging
            FormulaType formula = cap.getSelectedFormula();
            String formulaText = formula.getDisplayName();
            int formulaColor = formula == FormulaType.NONE ? 0xAAAAAA : formula.getCircleColor();
            gui.drawString(font, Component.literal(formulaText), x + (barWidth - font.width(formulaText)) / 2, y + barHeight + 2, formulaColor, true);
            int rings = formula.getRings();
            int lit = cap.isCharging() ? (int) (cap.getChargeProgress() * rings + 0.001f) : 0;
            int px = width / 2 - (rings * 6 - 2) / 2;
            for (int i = 0; i < rings; i++) {
                int py = y + barHeight + 12;
                gui.fill(px + i * 6, py, px + i * 6 + 4, py + 4, i < lit ? (0xFF000000 | formulaColor) : 0x88333333);
            }
        });
    }
}
