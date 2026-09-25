"""Verify a full repeat build and an independent rebuild of the distributed source."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import sys
import tempfile
import zipfile
import zlib

import build
from artifacts import current_bundle, verify_bundle
from check_release import source_version


def compare_bundles(expected, actual, version):
    if verify_bundle(expected, version) != verify_bundle(actual, version):
        raise ValueError('Rebuilt archives differ from the original build')
    if (expected / 'SHA256SUMS.txt').read_bytes() != (actual / 'SHA256SUMS.txt').read_bytes():
        raise ValueError('Rebuilt checksum manifest differs')


def extract_source(path, destination):
    with zipfile.ZipFile(path) as archive:
        seen = set()
        for entry in archive.infolist():
            parts = PurePosixPath(entry.filename).parts
            if (not parts or parts[0] != 'lumen-bedrock' or len(parts) < 2
                    or any(part in ('.', '..') for part in entry.filename.split('/'))
                    or '\\' in entry.filename or ':' in entry.filename
                    or entry.filename in seen or entry.is_dir()
                    or (entry.external_attr >> 16) & 0o170000 == 0o120000):
                raise ValueError('Invalid source archive member: ' + entry.filename)
            seen.add(entry.filename)
        if archive.testzip() is not None:
            raise ValueError('Source archive CRC error')
        archive.extractall(destination)
    return destination / 'lumen-bedrock'


def verify(root=build.ROOT):
    root = Path(root)
    version = '.'.join(map(str, source_version(root / 'scripts/create_pack.py')))
    print(f'Runtime: Python {sys.version.split()[0]}, zlib {zlib.ZLIB_RUNTIME_VERSION}')
    first = build.main(root)
    # Capture original digests, including the manifest, to detect unexpected
    # mutation even when a repeated build reuses the same content directory.
    original = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in first.iterdir()}
    second = build.main(root)
    compare_bundles(first, second, version)
    if original != {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in first.iterdir()}:
        raise ValueError('Original build was modified during verification')
    with tempfile.TemporaryDirectory(prefix='lumen-source-check-') as directory:
        extracted = extract_source(first / f'Lumen-WQHD-Source-{version}.zip', Path(directory))
        # Invoke the extracted scripts in their own interpreter and cwd. They
        # must work without Git or imports from this checkout.
        build.run_python(extracted, 'scripts/build.py')
        compare_bundles(first, current_bundle(extracted / 'dist'), version)
    print('PASS: full repeat build and independent source rebuild are byte-identical')
    return first


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--github-output', type=Path, help='Append the verified artifact path to this Actions output file')
    args = parser.parse_args()
    directory = verify()
    if args.github_output:
        with args.github_output.open('a', encoding='utf-8', newline='\n') as handle:
            handle.write(f'path={directory.relative_to(build.ROOT).as_posix()}\n')


if __name__ == '__main__':
    main()
