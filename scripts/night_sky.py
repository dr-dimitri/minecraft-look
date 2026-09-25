"""Night-only cubemap lighting and committed original sky artwork."""
import shutil

SKY_ONLY_BIOMES = {'pale_garden', 'deep_dark', 'lush_caves', 'dripstone_caves', 'sulfur_caves'}
EXCLUDED_BIOMES = {'hell', 'basalt_deltas', 'crimson_forest', 'warped_forest', 'soulsand_valley', 'the_end'}
TEXTURES = [f'textures/environment/overworld_cubemap/cubemap_{i}' for i in range(6)]
FACE_SIZE = 1024


def settings():
    # Bedrock keyframes: 0/1 = noon, 0.25 = sunset, 0.5 = midnight.
    # Daytime sky/directional contributions are zero so neither sun nor sky
    # relights the galaxy. Atmospheric scattering still supplies daylight haze.
    return {
        'lighting': {
            'ambient_light_illuminance': {
                '0': 0, '0.25': 0, '0.30': 0, '0.34': .02,
                '0.40': .55, '0.45': .8, '0.58': .8,
                '0.64': .4, '0.69': .03, '0.73': 0, '1': 0,
            },
            'sky_light_contribution': 0,
            'directional_light_contribution': 0,
            'affected_by_atmospheric_scattering': True,
            'affected_by_volumetric_scattering': True,
        },
    }


def copy_textures(root, pack):
    source = root / 'assets' / 'night_sky'
    # Build uses committed converted faces; FFmpeg/image generation are not
    # required on a user's machine or in the ordinary release workflow.
    for i, name in enumerate(TEXTURES):
        destination = pack / f'{name}.png'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / f'cubemap_{i}.png', destination)
    return list(TEXTURES)
