package com.obsolete.item;

import com.obsolete.entity.ExoframeBulletEntity;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.sound.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;

public class ExoframeAssaultRifleItem extends ExoframeWeaponItem {

    public ExoframeAssaultRifleItem(Properties properties) {
        super(properties.stacksTo(1), 5, "exoframe_assault_rifle");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        // 1. Check Exoframe utility slot (slot index 4)
        ItemStack utilityStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilityStack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM) {
            if (consume) {
                utilityStack.shrink(1);
                exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), utilityStack);
            }
            return true;
        }

        // 2. Check pilot player inventory
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack stack = pilot.getInventory().getItem(i);
            if (stack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM) {
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
            pilot.displayClientMessage(Component.translatable("message.obsolete.out_of_ammo_20mm").withStyle(ChatFormatting.RED), true);
            return false;
        }

        Level level = exoframe.level();
        Vec3 look = pilot.getLookAngle();
        // Weapon muzzle position: offset to right arm weapon mount
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.8D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(0.9D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        ExoframeBulletEntity bullet = new ExoframeBulletEntity(level, pilot);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 4.5F, 0.4F);
        level.addFreshEntity(bullet);

        // Sound & recoil
        level.playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_RIFLE_FIRE.get(), SoundSource.PLAYERS, 2.5F, 1.0F);
        exoframe.triggerRecoilAnim();
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.weapon_rifle_desc").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "20mm AP Kinetic Shells").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
