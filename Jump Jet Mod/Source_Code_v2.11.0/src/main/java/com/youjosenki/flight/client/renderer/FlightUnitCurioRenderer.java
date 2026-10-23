package com.youjosenki.flight.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.datafixers.util.Pair;
import com.mojang.math.Axis;
import com.youjosenki.flight.client.model.FlightUnitModel;
import com.youjosenki.flight.client.geo.FlightRigRenderer;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
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
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BannerBlockEntity;
import net.minecraft.world.level.block.entity.BannerPattern;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.client.ICurioRenderer;

import java.util.List;

public class FlightUnitCurioRenderer implements ICurioRenderer {
    private FlightRigRenderer rig;
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

        M parentModel = renderLayerParent.getModel();
        if (parentModel instanceof HumanoidModel<?> humanoid && stack.getItem() instanceof EleniumFlightUnitItem item) {
            // GeckoLib rig: bones follow the humanoid pose, keyframes + mechanics come from FlightRigGeoModel
            if (rig == null) {
                rig = new FlightRigRenderer();
            }
            rig.prepForRender(slotContext.entity(), stack, item.getEquipSlot(), humanoid);
            rig.renderToBuffer(matrixStack, null, light, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);

            FlightUnitModel.FlightDesign design = item.getFlightDesign();

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
