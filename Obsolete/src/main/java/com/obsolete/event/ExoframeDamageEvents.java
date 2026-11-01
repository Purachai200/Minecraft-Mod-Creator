package com.obsolete.event;

import com.obsolete.entity.ExoframeEntity;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(bus = Mod.EventBusSubscriber.Bus.FORGE)
public class ExoframeDamageEvents {

    /**
     * Intercepts incoming damage targeting the riding player (pilot protection).
     * Redirects projectile hits (TaCZ, SBW, arrows) and kinetic impacts to the Exoframe chassis.
     */
    @SubscribeEvent
    public static void onPilotAttacked(LivingAttackEvent event) {
        if (event.getEntity() instanceof Player player) {
            if (player.getVehicle() instanceof ExoframeEntity exoframe && exoframe.isAlive()) {
                DamageSource source = event.getSource();

                // Check if incoming damage is from any projectile (TaCZ, SBW, vanilla) or general hostile attack
                boolean isProjectile = source.getDirectEntity() instanceof Projectile
                        || source.is(net.minecraft.tags.DamageTypeTags.IS_PROJECTILE)
                        || source.getMsgId().contains("bullet")
                        || source.getMsgId().contains("tacz")
                        || source.getMsgId().contains("gun");

                if (isProjectile || !source.is(net.minecraft.tags.DamageTypeTags.BYPASSES_INVULNERABILITY)) {
                    // Cancel damage on the pilot player
                    event.setCanceled(true);

                    // Redirect damage to the Exoframe (which applies armor mitigation and degradation)
                    exoframe.hurt(source, event.getAmount());

                    // Play metallic deflection sound
                    player.level().playSound(null, player.blockPosition(),
                            SoundEvents.NETHERITE_BLOCK_HIT, SoundSource.PLAYERS, 1.2F, 1.2F);
                }
            }
        }
    }

    /**
     * Completely suppresses fall damage on the pilot player while riding or transitioning out of an Exoframe.
     */
    @SubscribeEvent
    public static void onPilotFall(net.minecraftforge.event.entity.living.LivingFallEvent event) {
        if (event.getEntity() instanceof Player player) {
            if (player.getVehicle() instanceof ExoframeEntity) {
                event.setCanceled(true);
                event.setDistance(0.0F);
                player.resetFallDistance();
                player.fallDistance = 0.0F;
            }
        }
    }
}
