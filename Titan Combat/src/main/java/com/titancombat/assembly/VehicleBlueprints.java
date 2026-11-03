package com.titancombat.assembly;

import com.titancombat.item.ModItems;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.List;
import java.util.function.Supplier;

/**
 * What the Vehicle Assembly Bay builds and what each vehicle costs. Components (chassis frame, actuator,
 * cockpit, reactor, weapon mount) are crafted at a normal crafting table, so the bay is the last step of the chain.
 */
public final class VehicleBlueprints {
    public record Part(Supplier<Item> item, int count) {}

    public record Blueprint(Supplier<Item> result, String category, List<Part> parts) {}

    private static Part p(Supplier<Item> item, int count) {
        return new Part(item, count);
    }

    private static final Supplier<Item> CHASSIS = () -> ModItems.CHASSIS_FRAME.get();
    private static final Supplier<Item> ACTUATOR = () -> ModItems.HYDRAULIC_ACTUATOR.get();
    private static final Supplier<Item> COCKPIT = () -> ModItems.COCKPIT_MODULE.get();
    private static final Supplier<Item> REACTOR = () -> ModItems.FUSION_REACTOR.get();
    private static final Supplier<Item> MOUNT = () -> ModItems.WEAPON_MOUNT.get();
    private static final Supplier<Item> IRON_BLOCK = () -> Items.IRON_BLOCK;
    private static final Supplier<Item> GLASS = () -> Items.GLASS_PANE;
    private static final Supplier<Item> PLANKS = () -> Items.OAK_PLANKS;
    private static final Supplier<Item> WOOL = () -> Items.WHITE_WOOL;
    private static final Supplier<Item> REDSTONE = () -> Items.REDSTONE_BLOCK;

    public static final List<Blueprint> ALL = List.of(
            new Blueprint(() -> ModItems.TACTICAL_TRUCK.get(), "GROUND", List.of(p(CHASSIS, 1), p(COCKPIT, 1), p(MOUNT, 1), p(IRON_BLOCK, 3))),
            new Blueprint(() -> ModItems.ARMORED_APC.get(), "GROUND", List.of(p(CHASSIS, 2), p(COCKPIT, 1), p(ACTUATOR, 2), p(MOUNT, 1), p(IRON_BLOCK, 6))),
            new Blueprint(() -> ModItems.HAULER_TRUCK.get(), "GROUND", List.of(p(CHASSIS, 2), p(COCKPIT, 1), p(ACTUATOR, 1), p(IRON_BLOCK, 3))),
            new Blueprint(() -> ModItems.MOBILE_SUIT_TRAILER.get(), "GROUND", List.of(p(CHASSIS, 3), p(COCKPIT, 1), p(ACTUATOR, 3), p(IRON_BLOCK, 6))),
            new Blueprint(() -> ModItems.REPAIR_TRUCK.get(), "GROUND", List.of(p(CHASSIS, 2), p(COCKPIT, 1), p(ACTUATOR, 3), p(REACTOR, 1), p(REDSTONE, 4), p(IRON_BLOCK, 4))),
            new Blueprint(() -> ModItems.CHINOOK_TRANSPORTER.get(), "AIR", List.of(p(CHASSIS, 2), p(COCKPIT, 1), p(REACTOR, 2), p(ACTUATOR, 2), p(GLASS, 8), p(IRON_BLOCK, 6))),
            new Blueprint(() -> ModItems.V22_OSPREY.get(), "AIR", List.of(p(CHASSIS, 2), p(COCKPIT, 1), p(REACTOR, 2), p(ACTUATOR, 4), p(GLASS, 8), p(IRON_BLOCK, 6))),
            new Blueprint(() -> ModItems.C130_HERCULES.get(), "AIR", List.of(p(CHASSIS, 4), p(COCKPIT, 1), p(REACTOR, 4), p(ACTUATOR, 4), p(GLASS, 12), p(IRON_BLOCK, 12))),
            new Blueprint(() -> ModItems.SKYCRANE_DRONE.get(), "AIR", List.of(p(CHASSIS, 1), p(REACTOR, 2), p(ACTUATOR, 2), p(IRON_BLOCK, 4))),
            new Blueprint(() -> ModItems.LCAC_HOVERCRAFT.get(), "SEA", List.of(p(CHASSIS, 2), p(COCKPIT, 1), p(REACTOR, 2), p(WOOL, 16), p(IRON_BLOCK, 6))),
            new Blueprint(() -> ModItems.CARGO_BARGE.get(), "SEA", List.of(p(CHASSIS, 1), p(COCKPIT, 1), p(PLANKS, 32), p(IRON_BLOCK, 4))),
            new Blueprint(() -> ModItems.OCEAN_CARRIER.get(), "SEA", List.of(p(CHASSIS, 8), p(COCKPIT, 2), p(REACTOR, 6), p(ACTUATOR, 6), p(MOUNT, 3), p(IRON_BLOCK, 48)))
    );

    private VehicleBlueprints() {}

    public static int countHeld(Player player, Item item) {
        int n = 0;
        for (ItemStack s : player.getInventory().items) {
            if (s.is(item)) n += s.getCount();
        }
        return n;
    }

    public static boolean canAfford(Player player, Blueprint bp) {
        if (player.getAbilities().instabuild) return true;
        for (Part part : bp.parts()) {
            if (countHeld(player, part.item().get()) < part.count()) return false;
        }
        return true;
    }

    /** Takes the parts out of the inventory; call only after canAfford. */
    public static void consume(Player player, Blueprint bp) {
        if (player.getAbilities().instabuild) return;
        for (Part part : bp.parts()) {
            int left = part.count();
            for (ItemStack s : player.getInventory().items) {
                if (left == 0) break;
                if (s.is(part.item().get())) {
                    int take = Math.min(left, s.getCount());
                    s.shrink(take);
                    left -= take;
                }
            }
        }
    }
}
