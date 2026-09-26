"""Preserve the user-approved 0.4.3 lighting independently of source presets.

This baseline is authored once, not refreshed by generation or validation.
Water motion and Quality/Balanced sampling are deliberately outside the lock.
"""
import hashlib
import json
from pathlib import Path


LOCKED_FOLDERS = ('lighting', 'color_grading', 'atmospherics', 'cubemaps', 'local_lighting')
VISUAL_BINDINGS = {f'minecraft:{kind}_identifier' for kind in
                   ('lighting', 'color_grading', 'atmosphere', 'cubemap', 'water')}


def fingerprints(files):
    """Hash effective style resources, including names but ignoring JSON order."""
    groups = {folder: {} for folder in LOCKED_FOLDERS}
    groups.update(water_optics={}, biome_bindings={}, materials={})
    for name, value in files.items():
        folder = name.split('/')[0]
        if folder in LOCKED_FOLDERS:
            groups[folder][name] = value
        elif folder == 'water':
            groups['water_optics'][name] = {
                **value,
                'minecraft:water_settings': {
                    key: item for key, item in value['minecraft:water_settings'].items()
                    if key != 'waves'
                },
            }
        elif folder == 'biomes':
            groups['biome_bindings'][name] = {
                key: item for key, item in value['minecraft:client_biome']['components'].items()
                if key in VISUAL_BINDINGS
            }
        elif name.endswith('.texture_set.json'):
            groups['materials'][name] = value
    return {
        group: hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':'),
                                        ensure_ascii=True, allow_nan=False).encode('utf-8')).hexdigest()
        for group, values in groups.items()
    }


def check_approved_brightness(files, style, root):
    path = Path(root) / 'reference' / 'approved_brightness.json'
    baseline = json.loads(path.read_text(encoding='utf-8'))
    if baseline.get('schema_version') != 1 or style not in baseline.get('styles', {}):
        raise ValueError(f'Incomplete approved brightness baseline: {style}')
    actual = fingerprints(files)
    expected = baseline['styles'][style]
    changed = sorted(key for key in actual.keys() | expected.keys()
                     if actual.get(key) != expected.get(key))
    if changed:
        raise ValueError(f'Approved brightness changed in {style}: {", ".join(changed)}. '
                         'Preserve the approved values; baseline changes require an explicit user request.')
