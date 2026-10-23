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
import software.bernie.geckolib.animatable.GeoItem;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.core.animation.AnimationController;
import software.bernie.geckolib.util.GeckoLibUtil;
import top.theillusivec4.curios.api.CuriosApi;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

public class EleniumFlightUnitItem extends Item implements ICurioItem, DyeableLeatherItem, GeoItem {
    public static final String MOD_VERSION_STRING = "2.11.0";
    public static final Set<UUID> FLYING_PLAYERS = Collections.newSetFromMap(new ConcurrentHashMap<>());
    private static final UUID VALKYRIE_SPEED_MODIFIER_UUID = UUID.fromString("6a345812-70b5-4b4e-9ff1-523e16f73188");

    public enum EquipmentCategory {
        TORSO_MAIN("ชุดหลักส่วนอก/หลัง (Torso/Back Rig)"),
        LEGS_AUX("อุปกรณ์เสริมส่วนขา/เท้า (Legs/Feet Frame)"),
        HEAD_AUX("อุปกรณ์เสริมส่วนศีรษะ/หน้ากาก (Head/Mask)");

        private final String displayName;

        EquipmentCategory(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

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
    private final EquipmentCategory category;

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);

    // Per-suit combat tuning; neutral defaults, set via tuning() in ModItems
    private float energyDrainMult = 1.0F;
    private float heatGainMult = 1.0F;
    private int boostCooldownTicks = 12;
    private double armor = 0.0D;
    private double armorToughness = 0.0D;
    private double knockbackResist = 0.0D;

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
        if (design == FlightUnitModel.FlightDesign.DIVING_MASK) {
            this.category = EquipmentCategory.HEAD_AUX;
        } else if (design == FlightUnitModel.FlightDesign.THRUST_BOOTS || design == FlightUnitModel.FlightDesign.URBAN_EXO_LEGS) {
            this.category = EquipmentCategory.LEGS_AUX;
        } else {
            this.category = EquipmentCategory.TORSO_MAIN;
        }
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

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        // 3-tick blend between sequences; state machine lives in RigAnimationDriver (client render only)
        controllers.add(new AnimationController<>(this, "rig", 3, com.youjosenki.flight.client.geo.RigAnimationDriver::predicate));
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    public EleniumFlightUnitItem tuning(float drainMult, float heatMult, int boostCooldown,
                                        double armor, double toughness, double knockback) {
        this.energyDrainMult = drainMult;
        this.heatGainMult = heatMult;
        this.boostCooldownTicks = boostCooldown;
        this.armor = armor;
        this.armorToughness = toughness;
        this.knockbackResist = knockback;
        return this;
    }

    /** How hard the exhaust hits the ground: scales downwash, landing shockwave and camera shake. */
    public float getThrustClass() {
        float thrust = switch (flightDesign) {
            case SIEGE_ARTILLERY -> 1.8F;
            case HEAVY_ROCKET -> 1.6F;
            case TWIN_DRIVE_EXO -> 1.2F;
            case BACK_JETPACK, HYDRO_SKIMMER -> 1.0F;
            case MAGE_UNIT -> 0.9F;
            case TACTICAL_WINGS -> 0.75F;
            case THRUST_BOOTS, URBAN_EXO_LEGS -> 0.7F;
            default -> 0.5F;
        };
        return soundProfile == FlightSoundProfile.STEALTH_RECON_WHISPER ? thrust * 0.5F : thrust;
    }

    public float getEnergyDrainMult() {
        return energyDrainMult;
    }

    public float getHeatGainMult() {
        return heatGainMult;
    }

    public int getBoostCooldownTicks() {
        return boostCooldownTicks;
    }

    public EquipmentSlot getEquipSlot() {
        return switch (category) {
            case HEAD_AUX -> EquipmentSlot.HEAD;
            case LEGS_AUX -> EquipmentSlot.FEET;
            default -> EquipmentSlot.CHEST;
        };
    }

    private void addCombatModifiers(Multimap<Attribute, AttributeModifier> modifiers, UUID uuid) {
        if (armor > 0) modifiers.put(Attributes.ARMOR, new AttributeModifier(uuid, "Flight rig plating", armor, AttributeModifier.Operation.ADDITION));
        if (armorToughness > 0) modifiers.put(Attributes.ARMOR_TOUGHNESS, new AttributeModifier(uuid, "Flight rig plating", armorToughness, AttributeModifier.Operation.ADDITION));
        if (knockbackResist > 0) modifiers.put(Attributes.KNOCKBACK_RESISTANCE, new AttributeModifier(uuid, "Flight rig mass", knockbackResist, AttributeModifier.Operation.ADDITION));
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

    public EquipmentCategory getCategory() {
        return category;
    }

    public boolean canFly() {
        return this.flightDesign != FlightUnitModel.FlightDesign.TACTICAL_SCUBA
                && this.flightDesign != FlightUnitModel.FlightDesign.URBAN_EXO_LEGS
                && this.flightDesign != FlightUnitModel.FlightDesign.DIVING_MASK;
    }

    public static boolean isCompatible(EleniumFlightUnitItem a, EleniumFlightUnitItem b) {
        if (a == null || b == null) return true;
        // Two items of the exact same category cannot be active together
        if (a.getCategory() == b.getCategory()) return false;

        // Head accessories (like Diving Mask) are compatible with all units
        if (a.getCategory() == EquipmentCategory.HEAD_AUX || b.getCategory() == EquipmentCategory.HEAD_AUX) {
            return true;
        }

        EleniumFlightUnitItem torso = a.getCategory() == EquipmentCategory.TORSO_MAIN ? a : b;
        EleniumFlightUnitItem leg = a.getCategory() == EquipmentCategory.LEGS_AUX ? a : b;

        // Heavy frames and full-body exoskeletons conflict with auxiliary leg modules
        if (torso.getFlightDesign() == FlightUnitModel.FlightDesign.TWIN_DRIVE_EXO) return false;
        if (torso.getFlightDesign() == FlightUnitModel.FlightDesign.SIEGE_ARTILLERY) return false;
        if (torso.getFlightDesign() == FlightUnitModel.FlightDesign.HEAVY_ROCKET) return false;

        // Valkyrie Thrust Boots conflict with Hydro Skimmer and Scuba Rig
        if (leg.getFlightDesign() == FlightUnitModel.FlightDesign.THRUST_BOOTS) {
            if (torso.getFlightDesign() == FlightUnitModel.FlightDesign.HYDRO_SKIMMER ||
                torso.getFlightDesign() == FlightUnitModel.FlightDesign.TACTICAL_SCUBA) {
                return false;
            }
        }

        // Urban Scout Exo-Legs are compatible with standard flight units, Hydro Skimmer, and Scuba Rig!
        return true;
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

        if (this.category == EquipmentCategory.HEAD_AUX) {
            ItemStack head = player.getItemBySlot(EquipmentSlot.HEAD);
            if (head.isEmpty()) {
                player.setItemSlot(EquipmentSlot.HEAD, stack.copy());
                stack.setCount(0);
                onEquipUnit(player, player.getItemBySlot(EquipmentSlot.HEAD));
                return InteractionResultHolder.sidedSuccess(ItemStack.EMPTY, level.isClientSide());
            }
        } else if (this.category == EquipmentCategory.LEGS_AUX) {
            ItemStack feet = player.getItemBySlot(EquipmentSlot.FEET);
            if (feet.isEmpty()) {
                player.setItemSlot(EquipmentSlot.FEET, stack.copy());
                stack.setCount(0);
                onEquipUnit(player, player.getItemBySlot(EquipmentSlot.FEET));
                return InteractionResultHolder.sidedSuccess(ItemStack.EMPTY, level.isClientSide());
            }
        } else {
            ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
            if (chest.isEmpty()) {
                player.setItemSlot(EquipmentSlot.CHEST, stack.copy());
                stack.setCount(0);
                onEquipUnit(player, player.getItemBySlot(EquipmentSlot.CHEST));
                return InteractionResultHolder.sidedSuccess(ItemStack.EMPTY, level.isClientSide());
            }
        }

        return super.use(level, player, hand);
    }

    @Override
    public void curioTick(SlotContext slotContext, ItemStack stack) {
        LivingEntity living = slotContext.entity();
        if (living instanceof Player player) {
            tickEquippedUnit(player, stack);
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
        } else if (this.flightDesign == FlightUnitModel.FlightDesign.URBAN_EXO_LEGS) {
            modifiers.put(Attributes.MOVEMENT_SPEED,
                    new AttributeModifier(VALKYRIE_SPEED_MODIFIER_UUID,
                            "Urban Scout Kinetic Boost", 0.025D, AttributeModifier.Operation.ADDITION));
        }
        addCombatModifiers(modifiers, uuid);
        return modifiers;
    }

    @Override
    public Multimap<Attribute, AttributeModifier> getDefaultAttributeModifiers(EquipmentSlot slot) {
        Multimap<Attribute, AttributeModifier> modifiers = HashMultimap.create();
        if (slot == EquipmentSlot.FEET || slot == EquipmentSlot.CHEST) {
            if (this.flightDesign == FlightUnitModel.FlightDesign.THRUST_BOOTS) {
                modifiers.put(Attributes.MOVEMENT_SPEED,
                        new AttributeModifier(VALKYRIE_SPEED_MODIFIER_UUID,
                                "Valkyrie Kinetic Ground Boost", 0.035D, AttributeModifier.Operation.ADDITION));
            } else if (this.flightDesign == FlightUnitModel.FlightDesign.URBAN_EXO_LEGS) {
                modifiers.put(Attributes.MOVEMENT_SPEED,
                        new AttributeModifier(VALKYRIE_SPEED_MODIFIER_UUID,
                                "Urban Scout Kinetic Boost", 0.025D, AttributeModifier.Operation.ADDITION));
            }
        }
        if (slot == getEquipSlot()) {
            addCombatModifiers(modifiers, UUID.nameUUIDFromBytes(("youjosenki:rig_plating:" + slot.getName()).getBytes()));
        }
        return modifiers;
    }

    @Override
    public void inventoryTick(@NotNull ItemStack stack, @NotNull Level level, @NotNull Entity entity, int slotId, boolean isSelected) {
        if (entity instanceof Player player) {
            ItemStack head = player.getItemBySlot(EquipmentSlot.HEAD);
            ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
            ItemStack feet = player.getItemBySlot(EquipmentSlot.FEET);
            if (chest == stack || feet == stack || head == stack) {
                tickEquippedUnit(player, stack);
            }
        }
    }

    public void tickEquippedUnit(Player player, ItemStack stack) {
        // Exclusivity / Compatibility check
        if (this.category == EquipmentCategory.TORSO_MAIN) {
            ItemStack activeMain = getEquippedMainUnit(player);
            if (activeMain != stack) {
                // Redundant secondary torso rig: suppress
                if (player.tickCount % 100 == 0 && !player.level().isClientSide()) {
                    player.displayClientMessage(Component.translatable("message.youjosenki.redundant_unit", stack.getHoverName().getString()), true);
                }
                return;
            }
        } else if (this.category == EquipmentCategory.LEGS_AUX) {
            ItemStack activeLeg = getEquippedLegUnit(player);
            if (activeLeg != stack) {
                // Redundant secondary leg rig: suppress
                return;
            }
            ItemStack activeMain = getEquippedMainUnit(player);
            if (activeMain != null && activeMain.getItem() instanceof EleniumFlightUnitItem mainItem) {
                if (!isCompatible(mainItem, this)) {
                    // Incompatible chassis combination: suppress
                    if (player.tickCount % 100 == 0 && !player.level().isClientSide()) {
                        player.displayClientMessage(Component.translatable("message.youjosenki.incompatible_unit", stack.getHoverName().getString(), activeMain.getHoverName().getString()), true);
                    }
                    return;
                }
            }
        } else if (this.category == EquipmentCategory.HEAD_AUX) {
            ItemStack activeHead = getEquippedHeadUnit(player);
            if (activeHead != stack) {
                return;
            }
        }

        // Dispatch behavior by model design
        switch (this.flightDesign) {
            case HYDRO_SKIMMER -> {
                handleHydroSkimmer(player, stack);
                handleFlight(player, stack);
            }
            case TACTICAL_SCUBA -> {
                handleTacticalScuba(player, stack);
            }
            case URBAN_EXO_LEGS -> {
                handleUrbanExoLegs(player, stack);
            }
            case DIVING_MASK -> {
                handleDivingMask(player, stack);
            }
            default -> {
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

    public static ItemStack getEquippedMainUnit(Player player) {
        ItemStack chest = player.getItemBySlot(EquipmentSlot.CHEST);
        if (chest.getItem() instanceof EleniumFlightUnitItem item && item.getCategory() == EquipmentCategory.TORSO_MAIN) {
            return chest;
        }

        if (CuriosCompat.isCuriosLoaded()) {
            top.theillusivec4.curios.api.type.capability.ICuriosItemHandler handler =
                    CuriosApi.getCuriosInventory(player).resolve().orElse(null);
            if (handler != null) {
                var res = handler.findFirstCurio(s -> s.getItem() instanceof EleniumFlightUnitItem item && item.getCategory() == EquipmentCategory.TORSO_MAIN);
                if (res.isPresent()) {
                    return res.get().stack();
                }
            }
        }
        return null;
    }

    public static ItemStack getEquippedLegUnit(Player player) {
        ItemStack feet = player.getItemBySlot(EquipmentSlot.FEET);
        if (feet.getItem() instanceof EleniumFlightUnitItem item && item.getCategory() == EquipmentCategory.LEGS_AUX) {
            return feet;
        }

        if (CuriosCompat.isCuriosLoaded()) {
            top.theillusivec4.curios.api.type.capability.ICuriosItemHandler handler =
                    CuriosApi.getCuriosInventory(player).resolve().orElse(null);
            if (handler != null) {
                var res = handler.findFirstCurio(s -> s.getItem() instanceof EleniumFlightUnitItem item && item.getCategory() == EquipmentCategory.LEGS_AUX);
                if (res.isPresent()) {
                    return res.get().stack();
                }
            }
        }
        return null;
    }

    public static ItemStack getEquippedHeadUnit(Player player) {
        ItemStack head = player.getItemBySlot(EquipmentSlot.HEAD);
        if (head.getItem() instanceof EleniumFlightUnitItem item && item.getCategory() == EquipmentCategory.HEAD_AUX) {
            return head;
        }

        if (CuriosCompat.isCuriosLoaded()) {
            top.theillusivec4.curios.api.type.capability.ICuriosItemHandler handler =
                    CuriosApi.getCuriosInventory(player).resolve().orElse(null);
            if (handler != null) {
                var res = handler.findFirstCurio(s -> s.getItem() instanceof EleniumFlightUnitItem item && item.getCategory() == EquipmentCategory.HEAD_AUX);
                if (res.isPresent()) {
                    return res.get().stack();
                }
            }
        }
        return null;
    }

    public static boolean hasEquippedMask(Player player) {
        ItemStack head = getEquippedHeadUnit(player);
        return head != null && head.getItem() instanceof EleniumFlightUnitItem item && item.getFlightDesign() == FlightUnitModel.FlightDesign.DIVING_MASK;
    }

    public static boolean hasEquippedScubaRig(Player player) {
        ItemStack main = getEquippedMainUnit(player);
        return main != null && main.getItem() instanceof EleniumFlightUnitItem item && item.getFlightDesign() == FlightUnitModel.FlightDesign.TACTICAL_SCUBA;
    }

    public static ItemStack getEquippedFlightUnit(Player player) {
        ItemStack main = getEquippedMainUnit(player);
        if (main != null && main.getItem() instanceof EleniumFlightUnitItem item) {
            // If main unit is Scuba Rig, its diving ballast overrides and blocks aerial flight!
            if (item.getFlightDesign() == FlightUnitModel.FlightDesign.TACTICAL_SCUBA) {
                return null;
            }
            if (item.canFly()) {
                return main;
            }
        }

        // Fallback: check if active leg unit can fly (e.g. Valkyrie Thrust Boots)
        ItemStack leg = getEquippedLegUnit(player);
        if (leg != null && leg.getItem() instanceof EleniumFlightUnitItem legItem && legItem.canFly()) {
            if (main != null && main.getItem() instanceof EleniumFlightUnitItem mainItem) {
                if (!isCompatible(mainItem, legItem)) return null;
            }
            return leg;
        }

        return null;
    }

    public static boolean hasEnergizedFlightUnit(Player player) {
        if (player.isCreative() || player.isSpectator()) return true;
        ItemStack flightUnit = getEquippedFlightUnit(player);
        return flightUnit != null && isItemEnergized(flightUnit);
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

        if (this.canFly()) {
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
        } else {
            if (!player.level().isClientSide) {
                player.displayClientMessage(Component.translatable("message.youjosenki.activated_ground", unitName), true);
            }
        }
    }

    public void onUnequipUnit(Player player) {
        // If player still has another energized flight unit equipped, keep flying!
        ItemStack remainingFlightUnit = getEquippedFlightUnit(player);
        if (remainingFlightUnit != null && isItemEnergized(remainingFlightUnit)) {
            return;
        }

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

    public void handleHydroSkimmer(Player player, ItemStack stack) {
        boolean isCreative = player.isCreative() || player.isSpectator();
        boolean hasEnergy = isCreative || isItemEnergized(stack);

        // 1. Unsinkable Positive Buoyancy:
        // Skimmer cannot dive underwater! If submerged or in water, push player upward
        if (player.isInWater()) {
            Vec3 vel = player.getDeltaMovement();
            if (player.isUnderWater()) {
                // Rapidly surface
                player.setDeltaMovement(vel.x, Math.max(vel.y, 0.42), vel.z);
            } else if (vel.y < 0) {
                // Float steady on the water surface (like a surfboard)
                player.setDeltaMovement(vel.x, 0.02, vel.z);
            }
        }

        // 2. High-Speed Hydro Skimming:
        // When touching water, apply extreme water skiing acceleration
        boolean onWater = player.isInWater() ||
                player.level().getBlockState(player.blockPosition().below()).is(net.minecraft.world.level.block.Blocks.WATER);

        if (onWater && hasEnergy) {
            Vec3 vel = player.getDeltaMovement();
            double horizSpeedSq = vel.x * vel.x + vel.z * vel.z;
            if (horizSpeedSq > 0.002) {
                // High velocity acceleration up to 0.88 blocks/tick (~63 km/h on water!)
                double curHoriz = Math.sqrt(horizSpeedSq);
                if (curHoriz < 0.88) {
                    player.setDeltaMovement(vel.x * 1.055, vel.y, vel.z * 1.055);
                }

                // Water spray particles and wake
                if (player.level() instanceof ServerLevel serverLevel && player.tickCount % 2 == 0) {
                    double yawRad = Math.toRadians(player.getYRot());
                    double cosYaw = Math.cos(yawRad);
                    double sinYaw = Math.sin(yawRad);
                    double lx = player.getX() + cosYaw * 0.35;
                    double lz = player.getZ() + sinYaw * 0.35;
                    double rx = player.getX() - cosYaw * 0.35;
                    double rz = player.getZ() - sinYaw * 0.35;
                    double y = player.getY() + 0.05;

                    serverLevel.sendParticles(ParticleTypes.SPLASH, lx, y, lz, 3, 0.1, 0.1, 0.1, 0.08);
                    serverLevel.sendParticles(ParticleTypes.SPLASH, rx, y, rz, 3, 0.1, 0.1, 0.1, 0.08);
                    serverLevel.sendParticles(ParticleTypes.BUBBLE, player.getX(), y, player.getZ(), 3, 0.2, 0.02, 0.2, 0.04);
                    serverLevel.sendParticles(ParticleTypes.CLOUD, player.getX(), y, player.getZ(), 1, 0.1, 0.02, 0.1, 0.01);
                }

                if (!player.level().isClientSide && player.tickCount % 8 == 0) {
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.GENERIC_SWIM, SoundSource.PLAYERS, 0.6F, 1.4F);
                }

                if (!isCreative && !player.level().isClientSide && player.tickCount % 4 == 0) {
                    IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                    if (energy != null) energy.extractEnergy(3, false);
                }
            }
        } else if (player.onGround() && !onWater) {
            // 3. Walk slower on dry land (simulating awkward heavy pontoons)
            Vec3 vel = player.getDeltaMovement();
            player.setDeltaMovement(vel.x * 0.88, vel.y, vel.z * 0.88);
        }

        // Service ceiling enforcement (Ceiling = 76m, very low)
        if (player.getAbilities().flying && !player.onGround() && player.getY() >= this.serviceCeiling) {
            Vec3 vel = player.getDeltaMovement();
            if (vel.y > 0) {
                player.setDeltaMovement(vel.x * 0.90, Math.min(vel.y * 0.15, 0.02), vel.z * 0.90);
            }
        }
    }

    public void handleTacticalScuba(Player player, ItemStack stack) {
        boolean isCreative = player.isCreative() || player.isSpectator();
        boolean hasEnergy = isCreative || isItemEnergized(stack);
        boolean hasMask = hasEquippedMask(player);

        // Scuba Rig completely suppresses airborne flight!
        if (player.getAbilities().flying || player.getAbilities().mayfly) {
            if (!isCreative) {
                player.getAbilities().flying = false;
                player.getAbilities().mayfly = false;
                player.onUpdateAbilities();
            }
        }

        if (player.isInWater()) {
            if (hasEnergy) {
                if (hasMask) {
                    // FULL 2/2 SET SYNERGY: True Diving Mastery
                    player.setAirSupply(player.getMaxAirSupply());

                    // Crystal Clear Underwater Vision
                    player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                            net.minecraft.world.effect.MobEffects.NIGHT_VISION, 260, 0, false, false, false));

                    // High-speed Underwater Swim Propulsion
                    if (player.isSwimming()) {
                        Vec3 look = player.getLookAngle();
                        player.setDeltaMovement(player.getDeltaMovement().add(look.scale(0.048)));
                    }

                    // Bubble Exhaust Particles & Regulator Audio
                    if (player.level() instanceof ServerLevel serverLevel && player.tickCount % 6 == 0) {
                        serverLevel.sendParticles(ParticleTypes.BUBBLE, player.getX(), player.getY() + 0.75, player.getZ(), 4, 0.15, 0.15, 0.15, 0.05);
                    }
                    if (!player.level().isClientSide && player.tickCount % 40 == 0) {
                        player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                                SoundEvents.PLAYER_BREATH, SoundSource.PLAYERS, 0.50F, 0.85F);
                    }

                    if (player.tickCount % 120 == 0 && !player.level().isClientSide()) {
                        player.displayClientMessage(Component.translatable("message.youjosenki.scuba_synergy_full"), true);
                    }
                } else {
                    // PARTIAL (1/2): Scuba Rig only (Missing Diving Mask)
                    // Tank provides air slowly, but oral seal is open: partial air replenishing
                    if (player.getAirSupply() < player.getMaxAirSupply() / 2) {
                        player.setAirSupply(player.getAirSupply() + 1);
                    }
                    // Prompt player once every 80 ticks
                    if (player.tickCount % 80 == 0 && !player.level().isClientSide()) {
                        player.displayClientMessage(Component.translatable("message.youjosenki.scuba_missing_mask"), true);
                    }
                }

                if (!isCreative && !player.level().isClientSide && player.tickCount % 5 == 0) {
                    IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                    if (energy != null) energy.extractEnergy(1, false);
                }
            }
        } else if (player.onGround()) {
            // Land penalties: heavy dive weight blocks jumping and slows movement
            Vec3 vel = player.getDeltaMovement();
            player.setDeltaMovement(vel.x * 0.78, vel.y, vel.z * 0.78);

            // Block high jumping on land
            if (vel.y > 0.08) {
                player.setDeltaMovement(vel.x, 0.01, vel.z);
                if (player.tickCount % 30 == 0 && !player.level().isClientSide()) {
                    player.displayClientMessage(Component.translatable("message.youjosenki.scuba_jump_blocked"), true);
                }
            }
        }
    }

    public void handleDivingMask(Player player, ItemStack stack) {
        boolean isCreative = player.isCreative() || player.isSpectator();
        boolean hasEnergy = isCreative || isItemEnergized(stack);
        boolean hasScubaRig = hasEquippedScubaRig(player);

        if (player.isInWater() && hasEnergy) {
            // Mask always provides clear underwater vision goggles
            player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                    net.minecraft.world.effect.MobEffects.NIGHT_VISION, 260, 0, false, false, false));

            if (!hasScubaRig) {
                // PARTIAL (1/2): Mask only (Emergency oral rebreather filter)
                // Filter slightly slows down drowning, but lacks main oxygen tanks
                if (player.tickCount % 3 == 0 && player.getAirSupply() < player.getMaxAirSupply()) {
                    player.setAirSupply(player.getAirSupply() + 1);
                }
                if (player.tickCount % 80 == 0 && !player.level().isClientSide()) {
                    player.displayClientMessage(Component.translatable("message.youjosenki.mask_missing_scuba"), true);
                }
            }

            if (!isCreative && !player.level().isClientSide && player.tickCount % 10 == 0) {
                IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                if (energy != null) energy.extractEnergy(1, false);
            }
        }
    }

    public void handleUrbanExoLegs(Player player, ItemStack stack) {
        boolean isCreative = player.isCreative() || player.isSpectator();
        boolean hasEnergy = isCreative || isItemEnergized(stack);

        if (!hasEnergy) return;

        // 1. Fall Damage Absorption
        player.fallDistance = 0.0F;

        // 2. High Jump Boost (+0.25 vertical velocity when leaving ground)
        Vec3 vel = player.getDeltaMovement();
        if (player.onGround()) {
            // Reset jump trigger latch in NBT
            CompoundTag tag = stack.getOrCreateTag();
            tag.putBoolean("CanJumpBoost", true);
        } else {
            CompoundTag tag = stack.getOrCreateTag();
            if (tag.getBoolean("CanJumpBoost") && vel.y > 0.25 && vel.y < 0.60) {
                tag.putBoolean("CanJumpBoost", false);
                player.setDeltaMovement(vel.x, vel.y * 1.45 + 0.12, vel.z);

                if (!player.level().isClientSide()) {
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.PISTON_EXTEND, SoundSource.PLAYERS, 0.7F, 1.8F);
                    if (player.level() instanceof ServerLevel serverLevel) {
                        serverLevel.sendParticles(ParticleTypes.POOF, player.getX(), player.getY(), player.getZ(), 4, 0.12, 0.05, 0.12, 0.02);
                    }
                    if (!isCreative) {
                        IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                        if (energy != null) energy.extractEnergy(15, false);
                    }
                }
            }
        }

        // 3. Kinetic Forward Dash (when sprinting on ground, pressing forward)
        CompoundTag tag = stack.getOrCreateTag();
        int cooldown = tag.getInt("DashCooldown");
        if (cooldown > 0) {
            tag.putInt("DashCooldown", cooldown - 1);
        }

        if (player.isSprinting() && player.onGround() && cooldown <= 0 && vel.horizontalDistanceSqr() > 0.005) {
            // Small burst dash triggered when sprint is active
            if (player.tickCount % 22 == 0) {
                tag.putInt("DashCooldown", 16);
                Vec3 look = player.getLookAngle();
                player.setDeltaMovement(vel.x + look.x * 0.42, 0.16, vel.z + look.z * 0.42);

                if (!player.level().isClientSide()) {
                    player.level().playSound(null, player.getX(), player.getY(), player.getZ(),
                            SoundEvents.FIREWORK_ROCKET_LAUNCH, SoundSource.PLAYERS, 0.75F, 1.6F);
                    if (player.level() instanceof ServerLevel serverLevel) {
                        serverLevel.sendParticles(ParticleTypes.ELECTRIC_SPARK, player.getX(), player.getY() + 0.15, player.getZ(), 3, 0.1, 0.08, 0.1, 0.03);
                    }
                    if (!isCreative) {
                        IEnergyStorage energy = stack.getCapability(ForgeCapabilities.ENERGY).orElse(null);
                        if (energy != null) energy.extractEnergy(25, false);
                    }
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

                // Position delta, not getDeltaMovement(): the server never integrates a client-driven player's velocity
                double movedX = player.getX() - player.xo, movedZ = player.getZ() - player.zo;
                boolean isMoving = movedX * movedX + movedZ * movedZ > 0.0005;

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
                    requiredEnergy = Math.round(requiredEnergy * this.energyDrainMult);

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
                    FlightVFXHelper.handleGroundDownwash((ServerLevel) player.level(), player, isSprinting, isMoving, this.soundProfile, getThrustClass());
                }
            } else {
                // Flying -> grounded this tick: touchdown
                if (FLYING_PLAYERS.remove(player.getUUID()) && player.onGround() && player.level() instanceof ServerLevel serverLevel) {
                    FlightVFXHelper.spawnLandingShockwave(serverLevel, player, getThrustClass());
                }

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
        tooltip.add(Component.translatable("tooltip.youjosenki.role", Component.translatable(this.getDescriptionId() + ".role")).withStyle(ChatFormatting.LIGHT_PURPLE));
        tooltip.add(Component.literal("§7Style: §f" + this.flightDesign.getDisplayName()).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§7Avionics: §f" + this.hudGeneration.getDisplayName()).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("§e✈ Cruising: §f" + String.format("%.0f%%", (this.baseFlightSpeed / 0.05F) * 100) +
                " §7| §6Sprint: §f" + String.format("%.1fx", this.sprintSpeedMultiplier)).withStyle(ChatFormatting.GOLD));

        if (armor > 0 || knockbackResist > 0) {
            tooltip.add(Component.literal(String.format("§9🛡 Armor: §f+%.0f §7| §9Toughness: §f+%.0f §7| §9KB Resist: §f%.0f%%",
                    armor, armorToughness, knockbackResist * 100)));
        }
        if (canFly()) {
            tooltip.add(Component.literal(String.format("§b⚡ Drain: §fx%.2f §7| §c🔥 Heat: §fx%.2f §7| §d⟳ Boost CD: §f%.2fs",
                    energyDrainMult, heatGainMult, boostCooldownTicks / 20.0F)));
        }
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
            if (canFly()) {
                tooltip.add(Component.translatable("tooltip.youjosenki.desc.flight",
                        Math.round(Config.COMMON.hoverEnergyCost.get() * energyDrainMult),
                        Math.round(Config.COMMON.flightEnergyCost.get() * energyDrainMult),
                        Math.round(Config.COMMON.sprintEnergyCost.get() * energyDrainMult),
                        serviceCeiling).withStyle(ChatFormatting.GREEN));
            }
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.sprint").withStyle(ChatFormatting.GOLD));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.smoke").withStyle(ChatFormatting.GRAY));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.dyeable").withStyle(ChatFormatting.LIGHT_PURPLE));
            tooltip.add(Component.translatable("tooltip.youjosenki.desc.falldamage").withStyle(ChatFormatting.BLUE));
        } else {
            tooltip.add(Component.translatable("tooltip.youjosenki.shift_hint").withStyle(ChatFormatting.DARK_GRAY));
        }
    }
}
