package com.youjosenki.flight.event;

import com.youjosenki.flight.Config;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = "youjosenki")
public class CommonEvents {

    @SubscribeEvent
    public static void onLivingFall(LivingFallEvent event) {
        if (!Config.COMMON.preventFallDamage.get()) {
            return;
        }

        if (event.getEntity() instanceof Player player) {
            if (EleniumFlightUnitItem.hasEnergizedFlightUnit(player)) {
                event.setCanceled(true);
            } else {
                ItemStack leg = EleniumFlightUnitItem.getEquippedLegUnit(player);
                if (leg != null && EleniumFlightUnitItem.isItemEnergized(leg)) {
                    event.setCanceled(true);
                }
            }
        }
    }

    @SubscribeEvent
    public static void onPlayerLoggedIn(PlayerEvent.PlayerLoggedInEvent event) {
        syncFlightAbilities(event.getEntity());
    }

    @SubscribeEvent
    public static void onPlayerLoggedOut(PlayerEvent.PlayerLoggedOutEvent event) {
        EleniumFlightUnitItem.FLYING_PLAYERS.remove(event.getEntity().getUUID());
    }

    @SubscribeEvent
    public static void onPlayerRespawn(PlayerEvent.PlayerRespawnEvent event) {
        EleniumFlightUnitItem.FLYING_PLAYERS.remove(event.getEntity().getUUID());
        syncFlightAbilities(event.getEntity());
    }

    @SubscribeEvent
    public static void onPlayerChangedDimension(PlayerEvent.PlayerChangedDimensionEvent event) {
        syncFlightAbilities(event.getEntity());
    }

    private static void syncFlightAbilities(Player player) {
        if (player.level().isClientSide() || player.isCreative() || player.isSpectator()) return;
        if (EleniumFlightUnitItem.hasEnergizedFlightUnit(player)) {
            player.getAbilities().mayfly = true;
            ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
            if (unit != null && unit.getItem() instanceof EleniumFlightUnitItem item) {
                player.getAbilities().setFlyingSpeed(item.getBaseFlightSpeed());
            }
            player.onUpdateAbilities();
        }
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) return;
        Player player = event.player;
        if (player.level().isClientSide() || player.isCreative() || player.isSpectator()) return;

        // Fallback safety check once every second
        if (player.tickCount % 20 != 0) return;

        boolean hasUnit = EleniumFlightUnitItem.hasEnergizedFlightUnit(player);
        if (hasUnit) {
            if (!player.getAbilities().mayfly) {
                player.getAbilities().mayfly = true;
                ItemStack unit = EleniumFlightUnitItem.getEquippedFlightUnit(player);
                if (unit != null && unit.getItem() instanceof EleniumFlightUnitItem item) {
                    player.getAbilities().setFlyingSpeed(item.getBaseFlightSpeed());
                }
                player.onUpdateAbilities();
            }
        } else {
            // Revoke flight ONLY if player is not flying with another mod (like Angel Ring)
            if (player.getAbilities().mayfly && !EleniumFlightUnitItem.hasOtherFlightSource(player)) {
                player.getAbilities().flying = false;
                player.getAbilities().mayfly = false;
                player.getAbilities().setFlyingSpeed(0.05F);
                player.onUpdateAbilities();
            }
        }
    }
}
