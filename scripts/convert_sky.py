"""Optional asset-format conversion: equirectangular PNG to six cube faces.

Requires FFmpeg with v360. No creative retouching: projection and face export
only. Normal builds copy the committed output and do not require FFmpeg.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import zlib
from night_sky import FACE_SIZE

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets' / 'night_sky'
SOURCE_NAMES = ('source.png', 'source-v2.png')
FACE_NAMES = tuple(f'cubemap_{index}.png' for index in range(6))


class SkyRecoveryError(RuntimeError):
    """Installation and rollback failed; retain original bytes for recovery."""

    def __init__(self, backup, names):
        self.backup = backup
        super().__init__(f'Sky rollback failed for {names}; original files retained in {backup}')


def validate_face(path):
    """Reject missing, truncated or malformed output before touching old faces."""
    raw = path.read_bytes()
    if (len(raw) < 33 or raw[:8] != b'\x89PNG\r\n\x1a\n'
            or raw[12:16] != b'IHDR'
            or struct.unpack('>IIBB', raw[16:26]) != (FACE_SIZE, FACE_SIZE, 8, 2)):
        raise ValueError(f'Invalid exported sky PNG: {path.name}')
    offset = 8
    has_image_data = False
    while offset + 12 <= len(raw):
        length = struct.unpack('>I', raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            break
        kind_and_data = raw[offset + 4:end - 4]
        if zlib.crc32(kind_and_data) != struct.unpack('>I', raw[end - 4:end])[0]:
            raise ValueError(f'PNG chunk CRC error: {path.name}')
        kind = kind_and_data[:4]
        has_image_data |= kind == b'IDAT' and length > 0
        if kind == b'IEND':
            if length == 0 and end == len(raw) and has_image_data:
                return
            break
        offset = end
    raise ValueError(f'Incomplete exported sky PNG: {path.name}')


def install_outputs(staged, assets):
    """Rollback completed file replacements if installation raises an error.

    This protects ordinary write errors/interrupts, not power loss or SIGKILL.
    Conversion failures occur earlier, before any original file is touched.
    """
    names = (*FACE_NAMES, 'source.json')
    backups = staged / 'backup'
    backups.mkdir()
    for name in names:
        current = assets / name
        if current.is_symlink():
            raise ValueError(f'Sky output must not be a symlink: {name}')
        if current.exists():
            shutil.copyfile(current, backups / name)
    attempted = []
    try:
        for name in names:
            attempted.append(name)
            os.replace(staged / name, assets / name)
    except BaseException as error:
        failed = []
        for name in reversed(attempted):
            backup = backups / name
            try:
                if backup.exists():
                    os.replace(backup, assets / name)
                else:
                    (assets / name).unlink(missing_ok=True)
            except OSError:
                failed.append(name)
        if failed:
            raise SkyRecoveryError(backups, failed) from error
        raise


def main():
    # Freeze the two selected artworks; local previews must never enter the
    # manifest's exact input set. Missing inputs fail before the first export.
    sources = {name: (ASSETS / name).read_bytes() for name in SOURCE_NAMES}
    staged = Path(tempfile.mkdtemp(prefix='.sky-export-', dir=ASSETS))
    preserve_backup = False
    try:
        for name, raw in sources.items():
            (staged / name).write_bytes(raw)
        # Bedrock ordering: four sides, zenith, nadir. FFmpeg f/r/b/l/u/d faces.
        # Orientation still needs an in-engine check.
        for index, name in enumerate(FACE_NAMES):
            projection = (
                f'v360=input=e:output=c6x1:out_forder=frblud:out_frot=000000:'
                f'w={6*FACE_SIZE}:h={FACE_SIZE}:interp=lanczos,'
                f'crop={FACE_SIZE}:{FACE_SIZE}:{index*FACE_SIZE}:0,format=rgb24'
            )
            subprocess.run([
                'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                '-i', str(staged / 'source-v2.png'), '-vf', projection,
                '-frames:v', '1', '-threads', '1', '-update', '1',
                str(staged / name),
            ], check=True)
            validate_face(staged / name)
        manifest = {
            'generator': 'Built-in image_gen; original image, no Oblivion assets',
            'source': 'source-v2.png',
            'conversion': 'FFmpeg v360 equirectangular to cubemap; frblud, 000000',
            'face_size': FACE_SIZE,
            'sha256': {name: hashlib.sha256((staged / name).read_bytes()).hexdigest()
                       for name in sorted((*SOURCE_NAMES, *FACE_NAMES))},
        }
        (staged / 'source.json').write_text(json.dumps(manifest, indent=2) + '\n',
                                          encoding='utf-8', newline='\n')
        if any((ASSETS / name).read_bytes() != raw for name, raw in sources.items()):
            raise ValueError('Sky artwork changed during conversion; retry with stable inputs')
        install_outputs(staged, ASSETS)
    except SkyRecoveryError:
        preserve_backup = True
        raise
    finally:
        if not preserve_backup:
            shutil.rmtree(staged)
    print('Exported 6 cubemap faces and asset checksums')


if __name__ == '__main__':
    main()
