package com.youjosenki.flight.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import org.jetbrains.annotations.NotNull;

public class FlightUnitModel<T extends LivingEntity> extends EntityModel<T> {
    public static final ModelLayerLocation LAYER_LOCATION =
            new ModelLayerLocation(new ResourceLocation("youjosenki", "flight_unit"), "main");

    public enum FlightDesign {
        MAGE_UNIT("Imperial Aerial Mage Rig"),
        BACK_JETPACK("Conventional Combat Jetpack"),
        TACTICAL_WINGS("Tactical Apex Glider-Jet"),
        HEAVY_ROCKET("Titan Industrial Rocket Rig"),
        TWIN_DRIVE_EXO("Type 95 Quad-Core Exoskeleton"),
        SIEGE_ARTILLERY("Titan Siege Assault Rig"),
        THRUST_BOOTS("Valkyrie Hover-Thrust Boots"),
        HYDRO_SKIMMER("Aquasurf Hydro-Glider Rig"),
        TACTICAL_SCUBA("Abyssal Combat Scuba Rig"),
        URBAN_EXO_LEGS("Urban Tactical Kinetic Exoskeleton"),
        DIVING_MASK("Abyssal Tactical Diving Mask");

        private final String displayName;

        FlightDesign(String name) {
            this.displayName = name;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    public final ModelPart body;
    public final ModelPart rightLeg;
    public final ModelPart leftLeg;
    public final ModelPart harness;
    public final ModelPart backJetpack;
    public final ModelPart tacticalWings;
    public final ModelPart leftWing;
    public final ModelPart rightWing;
    public final ModelPart heavyTanks;
    public final ModelPart twinDriveTorso;
    public final ModelPart siegeFrame;
    public final ModelPart thrustBootsRight;
    public final ModelPart thrustBootsLeft;
    public final ModelPart hydroSkimmerTorso;
    public final ModelPart hydroSkimmerRight;
    public final ModelPart hydroSkimmerLeft;
    public final ModelPart tacticalScuba;
    public final ModelPart urbanExoHarness;
    public final ModelPart urbanExoRight;
    public final ModelPart urbanExoLeft;
    public final ModelPart urbanExoRightArm;
    public final ModelPart urbanExoLeftArm;
    public final ModelPart divingMask;

    public FlightUnitModel(ModelPart root) {
        this.body = root.getChild("body");
        this.rightLeg = root.getChild("right_leg");
        this.leftLeg = root.getChild("left_leg");
        this.harness = root.getChild("harness");
        this.backJetpack = root.getChild("back_jetpack");
        this.tacticalWings = root.getChild("tactical_wings");
        this.leftWing = this.tacticalWings.getChild("left_wing");
        this.rightWing = this.tacticalWings.getChild("right_wing");
        this.heavyTanks = root.getChild("heavy_tanks");
        this.twinDriveTorso = root.getChild("twin_drive_torso");
        this.siegeFrame = root.getChild("siege_frame");
        this.thrustBootsRight = root.getChild("thrust_boots_right");
        this.thrustBootsLeft = root.getChild("thrust_boots_left");
        this.hydroSkimmerTorso = root.getChild("hydro_skimmer_torso");
        this.hydroSkimmerRight = root.getChild("hydro_skimmer_right");
        this.hydroSkimmerLeft = root.getChild("hydro_skimmer_left");
        this.tacticalScuba = root.getChild("tactical_scuba");
        this.urbanExoHarness = root.getChild("urban_exo_harness");
        this.urbanExoRight = root.getChild("urban_exo_right");
        this.urbanExoLeft = root.getChild("urban_exo_left");
        this.urbanExoRightArm = root.getChild("urban_exo_right_arm");
        this.urbanExoLeftArm = root.getChild("urban_exo_left_arm");
        this.divingMask = root.getChild("diving_mask");
    }

    public static LayerDefinition createBodyLayer() {
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();

        // 0. Base Harness Rig (Shared across all designs - Realistic 3D Military Combat Webbing)
        root.addOrReplaceChild("harness", CubeListBuilder.create()
                // Left & Right Load-Bearing Shoulder Straps
                .texOffs(0, 0).addBox(1.4F, -0.2F, -2.5F, 2.3F, 11.5F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(-3.7F, -0.2F, -2.5F, 2.3F, 11.5F, 0.7F, new CubeDeformation(0.0F))
                // Shoulder Shock-Absorber Epaulet Pads (distributing weight of rear thruster)
                .texOffs(0, 0).addBox(1.2F, -0.7F, -2.6F, 3.0F, 1.2F, 5.2F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(-4.2F, -0.7F, -2.6F, 3.0F, 1.2F, 5.2F, new CubeDeformation(0.0F))
                // Tactical Chest Sternum Cross-Connector & Locking Buckle
                .texOffs(0, 0).addBox(-2.0F, 2.8F, -2.7F, 4.0F, 1.8F, 0.8F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.0F, 2.6F, -3.0F, 2.0F, 2.2F, 0.6F, new CubeDeformation(0.0F))
                // Quick-Release D-Rings on Chest Straps
                .texOffs(32, 64).addBox(1.8F, 4.8F, -2.8F, 1.2F, 1.2F, 0.4F, new CubeDeformation(0.0F))
                .texOffs(32, 64).mirror().addBox(-3.0F, 4.8F, -2.8F, 1.2F, 1.2F, 0.4F, new CubeDeformation(0.0F))
                // Heavy Armored Waist Cummerbund & Combat Belt
                .texOffs(0, 0).addBox(-4.4F, 8.8F, -2.5F, 8.8F, 2.4F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.3F, 8.6F, -2.8F, 2.6F, 2.8F, 0.6F, new CubeDeformation(0.0F))
                // Left & Right Tactical Utility Pouches on Belt Flanks
                .texOffs(40, 0).addBox(3.8F, 8.2F, -1.2F, 1.2F, 3.2F, 2.4F, new CubeDeformation(0.0F))
                .texOffs(40, 0).mirror().addBox(-5.0F, 8.2F, -1.2F, 1.2F, 3.2F, 2.4F, new CubeDeformation(0.0F))
                // Twin Spinal Exoskeleton Mounting Rails on Back
                .texOffs(40, 8).addBox(-2.0F, 1.0F, 1.9F, 1.4F, 8.5F, 0.6F, new CubeDeformation(0.0F))
                .texOffs(40, 8).addBox(0.6F, 1.0F, 1.9F, 1.4F, 8.5F, 0.6F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // 1. MAGE UNIT: TORSO & ABDOMEN CORE (AUTHENTIC MILITARY APPARATUS)
        // ==========================================
        root.addOrReplaceChild("body", CubeListBuilder.create()
                // 3D Tactical Shoulder Suspension Straps
                .texOffs(0, 0).addBox(1.4F, -0.2F, -2.5F, 2.3F, 11.5F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(-3.7F, -0.2F, -2.5F, 2.3F, 11.5F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(1.2F, -0.7F, -2.6F, 3.0F, 1.2F, 5.2F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(-4.2F, -0.7F, -2.6F, 3.0F, 1.2F, 5.2F, new CubeDeformation(0.0F))
                // Heavy Waist Belt & Buckle
                .texOffs(0, 0).addBox(-4.4F, 8.8F, -2.5F, 8.8F, 2.4F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.3F, 8.6F, -2.8F, 2.6F, 2.8F, 0.6F, new CubeDeformation(0.0F))
                // Rear Manifold on back of torso
                .texOffs(40, 0).addBox(-3.8F, 1.8F, 2.1F, 7.6F, 8.2F, 2.4F, new CubeDeformation(0.0F))
                // Center Boiler Steam Tank on back
                .texOffs(0, 64).addBox(-1.8F, 1.0F, 3.6F, 3.6F, 9.5F, 2.0F, new CubeDeformation(0.0F))
                // Stepped cooling fins down the spine of the rear manifold
                .texOffs(40, 8).addBox(-0.8F, 2.6F, 5.4F, 1.6F, 6.8F, 0.8F, new CubeDeformation(0.0F))
                // Lower Exhaust Vent Ports on back
                .texOffs(48, 64).addBox(-2.8F, 9.8F, 2.6F, 2.0F, 2.0F, 1.8F, new CubeDeformation(0.0F))
                .texOffs(48, 70).addBox(0.8F, 9.8F, 2.6F, 2.0F, 2.0F, 1.8F, new CubeDeformation(0.0F))
                // Main Abdomen Propulsion Engine Housing
                .texOffs(0, 16).addBox(-3.6F, 4.2F, -5.4F, 7.2F, 7.0F, 3.4F, new CubeDeformation(0.0F))
                // Upper Aerodynamic Cowl & Valve Hood
                .texOffs(24, 16).addBox(-3.0F, 3.0F, -5.2F, 6.0F, 1.4F, 3.0F, new CubeDeformation(0.0F))
                // Dual Top Intake Scoops
                .texOffs(42, 16).addBox(-2.8F, 1.8F, -5.0F, 2.0F, 1.4F, 2.4F, new CubeDeformation(0.0F))
                .texOffs(42, 20).addBox(0.8F, 1.8F, -5.0F, 2.0F, 1.4F, 2.4F, new CubeDeformation(0.0F))
                // Left & Right Cooling Louvers
                .texOffs(0, 27).addBox(-4.4F, 4.8F, -5.0F, 1.0F, 6.0F, 2.8F, new CubeDeformation(0.0F))
                .texOffs(0, 36).addBox(3.4F, 4.8F, -5.0F, 1.0F, 6.0F, 2.8F, new CubeDeformation(0.0F))
                // Curved rib mana feed conduits connecting rear manifold to abdomen core
                .texOffs(40, 6).addBox(-4.5F, 5.4F, -2.8F, 1.0F, 1.4F, 5.2F, new CubeDeformation(0.0F))
                .texOffs(40, 6).addBox(3.5F, 5.4F, -2.8F, 1.0F, 1.4F, 5.2F, new CubeDeformation(0.0F))
                // Analog pressure / mana calibration dials on upper flanks
                .texOffs(32, 64).addBox(-4.4F, 3.2F, -4.8F, 1.2F, 2.0F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(32, 64).mirror().addBox(3.2F, 3.2F, -4.8F, 1.2F, 2.0F, 2.0F, new CubeDeformation(0.0F))
                // Multi-tiered Brass Bezel Collar framing core
                .texOffs(24, 26).addBox(-2.5F, 5.4F, -5.9F, 5.0F, 5.0F, 0.6F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-2.0F, 5.9F, -6.3F, 4.0F, 4.0F, 0.5F, new CubeDeformation(0.0F))
                // Protruding Radiant Mana Computation Crystal
                .texOffs(36, 26).addBox(-1.4F, 6.5F, -6.7F, 2.8F, 2.8F, 0.7F, new CubeDeformation(0.0F))
                // Lower Keel Skirt Armor Plate
                .texOffs(0, 46).addBox(-3.2F, 11.0F, -5.0F, 6.4F, 2.4F, 3.4F, new CubeDeformation(0.0F))
                // Underside Directional Thrust Nozzles
                .texOffs(20, 46).addBox(-2.4F, 13.2F, -4.5F, 1.8F, 1.4F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(28, 46).addBox(0.6F, 13.2F, -4.5F, 1.8F, 1.4F, 2.2F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // MECHANICAL LEG STRUTS & STIRRUPS (UPGRADED HIGH REALISM)
        // ==========================================
        // Right leg (Mechanical strut & stirrup)
        root.addOrReplaceChild("right_leg", CubeListBuilder.create()
                .texOffs(64, 0).mirror().addBox(-3.4F, 0.5F, -1.5F, 1.5F, 2.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(64, 6).mirror().addBox(-3.2F, 2.2F, -1.3F, 1.3F, 4.0F, 1.1F, new CubeDeformation(0.0F))
                .texOffs(70, 6).mirror().addBox(-3.2F, 2.2F, 0.2F, 1.3F, 4.0F, 1.1F, new CubeDeformation(0.0F))
                // Hydraulic shock absorber damper piston running behind the knee
                .texOffs(64, 6).mirror().addBox(-2.8F, 4.0F, 0.9F, 1.0F, 4.2F, 1.0F, new CubeDeformation(0.0F))
                // Front knee armor reinforcement
                .texOffs(64, 15).mirror().addBox(-3.0F, 4.8F, -1.9F, 1.6F, 1.8F, 0.6F, new CubeDeformation(0.0F))
                .texOffs(64, 15).mirror().addBox(-3.4F, 5.8F, -1.6F, 1.6F, 1.8F, 3.2F, new CubeDeformation(0.0F))
                .texOffs(64, 22).mirror().addBox(-3.2F, 7.4F, -1.0F, 1.3F, 4.2F, 2.0F, new CubeDeformation(0.0F))
                // Ankle tension stabilizing linkage rod
                .texOffs(70, 6).mirror().addBox(-3.3F, 8.2F, -1.8F, 0.8F, 2.6F, 0.8F, new CubeDeformation(0.0F))
                .texOffs(64, 34).mirror().addBox(-3.1F, 10.5F, -2.2F, 1.8F, 1.5F, 4.4F, new CubeDeformation(0.0F))
                .texOffs(76, 0).mirror().addBox(-2.6F, 11.6F, -3.8F, 4.6F, 1.2F, 7.6F, new CubeDeformation(0.0F))
                .texOffs(76, 10).mirror().addBox(-2.4F, 10.4F, -5.6F, 4.2F, 1.5F, 1.9F, new CubeDeformation(0.0F))
                .texOffs(76, 15).mirror().addBox(-1.7F, 10.0F, 3.6F, 2.6F, 2.4F, 2.5F, new CubeDeformation(0.0F))
                // Lateral foot clamp lock brackets gripping boot
                .texOffs(76, 0).mirror().addBox(-2.7F, 11.0F, -2.2F, 0.5F, 1.4F, 4.2F, new CubeDeformation(0.0F))
                .texOffs(76, 0).mirror().addBox(1.9F, 11.0F, -2.2F, 0.5F, 1.4F, 4.2F, new CubeDeformation(0.0F)),
                PartPose.offset(-1.9F, 12.0F, 0.0F)
        );

        // Left leg (Matching mechanical strut & stirrup for dual-leg exoskeleton rigs)
        root.addOrReplaceChild("left_leg", CubeListBuilder.create()
                .texOffs(64, 0).addBox(1.9F, 0.5F, -1.5F, 1.5F, 2.0F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(64, 6).addBox(1.9F, 2.2F, -1.3F, 1.3F, 4.0F, 1.1F, new CubeDeformation(0.0F))
                .texOffs(70, 6).addBox(1.9F, 2.2F, 0.2F, 1.3F, 4.0F, 1.1F, new CubeDeformation(0.0F))
                // Hydraulic shock absorber damper piston running behind the knee
                .texOffs(64, 6).addBox(1.8F, 4.0F, 0.9F, 1.0F, 4.2F, 1.0F, new CubeDeformation(0.0F))
                // Front knee armor reinforcement
                .texOffs(64, 15).addBox(1.4F, 4.8F, -1.9F, 1.6F, 1.8F, 0.6F, new CubeDeformation(0.0F))
                .texOffs(64, 15).addBox(1.8F, 5.8F, -1.6F, 1.6F, 1.8F, 3.2F, new CubeDeformation(0.0F))
                .texOffs(64, 22).addBox(1.9F, 7.4F, -1.0F, 1.3F, 4.2F, 2.0F, new CubeDeformation(0.0F))
                // Ankle tension stabilizing linkage rod
                .texOffs(70, 6).addBox(2.5F, 8.2F, -1.8F, 0.8F, 2.6F, 0.8F, new CubeDeformation(0.0F))
                .texOffs(64, 34).addBox(1.3F, 10.5F, -2.2F, 1.8F, 1.5F, 4.4F, new CubeDeformation(0.0F))
                .texOffs(76, 0).addBox(-2.0F, 11.6F, -3.8F, 4.6F, 1.2F, 7.6F, new CubeDeformation(0.0F))
                .texOffs(76, 10).addBox(-1.8F, 10.4F, -5.6F, 4.2F, 1.5F, 1.9F, new CubeDeformation(0.0F))
                .texOffs(76, 15).addBox(-0.9F, 10.0F, 3.6F, 2.6F, 2.4F, 2.5F, new CubeDeformation(0.0F))
                // Lateral foot clamp lock brackets gripping boot
                .texOffs(76, 0).addBox(-2.1F, 11.0F, -2.2F, 0.5F, 1.4F, 4.2F, new CubeDeformation(0.0F))
                .texOffs(76, 0).addBox(2.5F, 11.0F, -2.2F, 0.5F, 1.4F, 4.2F, new CubeDeformation(0.0F)),
                PartPose.offset(1.9F, 12.0F, 0.0F)
        );

        // ==========================================
        // 2. CONVENTIONAL BACK JETPACK (UPGRADED HIGH REALISM)
        // ==========================================
        root.addOrReplaceChild("back_jetpack", CubeListBuilder.create()
                // Left & Right Turbine Cylinders on back
                .texOffs(0, 64).addBox(-4.2F, 1.5F, 2.3F, 3.2F, 9.0F, 3.2F, new CubeDeformation(0.0F))
                .texOffs(16, 64).addBox(1.0F, 1.5F, 2.3F, 3.2F, 9.0F, 3.2F, new CubeDeformation(0.0F))
                // Top air intake cowlings & spinner hubs
                .texOffs(0, 64).addBox(-4.5F, 0.6F, 2.0F, 3.8F, 1.2F, 3.8F, new CubeDeformation(0.0F))
                .texOffs(16, 64).addBox(0.7F, 0.6F, 2.0F, 3.8F, 1.2F, 3.8F, new CubeDeformation(0.0F))
                .texOffs(48, 64).addBox(-2.9F, 0.3F, 3.6F, 0.6F, 0.6F, 0.6F, new CubeDeformation(0.0F))
                .texOffs(48, 64).addBox(2.3F, 0.3F, 3.6F, 0.6F, 0.6F, 0.6F, new CubeDeformation(0.0F))
                // Center Manifold & Fuel Distributor
                .texOffs(32, 64).addBox(-2.0F, 3.0F, 2.1F, 4.0F, 5.5F, 2.4F, new CubeDeformation(0.0F))
                // Braided fuel cross-feed conduits linking center distributor into turbines
                .texOffs(32, 64).addBox(-3.0F, 4.6F, 4.1F, 6.0F, 1.0F, 1.0F, new CubeDeformation(0.0F))
                // Dual avionics gauge cluster on center manifold
                .texOffs(32, 64).addBox(-1.2F, 4.0F, 4.4F, 2.4F, 2.4F, 0.5F, new CubeDeformation(0.0F))
                // Left & Right Exhaust Bells pointing down
                .texOffs(48, 64).addBox(-3.8F, 10.5F, 2.7F, 2.4F, 2.2F, 2.4F, new CubeDeformation(0.0F))
                .texOffs(48, 70).addBox(1.4F, 10.5F, 2.7F, 2.4F, 2.2F, 2.4F, new CubeDeformation(0.0F))
                // Gimbal thrust vectoring rings around exhaust bells
                .texOffs(48, 64).addBox(-4.1F, 11.2F, 2.4F, 3.0F, 0.8F, 3.0F, new CubeDeformation(0.0F))
                .texOffs(48, 70).addBox(1.1F, 11.2F, 2.4F, 3.0F, 0.8F, 3.0F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // 3. TACTICAL WINGS (UPGRADED HIGH REALISM)
        // ==========================================
        PartDefinition tacticalWings = root.addOrReplaceChild("tactical_wings", CubeListBuilder.create()
                // Center Avionics Flight Controller Pack
                .texOffs(64, 64).addBox(-3.0F, 2.0F, 2.2F, 6.0F, 8.0F, 2.4F, new CubeDeformation(0.0F))
                // Aerodynamic vertical tail fin / rudder rising above shoulders
                .texOffs(64, 64).addBox(-0.5F, -3.2F, 3.2F, 1.0F, 6.8F, 3.2F, new CubeDeformation(0.0F))
                // Supersonic shoulder air intake scoops
                .texOffs(64, 64).addBox(-3.8F, 0.8F, 2.0F, 1.8F, 2.2F, 2.6F, new CubeDeformation(0.0F))
                .texOffs(64, 64).addBox(2.0F, 0.8F, 2.0F, 1.8F, 2.2F, 2.6F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // Swept Left Wing Blade + Flap Actuator Fairing + Micro-Jet Afterburner Nozzle
        tacticalWings.addOrReplaceChild("left_wing", CubeListBuilder.create()
                .texOffs(64, 76).addBox(-9.5F, -0.7F, 0.0F, 9.5F, 3.2F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(96, 64).addBox(-9.8F, -1.3F, -0.7F, 1.8F, 4.5F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(96, 64).addBox(-6.0F, 1.8F, 0.0F, 1.0F, 0.8F, 1.8F, new CubeDeformation(0.0F))
                .texOffs(96, 64).addBox(-9.9F, 0.0F, 1.4F, 1.9F, 2.0F, 1.0F, new CubeDeformation(0.0F)),
                PartPose.offset(-3.0F, 3.5F, 2.8F)
        );

        // Swept Right Wing Blade + Flap Actuator Fairing + Micro-Jet Afterburner Nozzle
        tacticalWings.addOrReplaceChild("right_wing", CubeListBuilder.create()
                .texOffs(64, 82).addBox(0.0F, -0.7F, 0.0F, 9.5F, 3.2F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(106, 64).addBox(8.0F, -1.3F, -0.7F, 1.8F, 4.5F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(106, 64).addBox(5.0F, 1.8F, 0.0F, 1.0F, 0.8F, 1.8F, new CubeDeformation(0.0F))
                .texOffs(106, 64).addBox(8.0F, 0.0F, 1.4F, 1.9F, 2.0F, 1.0F, new CubeDeformation(0.0F)),
                PartPose.offset(3.0F, 3.5F, 2.8F)
        );

        // ==========================================
        // 4. HEAVY INDUSTRIAL ROCKET RIG (UPGRADED HIGH REALISM)
        // ==========================================
        root.addOrReplaceChild("heavy_tanks", CubeListBuilder.create()
                // Armored Torso Heavy Mounting Frame
                .texOffs(0, 96).addBox(-4.2F, 1.0F, 2.2F, 8.4F, 10.0F, 2.4F, new CubeDeformation(0.0F))
                // Massive Heavy Fuel Rockets (Left & Right)
                .texOffs(24, 96).addBox(-5.2F, -0.5F, 2.8F, 4.2F, 12.0F, 4.2F, new CubeDeformation(0.0F))
                .texOffs(42, 96).addBox(1.0F, -0.5F, 2.8F, 4.2F, 12.0F, 4.2F, new CubeDeformation(0.0F))
                // Tubular steel roll-cage protection bars
                .texOffs(0, 96).addBox(-5.8F, 1.5F, 3.2F, 0.8F, 9.0F, 3.4F, new CubeDeformation(0.0F))
                .texOffs(0, 96).addBox(5.0F, 1.5F, 3.2F, 0.8F, 9.0F, 3.4F, new CubeDeformation(0.0F))
                // Upper RCS vernier maneuvering thruster blocks on tank caps
                .texOffs(60, 96).addBox(-4.8F, -1.8F, 3.4F, 3.4F, 1.4F, 3.4F, new CubeDeformation(0.0F))
                .texOffs(74, 96).addBox(1.4F, -1.8F, 3.4F, 3.4F, 1.4F, 3.4F, new CubeDeformation(0.0F))
                // Heavy inter-tank equalizer bridge manifold
                .texOffs(24, 96).addBox(-1.5F, 4.2F, 3.8F, 3.0F, 1.8F, 2.2F, new CubeDeformation(0.0F))
                // Large Heavy Thruster Nozzle Bells
                .texOffs(60, 96).addBox(-4.7F, 11.5F, 3.3F, 3.2F, 2.8F, 3.2F, new CubeDeformation(0.0F))
                .texOffs(74, 96).addBox(1.5F, 11.5F, 3.3F, 3.2F, 2.8F, 3.2F, new CubeDeformation(0.0F))
                // Lower thermal blast deflector plate
                .texOffs(0, 96).addBox(-3.5F, 9.8F, 2.2F, 7.0F, 3.0F, 1.0F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // 5. NEW DESIGN: TYPE 95 QUAD-CORE EXOSKELETON (DUAL-DRIVE)
        // ==========================================
        root.addOrReplaceChild("twin_drive_torso", CubeListBuilder.create()
                // 3D Tactical Shoulder Suspension Straps
                .texOffs(0, 0).addBox(1.4F, -0.2F, -2.5F, 2.3F, 11.5F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(-3.7F, -0.2F, -2.5F, 2.3F, 11.5F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(1.2F, -0.7F, -2.6F, 3.0F, 1.2F, 5.2F, new CubeDeformation(0.0F))
                .texOffs(0, 0).mirror().addBox(-4.2F, -0.7F, -2.6F, 3.0F, 1.2F, 5.2F, new CubeDeformation(0.0F))
                // Heavy Armored Waist Cummerbund & Combat Belt
                .texOffs(0, 0).addBox(-4.4F, 8.8F, -2.5F, 8.8F, 2.4F, 5.0F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.3F, 8.6F, -2.8F, 2.6F, 2.8F, 0.6F, new CubeDeformation(0.0F))
                // High-Output Rear Injection Manifold
                .texOffs(40, 0).addBox(-3.5F, 2.0F, 2.1F, 7.0F, 8.0F, 2.4F, new CubeDeformation(0.0F))
                // Shoulder Mana Radiator Winglets (High altitude cooling fins)
                .texOffs(24, 16).addBox(-4.8F, -1.8F, 2.2F, 1.6F, 4.2F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(24, 16).addBox(3.2F, -1.8F, 2.2F, 1.6F, 4.2F, 2.2F, new CubeDeformation(0.0F))
                // Triple Elenium Injection Thrusters at lower rear
                .texOffs(48, 64).addBox(-3.0F, 10.0F, 2.6F, 1.8F, 2.2F, 1.8F, new CubeDeformation(0.0F))
                .texOffs(48, 64).addBox(-0.9F, 10.0F, 2.6F, 1.8F, 2.2F, 1.8F, new CubeDeformation(0.0F))
                .texOffs(48, 64).addBox(1.2F, 10.0F, 2.6F, 1.8F, 2.2F, 1.8F, new CubeDeformation(0.0F))
                // Front Dual-Core Engine Housing
                .texOffs(0, 16).addBox(-3.8F, 4.2F, -5.2F, 7.6F, 7.2F, 3.2F, new CubeDeformation(0.0F))
                .texOffs(24, 16).addBox(-3.2F, 3.2F, -5.0F, 6.4F, 1.2F, 2.8F, new CubeDeformation(0.0F))
                // Wide Dual-Core Brass Bezel Collar
                .texOffs(24, 26).addBox(-3.2F, 5.6F, -5.6F, 6.4F, 4.4F, 0.5F, new CubeDeformation(0.0F))
                // Twin Radiant Mana Computation Crystals (Left & Right Synchronized Orbs)
                .texOffs(36, 26).addBox(-2.7F, 6.2F, -6.1F, 2.3F, 3.2F, 0.7F, new CubeDeformation(0.0F))
                .texOffs(36, 26).addBox(0.4F, 6.2F, -6.1F, 2.3F, 3.2F, 0.7F, new CubeDeformation(0.0F))
                // Central High-Voltage Inter-Core Resonance Coupler
                .texOffs(42, 16).addBox(-0.4F, 6.8F, -6.2F, 0.8F, 2.0F, 0.7F, new CubeDeformation(0.0F))
                // Dual Directional Underbelly Nozzles
                .texOffs(20, 46).addBox(-2.6F, 12.8F, -4.2F, 1.8F, 1.2F, 2.0F, new CubeDeformation(0.0F))
                .texOffs(28, 46).addBox(0.8F, 12.8F, -4.2F, 1.8F, 1.2F, 2.0F, new CubeDeformation(0.0F))
                // Curved rib mana feed conduits
                .texOffs(40, 6).addBox(-4.3F, 5.8F, -2.5F, 0.8F, 1.4F, 4.6F, new CubeDeformation(0.0F))
                .texOffs(40, 6).addBox(3.5F, 5.8F, -2.5F, 0.8F, 1.4F, 4.6F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // 6. NEW DESIGN: TITAN HEAVY SIEGE ASSAULT FRAME
        // ==========================================
        root.addOrReplaceChild("siege_frame", CubeListBuilder.create()
                // Over-Shoulder Heavy Recoil Dampening Gantries
                .texOffs(0, 96).addBox(-4.8F, -2.8F, -1.8F, 2.2F, 3.8F, 6.2F, new CubeDeformation(0.0F))
                .texOffs(0, 96).addBox(2.6F, -2.8F, -1.8F, 2.2F, 3.8F, 6.2F, new CubeDeformation(0.0F))
                // Targeting Sensor Optics on pylons
                .texOffs(36, 26).addBox(-4.6F, -2.2F, -2.4F, 1.8F, 1.8F, 0.8F, new CubeDeformation(0.0F))
                .texOffs(36, 26).addBox(2.8F, -2.2F, -2.4F, 1.8F, 1.8F, 0.8F, new CubeDeformation(0.0F))
                // Heavy Bolted Front Chest Mantlet
                .texOffs(0, 16).addBox(-4.2F, 2.2F, -3.2F, 8.4F, 8.6F, 1.4F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-2.5F, 4.5F, -3.6F, 5.0F, 4.0F, 0.5F, new CubeDeformation(0.0F))
                // Rear Heavy Reactor Housing
                .texOffs(0, 96).addBox(-4.6F, 1.0F, 2.2F, 9.2F, 10.0F, 3.0F, new CubeDeformation(0.0F))
                // Quad Heavy Thruster Matrix (2x2 grid)
                .texOffs(60, 96).addBox(-4.2F, 2.4F, 5.2F, 3.2F, 3.2F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(74, 96).addBox(1.0F, 2.4F, 5.2F, 3.2F, 3.2F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(60, 96).addBox(-4.2F, 6.8F, 5.2F, 3.2F, 3.2F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(74, 96).addBox(1.0F, 6.8F, 5.2F, 3.2F, 3.2F, 2.2F, new CubeDeformation(0.0F))
                // Lower Landing Skid Stabilizers
                .texOffs(0, 110).addBox(-4.4F, 11.0F, 2.8F, 1.4F, 3.2F, 2.6F, new CubeDeformation(0.0F))
                .texOffs(10, 110).addBox(3.0F, 11.0F, 2.8F, 1.4F, 3.2F, 2.6F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // 7. NEW DESIGN: VALKYRIE KINETIC THRUST BOOTS (DUAL-LEG HOVER JETS)
        // ==========================================
        // Right Hover-Thrust Boot
        root.addOrReplaceChild("thrust_boots_right", CubeListBuilder.create()
                // Armored Shin Greave Collar
                .texOffs(64, 0).mirror().addBox(-2.6F, 4.0F, -2.4F, 4.8F, 7.5F, 4.8F, new CubeDeformation(0.0F))
                // Rear Supersonic Rocket Thruster Nozzle Housing
                .texOffs(48, 64).mirror().addBox(-1.8F, 7.0F, 2.4F, 3.6F, 4.5F, 2.8F, new CubeDeformation(0.0F))
                // Directional Hover Exhaust Bell (pointing down-rear)
                .texOffs(48, 70).mirror().addBox(-1.4F, 10.5F, 2.7F, 2.8F, 2.0F, 2.2F, new CubeDeformation(0.0F))
                // Outer Lateral Stabilization Hover Winglet
                .texOffs(64, 76).mirror().addBox(-3.6F, 7.5F, -0.5F, 1.2F, 3.2F, 3.8F, new CubeDeformation(0.0F))
                // Reinforced Toe Kick Plate & Heel Energy Absorber
                .texOffs(76, 10).mirror().addBox(-2.4F, 10.6F, -4.5F, 4.4F, 1.5F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(76, 15).mirror().addBox(-2.0F, 11.2F, 0.5F, 3.8F, 1.0F, 3.5F, new CubeDeformation(0.0F)),
                PartPose.offset(-1.9F, 12.0F, 0.0F)
        );

        // Left Hover-Thrust Boot
        root.addOrReplaceChild("thrust_boots_left", CubeListBuilder.create()
                // Armored Shin Greave Collar
                .texOffs(64, 0).addBox(-2.2F, 4.0F, -2.4F, 4.8F, 7.5F, 4.8F, new CubeDeformation(0.0F))
                // Rear Supersonic Rocket Thruster Nozzle Housing
                .texOffs(48, 64).addBox(-1.8F, 7.0F, 2.4F, 3.6F, 4.5F, 2.8F, new CubeDeformation(0.0F))
                // Directional Hover Exhaust Bell (pointing down-rear)
                .texOffs(48, 70).addBox(-1.4F, 10.5F, 2.7F, 2.8F, 2.0F, 2.2F, new CubeDeformation(0.0F))
                // Outer Lateral Stabilization Hover Winglet
                .texOffs(64, 76).addBox(2.4F, 7.5F, -0.5F, 1.2F, 3.2F, 3.8F, new CubeDeformation(0.0F))
                // Reinforced Toe Kick Plate & Heel Energy Absorber
                .texOffs(76, 10).addBox(-2.0F, 10.6F, -4.5F, 4.4F, 1.5F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(76, 15).addBox(-1.8F, 11.2F, 0.5F, 3.8F, 1.0F, 3.5F, new CubeDeformation(0.0F)),
                PartPose.offset(1.9F, 12.0F, 0.0F)
        );

        // ==========================================
        // 8. NEW DESIGN: AQUASURF HYDRO-GLIDER (WATER SKIMMER RIG)
        // ==========================================
        root.addOrReplaceChild("hydro_skimmer_torso", CubeListBuilder.create()
                // Front Buoyant Hydrofoil Chest Mantlet & Air/Water Separator
                .texOffs(0, 16).addBox(-3.5F, 2.5F, -3.2F, 7.0F, 6.8F, 1.2F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-2.8F, 8.2F, -3.6F, 5.6F, 2.2F, 1.0F, new CubeDeformation(0.0F))
                // Rear Dual Hydro-Pump Waterjet Cowling Housing
                .texOffs(0, 64).addBox(-3.8F, 1.5F, 2.0F, 7.6F, 8.5F, 3.2F, new CubeDeformation(0.0F))
                // Dual Waterjet Jet-Pump Exhaust Nozzles
                .texOffs(48, 70).addBox(-3.2F, 5.5F, 5.0F, 2.4F, 2.4F, 2.2F, new CubeDeformation(0.0F))
                .texOffs(48, 70).addBox(0.8F, 5.5F, 5.0F, 2.4F, 2.4F, 2.2F, new CubeDeformation(0.0F))
                // High-Altitude Hydro-Stabilizer Dorsal Fin
                .texOffs(0, 76).addBox(-0.5F, -0.5F, 3.5F, 1.0F, 9.0F, 3.8F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // Right Hydrofoil Ski-Pontoon
        root.addOrReplaceChild("hydro_skimmer_right", CubeListBuilder.create()
                // Shin Mounting Pylon
                .texOffs(64, 0).mirror().addBox(-3.4F, 3.0F, -1.0F, 1.4F, 3.0F, 2.0F, new CubeDeformation(0.0F))
                // Main Water-Ski Pontoon Body (long hydrodynamic float)
                .texOffs(64, 0).mirror().addBox(-4.2F, 6.0F, -5.5F, 2.4F, 2.8F, 12.0F, new CubeDeformation(0.0F))
                // Upturned Wave-Breaking Prow
                .texOffs(76, 10).mirror().addBox(-4.0F, 4.5F, -7.8F, 2.0F, 2.2F, 2.8F, new CubeDeformation(0.0F))
                // Rear Steering Rudder Fin
                .texOffs(64, 76).mirror().addBox(-3.5F, 5.0F, 5.5F, 0.8F, 3.0F, 2.4F, new CubeDeformation(0.0F)),
                PartPose.offset(-1.9F, 12.0F, 0.0F)
        );

        // Left Hydrofoil Ski-Pontoon
        root.addOrReplaceChild("hydro_skimmer_left", CubeListBuilder.create()
                // Shin Mounting Pylon
                .texOffs(64, 0).addBox(2.0F, 3.0F, -1.0F, 1.4F, 3.0F, 2.0F, new CubeDeformation(0.0F))
                // Main Water-Ski Pontoon Body
                .texOffs(64, 0).addBox(1.8F, 6.0F, -5.5F, 2.4F, 2.8F, 12.0F, new CubeDeformation(0.0F))
                // Upturned Wave-Breaking Prow
                .texOffs(76, 10).addBox(2.0F, 4.5F, -7.8F, 2.0F, 2.2F, 2.8F, new CubeDeformation(0.0F))
                // Rear Steering Rudder Fin
                .texOffs(64, 76).addBox(2.7F, 5.0F, 5.5F, 0.8F, 3.0F, 2.4F, new CubeDeformation(0.0F)),
                PartPose.offset(1.9F, 12.0F, 0.0F)
        );

        // ==========================================
        // 9. NEW DESIGN: ABYSSAL COMBAT SCUBA RIG
        // ==========================================
        root.addOrReplaceChild("tactical_scuba", CubeListBuilder.create()
                // Rear Twin High-Pressure Oxygen / Trimix Cylinders
                .texOffs(0, 96).addBox(-4.2F, 0.0F, 2.2F, 3.6F, 11.5F, 3.6F, new CubeDeformation(0.0F))
                .texOffs(0, 96).addBox(0.6F, 0.0F, 2.2F, 3.6F, 11.5F, 3.6F, new CubeDeformation(0.0F))
                // Tank Retention Straps & Steel Bands
                .texOffs(0, 0).addBox(-4.5F, 3.0F, 1.9F, 9.0F, 1.2F, 4.2F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-4.5F, 8.0F, 1.9F, 9.0F, 1.2F, 4.2F, new CubeDeformation(0.0F))
                // Top Cylinder Valve Manifold & Crossover Pipe
                .texOffs(24, 26).addBox(-3.6F, -1.2F, 2.8F, 2.4F, 1.2F, 2.4F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(1.2F, -1.2F, 2.8F, 2.4F, 1.2F, 2.4F, new CubeDeformation(0.0F))
                .texOffs(40, 8).addBox(-1.5F, -0.8F, 3.5F, 3.0F, 0.8F, 0.8F, new CubeDeformation(0.0F))
                // High-Pressure Dial Barometer / Regulator
                .texOffs(36, 26).addBox(2.2F, -1.8F, 3.0F, 1.6F, 1.6F, 1.2F, new CubeDeformation(0.0F))
                // Front Chest Rebreather / Air Scrubber Canister
                .texOffs(0, 16).addBox(-3.2F, 3.2F, -4.0F, 6.4F, 5.8F, 1.8F, new CubeDeformation(0.0F))
                // Front Depth Gauge / Sonar Meter
                .texOffs(36, 26).addBox(-1.2F, 4.2F, -4.6F, 2.4F, 2.4F, 0.8F, new CubeDeformation(0.0F))
                // Ribbed Shoulder Breathing Hoses (Looping over left & right shoulders)
                .texOffs(40, 8).addBox(1.8F, -1.5F, -2.4F, 1.6F, 1.6F, 5.6F, new CubeDeformation(0.0F))
                .texOffs(40, 8).addBox(-3.4F, -1.5F, -2.4F, 1.6F, 1.6F, 5.6F, new CubeDeformation(0.0F))
                // Waist Dive-Weight Ballast Belt (4 Lead Blocks)
                .texOffs(40, 0).addBox(-3.8F, 9.4F, -2.9F, 1.6F, 2.2F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(40, 0).addBox(2.2F, 9.4F, -2.9F, 1.6F, 2.2F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(40, 0).addBox(-3.8F, 9.4F, 2.2F, 1.6F, 2.2F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(40, 0).addBox(2.2F, 9.4F, 2.2F, 1.6F, 2.2F, 1.0F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // ==========================================
        // 10. NEW DESIGN: CALL OF DUTY STYLE KINETIC TACTICAL EXOSKELETON (ARMS + SPINE + LEGS)
        // ==========================================
        root.addOrReplaceChild("urban_exo_harness", CubeListBuilder.create()
                // Upper Back Capacitor & Power Junction Hub
                .texOffs(0, 64).addBox(-3.0F, 1.2F, 2.2F, 6.0F, 3.8F, 2.0F, new CubeDeformation(0.0F))
                // Tactical Communications Antenna (Left Shoulder)
                .texOffs(40, 8).addBox(-2.8F, -4.5F, 2.6F, 0.6F, 5.8F, 0.6F, new CubeDeformation(0.0F))
                // Tactical Sensor / Shoulder Flashlight (Right Shoulder)
                .texOffs(36, 26).addBox(1.8F, -0.2F, 2.4F, 1.4F, 1.6F, 1.4F, new CubeDeformation(0.0F))
                // Articulated Spinal Column Vertebrae (4 Mechanical Vertebra Segments)
                .texOffs(24, 26).addBox(-1.2F, 4.8F, 2.0F, 2.4F, 1.1F, 1.2F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.0F, 5.9F, 2.0F, 2.0F, 1.1F, 1.1F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.0F, 7.0F, 2.0F, 2.0F, 1.1F, 1.1F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(-1.2F, 8.1F, 2.0F, 2.4F, 1.1F, 1.2F, new CubeDeformation(0.0F))
                // Pelvic Bracing Girdle & Hip Stabilizer Belt
                .texOffs(0, 0).addBox(-4.5F, 9.2F, -2.5F, 9.0F, 2.4F, 5.0F, new CubeDeformation(0.0F))
                // Lower Back Kinetic Capacitor
                .texOffs(0, 64).addBox(-2.5F, 8.2F, 2.2F, 5.0F, 3.4F, 1.6F, new CubeDeformation(0.0F))
                // Dual Hip Rotary Articulation Bearing Hubs
                .texOffs(24, 26).addBox(-5.2F, 9.8F, -1.2F, 1.2F, 2.4F, 2.4F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(4.0F, 9.8F, -1.2F, 1.2F, 2.4F, 2.4F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        // Right Exo Arm (Cantilever Arch + Upper Arm Strut + Elbow Hinge + Forearm Rails + Wrist Cuff)
        root.addOrReplaceChild("urban_exo_right_arm", CubeListBuilder.create()
                // Shoulder Cantilever Ball Arch
                .texOffs(40, 8).mirror().addBox(-1.6F, -2.4F, -1.2F, 3.8F, 1.5F, 2.6F, new CubeDeformation(0.0F))
                // Outer Upper Arm Hydraulic Strut
                .texOffs(40, 8).mirror().addBox(1.2F, -1.0F, -1.0F, 1.2F, 6.2F, 2.0F, new CubeDeformation(0.0F))
                // Rotary Elbow Hinge Joint Hub
                .texOffs(48, 64).mirror().addBox(1.0F, 4.8F, -1.2F, 1.6F, 2.4F, 2.6F, new CubeDeformation(0.0F))
                // Forearm Dual Actuator Rails
                .texOffs(64, 0).mirror().addBox(1.2F, 6.5F, -0.8F, 1.1F, 5.0F, 1.8F, new CubeDeformation(0.0F))
                // Wrist Cuff & Palm Assist Brace
                .texOffs(76, 10).mirror().addBox(-1.8F, 9.8F, -2.2F, 4.4F, 1.5F, 4.4F, new CubeDeformation(0.0F)),
                PartPose.offset(-5.0F, 2.0F, 0.0F)
        );

        // Left Exo Arm (Cantilever Arch + Upper Arm Strut + Elbow Hinge + Forearm Rails + Wrist Cuff)
        root.addOrReplaceChild("urban_exo_left_arm", CubeListBuilder.create()
                // Shoulder Cantilever Ball Arch
                .texOffs(40, 8).addBox(-2.2F, -2.4F, -1.2F, 3.8F, 1.5F, 2.6F, new CubeDeformation(0.0F))
                // Outer Upper Arm Hydraulic Strut
                .texOffs(40, 8).addBox(-2.4F, -1.0F, -1.0F, 1.2F, 6.2F, 2.0F, new CubeDeformation(0.0F))
                // Rotary Elbow Hinge Joint Hub
                .texOffs(48, 64).addBox(-2.6F, 4.8F, -1.2F, 1.6F, 2.4F, 2.6F, new CubeDeformation(0.0F))
                // Forearm Dual Actuator Rails
                .texOffs(64, 0).addBox(-2.3F, 6.5F, -0.8F, 1.1F, 5.0F, 1.8F, new CubeDeformation(0.0F))
                // Wrist Cuff & Palm Assist Brace
                .texOffs(76, 10).addBox(-2.6F, 9.8F, -2.2F, 4.4F, 1.5F, 4.4F, new CubeDeformation(0.0F)),
                PartPose.offset(5.0F, 2.0F, 0.0F)
        );

        // Right Urban Scout Exo-Leg
        root.addOrReplaceChild("urban_exo_right", CubeListBuilder.create()
                // Outer Thigh Lateral Exoskeleton Strut
                .texOffs(40, 8).mirror().addBox(-2.8F, 0.5F, -1.0F, 1.2F, 6.5F, 2.0F, new CubeDeformation(0.0F))
                // Rotary Knee Actuator Hinge Hub
                .texOffs(48, 64).mirror().addBox(-3.1F, 6.0F, -1.5F, 1.6F, 2.6F, 3.0F, new CubeDeformation(0.0F))
                // Rear Hydraulic Compression Piston Cylinder (Behind Calf)
                .texOffs(64, 0).mirror().addBox(-1.2F, 4.0F, 2.0F, 2.4F, 6.0F, 1.8F, new CubeDeformation(0.0F))
                // Internal Sliding Piston Rod
                .texOffs(24, 26).mirror().addBox(-0.8F, 2.0F, 2.2F, 1.6F, 2.5F, 1.4F, new CubeDeformation(0.0F))
                // Shin Armored Guard
                .texOffs(64, 76).mirror().addBox(-2.0F, 5.0F, -2.8F, 4.0F, 6.0F, 1.0F, new CubeDeformation(0.0F))
                // Ankle Shock-Absorber Pivot
                .texOffs(48, 64).mirror().addBox(-2.6F, 9.5F, -0.8F, 1.2F, 2.2F, 2.2F, new CubeDeformation(0.0F))
                // Dual-Plate Kinetic Spring Sole with Ground Cleats
                .texOffs(76, 10).mirror().addBox(-2.2F, 11.2F, -4.2F, 4.4F, 1.2F, 8.0F, new CubeDeformation(0.0F)),
                PartPose.offset(-1.9F, 12.0F, 0.0F)
        );

        // Left Urban Scout Exo-Leg
        root.addOrReplaceChild("urban_exo_left", CubeListBuilder.create()
                // Outer Thigh Lateral Exoskeleton Strut
                .texOffs(40, 8).addBox(1.6F, 0.5F, -1.0F, 1.2F, 6.5F, 2.0F, new CubeDeformation(0.0F))
                // Rotary Knee Actuator Hinge Hub
                .texOffs(48, 64).addBox(1.5F, 6.0F, -1.5F, 1.6F, 2.6F, 3.0F, new CubeDeformation(0.0F))
                // Rear Hydraulic Compression Piston Cylinder (Behind Calf)
                .texOffs(64, 0).addBox(-1.2F, 4.0F, 2.0F, 2.4F, 6.0F, 1.8F, new CubeDeformation(0.0F))
                // Internal Sliding Piston Rod
                .texOffs(24, 26).addBox(-0.8F, 2.0F, 2.2F, 1.6F, 2.5F, 1.4F, new CubeDeformation(0.0F))
                // Shin Armored Guard
                .texOffs(64, 76).addBox(-2.0F, 5.0F, -2.8F, 4.0F, 6.0F, 1.0F, new CubeDeformation(0.0F))
                // Ankle Shock-Absorber Pivot
                .texOffs(48, 64).addBox(1.4F, 9.5F, -0.8F, 1.2F, 2.2F, 2.2F, new CubeDeformation(0.0F))
                // Dual-Plate Kinetic Spring Sole with Ground Cleats
                .texOffs(76, 10).addBox(-2.2F, 11.2F, -4.2F, 4.4F, 1.2F, 8.0F, new CubeDeformation(0.0F)),
                PartPose.offset(1.9F, 12.0F, 0.0F)
        );

        // ==========================================
        // 11. NEW DESIGN: ABYSSAL TACTICAL DIVING MASK (VISOR + REBREATHER MASK)
        // ==========================================
        root.addOrReplaceChild("diving_mask", CubeListBuilder.create()
                // Panoramic Tempered Glass Visor Frame
                .texOffs(36, 26).addBox(-4.2F, -5.8F, -4.8F, 8.4F, 3.2F, 1.0F, new CubeDeformation(0.0F))
                .texOffs(36, 26).addBox(-4.0F, -5.5F, -5.1F, 8.0F, 2.6F, 0.4F, new CubeDeformation(0.0F))
                // Oral-Nasal Rebreather Mask Body (Covering mouth, jaw, and nose)
                .texOffs(0, 16).addBox(-3.2F, -3.2F, -5.2F, 6.4F, 4.0F, 1.8F, new CubeDeformation(0.0F))
                // Dual Cheek Regulator Intake/Exhaust Valve Housings
                .texOffs(24, 26).addBox(-4.2F, -2.4F, -4.8F, 1.4F, 2.2F, 1.8F, new CubeDeformation(0.0F))
                .texOffs(24, 26).addBox(2.8F, -2.4F, -4.8F, 1.4F, 2.2F, 1.8F, new CubeDeformation(0.0F))
                // Central Chin Speech Diaphragm & Exhaust Port
                .texOffs(48, 64).addBox(-1.2F, -1.2F, -5.6F, 2.4F, 2.0F, 0.8F, new CubeDeformation(0.0F))
                // Silicone Retention Headstraps (Temples & Back of Head)
                .texOffs(0, 0).addBox(-4.4F, -4.8F, -4.2F, 8.8F, 1.2F, 8.8F, new CubeDeformation(0.0F))
                .texOffs(0, 0).addBox(-4.4F, -2.5F, -3.8F, 8.8F, 1.0F, 8.2F, new CubeDeformation(0.0F)),
                PartPose.ZERO
        );

        return LayerDefinition.create(mesh, 128, 128);
    }

    @Override
    public void setupAnim(@NotNull T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
    }

    @Override
    public void renderToBuffer(@NotNull PoseStack poseStack, @NotNull VertexConsumer buffer, int packedLight, int packedOverlay, float red, float green, float blue, float alpha) {
        body.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
        rightLeg.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
    }

    public void renderDesign(@NotNull PoseStack poseStack, @NotNull VertexConsumer buffer, int packedLight, int packedOverlay,
                             float red, float green, float blue, float alpha, FlightDesign design) {
        switch (design) {
            case MAGE_UNIT -> {
                body.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                rightLeg.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case BACK_JETPACK -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                backJetpack.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case TACTICAL_WINGS -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                tacticalWings.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case HEAVY_ROCKET -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                heavyTanks.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case TWIN_DRIVE_EXO -> {
                twinDriveTorso.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                rightLeg.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                leftLeg.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case SIEGE_ARTILLERY -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                siegeFrame.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case THRUST_BOOTS -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                thrustBootsRight.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                thrustBootsLeft.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case HYDRO_SKIMMER -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                hydroSkimmerTorso.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                hydroSkimmerRight.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                hydroSkimmerLeft.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case TACTICAL_SCUBA -> {
                harness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                tacticalScuba.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case URBAN_EXO_LEGS -> {
                urbanExoHarness.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                urbanExoRightArm.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                urbanExoLeftArm.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                urbanExoRight.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
                urbanExoLeft.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
            case DIVING_MASK -> {
                divingMask.render(poseStack, buffer, packedLight, packedOverlay, red, green, blue, alpha);
            }
        }
    }
}
