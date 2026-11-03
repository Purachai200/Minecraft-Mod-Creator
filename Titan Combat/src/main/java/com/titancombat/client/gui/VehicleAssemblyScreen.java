package com.titancombat.client.gui;

import com.titancombat.assembly.AssembleVehicleC2SPacket;
import com.titancombat.assembly.VehicleBlueprints;
import com.titancombat.network.ModNetworking;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;

/** Blueprint list on the left, parts (have / need) on the right, Assemble button underneath. */
public class VehicleAssemblyScreen extends Screen {
    private static final int W = 340, H = 200, ROW = 14, LIST_W = 140;
    private final BlockPos pos;
    private int selected = 0;
    private Button assemble;

    private VehicleAssemblyScreen(BlockPos pos) {
        super(Component.literal("Vehicle Assembly Bay"));
        this.pos = pos;
    }

    public static void open(BlockPos pos) {
        Minecraft.getInstance().setScreen(new VehicleAssemblyScreen(pos));
    }

    private int left() { return (this.width - W) / 2; }
    private int top() { return (this.height - H) / 2; }

    @Override
    protected void init() {
        for (int i = 0; i < VehicleBlueprints.ALL.size(); i++) {
            final int idx = i;
            this.addRenderableWidget(Button.builder(Component.literal(this.font.plainSubstrByWidth(shortName(i), LIST_W - 8)), b -> this.selected = idx)
                    .bounds(left() + 6, top() + 18 + i * ROW, LIST_W, ROW - 1).build());
        }
        this.assemble = this.addRenderableWidget(Button.builder(Component.literal("ASSEMBLE"),
                b -> ModNetworking.sendToServer(new AssembleVehicleC2SPacket(this.pos, this.selected)))
                .bounds(left() + LIST_W + 16, top() + H - 26, W - LIST_W - 24, 20).build());
    }

    /** Item names end in "Deployment Key"; the bay lists the vehicle itself. */
    private static String shortName(int i) {
        return new ItemStack(VehicleBlueprints.ALL.get(i).result().get()).getHoverName().getString().replace(" Deployment Key", "");
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(g);
        int x = left(), y = top();
        g.fill(x, y, x + W, y + H, 0xE0101418);
        g.renderOutline(x, y, W, H, 0xFF3FD0FF);
        g.drawString(this.font, "VEHICLE ASSEMBLY BAY // BLUEPRINTS", x + 6, y + 5, 0x3FD0FF);

        VehicleBlueprints.Blueprint bp = VehicleBlueprints.ALL.get(this.selected);
        ItemStack result = new ItemStack(bp.result().get());
        int px = x + LIST_W + 16, right = x + W - 8;
        g.renderItem(result, px, y + 18);
        g.drawString(this.font, this.font.plainSubstrByWidth(shortName(this.selected), right - px - 20), px + 20, y + 22, 0xFFFFFF);
        g.drawString(this.font, "CLASS: " + bp.category(), px, y + 38, 0x9AA5B1);

        var player = Minecraft.getInstance().player;
        int ry = y + 54;
        for (VehicleBlueprints.Part part : bp.parts()) {
            ItemStack ps = new ItemStack(part.item().get());
            int have = player == null ? 0 : VehicleBlueprints.countHeld(player, part.item().get());
            boolean ok = have >= part.count() || (player != null && player.getAbilities().instabuild);
            String count = Math.min(have, 999) + "/" + part.count();
            int cw = this.font.width(count);
            g.renderItem(ps, px, ry - 4);
            g.drawString(this.font, this.font.plainSubstrByWidth(ps.getHoverName().getString(), right - cw - px - 26), px + 20, ry, 0xDDDDDD);
            g.drawString(this.font, count, right - cw, ry, ok ? 0x55FF77 : 0xFF5555);
            ry += 17;
        }
        this.assemble.active = player != null && VehicleBlueprints.canAfford(player, bp);
        super.render(g, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }
}
