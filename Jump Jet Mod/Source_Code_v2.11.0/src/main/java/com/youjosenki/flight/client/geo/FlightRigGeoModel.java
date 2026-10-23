package com.youjosenki.flight.client.geo;

import com.youjosenki.flight.YoujoSenkiMod;
import com.youjosenki.flight.client.telemetry.ClientFlightTelemetry;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;

import java.util.Locale;

/**
 * One model class for every rig: geometry/animation files are picked by FlightDesign.
 * Keyframes (animations/*.animation.json) move the frames; this class layers the continuous
 * mechanics on top: thrust vectoring, turbine spool, control surfaces, radiators, optics and pistons.
 */
public class FlightRigGeoModel extends GeoModel<EleniumFlightUnitItem> {
    public static final ResourceLocation TEXTURE =
            new ResourceLocation(YoujoSenkiMod.MODID, "textures/models/armor/elenium_flight_unit.png");
    private static final float DEG = (float) (Math.PI / 180.0);

    private static String key(EleniumFlightUnitItem item) {
        return item.getFlightDesign().name().toLowerCase(Locale.ROOT);
    }

    @Override
    public ResourceLocation getModelResource(EleniumFlightUnitItem item) {
        return new ResourceLocation(YoujoSenkiMod.MODID, "geo/" + key(item) + ".geo.json");
    }

    @Override
    public ResourceLocation getTextureResource(EleniumFlightUnitItem item) {
        return TEXTURE;
    }

    @Override
    public ResourceLocation getAnimationResource(EleniumFlightUnitItem item) {
        return new ResourceLocation(YoujoSenkiMod.MODID, "animations/" + key(item) + ".animation.json");
    }

    @Override
    public void setCustomAnimations(EleniumFlightUnitItem item, long instanceId, AnimationState<EleniumFlightUnitItem> state) {
        Entity entity = state.getData(DataTickets.ENTITY);
        if (!(entity instanceof LivingEntity living)) return;

        float partial = state.getPartialTick();
        float age = entity.tickCount + partial;
        boolean flying = RigAnimationDriver.isAirborne(entity, item);
        boolean sprinting = entity.isSprinting();
        double dx = entity.getX() - entity.xo;
        double dz = entity.getZ() - entity.zo;
        float speed = (float) Math.sqrt(dx * dx + dz * dz);
        float yawRate = Mth.wrapDegrees(living.yBodyRot - living.yBodyRotO);
        float throttle = flying ? (sprinting ? 1.0F : 0.55F) : 0.0F;
        float jitter = Mth.sin(age * 2.7F) * 0.02F * throttle;
        float heat = entity == Minecraft.getInstance().player ? ClientFlightTelemetry.heat
                : (flying ? (sprinting ? 60.0F : 25.0F) : 0.0F);

        // Exhaust swings from straight down (hover) toward rearward (forward thrust) as airspeed builds
        float vector = flying ? Mth.clamp(speed * 0.9F, 0.0F, 0.75F) + jitter : 0.0F;
        rotX("back_jetpack_nozzle_left", vector);
        rotX("back_jetpack_nozzle_right", vector);
        rotX("thrust_boots_right_nozzle", vector);
        rotX("thrust_boots_left_nozzle", vector);
        rotX("heavy_tanks_nozzle_left", vector * 0.7F);
        rotX("heavy_tanks_nozzle_right", vector * 0.7F);
        rotX("body_belly_nozzles", vector * 0.8F);
        rotX("right_leg_heel_nozzle", vector * 0.8F);
        rotX("left_leg_heel_nozzle", vector * 0.8F);
        rotX("twin_drive_torso_injectors", vector * 0.6F);
        // Siege pods face rearward: pitched down to hover, levelling out at speed
        rotX("siege_frame_thrusters", flying ? -0.9F + Mth.clamp(speed, 0.0F, 0.9F) + jitter : -0.25F);
        // Exo boost pack kicks rearward whenever the wearer is airborne (boost jump / dash)
        float kick = entity.onGround() ? 0.0F : (sprinting ? 0.7F : 0.35F) + jitter;
        rotX("urban_exo_harness_thruster_left", kick);
        rotX("urban_exo_harness_thruster_right", kick);

        // Turbine spool: idle tick-over on the ground, full spin at sprint
        float fanSpeed = flying ? (sprinting ? 1.7F : 0.9F) : 0.12F;
        rot("back_jetpack_fan_left", 0, age * fanSpeed, 0);
        rot("back_jetpack_fan_right", 0, -age * fanSpeed, 0);
        rot("body_mana_crystal", 0, 0, age * (flying ? (sprinting ? 0.25F : 0.1F) : 0.03F));

        // Rudders counter the turn; flaps drop for low-speed lift and act as ailerons in a bank
        float rudder = Mth.clamp(-yawRate * 0.06F, -0.5F, 0.5F);
        rot("tactical_wings_rudder", 0, rudder, 0);
        rot("hydro_skimmer_right_rudder", 0, rudder, 0);
        rot("hydro_skimmer_left_rudder", 0, rudder, 0);
        float flap = flying ? Mth.clamp(0.6F - speed * 0.8F, 0.0F, 0.6F) : 0.0F;
        rotX("tactical_wings_left_wing_flap", flap + rudder * 0.6F);
        rotX("tactical_wings_right_wing_flap", flap - rudder * 0.6F);
        getBone("tactical_wings_rudder_strobe").ifPresent(b -> b.setHidden(((int) age % 24) >= 2));

        // Radiators hinge open as the core heats up
        float flare = 0.12F + Mth.clamp(heat / 100.0F, 0.0F, 1.0F) * 0.65F;
        rot("twin_drive_torso_radiator_left", 0, 0, -flare);
        rot("twin_drive_torso_radiator_right", 0, 0, flare);

        // Siege optics track the wearer's head
        float headYaw = Mth.wrapDegrees(living.getYHeadRot() - living.yBodyRot);
        rot("siege_frame_sensors", Mth.clamp(entity.getXRot(), -40.0F, 40.0F) * DEG * 0.6F,
                Mth.clamp(headYaw, -50.0F, 50.0F) * DEG * 0.6F, 0);

        // Leg pistons stroke with each step; triceps rams extend as the arms swing
        float stride = living.walkAnimation.position(partial) * 0.6662F;
        float swing = living.walkAnimation.speed(partial);
        posY("urban_exo_right_piston", Math.abs(Mth.sin(stride)) * swing * 1.4F);
        posY("urban_exo_left_piston", Math.abs(Mth.cos(stride)) * swing * 1.4F);
        getBone("armorRightArm").ifPresent(arm -> posY("urban_exo_right_arm_rod", Math.min(1.2F, Math.abs(arm.getRotX()) * 0.9F)));
        getBone("armorLeftArm").ifPresent(arm -> posY("urban_exo_left_arm_rod", Math.min(1.2F, Math.abs(arm.getRotX()) * 0.9F)));
    }

    // Angles use the vanilla ModelPart convention; GeckoLib bones mirror X and Y (see RenderUtils.matchModelPartRot)
    private void rot(String bone, float x, float y, float z) {
        getBone(bone).ifPresent(b -> {
            b.setRotX(-x);
            b.setRotY(-y);
            b.setRotZ(z);
        });
    }

    private void rotX(String bone, float x) {
        getBone(bone).ifPresent(b -> b.setRotX(-x));
    }

    // Downward slide in model pixels (vanilla y-down) -> GeckoLib y-up
    private void posY(String bone, float down) {
        getBone(bone).ifPresent(b -> b.setPosY(-down));
    }
}
