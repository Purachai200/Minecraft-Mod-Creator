package com.titancombat.client.renderer.layer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import com.titancombat.client.renderer.TitanRenderer;
import com.titancombat.entity.TitanFlightModule;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import software.bernie.geckolib.cache.GeckoLibCache;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.renderer.GeoRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;
import software.bernie.geckolib.util.RenderUtils;

import java.util.List;

/**
 * Renders back-mounted modular flight equipment (Drone Lifters, Jetpacks, VTOL Glide Wings)
 * attached to the titan's upper dorsal chassis/reactor (body3).
 *
 * Configured with per-chassis mounting offsets to ensure world-class ergonomic fit
 * high on the shoulder/reactor line across all 7 titan chassis.
 */
public class TitanFlightModuleLayer<T extends BaseTitanEntity> extends GeoRenderLayer<T> {
    private boolean drawing = false;

    public record MountConfig(double offsetY, double offsetZ, float scale, float pitchDegrees) {}

    public TitanFlightModuleLayer(GeoRenderer<T> renderer) {
        super(renderer);
    }

    private MountConfig getMountConfig(TitanClass titanClass) {
        return switch (titanClass) {
            case MONARCH -> new MountConfig(1.20D, 1.20D, 1.85F, 0.0F);
            case ION -> new MountConfig(1.36D, 1.30D, 1.85F, 0.0F);
            case LEGION -> new MountConfig(1.16D, 1.15D, 2.15F, 0.0F);
            case SCORCH -> new MountConfig(1.01D, 1.34D, 2.15F, 0.0F);
            case RONIN -> new MountConfig(1.38D, 1.20D, 1.70F, 0.0F);
            case NORTHSTAR -> new MountConfig(0.48D, 1.45D, 1.70F, 0.0F);
            case TONE -> new MountConfig(1.38D, 1.70D, 1.85F, 0.0F);
            case TROOPER, SCOUT, SHADE -> new MountConfig(1.10D, 1.15D, 1.80F, 0.0F);
        };
    }

    /** Jump-jet pack: top just under the shoulder line, harness flush with each chassis' back armour.
     *  TitanClass.getJetpackNozzle mirrors these for the exhaust particles; keep the two in sync. */
    private MountConfig getJetpackMount(TitanClass titanClass) {
        return switch (titanClass) {
            case MONARCH -> new MountConfig(0.63D, 1.23D, 1.48F, 0.0F);
            case ION -> new MountConfig(0.97D, 0.91D, 1.48F, 0.0F);
            case LEGION -> new MountConfig(1.15D, 2.50D, 1.72F, 0.0F);
            case SCORCH -> new MountConfig(0.79D, 3.36D, 1.72F, 0.0F);
            case RONIN -> new MountConfig(1.09D, 1.02D, 1.36F, 0.0F);
            case NORTHSTAR -> new MountConfig(0.37D, 1.46D, 1.36F, 0.0F);
            case TONE -> new MountConfig(0.73D, 1.54D, 1.48F, 0.0F);
            case TROOPER, SCOUT, SHADE -> new MountConfig(0.85D, 1.05D, 1.45F, 0.0F);
        };
    }

    @Override
    public void renderForBone(PoseStack poseStack, T titan, GeoBone bone, RenderType renderType, MultiBufferSource bufferSource,
                              VertexConsumer buffer, float partialTick, int packedLight, int packedOverlay) {
        if (this.drawing || !titan.hasFlightModule() || titan.isInvisible() || !"body3".equals(bone.getName())) return;

        TitanFlightModule module = titan.getFlightModule();
        String geoPath = module.getGeoPath();
        String texturePath = module.getTexturePath();
        if (geoPath.isEmpty() || texturePath.isEmpty()) return;

        BakedGeoModel model = GeckoLibCache.getBakedModels().get(new ResourceLocation(TitanCombatMod.MODID, geoPath));
        if (model == null) return;

        this.drawing = true;
        poseStack.pushPose();
        try {
            // First move matrix origin to bone's pivot point (cancelling translateAwayFromPivotPoint from GeckoLib)
            RenderUtils.translateToPivotPoint(poseStack, bone);

            MountConfig cfg = module == TitanFlightModule.ROCKET_JETPACK
                    ? getJetpackMount(titan.getTitanClass()) : getMountConfig(titan.getTitanClass());

            // Position directly on the upper dorsal reactor / shoulder line of the titan chassis
            poseStack.translate(0.0D, cfg.offsetY(), cfg.offsetZ());
            if (cfg.pitchDegrees() != 0.0F) {
                poseStack.mulPose(Axis.XP.rotationDegrees(cfg.pitchDegrees()));
            }
            poseStack.scale(cfg.scale(), cfg.scale(), cfg.scale());

            if (module == TitanFlightModule.ROCKET_JETPACK && getRenderer() instanceof TitanRenderer<?> titanRenderer
                    && titanRenderer.getEntityRenderTranslations() != null) {
                // Nozzle exits (bell bottom centres, model px) -> entity-relative world offsets for the exhaust particles.
                Matrix4f local = RenderUtils.invertAndMultiplyMatrices(new Matrix4f(poseStack.last().pose()),
                        new Matrix4f(titanRenderer.getEntityRenderTranslations()));
                Vector3f left = local.transformPosition(new Vector3f(6.5F / 16.0F, -10.0F / 16.0F, 4.5F / 16.0F));
                Vector3f right = local.transformPosition(new Vector3f(-6.5F / 16.0F, -10.0F / 16.0F, 4.5F / 16.0F));
                titan.setRenderedJetNozzles(new Vec3(left), new Vec3(right));
            }

            boolean activeThrust = titan.isFlying() || !titan.onGround();

            // Articulate mechanical bones dynamically
            switch (module) {
                case DRONE_LIFTER -> {
                    float spinSpeed = activeThrust ? 1.6F : 0.35F;
                    float spin = (titan.tickCount + partialTick) * spinSpeed;
                    model.getBone("fan_fl").ifPresent(f -> f.setRotY(spin));
                    model.getBone("fan_fr").ifPresent(f -> f.setRotY(-spin));
                    model.getBone("fan_rl").ifPresent(f -> f.setRotY(-spin));
                    model.getBone("fan_rr").ifPresent(f -> f.setRotY(spin));
                }
                case ROCKET_JETPACK -> {
                    if (activeThrust) {
                        float wobble = (float) Math.sin((titan.tickCount + partialTick) * 0.25F) * 0.06F;
                        model.getBone("nozzle_left").ifPresent(n -> n.setRotX(0.12F + wobble));
                        model.getBone("nozzle_right").ifPresent(n -> n.setRotX(0.12F - wobble));
                    } else {
                        model.getBone("nozzle_left").ifPresent(n -> n.setRotX(0.0F));
                        model.getBone("nozzle_right").ifPresent(n -> n.setRotX(0.0F));
                    }
                }
                case VTOL_GLIDE -> {
                    if (activeThrust) {
                        float flex = (float) Math.sin((titan.tickCount + partialTick) * 0.15F) * 0.02F;
                        model.getBone("left_wing").ifPresent(w -> {
                            w.setRotZ(-0.08F + flex);
                            w.setRotY(0.05F);
                        });
                        model.getBone("right_wing").ifPresent(w -> {
                            w.setRotZ(0.08F - flex);
                            w.setRotY(-0.05F);
                        });
                    } else {
                        model.getBone("left_wing").ifPresent(w -> {
                            w.setRotZ(0.0F);
                            w.setRotY(0.0F);
                        });
                        model.getBone("right_wing").ifPresent(w -> {
                            w.setRotZ(0.0F);
                            w.setRotY(0.0F);
                        });
                    }
                }
                default -> {}
            }

            RenderType modType = RenderType.entityCutoutNoCull(new ResourceLocation(TitanCombatMod.MODID, texturePath));
            VertexConsumer modBuffer = bufferSource.getBuffer(modType);

            List<GeoBone> roots = model.topLevelBones();
            if (roots != null && !roots.isEmpty()) {
                for (GeoBone rootBone : roots) {
                    rootBone.setHidden(false);
                    getRenderer().renderRecursively(poseStack, titan, rootBone, modType, bufferSource, modBuffer, false, partialTick,
                            packedLight, packedOverlay, 1.0F, 1.0F, 1.0F, 1.0F);
                }
            } else {
                model.getBone("root").or(() -> model.getBone("docking_mount")).ifPresent(b -> {
                    b.setHidden(false);
                    getRenderer().renderRecursively(poseStack, titan, b, modType, bufferSource, modBuffer, false, partialTick,
                            packedLight, packedOverlay, 1.0F, 1.0F, 1.0F, 1.0F);
                });
            }
        } finally {
            poseStack.popPose();
            this.drawing = false;
            bufferSource.getBuffer(renderType);
        }
    }
}
