"""Verify complete artifact sets and switch readers to them without partial updates."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile


def expected_names(version):
    return {f'Lumen-WQHD-{preset}-{version}.mcpack' for preset in ('Quality', 'Balanced')} | {
        f'Lumen-WQHD-Source-{version}.zip'}


def verify_bundle(directory, version):
    directory = Path(directory)
    expected = expected_names(version)
    if {p.name for p in directory.iterdir()} != expected | {'SHA256SUMS.txt'}:
        raise ValueError('Unexpected or missing release assets')
    checksums = {}
    for line in (directory / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if match is None or match[2] not in expected or match[2] in checksums:
            raise ValueError('Invalid checksum manifest')
        checksums[match[2]] = match[1]
    if set(checksums) != expected:
        raise ValueError('Incomplete checksum manifest')
    for name, digest in checksums.items():
        path = directory / name
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Checksum mismatch: ' + name)
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError('Archive CRC error: ' + name)
    return checksums


def current_bundle(dist):
    dist = Path(dist).resolve()
    pointer = json.loads((dist / 'current.json').read_text(encoding='utf-8'))
    version, digest = pointer['version'], pointer['sha256']
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', version):
        raise ValueError('Invalid current artifact version')
    if not re.fullmatch(r'[0-9a-f]{64}', digest):
        raise ValueError('Invalid current artifact digest')
    directory = dist / version / digest
    if hashlib.sha256((directory / 'SHA256SUMS.txt').read_bytes()).hexdigest() != digest:
        raise ValueError('Current artifact manifest changed')
    verify_bundle(directory, version)
    return directory


def publish_bundle(staged, dist, version):
    """Staged and dist must share a filesystem. Published directories are immutable.

    Only current.json is replaced: failures or concurrent builds never combine
    files from different runs. A crash before the switch may leave an unused,
    complete directory, which is safe to retain. No power-loss durability claim.
    """
    staged, dist = Path(staged), Path(dist).resolve()
    verify_bundle(staged, version)
    digest = hashlib.sha256((staged / 'SHA256SUMS.txt').read_bytes()).hexdigest()
    target = dist / version / digest
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        staged.rename(target)
    except OSError:
        # Identical concurrent/repeated builds can have already installed it.
        if not target.is_dir() or (target / 'SHA256SUMS.txt').read_bytes() != (staged / 'SHA256SUMS.txt').read_bytes():
            raise
        verify_bundle(target, version)
    pointer = {'version': version, 'sha256': digest}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=dist, prefix='.current-', delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(pointer, handle, sort_keys=True)
            handle.write('\n')
        os.replace(temporary, dist / 'current.json')
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return target
