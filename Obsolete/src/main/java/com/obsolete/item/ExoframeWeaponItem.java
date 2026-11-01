package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
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
     * Checks if ammunition exists in either Exoframe's utility slots or pilot's inventory.
     * If consume is true, decrements 1 ammo item.
     */
    public abstract boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume);

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
