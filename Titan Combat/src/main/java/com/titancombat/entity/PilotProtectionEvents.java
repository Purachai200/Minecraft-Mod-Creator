package com.titancombat.entity;

import com.titancombat.TitanCombatMod;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * The pilot sits sealed inside the hull. Gun mods ray-trace bullets against hitboxes, and the
 * pilot's hitbox is inside the titan's, so shots would otherwise hit the pilot directly. Any hit
 * on a seated pilot is cancelled and redirected to the titan (where the armor plating applies).
 */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID)
public final class PilotProtectionEvents {
    private PilotProtectionEvents() {}

    @SubscribeEvent
    public static void onPilotAttacked(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof Player pilot) || !(pilot.getVehicle() instanceof BaseTitanEntity titan)) return;
        DamageSource source = event.getSource();
        if (source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return; // /kill, void

        event.setCanceled(true);
        if (pilot.level().isClientSide) return;

        // Cockpit-environment damage (head poking into blocks, water, own falls) is simply ignored.
        boolean environmental = source.is(DamageTypes.IN_WALL) || source.is(DamageTypes.DROWN)
                || source.is(DamageTypeTags.IS_FALL) || source.getEntity() == pilot;
        if (!environmental && titan.isAlive()) {
            titan.hurt(source, event.getAmount());
        }
    }
}
