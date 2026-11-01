package com.obsolete.item;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.ExoframeRocketEntity;
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

public class ExoframeGrenadeLauncherItem extends ExoframeWeaponItem {

    public ExoframeGrenadeLauncherItem(Properties properties) {
        super(properties.stacksTo(1), 12, "weapon_grenade_launcher");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack util = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (util.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.GRENADE_40MM) {
            if (consume) {
                util.shrink(1);
                exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), util);
            }
            return true;
        }
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack s = pilot.getInventory().getItem(i);
            if (s.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.GRENADE_40MM) {
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
            pilot.displayClientMessage(Component.literal("§c[Munitions Depleted] Required: 40mm HE Grenade Rounds"), true);
            return false;
        }

        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.8D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.65D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.1D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        ExoframeRocketEntity grenade = new ExoframeRocketEntity(level, pilot);
        grenade.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        grenade.shoot(shootDir.x, shootDir.y, shootDir.z, 2.8F, 0.02F);
        level.addFreshEntity(grenade);

        spawnMuzzleFlashAndCasing(level, muzzlePos, forward, right, false);

        float pitch = 0.95F + (exoframe.getRandom().nextFloat() * 0.1F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.WEAPON_GRENADE_THUMP.get(), SoundSource.PLAYERS, 2.6F, pitch);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.4F, 4);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.obsolete.exoframe_grenade_launcher").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "40mm HE Grenade Rounds").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
