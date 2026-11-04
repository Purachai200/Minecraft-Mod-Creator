package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * Four-tube 66mm smoke discharger: each shot drops a smoke canister on the aim point (up to 48 blocks).
 * The screen blinds and slows hostiles caught in the burst, then lingers as a cloud for 12 s.
 */
public class ExoframeSmokeLauncherItem extends ExoframeWeaponItem {
    public static final float SMOKE_RADIUS = 4.0F;

    public ExoframeSmokeLauncherItem(Properties properties) {
        super(properties.stacksTo(1), 16, "weapon_smoke_launcher");
    }

    @Override
    public int getMagazineCapacity() {
        return 4;
    }

    @Override
    public int getReloadDurationTicks() {
        return 60;
    }

    @Override
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return ExoframeAmmoItem.AmmoType.GRENADE_40MM;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        Level level = exoframe.level();
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            return false;
        }
        Vec3 forward = pilot.getLookAngle().normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.9D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(0.9D * ExoframeEntity.MODEL_SCALE));
        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        if (target.distanceTo(muzzlePos) > 48.0D) {
            target = muzzlePos.add(target.subtract(muzzlePos).normalize().scale(48.0D));
        }

        AreaEffectCloud cloud = new AreaEffectCloud(level, target.x, target.y, target.z);
        cloud.setOwner(pilot);
        cloud.setParticle(ParticleTypes.LARGE_SMOKE);
        cloud.setRadius(SMOKE_RADIUS);
        cloud.setRadiusPerTick(0.0F);
        cloud.setDuration(240);
        cloud.setWaitTime(0);
        level.addFreshEntity(cloud);

        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, new AABB(target, target).inflate(SMOKE_RADIUS),
                e -> e != exoframe && e != pilot && !exoframe.isAlliedTo(e))) {
            e.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 120, 0));
            e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 120, 1));
        }

        if (level instanceof ServerLevel serverLevel) {
            serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, target.x, target.y + 0.5, target.z, 40, SMOKE_RADIUS * 0.4, 0.8, SMOKE_RADIUS * 0.4, 0.02);
            serverLevel.sendParticles(ParticleTypes.POOF, muzzlePos.x, muzzlePos.y, muzzlePos.z, 8, 0.1, 0.1, 0.1, 0.05);
        }
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_GRENADE_THUMP.get(), SoundSource.PLAYERS, 2.4F, 0.8F);
        exoframe.triggerRecoilAnim();
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Drops a 4-block smoke screen on the aim point; blinds hostiles inside").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "40mm Grenade Rounds (smoke-loaded)").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
