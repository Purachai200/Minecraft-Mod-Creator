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
    public int getMagazineCapacity() {
        return 0;
    }

    @Override
    public ExoframeAmmoItem.AmmoType getRequiredAmmoType() {
        return null;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        exoframe.performMeleeAttack(pilot);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.obsolete.exoframe_vibro_blade").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§eTactical High-Frequency Melee: §fNo ammunition required").withStyle(ChatFormatting.YELLOW));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
