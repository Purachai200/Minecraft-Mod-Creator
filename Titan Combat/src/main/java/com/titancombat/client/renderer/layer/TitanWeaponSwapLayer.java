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
 * Draws a weapon taken from another chassis' model when a titan mounts a non-factory weapon.
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
        if (this.drawing || !isSwapped(titan)) return;

        boolean stowed = titan.isWeaponStowed();
        String ownPart = stowed ? "weaponBack" : "weapon";
        BakedGeoModel own = getDefaultBakedModel(titan);
        Optional<GeoBone> ownGun = own.getBone(ownPart);
        if (ownGun.isEmpty() || ownGun.get().getParent() == null || ownGun.get().getParent() != bone) return;

        TitanWeapon weapon = titan.getActiveWeapon();
        TitanClass donor = weapon.getFactoryChassis();
        BakedGeoModel donorModel = GeckoLibCache.getBakedModels().get(
                new ResourceLocation(TitanCombatMod.MODID, "geo/" + donor.getId() + "_titan.geo.json"));
        if (donorModel == null) return;
        Optional<GeoBone> donorGun = donorModel.getBone(ownPart);
        if (donorGun.isEmpty()) return;

        GeoBone gun = donorGun.get();
        GeoBone target = ownGun.get();
        boolean wasHidden = gun.isHidden();
        boolean wasHidingChildren = gun.isHidingChildren();

        this.drawing = true;
        poseStack.pushPose();
        try {
            // Line the donor gun's grip/mount point up with where this chassis holds its own gun.
            poseStack.translate((target.getPivotX() - gun.getPivotX()) / 16.0F,
                    (target.getPivotY() - gun.getPivotY()) / 16.0F,
                    (target.getPivotZ() - gun.getPivotZ()) / 16.0F);
            gun.setHidden(false);
            RenderType donorType = RenderType.entityCutoutNoCull(donorTexture(donor, titan.getCamoIndex()));
            VertexConsumer donorBuffer = bufferSource.getBuffer(donorType);
            getRenderer().renderRecursively(poseStack, titan, gun, donorType, bufferSource, donorBuffer, false, partialTick,
                    packedLight, packedOverlay, 1.0F, 1.0F, 1.0F, 1.0F);
        } finally {
            gun.setHidden(wasHidden);
            gun.setChildrenHidden(wasHidingChildren);
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
