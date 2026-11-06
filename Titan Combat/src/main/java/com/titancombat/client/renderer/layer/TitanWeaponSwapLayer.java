package com.titancombat.client.renderer.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import com.titancombat.entity.TitanWeapon;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

import java.util.Optional;

/**
 * Draws a weapon taken from another chassis' model when a titan mounts a non-factory weapon, and the
 * Trooper's back howitzer on other chassis.
 * The donor gun geometry is attached where the titan's own gun would be: gripped in the right hand,
 * or on its back when stowed, aligned by the guns' grip/mount pivots. (TitanModel hides the titan's
 * own gun copies in that case.)
 */
public class TitanWeaponSwapLayer<T extends BaseTitanEntity> extends GeoRenderLayer<T> {
    private boolean drawing = false;

    public TitanWeaponSwapLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    public static boolean isSwapped(BaseTitanEntity titan) {
        TitanWeapon weapon = titan.getActiveWeapon();
        return weapon != null && weapon.getFactoryChassis() != titan.getTitanClass();
    }

    @Override
    public void renderForBone(PoseStack poseStack, T titan, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                              VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (this.drawing || titan.isInvisible()) return;
        BakedGeoModel own = getDefaultBakedModel(titan);

        // Howitzer & Rocket Pod back modules on other chassis
        boolean isFrameOrTrooper = titan.getTitanClass() == TitanClass.TROOPER
                || titan instanceof com.titancombat.entity.TitanFrameEntity;

        if (titan.hasHowitzer() && !isFrameOrTrooper) {
            Optional<GeoBone> anchor = own.getBone("weaponBack");
            if (anchor.isPresent() && anchor.get().getParent() == bone) {
                drawDonorPart(poseStack, titan, TitanClass.TROOPER, "artillery", anchor.get(), null, renderType, bufferSource,
                        partialTick, packedLight, packedOverlay);
            }
        }
        if (titan.hasRocketPod() && !isFrameOrTrooper) {
            Optional<GeoBone> anchor = own.getBone("weaponBack");
            if (anchor.isPresent() && anchor.get().getParent() == bone) {
                drawDonorPart(poseStack, titan, TitanClass.TROOPER, "back_rocket_pod", anchor.get(), null, renderType, bufferSource,
                        partialTick, packedLight, packedOverlay);
            }
        }

        if (!isSwapped(titan)) return;
        String ownPart = titan.isWeaponStowed() ? "weaponBack" : "weapon";
        Optional<GeoBone> ownGun = own.getBone(ownPart);
        if (ownGun.isEmpty() || ownGun.get().getParent() == null || ownGun.get().getParent() != bone) return;
        TitanWeapon weapon = titan.getActiveWeapon();
        drawDonorPart(poseStack, titan, weapon.getFactoryChassis(), ownPart, ownGun.get(), weapon, renderType, bufferSource,
                partialTick, packedLight, packedOverlay);
    }

    /** Draws bone `donorPart` of the donor chassis' model with its pivot on `target` (a bone of this titan). */
    private void drawDonorPart(PoseStack poseStack, T titan, TitanClass donor, String donorPart, GeoBone target,
                               @org.jetbrains.annotations.Nullable TitanWeapon weapon, RenderType renderType,
                               MultiBufferSource bufferSource, float partialTick, int packedLight, int packedOverlay) {
        BakedGeoModel donorModel = GeckoLibCache.getBakedModels().get(
                new ResourceLocation(TitanCombatMod.MODID, "geo/" + donor.getId() + "_titan.geo.json"));
        if (donorModel == null) return;
        Optional<GeoBone> donorGun = donorModel.getBone(donorPart);
        if (donorGun.isEmpty()) return;

        GeoBone gun = donorGun.get();
        boolean wasHidden = gun.isHidden();
        boolean wasHidingChildren = gun.isHidingChildren();
        float sx = gun.getScaleX(), sy = gun.getScaleY(), sz = gun.getScaleZ();

        // The Trooper's weapon bone holds tools and custom weapons; draw only the mounted one.
        if (weapon != null) {
            for (TitanWeapon w : TitanWeapon.values()) {
                if (w.getModelBone() != null) donorModel.getBone(w.getModelBone()).ifPresent(b -> b.setHidden(weapon != w));
            }

            donorModel.getBone("stowed_rifle").ifPresent(b -> b.setHidden(weapon != TitanWeapon.HEAVY_ASSAULT_RIFLE));
            donorModel.getBone("stowed_machine_gun").ifPresent(b -> b.setHidden(weapon != TitanWeapon.ROTARY_MACHINE_GUN));
            donorModel.getBone("stowed_rocket_launcher").ifPresent(b -> b.setHidden(weapon != TitanWeapon.ROCKET_POD));
        }

        this.drawing = true;
        poseStack.pushPose();
        try {
            // Line the donor gun's grip/mount point up with where this chassis holds its own gun.
            poseStack.translate((target.getPivotX() - gun.getPivotX()) / 16.0F,
                    (target.getPivotY() - gun.getPivotY()) / 16.0F,
                    (target.getPivotZ() - gun.getPivotZ()) / 16.0F);
            gun.setScaleX(1.0F);
            gun.setScaleY(1.0F);
            gun.setScaleZ(1.0F);
            gun.setHidden(false);
            RenderType donorType = RenderType.entityCutoutNoCull(donorTexture(donor, titan.getCamoIndex()));
            VertexConsumer donorBuffer = bufferSource.getBuffer(donorType);
            getRenderer().renderRecursively(poseStack, titan, gun, donorType, bufferSource, donorBuffer, false, partialTick,
                    packedLight, packedOverlay, 1.0F, 1.0F, 1.0F, 1.0F);
        } finally {
            gun.setHidden(wasHidden);
            gun.setChildrenHidden(wasHidingChildren);
            gun.setScaleX(sx);
            gun.setScaleY(sy);
            gun.setScaleZ(sz);
            poseStack.popPose();
            this.drawing = false;
            // Switch the shared buffer back to this titan's own texture for the rest of the model.
            bufferSource.getBuffer(renderType);
        }
    }

    private static ResourceLocation donorTexture(TitanClass donor, int camo) {
        String id = donor.getId();
        String file = camo <= 0 ? id + "_titan.png" : id + "_titan_" + camo + ".png";
        return new ResourceLocation(TitanCombatMod.MODID, "textures/entity/titan/" + id + "/" + file);
    }
}
