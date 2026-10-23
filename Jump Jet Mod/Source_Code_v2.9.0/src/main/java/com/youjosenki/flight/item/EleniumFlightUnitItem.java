package com.youjosenki.flight.item;

import com.google.common.collect.HashMultimap;
import com.google.common.collect.Multimap;
import com.youjosenki.flight.Config;
import com.youjosenki.flight.client.model.FlightUnitModel;
import com.youjosenki.flight.compat.curios.CuriosCompat;
import com.youjosenki.flight.energy.EnergyCapabilityProvider;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.DyeableLeatherItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.common.capabilities.ICapabilityProvider;
import net.minecraftforge.energy.IEnergyStorage;
import org.jetbrains.annotations.NotNull;
import com.youjosenki.flight.sound.FlightSoundProfile;
import com.youjosenki.flight.client.vfx.FlightVFXHelper;
import com.youjosenki.flight.telemetry.FlightStateManager;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import org.jetbrains.annotations.Nullable;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class EleniumFlightUnitItem extends Item implements ICurioItem, DyeableLeatherItem {
    public static final String MOD_VERSION_STRING = "2.8.8";
    public static final Set<UUID> FLYING_PLAYERS = Collections.newSetFromMap(new ConcurrentHashMap<>());
    private static final UUID VALKYRIE_SPEED_MODIFIER_UUID = UUID.fromString("6a345812-70b5-4b4e-9ff1-523e16f73188");

    public enum HudGeneration {
        VINTAGE_ANALOG("Vintage Mechanical (แผงหน้าปัดทองเหลืองอนาล็อก)"),
        MILITARY_STANDARD("Military Avionics (ค็อกพิทเครื่องบินรบเรดาร์เขียว)"),
        ADVANCED_DIGITAL("Advanced Holographic (หน้าจอโฮโลกราฟิกดิจิทัล)");

        private final String displayName;

        HudGeneration(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    private final int defaultColor;
    private final int maxEnergyCapacity;
    private final double sprintSpeedMultiplier;
    private final float baseFlightSpeed;
    private final FlightUnitModel.FlightDesign flightDesign;
    private final FlightSoundProfile soundProfile;
    private final int serviceCeiling;
    private final float boostMultiplier;
    private final float coolingRate;
    private final boolean waterproof;
    private final float rainSlowdown;
    private final HudGeneration hudGeneration;

    public EleniumFlightUnitItem(int maxEnergy, float baseSpeed, double sprintMult, int defaultColor,
                                 FlightUnitModel.FlightDesign design, FlightSoundProfile soundProfile,
                                 int serviceCeiling, float boostMultiplier, float coolingRate,
                                 boolean waterproof, float rainSlowdown, HudGeneration hudGeneration) {
        super(new Item.Properties()
                .stacksTo(1)
                .rarity(Rarity.EPIC)
                .fireResistant()
        );
        this.maxEnergyCapacity = maxEnergy;
        this.baseFlightSpeed = baseSpeed;
        this.sprintSpeedMultiplier = sprintMult;
        this.defaultColor = defaultColor;
        this.flightDesign = design;
        this.soundProfile = soundProfile != null ? soundProfile : deriveSoundProfile(design);
        this.serviceCeiling = serviceCeiling;
        this.boostMultiplier = boostMultiplier;
        this.coolingRate = coolingRate;
        this.waterproof = waterproof;
        this.rainSlowdown = rainSlowdown;
        this.hudGeneration = hudGeneration != null ? hudGeneration : deriveHudGeneration(design, soundProfile);
    }

    public EleniumFlightUnitItem(int maxEnergy, float baseSpeed, double sprintMult, int defaultColor,
                                 FlightUnitModel.FlightDesign design, FlightSoundProfile soundProfile,
                                 int serviceCeiling, float boostMultiplier, float coolingRate,
                                 boolean waterproof, float rainSlowdown) {
        this(maxEnergy, baseSpeed, sprintMult, defaultColor, design, soundProfile, serviceCeiling, boostMultiplier, coolingRate, waterproof, rainSlowdown, deriveHudGeneration(design, soundProfile));
    }

    public EleniumFlightUnitItem(int maxEnergy, float baseSpeed, double sprintMult, int defaultColor,
                                 FlightUnitModel.FlightDesign design, FlightSoundProfile soundProfile,
                                 int serviceCeiling, float boostMultiplier, float coolingRate) {
        this(maxEnergy, baseSpeed, sprintMult, defaultColor, design, soundProfile, serviceCeiling, boostMultiplier, coolingRate, false, 0.20F);
    }

    public EleniumFlightUnitItem(int maxEnergy, float baseSpeed, double sprintMult, int defaultColor,
                                 FlightUnitModel.FlightDesign design, FlightSoundProfile soundProfile) {
        this(maxEnergy, baseSpeed, sprintMult, defaultColor, design, soundProfile, 250, 1.8F, 1.0F);
    }

    public EleniumFlightUnitItem(int maxEnergy, float baseSpeed, double sprintMult, int defaultColor,
                                 FlightUnitModel.FlightDesign design) {
        this(maxEnergy, baseSpeed, sprintMult, defaultColor, design, deriveSoundProfile(design));
    }

    public EleniumFlightUnitItem(int maxEnergy, double speedMult, int defaultColor) {
        this(maxEnergy, 0.08F, speedMult, defaultColor, FlightUnitModel.FlightDesign.MAGE_UNIT, FlightSoundProfile.PROTOTYPE_MANA_CORE);
    }

    public static FlightSoundProfile deriveSoundProfile(FlightUnitModel.FlightDesign design) {
        if (design == null) return FlightSoundProfile.PROTOTYPE_MANA_CORE;
        return switch (design) {
            case HEAVY_ROCKET -> FlightSoundProfile.HEAVY_ROCKET_BOOSTER;
            case BACK_JETPACK -> FlightSoundProfile.MODERN_MILITARY_JET;
            case TACTICAL_WINGS -> FlightSoundProfile.AERODYNAMIC_STREAM;
            default -> FlightSoundProfile.VINTAGE_EARLY_MAGE;
        };
    }

    public static HudGeneration deriveHudGeneration(FlightUnitModel.FlightDesign design, FlightSoundProfile soundProfile) {
        if (soundProfile == FlightSoundProfile.STEALTH_RECON_WHISPER || design == FlightUnitModel.FlightDesign.TWIN_DRIVE_EXO) {
            return HudGeneration.ADVANCED_DIGITAL;
        }
        if (soundProfile == FlightSoundProfile.VINTAGE_EARLY_MAGE || soundProfile == FlightSoundProfile.HEAVY_ROCKET_BOOSTER) {
            return HudGeneration.VINTAGE_ANALOG;
        }
        return HudGeneration.MILITARY_STANDARD;
    }

    public HudGeneration getHudGeneration() {
        return hudGeneration;
    }

    public FlightSoundProfile getSoundProfile() {
        return soundProfile;
    }

    public int getServiceCeiling() {
        return serviceCeiling;
    }

    public float getBoostMultiplier() {
        return boostMultiplier;
    }

    public float getCoolingRate() {
        return coolingRate;
    }

    public int getMaxEnergyCapacity() {
        return maxEnergyCapacity;
    }

    public float getBaseFlightSpeed() {
        return baseFlightSpeed;
    }

    public double getSprintSpeedMultiplier() {
        return sprintSpeedMultiplier;
    }

    public FlightUnitModel.FlightDesign getFlightDesign() {
        return flightDesign;
    }

    public boolean isWaterproof() {
        return waterproof;
    }

    public float getRainSlowdown() {
        return rainSlowdown;
    }

    public float getEffectiveFlightSpeed(Player player, boolean isSprinting) {
        float speed = isSprinting ?
                (float) (this.baseFlightSpeed * this.sprintSpeedMultiplier) :
                this.baseFlightSpeed;

        if (this.rainSlowdown > 0.0F && player.level().isRainingAt(player.blockPosition())) {
            speed *= (1.0F - this.rainSlowdown);
        }

        return speed;
    }

    @Override
    public int getColor(ItemStack stack) {
        CompoundTag displayTag = stack.getTagElement(TAG_DISPLAY);
        if (displayTag != null && displayTag.contains(TAG_COLOR, CompoundTag.TAG_ANY_NUMERIC)) {
            return displayTag.getInt(TAG_COLOR);
        }
        return this.defaultColor;
    }

    @Override
    public @Nullable ICapabilityProvider initCapabilities(ItemStack stack, @Nullable CompoundTag nbt) {
        return new EnergyCapabilityProvider(stack);
    }

    @Override
    public boolean canRightClickEquip(ItemStack stack) {
        return true;
    }

    @Override
    public @NotNull InteractionResultHolder<ItemStack> use(@NotNull Level level, @NotNull Player player, @NotNull InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);

        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (chest.isEmpty()) {
            player.setItemSlot(EquipmentSlot.CHEST, stack.copy());
            stack.setCount(0);
            onEquipUnit(player, player.getItemBySlot(EquipmentSlot.CHEST));
            return InteractionResultHolder.sidedSuccess(ItemStack.EMPTY, level.isClientSide());
        }

        return super.use(level, player, hand);
    }

    @Override
    public void curioTick(SlotContext slotContext, ItemStack stack) {
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            handleFlight(player, stack);
        }
    }

    @Override
    public void onEquip(SlotContext slotContext, ItemStack prevStack, ItemStack stack) {
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            onEquipUnit(player, stack);
        }
    }

    @Override
    public void onUnequip(SlotContext slotContext, ItemStack newStack, ItemStack stack) {
        if (newStack.getItem() instanceof EleniumFlightUnitItem) {
            return;
        }
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            onUnequipUnit(player);
        }
    }

    @Override
    public Multimap<Attribute, AttributeModifier> getAttributeModifiers(SlotContext slotContext, UUID uuid, ItemStack stack) {
        Multimap<Attribute, AttributeModifier> modifiers = HashMultimap.create();
        if (this.flightDesign == FlightUnitModel.FlightDesign.THRUST_BOOTS) {
            modifiers.put(Attributes.MOVEMENT_SPEED,
                    new AttributeModifier(VALKYRIE_SPEED_MODIFIER_UUID,
                            "Valkyrie Kinetic Ground Boost", 0.035D, AttributeModifier.Operation.ADDITION));
        }
        return modifiers;
    }

    @Override
    public Multimap<Attribute, AttributeModifier> getDefaultAttributeModifiers(EquipmentSlot slot) {
        Multimap<Attribute, AttributeModifier> modifiers = HashMultimap.create();
        if (this.flightDesign == FlightUnitModel.FlightDesign.THRUST_BOOTS && (slot == EquipmentSlot.FEET || slot == EquipmentSlot.CHEST)) {
            modifiers.put(Attributes.MOVEMENT_SPEED,
                    new AttributeModifier(VALKYRIE_SPEED_MODIFIER_UUID,
                            "Valkyrie Kinetic Ground Boost", 0.035D, AttributeModifier.Operation.ADDITION));
        }
        return modifiers;
    }

    @Override
    public void inventoryTick(@NotNull ItemStack stack, @NotNull Level level, @NotNull Entity entity, int slotId, boolean isSelected) {
        if (entity instanceof Player player) {
            ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
            if (chest == stack) {
                handleFlight(player, stack);
            }
        }
    }

    public static boolean isItemEnergized(ItemStack stack) {
        if (stack.isEmpty() || !(stack.getItem() instanceof EleniumFlightUnitItem)) return false;
        CompoundTag tag = stack.getTag();
        int hoverCost = Config.COMMON.hoverEnergyCost.get();
        if (tag != null && tag.contains(com.youjosenki.flight.energy.ItemEnergyStorage.ENERGY_KEY)) {
            return tag.getInt(com.youjosenki.flight.energy.ItemEnergyStorage.ENERGY_KEY) > hoverCost;
        }
        return true;
    }

    public static boolean hasEnergizedFlightUnit(Player player) {
        if (player.isCreative() || player.isSpectator()) return true;

        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (isItemEnergized(chest)) return true;

        if (CuriosCompat.isCuriosLoaded()) {
            top.theillusivec4.curios.api.type.capability.ICuriosItemHandler handler =
                    CuriosApi.getCuriosInventory(player).resolve().orElse(null);
            if (handler != null) {
                if (handler.findFirstCurio(EleniumFlightUnitItem::isItemEnergized).isPresent()) {
                    return true;
                }
            }
        }

        return false;
    }

    public static ItemStack getEquippedFlightUnit(Player player) {
        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (chest.getItem() instanceof EleniumFlightUnitItem) {
            return chest;
        }

        if (CuriosCompat.isCuriosLoaded()) {
            top.theillusivec4.curios.api.type.capability.ICuriosItemHandler handler =
                    CuriosApi.getCuriosInventory(player).resolve().orElse(null);
            if (handler != null) {
                var res = handler.findFirstCurio(s -> s.getItem() instanceof EleniumFlightUnitItem);
                if (res.isPresent()) {
                    return res.get().stack();
                }
            }
        }
        return null;
    }

    public static boolean hasOtherFlightSource(Player player) {
        if (player.isCreative() || player.isSpectator()) return true;

        if (CuriosCompat.isCuriosLoaded()) {
            top.theillusivec4.curios.api.type.capability.ICuriosItemHandler handler =
                    CuriosApi.getCuriosInventory(player).resolve().orElse(null);
            if (handler != null) {
                var res = handler.findFirstCurio(stack -> {
                    if (stack.isEmpty() || stack.getItem() instanceof EleniumFlightUnitItem) return false;
                    net.minecraft.resources.ResourceLocation id = net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem());
                    return id != null && (id.getNamespace().equals("angelring") || id.getPath().contains("ring") || id.getPath().contains("flight"));
                });
                if (res.isPresent()) return true;
            }
        }
        return false;
    }

    public void onEquipUnit(Player player, ItemStack stack) {
        boolean isCreative = player.isCreative() || player.isSpectator();
        String unitName = stack.getHoverName().getString();
        if (isCreative || isItemEnergized(stack)) {
            player.getAbilities().mayfly = true;
            player.getAbilities().setFlyingSpeed(this.baseFlightSpeed);
            player.onUpdateAbilities();
            if (!player.level().isClientSide) {
                player.displayClientMessage(Component.translatable("message.youjosenki.activated", unitName), true);
            }
        } else {
            if (!player.level().isClientSide) {
                player.displayClientMessage(Component.translatable("message.youjosenki.no_energy", unitName), true);
            }
        }
    }

    public void onUnequipUnit(Player player) {
        FLYING_PLAYERS.remove(player.getUUID());
        FlightStateManager.clearPlayerData(player.getUUID());
        player.getAbilities().setFlyingSpeed(0.05F);
        if (!player.isCreative() && !player.isSpectator()) {
            if (!hasOtherFlightSource(player)) {
                player.getAbilities().flying = false;
                player.getAbilities().mayfly = false;
                player.onUpdateAbilities();
                if (!player.level().isClientSide) {
                    player.displayClientMessage(Component.translatable("message.youjosenki.deactivated"), true);
                }
            }
        }
    }

    public void handleFlight(Player player, ItemStack stack) {
        boolean isCreative = player.isCreative() || player.isSpectator();
        boolean canFly = isCreative || isItemEnergized(stack);

        if (canFly) {
            // Water Stall System: Non-waterproof units stall completely inside water
            boolean inWater = player.isInWater();
            if (inWater && !this.waterproof) {
                if (player.getAbilities().flying) {
                    player.getAbilities().flying = false;
                    player.onUpdateAbilities();
                    if (!player.level().isClientSide) {
                        player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                                SoundEvents.GENERIC_EXTINGUISH_FIRE, SoundSource.PLAYERS, 0.9F, 1.3F);
                        player.displayClientMessage(Component.translatable("message.youjosenki.water_stall", stack.getHoverName().getString()), true);
                    }
                }
                if (player.getAbilities().mayfly) {
                    player.getAbilities().mayfly = false;
                    player.onUpdateAbilities();
                }

                // Extinguishing steam & bubble particles when engine drowns
                if (player.level() instanceof ServerLevel serverLevel && player.tickCount % 4 == 0) {
                    serverLevel.sendParticles(ParticleTypes.BUBBLE, player.getX(), player.getY() + 0.4, player.getZ(), 4, 0.25, 0.2, 0.25, 0.05);
                    serverLevel.sendParticles(ParticleTypes.SMOKE, player.getX(), player.getY() + 0.8, player.getZ(), 2, 0.1, 0.1, 0.1, 0.02);
                }
                FLYING_PLAYERS.remove(player.getUUID());
                return;
            }

            // Calculate effective flight speed considering weather / rain
            float effectiveSpeed = this.getEffectiveFlightSpeed(player, player.isSprinting());

            // Guarantee mayfly is enabled cleanly without overriding flying state
            if (!player.getAbilities().mayfly) {
                player.getAbilities().mayfly = true;
                player.getAbilities().setFlyingSpeed(effectiveSpeed);
                player.onUpdateAbilities();
            } else if (player.getAbilities().getFlyingSpeed() != effectiveSpeed) {
                player.getAbilities().setFlyingSpeed(effectiveSpeed);
            }

            // Always prevent fall damage while energized
            if (Config.COMMON.preventFallDamage.get()) {
                player.fallDistance = 0.0F;
            }

            boolean isFlying = player.getAbilities().flying;
            boolean isSprinting = player.isSprinting();

            // Telemetry, Overheat, and Service Ceiling ticking on server
            if (player instanceof ServerPlayer serverPlayer) {
                FlightStateManager.tickServer(serverPlayer, this, stack, isFlying, isSprinting);
            }

            if (isFlying) {
                // Takeoff sound event (transition to flight)
                if (!FLYING_PLAYERS.contains(player.getUUID())) {
                    FLYING_PLAYERS.add(player.getUUID());
                    if (!player.level().isClientSide) {
                        this.soundProfile.playTakeoff(player);
                    }
                }

                boolean isMoving = player.getDeltaMovement().horizontalDistanceSqr() > 0.0005;

                // Drain energy only in Survival / Adventure mode on server
                // Dynamic energy scaling: Consecutive/higher boost steps consume significantly more energy!
                if (!isCreative && !player.level().isClientSide) {
                    int requiredEnergy = Config.COMMON.hoverEnergyCost.get();
                    if (isSprinting && isMoving) {
                        FlightStateManager.PlayerFlightData flightData = FlightStateManager.getPlayerData(player.getUUID());
                        float boostDrainFactor = (flightData != null && flightData.boostStep > 1) ? (1.0F + (flightData.boostStep - 1) * 0.75F) : 1.0F;
                        requiredEnergy = (int) (Config.COMMON.sprintEnergyCost.get() * boostDrainFactor);
                    } else if (isMoving) {
                        requiredEnergy = Config.COMMON.flightEnergyCost.get();
                    }

                    IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                    if (energy != null) {
                        energy.extractEnergy(requiredEnergy, false);
                    }
                }

                // 3D world spatial sound loops & continuous anime contrail streamer
                if (!player.level().isClientSide) {
                    if (isSprinting && isMoving) {
                        if (player.tickCount % 16 == 0) {
                            this.soundProfile.playSprint(player);
                        }
                    } else if (isMoving) {
                        if (player.tickCount % 30 == 0) {
                            this.soundProfile.playCruising(player);
                        }
                    } else {
                        if (player.tickCount % 40 == 0) {
                            this.soundProfile.playCruising(player);
                        }
                    }

                    spawnFlightParticles(player, isSprinting, isMoving);
                    FlightVFXHelper.handleGroundDownwash((ServerLevel) player.level(), player, isSprinting, isMoving, this.soundProfile);
                }
            } else {
                FLYING_PLAYERS.remove(player.getUUID());

                // Valkyrie Hover-Thrust Boots: Kinetic Ground Rocket Skating
                if (player.onGround() && isSprinting && this.flightDesign == FlightUnitModel.FlightDesign.THRUST_BOOTS) {
                    if (player.getDeltaMovement().horizontalDistanceSqr() > 0.002) {
                        Vec3 m = player.getDeltaMovement();
                        player.setDeltaMovement(m.x * 1.035, m.y, m.z * 1.035);

                        if (!isCreative && !player.level().isClientSide && player.tickCount % 4 == 0) {
                            IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                            if (energy != null) {
                                energy.extractEnergy(5, false);
                            }
                        }

                        if (player.level() instanceof ServerLevel serverLevel && player.tickCount % 2 == 0) {
                            double yawRad = Math.toRadians(player.getYRot());
                            double cosYaw = Math.cos(yawRad);
                            double sinYaw = Math.sin(yawRad);
                            double lx = player.getX() + cosYaw * 0.18;
                            double lz = player.getZ() + sinYaw * 0.18;
                            double rx = player.getX() - cosYaw * 0.18;
                            double rz = player.getZ() - sinYaw * 0.18;
                            double y = player.getY() + 0.05;
                            serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, lx, y, lz, 1, 0.02, 0.02, 0.02, 0.04);
                            serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rx, y, rz, 1, 0.02, 0.02, 0.02, 0.04);
                            serverLevel.sendParticles(ParticleTypes.SMOKE, lx, y, lz, 1, 0.01, 0.01, 0.01, 0.01);
                            serverLevel.sendParticles(ParticleTypes.SMOKE, rx, y, rz, 1, 0.01, 0.01, 0.01, 0.01);
                        }
                    }
                }
            }
        } else {
            FLYING_PLAYERS.remove(player.getUUID());
            // Energy depleted in survival
            if (player.getAbilities().flying || player.getAbilities().mayfly) {
                stopFlight(player);
                if (!player.level().isClientSide) {
                    player.displayClientMessage(Component.translatable("message.youjosenki.depleted", stack.getHoverName().getString()), true);
                }
            }
        }
    }

    private void spawnFlightParticles(Player player, boolean isSprinting, boolean isMoving) {
        if (!(player.level() instanceof ServerLevel serverLevel)) {
            return;
        }

        boolean emitMana = Config.COMMON.spawnManaParticles.get();
        boolean emitSmoke = Config.COMMON.spawnSmokeParticles.get();
        if (!emitMana && !emitSmoke) {
            return;
        }

        Vec3 currentPos = player.position();
        Vec3 prevPos = new Vec3(player.xo, player.yo, player.zo);
        Vec3 delta = currentPos.subtract(prevPos);
        double dist = delta.length();

        if (dist > 5.0) {
            // Player teleported or dimension hopped, prevent drawing long line across map
            prevPos = currentPos;
            dist = 0.0;
        }

        double yawRad = Math.toRadians(player.getYRot());
        double cosYaw = Math.cos(yawRad);
        double sinYaw = Math.sin(yawRad);
        int density = Math.min(3, Math.max(1, Config.COMMON.smokeDensity.get()));
        boolean isStealth = (this.soundProfile == FlightSoundProfile.STEALTH_RECON_WHISPER);

        // CASE 1: Stationary hover (dist < 0.05) - soft idle exhaust, no contrail line
        if (dist < 0.05 || !isMoving) {
            if (player.tickCount % 2 == 0 && emitSmoke) {
                spawnHoverSmoke(serverLevel, currentPos, cosYaw, sinYaw);
            }
            return;
        }

        // CASE 2: Cruising / Sprinting flight - continuous interpolated anime contrail streamer
        // Spaced every ~0.26 blocks so particles overlap into an unbroken solid ribbon
        int steps = Math.max(1, (int) Math.ceil(dist / 0.26));
        steps = Math.min(steps, 10); // Safeguard against extreme lag spikes

        for (int i = 0; i < steps; i++) {
            double t = (double) i / steps;
            Vec3 samplePos = prevPos.lerp(currentPos, t);
            boolean isLeadTip = (i == steps - 1); // Point closest to player

            spawnStreamerPoint(serverLevel, samplePos, cosYaw, sinYaw, isSprinting, isStealth, isLeadTip, emitMana, emitSmoke, density);
        }
    }

    private void spawnHoverSmoke(ServerLevel serverLevel, Vec3 pos, double cosYaw, double sinYaw) {
        switch (this.flightDesign) {
            case MAGE_UNIT -> {
                double rightX = pos.x - cosYaw * 0.22;
                double rightZ = pos.z - sinYaw * 0.22;
                double rightY = pos.y + 0.08;
                serverLevel.sendParticles(ParticleTypes.SMOKE, rightX, rightY, rightZ, 1, 0.02, -0.01, 0.02, 0.005);
            }
            case BACK_JETPACK, HEAVY_ROCKET -> {
                double leftX = pos.x - cosYaw * 0.22 - sinYaw * -0.22;
                double leftZ = pos.z - sinYaw * 0.22 + cosYaw * -0.22;
                double rightX = pos.x - cosYaw * -0.22 - sinYaw * -0.22;
                double rightZ = pos.z - sinYaw * -0.22 + cosYaw * -0.22;
                double y = pos.y + 0.60;
                serverLevel.sendParticles(ParticleTypes.SMOKE, leftX, y, leftZ, 1, 0.01, -0.01, 0.01, 0.005);
                serverLevel.sendParticles(ParticleTypes.SMOKE, rightX, y, rightZ, 1, 0.01, -0.01, 0.01, 0.005);
            }
            case TACTICAL_WINGS -> {
                double leftX = pos.x - cosYaw * 0.65;
                double leftZ = pos.z - sinYaw * 0.65;
                double rightX = pos.x + cosYaw * 0.65;
                double rightZ = pos.z + sinYaw * 0.65;
                double y = pos.y + 0.70;
                serverLevel.sendParticles(ParticleTypes.SMOKE, leftX, y, leftZ, 1, 0.01, -0.01, 0.01, 0.005);
                serverLevel.sendParticles(ParticleTypes.SMOKE, rightX, y, rightZ, 1, 0.01, -0.01, 0.01, 0.005);
            }
            case TWIN_DRIVE_EXO -> {
                double leftX = pos.x + cosYaw * 0.22;
                double leftZ = pos.z + sinYaw * 0.22;
                double rightX = pos.x - cosYaw * 0.22;
                double rightZ = pos.z - sinYaw * 0.22;
                double y = pos.y + 0.08;
                serverLevel.sendParticles(ParticleTypes.SMOKE, leftX, y, leftZ, 1, 0.02, -0.01, 0.02, 0.005);
                serverLevel.sendParticles(ParticleTypes.SMOKE, rightX, y, rightZ, 1, 0.02, -0.01, 0.02, 0.005);
            }
            case SIEGE_ARTILLERY -> {
                double leftX = pos.x - cosYaw * 0.25 - sinYaw * -0.28;
                double leftZ = pos.z - sinYaw * 0.25 + cosYaw * -0.28;
                double rightX = pos.x - cosYaw * -0.25 - sinYaw * -0.28;
                double rightZ = pos.z - sinYaw * -0.25 + cosYaw * -0.28;
                double y = pos.y + 0.50;
                serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, leftX, y, leftZ, 1, 0.02, -0.01, 0.02, 0.01);
                serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, rightX, y, rightZ, 1, 0.02, -0.01, 0.02, 0.01);
            }
            case THRUST_BOOTS -> {
                double leftX = pos.x + cosYaw * 0.18;
                double leftZ = pos.z + sinYaw * 0.18;
                double rightX = pos.x - cosYaw * 0.18;
                double rightZ = pos.z - sinYaw * 0.18;
                double y = pos.y + 0.08;
                serverLevel.sendParticles(ParticleTypes.SMOKE, leftX, y, leftZ, 1, 0.01, -0.01, 0.01, 0.005);
                serverLevel.sendParticles(ParticleTypes.SMOKE, rightX, y, rightZ, 1, 0.01, -0.01, 0.01, 0.005);
            }
        }
    }

    private void spawnStreamerPoint(ServerLevel serverLevel, Vec3 samplePos, double cosYaw, double sinYaw,
                                    boolean isSprinting, boolean isStealth, boolean isLeadTip,
                                    boolean emitMana, boolean emitSmoke, int density) {
        // STEALTH MODEL: Shadow Recon Wings leaves only faint smoke every other step and NO thick contrail line
        if (isStealth) {
            if (emitSmoke && isLeadTip) {
                double leftX = samplePos.x - cosYaw * 0.50;
                double leftZ = samplePos.z - sinYaw * 0.50;
                double rightX = samplePos.x + cosYaw * 0.50;
                double rightZ = samplePos.z + sinYaw * 0.50;
                double y = samplePos.y + 0.70;
                serverLevel.sendParticles(ParticleTypes.SMOKE, leftX, y, leftZ, 1, 0.02, 0.01, 0.02, 0.005);
                serverLevel.sendParticles(ParticleTypes.SMOKE, rightX, y, rightZ, 1, 0.02, 0.01, 0.02, 0.005);
            }
            return;
        }

        switch (this.flightDesign) {
            case MAGE_UNIT -> {
                // Right leg flight apparatus + abdominal mana exhaust
                double rightX = samplePos.x - cosYaw * 0.22;
                double rightZ = samplePos.z - sinYaw * 0.22;
                double rightY = samplePos.y + 0.10;

                double ventX = samplePos.x - sinYaw * -0.15;
                double ventZ = samplePos.z + cosYaw * -0.15;
                double ventY = samplePos.y + 0.65;

                if (emitSmoke) {
                    // Contrail streamer that hangs in the air forming an unbroken anime line
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, rightY, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.SMOKE, ventX, ventY, ventZ, 1, 0.02, 0.02, 0.02, 0.002);
                    }
                }
                if (emitMana) {
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, rightX, rightY, rightZ, 1, 0.015, 0.015, 0.015, 0.01);
                        if (isLeadTip) {
                            serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rightX, rightY, rightZ, 1, 0.04, 0.04, 0.04, 0.02);
                        }
                    } else if (isLeadTip) {
                        serverLevel.sendParticles(ParticleTypes.GLOW, rightX, rightY, rightZ, 1, 0.02, 0.02, 0.02, 0.01);
                    }
                }
            }
            case BACK_JETPACK -> {
                double leftX = samplePos.x - cosYaw * 0.22 - sinYaw * -0.22;
                double leftZ = samplePos.z - sinYaw * 0.22 + cosYaw * -0.22;
                double rightX = samplePos.x - cosYaw * -0.22 - sinYaw * -0.22;
                double rightZ = samplePos.z - sinYaw * -0.22 + cosYaw * -0.22;
                double y = samplePos.y + 0.65;

                if (emitSmoke) {
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftX, y, leftZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, y, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                }
                if (emitMana && isSprinting) {
                    serverLevel.sendParticles(ParticleTypes.FLAME, leftX, y, leftZ, 1, 0.02, 0.02, 0.02, 0.01);
                    serverLevel.sendParticles(ParticleTypes.FLAME, rightX, y, rightZ, 1, 0.02, 0.02, 0.02, 0.01);
                }
            }
            case TACTICAL_WINGS -> {
                double wingSpan = 0.65;
                double leftWingX = samplePos.x - cosYaw * wingSpan - sinYaw * -0.15;
                double leftWingZ = samplePos.z - sinYaw * wingSpan + cosYaw * -0.15;
                double rightWingX = samplePos.x + cosYaw * wingSpan - sinYaw * -0.15;
                double rightWingZ = samplePos.z + sinYaw * wingSpan + cosYaw * -0.15;
                double wingY = samplePos.y + 0.70;

                if (emitSmoke) {
                    // Aerodynamic delta wingtip condensation trails
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftWingX, wingY, leftWingZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightWingX, wingY, rightWingZ, 1, 0.01, 0.01, 0.01, 0.0005);
                }
                if (emitMana && isSprinting && isLeadTip) {
                    serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, leftWingX, wingY, leftWingZ, 1, 0.03, 0.03, 0.03, 0.02);
                    serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rightWingX, wingY, rightWingZ, 1, 0.03, 0.03, 0.03, 0.02);
                }
            }
            case HEAVY_ROCKET -> {
                double leftX = samplePos.x - cosYaw * 0.24 - sinYaw * -0.26;
                double leftZ = samplePos.z - sinYaw * 0.24 + cosYaw * -0.26;
                double rightX = samplePos.x - cosYaw * -0.24 - sinYaw * -0.26;
                double rightZ = samplePos.z - sinYaw * -0.24 + cosYaw * -0.26;
                double thrusterY = samplePos.y + 0.55;

                if (emitSmoke) {
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftX, thrusterY, leftZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, thrusterY, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, leftX, thrusterY, leftZ, 1, 0.02, 0.02, 0.02, 0.01);
                        serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, rightX, thrusterY, rightZ, 1, 0.02, 0.02, 0.02, 0.01);
                    }
                }
                if (emitMana && isSprinting) {
                    serverLevel.sendParticles(ParticleTypes.FLAME, leftX, thrusterY, leftZ, 1, 0.02, 0.02, 0.02, 0.015);
                    serverLevel.sendParticles(ParticleTypes.FLAME, rightX, thrusterY, rightZ, 1, 0.02, 0.02, 0.02, 0.015);
                }
            }
            case TWIN_DRIVE_EXO -> {
                // Dual-leg anime contrail streamers + twin mana core exhaust
                double leftX = samplePos.x + cosYaw * 0.22;
                double leftZ = samplePos.z + sinYaw * 0.22;
                double rightX = samplePos.x - cosYaw * 0.22;
                double rightZ = samplePos.z - sinYaw * 0.22;
                double legY = samplePos.y + 0.10;

                double ventX = samplePos.x - sinYaw * -0.15;
                double ventZ = samplePos.z + cosYaw * -0.15;
                double ventY = samplePos.y + 0.65;

                if (emitSmoke) {
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftX, legY, leftZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, legY, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.SMOKE, ventX, ventY, ventZ, 2, 0.02, 0.02, 0.02, 0.002);
                    }
                }
                if (emitMana) {
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, leftX, legY, leftZ, 1, 0.015, 0.015, 0.015, 0.01);
                        serverLevel.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, rightX, legY, rightZ, 1, 0.015, 0.015, 0.015, 0.01);
                        if (isLeadTip) {
                            serverLevel.sendParticles(ParticleTypes.SCULK_CHARGE_POP, ventX, ventY, ventZ, 1, 0.03, 0.03, 0.03, 0.02);
                            serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rightX, legY, rightZ, 1, 0.04, 0.04, 0.04, 0.02);
                            serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, leftX, legY, leftZ, 1, 0.04, 0.04, 0.04, 0.02);
                        }
                    } else if (isLeadTip) {
                        serverLevel.sendParticles(ParticleTypes.GLOW, leftX, legY, leftZ, 1, 0.02, 0.02, 0.02, 0.01);
                        serverLevel.sendParticles(ParticleTypes.GLOW, rightX, legY, rightZ, 1, 0.02, 0.02, 0.02, 0.01);
                    }
                }
            }
            case SIEGE_ARTILLERY -> {
                // Quad heavy industrial rocket thruster exhaust
                double leftX = samplePos.x - cosYaw * 0.25 - sinYaw * -0.28;
                double leftZ = samplePos.z - sinYaw * 0.25 + cosYaw * -0.28;
                double rightX = samplePos.x - cosYaw * -0.25 - sinYaw * -0.28;
                double rightZ = samplePos.z - sinYaw * -0.25 + cosYaw * -0.28;
                double upperY = samplePos.y + 0.70;
                double lowerY = samplePos.y + 0.45;

                if (emitSmoke) {
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftX, upperY, leftZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, upperY, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftX, lowerY, leftZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, lowerY, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, leftX, lowerY, leftZ, 2, 0.03, 0.03, 0.03, 0.02);
                        serverLevel.sendParticles(ParticleTypes.LARGE_SMOKE, rightX, lowerY, rightZ, 2, 0.03, 0.03, 0.03, 0.02);
                    }
                }
                if (emitMana && isSprinting) {
                    serverLevel.sendParticles(ParticleTypes.FLAME, leftX, lowerY, leftZ, 2, 0.02, 0.02, 0.02, 0.02);
                    serverLevel.sendParticles(ParticleTypes.FLAME, rightX, lowerY, rightZ, 2, 0.02, 0.02, 0.02, 0.02);
                }
            }
            case THRUST_BOOTS -> {
                // Dual rocket boot exhaust from both feet
                double leftX = samplePos.x + cosYaw * 0.18;
                double leftZ = samplePos.z + sinYaw * 0.18;
                double rightX = samplePos.x - cosYaw * 0.18;
                double rightZ = samplePos.z - sinYaw * 0.18;
                double bootY = samplePos.y + 0.12;

                if (emitSmoke) {
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, leftX, bootY, leftZ, 1, 0.01, 0.01, 0.01, 0.0005);
                    serverLevel.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, rightX, bootY, rightZ, 1, 0.01, 0.01, 0.01, 0.0005);
                }
                if (emitMana) {
                    if (isSprinting) {
                        serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, leftX, bootY, leftZ, 1, 0.03, 0.03, 0.03, 0.02);
                        serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rightX, bootY, rightZ, 1, 0.03, 0.03, 0.03, 0.02);
                        serverLevel.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, leftX, bootY, leftZ, 1, 0.015, 0.015, 0.015, 0.01);
                        serverLevel.sendParticles(ParticleTypes.SOUL_FIRE_FLAME, rightX, bootY, rightZ, 1, 0.015, 0.015, 0.015, 0.01);
                    } else if (isLeadTip) {
                        serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, leftX, bootY, leftZ, 1, 0.02, 0.02, 0.02, 0.01);
                        serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, rightX, bootY, rightZ, 1, 0.02, 0.02, 0.02, 0.01);
                    }
                }
            }
        }
    }

    private void stopFlight(Player player) {
        FLYING_PLAYERS.remove(player.getUUID());
        player.getAbilities().setFlyingSpeed(0.05F);
        if (!player.isCreative() && !player.isSpectator()) {
            if (!hasOtherFlightSource(player)) {
                if (player.getAbilities().flying || player.getAbilities().mayfly) {
                    player.getAbilities().flying = false;
                    player.getAbilities().mayfly = false;
                    player.onUpdateAbilities();
                }
            }
        }
    }

    @Override
    public boolean isBarVisible(@NotNull ItemStack stack) {
        return true;
    }

    @Override
    public int getBarWidth(@NotNull ItemStack stack) {
        IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
        if (energy == null || energy.getMaxEnergyStored() == 0) return 0;
        return Math.round(13.0F * (float) energy.getEnergyStored() / (float) energy.getMaxEnergyStored());
    }

    @Override
    public int getBarColor(@NotNull ItemStack stack) {
        return 0x00E5FF;
    }

    @Override
    public void appendHoverText(@NotNull ItemStack stack, @Nullable Level level, @NotNull List<Component> tooltip, @NotNull TooltipFlag flag) {
        IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
        int stored = energy != null ? energy.getEnergyStored() : this.maxEnergyCapacity;
        int max = energy != null ? energy.getMaxEnergyStored() : this.maxEnergyCapacity;
        double percent = max > 0 ? ((double) stored / max) * 100.0 : 0.0;

        ChatFormatting color = stored > (max * 0.5) ? ChatFormatting.AQUA :
                (stored > (max * 0.2) ? ChatFormatting.YELLOW : ChatFormatting.RED);

        // Version Banner
        tooltip.add(Component.literal("§a✔ Youjo Senki v" + MOD_VERSION_STRING + " §7(Active)").withStyle(ChatFormatting.BOLD));

        // Design & Speed Stats
        tooltip.add(Component.literal("§7Style: §f" + this.flightDesign.getDisplayName()).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§7Avionics: §f" + this.hudGeneration.getDisplayName()).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§e✈ Cruising: §f" + String.format("%.0f%%", (this.baseFlightSpeed / 0.05F) * 100) +
                " §7| §6Sprint: §f" + String.format("%.1fx", this.sprintSpeedMultiplier)).withStyle(ChatFormatting.GOLD));

        tooltip.add(Component.translatable("tooltip.youjosenki.energy",
                String.format("%,d", stored),
                String.format("%,d", max),
                String.format("%.1f", percent)
        ).withStyle(color));

        // Waterproof & Weather Aviation Certification (International Military Standard)
        if (this.waterproof) {
            tooltip.add(Component.literal("§b✦ Water Rating: §fHermetically Sealed §7(Submersible)").withStyle(ChatFormatting.AQUA));
        } else {
            tooltip.add(Component.literal("§c✦ Water Rating: §fUnsealed Intake §7(Stalls in Water)").withStyle(ChatFormatting.RED));
        }

        if (this.rainSlowdown == 0.0F) {
            tooltip.add(Component.literal("§a✦ Weather Rating: §fAll-Weather Certified §7(0% Rain Drag)").withStyle(ChatFormatting.GREEN));
        } else {
            int pct = (int) (this.rainSlowdown * 100);
            tooltip.add(Component.literal("§e✦ Weather Rating: §fRain Drag: §c-" + pct + "% Spd §7(Wet Weather)").withStyle(ChatFormatting.YELLOW));
        }

        if (hasCustomColor(stack)) {
            tooltip.add(Component.translatable("tooltip.youjosenki.dyed").withStyle(ChatFormatting.DARK_GREEN));
        }

        // Display Faction Banner Insignia in Tooltip
        CompoundTag blockEntityTag = stack.getTagElement("BlockEntityTag");
        if (blockEntityTag != null && (blockEntityTag.contains("Base", net.minecraft.nbt.Tag.TAG_INT) || blockEntityTag.contains("Patterns", net.minecraft.nbt.Tag.TAG_LIST))) {
            tooltip.add(Component.translatable("tooltip.youjosenki.banner_attached").withStyle(ChatFormatting.GOLD));
            net.minecraft.world.item.BannerItem.appendHoverTextFromBannerBlockEntityTag(stack, tooltip);
        }

        if (Screen.hasShiftDown()) {
            tooltip.add(Component.translatable(this.getDescriptionId() + ".lore").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            tooltip.add(Component.empty());
            tooltip.add(Component.literal(this.waterproof ? "✦ Waterproofing: Hermetically sealed (functions in water)" : "✦ Waterproofing: Non-waterproof (thrusters stall/extinguish in water)").withStyle(this.waterproof ? ChatFormatting.AQUA : ChatFormatting.RED));
            tooltip.add(Component.literal(this.rainSlowdown == 0.0F ? "✦ Weather Rating: All-Weather Certified (0% rain drag)" : "✦ Weather Rating: Rain moisture drag (-" + (int)(this.rainSlowdown * 100) + "% speed in rain)").withStyle(this.rainSlowdown == 0.0F ? ChatFormatting.GREEN : ChatFormatting.YELLOW));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.slot").withStyle(ChatFormatting.DARK_AQUA));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.flight").withStyle(ChatFormatting.GREEN));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.sprint").withStyle(ChatFormatting.GOLD));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.smoke").withStyle(ChatFormatting.GRAY));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.dyeable").withStyle(ChatFormatting.LIGHT_PURPLE));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.falldamage").withStyle(ChatFormatting.BLUE));
        } else {
            tooltip.add(Component.translatable("tooltip.youjosenki.shift_hint").withStyle(ChatFormatting.DARK_GRAY));
        }
    }
}
