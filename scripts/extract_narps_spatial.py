#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Center for Open Neuroscience
# SPDX-License-Identifier: Apache-2.0
"""Freeze later-round spatial evidence from hash-bound original deliveries.

This is descriptive extraction, not new group inference or research replay.
Use --runs-root for retained launcher captures and --iteration-root for their
published package indices. Offline rendering subsequently uses only this repo.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import posixpath
from pathlib import Path
import tempfile
import nibabel as nib
from nilearn import image
import nilearn
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'experiments/narps-poster/map-inputs'
REPO = 'https://github.com/leej3/stamped-in-practice'
CONDITIONS = [('baseline', 'No supplied research skills'), ('discover-general', 'Find useful skills'),
              ('discover-science', 'Find research skills'), ('stamped-explicit', 'Use STAMPED skills')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_bytes(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    temporary.replace(path)  # Never overwrite a symlink's annex object.


def write_json(path, value):
    write_bytes(path, (json.dumps(value, indent=2) + '\n').encode())


class Captures:
    def __init__(self, root, iteration, output):
        self.root, self.iteration, self.output = root, iteration, output
        self.sources, self.manifests, self.identities = {}, {}, {}

    def native(self, run):
        return self.root / run / 'attempt-01/native'

    def initialize(self, run, round_number):
        native = self.native(run)
        manifest = native / 'original-delivery/manifest.json'
        end = native / 'worker-end-state.json'
        state, capture = json.loads(end.read_text()), json.loads(manifest.read_text())
        if state['capture_status'] != 'complete' or capture['capture_status'] != 'complete':
            raise ValueError(f'Incomplete original delivery: {run}')
        if state['capture']['sha256'] != digest(manifest):
            raise ValueError(f'Capture binding differs: {run}')
        indices = list((self.iteration / f'rounds/round-{round_number:02}').glob(
            f'**/delivery-packages/{run}/index.json'))
        receipts = []
        for candidate in (self.iteration / f'rounds/round-{round_number:02}').glob('research-closure-01/**/*stop-validation.json'):
            for row in json.loads(candidate.read_text()).get('runs', []):
                if row['run'] == run:
                    receipts.append((candidate, row))
        if len(receipts) != 1:
            raise ValueError(f'Expected one retained stop validation for {run}')
        receipt, row = receipts[0]
        if row['capture_sha256'] != digest(manifest) or row['stop_sha256'] != digest(end):
            raise ValueError(f'Retained stop identity differs: {run}')
        if len(indices) > 1:
            raise ValueError(f'Ambiguous published package for {run}')
        if indices:
            index = json.loads(indices[0].read_text())
            if index['capture_sha256'] != digest(manifest) or index['end_state_sha256'] != digest(end):
                raise ValueError(f'Published package identity differs: {run}')
        assignment = native / 'condition-assignment.json'
        self.manifests[run] = {e['path']: e for e in capture['entries']}
        self.identities[run] = {
            'capture_sha256': digest(manifest), 'end_state_sha256': digest(end),
            'worker_head_commit': state['head_commit'],
            'condition_assignment_sha256': digest(assignment),
            'package_index_sha256': digest(indices[0]) if indices else None,
            'stop_validation_sha256': digest(receipt),
            'stop_validation_path': receipt.relative_to(self.iteration).as_posix(),
            'package_url': f'{REPO}/tree/codex/iteration-narps-neutral-v1/' +
                           (indices[0].parent if indices else receipt.parent).relative_to(self.iteration).as_posix(),
        }
        for name, source in [('capture-manifest.json', manifest), ('worker-end-state.json', end),
                             ('condition-assignment.json', assignment), ('stop-validation.json', receipt)]:
            write_bytes(self.output / 'sources' / run / name, source.read_bytes())
        if indices:
            write_bytes(self.output / 'sources' / run / 'package-index.json', indices[0].read_bytes())
        return json.loads(assignment.read_text())

    def read(self, run, relative, retain=False):
        key = f'content/workspace/{relative}'
        entry = self.manifests[run].get(key)
        if entry is None or entry['kind'] != 'file':
            raise ValueError(f'No retained original file: {run}/{relative}')
        path = self.native(run) / 'original-delivery' / key
        if digest(path) != entry['sha256']:
            raise ValueError(f'Original delivery hash mismatch: {run}/{relative}')
        self.sources[f'{run}/{relative}'] = {'run': run, 'path': relative,
                                            'sha256': entry['sha256'], 'bytes': entry['size']}
        if retain:
            write_bytes(self.output / 'sources' / run / 'workspace' / relative, path.read_bytes())
        return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-root', type=Path, required=True)
    parser.add_argument('--iteration-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=DATA / 'spatial')
    parser.add_argument('--example-output', type=Path, default=DATA / 'example')
    args = parser.parse_args()
    out = args.output.resolve()
    selection = json.loads((out / 'selection.json').read_text())
    binding = Captures(args.runs_root.resolve(), args.iteration_root.resolve(), out)
    assignments = {r['run']: binding.initialize(r['run'], r['round']) for r in selection['records']}
    reference = None
    cohort_identity = None

    def volume(run, relative):
        nonlocal reference
        img = nib.load(binding.read(run, relative))
        if reference is None:
            reference = img
        if img.shape != reference.shape or not np.allclose(img.affine, reference.affine, atol=1e-5):
            raise ValueError(f'Native map geometry differs: {run}/{relative}')
        return img.get_fdata()

    common54 = volume('narps-neutral-r2-03', 'results/group_common_support_mask.nii.gz') > 0
    coverage90 = volume('narps-neutral-r2-05', 'results/analysis_mask.nii.gz') > 0
    masks, positives, records = [], [], []
    for item in selection['records']:
        run = item['run']
        cohort = json.loads(binding.read(run, 'input/sources.json', retain=True).read_text())
        identity = {k: v['sha256'] for k, v in cohort['files'].items() if k.endswith('.nii.gz')}
        for relative, expected in identity.items():
            key = f'content/workspace/input/{relative}'
            entry = binding.manifests[run][key]
            if entry['kind'] == 'symlink':
                key = posixpath.normpath(posixpath.join(posixpath.dirname(key), entry['link_target']))
                entry = binding.manifests[run][key]
            if entry['kind'] != 'file' or entry['sha256'] != expected:
                raise ValueError(f'Captured participant payload differs: {run}/{relative}')
        if cohort_identity is None:
            cohort_identity = identity
        if identity != cohort_identity or len(identity) != 54:
            raise ValueError(f'Participant map identity differs: {run}')
        for key, entry in binding.manifests[run].items():
            relative = key.removeprefix('content/workspace/')
            if not key.startswith('content/workspace/') or entry['kind'] != 'file':
                continue
            if relative.startswith(('.', 'input/', 'skills/', 'local-skills/')):
                continue
            if any(x in relative for x in ('/atlases/', '/atlas/', '/reference/', '/pilot/', '/replay/', '/attempts/')):
                continue
            if entry.get('size', 0) < 100000 and relative.endswith(('.py', '.md', '.json', '.tsv', '.csv')):
                binding.read(run, relative, retain=True)
        stat = volume(run, item['statistic'])
        field = volume(run, item['decision'])
        rule = item['mask']
        if rule == 'common54':
            mask = common54.copy()
            mask_note = 'Derived: intersection of the same 54 finite nonzero input maps, using the identical retained rule and native r2-03 mask.'
        elif rule == 'coverage90':
            mask = coverage90.copy()
            mask_note = 'Derived: nonzero coverage in at least 49/54 identical participant maps, using the identical retained rule and native r2-05 mask.'
        elif rule.startswith('exact:'):
            mask = np.isfinite(stat) & (stat != 0)
            expected = int(rule.split(':')[1])
            if mask.sum() != expected:
                raise ValueError(f'Cannot reconstruct complete native mask: {run}')
            count_sources = {
                'narps-neutral-r2-11': ('results/summary.json', 'standard_brain_mask_intersection_voxels'),
                'narps-neutral-r2-13': ('results/summary.json', 'mask_voxels'),
                'narps-neutral-r2-15': ('results/analysis_summary.json', 'mask_voxels'),
                'narps-neutral-r3-04': ('results/summary.json', 'common_support_voxels'),
                'narps-neutral-r3-11': ('results/summary.json', 'analysis_mask_voxels'),
                'narps-neutral-r3-12': ('results/analysis_summary.json', 'n_voxels_tested'),
            }
            summary_path, count_key = count_sources[run]
            if json.loads(binding.read(run, summary_path).read_text())[count_key] != expected:
                raise ValueError(f'Mask count does not match retained summary: {run}')
            mask_note = ('Derived exactly from nonzero finite statistics: source code writes zero outside its analysis mask; '
                         f'the {expected} nonzero voxels equal its retained reported mask count. No in-mask zeros are omitted.')
        elif rule == 'proven':
            mask = np.isfinite(stat) & (stat != 0)
            mask_note = ('Derived proven tested-support subset: native source writes zero outside its template mask. '
                         '196115 nonzero finite statistics certify inclusion; five zero-valued native-mask voxels remain unknown. '
                         'No installed template is substituted; only the certified subset enters shared coverage.')
            if mask.sum() != 196115:
                raise ValueError('Unexpected R2-01 proven support')
        else:
            mask = volume(run, rule) > 0
            mask_note = 'Native retained analysis-support map; positive entries define tested voxels.'
        if not np.all(np.isfinite(stat[mask])) or not np.all(np.isfinite(field[mask])):
            raise ValueError(f'Nonfinite values on tested support: {run}')
        if item['decision_kind'] == 'binary':
            positive = (field > 0) & mask & (stat > 0)
        elif item['decision_kind'] == 'logp':
            positive = (field >= -np.log10(.05)) & mask & (stat > 0)
        else:
            positive = (field <= np.float32(.05)) & mask & (stat > 0)
        if int(positive.sum()) != item['expected_native_positive_voxels']:
            raise ValueError(f'Native primary decision count differs for {run}: {positive.sum()}')
        records.append({**item, 'condition': assignments[run]['condition'],
                        'condition_coordinator_revision': assignments[run]['coordinator_commit'],
                        'mask_rule': mask_note, 'retained_support_voxels': int(mask.sum()),
                        'native_positive_voxels': int(positive.sum()), **binding.identities[run]})
        masks.append(mask); positives.append(positive)
    masks, positives = np.stack(masks), np.stack(positives)
    shared = masks.all(axis=0)
    if not shared.any():
        raise ValueError('No shared coverage')
    anatomy_path = binding.read('narps-neutral-r3-11', 'results/mni152_template.nii.gz')
    anatomy = image.resample_to_img(nib.load(anatomy_path), reference,
                                   interpolation='continuous', force_resample=True, copy_header=True)
    anatomy_array = anatomy.get_fdata(dtype=np.float32)
    with tempfile.NamedTemporaryFile(dir=out, suffix='.npz', delete=False) as handle:
        temporary = Path(handle.name)
    np.savez_compressed(temporary, affine=reference.affine, native_masks=masks, native_positive=positives,
                        shared_support=shared, anatomy=anatomy_array)
    temporary.replace(out / 'spatial-inputs.npz')
    provenance = {
        'schema_version': 2, 'comparison': 'narps-neutral-v1', 'rounds': [2, 3],
        'study': 'NARPS AO86 equal-indifference potential-gain group analysis', 'n_participants': 54,
        'conditions': [{'id': c, 'label': label} for c, label in CONDITIONS], 'records': records,
        'evaluation_support': 'Intersection of certified tested supports of all 48 delivered primary analyses. Outside is unavailable, never a negative result.',
        'frequency_definition': 'Native positive whole-brain FWE decisions at alpha .05, divided by 12 delivered analyses per assigned condition, on identical shared coverage. Retains each worker correction and computation as delivered.',
        'selection': selection['selection'],
        'statistic_note': 'Unthresholded field identities are retained in provenance, not pooled as interchangeable t statistics: R2-13 uses RMS standardization and original numerical differences are preserved.',
        'display': {'view': 'posterior axial crops', 'xlim_mni_mm': [-42, 42], 'ylim_mni_mm': [-110, -78],
                    'z_cuts_mni_mm': [-8.4, -3.6, -1.2], 'orientation': 'neurological: image left is participant left',
                    'slice_selection': 'Three fixed planes used by the poster prototype, containing posterior corrected loci; descriptive display, not independent localization.'},
        'anatomy': {'run': 'narps-neutral-r3-11', 'path': 'results/mni152_template.nii.gz',
                    'sha256': digest(anatomy_path), 'use': 'Native retained MNI152 anatomy resampled for context only; never used to reconstruct analysis support.'},
        'software': {'numpy': np.__version__, 'nibabel': nib.__version__, 'nilearn': nilearn.__version__},
        'selection_sha256': digest(out / 'selection.json'), 'npz_sha256': digest(out / 'spatial-inputs.npz'),
        'source_files': binding.sources,
    }
    write_json(out / 'provenance.json', provenance)
    example_run = 'narps-neutral-r2-09'
    example = args.example_output.resolve()
    native_files = {'group_t.nii.gz': 'results/group_tstat.nii.gz',
                    'analysis_mask.nii.gz': 'results/common_mask.nii.gz',
                    'vmPFC_mask.nii.gz': 'results/vmPFC_HO_proxy.nii.gz'}
    sources = {}
    for target, source in native_files.items():
        p = binding.read(example_run, source)
        rel = f'maps/{target}'
        write_bytes(example / rel, p.read_bytes())
        sources[rel] = {'sha256': digest(example / rel), 'run': example_run, 'path': source}
    for target, arr in [('positive_fwe_mask.nii.gz', positives[8].astype(np.uint8)),
                        ('anatomical-context.nii.gz', anatomy_array)]:
        p = example / 'maps' / target
        with tempfile.NamedTemporaryFile(dir=p.parent, suffix='.nii.gz', delete=False) as handle:
            temp = Path(handle.name)
        nib.save(nib.Nifti1Image(arr, reference.affine), temp)
        temp.replace(p)
        sources[f'maps/{target}'] = {'sha256': digest(p), 'derivation': 'Native R2-09 positive decision' if target.startswith('positive') else provenance['anatomy']}
    write_json(example / 'provenance.json', {
        'schema_version': 2, 'representative_map_run': example_run,
        'selection': 'First STAMPED R2 delivery in run order with a saved analysis mask and anatomical vmPFC proxy.',
        'native_support_voxels': int(masks[8].sum()), 'native_positive_voxels': int(positives[8].sum()),
        'map_display': {'slice_centers_mni_mm': [0, 40, -4]},
        'sources': sources, 'source_identity': binding.identities[example_run],
        'spatial_provenance_sha256': digest(out / 'provenance.json'),
    })
    print(f'Frozen 48 original R2/R3 outputs; {shared.sum():,} shared voxels; native decision counts verified.')


if __name__ == '__main__':
    main()
