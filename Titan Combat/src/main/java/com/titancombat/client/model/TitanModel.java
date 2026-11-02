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
    /** Standing crouch in blocks (1.5 px): loads the knees without moving the hitbox or cockpit eye noticeably. */
    private static final float STANCE_CROUCH = 1.5F / 16.0F;
    /** Barrel elevation baked into trooper_titan.geo.json (build_trooper_assets.ARTILLERY_ELEVATION). */
    private static final float HOWITZER_REST_ELEVATION = 35.0F * Mth.DEG_TO_RAD;
    /** Howitzer firing stance: extra squat (blocks), leg spread (radians), how long it holds after a shot and eases. */
    private static final float BRACE_CROUCH = 7.0F / 16.0F;
    private static final float BRACE_SPREAD = 0.20F;
    private static final int BRACE_HOLD_TICKS = 40;
    private static final float BRACE_EASE_TICKS = 10.0F;
    /** Turret/barrel slew rate: ~105 degrees in Howitzer.LAYING_TICKS (30). */
    private static final float HOWITZER_SLEW_PER_TICK = 3.5F * Mth.DEG_TO_RAD;

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
        // Howitzer & Rocket Pod back modules
        boolean artillery = titan.hasHowitzer();
        setHidden("artillery", !artillery);
        boolean rocketPod = titan.hasRocketPod();
        setHidden("back_rocket_pod", !rocketPod);
        if (titan instanceof com.titancombat.entity.TitanFrameEntity frame) {
            setHidden("armor_head", !frame.hasHeadArmor());
            setHidden("armor_chest", !frame.hasChestArmor());
            setHidden("armor_arms", !frame.hasArmsArmor());
            setHidden("armor_left_arm", !frame.hasArmsArmor());
            setHidden("armor_right_arm", !frame.hasArmsArmor());
            setHidden("armor_legs", !frame.hasLegsArmor());
            setHidden("armor_left_leg", !frame.hasLegsArmor());
            setHidden("armor_right_leg", !frame.hasLegsArmor());

            com.titancombat.entity.TitanArmorArchetype headArch = frame.getHeadTheme().getArchetype();
            com.titancombat.entity.TitanArmorArchetype chestArch = frame.getChestTheme().getArchetype();
            com.titancombat.entity.TitanArmorArchetype armsArch = frame.getArmsTheme().getArchetype();
            com.titancombat.entity.TitanArmorArchetype legsArch = frame.getLegsTheme().getArchetype();

            for (com.titancombat.entity.TitanArmorArchetype arch : com.titancombat.entity.TitanArmorArchetype.values()) {
                String aid = arch.getId();
                setHidden("armor_head_" + aid, !frame.hasHeadArmor() || headArch != arch);
                setHidden("armor_chest_" + aid, !frame.hasChestArmor() || chestArch != arch);
                setHidden("armor_left_arm_" + aid, !frame.hasArmsArmor() || armsArch != arch);
                setHidden("armor_right_arm_" + aid, !frame.hasArmsArmor() || armsArch != arch);
                setHidden("armor_left_leg_" + aid, !frame.hasLegsArmor() || legsArch != arch);
                setHidden("armor_right_leg_" + aid, !frame.hasLegsArmor() || legsArch != arch);
            }
        }
        boolean isTrooperOrFrame = titan.getTitanClass() == TitanClass.TROOPER
                || titan instanceof com.titancombat.entity.TitanFrameEntity;
        if (isTrooperOrFrame) {
            // Weapon bones: show only the currently mounted one
            com.titancombat.entity.TitanWeapon wep = titan.getActiveWeapon();
            boolean saw = wep == com.titancombat.entity.TitanWeapon.CHAINSAW;
            boolean drill = wep == com.titancombat.entity.TitanWeapon.MINING_DRILL;
            boolean rifle = wep == com.titancombat.entity.TitanWeapon.HEAVY_ASSAULT_RIFLE;
            boolean mg = wep == com.titancombat.entity.TitanWeapon.ROTARY_MACHINE_GUN;
            boolean rocket = wep == com.titancombat.entity.TitanWeapon.ROCKET_POD;

            setHidden("drill", !drill || stowed || swapped || unarmed);
            setHidden("chainsaw", !saw || stowed || swapped || unarmed);
            setHidden("rifle", !rifle || stowed || swapped || unarmed);
            setHidden("machine_gun", !mg || stowed || swapped || unarmed);
            setHidden("rocket_launcher", !rocket || stowed || swapped || unarmed);

            setHidden("stowed_rifle", !stowed || swapped || unarmed || !rifle);
            setHidden("stowed_machine_gun", !stowed || swapped || unarmed || !mg);
            setHidden("stowed_rocket_launcher", !stowed || swapped || unarmed || !rocket);
        }
        if (titan.getTitanClass() == TitanClass.SHADE) {
            // Cloak streams back with speed and ripples gently while idle.
            double speed = titan.getDeltaMovement().horizontalDistance();
            float t = titan.tickCount + state.getPartialTick();
            float lift = (float) Math.min(1.1D, speed * 2.5D);
            addRotation("cape", -(lift + 0.05F + 0.04F * Mth.sin(t * 0.12F)), 0, 0.03F * Mth.sin(t * 0.09F));
        }
        if (titan.getTitanClass() == TitanClass.RONIN) {
            boolean swordOut = titan.getEntityData().get(BaseTitanEntity.DATA_IS_MELEEING);
            setHidden("sword", !swordOut);
            setHidden("swordBack", swordOut);
        }

        BaseTitanEntity.Gait gait = titan.getGait();
        // Not in the jump-jet/fall tuck (DASH), whose legs are posed apart on purpose.
        boolean standing = !titan.isKneeling() && !titan.isSaluting() && gait != BaseTitanEntity.Gait.DASH;
        // Unarmed: swing the arms off the legs' keyframed stride (right arm with left thigh), not vanilla
        // limbSwing, whose player-sized cadence ran the arms 4-5x faster than a titan's gait.
        // Read before foot placement bends the thighs.
        if (unarmed && standing) {
            // Hands free: arms hang in toward the hull (the rest pose splays them 30 degrees) with soft elbows.
            addRotation("rightArm1", 0, 0, -0.38F);
            addRotation("leftArm1", 0, 0, 0.38F);
            float stride = gait == BaseTitanEntity.Gait.IDLE ? 0.0F : (boneRotX("leftLeg3") - boneRotX("rightLeg3")) * 0.5F;
            addRotation("rightArm1", -0.35F * stride, 0, 0);
            addRotation("leftArm1", 0.35F * stride, 0, 0);
            // Elbows stay soft and bend further on the back-swing.
            addRotation("rightArm2", 0.25F + 0.3F * Math.max(0.0F, stride), 0, 0);
            addRotation("leftArm2", 0.25F + 0.3F * Math.max(0.0F, -stride), 0, 0);
        }
        // Loaded stance: torso hunched over the hips instead of standing straight-backed.
        float torsoPitch = 0.0F;  // x rotation added on the body chain, which the howitzer barrel cancels out
        float torsoYaw = 0.0F;
        if (standing) {
            addRotation("body2", -0.10F, 0, 0);
            torsoPitch -= 0.10F;
        }
        if (artillery) {
            // Howitzer recoil: the hull rocks back and the knees take the kick.
            float kick = Math.max(0.0F, 1.0F - (titan.tickCount - titan.clientFireTick + state.getPartialTick()) / 10.0F);
            if (kick > 0.0F) {
                addRotation("body3", 0.09F * kick, 0, 0);
                torsoPitch += 0.09F * kick;
            }
        }

        // Howitzer firing stance: while the gun lays onto a target and for a moment after each shot the titan
        // squats lower, plants its feet wide and leans into the recoil; it eases in and out (~0.5 s).
        float brace = 0.0F;
        if (artillery) {
            boolean bracing = standing && gait == BaseTitanEntity.Gait.IDLE
                    && (titan.getArtilleryLaying() > 0 || titan.tickCount - titan.clientFireTick < BRACE_HOLD_TICKS);
            float now = titan.tickCount + state.getPartialTick();
            float dt = titan.clientBraceClock < 0 ? 0.0F : Mth.clamp(now - titan.clientBraceClock, 0.0F, 10.0F);
            titan.clientBraceClock = now;
            titan.clientBrace = Mth.clamp(titan.clientBrace + (bracing ? dt : -dt) / BRACE_EASE_TICKS, 0.0F, 1.0F);
            brace = titan.clientBrace * titan.clientBrace * (3.0F - 2.0F * titan.clientBrace);  // smoothstep
        }
        if (brace > 0.0F) {
            addRotation("body2", -0.16F * brace, 0, 0);                     // lean into the gun
            torsoPitch -= 0.16F * brace;
            addRotation("rightLeg3", 0, 0, -BRACE_SPREAD * brace);           // feet planted wide...
            addRotation("leftLeg3", 0, 0, BRACE_SPREAD * brace);
            addRotation("rightFoot", 0, 0, BRACE_SPREAD * brace);            // ...soles kept flat
            addRotation("leftFoot", 0, 0, -BRACE_SPREAD * brace);
        }

        applyFootPlacement(titan, state.getPartialTick(), (standing ? STANCE_CROUCH : 0.0F) + BRACE_CROUCH * brace);

        // Lowered weapon (H): natural low-ready hip carry with gun pointed down-forward.
        float lower = titan.getLowerBlend(state.getPartialTick());
        if (lower > 0.001F) {
            addRotation("rightArm1", 0.18F * lower, 0, 0.08F * lower);
            addRotation("rightArm2", 0.95F * lower, 0, 0);
            addRotation("leftArm1", 0.22F * lower, 0, -0.12F * lower);
            addRotation("leftArm2", 0.85F * lower, 0, 0);
        }

        // Titan military salute pose
        int saluteTicks = titan.getSaluteTicks();
        if (saluteTicks > 0) {
            float progress = (45 - saluteTicks + state.getPartialTick()) / 45.0F;
            float blend = progress < 0.15F ? progress / 0.15F : (progress > 0.85F ? (1.0F - progress) / 0.15F : 1.0F);
            blend = Mth.clamp(blend, 0.0F, 1.0F);

            // The arm bones rest turned 180 degrees about y, which mirrors their x axis: negative x raises an
            // arm forward. (Positive x lifted the saluting hand up behind the head.)
            // Left arm stands firmly at crisp military attention along the side
            addRotation("leftArm1", 0.0F, 0.0F, -0.08F * blend);
            addRotation("leftArm2", 0.12F * blend, 0, 0);

            // Right arm raises smartly with elbow at shoulder height, hand touching visor edge
            addRotation("rightArm1", -1.65F * blend, -0.42F * blend, 1.10F * blend);
            addRotation("rightArm2", -1.60F * blend, 0.65F * blend, -0.25F * blend);
            addRotation("rightHand", 0.20F * blend, 0.45F * blend, 0.25F * blend);

            // Torso stands tall and proud at military attention
            addRotation("body3", -0.06F * blend, 0, 0);
        }

        float weight = titan.getProceduralWeight(state.getPartialTick());
        if (weight > 0.001F) {
            EntityModelData data = state.getData(DataTickets.ENTITY_MODEL_DATA);
            if (data != null) {
                // Upper torso pitches with the aim; the waist twists toward where the pilot looks while the legs catch up.
                float pitch = Mth.clamp(data.headPitch(), -35.0F, 35.0F) * Mth.DEG_TO_RAD * weight;
                float twist = Mth.clamp(data.netHeadYaw(), -60.0F, 60.0F) * Mth.DEG_TO_RAD * weight;
                addRotation("body3", pitch, 0, 0);
                addRotation("body2", 0, twist, 0);
                torsoPitch += pitch;
                torsoYaw += twist;
            }
            float partial = state.getPartialTick();
            float lean = -titan.getLeanForward(partial) * Mth.DEG_TO_RAD * weight;
            addRotation("body1", lean, 0, titan.getLeanSide(partial) * Mth.DEG_TO_RAD * weight);
            torsoPitch += lean;
        }
        if (artillery) aimHowitzer(titan, state.getPartialTick(), torsoPitch, torsoYaw);
    }

    /**
     * Turns the howitzer onto the firing solution: the turret traverses to the target's bearing and the barrel
     * elevates to the launch angle, both measured in the world and corrected for how far the torso is already
     * pitched/twisted. Recoil slides the barrel back along its own axis.
     */
    private void aimHowitzer(T titan, float partial, float torsoPitch, float torsoYaw) {
        float elevation = HOWITZER_REST_ELEVATION;
        float bearingRel = 0.0F;  // target bearing relative to the hull, radians (Minecraft yaw sense)
        net.minecraft.world.phys.Vec3 v = titan.artillerySolution();
        net.minecraft.core.BlockPos t = titan.getArtilleryTarget();
        if (v != null && t != null) {
            elevation = (float) Math.atan2(v.y, v.horizontalDistance());
            double dx = t.getX() + 0.5D - titan.getX(), dz = t.getZ() + 0.5D - titan.getZ();
            float bearing = (float) Math.toDegrees(Math.atan2(-dx, dz));
            float body = Mth.rotLerp(partial, titan.yBodyRotO, titan.yBodyRot);
            bearingRel = Mth.wrapDegrees(bearing - body) * Mth.DEG_TO_RAD;
        }
        // Gun laying: the turret and barrel slew at a fixed rate instead of snapping, about as long as the
        // server's Howitzer.LAYING_TICKS for a large swing.
        float now = titan.tickCount + partial;
        float dt = titan.clientHowitzerClock < 0 ? 0.0F : Mth.clamp(now - titan.clientHowitzerClock, 0.0F, 10.0F);
        titan.clientHowitzerClock = now;
        float step = HOWITZER_SLEW_PER_TICK * dt;
        titan.clientHowitzerTraverse += Mth.clamp(Mth.wrapDegrees((bearingRel - titan.clientHowitzerTraverse) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD, -step, step);
        titan.clientHowitzerElevation += Mth.clamp(elevation - titan.clientHowitzerElevation, -step, step);
        elevation = titan.clientHowitzerElevation;
        // Model rotY runs opposite to Minecraft yaw (checked in game: + swung the gun to the titan's left).
        addRotation("artilleryTurret", 0, -titan.clientHowitzerTraverse - torsoYaw, 0);
        addRotation("artilleryBarrel", elevation - HOWITZER_REST_ELEVATION - torsoPitch, 0, 0);

        float kick = Math.max(0.0F, 1.0F - (titan.tickCount - titan.clientFireTick + partial) / 8.0F);
        CoreGeoBone barrel = getAnimationProcessor().getBone("artilleryBarrel");
        if (barrel != null && kick > 0.0F) {
            float slide = 3.0F * kick;  // pixels back along the barrel
            barrel.setPosZ(barrel.getPosZ() + slide * Mth.cos(elevation));
            barrel.setPosY(barrel.getPosY() - slide * Mth.sin(elevation));
            barrel.resetStateChanges();
        }
    }

    /**
     * Uneven ground while standing: lower the pelvis until the foot over lower ground reaches it,
     * then bend the other leg (hip/knee/ankle) so its foot rests on the higher block instead of
     * sinking into it. Two-segment leg solved from the model's own joint pivots.
     */
    private void applyFootPlacement(T titan, float partial, float crouch) {
        // crouch (blocks) sinks the pelvis and bends both legs by the same amount, feet staying flat.
        float drop = titan.getPelvisDrop(partial) - crouch;
        float leftLift = titan.getLegLift(true, partial) + crouch;
        float rightLift = titan.getLegLift(false, partial) + crouch;
        if (drop > -0.01F && leftLift < 0.01F && rightLift < 0.01F) return;

        CoreGeoBone pelvis = getAnimationProcessor().getBone("body1");
        if (pelvis != null) {
            pelvis.setPosY(pelvis.getPosY() + drop * 16.0F);
            pelvis.resetStateChanges();
        }
        bendLeg("left", leftLift * 16.0F);
        bendLeg("right", rightLift * 16.0F);
        bendLeg("midLeft", rightLift * 16.0F);
        bendLeg("midRight", leftLift * 16.0F);
        bendLeg("rearLeft", leftLift * 16.0F);
        bendLeg("rearRight", rightLift * 16.0F);
    }

    private float boneRotX(String name) {
        CoreGeoBone bone = getAnimationProcessor().getBone(name);
        return bone == null ? 0.0F : bone.getRotX();
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
