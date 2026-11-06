package com.titancombat.client.debug;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.ModEntities;
import com.titancombat.entity.TitanArmorTheme;
import com.titancombat.entity.TitanFrameEntity;
import com.titancombat.entity.TitanWeapon;
import com.titancombat.gui.TitanMenu;
import com.titancombat.item.ModItems;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;

/**
 * TITAN_AUTOTEST=arsenal: the heavy weapons pack and MOD modules on a Titan Exo in Ion armour. Each new weapon is
 * mounted, photographed and fired by the pilot (projectiles must appear); then shield capacitor, reinforced plating
 * and nanite repair are checked by their effect on shield, damage taken and hull.
 */
final class ArsenalAutoTest {
    private static final TitanWeapon[] WEAPONS = {TitanWeapon.ARC_CANNON, TitanWeapon.SCATTER_CANNON,
            TitanWeapon.INFERNO_FLAMETHROWER, TitanWeapon.GRENADE_LAUNCHER};
    private static int clock = 0, titanId = -1, seen = 0;
    private static double bx, by, bz;
    private static float before;

    private ArsenalAutoTest() {}

    private static void check(String name, boolean pass, Object detail) {
        TitanCombatMod.LOGGER.info("[autotest] CHECK {} {} : {}", name, detail, pass ? "PASS" : "FAIL");
    }

    private static BaseTitanEntity titan(net.minecraft.server.level.ServerLevel l) {
        return l.getEntity(titanId) instanceof BaseTitanEntity t ? t : null;
    }

    static void run(Minecraft mc) {
        clock++;
        if (clock == 20 && mc.player.isDeadOrDying()) mc.player.respawn();
        if (clock == 40) ClientAutoTest.server2(mc, (p, l) -> {
            p.stopRiding();
            l.setDayTime(6000L);
            bx = Math.floor(p.getX()) + 0.5D; by = Math.floor(p.getY()); bz = Math.floor(p.getZ()) + 0.5D;
            ClientAutoTest.tBaseY = by;
            for (Entity e : l.getAllEntities()) if (e instanceof BaseTitanEntity) e.discard();
            for (int dx = -24; dx <= 24; dx++) for (int dz = -24; dz <= 40; dz++) {
                for (int dy = 0; dy <= 16; dy++) l.setBlock(new BlockPos((int) Math.floor(bx) + dx, (int) by + dy, (int) Math.floor(bz) + dz), Blocks.AIR.defaultBlockState(), 2);
                l.setBlock(new BlockPos((int) Math.floor(bx) + dx, (int) by - 1, (int) Math.floor(bz) + dz), Blocks.SMOOTH_STONE.defaultBlockState(), 2);
            }
            var t = ModEntities.TITAN_EXO_TITAN.get().create(l);
            t.moveTo(bx, by, bz, 0.0F, 0.0F); // facing south (+Z), into the cleared range
            l.addFreshEntity(t);
            t.setEnergy(t.getMaxEnergy()); // the beacon fills the reactor; a bare spawn starts empty and won't fire
            t.setHeadArmor(true); t.setChestArmor(true); t.setArmsArmor(true); t.setLegsArmor(true);
            for (var s : new TitanFrameEntity[]{t}) {
                s.setHeadTheme(TitanArmorTheme.VANGUARD); s.setChestTheme(TitanArmorTheme.VANGUARD);
                s.setArmsTheme(TitanArmorTheme.VANGUARD); s.setLegsTheme(TitanArmorTheme.VANGUARD);
            }
            titanId = t.getId();
            p.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);
            p.startRiding(t, true);
        });
        // ---- weapons
        for (int i = 0; i < WEAPONS.length; i++) {
            TitanWeapon w = WEAPONS[i];
            int t0 = 160 + i * 170;
            if (clock == t0) {
                seen = 0;
                mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT);
                ClientAutoTest.server2(mc, (p, l) -> {
                    var t = titan(l);
                    if (t == null) return;
                    t.getTitanInventory().setItem(TitanMenu.WEAPON_SLOT, new ItemStack(ModItems.WEAPON_MODULES.get(w).get()));
                    t.getTitanInventory().setItem(TitanMenu.AMMO_SLOT_1, new ItemStack(ModItems.WEAPON_MAGAZINES.get(w).get(), 8));
                });
            }
            if (clock > t0 + 10 && clock < t0 + 140 && clock % 3 == 0) ClientAutoTest.server2(mc, (p, l) -> {
                var t = titan(l);
                if (t == null) return;
                t.firePrimaryWeapon(p);
                seen = Math.max(seen, l.getEntities(ModEntities.TITAN_BULLET.get(), t.getBoundingBox().inflate(48.0D), e -> true).size());
            });
            if (clock == t0 + 100) ClientAutoTest.shot(mc, "weapon_" + w.getId());
            if (clock == t0 + 150) check("fires_" + w.getId(), seen > 0, seen + " rounds in flight at peak");
        }
        int m = 160 + WEAPONS.length * 170;
        // ---- modules
        if (clock == m) ClientAutoTest.server2(mc, (p, l) -> {
            var t = titan(l);
            if (t != null) t.getTitanInventory().setItem(TitanMenu.UTILITY_SLOT, new ItemStack(ModItems.SHIELD_CAPACITOR_MODULE.get()));
        });
        if (clock == m + 45) ClientAutoTest.server2(mc, (p, l) -> {
            var t = titan(l);
            if (t == null) return;
            check("shield_capacitor", t.getMaxShield() > 140.0F, "max shield " + t.getMaxShield());
            t.getTitanInventory().setItem(TitanMenu.UTILITY_SLOT, ItemStack.EMPTY);
            t.setShield(0.0F);
            t.setDefenseActive(false);
            before = t.getHealth();
            t.hurt(l.damageSources().generic(), 40.0F);
            before = before - t.getHealth(); // damage taken bare
        });
        if (clock == m + 70) ClientAutoTest.server2(mc, (p, l) -> {
            var t = titan(l);
            if (t == null) return;
            t.getTitanInventory().setItem(TitanMenu.UTILITY_SLOT, new ItemStack(ModItems.REINFORCED_PLATING_MODULE.get()));
            t.setShield(0.0F);
            float h = t.getHealth();
            t.invulnerableTime = 0;
            t.hurt(l.damageSources().generic(), 40.0F);
            float taken = h - t.getHealth();
            check("reinforced_plating", before > 0 && taken < before * 0.85F, String.format("took %.1f with plating vs %.1f without", taken, before));
            t.getTitanInventory().setItem(TitanMenu.UTILITY_SLOT, new ItemStack(ModItems.NANITE_REPAIR_MODULE.get()));
            before = t.getHealth();
        });
        if (clock == m + 140) ClientAutoTest.server2(mc, (p, l) -> {
            var t = titan(l);
            if (t != null) check("nanite_repair", t.getHealth() > before + 3.0F, String.format("hull %.1f -> %.1f over 3.5 s", before, t.getHealth()));
        });
        if (clock == m + 150) {
            TitanCombatMod.LOGGER.info("[autotest] Completed arsenal");
            mc.stop();
        }
    }
}
