package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanWeapon;
import com.titancombat.gui.TitanMenu;
import com.titancombat.item.ModItems;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;

/**
 * TITAN_AUTOTEST=look [TITAN_AUTOTEST_TITAN=<class id>, default trooper]: design lookbook. One unpiloted titan on cleared flat ground,
 * close shots from five angles with the rotary gun, then the mining drill. Screenshots: autotest_look_*.png
 */
final class LookAutoTest {
    private static int clock = 0, trooperId = -1;
    private static double bx, by, bz;

    private LookAutoTest() {}

    private static final double[][] VIEWS = { // distance, elevation, azimuth (0 = camera on the north side, in front of the north-facing titan)
            {11, 8, 0}, {11, 12, 35}, {11, 6, 90}, {11, 20, 200}, {7, 4, 15}};
    private static final String[] NAMES = {"front", "front_three_quarter", "side", "back_high", "close"};

    /** One theme per armour archetype. */
    private static final com.titancombat.entity.TitanArmorTheme[] ARMOUR_SHOWCASE = {
            com.titancombat.entity.TitanArmorTheme.VANGUARD, com.titancombat.entity.TitanArmorTheme.COLOSSUS,
            com.titancombat.entity.TitanArmorTheme.SHIDEN_SAMURAI, com.titancombat.entity.TitanArmorTheme.STRIKER,
            com.titancombat.entity.TitanArmorTheme.SALVAGE_SCRAP, com.titancombat.entity.TitanArmorTheme.SPECTER_STEALTH,
            com.titancombat.entity.TitanArmorTheme.APEX_PREDATOR, com.titancombat.entity.TitanArmorTheme.SAND_RAIDER};
    private static boolean isFrame = false;
    private static net.minecraft.world.phys.Vec3 walkStart;
    private static final double[] walked = new double[2];

    static void run(Minecraft mc) {
        clock++;
        if (clock == 20 && mc.player.isDeadOrDying()) mc.player.respawn();
        if (clock == 40) ClientAutoTest.server2(mc, (p, l) -> {
            p.stopRiding();
            l.setDayTime(6000L);
            l.setWeatherParameters(60000, 0, false, false);
            bx = Math.floor(p.getX()) + 0.5D; by = Math.floor(p.getY()); bz = Math.floor(p.getZ()) + 0.5D;
            ClientAutoTest.tBaseY = by;
            for (Entity e : l.getAllEntities()) if (e instanceof BaseTitanEntity || e instanceof com.titancombat.entity.transport.BaseTransportVehicleEntity) e.discard();
            for (int dx = -20; dx <= 20; dx++) for (int dz = -20; dz <= 20; dz++) {
                for (int dy = 0; dy <= 16; dy++) l.setBlock(new BlockPos((int) Math.floor(bx) + dx, (int) by + dy, (int) Math.floor(bz) + dz), Blocks.AIR.defaultBlockState(), 2);
                l.setBlock(new BlockPos((int) Math.floor(bx) + dx, (int) by - 1, (int) Math.floor(bz) + dz), Blocks.SMOOTH_STONE.defaultBlockState(), 2);
            }
            String id = System.getProperty("titancombat.autotest.titan", "trooper");
            if (!(net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.get(new net.minecraft.resources.ResourceLocation(TitanCombatMod.MODID, id + "_titan"))
                    .create(l) instanceof BaseTitanEntity t)) return;
            t.moveTo(bx, by, bz, 180.0F, 0.0F); // facing north (-Z)
            t.setYBodyRot(180.0F);
            t.setYHeadRot(180.0F);
            t.setNoAi(true);
            t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.ROTARY_MACHINE_GUN).get()));
            l.addFreshEntity(t);
            isFrame = t instanceof com.titancombat.entity.TitanFrameEntity;
            trooperId = t.getId();
        });
        int base = 80;
        for (int pass = 0; pass < 2; pass++) {
            for (int v = 0; v < VIEWS.length; v++) {
                int at = base + (pass * VIEWS.length + v) * 30;
                double[] view = VIEWS[v];
                if (clock == at) ClientAutoTest.aimCameraAt(mc, bx, by + 3.2D, bz, view[0], view[1], view[2]);
                if (clock == at + 25) ClientAutoTest.shot(mc, (pass == 0 ? "gun_" : "drill_") + NAMES[v]);
            }
        }
        if (clock == base + VIEWS.length * 30 - 2) ClientAutoTest.server2(mc, (p, l) -> {
            if (l.getEntity(trooperId) instanceof BaseTitanEntity t)
                t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(TitanWeapon.MINING_DRILL).get()));
        });
        // Modular frames: bolt on a full set of each armour archetype (one theme per archetype) and photograph it
        int armourStart = base + VIEWS.length * 60;
        int sets = isFrame ? ARMOUR_SHOWCASE.length : 0;
        for (int i = 0; i < sets; i++) {
            int t0 = armourStart + i * 55;
            var theme = ARMOUR_SHOWCASE[i];
            if (clock == t0) ClientAutoTest.server2(mc, (p, l) -> {
                if (!(l.getEntity(trooperId) instanceof com.titancombat.entity.TitanFrameEntity f)) return;
                f.setHeadArmor(true); f.setChestArmor(true); f.setArmsArmor(true); f.setLegsArmor(true);
                f.setHeadTheme(theme); f.setChestTheme(theme); f.setArmsTheme(theme); f.setLegsTheme(theme);
            });
            if (clock == t0 + 3) ClientAutoTest.aimCameraAt(mc, bx, by + 3.2D, bz, 10, 10, 35);
            if (clock == t0 + 25) ClientAutoTest.shot(mc, "armour_" + theme.getArchetype().getId() + "_front");
            if (clock == t0 + 28) ClientAutoTest.aimCameraAt(mc, bx, by + 3.2D, bz, 10, 14, 215);
            if (clock == t0 + 50) ClientAutoTest.shot(mc, "armour_" + theme.getArchetype().getId() + "_back");
        }
        int end = armourStart + sets * 55;
        if (clock == end + 4) ClientAutoTest.server2(mc, (p, l) -> {
            // The class's own beacon: used on the ground it must deploy one more of this class
            String id = System.getProperty("titancombat.autotest.titan", "trooper");
            var item = net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation(TitanCombatMod.MODID, id + "_beacon"));
            if (item == net.minecraft.world.item.Items.AIR) return;
            var type = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.get(new net.minecraft.resources.ResourceLocation(TitanCombatMod.MODID, id + "_titan"));
            int before = l.getEntities(type, e -> true).size();
            p.setGameMode(net.minecraft.world.level.GameType.CREATIVE);
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND, new ItemStack(item));
            BlockPos ground = new BlockPos((int) Math.floor(bx) + 8, (int) by - 1, (int) Math.floor(bz) + 8);
            var hit = new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(ground), net.minecraft.core.Direction.UP, ground, false);
            item.useOn(new net.minecraft.world.item.context.UseOnContext(p, net.minecraft.world.InteractionHand.MAIN_HAND, hit));
            int after = l.getEntities(type, e -> true).size();
            TitanCombatMod.LOGGER.info("[autotest] CHECK {}_beacon_deploys {} -> {} : {}", id, before, after, after == before + 1 ? "PASS" : "FAIL");
        });
        // look_full: jetpack shots, bay screen + cargo hold, and a timed walk with and without the speed module
        boolean full = System.getProperty("titancombat.autotest", "").equals("look_full");
        int e = end + 10;
        if (full) {
            if (clock == e + 10) ClientAutoTest.server2(mc, (p, l) -> {
                if (l.getEntity(trooperId) instanceof BaseTitanEntity t) t.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT,
                        new ItemStack(ModItems.FLIGHT_MODULES.get(com.titancombat.entity.TitanFlightModule.ROCKET_JETPACK).get()));
            });
            if (clock == e + 12) ClientAutoTest.aimCameraAt(mc, bx, by + 4.0D, bz, 9, 12, 160);
            if (clock == e + 35) ClientAutoTest.shot(mc, "jetpack_back");
            if (clock == e + 37) ClientAutoTest.aimCameraAt(mc, bx, by + 4.0D, bz, 9, 8, 100);
            if (clock == e + 60) ClientAutoTest.shot(mc, "jetpack_side");
            if (clock == e + 62) ClientAutoTest.server2(mc, (p, l) -> {
                p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
                p.teleportTo(l, bx, by, bz - 5, 0.0F, 0.0F);
                if (l.getEntity(trooperId) instanceof BaseTitanEntity t) t.openCustomInventoryScreen(p);
            });
            if (clock == e + 85) ClientAutoTest.shot(mc, "gui_bay");
            if (clock == e + 87) com.titancombat.network.ModNetworking.sendToServer(new com.titancombat.network.OpenTitanInventoryC2SPacket(trooperId, true));
            if (clock == e + 110) ClientAutoTest.shot(mc, "gui_cargo_hold");
            if (clock == e + 112) {
                if (mc.screen != null) mc.screen.onClose();
                ClientAutoTest.server2(mc, (p, l) -> {
                    if (!(l.getEntity(trooperId) instanceof BaseTitanEntity t)) return;
                    t.setNoAi(false);
                    t.getTitanInventory().setItem(TitanMenu.FLIGHT_SLOT, ItemStack.EMPTY);
                    t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, ItemStack.EMPTY);
                    p.startRiding(t, true);
                });
            }
            for (int run = 0; run < 2; run++) {
                int t0 = e + 200 + run * 120;
                final int r = run;
                if (clock == t0 - 20 && run == 1) ClientAutoTest.server2(mc, (p, l) -> {
                    if (l.getEntity(trooperId) instanceof BaseTitanEntity t)
                        t.getTitanInventory().setItem(TitanMenu.UTILITY_SLOT, new ItemStack(ModItems.SERVO_OVERDRIVE_MODULE.get()));
                });
                if (clock == t0) {
                    walkStart = mc.player.getVehicle() != null ? mc.player.getVehicle().position() : null;
                    mc.options.keyUp.setDown(true);
                }
                if (clock == t0 + 60) {
                    mc.options.keyUp.setDown(false);
                    var v = mc.player.getVehicle();
                    walked[r] = v == null || walkStart == null ? 0.0D : v.position().subtract(walkStart).horizontalDistance();
                    TitanCombatMod.LOGGER.info("[autotest] walk run {} (overdrive={}): {} blocks in 60 ticks", r, r == 1, String.format("%.2f", walked[r]));
                    if (r == 1) TitanCombatMod.LOGGER.info("[autotest] CHECK overdrive_faster {} vs {} : {}", String.format("%.2f", walked[1]),
                            String.format("%.2f", walked[0]), walked[0] > 3.0D && walked[1] > walked[0] * 1.2D ? "PASS" : "FAIL");
                }
            }
            e += 450;
        }
        if (clock == e) {
            TitanCombatMod.LOGGER.info("[autotest] Completed look");
            mc.stop();
        }
    }
}
