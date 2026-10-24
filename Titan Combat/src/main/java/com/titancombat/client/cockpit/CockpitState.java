package com.titancombat.client.cockpit;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.BaseTitanEntity;
import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Tracks the titan the local player is piloting, for the first-person cockpit animations. */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID, value = Dist.CLIENT)
public final class CockpitState {
    private static final int MELEE_VIEW_TICKS = 17;

    private static BaseTitanEntity titan;
    private static boolean wasMeleeing;
    private static int meleeSerial;
    private static int meleeTicks;

    private static int ejectLaunchTicks;
    private static double ejectX, ejectY, ejectZ;

    private CockpitState() {}

    /** Launch the local player once they are out of the seat (within a few ticks). */
    public static void queueEjectLaunch(double x, double y, double z) {
        ejectX = x;
        ejectY = y;
        ejectZ = z;
        ejectLaunchTicks = 10;
    }

    public static BaseTitanEntity titan() {
        return titan;
    }

    public static int meleeSerial() {
        return meleeSerial;
    }

    public static boolean meleeActive() {
        return meleeTicks > 0;
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        titan = mc.player != null && mc.player.getVehicle() instanceof BaseTitanEntity t ? t : null;
        if (meleeTicks > 0) meleeTicks--;
        if (ejectLaunchTicks > 0 && mc.player != null) {
            ejectLaunchTicks--;
            if (!mc.player.isPassenger()) {
                mc.player.setDeltaMovement(ejectX, ejectY, ejectZ);
                mc.player.fallDistance = 0.0F;
                ejectLaunchTicks = 0;
            }
        }
        if (titan == null) {
            wasMeleeing = false;
            return;
        }
        boolean meleeing = titan.getEntityData().get(BaseTitanEntity.DATA_IS_MELEEING);
        if (meleeing && !wasMeleeing) {
            meleeSerial++;
            meleeTicks = MELEE_VIEW_TICKS;
        }
        wasMeleeing = meleeing;
    }
}
