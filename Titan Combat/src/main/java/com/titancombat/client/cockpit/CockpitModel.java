package com.titancombat.client.cockpit;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;

public class CockpitModel extends GeoModel<CockpitPart> {
    private static final ResourceLocation CABIN_ANIMS = rl("animations/cockpit/titan_cabin.animation.json");

    private static ResourceLocation rl(String path) {
        return new ResourceLocation(TitanCombatMod.MODID, path);
    }

    /**
     * Resolves the first-person cockpit rig for a titan class.
     * Original titan chassis have their own dedicated 1st-person arm rigs.
     * Modular Titan Frames fallback to the versatile Trooper industrial mechanical arm rig.
     */
    public static TitanClass getCockpitRig(TitanClass titanClass) {
        if (titanClass == null) return TitanClass.TROOPER;
        return switch (titanClass) {
            case MONARCH, ION, LEGION, SCORCH, RONIN, NORTHSTAR, TONE, TROOPER, SCOUT, SHADE, BULWARK, EXO_FRAME -> titanClass;
            default -> TitanClass.TROOPER;
        };
    }

    @Override
    public ResourceLocation getModelResource(CockpitPart part) {
        return switch (part.getKind()) {
            case ARMS -> rl("geo/cockpit/" + getCockpitRig(part.getTitanClass()).getId() + "_titan_1st.geo.json");
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
        TitanClass rig = getCockpitRig(part.getTitanClass());
        String id = rig.getId();
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

        // Trooper chassis has tools and custom weapons under the weapon bone
        com.titancombat.entity.TitanWeapon wep = titan != null ? titan.getActiveWeapon() : null;
        for (com.titancombat.entity.TitanWeapon w : com.titancombat.entity.TitanWeapon.values()) {
            if (w.getModelBone() == null) continue;
            var bone = getAnimationProcessor().getBone(w.getModelBone());
            if (bone != null) bone.setHidden(!hasWep || wep != w);
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
            return rl("animations/cockpit/" + getCockpitRig(part.getTitanClass()).getId() + "_titan_1st.animation.json");
        }
        return CABIN_ANIMS;
    }
}
