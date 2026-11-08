package com.vehiclefleet.compat;

import net.minecraft.world.entity.Entity;
import net.minecraftforge.fml.ModList;

import java.lang.reflect.Method;

/** Optional Titan Combat / Obsolete support. Nothing here references their classes at compile time; everything is reflection and fails soft. */
public final class TitanCompat {
    private static boolean init;
    private static Method eligible;

    private TitanCompat() {}

    public static boolean present() {
        return ModList.get().isLoaded("titancombat") || ModList.get().isLoaded("obsolete");
    }

    /** True for a Titan, a mech or an Obsolete Exoframe that a vehicle may carry. */
    public static boolean isCargo(Entity e) {
        if (!present()) return false;
        if (!init) {
            init = true;
            try {
                eligible = Class.forName("com.titancombat.util.CrossModCargoHelper").getMethod("isCargoEligible", Entity.class);
            } catch (Throwable t) {
                eligible = null;
            }
        }
        if (eligible == null) return false;
        try {
            return (boolean) eligible.invoke(null, e);
        } catch (Throwable t) {
            return false;
        }
    }
}
