package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeVibroBladeItem extends ExoframeWeaponItem {

    public ExoframeVibroBladeItem(Properties properties) {
        super(properties.stacksTo(1), 8, "weapon_vibro_blade");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        // Melee weapon requires no ammunition!
        return true;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        Level level = exoframe.level();
        exoframe.performMeleeAttack(pilot);

        Vec3 forward = pilot.getLookAngle().normalize();
        Vec3 strikeCenter = exoframe.position().add(0, 1.2D * ExoframeEntity.MODEL_SCALE, 0).add(forward.scale(1.8D * ExoframeEntity.MODEL_SCALE));
        double reach = 1.8D * ExoframeEntity.MODEL_SCALE;

        AABB strikeBox = new AABB(strikeCenter.x - reach, strikeCenter.y - reach, strikeCenter.z - reach,
                strikeCenter.x + reach, strikeCenter.y + reach, strikeCenter.z + reach);

        if (level instanceof ServerLevel serverLevel) {
            // Vibro-blade thermal particle sweep
            for (double angle = -0.6; angle <= 0.6; angle += 0.15) {
                Vec3 p = strikeCenter.add(forward.yRot((float) angle).scale(0.8));
                serverLevel.sendParticles(ParticleTypes.CRIT, p.x, p.y, p.z, 2, 0.1, 0.1, 0.1, 0.05);
                serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, p.x, p.y, p.z, 1, 0, 0, 0, 0.1);
            }

            List<LivingEntity> targets = serverLevel.getEntitiesOfClass(LivingEntity.class, strikeBox,
                    e -> e != exoframe && e != pilot && e.isAlive());

            for (LivingEntity target : targets) {
                target.hurt(level.damageSources().playerAttack(pilot), 32.0F);
                target.knockback(0.8F, -forward.x, -forward.z);
            }
        }

        level.playSound(null, exoframe.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 2.0F, 1.2F);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.obsolete.exoframe_vibro_blade").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§eTactical High-Frequency Melee: §fNo ammunition required").withStyle(ChatFormatting.YELLOW));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
