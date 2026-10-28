package com.titancombat.client.gui;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.network.ArtilleryTargetC2SPacket;
import com.titancombat.network.ModNetworking;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;

/**
 * Howitzer fire control: type the target's X / Z (and optionally Y; blank = on the ground there), like
 * entering firing parameters for a mortar. The server checks the range.
 */
public class ArtilleryFireControlScreen extends Screen {
    private final BaseTitanEntity titan;
    private EditBox xBox, yBox, zBox;
    private Component error = Component.empty();

    public ArtilleryFireControlScreen(BaseTitanEntity titan) {
        super(Component.translatable("gui.titancombat.fire_control"));
        this.titan = titan;
    }

    @Override
    protected void init() {
        BlockPos t = titan.getArtilleryTarget();
        int cx = this.width / 2, y = this.height / 2 - 30;
        xBox = coordBox(cx - 105, y, t != null ? String.valueOf(t.getX()) : String.valueOf(titan.getBlockX()), "X");
        yBox = coordBox(cx - 30, y, "", "Y");
        zBox = coordBox(cx + 45, y, t != null ? String.valueOf(t.getZ()) : String.valueOf(titan.getBlockZ()), "Z");
        addRenderableWidget(Button.builder(Component.translatable("gui.titancombat.fire_control.set"), b -> submit())
                .bounds(cx - 60, y + 34, 120, 20).build());
        setInitialFocus(xBox);
    }

    private EditBox coordBox(int x, int y, String value, String label) {
        EditBox box = new EditBox(this.font, x, y, 60, 20, Component.literal(label));
        box.setMaxLength(9);
        box.setValue(value);
        box.setFilter(s -> s.matches("-?\\d*"));
        return addRenderableWidget(box);
    }

    private void submit() {
        try {
            int x = Integer.parseInt(xBox.getValue()), z = Integer.parseInt(zBox.getValue());
            boolean hasY = !yBox.getValue().isEmpty() && !yBox.getValue().equals("-");
            int y = hasY ? Integer.parseInt(yBox.getValue()) : 0;
            ModNetworking.sendToServer(new ArtilleryTargetC2SPacket(x, hasY, y, z));
            onClose();
        } catch (NumberFormatException e) {
            error = Component.translatable("gui.titancombat.fire_control.invalid");
        }
    }

    @Override
    public boolean keyPressed(int key, int scan, int mods) {
        if (key == org.lwjgl.glfw.GLFW.GLFW_KEY_ENTER || key == org.lwjgl.glfw.GLFW.GLFW_KEY_KP_ENTER) {
            submit();
            return true;
        }
        return super.keyPressed(key, scan, mods);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partial) {
        renderBackground(g);
        int cx = this.width / 2, y = this.height / 2 - 30;
        g.drawCenteredString(this.font, this.title, cx, y - 34, 0xFFB000);
        g.drawCenteredString(this.font, Component.translatable("gui.titancombat.fire_control.hint",
                titan.getBlockX(), titan.getBlockY(), titan.getBlockZ()), cx, y - 20, 0xA0C8D8);
        g.drawString(this.font, "X", cx - 115, y + 6, 0xFFFFFF);
        g.drawString(this.font, "Y", cx - 40, y + 6, 0xFFFFFF);
        g.drawString(this.font, "Z", cx + 35, y + 6, 0xFFFFFF);
        g.drawCenteredString(this.font, error, cx, y + 60, 0xFF5050);
        super.render(g, mouseX, mouseY, partial);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
