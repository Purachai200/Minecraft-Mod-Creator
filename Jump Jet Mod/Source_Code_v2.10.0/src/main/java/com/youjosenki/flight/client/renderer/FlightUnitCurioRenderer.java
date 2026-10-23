package com.youjosenki.flight.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.datafixers.util.Pair;
import com.mojang.math.Axis;
import com.youjosenki.flight.client.model.FlightUnitModel;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.blockentity.BannerRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.ModelBakery;
import net.minecraft.core.Holder;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.DyeableLeatherItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BannerBlockEntity;
import net.minecraft.world.level.block.entity.BannerPattern;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.client.ICurioRenderer;

import java.util.List;

public class FlightUnitCurioRenderer implements ICurioRenderer {
    public static final ResourceLocation TEXTURE_BASE =
            new ResourceLocation("youjosenki", "textures/models/armor/elenium_flight_unit.png");
    public static final ResourceLocation TEXTURE_OVERLAY =
            new ResourceLocation("youjosenki", "textures/models/armor/elenium_flight_unit_overlay.png");

    private FlightUnitModel<LivingEntity> model;
    private ModelPart insigniaPlate;
    private int lastTagHash = 0;
    private List<Pair<Holder<BannerPattern>, DyeColor>> cachedPatterns = null;

    @Override
    public <T extends LivingEntity, M extends EntityModel<T>> void render(
            ItemStack stack,
            SlotContext slotContext,
            PoseStack matrixStack,
            RenderLayerParent<T, M> renderLayerParent,
            MultiBufferSource renderTypeBuffer,
            int light,
            float limbSwing,
            float limbSwingAmount,
            float partialTicks,
            float ageInTicks,
            float netHeadYaw,
            float headPitch) {

        if (model == null) {
            model = new FlightUnitModel<>(Minecraft.getInstance().getEntityModels().bakeLayer(FlightUnitModel.LAYER_LOCATION));
        }

        M parentModel = renderLayerParent.getModel();
        if (parentModel instanceof HumanoidModel<?> humanoid) {
            // Synchronize with humanoid torso and legs
            model.body.copyFrom(humanoid.body);
            model.harness.copyFrom(humanoid.body);
            model.rightLeg.copyFrom(humanoid.rightLeg);
            model.leftLeg.copyFrom(humanoid.leftLeg);
            model.backJetpack.copyFrom(humanoid.body);
            model.tacticalWings.copyFrom(humanoid.body);
            model.heavyTanks.copyFrom(humanoid.body);
            model.twinDriveTorso.copyFrom(humanoid.body);
            model.siegeFrame.copyFrom(humanoid.body);
            model.thrustBootsRight.copyFrom(humanoid.rightLeg);
            model.thrustBootsLeft.copyFrom(humanoid.leftLeg);
            model.hydroSkimmerTorso.copyFrom(humanoid.body);
            model.hydroSkimmerRight.copyFrom(humanoid.rightLeg);
            model.hydroSkimmerLeft.copyFrom(humanoid.leftLeg);
            model.tacticalScuba.copyFrom(humanoid.body);
            model.urbanExoHarness.copyFrom(humanoid.body);
            model.urbanExoRight.copyFrom(humanoid.rightLeg);
            model.urbanExoLeft.copyFrom(humanoid.leftLeg);
            model.urbanExoRightArm.copyFrom(humanoid.rightArm);
            model.urbanExoLeftArm.copyFrom(humanoid.leftArm);
            model.divingMask.copyFrom(humanoid.head);

            boolean isFlying = false;
            if (slotContext.entity() instanceof net.minecraft.world.entity.player.Player player) {
                isFlying = player.getAbilities().flying;
            }
            boolean isSprinting = slotContext.entity().isSprinting();
            boolean onGround = slotContext.entity().onGround();

            // Dynamic Wings Animation:
            // 1. On ground / walking: wings folded like insect elytra wings (angled diagonally down toward the ground along the hips)
            // 2. Flying cruising: wings fully deployed & extended horizontally for maximum lift
            // 3. Sprinting / Boosting: wings swept back into supersonic delta dagger
            if (!isFlying || onGround) {
                // Insect wing fold: swept back along the spine and angled down diagonally toward the ground
                model.leftWing.yRot = 0.85F;
                model.leftWing.zRot = -0.92F;
                model.leftWing.xRot = 0.18F;
                model.rightWing.yRot = -0.85F;
                model.rightWing.zRot = 0.92F;
                model.rightWing.xRot = 0.18F;
            } else if (isSprinting) {
                // High-speed supersonic swept-back delta dagger
                model.leftWing.yRot = 0.65F;
                model.leftWing.zRot = -0.10F;
                model.leftWing.xRot = 0.0F;
                model.rightWing.yRot = -0.65F;
                model.rightWing.zRot = 0.10F;
                model.rightWing.xRot = 0.0F;
            } else {
                // Cruising: fully extended horizontal lift wings
                model.leftWing.yRot = 0.0F;
                model.leftWing.zRot = 0.0F;
                model.leftWing.xRot = 0.0F;
                model.rightWing.yRot = 0.0F;
                model.rightWing.zRot = 0.0F;
                model.rightWing.xRot = 0.0F;
            }

            // Note: model.rightLeg is synchronized directly with humanoid.rightLeg via copyFrom()
            // above, ensuring it stays 100% attached across all animations (sprint, dive, parcool).

            FlightUnitModel.FlightDesign design = FlightUnitModel.FlightDesign.MAGE_UNIT;
            if (stack.getItem() instanceof EleniumFlightUnitItem item) {
                design = item.getFlightDesign();
            }

            // 1. Get dyed color or default color
            int color = 0x3A4850;
            if (stack.getItem() instanceof DyeableLeatherItem dyeable) {
                color = dyeable.getColor(stack);
            }
            float r = (float) (color >> 16 & 255) / 255.0F;
            float g = (float) (color >> 8 & 255) / 255.0F;
            float b = (float) (color & 255) / 255.0F;

            // 2. Render dyeable armor plate base layer
            VertexConsumer baseConsumer = renderTypeBuffer.getBuffer(RenderType.entityCutoutNoCull(TEXTURE_BASE));
            model.renderDesign(matrixStack, baseConsumer, light, OverlayTexture.NO_OVERLAY, r, g, b, 1.0F, design);

            // 3. Render overlay (emissive glowing mana crystal / jet nozzles / hazard stripes at full bright light!)
            VertexConsumer overlayConsumer = renderTypeBuffer.getBuffer(RenderType.entityTranslucentCull(TEXTURE_OVERLAY));
            model.renderDesign(matrixStack, overlayConsumer, 0xF000F0, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F, design);

            // 4. Render Faction Banner Insignia Decal (if player decorated the flight unit with a banner!)
            CompoundTag blockEntityTag = stack.getTagElement("BlockEntityTag");
            if (blockEntityTag != null && (blockEntityTag.contains("Base", Tag.TAG_INT) || blockEntityTag.contains("Patterns", Tag.TAG_LIST))) {
                int tagHash = blockEntityTag.hashCode();
                if (cachedPatterns == null || tagHash != lastTagHash) {
                    lastTagHash = tagHash;
                    DyeColor baseColor = DyeColor.byId(blockEntityTag.getInt("Base"));
                    ListTag patternsTag = blockEntityTag.getList("Patterns", Tag.TAG_COMPOUND);
                    cachedPatterns = BannerBlockEntity.createPatterns(baseColor, patternsTag);
                }

                if (insigniaPlate == null) {
                    ModelPart shieldModel = Minecraft.getInstance().getEntityModels().bakeLayer(ModelLayers.SHIELD);
                    insigniaPlate = shieldModel.getChild("plate");
                }

                matrixStack.pushPose();
                humanoid.body.translateAndRotate(matrixStack);

                // Position and scale the heraldic crest cleanly on the flight pack backplate
                switch (design) {
                    case MAGE_UNIT -> {
                        // Centered on the upper rear manifold plate
                        matrixStack.translate(0.0, 0.38, 0.285);
                        matrixStack.scale(0.28F, 0.28F, 0.28F);
                    }
                    case BACK_JETPACK -> {
                        // Centered between the dual turbines on the manifold plate
                        matrixStack.translate(0.0, 0.36, 0.295);
                        matrixStack.scale(0.26F, 0.26F, 0.26F);
                    }
                    case TACTICAL_WINGS -> {
                        // On the avionics fuselage controller plate between the swept wings
                        matrixStack.translate(0.0, 0.38, 0.305);
                        matrixStack.scale(0.30F, 0.30F, 0.30F);
                    }
                    case HEAVY_ROCKET -> {
                        // On the armored center mounting bulkhead between the giant rocket thrusters
                        matrixStack.translate(0.0, 0.38, 0.310);
                        matrixStack.scale(0.32F, 0.32F, 0.32F);
                    }
                    case TWIN_DRIVE_EXO -> {
                        // Centered on the high-output Elenium injection manifold
                        matrixStack.translate(0.0, 0.36, 0.295);
                        matrixStack.scale(0.28F, 0.28F, 0.28F);
                    }
                    case SIEGE_ARTILLERY -> {
                        // Centered on the heavy armored siege reactor box
                        matrixStack.translate(0.0, 0.38, 0.325);
                        matrixStack.scale(0.30F, 0.30F, 0.30F);
                    }
                }

                // Invert rotation so the heraldic face points outwards toward 3rd-person camera
                matrixStack.mulPose(Axis.YP.rotationDegrees(180.0F));

                BannerRenderer.renderPatterns(
                        matrixStack,
                        renderTypeBuffer,
                        light,
                        OverlayTexture.NO_OVERLAY,
                        insigniaPlate,
                        ModelBakery.SHIELD_BASE,
                        false, // false = shield sheet patterns
                        cachedPatterns
                );

                matrixStack.popPose();
            }
        }
    }
}
