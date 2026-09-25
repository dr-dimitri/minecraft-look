"""Create reproducible MCPACKs and a GitHub-ready source ZIP. Python 3.10+."""
import hashlib
import json
import runpy
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from validate import require, ROOT
from check_release import read_manifest, source_version
from source_archive import source_entries
from artifacts import publish_bundle

def archive(path, entries):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,9,25,0,0,0))
            info.create_system=3
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            z.writestr(info,data)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('Archive CRC error')

def run_python(root, script):
    command = [sys.executable, '-B']
    if sys.flags.optimize:
        command.append('-O')
    subprocess.run([*command, str(root / script)], cwd=root, check=True)


def stage_archives(root, dist):
    profiles = runpy.run_path(str(root / 'scripts/water_profiles.py'))
    quality, balanced = profiles['QUALITY'], profiles['BALANCED']
    pack = root / 'pack'
    read_manifest(pack / 'manifest.json', source_version(root / 'scripts/create_pack.py'))
    source = source_entries(root)
    dist.mkdir()
    base = {p.relative_to(pack).as_posix(): p.read_bytes() for p in pack.rglob('*') if p.is_file()}
    version=json.loads(base['manifest.json'])['header']['version']
    version_text='.'.join(map(str,version))
    outputs=[]
    for preset in ('Quality','Balanced'):
        files=dict(base)
        manifest=json.loads(files['manifest.json'])
        if preset=='Balanced':
            manifest['header']['name']='Lumen WQHD · Balanced'
            manifest['header']['uuid']='4813d437-9f63-49c3-8089-5c683d4da180'
            manifest['modules'][0]['uuid']='b849e35b-dcc4-460c-8f87-33b22070b38e'
            for name in files:
                if Path(name).parent.name == 'water' and name.endswith('.json'):
                    data=json.loads(files[name])
                    data['minecraft:water_settings']['waves'].update(balanced)
                    files[name]=(json.dumps(data,indent=2)+'\n').encode()
        files['manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
        target=dist/f'Lumen-WQHD-{preset}-{version_text}.mcpack'
        archive(target,files)
        with zipfile.ZipFile(target) as z:
            require('manifest.json' in z.namelist() and not any(n.startswith('pack/') for n in z.namelist()),
                    'Installer must contain its manifest at the archive root')
            expected=quality if preset=='Quality' else balanced
            require(all(all(json.loads(z.read(n))['minecraft:water_settings']['waves'][key]==value for key,value in expected.items()) for n in z.namelist() if Path(n).parent.name == 'water' and n.endswith('.json')),
                    f'Unexpected wave budget in {preset} installer')
        outputs.append(target)
    target=dist/f'Lumen-WQHD-Source-{version_text}.zip'
    archive(target,source)
    outputs.append(target)
    (dist/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in outputs),encoding='utf-8', newline='\n')
    for p in outputs:
        print(f'{p.name}: {p.stat().st_size:,} bytes')
    return version_text

def main(root=None):
    root = (Path(root) if root is not None else ROOT).resolve()
    # Snapshot authored files before generating anything; never overwrite local
    # pack edits or allow them to become the authority for an installer.
    inputs = source_entries(root, include_generated=False)
    with tempfile.TemporaryDirectory(prefix='.lumen-build-', dir=root) as directory:
        workspace = Path(directory)
        snapshot = workspace / 'source'
        for name, data in inputs.items():
            target = snapshot / name.removeprefix('lumen-bedrock/')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        run_python(snapshot, 'scripts/create_pack.py')
        run_python(snapshot, 'scripts/validate.py')
        staged = workspace / 'artifacts'
        version = stage_archives(snapshot, staged)
        published = publish_bundle(staged, root / 'dist', version)
    print(f'Complete artifact set: {published}')
    return published


if __name__=='__main__':
    main()
