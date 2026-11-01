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

public class ExoframeMachineGunItem extends ExoframeWeaponItem {

    public ExoframeMachineGunItem(Properties properties) {
        super(properties.stacksTo(1), 2, "weapon_machine_gun");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack utilityStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilityStack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_20MM) {
            if (consume) {
                utilityStack.shrink(1);
                exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), utilityStack);
            }
            return true;
        }

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
        Level level = exoframe.level();
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_EMPTY_CLICK.get(), SoundSource.PLAYERS, 1.2F, 1.0F);
            pilot.displayClientMessage(Component.translatable("message.obsolete.out_of_ammo_20mm").withStyle(ChatFormatting.RED), true);
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

        ExoframeBulletEntity bullet = new ExoframeBulletEntity(level, pilot);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        // Slight spread for high-rate heavy machine gun
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 4.2F, 1.2F);
        level.addFreshEntity(bullet);

        spawnMuzzleFlashAndCasing(level, muzzlePos, forward, right, true);

        float pitch = 1.1F + (exoframe.getRandom().nextFloat() * 0.2F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_RIFLE_FIRE.get(), SoundSource.PLAYERS, 2.2F, pitch);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.25F, 2);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.machine_gun_desc").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "20mm AP Kinetic Shells").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
