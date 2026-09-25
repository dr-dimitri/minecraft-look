"""Optional asset-format conversion: equirectangular PNG to six cube faces.

Requires FFmpeg with v360. No creative retouching: projection and face export
only. Normal builds copy the committed output and do not require FFmpeg.
"""
import hashlib
import json
import subprocess
from pathlib import Path
from night_sky import FACE_SIZE

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'night_sky'


def main():
    # Bedrock ordering: four sides, zenith, nadir. FFmpeg f/r/b/l/u/d faces.
    # See source/format notes in docs/NIGHT_SKY.md; orientation still needs an
    # in-engine check. All faces come from one spherical projection.
    for index in range(6):
        projection = (
            f'v360=input=e:output=c6x1:out_forder=frblud:out_frot=000000:'
            f'w={6*FACE_SIZE}:h={FACE_SIZE}:interp=lanczos,'
            f'crop={FACE_SIZE}:{FACE_SIZE}:{index*FACE_SIZE}:0,format=rgb24'
        )
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-i', str(ASSETS / 'source-v2.png'), '-vf', projection,
            '-frames:v', '1', '-threads', '1', '-update', '1',
            str(ASSETS / f'cubemap_{index}.png'),
        ], check=True)
    manifest = {
        'generator': 'Built-in image_gen; original image, no Oblivion assets',
        'source': 'source-v2.png',
        'conversion': 'FFmpeg v360 equirectangular to cubemap; frblud, 000000',
        'face_size': FACE_SIZE,
        'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(ASSETS.glob('*.png'))},
    }
    (ASSETS / 'source.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print('Exported 6 cubemap faces and asset checksums')


if __name__ == '__main__':
    main()
