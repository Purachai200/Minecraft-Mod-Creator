import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.getcwd())
import create_test_world as nbt
from scratch.create_test_world import (
    TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG,
    TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING,
    TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY
)

TEMPLATE_PATH = r"C:\Users\Purachai\curseforge\minecraft\Instances\Tactical Frontier Line\saves\New World\level.dat"
DEST_BASE = r"C:\Users\Purachai\curseforge\minecraft\Instances\Mod Tester\saves"

def make_inventory():
    items_to_give = [
        # Hotbar (0 - 8)
        (0, "titancombat:exo_frame_beacon", 16),
        (1, "titancombat:bulwark_beacon", 16),
        (2, "titancombat:titan_exo_beacon", 16),
        (3, "titancombat:paint_spray_can", 1),
        (4, "titancombat:titan_armor_head", 4),
        (5, "titancombat:titan_armor_chest", 4),
        (6, "titancombat:titan_armor_arms", 4),
        (7, "titancombat:titan_armor_legs", 4),
        (8, "titancombat:vehicle_wrench", 1),

        # Main Inventory (9 - 35)
        (9, "titancombat:dense_fusion_battery", 4),
        (10, "titancombat:pilot_license", 1),
        (11, "titancombat:lcac_hovercraft", 1),
        (12, "titancombat:ocean_carrier", 1),
        (13, "titancombat:hauler_truck", 1),
        (14, "titancombat:chinook_transporter", 1),
        (15, "titancombat:v22_osprey", 1),
        (16, "titancombat:armored_apc", 1),
        (17, "titancombat:skycrane_drone", 1),
        (18, "titancombat:c130_hercules", 1),
        (19, "titancombat:mobile_suit_trailer", 1),
        (20, "titancombat:repair_truck", 1),
        (21, "titancombat:tactical_truck", 1),
        (22, "titancombat:striker_frame_beacon", 1),
        (23, "titancombat:vanguard_frame_beacon", 1),
        (24, "titancombat:colossus_frame_beacon", 1),
        (25, "titancombat:terrain_frame_beacon", 1),
        (26, "titancombat:cyclops_frame_beacon", 1),
        (27, "titancombat:spider_frame_beacon", 1),
        (28, "titancombat:weapon_sword", 1),
        (29, "titancombat:weapon_autocannon", 1),
        (30, "titancombat:weapon_railgun", 1),
        (31, "titancombat:weapon_plasma_blade", 1),
        (32, "titancombat:howitzer_module", 1),
        (33, "titancombat:rocket_launcher_module", 1),
        (34, "titancombat:ammo_artillery", 64),
        (35, "titancombat:ammo_rocket_salvo", 64),
    ]

    inv_list = []
    for slot, item_id, count in items_to_give:
        inv_list.append({
            'Slot': (TAG_BYTE, slot),
            'id': (TAG_STRING, item_id),
            'Count': (TAG_BYTE, count)
        })
    return inv_list

def create_superflat_save():
    save_dir = os.path.join(DEST_BASE, "Titan Combat Test Arena (Superflat)")
    os.makedirs(save_dir, exist_ok=True)

    root_name, root_type, val = nbt.load_nbt(TEMPLATE_PATH)
    data = val['Data'][1]

    # Configure metadata
    data['LevelName'] = (TAG_STRING, "Titan Combat Test Arena (Superflat)")
    data['GameType'] = (TAG_INT, 1) # Creative
    data['allowCommands'] = (TAG_BYTE, 1) # Cheats allowed
    data['hardcore'] = (TAG_BYTE, 0)
    data['Difficulty'] = (TAG_BYTE, 1)
    data['DifficultyLocked'] = (TAG_BYTE, 0)
    data['DayTime'] = (TAG_LONG, 6000)
    data['Time'] = (TAG_LONG, 6000)
    data['raining'] = (TAG_BYTE, 0)
    data['thundering'] = (TAG_BYTE, 0)
    data['rainTime'] = (TAG_INT, 999999)
    data['thunderTime'] = (TAG_INT, 999999)
    data['clearWeatherTime'] = (TAG_INT, 999999)

    # Spawn coordinates on flat surface
    data['SpawnX'] = (TAG_INT, 0)
    data['SpawnY'] = (TAG_INT, 65)
    data['SpawnZ'] = (TAG_INT, 0)
    data['SpawnAngle'] = (TAG_FLOAT, 0.0)

    # Clean vanilla datapacks
    data['DataPacks'] = (TAG_COMPOUND, {
        'Enabled': (TAG_LIST, (TAG_STRING, ['vanilla', 'mod:forge', 'mod:geckolib', 'mod:titancombat'])),
        'Disabled': (TAG_LIST, (TAG_STRING, []))
    })

    # Standard clean GameRules
    gr = data.get('GameRules', (TAG_COMPOUND, {}))[1]
    gr['keepInventory'] = (TAG_STRING, 'true')
    gr['doDaylightCycle'] = (TAG_STRING, 'false')
    gr['doWeatherCycle'] = (TAG_STRING, 'false')
    gr['doMobSpawning'] = (TAG_STRING, 'false')

    # Player config
    player = data['Player'][1]
    player['playerGameType'] = (TAG_INT, 1)
    player['Invulnerable'] = (TAG_BYTE, 1)
    player['Health'] = (TAG_FLOAT, 20.0)
    player['foodLevel'] = (TAG_INT, 20)
    player['Pos'] = (TAG_LIST, (TAG_DOUBLE, [0.5, 65.0, 0.5]))
    player['Motion'] = (TAG_LIST, (TAG_DOUBLE, [0.0, 0.0, 0.0]))
    player['Rotation'] = (TAG_LIST, (TAG_FLOAT, [0.0, 0.0]))
    player['FallDistance'] = (TAG_FLOAT, 0.0)
    player['Dimension'] = (TAG_STRING, 'minecraft:overworld')
    player['SpawnX'] = (TAG_INT, 0)
    player['SpawnY'] = (TAG_INT, 65)
    player['SpawnZ'] = (TAG_INT, 0)
    player['abilities'] = (TAG_COMPOUND, {
        'flying': (TAG_BYTE, 0),
        'flyingSpeed': (TAG_FLOAT, 0.05),
        'instabuild': (TAG_BYTE, 1),
        'invulnerable': (TAG_BYTE, 1),
        'mayBuild': (TAG_BYTE, 1),
        'mayfly': (TAG_BYTE, 1),
        'walkSpeed': (TAG_FLOAT, 0.1)
    })
    player['Inventory'] = (TAG_LIST, (TAG_COMPOUND, make_inventory()))
    player['SelectedItemSlot'] = (TAG_INT, 0)

    # Superflat Overworld Generator Settings
    wgen = data['WorldGenSettings'][1]
    wgen['generate_features'] = (TAG_BYTE, 0)
    wgen['bonus_chest'] = (TAG_BYTE, 0)

    overworld_gen = {
        'type': (TAG_STRING, 'minecraft:flat'),
        'settings': (TAG_COMPOUND, {
            'biome': (TAG_STRING, 'minecraft:plains'),
            'features': (TAG_BYTE, 0),
            'lakes': (TAG_BYTE, 0),
            'layers': (TAG_LIST, (TAG_COMPOUND, [
                {'block': (TAG_STRING, 'minecraft:bedrock'), 'height': (TAG_INT, 1)},
                {'block': (TAG_STRING, 'minecraft:deepslate'), 'height': (TAG_INT, 64)},
                {'block': (TAG_STRING, 'minecraft:stone'), 'height': (TAG_INT, 60)},
                {'block': (TAG_STRING, 'minecraft:dirt'), 'height': (TAG_INT, 3)},
                {'block': (TAG_STRING, 'minecraft:grass_block'), 'height': (TAG_INT, 1)},
            ])),
            'structure_overrides': (TAG_LIST, (TAG_STRING, []))
        })
    }

    wgen['dimensions'][1]['minecraft:overworld'] = (TAG_COMPOUND, {
        'type': (TAG_STRING, 'minecraft:overworld'),
        'generator': (TAG_COMPOUND, overworld_gen)
    })

    dest_file = os.path.join(save_dir, "level.dat")
    nbt.save_nbt(dest_file, root_name, root_type, val)
    # Also create level.dat_old
    nbt.save_nbt(os.path.join(save_dir, "level.dat_old"), root_name, root_type, val)
    print(f"[OK] Generated Superflat world at: {save_dir}")

def create_varied_save():
    save_dir = os.path.join(DEST_BASE, "Titan Combat Test Arena (Varied Terrain)")
    os.makedirs(save_dir, exist_ok=True)

    root_name, root_type, val = nbt.load_nbt(TEMPLATE_PATH)
    data = val['Data'][1]

    data['LevelName'] = (TAG_STRING, "Titan Combat Test Arena (Varied Terrain)")
    data['GameType'] = (TAG_INT, 1) # Creative
    data['allowCommands'] = (TAG_BYTE, 1)
    data['hardcore'] = (TAG_BYTE, 0)
    data['Difficulty'] = (TAG_BYTE, 1)
    data['DifficultyLocked'] = (TAG_BYTE, 0)
    data['DayTime'] = (TAG_LONG, 6000)
    data['Time'] = (TAG_LONG, 6000)
    data['raining'] = (TAG_BYTE, 0)
    data['thundering'] = (TAG_BYTE, 0)

    data['DataPacks'] = (TAG_COMPOUND, {
        'Enabled': (TAG_LIST, (TAG_STRING, ['vanilla', 'mod:forge', 'mod:geckolib', 'mod:titancombat'])),
        'Disabled': (TAG_LIST, (TAG_STRING, []))
    })

    gr = data.get('GameRules', (TAG_COMPOUND, {}))[1]
    gr['keepInventory'] = (TAG_STRING, 'true')
    gr['doDaylightCycle'] = (TAG_STRING, 'false')
    gr['doWeatherCycle'] = (TAG_STRING, 'false')

    player = data['Player'][1]
    player['playerGameType'] = (TAG_INT, 1)
    player['Invulnerable'] = (TAG_BYTE, 1)
    player['Health'] = (TAG_FLOAT, 20.0)
    player['foodLevel'] = (TAG_INT, 20)
    player['abilities'] = (TAG_COMPOUND, {
        'flying': (TAG_BYTE, 0),
        'flyingSpeed': (TAG_FLOAT, 0.05),
        'instabuild': (TAG_BYTE, 1),
        'invulnerable': (TAG_BYTE, 1),
        'mayBuild': (TAG_BYTE, 1),
        'mayfly': (TAG_BYTE, 1),
        'walkSpeed': (TAG_FLOAT, 0.1)
    })
    player['Inventory'] = (TAG_LIST, (TAG_COMPOUND, make_inventory()))
    player['SelectedItemSlot'] = (TAG_INT, 0)

    # Standard Vanilla Overworld Noise Generator (mountains, oceans, plains, forests)
    wgen = data['WorldGenSettings'][1]
    wgen['dimensions'][1]['minecraft:overworld'] = (TAG_COMPOUND, {
        'type': (TAG_STRING, 'minecraft:overworld'),
        'generator': (TAG_COMPOUND, {
            'type': (TAG_STRING, 'minecraft:noise'),
            'settings': (TAG_STRING, 'minecraft:overworld'),
            'biome_source': (TAG_COMPOUND, {
                'type': (TAG_STRING, 'minecraft:multi_noise'),
                'preset': (TAG_STRING, 'minecraft:overworld')
            })
        })
    })

    dest_file = os.path.join(save_dir, "level.dat")
    nbt.save_nbt(dest_file, root_name, root_type, val)
    nbt.save_nbt(os.path.join(save_dir, "level.dat_old"), root_name, root_type, val)
    print(f"[OK] Generated Varied Terrain world at: {save_dir}")

if __name__ == "__main__":
    create_superflat_save()
    create_varied_save()
