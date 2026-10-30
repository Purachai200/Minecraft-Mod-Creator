package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.ExoframeRocketEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.sound.ModSounds;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;

public class ExoframeRPG7Item extends ExoframeWeaponItem {

    public ExoframeRPG7Item(Properties properties) {
        super(properties.stacksTo(1), 35, "weapon_rpg7_heavy"); // 1.75s reload cooldown
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        // Check utility slot first for RPG warhead or rocket
        ItemStack utilStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilStack.getItem() instanceof ExoframeAmmoItem ammo &&
                (ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.HEAVY_RPG_WARHEAD || ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.AT_ROCKET)) {
            if (consume) {
                utilStack.shrink(1);
            }
            return true;
        }

        // Check pilot inventory
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack stack = pilot.getInventory().getItem(i);
            if (stack.getItem() instanceof ExoframeAmmoItem ammo &&
                    (ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.HEAVY_RPG_WARHEAD || ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.AT_ROCKET)) {
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
                    SoundSource.PLAYERS, 1.0F, 1.2F);
            return false;
        }

        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.9D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(0.9D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(exoframe.level(), pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        // Spawn heavy shaped-charge demolition rocket
        ExoframeRocketEntity rocket = new ExoframeRocketEntity(exoframe.level(), pilot, 55.0F);
        rocket.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        rocket.shoot(shootDir.x, shootDir.y, shootDir.z, 3.2F, 0.15F);
        exoframe.level().addFreshEntity(rocket);

        // Heavy rocket backblast launch sound
        exoframe.level().playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_ROCKET_FIRE.get(),
                SoundSource.PLAYERS, 2.5F, 0.9F);

        exoframe.triggerRecoilAnim();
        return true;
    }
}
