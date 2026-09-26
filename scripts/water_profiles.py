"""Authored water optics, not measured samples or a fluid simulation.

Concentrations use Bedrock's mg/L fields. Water color comes from the engine's
absorption/scattering model; the legacy biome color is deliberately not added.
"""
from copy import deepcopy

# CDOM, chlorophyll, sediment, wave depth, base frequency, speed, crest shape.
PROFILES = {
    'lake':        (.080, .015, .035, .100, .50, .55, 1.10),
    'clear_lake':  (.035, .008, .015, .075, .55, .45, 1.06),
    'river':       (.350, .070, .350, .080, .65, .70, 1.12),
    'coastal':     (.075, .035, .150, .140, .40, .60, 1.12),
    'ocean':       (.035, .025, .025, .180, .30, .65, 1.14),
    'cold_ocean':  (.025, .020, .025, .160, .32, .55, 1.12),
    'tropical':   (.008, .007, .015, .130, .40, .58, 1.10),
    'swamp':      (1.600, .450, 1.200, .045, .48, .30, 1.04),
}

# Requested approximation of 10% darker water, not a screen-luminance scale.
# Increase absorbing constituents modestly; leave sediment/scattering alone.
# The actual attenuation depends on wavelength, depth and illumination.
ABSORPTION_SCALE = 1.10

# All biomes must share these non-blendable parameters. Use the engine's
# built-in 64-frame animation; moderate power avoids an exaggerated pool look.
CAUSTICS = {'enabled': True, 'frame_length': .09, 'power': 1, 'scale': .5}
QUALITY = {'octaves': 16, 'sampleWidth': .055}
BALANCED = {'octaves': 8, 'sampleWidth': .11}


def settings(name):
    cdom, chlorophyll, sediment, depth, frequency, speed, shape = PROFILES[name]
    return {
        'particle_concentrations': {
            'cdom': round(cdom * ABSORPTION_SCALE, 6),
            'chlorophyll': round(chlorophyll * ABSORPTION_SCALE, 6),
            'suspended_sediment': sediment,
        },
        'waves': {
            'enabled': True, 'depth': depth,
            # An irrational turn avoids the repeated five-heading pattern of 72°.
            'direction_increment': 137.507764,
            # Shallow, nearly sinusoidal ripples; fine octaves stay close in
            # frequency and speed instead of forming sharp, fast small crests.
            'frequency': frequency, 'frequency_scaling': 1.16,
            'mix': .20, **QUALITY, 'pull': .10, 'shape': shape,
            'speed': speed, 'speed_scaling': 1.01,
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
