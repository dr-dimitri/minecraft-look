"""Authored water optics, not measured samples or a fluid simulation.

Concentrations use Bedrock's mg/L fields. Water color comes from the engine's
absorption/scattering model; the legacy biome color is deliberately not added.
"""
from copy import deepcopy

# CDOM, chlorophyll, sediment, wave depth, base frequency, speed, crest shape.
PROFILES = {
    'lake':        (.080, .015, .035, .120, .36, .32, 1.18),
    'clear_lake':  (.035, .008, .015, .065, .40, .26, 1.12),
    'river':       (.350, .070, .350, .095, .56, .72, 1.22),
    'coastal':     (.075, .035, .150, .200, .32, .50, 1.28),
    'ocean':       (.035, .025, .025, .340, .19, .56, 1.35),
    'cold_ocean':  (.025, .020, .025, .300, .21, .48, 1.30),
    'tropical':   (.008, .007, .015, .200, .26, .50, 1.25),
    'swamp':      (1.600, .450, 1.200, .045, .45, .19, 1.10),
}

# All biomes must share these non-blendable parameters. Use the engine's
# built-in 64-frame animation; moderate power avoids an exaggerated pool look.
CAUSTICS = {'enabled': True, 'frame_length': .09, 'power': 1, 'scale': .5}
QUALITY = {'octaves': 16, 'sampleWidth': .055}
BALANCED = {'octaves': 8, 'sampleWidth': .11}


def settings(name):
    cdom, chlorophyll, sediment, depth, frequency, speed, shape = PROFILES[name]
    return {
        'particle_concentrations': {
            'cdom': cdom, 'chlorophyll': chlorophyll, 'suspended_sediment': sediment,
        },
        'waves': {
            'enabled': True, 'depth': depth,
            # An irrational turn avoids the repeated five-heading pattern of 72°.
            'direction_increment': 137.507764,
            'frequency': frequency, 'frequency_scaling': 1.22,
            'mix': .20, **QUALITY, 'pull': .22, 'shape': shape,
            'speed': speed, 'speed_scaling': 1.025,
        },
        'caustics': deepcopy(CAUSTICS),
        'biome_water_color_contribution': 0.0,
    }


def for_biome(name, climate):
    if 'swamp' in name:
        return 'swamp'
    if name == 'frozen_river':
        return 'clear_lake'
    if name == 'river':
        return 'river'
    # Explicit warm names: "lukewarm_ocean" must not match "warm_ocean".
    if name in {'warm_ocean', 'deep_warm_ocean'}:
        return 'tropical'
    if 'ocean' in name:
        return 'cold_ocean' if 'cold' in name or 'frozen' in name else 'ocean'
    if name == 'cold_beach':
        return 'cold_ocean'
    if name in {'beach', 'stone_beach', 'mushroom_island_shore'}:
        return 'coastal'
    return 'clear_lake' if climate == 'cold' else 'lake'
