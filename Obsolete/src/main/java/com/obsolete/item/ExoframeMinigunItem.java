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

public class ExoframeMinigunItem extends ExoframeWeaponItem {

    public ExoframeMinigunItem(Properties properties) {
        super(properties.stacksTo(1), 2, "weapon_minigun_m134"); // 2 ticks = 10 rounds/sec rapid fire
    }

    @Override
    public boolean isAutomatic() {
        return true;
    }

    @Override
    public int getMagazineCapacity() {
        return 150;
    }

    @Override
    public int getReloadDurationTicks() {
        return 90;
    }

    @Override
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return ExoframeAmmoItem.AmmoType.CALIBER_762_MINIGUN;
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
        Vec3 muzzlePos = exoframe.position().add(0, 1.7D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.1D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        // Rapid fire 7.62mm minigun burst (damage 14.0F, speed 6.5F, spread 1.2F)
        ExoframeBulletEntity bullet = new ExoframeBulletEntity(level, pilot, 14.0F);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 6.5F, 1.2F);
        level.addFreshEntity(bullet);

        spawnMuzzleFlashAndCasing(level, muzzlePos, forward, right, true);

        float pitch = 0.95F + (exoframe.getRandom().nextFloat() * 0.15F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_MINIGUN_FIRE.get(), SoundSource.PLAYERS, 2.0F, pitch);

        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.2F, 2);
        return true;
    }
}
