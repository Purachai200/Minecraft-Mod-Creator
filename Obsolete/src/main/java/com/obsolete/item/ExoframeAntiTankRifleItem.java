package com.obsolete.item;

import com.obsolete.entity.ExoframeBulletEntity;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** Long bolt-action 20mm anti-tank rifle: slow, three-round side box, hits harder than the semi-auto AMR. */
public class ExoframeAntiTankRifleItem extends ExoframeWeaponItem {

    public ExoframeAntiTankRifleItem(Properties properties) {
        super(properties.stacksTo(1), 34, "weapon_antitank_rifle"); // bolt cycle
    }

    @Override
    public int getMagazineCapacity() {
        return 3;
    }

    @Override
    public int getReloadDurationTicks() {
        return 70;
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
        Vec3 forward = pilot.getLookAngle().normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.8D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.6D * ExoframeEntity.MODEL_SCALE));
        Vec3 shootDir = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe).subtract(muzzlePos).normalize();

        ExoframeBulletEntity bullet = new ExoframeBulletEntity(level, pilot, 70.0F);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 10.0F, 0.02F);
        level.addFreshEntity(bullet);

        spawnMuzzleFlashAndCasing(level, muzzlePos, forward, right, true);
        if (level instanceof ServerLevel serverLevel) {
            // side-venting brake throws the blast sideways
            serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, muzzlePos.x, muzzlePos.y, muzzlePos.z, 10, right.x * 0.5, 0.05, right.z * 0.5, 0.06);
            serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, muzzlePos.x, muzzlePos.y, muzzlePos.z, 10, -right.x * 0.5, 0.05, -right.z * 0.5, 0.06);
            serverLevel.sendParticles(ParticleTypes.FLASH, muzzlePos.x, muzzlePos.y, muzzlePos.z, 1, 0, 0, 0, 0.0);
        }
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_SNIPER_FIRE.get(), SoundSource.PLAYERS, 7.5F, 0.78F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_AUTOCANNON_FIRE.get(), SoundSource.PLAYERS, 4.0F, 0.6F);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(2.0F, 14);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Bolt-action, 70 damage, side-venting brake").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "20mm AP Kinetic Shells").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
