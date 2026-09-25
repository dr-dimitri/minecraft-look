"""Create reproducible MCPACKs and a GitHub-ready source ZIP. Python 3.10+."""
import hashlib
import json
import zipfile
from pathlib import Path
from validate import validate, require, ROOT, PACK
from water_profiles import QUALITY, BALANCED
from check_release import read_manifest, source_version
from source_archive import source_entries

def archive(path, entries):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,9,25,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644 << 16
            z.writestr(info,data)
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise ValueError('Archive CRC error')

def main():
    validate()
    read_manifest(PACK/'manifest.json', source_version(ROOT/'scripts/create_pack.py'))
    # Inspect source inputs before writing any artifacts, including symlink checks.
    source = source_entries(ROOT)
    dist=ROOT/'dist'
    dist.mkdir(exist_ok=True)
    base={p.relative_to(PACK).as_posix():p.read_bytes() for p in PACK.rglob('*') if p.is_file()}
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
                    data['minecraft:water_settings']['waves'].update(BALANCED)
                    files[name]=(json.dumps(data,indent=2)+'\n').encode()
        files['manifest.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode()
        target=dist/f'Lumen-WQHD-{preset}-{version_text}.mcpack'
        archive(target,files)
        with zipfile.ZipFile(target) as z:
            require('manifest.json' in z.namelist() and not any(n.startswith('pack/') for n in z.namelist()),
                    'Installer must contain its manifest at the archive root')
            expected=QUALITY if preset=='Quality' else BALANCED
            require(all(all(json.loads(z.read(n))['minecraft:water_settings']['waves'][key]==value for key,value in expected.items()) for n in z.namelist() if Path(n).parent.name == 'water' and n.endswith('.json')),
                    f'Unexpected wave budget in {preset} installer')
        outputs.append(target)
    target=dist/f'Lumen-WQHD-Source-{version_text}.zip'
    archive(target,source)
    outputs.append(target)
    (dist/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in outputs),encoding='utf-8')
    for p in outputs:
        print(f'{p.name}: {p.stat().st_size:,} bytes')

if __name__=='__main__':
    main()
