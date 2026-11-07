package com.youjoarms.mana;

import com.tacz.guns.api.item.IGun;
import com.tacz.guns.api.item.attachment.AttachmentType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import java.util.Map;

/**
 * Per-gun mana profile. The mana pool, its regeneration and the cost of a formula follow the gun in the player's
 * main hand; a Mana Cell in the gun's extended-mag slot multiplies pool and regeneration by {@link #TIER_STEP}
 * once per tier (tiers 1-5, i.e. up to about x7.6).
 */
public final class GunMana {
    /** maxMana, regen per second, formula cost multiplier. */
    public record Profile(int maxMana, int regenPerSecond, double costMultiplier) {}

    public static final double TIER_STEP = 1.5;
    public static final int MAX_TIER = 5;

    private static final Map<String, Profile> PROFILES = Map.ofEntries(
            Map.entry("kar98k", new Profile(100, 5, 1.0)),
            Map.entry("gewehr98", new Profile(110, 5, 1.0)),
            Map.entry("t_gewehr", new Profile(220, 4, 0.9)),   // artillery rifle: deep pool, slow regen
            Map.entry("mosin", new Profile(90, 5, 1.1)),
            Map.entry("lebel", new Profile(120, 6, 1.0)),
            Map.entry("lee_enfield", new Profile(100, 7, 1.0)),
            Map.entry("springfield", new Profile(110, 6, 0.95)),
            Map.entry("c96", new Profile(70, 8, 0.8)),          // sidearms: small pool, cheap casts
            Map.entry("luger_p08", new Profile(80, 7, 0.9)),
            Map.entry("m1911", new Profile(75, 7, 0.9)),
            Map.entry("mp18", new Profile(90, 9, 1.2)),         // SMGs: fast regen, dear casts
            Map.entry("thompson", new Profile(100, 9, 1.1)),
            Map.entry("bar_m1918", new Profile(140, 6, 1.0)),
            Map.entry("mg08", new Profile(260, 4, 1.2)),        // machine guns: huge pool
            Map.entry("mg08_15", new Profile(180, 5, 1.1)),
            Map.entry("m1897", new Profile(90, 5, 0.9)),
            Map.entry("kampfpistole", new Profile(160, 3, 0.7)));

    /** A Mana Cell holds this many casts; it is stored on the gun, and a gun with no entry counts as full. */
    public static final int CHARGE_CAPACITY = 20;
    private static final String CHARGE_KEY = "YoujoCellCharge";

    private GunMana() {}

    public static int charge(ItemStack gunStack) {
        var tag = gunStack.getTag();
        return tag != null && tag.contains(CHARGE_KEY) ? Math.max(0, Math.min(CHARGE_CAPACITY, tag.getInt(CHARGE_KEY))) : CHARGE_CAPACITY;
    }

    public static void setCharge(ItemStack gunStack, int value) {
        gunStack.getOrCreateTag().putInt(CHARGE_KEY, Math.max(0, Math.min(CHARGE_CAPACITY, value)));
    }

    /** Charge restored per Amethyst Shard: rarer cells are hungrier (5 for tier 1 down to 1 for tier 5). */
    public static int chargePerShard(int tier) {
        return Math.max(1, 6 - tier);
    }

    /** Mana Cell tier (0 = none) in the gun's extended-mag slot. */
    public static int cellTier(ItemStack gunStack) {
        IGun gun = IGun.getIGunOrNull(gunStack);
        if (gun == null) return 0;
        ResourceLocation id = gun.getAttachmentId(gunStack, AttachmentType.EXTENDED_MAG);
        if (id == null || !id.getNamespace().equals("youjoarms") || !id.getPath().startsWith("mana_cell_")) return 0;
        try {
            return Math.min(MAX_TIER, Integer.parseInt(id.getPath().substring("mana_cell_".length())));
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    /** True for a youjoarms gun; formulas are never cast from another pack's or mod's guns. */
    public static boolean isOurs(ItemStack gunStack) {
        IGun gun = IGun.getIGunOrNull(gunStack);
        return gun != null && gun.getGunId(gunStack).getNamespace().equals("youjoarms");
    }

    /** Effective profile of a held gun, or null when it is not one of ours (the config defaults apply). */
    public static Profile of(ItemStack gunStack) {
        IGun gun = IGun.getIGunOrNull(gunStack);
        if (gun == null) return null;
        ResourceLocation gunId = gun.getGunId(gunStack);
        Profile base = gunId.getNamespace().equals("youjoarms") ? PROFILES.get(gunId.getPath()) : null;
        if (base == null) return null;
        int tier = charge(gunStack) > 0 ? cellTier(gunStack) : 0;   // a flat cell gives nothing
        double k = Math.pow(TIER_STEP, tier);
        return new Profile((int) Math.round(base.maxMana() * k), (int) Math.round(base.regenPerSecond() * k), base.costMultiplier());
    }
}
