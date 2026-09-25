"""Rebuild the authored pack from pinned biome references and visual settings."""
import json
import shutil
from pathlib import Path
from themes import STYLES, generate
import water_profiles
import night_sky

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'pack'
REF = ROOT / 'reference' / 'resource_pack'
VERSION = [0, 4, 1]

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def settings(folder, name, key, values, version='1.21.80'):
    write(PACK / folder / f'{name}.json', {
        'format_version': version,
        f'minecraft:{key}_settings': {'description': {'identifier': f'lumen:{name}'}, **values},
    })

def curve(values):
    return {str(k): v for k, v in values}

def main():
    # Only generated pack output is replaced. Sources/reference files remain intact.
    if PACK.exists():
        shutil.rmtree(PACK)
    write(PACK / 'manifest.json', {
        'format_version': 2,
        'header': {
            'name': 'Lumen WQHD · Quality',
            'description': 'Galaxienhimmel bei Nacht · Vier Stile am Zahnrad · WQHD / RX 9060 XT · 80 FPS ungemessen · v' + '.'.join(map(str, VERSION)),
            'uuid': '62534bcd-5dc1-47bf-9903-5277eeb54f6a',
            'version': VERSION,
            'min_engine_version': [1, 26, 50],
        },
        'modules': [{'type': 'resources', 'uuid': '6e9469ee-631e-48ba-9f79-29de64b4b2ac', 'version': VERSION}],
        'capabilities': ['pbr'],
        'subpacks': [{'folder_name': key, 'name': name, 'memory_tier': 0} for key,name in STYLES],
    })
    for climate, noon, moon, sky in [
        ('temperate', [255, 250, 244], [221, 230, 242], 1.0),
        ('warm', [255, 247, 237], [226, 232, 242], 1.0),
        ('cold', [247, 250, 255], [219, 231, 245], 1.0),
        ('wet', [250, 251, 247], [221, 233, 241], .98),
    ]:
        settings('lighting', f'light_{climate}', 'lighting', {
            'directional_lights': {'orbital': {
                'sun': {
                    # Lux, not an arbitrary brightness multiplier. Bedrock's
                    # exposure/tone mapper handles the day/night dynamic range.
                    'illuminance': curve([(0,110000),(.08,105000),(.18,52000),(.25,16000),(.30,900),(.35,10),(.42,0),(.58,0),(.65,10),(.70,900),(.75,16000),(.82,52000),(.92,105000),(1,110000)]),
                    'color': curve([(0,noon),(.15,noon),(.25,[255,197,151]),(.35,[255,173,143]),(.65,[255,173,143]),(.75,[255,208,166]),(.85,noon),(1,noon)]),
                },
                'moon': {'illuminance': curve([(0,0),(.20,0),(.30,.20),(.50,.27),(.70,.20),(.80,0),(1,0)]), 'color': moon},
                'orbital_offset_degrees': 8.0,
            }, 'flash': {'illuminance': 10, 'color': [228,93,255]}},
            'emissive': {'desaturation': .08},
            'ambient': {'illuminance': .02, 'color': '#F4F6FA'},
            'sky': {'intensity': sky},
        })
    for climate, zenith, horizon in [
        ('temperate',[105,143,188],[195,208,222]),
        ('warm',[108,146,187],[222,210,192]),
        ('cold',[116,151,190],[207,222,236]),
        ('wet',[109,145,168],[184,207,205]),
    ]:
        values = {
            'horizon_blend_stops': {'min':0, 'start':.55, 'mie_start':.6, 'max':.25},
            'rayleigh_strength': curve([(0,8),(.15,8),(.25,4.5),(.35,4),(.65,4),(.75,4.5),(.85,8),(1,8)]),
            'sun_mie_strength': curve([(0,.04),(.17,.1),(.25,.65),(.32,0),(.68,0),(.75,.6),(.83,.1),(1,.04)]),
            'moon_mie_strength': .015,
            'sun_glare_shape': .065,
            'sky_zenith_color': curve([(0,zenith),(.18,zenith),(.27,[75,93,134]),(.36,[35,43,65]),(.64,[35,43,65]),(.73,[82,107,153]),(.82,zenith),(1,zenith)]),
            'sky_horizon_color': curve([(0,horizon),(.17,horizon),(.25,[238,197,162]),(.34,[107,113,137]),(.42,[65,78,98]),(.60,[65,78,98]),(.68,[140,138,153]),(.75,[240,207,174]),(.83,horizon),(1,horizon)]),
        }
        settings('atmospherics', f'air_{climate}', 'atmosphere', values, '1.21.40')
    settings('color_grading', 'natural', 'color_grading', {
        'color_grading': {
            'midtones': {'contrast':[1.02]*3, 'gain':[1]*3, 'gamma':[2.2]*3, 'offset':[0]*3, 'saturation':[1.0]*3},
        },
        'tone_mapping': {'operator':'aces'},
    }, '1.21.90')
    for name in water_profiles.PROFILES:
        settings('water', name, 'water', water_profiles.settings(name), '1.26.0')
    settings('cubemaps', 'galaxy', 'cubemap', night_sky.settings(), '1.21.130')
    mapping = {}
    for file in sorted((REF / 'biomes').glob('*.json')):
        data = json.loads(file.read_text(encoding='utf-8'))
        body = data['minecraft:client_biome']
        name = body['description']['identifier'].split(':')[-1]
        if name in night_sky.EXCLUDED_BIOMES:
            continue
        # The cubemap component requires >=1.21.130, unlike old biome inputs.
        if tuple(map(int, data['format_version'].split('.'))) < (1,21,130):
            data['format_version'] = '1.21.130'
        body['components']['minecraft:cubemap_identifier'] = {'cubemap_identifier':'lumen:galaxy'}
        if name in night_sky.SKY_ONLY_BIOMES:
            # Keep native cave/Pale Garden lighting, fog and water. Explicitly
            # assign night fading here too, so the shared sky textures do not
            # fall back to all-day default cubemap illumination in these biomes.
            write(PACK / 'biomes' / file.name, data)
            mapping[name] = {'climate':'vanilla', 'water':'vanilla', 'sky':'galaxy'}
            continue
        climate = 'temperate'
        if name == 'grove' or any(s in name for s in ('cold','frozen','ice_','snow','jagged')):
            climate = 'cold'
        elif any(s in name for s in ('desert','mesa','savanna')):
            climate = 'warm'
        elif any(s in name for s in ('jungle','swamp')):
            climate = 'wet'
        water = water_profiles.for_biome(name, climate)
        for key, value in [('lighting',f'light_{climate}'),('atmosphere',f'air_{climate}'),('color_grading','natural'),('water',water)]:
            body['components'][f'minecraft:{key}_identifier'] = {f'{key}_identifier':f'lumen:{value}'}
        write(PACK / 'biomes' / file.name, data)
        mapping[name] = {'climate':climate, 'water':water, 'sky':'galaxy'}
    write(ROOT / 'docs' / 'biome-map.json', mapping)
    write(PACK / 'local_lighting' / 'local_lighting.json', {
        'format_version':'1.21.120',
        'minecraft:local_light_settings': {
            f'minecraft:{block}': {'light_color':color, 'light_type':'point_light'}
            for block, color in [('torch','#FFD2A0'),('lantern','#FFD2A0'),('soul_torch','#8FDDEB'),('soul_lantern','#8FDDEB')]
        },
    })
    texture_names = []
    # Solid metals use binary metalness; diamond remains a dielectric.
    # Moderate roughness keeps metal from behaving like a perfect mirror.
    for block, metal, roughness in [('iron_block',255,100),('gold_block',255,72),('copper_block',255,116),('diamond_block',0,64)]:
        folder = PACK / 'textures' / 'blocks'
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REF / 'textures' / 'blocks' / f'{block}.png', folder / f'{block}.png')
        write(folder / f'{block}.texture_set.json', {
            'format_version':'1.21.30',
            'minecraft:texture_set': {'color':block, 'metalness_emissive_roughness_subsurface':[metal,0,roughness,0]},
        })
        texture_names.append(f'textures/blocks/{block}')
    texture_names.extend(night_sky.copy_textures(ROOT, PACK))
    write(PACK / 'textures' / 'textures_list.json', texture_names)
    shutil.copyfile(ROOT / 'NOTICE.md', PACK / 'NOTICE.md')
    generate(PACK, write)
    print(f'Generated pack: {len(mapping)} Overworld sky bindings, 78 full visual biomes, {len(water_profiles.PROFILES)} water profiles, 4 styles.')

if __name__ == '__main__':
    main()
