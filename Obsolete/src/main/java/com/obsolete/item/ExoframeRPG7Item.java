package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.ExoframeRocketEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.sound.ModSounds;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

public class ExoframeRPG7Item extends ExoframeWeaponItem {

    public ExoframeRPG7Item(Properties properties) {
        super(properties.stacksTo(1), 35, "weapon_rpg7_heavy"); // 1.75s reload cooldown
    }

    @Override
    public int getMagazineCapacity() {
        return 1;
    }

    @Override
    public int getReloadDurationTicks() {
        return 65;
    }

    @Override
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return ExoframeAmmoItem.AmmoType.HEAVY_RPG_WARHEAD;
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
        Vec3 muzzlePos = exoframe.position().add(0, 1.9D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(0.9D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        ExoframeRocketEntity rocket = new ExoframeRocketEntity(level, pilot, 55.0F);
        rocket.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        rocket.shoot(shootDir.x, shootDir.y, shootDir.z, 3.2F, 0.15F);
        level.addFreshEntity(rocket);

        spawnRocketBackblast(level, muzzlePos, forward);

        float pitch = 0.95F + (exoframe.getRandom().nextFloat() * 0.1F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_ROCKET_FIRE.get(), SoundSource.PLAYERS, 3.2F, pitch);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.8F, 7);
        return true;
    }
}
