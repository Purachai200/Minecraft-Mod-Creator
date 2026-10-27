package com.titancombat.client.cockpit;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public class CockpitModel extends GeoModel<CockpitPart> {
    private static final ResourceLocation CABIN_ANIMS = rl("animations/cockpit/titan_cabin.animation.json");

    private static ResourceLocation rl(String path) {
        return new ResourceLocation(TitanCombatMod.MODID, path);
    }

    @Override
    public ResourceLocation getModelResource(CockpitPart part) {
        return switch (part.getKind()) {
            case ARMS -> rl("geo/cockpit/" + part.getTitanClass().getId() + "_titan_1st.geo.json");
            case CABIN_BASE -> rl("geo/cockpit/titan_cabin_base.geo.json");
            case CABIN_FRAME -> rl("geo/cockpit/titan_cabin_frame.geo.json");
        };
    }

    @Override
    public ResourceLocation getTextureResource(CockpitPart part) {
        return switch (part.getKind()) {
            case ARMS -> armsTexture(part);
            case CABIN_BASE -> rl("textures/entity/cockpit/titan_cabin_base.png");
            case CABIN_FRAME -> rl("textures/entity/cockpit/titan_cabin_frame.png");
        };
    }

    /** The arms wear the same paint job as the titan outside. */
    private static ResourceLocation armsTexture(CockpitPart part) {
        String id = part.getTitanClass().getId();
        BaseTitanEntity titan = CockpitState.titan();
        int camo = titan != null ? titan.getCamoIndex() : 0;
        String file = camo <= 0 ? id + "_titan.png" : id + "_titan_" + camo + ".png";
        return rl("textures/entity/titan/" + id + "/" + file);
    }

    /** Unarmed titans: hide the gun of the first-person rig. */
    @Override
    public void setCustomAnimations(CockpitPart part, long instanceId, software.bernie.geckolib.core.animation.AnimationState<CockpitPart> state) {
        super.setCustomAnimations(part, instanceId, state);
        if (part.getKind() != CockpitPart.Kind.ARMS) return;
        BaseTitanEntity titan = CockpitState.titan();
        boolean hasWep = titan != null && titan.hasWeapon();
        var gun = getAnimationProcessor().getBone("weapon");
        if (gun != null) gun.setHidden(!hasWep);

        // Trooper chassis has two tools (Mining Drill & Chainsaw) under the weapon bone
        var drill = getAnimationProcessor().getBone("drill");
        var saw = getAnimationProcessor().getBone("chainsaw");
        if (drill != null || saw != null) {
            boolean isSaw = titan != null && titan.getActiveWeapon() == com.titancombat.entity.TitanWeapon.CHAINSAW;
            boolean isDrill = titan != null && titan.getActiveWeapon() == com.titancombat.entity.TitanWeapon.MINING_DRILL;
            if (drill != null) drill.setHidden(!hasWep || !isDrill);
            if (saw != null) saw.setHidden(!hasWep || !isSaw);
        }

        // Hide shoulder laser bones on non-Ion rigs if present
        var laser = getAnimationProcessor().getBone("laser1");
        if (laser != null && (titan == null || titan.getActiveWeapon() != com.titancombat.entity.TitanWeapon.SPLITTER_RIFLE)) {
            laser.setHidden(true);
        }
    }

    @Override
    public ResourceLocation getAnimationResource(CockpitPart part) {
        if (part.getKind() == CockpitPart.Kind.ARMS) {
            return rl("animations/cockpit/" + part.getTitanClass().getId() + "_titan_1st.animation.json");
        }
        return CABIN_ANIMS;
    }
}
