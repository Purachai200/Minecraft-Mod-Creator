package com.youjosenki.flight.client.geo;

import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.core.animation.RawAnimation;
import software.bernie.geckolib.core.object.PlayState;

import java.util.HashMap;
import java.util.Map;

/**
 * Picks the keyframed sequence for a worn rig from the wearer's flight state:
 * deploy on first sight, takeoff/landing on air-ground transitions, boost on a velocity spike,
 * and hover/cruise/sprint/idle loops otherwise. Runs only while rendering (client side).
 */
public final class RigAnimationDriver {
    private enum Mode {
        GROUND("idle"), HOVER("hover"), CRUISE("cruise"), SPRINT("sprint");

        final RawAnimation loop, deploy, takeoff, boost;

        Mode(String loopName) {
            this.loop = RawAnimation.begin().thenLoop(loopName);
            this.deploy = RawAnimation.begin().thenPlay("deploy").thenLoop(loopName);
            this.takeoff = RawAnimation.begin().thenPlay("takeoff").thenLoop(loopName);
            this.boost = RawAnimation.begin().thenPlay("boost").thenLoop(loopName);
        }
    }

    private static final RawAnimation LANDING = RawAnimation.begin().thenPlay("landing").thenLoop("idle");

    private static final class Track {
        Mode mode;
        Mode playing;
        long lockUntil;
        long lastTick = -1;
        long lastSeen;
        int airTicks;
        double speed;
        double lastSpeed;
    }

    // shortcut: keyed by entity id + design, pruned by age; fine for the handful of rigs on screen
    private static final Map<Long, Track> TRACKS = new HashMap<>();

    private RigAnimationDriver() {
    }

    public static PlayState predicate(AnimationState<EleniumFlightUnitItem> state) {
        AnimationController<EleniumFlightUnitItem> controller = state.getController();
        Entity entity = state.getData(DataTickets.ENTITY);
        if (entity == null) {
            controller.setAnimation(Mode.GROUND.loop);
            return PlayState.CONTINUE;
        }
        Track t = track(entity, state.getAnimatable());
        long now = entity.level().getGameTime();
        boolean airborne = isAirborne(entity, t);
        Mode mode = !airborne ? Mode.GROUND
                : entity.isSprinting() ? Mode.SPRINT
                : t.speed > 0.08 ? Mode.CRUISE : Mode.HOVER;

        RawAnimation next = null;
        int lock = 0;
        if (t.mode == null || now - t.lastSeen > 20) {
            next = mode.deploy;
            lock = 24;
        } else if (t.mode == Mode.GROUND && airborne) {
            next = mode.takeoff;
            lock = 14;
        } else if (t.mode != Mode.GROUND && !airborne) {
            next = LANDING;
            mode = Mode.GROUND;
            lock = 12;
        } else if (airborne && now >= t.lockUntil && t.speed - t.lastSpeed > 0.2) {
            next = mode.boost;
            lock = 9;
        } else if (now >= t.lockUntil && t.playing != mode) {
            next = mode.loop;
        }
        if (next != null) {
            controller.forceAnimationReset();
            controller.setAnimation(next);
            t.lockUntil = now + lock;
            t.playing = mode;
        }
        t.mode = airborne ? mode : Mode.GROUND;
        t.lastSeen = now;
        return PlayState.CONTINUE;
    }

    /** Shared with the procedural mechanics so both agree on whether the wearer is flying. */
    public static boolean isAirborne(Entity entity, EleniumFlightUnitItem item) {
        return isAirborne(entity, track(entity, item));
    }

    private static boolean isAirborne(Entity entity, Track t) {
        // Abilities only sync to the owning client: other players count as airborne after a sustained jump
        if (entity instanceof Player p && p.isLocalPlayer()) {
            return p.getAbilities().flying && !p.onGround();
        }
        return t.airTicks > 6;
    }

    private static Track track(Entity entity, EleniumFlightUnitItem item) {
        long key = ((long) entity.getId() << 6) | item.getFlightDesign().ordinal();
        Track t = TRACKS.computeIfAbsent(key, k -> new Track());
        long now = entity.level().getGameTime();
        if (t.lastTick != now) {
            t.lastTick = now;
            t.lastSpeed = t.speed;
            double dx = entity.getX() - entity.xo, dy = entity.getY() - entity.yo, dz = entity.getZ() - entity.zo;
            t.speed = Math.sqrt(dx * dx + dy * dy + dz * dz);
            t.airTicks = entity.onGround() || entity.isInWater() ? 0 : t.airTicks + 1;
            if (TRACKS.size() > 128) {
                TRACKS.values().removeIf(o -> now - o.lastTick > 600);
            }
        }
        return t;
    }
}
