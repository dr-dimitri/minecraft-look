"""Select portable project sources, excluding local environments and scratch files."""
import os
from pathlib import Path

ROOT_FILES = {'.gitattributes', '.gitignore', 'AGENTS.md', 'CHANGELOG.md', 'LICENSE', 'NOTICE.md', 'README.md'}
SOURCE_DIRS = {
    '.agents': {'.md', '.yaml', '.yml'},
    '.github': {'.md', '.yaml', '.yml'},
    'assets': {'.png', '.json', '.md'},
    'docs': {'.md', '.json', '.csv', '.svg', '.png'},
    'pack': {'.json', '.png', '.md'},
    'reference': {'.json', '.png', '.tga', '.md'},
    'scripts': {'.py'},
    'tests': {'.py'},
}
LOCAL_DIRS = {'__pycache__', 'node_modules', 'dist', 'venv'}


def source_entries(root, *, include_generated=True):
    """Work in both a checkout and an extracted source ZIP; Git is not required.

    Only declared project folders/file types belong in a distribution. This is
    not a secret scanner: maintainers must still review authored project files.
    Never follow symlinks, which can pull unrelated files into an archive.
    """
    root = Path(root)
    entries = {}

    def include(path):
        if path.is_symlink():
            raise ValueError(f'Source archive must not follow symlinks: {path}')
        if path.is_file():
            entries['lumen-bedrock/' + path.relative_to(root).as_posix()] = path.read_bytes()

    for name in sorted(ROOT_FILES):
        include(root / name)
    for folder, suffixes in SOURCE_DIRS.items():
        if folder == 'pack' and not include_generated:
            continue
        directory = root / folder
        if directory.is_symlink():
            raise ValueError(f'Source archive must not follow symlinks: {directory}')
        if not directory.exists():
            continue
        def fail(error):
            raise error

        for current, directories, filenames in os.walk(directory, followlinks=False, onerror=fail):
            directories[:] = sorted(name for name in directories
                                    if not name.startswith('.') and name not in LOCAL_DIRS)
            for name in directories:
                path = Path(current) / name
                if path.is_symlink():
                    raise ValueError(f'Source archive must not follow symlinks: {path}')
            for name in sorted(filenames):
                if not include_generated and Path(current) / name == root / 'docs/biome-map.json':
                    continue
                if not name.startswith('.') and Path(name).suffix in suffixes:
                    include(Path(current) / name)
    return entries
