package com.titancombat.entity;

import com.titancombat.TitanCombatMod;
import com.titancombat.entity.transport.BaseTransportVehicleEntity;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Protects seated pilots inside enclosed cabins:
 * 1. Titans: The pilot sits sealed inside the titan core. Bullets and external hits are absorbed by titan plating.
 * 2. Transport Vehicles (Trucks, Drones, Barges): Seated pilots are inside the vehicle's cabin AABB.
 *    Suffocation in walls, cabin clipping, drowning, and fall damage are negated, with attack damage redirected to the hull.
 */
@Mod.EventBusSubscriber(modid = TitanCombatMod.MODID)
public final class PilotProtectionEvents {
    private PilotProtectionEvents() {}

    @SubscribeEvent
    public static void onPilotAttacked(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof Player pilot)) return;

        Entity vehicle = pilot.getVehicle();
        if (vehicle == null) return;

        DamageSource source = event.getSource();
        if (source.is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return; // /kill, void

        // 1. Titan Pilot Protection
        if (vehicle instanceof BaseTitanEntity titan) {
            event.setCanceled(true);
            if (pilot.level().isClientSide) return;

            // Cockpit-environment damage (head poking into blocks, water, own falls) is simply ignored.
            boolean environmental = source.is(DamageTypes.IN_WALL) || source.is(DamageTypes.DROWN)
                    || source.is(DamageTypeTags.IS_FALL) || source.getEntity() == pilot;
            if (!environmental && titan.isAlive()) {
                titan.hurt(source, event.getAmount());
            }
            return;
        }

        // 2. Transport Vehicle Driver & Passenger Protection (Truck Cab, Drone Cockpit, Barge Helm)
        if (vehicle instanceof BaseTransportVehicleEntity transport) {
            event.setCanceled(true);
            if (pilot.level().isClientSide) return;

            // Strictly negate in-wall suffocation, cabin water clipping, and vehicle fall damage
            boolean environmental = source.is(DamageTypes.IN_WALL) || source.is(DamageTypes.DROWN)
                    || source.is(DamageTypeTags.IS_FALL) || source.getEntity() == pilot;
            if (!environmental && transport.isAlive()) {
                transport.hurt(source, event.getAmount());
            }
        }
    }
}
