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
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack utilStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilStack.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM) {
            if (consume) {
                utilStack.shrink(1);
            }
            return true;
        }

        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack stack = pilot.getInventory().getItem(i);
            if (stack.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM) {
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
        Level level = exoframe.level();
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_EMPTY_CLICK.get(), SoundSource.PLAYERS, 1.2F, 1.0F);
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

        // Loud sniper firing report
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_SNIPER_FIRE.get(), SoundSource.PLAYERS, 3.5F, 1.0F);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.8F, 7);
        return true;
    }
}
