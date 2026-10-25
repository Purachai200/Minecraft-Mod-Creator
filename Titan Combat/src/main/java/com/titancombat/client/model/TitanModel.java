package com.titancombat.client.model;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.model.data.EntityModelData;

public class TitanModel<T extends BaseTitanEntity> extends GeoModel<T> {

    @Override
    public ResourceLocation getModelResource(T animatable) {
        String id = animatable.getTitanClass().getId();
        return new ResourceLocation(TitanCombatMod.MODID, "geo/" + id + "_titan.geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(T animatable) {
        String id = animatable.getTitanClass().getId();
        int camo = animatable.getCamoIndex();
        if (camo <= 0) {
            return new ResourceLocation(TitanCombatMod.MODID, "textures/entity/titan/" + id + "/" + id + "_titan.png");
        }
        return new ResourceLocation(TitanCombatMod.MODID, "textures/entity/titan/" + id + "/" + id + "_titan_" + camo + ".png");
    }

    @Override
    public ResourceLocation getAnimationResource(T animatable) {
        String id = animatable.getTitanClass().getId();
        return new ResourceLocation(TitanCombatMod.MODID, "animations/" + id + "_titan.animation.json");
    }

    /**
     * Runs after the keyframed clips each frame and layers the "live" parts on top:
     * which weapon copy is visible, the torso tracking the pilot's aim (as the addon's
     * titan_look_rotate does), and body lean from acceleration and turning.
     */
    @Override
    public void setCustomAnimations(T titan, long instanceId, AnimationState<T> state) {
        super.setCustomAnimations(titan, instanceId, state);

        boolean stowed = titan.isWeaponStowed();
        // A weapon from another chassis is drawn by TitanWeaponSwapLayer; hide this model's own gun copies.
        boolean swapped = com.titancombat.client.renderer.layer.TitanWeaponSwapLayer.isSwapped(titan);
        boolean unarmed = !titan.hasWeapon();
        setHidden("weapon", stowed || swapped || unarmed);
        setHidden("weaponBack", !stowed || swapped || unarmed);
        if (titan.getTitanClass() == TitanClass.TROOPER) {
            // One weapon bone, two tool models: show the one that is mounted.
            boolean saw = titan.getActiveWeapon() == com.titancombat.entity.TitanWeapon.CHAINSAW;
            setHidden("drill", saw);
            setHidden("chainsaw", !saw);
        }
        if (titan.getTitanClass() == TitanClass.RONIN) {
            boolean swordOut = titan.getEntityData().get(BaseTitanEntity.DATA_IS_MELEEING);
            setHidden("sword", !swordOut);
            setHidden("swordBack", swordOut);
        }

        applyFootPlacement(titan, state.getPartialTick());

        // Lowered weapon (H): natural low-ready hip carry with gun pointed down-forward.
        float lower = titan.getLowerBlend(state.getPartialTick());
        if (lower > 0.001F) {
            addRotation("rightArm1", 0.18F * lower, 0, 0.08F * lower);
            addRotation("rightArm2", 0.95F * lower, 0, 0);
            addRotation("leftArm1", 0.22F * lower, 0, -0.12F * lower);
            addRotation("leftArm2", 0.85F * lower, 0, 0);
        }

        // Unarmed locomotion: natural rhythmic arm swing at sides while walking/running
        if (unarmed && !titan.isKneeling() && !titan.isSaluting()) {
            float swing = Mth.cos(state.getLimbSwing() * 0.6662F) * 0.25F * state.getLimbSwingAmount();
            addRotation("rightArm1", -swing, 0, 0);
            addRotation("leftArm1", swing, 0, 0);
        }

        // Titan military salute pose
        int saluteTicks = titan.getSaluteTicks();
        if (saluteTicks > 0) {
            float progress = (45 - saluteTicks + state.getPartialTick()) / 45.0F;
            float blend = progress < 0.15F ? progress / 0.15F : (progress > 0.85F ? (1.0F - progress) / 0.15F : 1.0F);
            blend = Mth.clamp(blend, 0.0F, 1.0F);

            // Left arm stands firmly at crisp military attention along the side
            addRotation("leftArm1", 0.0F, 0.0F, -0.08F * blend);
            addRotation("leftArm2", -0.12F * blend, 0, 0);

            // Right arm raises smartly with elbow at shoulder height, hand touching visor edge
            addRotation("rightArm1", 1.65F * blend, -0.42F * blend, 1.10F * blend);
            addRotation("rightArm2", 1.60F * blend, 0.65F * blend, -0.25F * blend);
            addRotation("rightHand", -0.20F * blend, 0.45F * blend, 0.25F * blend);

            // Torso stands tall and proud at military attention
            addRotation("body3", -0.06F * blend, 0, 0);
        }

        float weight = titan.getProceduralWeight(state.getPartialTick());
        if (weight <= 0.001F) return;

        EntityModelData data = state.getData(DataTickets.ENTITY_MODEL_DATA);
        if (data != null) {
            // Upper torso pitches with the aim; the waist twists toward where the pilot looks while the legs catch up.
            addRotation("body3", Mth.clamp(data.headPitch(), -35.0F, 35.0F) * Mth.DEG_TO_RAD * weight, 0, 0);
            addRotation("body2", 0, Mth.clamp(data.netHeadYaw(), -60.0F, 60.0F) * Mth.DEG_TO_RAD * weight, 0);
        }
        float partial = state.getPartialTick();
        addRotation("body1", -titan.getLeanForward(partial) * Mth.DEG_TO_RAD * weight, 0, titan.getLeanSide(partial) * Mth.DEG_TO_RAD * weight);
    }

    /**
     * Uneven ground while standing: lower the pelvis until the foot over lower ground reaches it,
     * then bend the other leg (hip/knee/ankle) so its foot rests on the higher block instead of
     * sinking into it. Two-segment leg solved from the model's own joint pivots.
     */
    private void applyFootPlacement(T titan, float partial) {
        float drop = titan.getPelvisDrop(partial);
        if (drop > -0.01F && titan.getLegLift(true, partial) < 0.01F && titan.getLegLift(false, partial) < 0.01F) return;

        CoreGeoBone pelvis = getAnimationProcessor().getBone("body1");
        if (pelvis != null) {
            pelvis.setPosY(pelvis.getPosY() + drop * 16.0F);
            pelvis.resetStateChanges();
        }
        bendLeg("left", titan.getLegLift(true, partial) * 16.0F);
        bendLeg("right", titan.getLegLift(false, partial) * 16.0F);
    }

    private void bendLeg(String side, float liftPx) {
        if (liftPx < 0.2F) return;
        CoreGeoBone thigh = getAnimationProcessor().getBone(side + "Leg3");
        CoreGeoBone shin = getAnimationProcessor().getBone(side + "Leg2");
        CoreGeoBone foot = getAnimationProcessor().getBone(side + "Foot");
        if (thigh == null || shin == null || foot == null) return;

        float l1 = Math.max(4.0F, thigh.getPivotY() - shin.getPivotY());
        float l2 = Math.max(4.0F, shin.getPivotY() - foot.getPivotY());
        liftPx = Math.min(liftPx, (l1 + l2) * 0.8F);
        // Find thigh angle a (and shin angle b, keeping the foot under the hip) that shortens the leg by liftPx.
        float lo = 0.0F, hi = 1.4F, a = 0.0F, b = 0.0F;
        for (int i = 0; i < 12; i++) {
            a = (lo + hi) * 0.5F;
            b = (float) Math.asin(Mth.clamp(l1 * Mth.sin(a) / l2, -1.0F, 1.0F));
            float shortening = l1 * (1.0F - Mth.cos(a)) + l2 * (1.0F - Mth.cos(b));
            if (shortening < liftPx) lo = a; else hi = a;
        }
        // In-game, negative rotX swings a hanging limb forward: knee comes forward, foot stays flat.
        thigh.setRotX(thigh.getRotX() - a);
        shin.setRotX(shin.getRotX() + (a + b));
        foot.setRotX(foot.getRotX() - b);
        thigh.resetStateChanges();
        shin.resetStateChanges();
        foot.resetStateChanges();
    }

    private void setHidden(String name, boolean hidden) {
        CoreGeoBone bone = getAnimationProcessor().getBone(name);
        if (bone != null) bone.setHidden(hidden);
    }

    // Offsets stack on whatever the bone holds, so each edit clears GeckoLib's "changed" flag:
    // otherwise a bone the current clip doesn't key skips its reset next frame and the offsets
    // pile up every frame until the chassis spins/rolls.
    private void addRotation(String name, float x, float y, float z) {
        CoreGeoBone bone = getAnimationProcessor().getBone(name);
        if (bone == null) return;
        bone.setRotX(bone.getRotX() + x);
        bone.setRotY(bone.getRotY() + y);
        bone.setRotZ(bone.getRotZ() + z);
        bone.resetStateChanges();
    }
}
