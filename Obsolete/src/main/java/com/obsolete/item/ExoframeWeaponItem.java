package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

public abstract class ExoframeWeaponItem extends Item {
    private final int fireCooldownTicks;
    private final String weaponModelName;

    public ExoframeWeaponItem(Properties properties, int fireCooldownTicks, String weaponModelName) {
        super(properties);
        this.fireCooldownTicks = fireCooldownTicks;
        this.weaponModelName = weaponModelName;
    }

    public int getFireCooldownTicks() {
        return fireCooldownTicks;
    }

    public String getWeaponModelName() {
        return weaponModelName;
    }

    /**
     * Whether holding down the attack/fire key triggers continuous automatic fire.
     */
    public boolean isAutomatic() {
        return false;
    }

    /**
     * Maximum rounds in a single magazine. Return <= 0 for non-magazine weapons (melee, tools, shield).
     */
    public int getMagazineCapacity() {
        return 30;
    }

    /**
     * Duration in ticks to reload this weapon.
     */
    public int getReloadDurationTicks() {
        return 45;
    }

    /**
     * Type of ammunition required by this weapon. Return null if none.
     */
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return ExoframeAmmoItem.AmmoType.CALIBER_20MM;
    }

    /**
     * How many rounds of magazine capacity are refilled by 1 item of reserve ammo.
     */
    public int getRoundsPerAmmoItem() {
        return 1;
    }

    public static int getLoadedAmmo(ItemStack stack) {
        if (stack.isEmpty() || !(stack.getItem() instanceof ExoframeWeaponItem weapon)) return 0;
        int cap = weapon.getMagazineCapacity();
        if (cap <= 0) return 1;
        CompoundTag tag = stack.getTag();
        if (tag == null || !tag.contains("LoadedAmmo")) {
            return cap; // fresh weapons start with full magazine
        }
        return tag.getInt("LoadedAmmo");
    }

    public static void setLoadedAmmo(ItemStack stack, int ammo) {
        if (stack.isEmpty() || !(stack.getItem() instanceof ExoframeWeaponItem weapon)) return;
        int cap = weapon.getMagazineCapacity();
        if (cap <= 0) return;
        stack.getOrCreateTag().putInt("LoadedAmmo", Math.max(0, Math.min(cap, ammo)));
    }

    public static void decrementLoadedAmmo(ItemStack stack) {
        int current = getLoadedAmmo(stack);
        if (current > 0) {
            setLoadedAmmo(stack, current - 1);
        }
    }

    /**
     * Counts reserve rounds available in Exoframe inventory and pilot inventory.
     */
    public int getReserveRoundsAvailable(ExoframeEntity exoframe, ServerPlayer pilot) {
        ExoframeAmmoItem.AmmoType required = getRequiredAmmoType();
        if (required == null) return 999;
        int count = 0;
        int multiplier = getRoundsPerAmmoItem();

        int slots = exoframe.getModularInventory().getSlots();
        for (int i = 0; i < slots; i++) {
            ItemStack st = exoframe.getModularInventory().getStackInSlot(i);
            if (st.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == required) {
                count += st.getCount() * multiplier;
            }
        }

        if (pilot != null) {
            for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
                ItemStack st = pilot.getInventory().getItem(i);
                if (st.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == required) {
                    count += st.getCount() * multiplier;
                }
            }
        }
        return count;
    }

    /**
     * Consumes reserve ammo items from Exoframe inventory first, then pilot inventory,
     * to fulfill the requested number of rounds.
     */
    public int consumeReserveRounds(ExoframeEntity exoframe, ServerPlayer pilot, int roundsNeeded) {
        ExoframeAmmoItem.AmmoType required = getRequiredAmmoType();
        if (required == null) return roundsNeeded;
        int multiplier = getRoundsPerAmmoItem();
        int loadedRounds = 0;

        int slots = exoframe.getModularInventory().getSlots();
        for (int i = 0; i < slots && loadedRounds < roundsNeeded; i++) {
            ItemStack st = exoframe.getModularInventory().getStackInSlot(i);
            if (st.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == required) {
                while (!st.isEmpty() && loadedRounds < roundsNeeded) {
                    st.shrink(1);
                    loadedRounds += multiplier;
                }
                exoframe.getModularInventory().setStackInSlot(i, st);
            }
        }

        if (pilot != null && loadedRounds < roundsNeeded) {
            for (int i = 0; i < pilot.getInventory().getContainerSize() && loadedRounds < roundsNeeded; i++) {
                ItemStack st = pilot.getInventory().getItem(i);
                if (st.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == required) {
                    while (!st.isEmpty() && loadedRounds < roundsNeeded) {
                        st.shrink(1);
                        loadedRounds += multiplier;
                    }
                }
            }
        }
        return loadedRounds;
    }

    /**
     * Checks if current magazine has ammo. If consuming, decrements loaded ammo.
     * If empty, plays empty click and triggers auto-reload if reserve ammo is available.
     */
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        if (getMagazineCapacity() <= 0) return true; // non-magazine melee or tool

        ItemStack weapon = exoframe.getModularInventory().getStackInSlot(com.obsolete.entity.inventory.ExoframeArmorSlot.MAIN_WEAPON.getIndex());
        int loaded = getLoadedAmmo(weapon);
        if (loaded <= 0) {
            exoframe.level().playSound(null, exoframe.blockPosition(), com.obsolete.sound.ModSounds.WEAPON_EMPTY_CLICK.get(), net.minecraft.sounds.SoundSource.PLAYERS, 1.2F, 1.0F);
            if (pilot != null) {
                if (getReserveRoundsAvailable(exoframe, pilot) > 0) {
                    exoframe.triggerReload(pilot);
                } else {
                    pilot.displayClientMessage(net.minecraft.network.chat.Component.literal("§c[OUT OF AMMUNITION - NO RESERVES]").withStyle(net.minecraft.ChatFormatting.RED), true);
                }
            }
            return false;
        }

        if (consume) {
            decrementLoadedAmmo(weapon);
            if (getLoadedAmmo(weapon) <= 0 && pilot != null && getReserveRoundsAvailable(exoframe, pilot) > 0) {
                exoframe.triggerReload(pilot);
            }
        }
        return true;
    }

    @Override
    public boolean isBarVisible(ItemStack stack) {
        int cap = getMagazineCapacity();
        return cap > 0 && getLoadedAmmo(stack) < cap;
    }

    @Override
    public int getBarWidth(ItemStack stack) {
        int cap = getMagazineCapacity();
        if (cap <= 0) return 0;
        int loaded = getLoadedAmmo(stack);
        return Math.round(13.0F * ((float) loaded / (float) cap));
    }

    @Override
    public int getBarColor(ItemStack stack) {
        int cap = getMagazineCapacity();
        if (cap <= 0) return 0xFFFFFF;
        float ratio = (float) getLoadedAmmo(stack) / (float) cap;
        return net.minecraft.util.Mth.hsvToRgb(ratio / 3.0F, 1.0F, 1.0F); // Red -> Yellow -> Green
    }

    @Override
    public void appendHoverText(ItemStack stack, @org.jetbrains.annotations.Nullable Level level, java.util.List<net.minecraft.network.chat.Component> tooltip, net.minecraft.world.item.TooltipFlag flag) {
        if (getMagazineCapacity() > 0) {
            int loaded = getLoadedAmmo(stack);
            int cap = getMagazineCapacity();
            net.minecraft.ChatFormatting col = loaded > (cap / 2) ? net.minecraft.ChatFormatting.GREEN : (loaded > 0 ? net.minecraft.ChatFormatting.YELLOW : net.minecraft.ChatFormatting.RED);
            tooltip.add(net.minecraft.network.chat.Component.literal("§7Magazine: " + col + loaded + " / " + cap + " RDS§7 (Press §eR§7 in mech to reload)"));
        }
        super.appendHoverText(stack, level, tooltip, flag);
    }

    /**
     * Executes the weapon firing logic server-side.
     */
    public abstract boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot);

    public static void spawnMuzzleFlashAndCasing(Level level, Vec3 muzzlePos, Vec3 forward, Vec3 right, boolean ejectCasing) {
        if (level instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.FLAME, muzzlePos.x, muzzlePos.y, muzzlePos.z, 2, forward.x * 0.1, forward.y * 0.1, forward.z * 0.1, 0.05);
            serverLevel.sendParticles(ParticleTypes.SMOKE, muzzlePos.x, muzzlePos.y, muzzlePos.z, 4, forward.x * 0.05, forward.y * 0.05, forward.z * 0.05, 0.02);
            if (ejectCasing) {
                Vec3 casingPos = muzzlePos.subtract(forward.scale(0.38D)).add(right.scale(0.30D));
                com.obsolete.entity.ExoframeCasingEntity casing = new com.obsolete.entity.ExoframeCasingEntity(serverLevel, casingPos, forward, right);
                serverLevel.addFreshEntity(casing);
            }
        }
    }

    public static void spawnRocketBackblast(Level level, Vec3 launchPos, Vec3 forward) {
        if (level instanceof ServerLevel serverLevel) {
            Vec3 backPos = launchPos.subtract(forward.scale(0.85D));
            serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, backPos.x, backPos.y, backPos.z, 12, -forward.x * 0.25, 0.08, -forward.z * 0.25, 0.05);
            serverLevel.sendParticles(ParticleTypes.FLAME, backPos.x, backPos.y, backPos.z, 4, -forward.x * 0.15, 0.05, -forward.z * 0.15, 0.04);
        }
    }
}
