package com.obsolete.item;

import com.obsolete.entity.ExoframeBulletEntity;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.sound.ModSounds;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

public class ExoframeMinigunItem extends ExoframeWeaponItem {

    public ExoframeMinigunItem(Properties properties) {
        super(properties.stacksTo(1), 2, "weapon_minigun_m134"); // 2 ticks = 10 rounds/sec rapid fire
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        // Check utility slot first for 7.62mm minigun ammo or 20mm
        ItemStack utilStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilStack.getItem() instanceof ExoframeAmmoItem ammo &&
                (ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_762_MINIGUN || ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM)) {
            if (consume) {
                utilStack.shrink(1);
            }
            return true;
        }

        // Check pilot inventory
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack stack = pilot.getInventory().getItem(i);
            if (stack.getItem() instanceof ExoframeAmmoItem ammo &&
                    (ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_762_MINIGUN || ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM)) {
                if (consume) {
                    stack.shrink(1);
                }
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            exoframe.level().playSound(null, exoframe.blockPosition(), net.minecraft.sounds.SoundEvents.UI_BUTTON_CLICK.get(),
                    SoundSource.PLAYERS, 0.8F, 1.4F);
            return false;
        }

        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.7D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.1D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(exoframe.level(), pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        // Rapid fire 7.62mm minigun burst (damage 14.0F, speed 6.5F, spread 1.2F)
        ExoframeBulletEntity bullet = new ExoframeBulletEntity(exoframe.level(), pilot, 14.0F);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 6.5F, 1.2F);
        exoframe.level().addFreshEntity(bullet);

        // Rapid fire sound
        float pitch = 1.2F + (exoframe.getRandom().nextFloat() * 0.3F);
        exoframe.level().playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_RIFLE_FIRE.get(),
                SoundSource.PLAYERS, 1.8F, pitch);

        exoframe.triggerRecoilAnim();
        return true;
    }
}
