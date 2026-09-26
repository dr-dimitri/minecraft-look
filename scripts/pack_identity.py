"""Keep released resource-pack identities stable across updates."""

# These identify the already released packs, independently of the generator.
# Changing them would create a different pack instead of updating installations.
RELEASED_IDENTITIES = {
    'Quality': (
        '62534bcd-5dc1-47bf-9903-5277eeb54f6a',
        '6e9469ee-631e-48ba-9f79-29de64b4b2ac',
    ),
    'Balanced': (
        '4813d437-9f63-49c3-8089-5c683d4da180',
        'b849e35b-dcc4-460c-8f87-33b22070b38e',
    ),
}


def check_pack_identity(manifest, variant='Quality'):
    """Reject changed identities even if the replacement UUIDs are valid."""
    if variant not in RELEASED_IDENTITIES:
        raise ValueError(f'Unknown pack variant: {variant}')
    header_id, module_id = RELEASED_IDENTITIES[variant]
    if not isinstance(manifest, dict):
        raise ValueError(f'{variant}: invalid pack manifest')
    header = manifest.get('header')
    if not isinstance(header, dict) or header.get('uuid') != header_id:
        raise ValueError(f'{variant}: header UUID differs from released pack identity')
    modules = manifest.get('modules')
    if (not isinstance(modules, list) or len(modules) != 1
            or not isinstance(modules[0], dict)
            or modules[0].get('type') != 'resources'):
        raise ValueError(f'{variant}: expected the single released resource module')
    if modules[0].get('uuid') != module_id:
        raise ValueError(f'{variant}: module UUID differs from released pack identity')
