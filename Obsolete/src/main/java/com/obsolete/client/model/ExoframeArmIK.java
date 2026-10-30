package com.obsolete.client.model;

import com.obsolete.entity.ExoframeEntity;
import com.obsolete.item.*;
import net.minecraft.util.Mth;
import net.minecraft.world.item.Item;
import org.joml.Matrix3f;
import org.joml.Vector3f;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;

import java.util.function.Function;

/**
 * Weapon handling for the exoframe: each hold is "where the right fist is + where the gun points".
 * The right arm is IK'd to the fist target, the mount is rotated so the gun points exactly along the
 * hold direction and translated so the weapon's grip sits inside the fist, then the left arm is IK'd
 * onto the weapon's support point. All maths is in GeckoLib render space (geo JSON x negated,
 * bone rotation = Rz*Ry*Rx, bone position translates by (-posX, posY, posZ)).
 *
 * Hold numbers were checked offline against arm reach (upper 6.5px + forearm/fist 11.5px) over the full
 * look-pitch range, and fists sit in front of the chest armour (z <= -6.8) so nothing clips.
 */
public final class ExoframeArmIK {

    /** Fist centre in the hand bones' rest frame, geo JSON coords (left hand is the mirror). */
    private static final Vector3f RIGHT_FIST = new Vector3f(-7.9F, 12.0F, -0.6F);

    public enum Hold {
        //               grip (JSON)           support (JSON)      rest fist (JSON)        yaw   pitch | aim fist (JSON)     yaw   pitch share
        RIFLE(       v(-8, 11.9F, -1.1F), v(-8, 13.6F, -5.5F),  v(-1.5F, 21.5F, -7.2F), 0.7F,  -0.4F,  v(-5.6F, 27.5F, -6.8F), 0.04F, 1F),
        SNIPER(      v(-8, 11.7F, -2.3F), v(-8, 13.4F, -6.5F), v(-1.5F, 21F, -7.2F),   0.75F, -0.45F, v(-5.6F, 27.5F, -6.8F), 0.04F, 1F),
        MACHINE_GUN( v(-8, 10.8F, -2.4F), v(-8, 13.6F, -6.5F), v(-3F, 21.5F, -7.5F),   0.45F, -0.05F, v(-6.4F, 22.5F, -7.0F), 0.04F, 1F),
        MINIGUN(     v(-8, 11.5F, -1.1F), v(-8, 15.0F, -3.5F), v(-3F, 21.5F, -7.5F),   0.3F,  -0.05F, v(-7.2F, 24.0F, -7.5F), 0.02F, 1F),
        POD_LAUNCHER(v(-8, 9.4F, -3.2F),  v(-8, 10.6F, -5.5F), v(-4.5F, 21F, -7.5F),   0.4F,  -0.3F,  v(-7.6F, 28.0F, -7.0F), 0.02F, 1F),
        RPG(         v(-8, 10.9F, 0.7F),  v(-8, 10.9F, -4.0F), v(-2.5F, 21.5F, -7.2F), 0.65F, -0.3F,  v(-5.8F, 27.5F, -7.0F), 0.04F, 1F),
        TOOL_DRILL(  v(-8, 9.2F, -3.2F),  v(-8, 17.4F, -6F),    v(-4F, 18F, -7.5F),     0.25F, -0.4F,  v(-4.5F, 21F, -7.5F),   0.03F, 0.5F),
        TOOL_SAW(    v(-8, 9.6F, -3.2F),  v(-8, 18.9F, -6F),    v(-4F, 18F, -7.5F),     0.25F, -0.4F,  v(-4.5F, 21F, -7.5F),   0.03F, 0.5F),
        BATTLE_RIFLE(v(-8, 11.9F, -1.1F), v(-8, 13.2F, -4.5F), v(-1.8F, 21.5F, -7.2F), 0.65F, -0.35F, v(-5.6F, 27.2F, -7.2F), 0.04F, 1.0F),
        AUTOCANNON_30MM(v(-8, 10.8F, -2.4F), v(-8, 12.0F, -3.2F), v(-3.2F, 21.5F, -7.5F), 0.42F, -0.05F, v(-6.5F, 23.5F, -7.4F), 0.03F, 0.75F),
        SHOTGUN_BREACHER(v(-8, 11.8F, -1.2F), v(-8, 13.0F, -4.4F), v(-2.0F, 21.5F, -7.2F), 0.60F, -0.30F, v(-5.8F, 26.5F, -7.2F), 0.04F, 1.0F),
        GRENADE_LAUNCHER(v(-8, 11.2F, -1.5F), v(-8, 12.6F, -3.8F), v(-2.8F, 21.5F, -7.3F), 0.45F, -0.20F, v(-6.2F, 25.0F, -7.3F), 0.03F, 0.85F),
        RECOILLESS_RIFLE(v(-8, 11.0F, 0.5F), v(-8, 11.8F, -2.8F), v(-2.5F, 21.5F, -7.2F), 0.60F, -0.25F, v(-5.8F, 27.0F, -7.2F), 0.04F, 0.85F),
        ATGM_GUIDED( v(-8, 10.0F, -2.0F), v(-8, 11.2F, -3.8F), v(-4.0F, 21.0F, -7.5F), 0.35F, -0.20F, v(-7.0F, 27.5F, -7.3F), 0.02F, 0.80F),
        FLAMETHROWER(v(-8, 11.0F, -1.8F), v(-8, 12.2F, -3.0F), v(-3.0F, 21.0F, -7.4F), 0.45F, -0.15F, v(-6.4F, 24.0F, -7.4F), 0.03F, 0.75F),
        VIBRO_BLADE( v(-8, 12.0F, -1.0F), v(-8, 12.0F, -1.0F), v(-4.5F, 18.0F, -7.0F), 0.20F, -0.40F, v(-5.5F, 24.0F, -7.0F), 0.02F, 0.50F);

        public final Vector3f grip, support, restFist, aimFist;
        public final float restYaw, restPitch, aimYaw, pitchShare;

        Hold(Vector3f grip, Vector3f support, Vector3f restFist, float restYaw, float restPitch,
             Vector3f aimFist, float aimYaw, float pitchShare) {
            this.grip = render(grip);
            this.support = render(support);
            this.restFist = render(restFist);
            this.aimFist = render(aimFist);
            this.restYaw = restYaw;
            this.restPitch = restPitch;
            this.aimYaw = aimYaw;
            this.pitchShare = pitchShare;
        }

        public static Hold of(Item item) {
            return com.obsolete.registry.ExoframeVariantRegistry.getHoldForWeapon(item);
        }
    }

    private ExoframeArmIK() {
    }

    public static void clearMount(CoreGeoBone mount) {
        if (mount == null) return;
        mount.setRotX(0);
        mount.setRotY(0);
        mount.setRotZ(0);
        mount.setPosX(0);
        mount.setPosY(0);
        mount.setPosZ(0);
    }

    public static void pose(Function<String, CoreGeoBone> bones, ExoframeEntity exo, Item item, float partialTick,
                            float moveAmount, float lookPitch, float recoilKick, boolean firing, boolean emoting) {
        CoreGeoBone rArm = bones.apply("right_arm"), rFore = bones.apply("right_forearm"), rHand = bones.apply("right_hand");
        CoreGeoBone mount = bones.apply("right_hand_weapon_mount");
        CoreGeoBone lArm = bones.apply("left_arm"), lFore = bones.apply("left_forearm"), lHand = bones.apply("left_hand");
        if (rArm == null || rFore == null || rHand == null || mount == null || lArm == null || lFore == null || lHand == null) return;

        Hold hold = Hold.of(item);

        // Ease in/out of the shouldered aim instead of snapping (~4 ticks).
        float age = exo.tickCount + partialTick;
        float target = exo.isAiming() || firing ? 1F : 0F;
        exo.clientAimBlend += (target - exo.clientAimBlend) * Mth.clamp((age - exo.clientAimAge) * 0.3F, 0F, 1F);
        exo.clientAimAge = age;
        float aim = exo.clientAimBlend * exo.clientAimBlend * (3F - 2F * exo.clientAimBlend);

        float aimPitch = lookPitch * hold.pitchShare;
        float pitch = Mth.lerp(aim, hold.restPitch, aimPitch) + recoilKick * aim;
        float yaw = Mth.lerp(aim, hold.restYaw, hold.aimYaw);

        // Aimed guns pivot about their middle so the support hand stays in reach when looking up/down.
        Vector3f mid = new Vector3f(hold.support).sub(hold.grip).mul(0.5F);
        Vector3f aimFist = new Vector3f(hold.aimFist)
                .add(gunRot(hold.aimYaw, 0).transform(new Vector3f(mid)))
                .sub(gunRot(hold.aimYaw, aimPitch).transform(new Vector3f(mid)));
        Vector3f fist = new Vector3f(hold.restFist).lerp(aimFist, aim);
        fist.y += Mth.sin(age * 0.6F) * 0.35F * Mth.clamp(moveAmount, 0F, 1F) * (1F - 0.5F * aim)  // gait bob
                + Mth.sin(age * 0.08F) * 0.12F;                                                    // breathing
        fist.z += recoilKick * 8F * aim;                                                           // recoil into the shoulder

        // ---- right arm onto the fist target ----
        Vector3f rFist = render(RIGHT_FIST);
        solveArm(rArm, rFore, rFist, fist);
        zero(rHand);

        // ---- weapon: exact aim direction, grip seated in the fist ----
        Matrix3f gun = gunRot(yaw, pitch);
        Matrix3f wrist = rot(rArm).mul(rot(rFore)).mul(rot(rHand));
        Matrix3f local = new Matrix3f(wrist).transpose().mul(gun);
        Vector3f euler = local.getEulerAnglesZYX(new Vector3f());
        mount.setRotX(euler.x);
        mount.setRotY(euler.y);
        mount.setRotZ(euler.z);
        Vector3f pivot = pivot(mount);
        Vector3f placed = local.transform(new Vector3f(hold.grip).sub(pivot)).add(pivot);
        Vector3f offset = new Vector3f(rFist).sub(placed);
        mount.setPosX(-offset.x);
        mount.setPosY(offset.y);
        mount.setPosZ(offset.z);

        // ---- left hand onto the support point (emotes own the left arm while armed) ----
        if (emoting) return;
        Vector3f realFist = fk(rArm, rFore, rFist);
        Vector3f support = gun.transform(new Vector3f(hold.support).sub(hold.grip)).add(realFist);
        solveArm(lArm, lFore, new Vector3f(-rFist.x, rFist.y, rFist.z), support);
        zero(lHand);
    }

    /**
     * Two-bone IK: shoulder (arm pivot) -> elbow hinge (forearm pivot, rotX only, flexes forward) -> fist.
     * Sets arm rotX/rotY and forearm rotX so the fist reaches the target (clamped to arm reach).
     */
    static void solveArm(CoreGeoBone arm, CoreGeoBone fore, Vector3f fist, Vector3f target) {
        Vector3f s = pivot(arm), e = pivot(fore);
        Vector3f a = new Vector3f(e).sub(s), b = new Vector3f(fist).sub(e), w = new Vector3f(target).sub(s);
        float la = a.length(), lb = b.length();
        float d = Mth.clamp(w.length(), Math.abs(la - lb) + 0.05F, la + lb - 0.05F);

        // elbow: |a + Rx(phi) b| = d  ->  K + A cos(phi) + B sin(phi) = (d^2 - la^2 - lb^2) / 2
        float k = a.x * b.x, aa = a.y * b.y + a.z * b.z, bb = a.z * b.y - a.y * b.z;
        float r = (float) Math.hypot(aa, bb), psi = (float) Math.atan2(bb, aa);
        float acos = (float) Math.acos(Mth.clamp(((d * d - la * la - lb * lb) / 2F - k) / r, -1F, 1F));
        float p1 = Mth.wrapDegrees((psi + acos) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
        float p2 = Mth.wrapDegrees((psi - acos) * Mth.RAD_TO_DEG) * Mth.DEG_TO_RAD;
        float phi = p1 >= 0 && (p2 < 0 || p1 < p2) ? p1 : Math.max(p2, 0F);

        // shoulder: Ry(beta) Rx(alpha) u = target direction; of the two solutions keep the lower elbow.
        Vector3f u = new Matrix3f().rotationX(phi).transform(new Vector3f(b)).add(a);
        Vector3f dir = new Vector3f(w).normalize(u.length());
        float ru = (float) Math.hypot(u.y, u.z), delta = (float) Math.atan2(u.z, u.y);
        float ac = (float) Math.acos(Mth.clamp(dir.y / ru, -1F, 1F));
        float bestX = 0, bestY = 0, bestElbow = Float.MAX_VALUE;
        for (float alpha : new float[]{ac - delta, -ac - delta}) {
            float uz = u.y * Mth.sin(alpha) + u.z * Mth.cos(alpha);
            float beta = (float) (Math.atan2(dir.x, dir.z) - Math.atan2(u.x, uz));
            float elbowY = new Matrix3f().rotationY(beta).rotateX(alpha).transform(new Vector3f(a)).y;
            if (elbowY < bestElbow) {
                bestElbow = elbowY;
                bestX = alpha;
                bestY = beta;
            }
        }
        arm.setRotX(bestX);
        arm.setRotY(bestY);
        arm.setRotZ(0);
        fore.setRotX(phi);
        fore.setRotY(0);
        fore.setRotZ(0);
    }

    /** Fist position after the arm chain (positions assumed zero on arm bones, as in every clip). */
    private static Vector3f fk(CoreGeoBone arm, CoreGeoBone fore, Vector3f fist) {
        Vector3f s = pivot(arm), e = pivot(fore);
        Vector3f p = rot(fore).transform(new Vector3f(fist).sub(e)).add(e);
        return rot(arm).transform(p.sub(s)).add(s);
    }

    private static Matrix3f gunRot(float yaw, float pitch) {
        return new Matrix3f().rotationY(yaw).rotateX(pitch);
    }

    private static Matrix3f rot(CoreGeoBone b) {
        return new Matrix3f().rotationZ(b.getRotZ()).rotateY(b.getRotY()).rotateX(b.getRotX());
    }

    private static Vector3f pivot(CoreGeoBone b) {
        return new Vector3f(b.getPivotX(), b.getPivotY(), b.getPivotZ());
    }

    private static void zero(CoreGeoBone b) {
        b.setRotX(0);
        b.setRotY(0);
        b.setRotZ(0);
    }

    private static Vector3f v(float x, float y, float z) {
        return new Vector3f(x, y, z);
    }

    private static Vector3f render(Vector3f json) {
        return new Vector3f(-json.x, json.y, json.z);
    }
}
