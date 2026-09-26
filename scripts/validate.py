"""Offline structural checks for the package; not an in-game rendering test."""
import hashlib
import json
import math
import struct
from pathlib import Path
from pack_identity import check_pack_identity
from brightness_lock import check_approved_brightness
import halloween_fog
import leaf_motion
from themes import STYLES, AUTUMN_BIOMES
from water_profiles import PROFILES
from night_sky import SKY_ONLY_BIOMES, EXCLUDED_BIOMES, TEXTURES, FACE_SIZE

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'pack'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f'Duplicate JSON key in {path}: {key}')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

def numeric(value, low, high, label):
    require(type(value) in (int, float) and math.isfinite(value) and low <= value <= high, f'{label}: out of range')

def color(value):
    require(isinstance(value, list) and len(value) == 3, 'RGB must have three components')
    for channel in value:
        numeric(channel, 0, 255, 'RGB')

def frame(value, check):
    if isinstance(value, dict):
        require('0' in value and '1' in value and value['0'] == value['1'], 'Day cycle must wrap without a jump')
        times = [float(k) for k in value]
        require(times == sorted(set(times)) and all(0 <= t <= 1 for t in times), 'Invalid frame times')
        for item in value.values():
            check(item)
    else:
        check(value)

def validate():
    source = load(ROOT / 'reference' / 'source.json')
    for name, digest in source['sha256'].items():
        require(hashlib.sha256((ROOT / 'reference' / name).read_bytes()).hexdigest() == digest, f'Reference changed: {name}')
    sky_source = load(ROOT/'assets'/'night_sky'/'source.json')
    require(sky_source['source']=='source-v2.png','Unexpected selected sky artwork')
    require(set(sky_source['sha256']) == {'source.png', 'source-v2.png', *(f'cubemap_{i}.png' for i in range(6))}, 'Incomplete sky artwork')
    for name, digest in sky_source['sha256'].items():
        require(hashlib.sha256((ROOT/'assets'/'night_sky'/name).read_bytes()).hexdigest()==digest, f'Sky source changed: {name}')
    for i, texture in enumerate(TEXTURES):
        path=PACK/(texture+'.png')
        require(path.is_file(), f'Missing sky face: {texture}')
        raw=path.read_bytes()
        require(hashlib.sha256(raw).hexdigest()==sky_source['sha256'][f'cubemap_{i}.png'],f'Sky face does not match source: {texture}')
        require(raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>IIBB',raw[16:26])==(FACE_SIZE,FACE_SIZE,8,2),'Invalid sky PNG format')
    all_files = {p.relative_to(PACK).as_posix(): load(p) for p in PACK.rglob('*.json')}
    files = {n:v for n,v in all_files.items() if not n.startswith('subpacks/')}
    manifest = files['manifest.json']
    require(manifest['format_version'] == 2 and manifest['capabilities'] == ['pbr'], 'Invalid pack manifest')
    require(manifest['header']['min_engine_version'] == [1,26,50], 'Unexpected engine target')
    check_pack_identity(manifest, 'Quality')
    require(manifest['header']['version'] == manifest['modules'][0]['version'], 'Versions differ')

    expected = [{'folder_name':key,'name':name,'memory_tier':0} for key,name in STYLES]
    require(manifest.get('subpacks') == expected, 'Missing, reordered or gated style choices')
    require(manifest['subpacks'][-1]['folder_name']=='natural', 'Natural must remain the default')
    actual = {n.split('/')[1] for n in all_files if n.startswith('subpacks/')}
    require(actual == {key for key,_ in STYLES}, 'Unknown or missing subpack folder')
    validate_data(files, 'natural')
    folders={'lighting','atmospherics','water','color_grading','local_lighting','biomes','cubemaps'}
    expected_paths={n for n in files if n.split('/')[0] in folders}
    for style,_ in STYLES:
        prefix=f'subpacks/{style}/'
        overlay={n[len(prefix):]:v for n,v in all_files.items() if n.startswith(prefix)}
        extras = halloween_fog.JSON_PATHS if style == 'halloween' else set()
        require(set(overlay)==expected_paths | extras, f'Incomplete or unexpected style resources: {style}')
        if style == 'natural':
            require(overlay == {n:files[n] for n in expected_paths}, 'Natural style must restore base settings')
        validate_data({**files, **overlay},style)
    print(f'PASS: {len(all_files)} JSON files; base plus 4 styles, 83 sky bindings each, 6 cubemap faces, references, ranges, cycles and source hashes.')
    return all_files

def validate_data(files, style):
    identifiers = {}
    kinds = {'lighting':'lighting', 'atmospherics':'atmosphere', 'water':'water', 'color_grading':'color_grading', 'cubemaps':'cubemap'}
    for name, value in files.items():
        folder = name.split('/')[0]
        if folder not in kinds:
            continue
        body = value[f'minecraft:{kinds[folder]}_settings']
        identity = body['description']['identifier']
        require(identity.startswith('lumen:') and identity not in identifiers, 'Duplicate or non-local graphic ID')
        identifiers[identity] = kinds[folder]
        if folder == 'cubemaps':
            require(value['format_version']=='1.21.130','Unsupported cubemap schema')
            lighting=body['lighting']
            require(set(lighting)=={'ambient_light_illuminance','sky_light_contribution','directional_light_contribution','affected_by_atmospheric_scattering','affected_by_volumetric_scattering'}, 'Invalid cubemap fields')
            frame(lighting['ambient_light_illuminance'],lambda x:numeric(x,0,100000,'cubemap lux'))
            for key in ('sky_light_contribution','directional_light_contribution'):
                numeric(lighting[key],0,1,key)
            for key in ('affected_by_atmospheric_scattering','affected_by_volumetric_scattering'):
                require(type(lighting[key]) is bool,'Invalid cubemap scattering flag')
        elif folder == 'water':
            w = body['waves']
            require(set(w) == {'enabled','depth','direction_increment','frequency','frequency_scaling','mix','octaves','pull','sampleWidth','shape','speed','speed_scaling'}, 'Unknown/missing wave field')
            require(w['enabled'] is True and type(w['octaves']) is int, 'Invalid wave mode')
            for field, low, high in [('depth',0,3),('direction_increment',0,360),('frequency',.01,3),('frequency_scaling',0,2),('mix',0,1),('octaves',1,30),('pull',-1,1),('sampleWidth',.01,1),('shape',1,10),('speed',.01,10),('speed_scaling',0,2)]:
                numeric(w[field],low,high,field)
            for field,high in [('cdom',15),('chlorophyll',10),('suspended_sediment',300)]:
                numeric(body['particle_concentrations'][field],0,high,field)
            numeric(body['biome_water_color_contribution'],0,1,'biome color')
            c=body['caustics']
            require(c['enabled'] is True and type(c['power']) is int, 'Invalid caustics')
            for field,low,high in [('power',1,6),('frame_length',.01,5),('scale',.1,5)]:
                numeric(c[field],low,high,field)
        elif folder == 'lighting':
            orbital=body['directional_lights']['orbital']
            for light in ('sun','moon'):
                frame(orbital[light]['color'],color)
                ceiling = 100 if light == 'sun' else .4
                frame(orbital[light]['illuminance'],lambda x:numeric(x,0,ceiling,'Mojang preset illuminance'))
            numeric(body['ambient']['illuminance'],0,5,'ambient')
            numeric(body['sky']['intensity'],.1,1,'sky')
        elif folder == 'atmospherics':
            for field in ('sky_zenith_color','sky_horizon_color'):
                frame(body[field],color)
            for field in ('rayleigh_strength','sun_mie_strength','moon_mie_strength','sun_glare_shape'):
                frame(body[field],lambda x:numeric(x,0,100,'atmosphere'))
        elif folder == 'color_grading':
            require(body['tone_mapping']['operator'] == 'generic','Tone map must use the Mojang Generic preset')
            require(body['color_grading'].get('temperature') == {
                'enabled': True, 'temperature': 6500, 'type': 'color_temperature'},
                'Color temperature must retain the Mojang daylight preset')
            for field, low, high in [('contrast',0,4),('gain',0,10),('gamma',0,4),('offset',-1,1),('saturation',0,10)]:
                channels=body['color_grading']['midtones'][field]
                require(isinstance(channels,list) and len(channels)==3, f'Expected three {field} channels')
                for channel in channels:
                    numeric(channel,low,high,field)
    biome_count = 0
    for name,data in files.items():
        if not name.startswith('biomes/'):
            continue
        biome_count += 1
        body=data['minecraft:client_biome']
        original=load(ROOT/'reference'/'resource_pack'/name)['minecraft:client_biome']
        require(body['description'] == original['description'],f'Biome identity changed: {name}')
        components=body['components']
        changed = {f'minecraft:{k}_identifier' for k in kinds.values()}
        biome_name=body['description']['identifier'].split(':')[-1]
        if biome_name in SKY_ONLY_BIOMES:
            changed={'minecraft:cubemap_identifier'}
        require(tuple(map(int,data['format_version'].split('.'))) >= (1,21,130), f'Cubemap biome schema too old: {name}')
        if style == 'autumn' and biome_name in AUTUMN_BIOMES:
            changed.add('minecraft:foliage_appearance')
            color(components['minecraft:foliage_appearance']['color'])
        require({k:v for k,v in components.items() if k not in changed} == {k:v for k,v in original['components'].items() if k not in changed},f'Non-visual biome data changed: {name}')
        for kind in kinds.values():
            if biome_name in SKY_ONLY_BIOMES and kind != 'cubemap':
                continue
            ref=components[f'minecraft:{kind}_identifier'][f'{kind}_identifier']
            require(identifiers.get(ref) == kind, f'Broken graphic reference in {name}: {ref}')
    require(biome_count == 83, 'Unexpected Overworld biome coverage')
    for forbidden in EXCLUDED_BIOMES:
        require(f'biomes/{forbidden}.client_biome.json' not in files, 'Other dimension overwritten')
    water=[n for n in files if n.startswith('water/')]
    effects=[files[n]['minecraft:water_settings'] for n in water]
    require(set(water)=={f'water/{name}.json' for name in PROFILES},'Missing or unexpected water profile')
    require(all(v['caustics']==effects[0]['caustics'] and v['waves']['enabled']==effects[0]['waves']['enabled'] for v in effects),'Non-blendable water settings differ')
    require(len({v['minecraft:lighting_settings']['directional_lights']['orbital']['orbital_offset_degrees'] for n,v in files.items() if n.startswith('lighting/')}) == 1,'Orbital offsets differ')
    blocks = {'iron_block', 'gold_block', 'copper_block', 'diamond_block'}
    material_paths = {f'textures/blocks/{block}.texture_set.json' for block in blocks}
    require({name for name in files if name.startswith('textures/blocks/')
             and name.endswith('.texture_set.json')} == material_paths,
            'Missing or unexpected block material definitions')
    for name in sorted(material_paths):
        p = PACK / name
        texture=load(p)['minecraft:texture_set']
        require(texture['color'] == p.name.removesuffix('.texture_set.json'),
                f'Unexpected block color reference: {p.name}')
        png=p.parent/(texture['color']+'.png')
        data=png.read_bytes()
        require(data == (ROOT/'reference'/'resource_pack'/'textures'/'blocks'/png.name).read_bytes(),
                f'Block color texture differs from pinned reference: {png.name}')
        require(data[:8]==b'\x89PNG\r\n\x1a\n', 'Invalid PNG')
        width,height,depth,kind=struct.unpack('>IIBB', data[16:26])
        require(width==height and depth==8 and kind in (2,6), 'Invalid RGB/RGBA color texture')
        require(len(texture['metalness_emissive_roughness_subsurface'])==4, 'MERS requires 4 channels')
        for x in texture['metalness_emissive_roughness_subsurface']:
            numeric(x,0,255,'MERS')
    for ref in files['textures/textures_list.json']:
        require((PACK/(ref+'.png')).is_file() or
                (PACK/'subpacks'/style/(ref+'.png')).is_file(), f'Missing texture: {ref}')
    require(set(TEXTURES).issubset(files['textures/textures_list.json']),'Sky faces not registered')
    local=files['local_lighting/local_lighting.json']['minecraft:local_light_settings']
    require(set(local)=={'minecraft:torch','minecraft:lantern','minecraft:soul_torch','minecraft:soul_lantern'},'Unexpected added lights')
    for entry in local.values():
        require(entry['light_type']=='point_light','Unexpected light type')
        require(isinstance(entry['light_color'],str) and len(entry['light_color'])==7 and entry['light_color'].startswith('#'),'Invalid local color')
        int(entry['light_color'][1:],16)
    halloween_fog.validate_resources(files, style, ROOT, PACK)
    leaf_motion.validate_resources(files, ROOT, PACK)
    check_approved_brightness(files, style, ROOT)

if __name__ == '__main__':
    validate()
