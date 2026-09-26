"""Selectable, cosmetic subpacks using the stable manifest-v2 format."""
import copy
import json

# Equal memory cost: the last eligible entry is the documented default.
# These tiers are deliberately not used to gate artistic styles by hardware.
STYLES = [('mysterious', 'Geheimnisvoll'), ('autumn', 'Herbst'),
          ('halloween', 'Halloween'), ('natural', 'Natürlich')]

AUTUMN_BIOMES = {
    'plains', 'sunflower_plains', 'forest', 'forest_hills', 'flower_forest',
    'birch_forest', 'birch_forest_hills', 'birch_forest_mutated',
    'birch_forest_hills_mutated', 'roofed_forest', 'roofed_forest_mutated',
    'meadow', 'dappled_forest', 'extreme_hills_plus_trees',
    'extreme_hills_plus_trees_mutated',
}

PALETTES = {
    'mysterious': {
        'sun': [171,211,231], 'moon': [143,209,232],
        'zenith': [76,116,155], 'horizon': [116,166,177],
        'sun_strength': .82, 'moon_strength': 1.05, 'sky': .90,
        'ambient': '#B6D6E4', 'torch': '#EBCBAA', 'soul': '#81DEE5',
        'contrast': 1.035, 'saturation': .94, 'gain': [.985,1.0,1.015],
    },
    'autumn': {
        'sun': [255,204,141], 'moon': [209,207,244],
        'zenith': [140,158,180], 'horizon': [240,190,139],
        'sun_strength': 1.0, 'moon_strength': 1.0, 'sky': .97,
        'ambient': '#EEE3D8', 'torch': '#FFD0A0', 'soul': '#9BD7E4',
        'contrast': 1.025, 'saturation': 1.015, 'gain': [1.015,1.0,.99],
    },
    'halloween': {
        'sun': [244,166,104], 'moon': [183,153,236],
        'zenith': [94,79,128], 'horizon': [198,127,113],
        'sun_strength': .72, 'moon_strength': 1.08, 'sky': .86,
        'ambient': '#D1C0E8', 'torch': '#FFB76D', 'soul': '#BC92F0',
        'contrast': 1.045, 'saturation': .98, 'gain': [1.015,.98,1.015],
    },
}


def map_curve(value, transform):
    return {k: transform(v) for k,v in value.items()} if isinstance(value,dict) else transform(value)


def blend(color, target, amount):
    return [round(a*(1-amount)+b*amount) for a,b in zip(color,target)]


def transform(relative, original, style):
    value = copy.deepcopy(original)
    if style == 'natural':
        return value
    p = PALETTES[style]
    folder = relative.split('/')[0]
    if folder == 'lighting':
        light = value['minecraft:lighting_settings']
        orbit = light['directional_lights']['orbital']
        orbit['sun']['color'] = map_curve(orbit['sun']['color'],lambda c:blend(c,p['sun'],.24))
        orbit['moon']['color'] = p['moon']
        for key in ('sun','moon'):
            orbit[key]['illuminance'] = map_curve(orbit[key]['illuminance'],lambda x:round(x*p[key+'_strength'],5))
        light['sky']['intensity'] = round(light['sky']['intensity']*p['sky'],4)
        light['ambient'] = {'illuminance': light['ambient']['illuminance'], 'color': p['ambient']}
    elif folder == 'cubemaps':
        lighting = value['minecraft:cubemap_settings']['lighting']
        strength = {'mysterious':1.2, 'autumn':.85, 'halloween':1.1}[style]
        lighting['ambient_light_illuminance'] = map_curve(
            lighting['ambient_light_illuminance'], lambda x:round(x*strength,5))
    elif folder == 'atmospherics':
        air = value['minecraft:atmosphere_settings']
        # Multiplicative tint retains dark night frames and matching cycle ends.
        for key,target in [('sky_zenith_color',p['zenith']),('sky_horizon_color',p['horizon'])]:
            air[key] = map_curve(air[key],lambda c:[round(min(255,max(0,v*(.65+.35*t/180)))) for v,t in zip(c,target)])
    elif folder == 'color_grading':
        grading = value['minecraft:color_grading_settings']['color_grading']['midtones']
        grading['contrast'] = [p['contrast']]*3
        grading['saturation'] = [p['saturation']]*3
        # Palette gains are relative tints, preserving the shared brightness
        # correction when switching away from the natural style.
        grading['gain'] = [round(base*tint,5) for base,tint in zip(grading['gain'],p['gain'])]
    # All themes share the same water optics. Lighting creates the mood without
    # adding an artificial algae/CDOM filter to clear lakes and tropical water.
    elif folder == 'local_lighting':
        for block,entry in value['minecraft:local_light_settings'].items():
            entry['light_color'] = p['soul'] if 'soul_' in block else p['torch']
    elif folder == 'biomes' and style == 'autumn':
        biome = value['minecraft:client_biome']
        name = biome['description']['identifier'].split(':')[-1]
        if name in AUTUMN_BIOMES:
            # Only foliage that follows the biome tint is affected. Fixed-color
            # leaves (and other packs' texture overrides) may retain their color.
            tint = [215,178,73] if 'birch' in name else [191,132,63]
            biome['components']['minecraft:foliage_appearance'] = {'color':tint}
    return value


def generate(pack, write):
    folders = {'lighting','atmospherics','water','color_grading','local_lighting','biomes','cubemaps'}
    base = {p.relative_to(pack).as_posix():json.loads(p.read_text(encoding='utf-8'))
            for p in pack.rglob('*.json') if p.relative_to(pack).parts[0] in folders}
    for style,_ in STYLES:
        for relative,value in base.items():
            write(pack/'subpacks'/style/relative,transform(relative,value,style))
