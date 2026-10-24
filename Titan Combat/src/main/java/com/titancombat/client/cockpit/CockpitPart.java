package com.titancombat.client.cockpit;

import com.titancombat.entity.BaseTitanEntity;
import com.titancombat.entity.TitanClass;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.Animation;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;
import software.bernie.geckolib.util.GeckoLibUtil;
import software.bernie.geckolib.util.RenderUtils;

/**
 * One piece of the first-person cockpit (the titan's own arms + weapon, or the cabin shell).
 * Its animations follow the piloted titan's live state through {@link CockpitState}.
 */
public class CockpitPart implements GeoAnimatable {
    public enum Kind { ARMS, CABIN_BASE, CABIN_FRAME }

    private final Kind kind;
    private final TitanClass titanClass;
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private AnimationController<CockpitPart> actionController;
    private int lastMeleeSerial = -1;

    public CockpitPart(Kind kind, TitanClass titanClass) {
        this.kind = kind;
        this.titanClass = titanClass;
    }

    public Kind getKind() {
        return kind;
    }

    public TitanClass getTitanClass() {
        return titanClass;
    }

    private String clip(String name) {
        return "animation." + titanClass.getId() + "_titan." + name;
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        AnimationController<CockpitPart> sway = new AnimationController<>(this, "sway", 6, this::swayPredicate);
        sway.setAnimationSpeedHandler(p -> {
            BaseTitanEntity titan = CockpitState.titan();
            return titan != null ? titan.getLocomotionPlayback() : 1.0D;
        });
        controllers.add(sway);

        if (kind == Kind.ARMS) {
            this.actionController = new AnimationController<>(this, "action", 3, this::actionPredicate);
            controllers.add(this.actionController);
        }
    }

    // GeckoLib won't restart a stopped controller handed the same clip again, so every clip change
    // (including leaving "stopped") forces a reset.
    private final java.util.Map<String, String> currentClips = new java.util.HashMap<>();

    private PlayState play(AnimationState<CockpitPart> event, String key, RawAnimation animation) {
        if (!key.equals(this.currentClips.put(event.getController().getName(), key))) {
            event.getController().forceAnimationReset();
        }
        return event.setAndContinue(animation);
    }

    private PlayState stop(AnimationState<CockpitPart> event) {
        this.currentClips.remove(event.getController().getName());
        return PlayState.STOP;
    }

    private PlayState swayPredicate(AnimationState<CockpitPart> event) {
        BaseTitanEntity titan = CockpitState.titan();
        if (titan == null) return stop(event);
        return switch (titan.getGait()) {
            // The addon sways the arms with move.1st when sprinting, and bobs cabin + arms when walking.
            // (The addon's move.1st sprint sway spins the whole rig up to 180 degrees; use the gentle bob instead.)
            case RUN -> play(event, "run", RawAnimation.begin().thenLoop(kind == Kind.ARMS ? "animation.cabin_walk" : "animation.cabin_run"));
            case WALK -> play(event, "walk", RawAnimation.begin().thenLoop("animation.cabin_walk"));
            default -> stop(event);
        };
    }

    private PlayState actionPredicate(AnimationState<CockpitPart> event) {
        BaseTitanEntity titan = CockpitState.titan();
        if (titan == null) return stop(event);

        int serial = CockpitState.meleeSerial();
        if (serial != this.lastMeleeSerial && CockpitState.meleeActive()) {
            this.lastMeleeSerial = serial;
            this.currentClips.remove("action"); // restart the swing even if it's the same clip
        }
        if (CockpitState.meleeActive()) {
            return play(event, "melee" + serial, RawAnimation.begin().then(meleeClip(serial, titan), Animation.LoopType.PLAY_ONCE));
        }

        if (titan.isReloading()) {
            return play(event, "reload", RawAnimation.begin().then(clip("reload.1st"), Animation.LoopType.PLAY_ONCE));
        }

        if (titan.isFiringWeapon()) {
            if (titanClass == TitanClass.LEGION) {
                return play(event, "fire", RawAnimation.begin().thenPlay(clip("fire_pre.1st")).thenLoop(clip("fire.1st")));
            }
            if (titanClass == TitanClass.NORTHSTAR || titanClass == TitanClass.SCORCH) {
                return play(event, "fire", RawAnimation.begin().then(clip("fire.1st"), Animation.LoopType.PLAY_ONCE));
            }
            return play(event, "fire", RawAnimation.begin().thenLoop(clip("fire.1st")));
        }
        return stop(event);
    }

    private String meleeClip(int serial, BaseTitanEntity titan) {
        if (titanClass == TitanClass.RONIN) {
            int combo = 1 + Math.floorMod(serial, 3);
            return clip((titan.isOverdriveActive() ? "melee_core_" : "melee_") + combo + ".1st");
        }
        return clip("melee.1st");
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return cache;
    }

    @Override
    public double getTick(Object object) {
        return RenderUtils.getCurrentTick();
    }
}
