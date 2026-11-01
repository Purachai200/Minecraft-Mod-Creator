package com.obsolete.item;

import com.obsolete.entity.ExoframeBulletEntity;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.sound.ModSounds;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

public class ExoframeSniperRifleItem extends ExoframeWeaponItem {

    public ExoframeSniperRifleItem(Properties properties) {
        super(properties.stacksTo(1), 25, "weapon_sniper_amr"); // 1.25s cooldown between sniper shots
    }

    @Override
    public int getMagazineCapacity() {
        return 5;
    }

    @Override
    public int getReloadDurationTicks() {
        return 60;
    }

    @Override
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return ExoframeAmmoItem.AmmoType.CALIBER_20MM;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        Level level = exoframe.level();
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            return false;
        }

        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.8D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.4D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        // High velocity 20mm Anti-Materiel Round (damage 50.0F, velocity 9.0F)
        ExoframeBulletEntity bullet = new ExoframeBulletEntity(level, pilot, 50.0F);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 9.0F, 0.05F);
        level.addFreshEntity(bullet);

        spawnMuzzleFlashAndCasing(level, muzzlePos, forward, right, true);

        // Massive 20mm Anti-Materiel cannon blast: high-velocity railgun crack + deep concussive thunder
        if (level instanceof net.minecraft.server.level.ServerLevel serverLevel) {
            serverLevel.sendParticles(net.minecraft.core.particles.ParticleTypes.CAMPFIRE_COSY_SMOKE, muzzlePos.x, muzzlePos.y, muzzlePos.z, 16, forward.x * 0.4, forward.y * 0.4, forward.z * 0.4, 0.08);
            serverLevel.sendParticles(net.minecraft.core.particles.ParticleTypes.EXPLOSION, muzzlePos.x, muzzlePos.y, muzzlePos.z, 1, 0, 0, 0, 0.0);
            serverLevel.sendParticles(net.minecraft.core.particles.ParticleTypes.FLASH, muzzlePos.x, muzzlePos.y, muzzlePos.z, 2, 0, 0, 0, 0.0);
        }

        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_SNIPER_FIRE.get(), SoundSource.PLAYERS, 7.0F, 0.92F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_RECOILLESS_FIRE.get(), SoundSource.PLAYERS, 5.0F, 0.65F);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(1.6F, 12);
        return true;
    }
}
