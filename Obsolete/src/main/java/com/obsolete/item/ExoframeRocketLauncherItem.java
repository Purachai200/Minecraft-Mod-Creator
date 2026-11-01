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

public class ExoframeRocketLauncherItem extends ExoframeWeaponItem {

    public ExoframeRocketLauncherItem(Properties properties) {
        super(properties.stacksTo(1), 30, "exoframe_rocket_launcher");
    }

    @Override
    public boolean checkOrConsumeAmmo(ExoframeEntity exoframe, ServerPlayer pilot, boolean consume) {
        ItemStack utilityStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.UTILITY.getIndex());
        if (utilityStack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.AT_ROCKET) {
            if (consume) {
                utilityStack.shrink(1);
                exoframe.getModularInventory().setStackInSlot(ExoframeArmorSlot.UTILITY.getIndex(), utilityStack);
            }
            return true;
        }

        for (int i = 0; i < pilot.getInventory().getContainerSize(); i++) {
            ItemStack stack = pilot.getInventory().getItem(i);
            if (stack.getItem() instanceof ExoframeAmmoItem ammoItem && ammoItem.getAmmoType() == ExoframeAmmoItem.AmmoType.AT_ROCKET) {
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
            pilot.displayClientMessage(Component.translatable("message.obsolete.out_of_ammo_rocket").withStyle(ChatFormatting.RED), true);
            return false;
        }

        Vec3 look = pilot.getLookAngle();
        Vec3 forward = look.normalize();
        Vec3 right = new Vec3(-forward.z, 0, forward.x).normalize();
        Vec3 podPos = exoframe.position().add(0, 2.1D * ExoframeEntity.MODEL_SCALE, 0)
                .add(right.scale(0.75D * ExoframeEntity.MODEL_SCALE))
                .add(forward.scale(0.6D * ExoframeEntity.MODEL_SCALE));

        Vec3 target = ExoframeEntity.computeTargetConvergence(level, pilot, exoframe);
        Vec3 shootDir = target.subtract(podPos).normalize();

        ExoframeRocketEntity rocket = new ExoframeRocketEntity(level, pilot);
        rocket.setPos(podPos.x, podPos.y, podPos.z);
        rocket.shoot(shootDir.x, shootDir.y, shootDir.z, 2.4F, 0.1F);
        level.addFreshEntity(rocket);

        spawnRocketBackblast(level, podPos, forward);

        float pitch = 0.95F + (exoframe.getRandom().nextFloat() * 0.1F);
        level.playSound(null, exoframe.blockPosition(), ModSounds.EXOFRAME_ROCKET_FIRE.get(), SoundSource.PLAYERS, 3.0F, pitch);
        exoframe.triggerRecoilAnim();
        exoframe.triggerPilotCameraShake(0.7F, 6);
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, @Nullable Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("tooltip.obsolete.weapon_rocket_desc").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("tooltip.obsolete.required_ammo", "Anti-Tank Guided Missile").withStyle(ChatFormatting.GOLD));
        super.appendHoverText(stack, level, tooltip, flag);
    }
}
