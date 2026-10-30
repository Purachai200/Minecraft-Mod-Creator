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

public class ExoframeRecoillessRifleItem extends ExoframeWeaponItem {

    public ExoframeRecoillessRifleItem(Properties properties) {
        super(properties.stacksTo(1), 28, "weapon_recoilless_rifle");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack util = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (util.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.ROCKET_84MM) {
            if (consume) {
                util.shrink(1);
                exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), util);
            }
            return true;
        }
        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack s = pilot.getInventory().getItem(i);
            if (s.getItem() instanceof ExoframeAmmoItem ammo && ammo.getAmmoType() == ExoframeAmmoItem.AmmoType.ROCKET_84MM) {
                if (consume) s.shrink(1);
                return true;
            }
        }
        return false;
    }

    @Override
    public boolean performFire(ExoframeEntity exoframe, ServerPlayer pilot) {
        if (!checkOrConsumeAmmo(exoframe, pilot, true)) {
            pilot.displayClientMessage(Component.literal("§c[Munitions Depleted] Required: 84mm HEAT Recoilless Rocket"), true);
            return false;
        }

        Level level = exoframe.level();
        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 muzzlePos = exoframe.position().add(0, 1.9D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.70D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(1.2D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(muzzlePos).normalize();

        ExoframeRocketEntity rocket = new ExoframeRocketEntity(level, pilot);
        rocket.setPos(muzzlePos.x, muzzlePos.y, muzzlePos.z);
        rocket.shoot(shootDir.x, shootDir.y, shootDir.z, 3.8F, 0.05F);
        level.addFreshEntity(rocket);

        level.playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_ROCKET_FIRE.get(), SoundSource.PLAYERS, 3.6F, 0.9F);
        exoframe.triggerRecoilAnim();
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.obsolete.exoframe_recoilless_rifle").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "84mm HEAT Recoilless Rocket").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
