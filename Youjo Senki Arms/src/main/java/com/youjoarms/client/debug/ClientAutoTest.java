package com.youjoarms.client.debug;

import com.tacz.guns.api.client.gameplay.IClientPlayerGunOperator;
import com.tacz.guns.api.item.attachment.AttachmentType;
import com.tacz.guns.api.item.builder.GunItemBuilder;
import com.youjoarms.capability.PlayerMageProvider;
import com.youjoarms.formula.FormulaType;
import net.minecraft.client.CameraType;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

/**
 * Dev-only scripted test: YOUJOARMS_AUTOTEST=guns ./gradlew runClient
 * Creates a fresh world, holds/aims/fires every gun, then charges and fires every formula, saving screenshots
 * to run/screenshots/autotest_*.png. Inert unless -Dyoujoarms.autotest is set.
 */
@Mod.EventBusSubscriber(modid = "youjoarms", value = Dist.CLIENT)
public final class ClientAutoTest {
    private static final Logger LOG = LoggerFactory.getLogger("youjoarms-autotest");
    private static final String NAME = System.getProperty("youjoarms.autotest", "");
    private static final String[] GUNS = {"kar98k", "gewehr98", "t_gewehr", "c96", "mp18", "luger_p08", "mosin", "lebel",
            "lee_enfield", "mg08_15", "mg08", "m1897", "kampfpistole", "m1911", "springfield", "thompson", "bar_m1918"};
    private static final int[] AMMO = {5, 5, 1, 10, 32, 8, 5, 8, 10, 100, 250, 5, 1, 7, 5, 20, 20};

    private record Step(int at, Consumer<Minecraft> action) {}

    private static Step[] steps;
    private static int start = -1, tick = -1;
    private static boolean openedCreate, created;

    private static Step[] build() {
        List<Step> s = new ArrayList<>();
        s.add(new Step(20, mc -> server(mc, p -> {
            p.setGameMode(GameType.CREATIVE);
            var level = p.serverLevel();
            level.setDayTime(6000L);
            level.setWeatherParameters(60000, 0, false, false);
            BlockPos base = p.blockPosition().atY(100);
            for (int dx = -12; dx <= 12; dx++)
                for (int dz = -40; dz <= 6; dz++) {
                    level.setBlockAndUpdate(base.offset(dx, -1, dz), Blocks.SMOOTH_STONE.defaultBlockState());
                    for (int y = 0; y < 12; y++) level.setBlockAndUpdate(base.offset(dx, y, dz), Blocks.AIR.defaultBlockState());
                }
            for (int dx = -3; dx <= 3; dx++)  // backstop wall downrange so impacts are visible
                for (int y = 0; y < 5; y++) level.setBlockAndUpdate(base.offset(dx, y, -30), Blocks.WHITE_CONCRETE.defaultBlockState());
            p.teleportTo(level, base.getX() + 0.5, base.getY(), base.getZ() + 0.5, 180f, 0f);
            var husk = EntityType.HUSK.create(level);
            if (husk != null) {
                husk.moveTo(base.getX() + 0.5, base.getY(), base.getZ() - 12.5, 0f, 0f);
                husk.setNoAi(true);
                level.addFreshEntity(husk);
            }
        })));
        s.add(new Step(30, mc -> {
            mc.options.pauseOnLostFocus = false;
            mc.options.hideGui = false;
            mc.options.bobView().set(false);
            if (mc.screen != null) mc.setScreen(null);
        }));
        if (NAME.equals("showcase")) {
            showcase(s);
            return s.toArray(Step[]::new);
        }
        int t = 60;
        // phase 1: every gun held, aimed and fired once
        for (int i = 0; i < GUNS.length; i++) {
            final String gun = GUNS[i];
            final int ammo = AMMO[i];
            s.add(new Step(t, mc -> hold(mc, gun, ammo)));
            s.add(new Step(t + 30, mc -> shot(mc, gun + "_1_idle")));
            s.add(new Step(t + 32, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(true)));
            s.add(new Step(t + 50, mc -> shot(mc, gun + "_2_aim")));
            s.add(new Step(t + 51, mc -> LOG.info("[autotest] {} shoot result {}", gun, IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot())));
            s.add(new Step(t + 53, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(false)));
            t += 70;
        }
        // attachments from TACZ's own pack (stand-ins for any add-on's, which join the same tags)
        String[][] fits = {{"kar98k", "SCOPE", "tacz:scope_standard_8x"}, {"mosin", "SCOPE", "tacz:scope_elcan_4x"},
                {"lee_enfield", "MUZZLE", "tacz:muzzle_silencer_ursus"}, {"mg08_15", "SCOPE", "tacz:sight_552"},
                {"c96", "MUZZLE", "tacz:muzzle_silencer_ptilopsis"},
                {"kar98k", "EXTENDED_MAG", "youjoarms:mana_cell_3"}, {"mg08", "EXTENDED_MAG", "youjoarms:mana_cell_5"}};
        for (String[] fit : fits) {
            s.add(new Step(t, mc -> {
                mc.player.getInventory().selected = 0;
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                server(mc, p -> {
                    var stack = GunItemBuilder.create().setId(new ResourceLocation("youjoarms", fit[0])).setAmmoCount(5).setAmmoInBarrel(true)
                            .putAttachment(AttachmentType.valueOf(fit[1]), new ResourceLocation(fit[2])).build();
                    p.getInventory().clearContent();
                    p.getInventory().setItem(0, stack);
                    p.setXRot(0f);
                    p.setYRot(180f);
                });
            }));
            s.add(new Step(t + 30, mc -> shot(mc, "att_" + fit[0] + "_1_hip")));
            s.add(new Step(t + 32, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(true)));
            s.add(new Step(t + 52, mc -> shot(mc, "att_" + fit[0] + "_2_aim")));
            s.add(new Step(t + 40, mc -> {
                var held = mc.player.getMainHandItem();
                var prof = com.youjoarms.mana.GunMana.of(held);
                LOG.info("[autotest] mana {} {} tier={} max={} regen={} cost x{}", fit[0], fit[2], com.youjoarms.mana.GunMana.cellTier(held),
                        prof == null ? -1 : prof.maxMana(), prof == null ? -1 : prof.regenPerSecond(), prof == null ? 0 : prof.costMultiplier());
                var flat = held.copy();
                com.youjoarms.mana.GunMana.setCharge(flat, 0);
                var fp = com.youjoarms.mana.GunMana.of(flat);
                LOG.info("[autotest] mana flat cell -> max={} (base), charge/shard tier{}={}", fp == null ? -1 : fp.maxMana(), com.youjoarms.mana.GunMana.cellTier(held), com.youjoarms.mana.GunMana.chargePerShard(com.youjoarms.mana.GunMana.cellTier(held)));
            }));
            s.add(new Step(t + 53, mc -> LOG.info("[autotest] att {} shoot result {}", fit[0], IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot())));
            s.add(new Step(t + 56, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(false)));
            t += 70;
        }
        // phase 2: every formula on the Kar98k; the charge is shown part-way so the circle stack is visible growing
        for (FormulaType f : FormulaType.values()) {
            if (f == FormulaType.NONE) continue;
            final String name = f.name().toLowerCase();
            s.add(new Step(t, mc -> {
                hold(mc, "kar98k", 5);
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                mc.player.setXRot(f == FormulaType.ULTIMATE ? 6f : 0f);  // look is client-authoritative
            }));
            s.add(new Step(t + 20, mc -> charge(mc, f, 0.5f)));
            s.add(new Step(t + 24, mc -> shot(mc, "f_" + name + "_1_half")));
            s.add(new Step(t + 25, mc -> charge(mc, f, 1f)));
            s.add(new Step(t + 35, mc -> shot(mc, "f_" + name + "_2_full")));
            s.add(new Step(t + 36, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)));
            s.add(new Step(t + 44, mc -> shot(mc, "f_" + name + "_3_third_person")));
            s.add(new Step(t + 45, mc -> {
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                LOG.info("[autotest] formula {} shoot result {}", name, IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot());
            }));
            s.add(new Step(t + 48, mc -> shot(mc, "f_" + name + "_4_release")));
            if (f == FormulaType.ULTIMATE) {
                s.add(new Step(t + 66, mc -> mc.player.setXRot(-28f)));  // look up at the sky circles
                s.add(new Step(t + 75, mc -> shot(mc, "f_" + name + "_5_sky")));
                s.add(new Step(t + 101, mc -> shot(mc, "f_" + name + "_6_pillar")));
                s.add(new Step(t + 108, mc -> shot(mc, "f_" + name + "_7_detonate")));
                s.add(new Step(t + 112, mc -> mc.player.setXRot(0f)));
            } else if (f == FormulaType.SHIELD) {
                s.add(new Step(t + 60, mc -> shot(mc, "f_" + name + "_5_after")));
                s.add(new Step(t + 62, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)));
                s.add(new Step(t + 72, mc -> shot(mc, "f_" + name + "_6_third_person_active")));
                s.add(new Step(t + 74, mc -> mc.options.setCameraType(CameraType.FIRST_PERSON)));
            } else {
                s.add(new Step(t + 70, mc -> shot(mc, "f_" + name + "_5_after")));
            }
            t += f == FormulaType.ULTIMATE ? 140 : 90;
        }
        s.add(new Step(t, mc -> {
            LOG.info("[autotest] done");
            mc.stop();
        }));
        return s.toArray(Step[]::new);
    }

    /** Gallery shots for the CurseForge page: HUD hidden, golden-hour light. YOUJOARMS_AUTOTEST=showcase */
    private static void showcase(List<Step> s) {
        s.add(new Step(40, mc -> {
            mc.getTutorial().setStep(net.minecraft.client.tutorial.TutorialSteps.NONE);  // no "Move with WASD" toast
            mc.getToasts().clear();
            server(mc, p -> p.serverLevel().setDayTime(11200L));
        }));
        int t = 60;
        // charged stacks: first person, then the stack seen from the front
        Object[][] stacks = {{FormulaType.EXPLOSIVE, "01_explosion"}, {FormulaType.ARTILLERY, "02_artillery"}, {FormulaType.ULTIMATE, "03_annihilation"}};
        for (Object[] st : stacks) {
            FormulaType f = (FormulaType) st[0];
            String name = (String) st[1];
            s.add(new Step(t, mc -> hold(mc, "kar98k", 5)));
            s.add(new Step(t + 20, mc -> charge(mc, f, 1f)));
            s.add(new Step(t + 32, mc -> shot(mc, "showcase_" + name + "_fp")));
            s.add(new Step(t + 34, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)));
            s.add(new Step(t + 46, mc -> shot(mc, "showcase_" + name + "_front")));
            s.add(new Step(t + 48, mc -> {
                mc.options.setCameraType(CameraType.FIRST_PERSON);
                charge(mc, f, 0f);
                server(mc, p -> p.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(c -> c.setCharging(false)));
            }));
            t += 70;
        }
        // Annihilation fired: sky circles, pillar, detonation
        s.add(new Step(t, mc -> {
            hold(mc, "kar98k", 5);
            mc.player.setXRot(6f);
        }));
        s.add(new Step(t + 20, mc -> charge(mc, FormulaType.ULTIMATE, 1f)));
        s.add(new Step(t + 30, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot()));
        s.add(new Step(t + 44, mc -> mc.player.setXRot(-24f)));
        s.add(new Step(t + 60, mc -> shot(mc, "showcase_04_sky_circles")));
        s.add(new Step(t + 86, mc -> shot(mc, "showcase_05_pillar")));
        s.add(new Step(t + 92, mc -> shot(mc, "showcase_06_detonation")));
        t += 130;
        // Area Suppression from behind, then Defensive Shell from the front, then a Barrage release
        s.add(new Step(t, mc -> {
            hold(mc, "kar98k", 5);
            mc.player.setXRot(10f);
        }));
        s.add(new Step(t + 20, mc -> charge(mc, FormulaType.AREA, 1f)));
        s.add(new Step(t + 30, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot()));
        s.add(new Step(t + 32, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_BACK)));
        s.add(new Step(t + 48, mc -> shot(mc, "showcase_08_area")));
        t += 70;
        s.add(new Step(t, mc -> hold(mc, "gewehr98", 5)));
        s.add(new Step(t + 20, mc -> charge(mc, FormulaType.SHIELD, 1f)));
        s.add(new Step(t + 30, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot()));
        s.add(new Step(t + 34, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)));
        s.add(new Step(t + 50, mc -> shot(mc, "showcase_07_shield")));
        t += 70;
        s.add(new Step(t, mc -> hold(mc, "mp18", 32)));
        s.add(new Step(t + 20, mc -> charge(mc, FormulaType.BARRAGE, 1f)));
        s.add(new Step(t + 30, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).shoot()));
        s.add(new Step(t + 33, mc -> shot(mc, "showcase_09_barrage")));
        t += 60;
        // guns: scoped Kar98k, MG 08 hip, MG 08/15 from the front, Mosin irons, Luger
        s.add(new Step(t, mc -> {
            hold(mc, "kar98k", 5);
            server(mc, p -> p.getInventory().setItem(0, GunItemBuilder.create().setId(new ResourceLocation("youjoarms", "kar98k"))
                    .setAmmoCount(5).setAmmoInBarrel(true).putAttachment(AttachmentType.SCOPE, new ResourceLocation("tacz", "scope_standard_8x")).build()));
        }));
        s.add(new Step(t + 30, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(true)));
        s.add(new Step(t + 50, mc -> shot(mc, "showcase_10_scope")));
        s.add(new Step(t + 52, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(false)));
        t += 70;
        String[][] guns = {{"mg08", "250", "fp", "11_mg08"}, {"mg08_15", "100", "front", "12_mg08_15"},
                {"mosin", "5", "aim", "13_mosin"}, {"luger_p08", "8", "fp", "14_luger"}, {"lee_enfield", "10", "front", "15_enfield"}};
        for (String[] g : guns) {
            s.add(new Step(t, mc -> hold(mc, g[0], Integer.parseInt(g[1]))));
            if (g[2].equals("front")) s.add(new Step(t + 30, mc -> mc.options.setCameraType(CameraType.THIRD_PERSON_FRONT)));
            if (g[2].equals("aim")) s.add(new Step(t + 30, mc -> IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(true)));
            s.add(new Step(t + 50, mc -> shot(mc, "showcase_" + g[3])));
            s.add(new Step(t + 52, mc -> {
                IClientPlayerGunOperator.fromLocalPlayer(mc.player).aim(false);
                mc.options.setCameraType(CameraType.FIRST_PERSON);
            }));
            t += 70;
        }
        s.add(new Step(t, mc -> {
            LOG.info("[autotest] done");
            mc.stop();
        }));
    }

    private static void hold(Minecraft mc, String gun, int ammo) {
        mc.options.setCameraType(CameraType.FIRST_PERSON);
        mc.player.getInventory().selected = 0;  // the selected slot is client-authoritative
        server(mc, p -> {
            p.getInventory().clearContent();
            p.getInventory().setItem(0, GunItemBuilder.create().setId(new ResourceLocation("youjoarms", gun))
                    .setAmmoCount(ammo).setAmmoInBarrel(true).build());
            p.getInventory().selected = 0;
            p.setXRot(0f);
            p.setYRot(180f);
            p.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> cap.setMana(cap.getMaxMana()));
        });
    }

    /** Puts the formula at the given charge fraction on both sides (the server only fires it once full). */
    private static void charge(Minecraft mc, FormulaType formula, float progress) {
        Consumer<Player> set = pl -> pl.getCapability(PlayerMageProvider.MAGE_DATA).ifPresent(cap -> {
            cap.setSelectedFormula(formula);
            cap.setCharging(true);
            cap.setChargeTicks(Math.round(formula.getChargeTicks() * progress));
        });
        set.accept(mc.player);
        server(mc, set::accept);
    }

    @SubscribeEvent
    public static void onRenderOverlay(net.minecraftforge.client.event.RenderGuiOverlayEvent.Pre event) {
        if (NAME.equals("showcase")) event.setCanceled(true);
    }

    @SubscribeEvent
    public static void onClientTick(TickEvent.ClientTickEvent event) {
        if (NAME.isEmpty() || event.phase != TickEvent.Phase.END) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null || mc.getSingleplayerServer() == null || !mc.getSingleplayerServer().isReady()) {
            if (!openedCreate && mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen) {
                openedCreate = true;
                net.minecraft.client.gui.screens.worldselection.CreateWorldScreen.openFresh(mc, null);
            } else if (!created && mc.screen instanceof net.minecraft.client.gui.screens.worldselection.CreateWorldScreen cws) {
                created = true;
                try {
                    var m = cws.getClass().getDeclaredMethod("onCreate");
                    m.setAccessible(true);
                    m.invoke(cws);
                } catch (ReflectiveOperationException e) {
                    LOG.error("[autotest] could not create world", e);
                }
            }
            return;
        }
        if (steps == null) steps = build();
        // steps follow the integrated server clock so a slow server cannot make them fire early
        int serverTick = mc.getSingleplayerServer().getTickCount();
        if (start < 0) start = serverTick;
        int previous = tick;
        tick = serverTick - start;
        for (Step st : steps) {
            if (st.at() > previous && st.at() <= tick) st.action().accept(mc);
        }
    }

    private static void server(Minecraft mc, Consumer<ServerPlayer> action) {
        var server = mc.getSingleplayerServer();
        var uuid = mc.player.getUUID();
        server.execute(() -> {
            ServerPlayer p = server.getPlayerList().getPlayer(uuid);
            if (p != null) action.accept(p);
        });
    }

    private static void shot(Minecraft mc, String name) {
        Screenshot.grab(mc.gameDirectory, "autotest_" + name + ".png", mc.getMainRenderTarget(), msg -> {});
        LOG.info("[autotest] screenshot autotest_{}.png", name);
    }
}
