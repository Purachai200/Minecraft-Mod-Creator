package com.titancombat.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.titancombat.TitanCombatMod;
import com.titancombat.entity.AegisStrikerEntity;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;

public class AegisStrikerModel extends EntityModel<AegisStrikerEntity> {
    public static final ModelLayerLocation LAYER_LOCATION =
            new ModelLayerLocation(new ResourceLocation(TitanCombatMod.MODID, "aegis_striker"), "main");

    private final ModelPart root;
    private final ModelPart torso;
    private final ModelPart cockpit;
    private final ModelPart leftLeg;
    private final ModelPart rightLeg;
    private final ModelPart leftArm;
    private final ModelPart rightArm;

    public AegisStrikerModel(ModelPart root) {
        this.root = root;
        this.torso = root.getChild("torso");
        this.cockpit = this.torso.getChild("cockpit");
        this.leftLeg = root.getChild("left_leg");
        this.rightLeg = root.getChild("right_leg");
        this.leftArm = this.torso.getChild("left_arm");
        this.rightArm = this.torso.getChild("right_arm");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition meshdefinition = new MeshDefinition();
        PartDefinition partdefinition = meshdefinition.getRoot();

        // Main Torso Chassis (Heavy Assault Frame)
        PartDefinition torso = partdefinition.addOrReplaceChild("torso",
                CubeListBuilder.create()
                        .texOffs(0, 0).addBox(-14.0F, -38.0F, -10.0F, 28.0F, 20.0F, 20.0F, new CubeDeformation(0.0F)) // Upper Torso
                        .texOffs(0, 40).addBox(-10.0F, -18.0F, -7.0F, 20.0F, 10.0F, 14.0F, new CubeDeformation(0.0F)) // Lower Waist
                        .texOffs(68, 40).addBox(-12.0F, -36.0F, 10.0F, 24.0F, 14.0F, 8.0F, new CubeDeformation(0.0F)), // Rear Thruster Packs
                PartPose.offset(0.0F, 8.0F, 0.0F));

        // Armored Cockpit Hatch & Visor
        torso.addOrReplaceChild("cockpit",
                CubeListBuilder.create()
                        .texOffs(76, 0).addBox(-8.0F, -34.0F, -14.0F, 16.0F, 14.0F, 8.0F, new CubeDeformation(0.0F)) // Front Hatch
                        .texOffs(76, 22).addBox(-6.0F, -30.0F, -15.0F, 12.0F, 5.0F, 2.0F, new CubeDeformation(0.0F)), // Visor Slit
                PartPose.ZERO);

        // Heavy Weapon Arms / Autocannon Pods
        torso.addOrReplaceChild("left_arm",
                CubeListBuilder.create()
                        .texOffs(0, 64).addBox(0.0F, -4.0F, -6.0F, 8.0F, 10.0F, 12.0F, new CubeDeformation(0.0F)) // Shoulder Pad
                        .texOffs(40, 64).addBox(2.0F, 6.0F, -16.0F, 6.0F, 8.0F, 24.0F, new CubeDeformation(0.0F)), // Kinetic Cannon
                PartPose.offset(14.0F, -32.0F, 0.0F));

        torso.addOrReplaceChild("right_arm",
                CubeListBuilder.create()
                        .texOffs(0, 64).mirror().addBox(-8.0F, -4.0F, -6.0F, 8.0F, 10.0F, 12.0F, new CubeDeformation(0.0F)).mirror(false)
                        .texOffs(40, 64).mirror().addBox(-8.0F, 6.0F, -16.0F, 6.0F, 8.0F, 24.0F, new CubeDeformation(0.0F)).mirror(false),
                PartPose.offset(-14.0F, -32.0F, 0.0F));

        // Multi-Jointed Heavy Legs
        partdefinition.addOrReplaceChild("left_leg",
                CubeListBuilder.create()
                        .texOffs(0, 96).addBox(-4.0F, 0.0F, -5.0F, 8.0F, 14.0F, 10.0F, new CubeDeformation(0.0F)) // Thigh
                        .texOffs(36, 96).addBox(-3.0F, 14.0F, -4.0F, 6.0F, 12.0F, 8.0F, new CubeDeformation(0.0F)) // Shin
                        .texOffs(64, 96).addBox(-5.0F, 22.0F, -10.0F, 10.0F, 4.0F, 16.0F, new CubeDeformation(0.0F)), // Foot
                PartPose.offset(8.0F, -2.0F, 0.0F));

        partdefinition.addOrReplaceChild("right_leg",
                CubeListBuilder.create()
                        .texOffs(0, 96).mirror().addBox(-4.0F, 0.0F, -5.0F, 8.0F, 14.0F, 10.0F, new CubeDeformation(0.0F)).mirror(false)
                        .texOffs(36, 96).mirror().addBox(-3.0F, 14.0F, -4.0F, 6.0F, 12.0F, 8.0F, new CubeDeformation(0.0F)).mirror(false)
                        .texOffs(64, 96).mirror().addBox(-5.0F, 22.0F, -10.0F, 10.0F, 4.0F, 16.0F, new CubeDeformation(0.0F)).mirror(false),
                PartPose.offset(-8.0F, -2.0F, 0.0F));

        return LayerDefinition.create(meshdefinition, 128, 128);
    }

    @Override
    public void setupAnim(AegisStrikerEntity entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        // Natural heavy hydraulic walking animation
        this.leftLeg.xRot = Mth.cos(limbSwing * 0.4F) * 0.6F * limbSwingAmount;
        this.rightLeg.xRot = Mth.cos(limbSwing * 0.4F + (float) Math.PI) * 0.6F * limbSwingAmount;

        // Arm counter-swing
        this.leftArm.xRot = Mth.cos(limbSwing * 0.4F + (float) Math.PI) * 0.25F * limbSwingAmount;
        this.rightArm.xRot = Mth.cos(limbSwing * 0.4F) * 0.25F * limbSwingAmount;

        // Torso tilt with rider aim
        this.torso.yRot = netHeadYaw * ((float) Math.PI / 180F) * 0.5F;
        this.cockpit.xRot = headPitch * ((float) Math.PI / 180F) * 0.3F;
    }

    @Override
    public void renderToBuffer(PoseStack poseStack, VertexConsumer vertexConsumer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        root.render(poseStack, vertexConsumer, packedLight, packedOverlay, red, green, blue, alpha);
    }
}
