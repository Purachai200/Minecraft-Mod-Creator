package com.youjosenki.flight.client.debug;

import com.youjosenki.flight.YoujoSenkiMod;
import com.youjosenki.flight.energy.ItemEnergyStorage;
import com.youjosenki.flight.item.EleniumFlightUnitItem;
import com.youjosenki.flight.item.ModItems;
import com.youjosenki.flight.network.FlightBoostC2SPacket;
import com.youjosenki.flight.network.ModNetworking;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import top.theillusivec4.curios.api.CuriosApi;

import java.util.List;
import java.util.function.Consumer;

/**
 * Dev-only scripted rig showcase. Inactive unless the JVM runs with -Dyoujosenki.autotest=<name>
 * (build.gradle sets it from JUMPJET_AUTOTEST for runClient). For one rig per design it equips the rig
 * in a Curios slot, cycles deploy / idle / takeoff / hover / sprint / boost / landing, and saves
 * run/screenshots/autotest_<name>_<rig>_<T|W><n>_<state>.png (T = 4-angle turntable, W = world view).
 */
@Mod.EventBusSubscriber(modid = YoujoSenkiMod.MODID, value = Dist.CLIENT)
public final class ClientAutoTest {
    private static final String NAME = System.getProperty("youjosenki.autotest", "");
    private static final Logger LOGGER = com.mojang.logging.LogUtils.getLogger();
    private static final int CYCLE = 200;

    private record Rig(String id, RegistryObject<Item> item, RegistryObject<Item> extra) {}

    private static final List<Rig> ALL_RIGS = List.of(
            new Rig("mage", ModItems.ELENIUM_TYPE95_FLIGHT_UNIT, null),
            new Rig("jetpack", ModItems.TACTICAL_COMBAT_JETPACK, null),
            new Rig("wings", ModItems.REPUBLIC_TYPE101_FLIGHT_UNIT, null),
            new Rig("heavy", ModItems.FEDERATION_TYPE82_FLIGHT_UNIT, null),
            new Rig("twin", ModItems.ELENIUM_TYPE95_EXO, null),
            new Rig("siege", ModItems.TITAN_SIEGE_FRAME, null),
            new Rig("boots", ModItems.VALKYRIE_THRUST_BOOTS, null),
            new Rig("hydro", ModItems.AQUASURF_SKIMMER_UNIT, null),
            new Rig("scuba", ModItems.ABYSSAL_SCUBA_RIG, ModItems.ABYSSAL_DIVING_MASK),
            new Rig("exo", ModItems.URBAN_SCOUT_EXOLEGS, null));
    // Optional -Dyoujosenki.autotest.rigs=siege,jetpack to re-shoot a subset
    private static final List<Rig> RIGS = ALL_RIGS.stream()
            .filter(r -> System.getProperty("youjosenki.autotest.rigs", "").isEmpty()
                    || List.of(System.getProperty("youjosenki.autotest.rigs").split(",")).contains(r.id()))
            .toList();

    private record Step(int at, Consumer<Minecraft> action) {}

    // T_ = turntable (front/side/back/3-quarter at once, flat lighting), W_ = world view for VFX
    private static final Step[] CYCLE_STEPS = {
            new Step(0, mc -> { equipCurrent(mc); mc.setScreen(new Turntable()); }),
            new Step(10, mc -> shot(mc, "T1_deploy")),
            new Step(45, mc -> shot(mc, "T2_idle")),
            new Step(50, mc -> takeoff(mc)),
            new Step(55, mc -> shot(mc, "T3_takeoff")),
            new Step(80, mc -> shot(mc, "T4_hover")),
            new Step(82, mc -> sprinting = true),
            new Step(110, mc -> shot(mc, "T5_sprint")),
            new Step(112, mc -> ModNetworking.sendToServer(new FlightBoostC2SPacket())),
            new Step(115, mc -> shot(mc, "T6_boost")),
            new Step(118, mc -> { mc.setScreen(null); mc.options.setCameraType(CameraType.THIRD_PERSON_BACK); }),
            new Step(126, mc -> shot(mc, "W1_sprint")),
            new Step(128, mc -> { sprinting = false; land(mc); awaitLanding = 0; }),
    };

    private static int tick = -1;
    private static boolean sprinting;
    private static int awaitLanding = -1;

    private ClientAutoTest() {
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (NAME.isEmpty() || event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.level == null || mc.getSingleplayerServer() == null) return;
        tick++;
        if (tick == 20) {
            setup(mc);
            return;
        }
        int t = tick - 40;
        if (t < 0) return;
        if (sprinting) {
            mc.player.setSprinting(true);
            mc.player.setDeltaMovement(0, 0, -0.9);
        }
        // Touchdown is event-driven: world shot right after impact, then the landing pose on the turntable
        if (awaitLanding >= 0) {
            if (awaitLanding == 0 && mc.player.onGround()) awaitLanding = 1;
            else if (awaitLanding > 0 && ++awaitLanding == 3) shot(mc, "W2_touchdown");
            else if (awaitLanding == 4) mc.setScreen(new Turntable());
            else if (awaitLanding == 9) { shot(mc, "T7_landing"); awaitLanding = -1; }
        }
        int rig = t / CYCLE;
        if (rig >= RIGS.size()) {
            if (t == RIGS.size() * CYCLE) {
                LOGGER.info("[autotest] done");
                mc.stop();
            }
            return;
        }
        for (Step s : CYCLE_STEPS) {
            if (s.at() == t % CYCLE) s.action().accept(mc);
        }
    }

    /** Draws the pilot four times (front, right side, back, rear three-quarter) under inventory lighting. */
    private static final class Turntable extends net.minecraft.client.gui.screens.Screen {
        Turntable() {
            super(net.minecraft.network.chat.Component.literal("rig turntable"));
        }

        @Override
        public boolean isPauseScreen() {
            return false;
        }

        @Override
        public void render(net.minecraft.client.gui.GuiGraphics g, int mouseX, int mouseY, float partialTick) {
            g.fill(0, 0, width, height, 0xFF5A6270);
            var p = minecraft.player;
            int[] yaws = {0, 90, 180, 225};
            int scale = height / 3;
            for (int i = 0; i < yaws.length; i++) {
                float bo = p.yBodyRot, bO = p.yBodyRotO, yr = p.getYRot(), hr = p.yHeadRot, hO = p.yHeadRotO, xr = p.getXRot(), xO = p.xRotO;
                p.yBodyRot = p.yBodyRotO = 180.0F;
                p.setYRot(180.0F);
                p.yHeadRot = p.yHeadRotO = 180.0F;
                p.setXRot(0.0F);
                p.xRotO = 0.0F;
                var pose = new org.joml.Quaternionf().rotateZ((float) Math.PI).rotateY((float) Math.toRadians(yaws[i]));
                net.minecraft.client.gui.screens.inventory.InventoryScreen.renderEntityInInventory(
                        g, width * (2 * i + 1) / 8, height * 4 / 5, scale, pose, null, p);
                p.yBodyRot = bo; p.yBodyRotO = bO; p.setYRot(yr); p.yHeadRot = hr; p.yHeadRotO = hO; p.setXRot(xr); p.xRotO = xO;
            }
        }
    }

    private static Rig current() {
        return RIGS.get(Math.min(RIGS.size() - 1, Math.max(0, (tick - 40) / CYCLE)));
    }

    private static void setup(Minecraft mc) {
        mc.options.hideGui = true;
        mc.options.pauseOnLostFocus = false;
        server(mc, p -> {
            p.serverLevel().getGameRules().getRule(net.minecraft.world.level.GameRules.RULE_DAYLIGHT).set(false, p.getServer());
            p.setGameMode(GameType.CREATIVE);
            p.serverLevel().setDayTime(6000L);
            p.serverLevel().setWeatherParameters(6000, 0, false, false);
            p.getInventory().clearContent();
        });
    }

    private static void equipCurrent(Minecraft mc) {
        Rig rig = current();
        server(mc, p -> {
            // fresh spot each rig so earlier particles and pushed items are out of frame
            p.teleportTo(p.serverLevel(), 0.5, -60.0, 0.5 + (tick / CYCLE) * 40.0, 180.0F, 12.0F);
            p.getAbilities().flying = false;
            p.onUpdateAbilities();
            CuriosApi.getCuriosInventory(p).ifPresent(inv -> {
                inv.getStacksHandler("body").ifPresent(h -> h.getStacks().setStackInSlot(0, ItemStack.EMPTY));
                inv.getStacksHandler("belt").ifPresent(h -> h.getStacks().setStackInSlot(0, ItemStack.EMPTY));
                ItemStack main = charged(rig.item().get());
                boolean legs = ((EleniumFlightUnitItem) main.getItem()).getCategory() == EleniumFlightUnitItem.EquipmentCategory.LEGS_AUX;
                inv.getStacksHandler(legs ? "belt" : "body").ifPresent(h -> h.getStacks().setStackInSlot(0, main));
                if (rig.extra() != null) {
                    inv.getStacksHandler("belt").ifPresent(h -> h.getStacks().setStackInSlot(0, charged(rig.extra().get())));
                }
            });
        });
        LOGGER.info("[autotest] rig {}", rig.id());
    }

    private static ItemStack charged(Item item) {
        ItemStack stack = new ItemStack(item);
        stack.getOrCreateTag().putInt(ItemEnergyStorage.ENERGY_KEY, ((EleniumFlightUnitItem) item).getMaxEnergyCapacity());
        return stack;
    }

    private static void takeoff(Minecraft mc) {
        mc.player.getAbilities().flying = true;
        mc.player.onUpdateAbilities();
        mc.player.setDeltaMovement(0, 0.9, 0);
    }

    private static void land(Minecraft mc) {
        mc.player.getAbilities().flying = false;
        mc.player.onUpdateAbilities();
    }

    private static void server(Minecraft mc, Consumer<ServerPlayer> action) {
        var server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer p = server.getPlayerList().getPlayer(uuid);
            if (p != null) action.accept(p);
        });
    }

    private static void shot(Minecraft mc, String state) {
        String name = "autotest_" + NAME + "_" + current().id() + "_" + state + ".png";
        Screenshot.grab(mc.gameDirectory, name, mc.getMainRenderTarget(), msg -> {});
        LOGGER.info("[autotest] {} flying={} ground={} y={} particles={}", name, mc.player.getAbilities().flying, mc.player.onGround(),
                String.format("%.1f", mc.player.getY()), mc.particleEngine.countParticles());
        server(mc, p -> LOGGER.info("[autotest]   server flying={} tracked={} unit={} vel={}", p.getAbilities().flying,
                EleniumFlightUnitItem.FLYING_PLAYERS.contains(p.getUUID()), EleniumFlightUnitItem.getEquippedFlightUnit(p),
                p.getDeltaMovement()));
    }
}
