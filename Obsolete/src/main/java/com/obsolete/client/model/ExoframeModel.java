package com.obsolete.client.model;

import com.obsolete.ObsoleteMod;
import com.obsolete.entity.ExoframeEntity;
import com.obsolete.entity.inventory.ExoframeArmorSlot;
import com.obsolete.item.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

public class ExoframeModel extends GeoModel<ExoframeEntity> {

    @Override
    public ResourceLocation getModelResource(ExoframeEntity animatable) {
        return new ResourceLocation(ObsoleteMod.MODID, "geo/exoframe.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(ExoframeEntity animatable) {
        int camo = animatable.getCamoPattern();
        return switch (camo) {
            case 1 -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe_woodland.png");
            case 2 -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe_desert.png");
            case 3 -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe_urban.png");
            case 4 -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe_arctic.png");
            case 5 -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe_tigerstripe.png");
            case 6 -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe_hazard.png");
            default -> new ResourceLocation(ObsoleteMod.MODID, "textures/entity/exoframe/exoframe.png");
        };
    }

    @Override
    public ResourceLocation getAnimationResource(ExoframeEntity animatable) {
        return new ResourceLocation(ObsoleteMod.MODID, "animations/exoframe.animation.json");
    }

    @Override
    public void setCustomAnimations(ExoframeEntity exoframe, long instanceId, AnimationState<ExoframeEntity> state) {
        super.setCustomAnimations(exoframe, instanceId, state);

        // Check if the local client player is currently piloting in first-person view.
        // In first-person cockpit view, hide the overhead canopy so the pilot has an unobstructed tactical view.
        boolean isFirstPersonPilot = false;
        try {
            net.minecraft.client.Minecraft mc = net.minecraft.client.Minecraft.getInstance();
            if (mc.player != null && mc.player.getVehicle() == exoframe && mc.options.getCameraType().isFirstPerson()) {
                isFirstPersonPilot = true;
            }
        } catch (Throwable ignored) {}

        // ==================== DATA-DRIVEN ARMOR & MODULE VARIANTS ====================
        java.util.Set<String> visibleBones = new java.util.HashSet<>();
        boolean shouldHideFrameHead = false;

        for (ExoframeArmorSlot slot : ExoframeArmorSlot.values()) {
            if (slot == ExoframeArmorSlot.MAIN_WEAPON) continue;
            ItemStack stack = exoframe.getModularInventory().getStackInSlot(slot.getIndex());
            if (stack.isEmpty()) continue;

            com.obsolete.registry.ExoframeVariantRegistry.ArmorVariantData data =
                    com.obsolete.registry.ExoframeVariantRegistry.getArmorData(stack.getItem());
            if (data != null) {
                for (String b : data.visibleBones()) {
                    if (isFirstPersonPilot && data.firstPersonHiddenBones().contains(b)) {
                        continue;
                    }
                    visibleBones.add(b);
                }
                if (data.hidesFrameHead()) {
                    shouldHideFrameHead = true;
                }
            } else if (slot == ExoframeArmorSlot.UTILITY) {
                // Fallback for utility items: AmmoItem -> backpack_ammo, other item -> backpack_cargo
                if (stack.getItem() instanceof ExoframeAmmoItem) {
                    visibleBones.add("backpack_ammo");
                } else {
                    visibleBones.add("backpack_cargo");
                }
            }
        }

        // Apply visibility for all known armor bones
        for (String armorBone : com.obsolete.registry.ExoframeVariantRegistry.getAllKnownArmorBones()) {
            setHidden(armorBone, !visibleBones.contains(armorBone));
        }

        // Frame head handling: bare frame has NO head; head is hidden unless head armor brings a sensor, or if chest piece replaces it
        boolean hasHeadArmor = !exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.HEAD.getIndex()).isEmpty();
        setHidden("head", !hasHeadArmor || shouldHideFrameHead);
        if (shouldHideFrameHead) {
            for (com.obsolete.registry.ExoframeVariantRegistry.ArmorVariantData d : com.obsolete.registry.ExoframeVariantRegistry.getAllArmorData()) {
                if (d.slot() == ExoframeArmorSlot.HEAD) {
                    for (String b : d.visibleBones()) {
                        setHidden(b, true);
                    }
                }
            }
        }

        // ==================== DATA-DRIVEN WEAPONS & WORKING TOOLS ====================
        ItemStack weaponStack = exoframe.getModularInventory().getStackInSlot(ExoframeArmorSlot.MAIN_WEAPON.getIndex());
        String activeWeaponBone = null;
        if (!weaponStack.isEmpty()) {
            com.obsolete.registry.ExoframeVariantRegistry.WeaponVariantData wData =
                    com.obsolete.registry.ExoframeVariantRegistry.getWeaponData(weaponStack.getItem());
            if (wData != null) {
                activeWeaponBone = wData.weaponBoneName();
            }
        }

        for (String wBone : com.obsolete.registry.ExoframeVariantRegistry.getAllKnownWeaponBones()) {
            setHidden(wBone, !wBone.equals(activeWeaponBone));
        }

        // Pitch tracking: Minecraft pitch is negative looking up, positive looking down.
        // In OpenGL/GeckoLib, positive X rotation tilts barrel UP, negative tilts DOWN.
        float pilotPitch = exoframe.getXRot();
        float targetPitch = -pilotPitch * ((float) Math.PI / 180.0F);
        targetPitch = net.minecraft.util.Mth.clamp(targetPitch, -1.05F, 1.15F);

        // Visual firing recoil kick (sharp 6-tick impulse)
        int recoilTickDiff = exoframe.tickCount - exoframe.getEntityData().get(ExoframeEntity.DATA_RECOIL_TICK);
        float recoilKick = 0.0F;
        if (recoilTickDiff >= 0 && recoilTickDiff < 6) {
            recoilKick = (6 - recoilTickDiff) * 0.035F;
        }

        // ==================== 7. SHOULDER MISSILE POD DYNAMICS ====================
        // When aiming (ADS), shoulder launchers elevate/depress along with the line of sight.
        for (String podBone : new String[]{"backpack_missile_pod", "backpack_manpads"}) {
            CoreGeoBone missilePod = getAnimationProcessor().getBone(podBone);
            if (missilePod != null) {
                missilePod.setRotX(exoframe.isAiming() ? targetPitch * 0.85F : 0.0F);
            }
        }

        // ==================== 8. WEAPON HANDLING ====================
        // Poses are hand targets + gun direction; both arms are solved so the grip sits in the right fist
        // and the left hand lands on the weapon's support point (see ExoframeArmIK).
        if (!weaponStack.isEmpty()) {
            boolean emoting = exoframe.getAnimatableInstanceCache().getManagerForId(instanceId)
                    .getAnimationControllers().get(ExoframeEntity.EMOTE_CONTROLLER).isPlayingTriggeredAnimation();
            ExoframeArmIK.pose(this::bone, exoframe, weaponStack.getItem(), state.getPartialTick(),
                    state.getLimbSwingAmount(), targetPitch, recoilKick, recoilTickDiff >= 0 && recoilTickDiff < 8, emoting);
        } else {
            ExoframeArmIK.clearMount(bone("right_hand_weapon_mount"));
        }
    }

    private CoreGeoBone bone(String name) {
        return getAnimationProcessor().getBone(name);
    }

    private void setShinsHidden(String faction, boolean hidden) {
        setHidden("armor_left_shin_" + faction, hidden);
        setHidden("armor_right_shin_" + faction, hidden);
    }

    private void setHidden(String boneName, boolean hidden) {
        CoreGeoBone bone = getAnimationProcessor().getBone(boneName);
        if (bone != null) {
            bone.setHidden(hidden);
        }
    }
}
