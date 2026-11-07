package com.youjoarms.client;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.tacz.guns.api.entity.IGunOperator;
import com.tacz.guns.api.item.IGun;
import com.youjoarms.capability.PlayerMageData;
import com.youjoarms.capability.PlayerMageProvider;
import com.youjoarms.entity.FormulaZoneEntity;
import com.youjoarms.formula.FormulaType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

import java.util.HashMap;
import java.util.Map;

/**
 * All formula VFX, drawn additively in world space:
 * - charging: a stack of circles in front of the muzzle, one more per charge stage, each bigger and further out
 * - release: the stack bursts outward and fades when the formula fires
 * - Defensive Shell: crossed circles forming a dome around the caster
 * - zones: Area Suppression ground circle; Annihilation ground circle + three sky circles + light pillar
 */
@Mod.EventBusSubscriber(modid = "youjoarms", value = Dist.CLIENT, bus = Mod.EventBusSubscriber.Bus.FORGE)
public class MagicCircleRenderer {
    private static final ResourceLocation[] CIRCLES = {tex("magic_circle"), tex("circle_gear"), tex("circle_seal"), tex("circle_lens")};
    private static final ResourceLocation GLOW = tex("glow");
    private static final ResourceLocation BEAM = tex("beam");
    private static final int RELEASE_TICKS = 12;

    /** Last charge seen per player, to detect the moment a charged formula is released. */
    private record Charge(FormulaType formula, float progress, Vec3 eye, Vec3 look, float yaw, float pitch, float aim) {}

    private record Release(Charge charge, float startTime) {}

    private static final Map<Integer, Charge> LAST_CHARGE = new HashMap<>();
    private static final Map<Integer, Release> RELEASES = new HashMap<>();

    private static ResourceLocation tex(String name) {
        return new ResourceLocation("youjoarms", "textures/vfx/" + name + ".png");
    }

    @SubscribeEvent
    public static void onRenderLevelStage(RenderLevelStageEvent event) {
        if (event.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null) return;

        PoseStack pose = event.getPoseStack();
        Vec3 cam = event.getCamera().getPosition();
        float pt = event.getPartialTick();
        float now = mc.level.getGameTime() + pt;

        RenderSystem.setShader(GameRenderer::getPositionTexColorShader);
        RenderSystem.enableBlend();
        // additive: white textures glow in the formula colour and never darken what is behind them
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE);
        RenderSystem.disableCull();
        RenderSystem.depthMask(false);

        for (Player player : mc.level.players()) {
            player.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
                renderCharge(player, cap, pose, cam, pt, now);
                if (cap.getShieldTicks() > 0) renderShield(player, cap, pose, cam, pt, now);
            });
        }
        RELEASES.entrySet().removeIf(e -> now - e.getValue().startTime() > RELEASE_TICKS);
        RELEASES.values().forEach(r -> renderRelease(r, pose, cam, now));

        for (Entity e : mc.level.entitiesForRendering()) {
            if (e instanceof FormulaZoneEntity zone) renderZone(zone, pose, cam, pt);
        }

        RenderSystem.depthMask(true);
        RenderSystem.enableCull();
        RenderSystem.defaultBlendFunc();
        RenderSystem.disableBlend();
    }

    // ------------------------------------------------------------ charging stack

    private static void renderCharge(Player player, PlayerMageData cap, PoseStack pose, Vec3 cam, float pt, float now) {
        boolean charging = cap.isCharging() && cap.getSelectedFormula() != FormulaType.NONE
                && com.youjoarms.mana.GunMana.isOurs(player.getMainHandItem());
        Charge last = LAST_CHARGE.get(player.getId());
        if (!charging) {
            if (last != null && last.progress() >= 1f) RELEASES.put(player.getId(), new Release(last, now));
            LAST_CHARGE.remove(player.getId());
            return;
        }
        float aim = IGunOperator.fromLivingEntity(player).getSynAimingProgress();
        Charge c = new Charge(cap.getSelectedFormula(), cap.getChargeProgress(), player.getEyePosition(pt),
                player.getViewVector(pt), player.getViewYRot(pt), player.getViewXRot(pt), aim);
        LAST_CHARGE.put(player.getId(), c);
        drawStack(c, pose, cam, now, 0f);
    }

    /** burst 0..1: 0 while charging, then the circles grow and fade after release. */
    private static void drawStack(Charge c, PoseStack pose, Vec3 cam, float now, float burst) {
        int n = c.formula().getRings();
        float[] rgb = rgb(c.formula());
        boolean full = c.progress() >= 1f;
        float pulse = full ? 1.0f + 0.25f * Mth.sin(now * 0.6f) : 1.0f;
        // hip-fire: the stack sits off to the right like the gun; aiming centres it on the sights
        // offsets are along the camera's own right/up axes so the stack stays on the muzzle line when looking up or down
        double yawRad = Math.toRadians(c.yaw());
        Vec3 right = new Vec3(-Math.cos(yawRad), 0, -Math.sin(yawRad));
        Vec3 up = right.cross(c.look()).normalize();
        Vec3 origin = c.eye().add(right.scale(0.22 * (1 - c.aim()))).subtract(up.scale(0.16 * (1 - c.aim())));

        for (int i = 0; i < n; i++) {
            float appear = Mth.clamp((c.progress() * n - i) * 2f, 0f, 1f);
            if (appear <= 0f) continue;
            float base = 0.8f * (float) Math.pow(1.42, i);
            float size = base * easeOutBack(appear) * (1f + burst * 0.9f);
            double dist = 1.1 + 0.6 * i + base * 0.15 + burst * 0.8;
            // each further ring is a little dimmer so a six-ring stack stays readable instead of washing out
            float alpha = appear * (1f - burst) * (0.75f + 0.25f * pulse) * (1f - 0.09f * i);
            float spin = now * (i % 2 == 0 ? 3f : -4.5f) * (1f + i * 0.15f);
            Vec3 at = origin.add(c.look().scale(dist));

            facing(pose, at, cam, c.yaw(), c.pitch());
            draw(pose, CIRCLES[i % CIRCLES.length], size, spin, rgb, alpha);
            draw(pose, GLOW, size * 1.25f, 0, rgb, alpha * 0.1f);  // cheap bloom behind each ring
            if (i == 0) draw(pose, GLOW, size * 0.45f, 0, new float[]{1, 1, 1}, alpha * 0.4f * pulse);
            pose.popPose();
        }
    }

    private static void renderRelease(Release r, PoseStack pose, Vec3 cam, float now) {
        float t = Mth.clamp((now - r.startTime()) / RELEASE_TICKS, 0f, 1f);
        drawStack(r.charge(), pose, cam, now, t);
    }

    // ------------------------------------------------------------ Defensive Shell

    private static void renderShield(Player player, PlayerMageData cap, PoseStack pose, Vec3 cam, float pt, float now) {
        float[] rgb = rgb(FormulaType.SHIELD);
        float fade = Mth.clamp(cap.getShieldTicks() / 20f, 0f, 1f);
        Vec3 center = player.getPosition(pt).add(0, 1.0, 0);
        for (int k = 0; k < 3; k++) {  // three vertical circles 60 degrees apart make the dome
            pose.pushPose();
            pose.translate(center.x - cam.x, center.y - cam.y, center.z - cam.z);
            pose.mulPose(new Quaternionf().rotationY((float) Math.toRadians(k * 60 + now * 1.5f)));
            draw(pose, CIRCLES[3], 3.6f, now * 2f, rgb, 0.35f * fade);
            pose.popPose();
        }
        // horizontal rings at feet, chest and above the head: the caster sees these around them in first person
        float[][] rings = {{-0.95f, 4.2f, 0.85f}, {0.25f, 4.0f, 0.45f}, {1.35f, 2.8f, 0.55f}};
        for (int k = 0; k < rings.length; k++) {
            flat(pose, center.add(0, rings[k][0], 0), cam);
            draw(pose, CIRCLES[k == 0 ? 0 : 3], rings[k][1], now * (k % 2 == 0 ? 2.5f : -3f), rgb, rings[k][2] * fade);
            if (k == 0) draw(pose, GLOW, 4.6f, 0, rgb, 0.2f * fade);
            pose.popPose();
        }
    }

    // ------------------------------------------------------------ zones

    private static void renderZone(FormulaZoneEntity zone, PoseStack pose, Vec3 cam, float pt) {
        float age = zone.tickCount + pt;
        int fuse = zone.getFuse();
        float t = Mth.clamp(age / fuse, 0f, 1f);
        float after = Mth.clamp((age - fuse) / 20f, 0f, 1f);  // 0 until detonation, then fades out
        float alpha = 1f - after;
        float r = zone.getRadius();
        float grow = easeOutBack(Math.min(1f, t * 1.6f)) * (1f + after * 0.5f);
        float[] rgb = rgb(zone.getFormula());
        Vec3 ground = zone.getPosition(pt).add(0, 0.06, 0);

        flat(pose, ground, cam);
        draw(pose, CIRCLES[0], 2 * r * grow, age * 2f, rgb, alpha);
        draw(pose, CIRCLES[1], 1.4f * r * grow, -age * 3f, rgb, alpha * 0.9f);
        draw(pose, CIRCLES[3], 2.4f * r * grow, age * 0.7f, rgb, alpha * 0.5f);
        draw(pose, GLOW, 2.6f * r * grow, 0, rgb, alpha * 0.25f);
        pose.popPose();

        if (zone.getFormula() != FormulaType.ULTIMATE) return;

        // Annihilation: three sky circles stacked above the target, appearing one after another, then a pillar
        float[] heights = {1.4f, 2.0f, 2.6f};
        float[] sizes = {2.2f, 1.6f, 1.0f};
        for (int k = 0; k < 3; k++) {
            float appear = Mth.clamp((t - k * 0.2f) * 3f, 0f, 1f);
            if (appear <= 0f) continue;
            flat(pose, ground.add(0, r * heights[k], 0), cam);
            draw(pose, CIRCLES[(k + 2) % CIRCLES.length], sizes[k] * r * easeOutBack(appear) * (1f + after * 0.4f),
                    age * (k % 2 == 0 ? 2.5f : -3.5f), rgb, appear * alpha);
            draw(pose, GLOW, sizes[k] * r * 1.2f * appear, 0, rgb, appear * alpha * 0.2f);
            pose.popPose();
        }
        float pillar = t < 0.7f ? 0f : (t - 0.7f) / 0.3f;  // gathers over the last 30% of the fuse
        if (after > 0f) pillar = 1f + 1.5f * (1f - after);  // flash wide at detonation
        if (pillar > 0f) {
            float h = r * heights[2];
            for (int k = 0; k < 2; k++) {  // two crossed quads read as a column from any side
                pose.pushPose();
                pose.translate(ground.x - cam.x, ground.y - cam.y + h / 2, ground.z - cam.z);
                pose.mulPose(new Quaternionf().rotationY((float) Math.toRadians(45 + k * 90)));
                quad(pose, BEAM, r * 0.35f * pillar, h, new float[]{1, 1, 1}, Math.min(1f, pillar) * alpha);
                quad(pose, BEAM, r * 0.7f * pillar, h, rgb, 0.6f * Math.min(1f, pillar) * alpha);
                pose.popPose();
            }
        }
    }

    // ------------------------------------------------------------ drawing helpers

    /** Pushes a pose at {@code at} facing along yaw/pitch (circle plane perpendicular to the aim). Caller pops. */
    private static void facing(PoseStack pose, Vec3 at, Vec3 cam, float yaw, float pitch) {
        pose.pushPose();
        pose.translate(at.x - cam.x, at.y - cam.y, at.z - cam.z);
        pose.mulPose(new Quaternionf().rotationY((float) Math.toRadians(-yaw + 180f)));
        pose.mulPose(new Quaternionf().rotationX((float) Math.toRadians(-pitch)));  // with the 180 flip above, -pitch keeps the plane square to the aim
    }

    /** Pushes a pose at {@code at} lying flat on the ground. Caller pops. */
    private static void flat(PoseStack pose, Vec3 at, Vec3 cam) {
        pose.pushPose();
        pose.translate(at.x - cam.x, at.y - cam.y, at.z - cam.z);
        pose.mulPose(new Quaternionf().rotationX((float) Math.toRadians(90)));
    }

    private static void draw(PoseStack pose, ResourceLocation texture, float size, float spinDeg, float[] rgb, float a) {
        if (a <= 0.01f || size <= 0.01f) return;
        pose.pushPose();
        pose.mulPose(new Quaternionf().rotationZ((float) Math.toRadians(spinDeg)));
        quad(pose, texture, size, size, rgb, a);
        pose.popPose();
    }

    private static void quad(PoseStack pose, ResourceLocation texture, float w, float h, float[] rgb, float a) {
        RenderSystem.setShaderTexture(0, texture);
        Matrix4f mat = pose.last().pose();
        BufferBuilder buffer = Tesselator.getInstance().getBuilder();
        buffer.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX_COLOR);
        float x = w / 2, y = h / 2;
        a = Math.min(1f, a);
        buffer.vertex(mat, -x, -y, 0).uv(0, 1).color(rgb[0], rgb[1], rgb[2], a).endVertex();
        buffer.vertex(mat, x, -y, 0).uv(1, 1).color(rgb[0], rgb[1], rgb[2], a).endVertex();
        buffer.vertex(mat, x, y, 0).uv(1, 0).color(rgb[0], rgb[1], rgb[2], a).endVertex();
        buffer.vertex(mat, -x, y, 0).uv(0, 0).color(rgb[0], rgb[1], rgb[2], a).endVertex();
        Tesselator.getInstance().end();
    }

    private static float[] rgb(FormulaType f) {
        int c = f.getCircleColor();
        return new float[]{((c >> 16) & 0xFF) / 255f, ((c >> 8) & 0xFF) / 255f, (c & 0xFF) / 255f};
    }

    /** Overshoots a little before settling, so each circle "pops" into place. */
    private static float easeOutBack(float t) {
        float c1 = 1.70158f, c3 = c1 + 1;
        return 1 + c3 * (float) Math.pow(t - 1, 3) + c1 * (float) Math.pow(t - 1, 2);
    }
}
