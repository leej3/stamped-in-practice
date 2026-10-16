"""Check scientific identity and denominator invariants of the frozen figures."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import nibabel as nib
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'experiments/narps-poster/map-inputs'
FIGURES = ROOT / 'experiments/narps-poster/figures'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope='module')
def snapshot():
    meta = json.loads((DATA / 'spatial/provenance.json').read_text())
    assert sha(DATA / 'spatial/spatial-inputs.npz') == meta['npz_sha256']
    return meta, np.load(DATA / 'spatial/spatial-inputs.npz', allow_pickle=False)


def test_original_identities_and_retained_source_hashes(snapshot):
    meta, _ = snapshot
    assert len(meta['records']) == 48
    for row in meta['records']:
        folder = DATA / 'spatial/sources' / row['run']
        assert sha(folder / 'capture-manifest.json') == row['capture_sha256']
        assert sha(folder / 'worker-end-state.json') == row['end_state_sha256']
        assert sha(folder / 'condition-assignment.json') == row['condition_assignment_sha256']
        assert sha(folder / 'stop-validation.json') == row['stop_validation_sha256']
        manifest = json.loads((folder / 'capture-manifest.json').read_text())
        assert manifest['capture_status'] == 'complete'
        entries = {e['path']: e for e in manifest['entries']}
        for source in meta['source_files'].values():
            if source['run'] != row['run']:
                continue
            assert entries['content/workspace/' + source['path']]['sha256'] == source['sha256']
            retained = folder / 'workspace' / source['path']
            if retained.exists():
                assert sha(retained) == source['sha256']


def test_all_deliveries_preserve_decisions_and_shared_denominators(snapshot):
    meta, data = snapshot
    support, positive, shared = data['native_masks'], data['native_positive'], data['shared_support']
    assert support.shape == positive.shape == (48, 97, 115, 81)
    assert np.array_equal(shared, support.all(axis=0))
    assert int(shared.sum()) == 168285
    assert not np.any(positive & ~support)
    assert positive.sum(axis=(1, 2, 3)).tolist() == [r['expected_native_positive_voxels'] for r in meta['records']]
    for condition in meta['conditions']:
        ids = [i for i, r in enumerate(meta['records']) if r['condition'] == condition['id']]
        assert len(ids) == 12
        assert all(sum(meta['records'][i]['round'] == r for i in ids) == 6 for r in (2, 3))
        assert np.all(support[ids][:, shared])
    # A delivered zero result stays zero; it is not dropped from the denominator.
    assert positive[26].sum() == positive[35].sum() == 0
    # Locations outside shared coverage remain available in native records.
    assert np.any(positive & ~shared)


def test_example_maps_are_one_original_later_round_analysis(snapshot):
    meta = json.loads((DATA / 'example/provenance.json').read_text())
    assert meta['representative_map_run'] == 'narps-neutral-r2-09'
    for rel, record in meta['sources'].items():
        assert sha(DATA / 'example' / rel) == record['sha256']
    maps = {name: nib.load(DATA / 'example/maps' / (name + '.nii.gz'))
            for name in ('group_t', 'analysis_mask', 'positive_fwe_mask', 'vmPFC_mask', 'anatomical-context')}
    ref = maps['group_t']
    assert all(im.shape == ref.shape and np.allclose(im.affine, ref.affine) for im in maps.values())
    mask = maps['analysis_mask'].get_fdata() > 0
    positive = maps['positive_fwe_mask'].get_fdata() > 0
    roi = maps['vmPFC_mask'].get_fdata() > 0
    assert mask.sum() == 198029 and positive.sum() == 24
    assert not np.any(positive & roi)
    assert not np.any(positive & ~mask)


def test_offline_figures_reproduce_frozen_outputs(tmp_path):
    # No capture root, worker worktree, source checkout or network is provided.
    for script in ('render_narps_spatial.py', 'render_narps_group_map.py'):
        subprocess.run([sys.executable, str(ROOT / 'scripts' / script), '--output', str(tmp_path)], check=True)
    for name in ('narps-spatial-agreement.svg', 'narps-spatial-agreement.png',
                 'narps-group-map.svg', 'narps-group-map.png', 'narps-spatial-summary.json'):
        assert sha(tmp_path / name) == sha(FIGURES / name)
