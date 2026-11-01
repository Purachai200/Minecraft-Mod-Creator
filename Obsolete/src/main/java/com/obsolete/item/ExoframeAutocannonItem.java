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

public class ExoframeAutocannonItem extends ExoframeWeaponItem {

    public ExoframeAutocannonItem(Properties properties) {
        super(properties.stacksTo(1), 8, "weapon_autocannon_30mm");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack util = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (util.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_30MM) {
            if (consume) {
                util.shrink(1);
                exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), util);
            }
            return true;
        }
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack s = pilot.getInventory().getItem(i);
            if (s.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.CALIBER_30MM) {
                if (consume) s.shrink(1);
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
            pilot.displayClientMessage(Component.literal("§c[Munitions Depleted] Required: 30mm HE Autocannon Rounds"), true);
            return false;
        }

        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.7D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.72D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.3D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        ExoframeBulletEntity bullet = new ExoframeBulletEntity(level, pilot);
        bullet.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        bullet.shoot(shootDir.x, shootDir.y, shootDir.z, 4.6F, 0.25F);
        level.addFreshEntity(bullet);

        spawnMuzzleFlashAndCasing(level, muzzlePos, forward, right, true);

        float pitch = 0.95F + (exoframe.getRandom().nextFloat() * 0.1F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_AUTOCANNON_FIRE.get(), SoundSource.PLAYERS, 3.2F, pitch);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.6F, 5);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.obsolete.exoframe_autocannon_30mm").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "30mm HE Autocannon Rounds").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
