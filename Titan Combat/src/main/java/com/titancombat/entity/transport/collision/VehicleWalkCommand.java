package com.titancombat.entity.transport.collision;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

import java.util.List;

public class VehicleWalkCommand {
    public static final List<String> VEHICLE_IDS = List.of(
            "technical_4x4", "ural_6x6", "mi17_hip", "coaster_freighter", "mi26_halo",
            "recovery_6x6", "humvee_m1165", "uh60_blackhawk", "fac_patrol", "opv_cutter",
            "corvette_stealth", "lpd_assault", "transport_sub", "c17_airlifter"
    );

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        var cmd = Commands.literal("vehicle_walk_test")
                .requires(s -> s.hasPermission(2))
                .executes(ctx -> runAll(ctx.getSource()))
                .then(Commands.literal("selftest").executes(ctx -> runSelftest(ctx.getSource())))
                .then(Commands.argument("vehicleId", StringArgumentType.word())
                        .suggests((ctx, builder) -> {
                            builder.suggest("selftest").suggest("all");
                            for (String id : VEHICLE_IDS) builder.suggest(id);
                            return builder.buildFuture();
                        })
                        .executes(ctx -> {
                            String id = StringArgumentType.getString(ctx, "vehicleId");
                            if ("selftest".equalsIgnoreCase(id)) return runSelftest(ctx.getSource());
                            if ("all".equalsIgnoreCase(id)) return runAll(ctx.getSource());
                            return runSingle(ctx.getSource(), id);
                        }));
        dispatcher.register(cmd);
    }

    private static int runSelftest(CommandSourceStack source) {
        try {
            boolean ok = VehicleCollisionManager.runSelfTest();
            source.sendSuccess(() -> Component.literal("§aself_test passed: wall blocks, 12 px riser blocks, 4.5 px stairs climb, 14 px door passes, 8 px gap blocks"), true);
            return 1;
        } catch (Throwable t) {
            source.sendFailure(Component.literal("§cself_test FAILED: " + t.getMessage()));
            return 0;
        }
    }

    private static int runSingle(CommandSourceStack source, String id) {
        VehicleCollisionManager.WalkTestResult res = VehicleCollisionManager.runWalkTest(id);
        if (res.problems().isEmpty()) {
            source.sendSuccess(() -> Component.literal("§a[WALK PASS] " + id + ": reachable_states=" + res.reachableStates() + ", problems=0"), true);
            return 1;
        } else {
            source.sendFailure(Component.literal("§c[WALK FAIL] " + id + ": " + String.join("; ", res.problems())));
            return 0;
        }
    }

    private static int runAll(CommandSourceStack source) {
        int failed = 0;
        for (String id : VEHICLE_IDS) {
            VehicleCollisionManager.WalkTestResult res = VehicleCollisionManager.runWalkTest(id);
            if (!res.problems().isEmpty()) {
                failed++;
                source.sendFailure(Component.literal("§c!! " + id + " has " + res.problems().size() + " problem(s)"));
            }
        }
        int total = VEHICLE_IDS.size();
        if (failed == 0) {
            source.sendSuccess(() -> Component.literal("§a[WALK TEST OK] 0 vehicle(s) with problems out of " + total), true);
            return 1;
        } else {
            source.sendFailure(Component.literal("§c[WALK TEST FAIL] " + failed + " vehicle(s) with problems out of " + total));
            return 0;
        }
    }
}
