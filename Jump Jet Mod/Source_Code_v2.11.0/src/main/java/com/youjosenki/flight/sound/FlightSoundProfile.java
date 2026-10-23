package com.youjosenki.flight.sound;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

/**
 * Premium sound profiles tailored for modern high-tech apparatus vs classic vintage apparatus.
 * NO annoying wind noise (Elytra) and NO train rattling (Minecart).
 * Designed for comfortable, non-fatiguing pilot audio and clear 3D tactical enemy detection.
 */
public enum FlightSoundProfile {
    // 1. Tanya's Quad-Core Elenium Type 95 Prototype (เทคโนโลยีแกนเวทมนตร์ล้ำสมัยที่สุด)
    PROTOTYPE_MANA_CORE(0.42F, 1.25F, 0.75F, 1.30F, 24.0F, "prototype_mana"),

    // 2. Republic Type 101 Francois Delta-Wings (เทคโนโลยีปีกอากาศพลศาสตร์ล้ำยุค)
    AERODYNAMIC_STREAM(0.40F, 1.35F, 0.70F, 1.35F, 22.0F, "aerodynamic_stream"),

    // 3. Tactical Combat Jetpack & Allied Model 1923 (เทคโนโลยีทวินเจ็ตทหารสมัยใหม่)
    MODERN_MILITARY_JET(0.45F, 1.10F, 0.75F, 1.15F, 26.0F, "modern_military_jet"),

    // 4. Shadow Recon Apex Delta-Wings (เทคโนโลยีลอบเร้นขั้นสูงสุด เสียงเบากริบ)
    STEALTH_RECON_WHISPER(0.22F, 1.55F, 0.35F, 1.60F, 10.0F, "stealth_recon_whisper"),

    // 5. Titan Heavy Industrial Rocket & Russy Federation Type 82 (เทคโนโลยีจรวดหนัก เสียงทุ้มแน่นดุดัน)
    HEAVY_ROCKET_BOOSTER(0.55F, 0.70F, 0.85F, 0.75F, 38.0F, "heavy_rocket_booster"),

    // 6. 203rd Battalion Type 97, Commonwealth Mk2, Entente Ski-rig (รุ่นคลาสสิก / ยุคแรก กลไกไอน้ำและห้องเผาไหม้)
    VINTAGE_EARLY_MAGE(0.38F, 0.95F, 0.70F, 1.05F, 20.0F, "vintage_early_mage");

    public final float cruiseVolume;
    public final float cruisePitch;
    public final float sprintVolume;
    public final float sprintPitch;
    public final float audibleRange;
    public final String id;

    FlightSoundProfile(float cruiseVolume, float cruisePitch, float sprintVolume, float sprintPitch, float audibleRange, String id) {
        this.cruiseVolume = cruiseVolume;
        this.cruisePitch = cruisePitch;
        this.sprintVolume = sprintVolume;
        this.sprintPitch = sprintPitch;
        this.audibleRange = audibleRange;
        this.id = id;
    }

    /**
     * Punchy, satisfying takeoff activation burst.
     * High volume and distinct rising whoosh surge to signal instant liftoff:
     * - Modern/Prototype models: High-tech mana/reactor surge with supersonic high-frequency rising whoosh.
     * - Vintage/Early models: Mechanical pneumatic snap and deep throaty combustion blast.
     */
    public void playTakeoff(Player player) {
        Level level = player.level();
        double x = player.getX();
        double y = player.getY();
        double z = player.getZ();

        switch (this) {
            case PROTOTYPE_MANA_CORE -> {
                // [NEW MODEL] High-tech Quad-Core Mana surge + supersonic rising whoosh
                level.playSound(null, x, y, z, SoundEvents.BEACON_ACTIVATE, SoundSource.PLAYERS, 1.40F, 1.35F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_3, SoundSource.PLAYERS, 1.50F, 1.30F);
                level.playSound(null, x, y, z, SoundEvents.FIREWORK_ROCKET_LAUNCH, SoundSource.PLAYERS, 1.30F, 1.45F);
                level.playSound(null, x, y, z, SoundEvents.WARDEN_SONIC_CHARGE, SoundSource.PLAYERS, 0.75F, 1.60F);
            }
            case AERODYNAMIC_STREAM -> {
                // [NEW MODEL] Aerodynamic supersonic stream release + high-frequency turbine spin
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_2, SoundSource.PLAYERS, 1.50F, 1.35F);
                level.playSound(null, x, y, z, SoundEvents.BEACON_POWER_SELECT, SoundSource.PLAYERS, 1.30F, 1.50F);
                level.playSound(null, x, y, z, SoundEvents.FIREWORK_ROCKET_LAUNCH, SoundSource.PLAYERS, 1.25F, 1.40F);
            }
            case MODERN_MILITARY_JET -> {
                // [NEW MODEL] Military turbojet afterburner ignition + clean supersonic thrust spool
                level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 1.45F, 1.25F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_3, SoundSource.PLAYERS, 1.50F, 1.28F);
                level.playSound(null, x, y, z, SoundEvents.FIREWORK_ROCKET_LAUNCH, SoundSource.PLAYERS, 1.35F, 1.35F);
            }
            case STEALTH_RECON_WHISPER -> {
                // [NEW MODEL] Supersonic phase slipstream surge (sharp, clean, high-frequency)
                level.playSound(null, x, y, z, SoundEvents.ILLUSIONER_MIRROR_MOVE, SoundSource.PLAYERS, 1.15F, 1.60F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_3, SoundSource.PLAYERS, 1.25F, 1.70F);
                level.playSound(null, x, y, z, SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.PLAYERS, 1.00F, 1.60F);
            }
            case HEAVY_ROCKET_BOOSTER -> {
                // [HEAVY INDUSTRIAL] Thunderous rocket blast & deep bass combustion
                level.playSound(null, x, y, z, SoundEvents.GENERIC_EXPLODE, SoundSource.PLAYERS, 0.95F, 1.50F);
                level.playSound(null, x, y, z, SoundEvents.FIREWORK_ROCKET_LARGE_BLAST, SoundSource.PLAYERS, 1.60F, 0.65F);
                level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 1.50F, 0.60F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_1, SoundSource.PLAYERS, 1.35F, 0.70F);
            }
            case VINTAGE_EARLY_MAGE -> {
                // [OLD MODEL] Mechanical pneumatic valve snap + throaty vintage furnace combustion blast
                level.playSound(null, x, y, z, SoundEvents.PISTON_EXTEND, SoundSource.PLAYERS, 1.50F, 0.85F);
                level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, 1.45F, 0.80F);
                level.playSound(null, x, y, z, SoundEvents.FIREWORK_ROCKET_LARGE_BLAST, SoundSource.PLAYERS, 1.35F, 0.80F);
                level.playSound(null, x, y, z, SoundEvents.BLASTFURNACE_FIRE_CRACKLE, SoundSource.PLAYERS, 1.25F, 0.90F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_1, SoundSource.PLAYERS, 1.30F, 0.80F);
            }
        }
    }

    /**
     * Smooth, non-fatiguing ambient cruising loop (no harsh wind or train rattle).
     */
    public void playCruising(Player player) {
        Level level = player.level();
        double x = player.getX();
        double y = player.getY();
        double z = player.getZ();

        switch (this) {
            case PROTOTYPE_MANA_CORE -> {
                // Sleek, calming sci-fi reactor core hum
                level.playSound(null, x, y, z, SoundEvents.CONDUIT_AMBIENT, SoundSource.PLAYERS, cruiseVolume, cruisePitch);
                level.playSound(null, x, y, z, SoundEvents.RESPAWN_ANCHOR_AMBIENT, SoundSource.PLAYERS, cruiseVolume * 0.45F, 1.40F);
            }
            case AERODYNAMIC_STREAM -> {
                // High-altitude whistling resonance
                level.playSound(null, x, y, z, SoundEvents.CONDUIT_AMBIENT_SHORT, SoundSource.PLAYERS, cruiseVolume, cruisePitch);
                level.playSound(null, x, y, z, SoundEvents.BEACON_AMBIENT, SoundSource.PLAYERS, cruiseVolume * 0.50F, 1.45F);
            }
            case MODERN_MILITARY_JET -> {
                // Pressurized clean turbojet combustion hum
                level.playSound(null, x, y, z, SoundEvents.BLASTFURNACE_FIRE_CRACKLE, SoundSource.PLAYERS, cruiseVolume, 1.20F);
                level.playSound(null, x, y, z, SoundEvents.CONDUIT_AMBIENT, SoundSource.PLAYERS, cruiseVolume * 0.65F, 1.05F);
            }
            case STEALTH_RECON_WHISPER -> {
                // Subtle crystalline oscillation
                level.playSound(null, x, y, z, SoundEvents.AMETHYST_BLOCK_RESONATE, SoundSource.PLAYERS, cruiseVolume, 1.60F);
                level.playSound(null, x, y, z, SoundEvents.CONDUIT_AMBIENT_SHORT, SoundSource.PLAYERS, cruiseVolume * 0.80F, 1.50F);
            }
            case HEAVY_ROCKET_BOOSTER -> {
                // Deep, warm combustion chamber rumble
                level.playSound(null, x, y, z, SoundEvents.BLASTFURNACE_FIRE_CRACKLE, SoundSource.PLAYERS, cruiseVolume, 0.70F);
                level.playSound(null, x, y, z, SoundEvents.RESPAWN_ANCHOR_AMBIENT, SoundSource.PLAYERS, cruiseVolume * 0.60F, 0.65F);
            }
            case VINTAGE_EARLY_MAGE -> {
                // Classic mechanical furnace and mana purr
                level.playSound(null, x, y, z, SoundEvents.BLASTFURNACE_FIRE_CRACKLE, SoundSource.PLAYERS, cruiseVolume, 0.95F);
                level.playSound(null, x, y, z, SoundEvents.BEACON_AMBIENT, SoundSource.PLAYERS, cruiseVolume * 0.60F, 0.95F);
            }
        }
    }

    /**
     * Awesome, high-velocity sprint afterburner / thrust surge.
     */
    public void playSprint(Player player) {
        Level level = player.level();
        double x = player.getX();
        double y = player.getY();
        double z = player.getZ();

        switch (this) {
            case PROTOTYPE_MANA_CORE -> {
                // Heroic anime hyperdrive surge + particle accelerator resonance
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_2, SoundSource.PLAYERS, sprintVolume, sprintPitch);
                level.playSound(null, x, y, z, SoundEvents.WARDEN_SONIC_CHARGE, SoundSource.PLAYERS, sprintVolume * 0.40F, 1.45F);
            }
            case AERODYNAMIC_STREAM -> {
                // Aerodynamic supersonic slipstream
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_1, SoundSource.PLAYERS, sprintVolume, sprintPitch);
                level.playSound(null, x, y, z, SoundEvents.ILLUSIONER_MIRROR_MOVE, SoundSource.PLAYERS, sprintVolume * 0.55F, 1.25F);
            }
            case MODERN_MILITARY_JET -> {
                // Punchy afterburner ignition and thrust
                level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, sprintVolume, 1.20F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_1, SoundSource.PLAYERS, sprintVolume * 0.80F, 1.10F);
            }
            case STEALTH_RECON_WHISPER -> {
                // Ghostly silent displacement
                level.playSound(null, x, y, z, SoundEvents.ILLUSIONER_MIRROR_MOVE, SoundSource.PLAYERS, sprintVolume, 1.45F);
                level.playSound(null, x, y, z, SoundEvents.TRIDENT_RIPTIDE_3, SoundSource.PLAYERS, sprintVolume * 0.60F, 1.70F);
            }
            case HEAVY_ROCKET_BOOSTER -> {
                // Massive heavy rocket booster burn
                level.playSound(null, x, y, z, SoundEvents.FIREWORK_ROCKET_BLAST, SoundSource.PLAYERS, sprintVolume, 0.75F);
                level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, sprintVolume * 0.85F, 0.75F);
                level.playSound(null, x, y, z, SoundEvents.DRAGON_FIREBALL_EXPLODE, SoundSource.PLAYERS, sprintVolume * 0.35F, 1.80F);
            }
            case VINTAGE_EARLY_MAGE -> {
                // Vintage forced-induction boost & combustion roar
                level.playSound(null, x, y, z, SoundEvents.FIRECHARGE_USE, SoundSource.PLAYERS, sprintVolume, 1.05F);
                level.playSound(null, x, y, z, SoundEvents.BLAZE_SHOOT, SoundSource.PLAYERS, sprintVolume * 0.70F, 1.15F);
            }
        }
    }
}
