"""Bind final-linked stopped judgment artifacts; never infer scientific verdicts."""
from pathlib import Path
import argparse
import hashlib
import json
import re

B = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': sha(path)}


def select_output(final_text, workspace, word, suffix):
    candidates = []
    for label, path in re.findall(r'\[([^\]]+)\]\((<?[^\n)]+>?)\)', final_text):
        if word not in label.casefold():
            continue
        path = Path(path.strip('<>'))
        if not path.is_absolute():
            path = workspace / path
        if path.suffix != suffix:
            continue
        path = path.resolve()
        if not path.is_relative_to(workspace):
            raise ValueError('Final-linked output is outside the judgment workspace')
        if path not in candidates:
            candidates.append(path)
    if len(candidates) != 1 or not candidates[0].is_file():
        raise ValueError(f'Canonical {word} output needs explicit review: {candidates}')
    return candidates[0]


def report_lines(report_text):
    fence = None
    for number, line in enumerate(report_text.splitlines(), 1):
        marker = re.match(r'^\s{0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = marker[1]
            continue
        yield number, line


def extract_conclusion(report_text):
    matches = []
    for number, line in report_lines(report_text):
        for match in re.finditer(r'Reported hypothesis outcome\s*(?:\*\*)?\s*:', line, re.I):
            matches.append({'quote': line[match.start():], 'start_line': number, 'end_line': number})
    return matches[0] if len(matches) == 1 else None


def extract_adequacy(report_text):
    labels = []
    for number, line in report_lines(report_text):
        plain = re.sub(r"[*_'\"`]", '', line)
        # Only a labeled report line, never an occurrence in explanatory prose.
        if not re.match(r'^\s*(?:[>#-]+\s*)?Scientific adequacy\s*:', plain, re.I):
            continue
        values = re.findall(r'Scientific adequacy\s*:\s*([^.;\n]+)', plain, re.I)
        for value in values:
            match = re.fullmatch(r'(not supported|unable to assess|supported|qualified)\s*', value, re.I)
            labels.append((number, match.group(1).casefold() if match else None, line))
    categories = {value for _, value, _ in labels}
    if len(categories) == 1 and None not in categories:
        number, category, quote = labels[0]
        return {'extraction_status': 'explicit', 'category': category,
                'excerpt': {'quote': quote, 'start_line': number, 'end_line': number}}
    return {'extraction_status': 'ambiguous' if labels else 'missing', 'category': None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('judgment')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    allocation_path = B / 'dataset/allocation.json'
    expected_allocation = 'a4678aa8dbc52d7d46ba5bd659746d81a48427a0a29a1f17f651b5821127889c'
    assert sha(allocation_path) == expected_allocation
    allocation = json.loads(allocation_path.read_text())
    assigned = [j for r in allocation['rounds'] for j in r['judgment_dispatch_order']
                if j['judgment'] == args.judgment]
    assert len(assigned) == 1
    slot = assigned[0]
    run, role = slot['run'], slot['role']
    parent = B / 'runs' / run / 'judgments' / args.judgment
    dispatch_path = parent / 'dispatch.json'
    dispatch = json.loads(dispatch_path.read_text())
    assert dispatch['status'] == 'launcher-finished'
    attempt = parent / 'attempt-01'
    result = attempt / 'native/result.json'
    native = json.loads(result.read_text())
    assert native['finished_at'] and native['native_session_ids']
    workspace = Path(native['judge_workspace']).resolve()
    final = attempt / 'native/final.txt'
    report = select_output(final.read_text(), workspace, 'report', '.md')
    response = select_output(final.read_text(), workspace, 'response', '.json')
    report_text = report.read_text()
    adequacy = extract_adequacy(report_text)
    conclusion = extract_conclusion(report_text)
    outputs = {'report': ref(report), 'response': ref(response)}
    if args.check_only:
        print(json.dumps({'judgment': args.judgment, 'outputs': outputs,
                          'adequacy': adequacy, 'target_unchanged': native.get('target_unchanged'),
                          'conclusion': conclusion}, indent=2))
        return
    out = B / 'judgment-extractions' / args.judgment
    out.mkdir(parents=True, exist_ok=False)
    binding = {'schema_version': 1, 'kind': 'coordinator-assessment-output-binding',
               'native_result_sha256': sha(result), 'native_session_ids': native['native_session_ids'],
               'outputs': outputs}
    (out / 'output-binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    judgment = {'judgment_id': args.judgment, **outputs,
                'native': {'procedure_status': ref(attempt / 'native/procedure-status.json'), 'result': ref(result)},
                'output_binding': ref(out / 'output-binding.json'), 'adequacy': adequacy}
    if conclusion is not None:
        judgment['conclusion'] = conclusion
    admission = native.get('target_unchanged') is True and dispatch['returncode'] == 0
    record = {'run_id': run, 'role': role, 'judgment': judgment, 'operations': [
        {'operation_id': args.judgment + '-native', 'stage': 'judging', 'actor': 'judge',
         'judgment_role': role, 'status': 'succeeded' if admission else 'partial',
         'scope': 'native independent judgment session elapsed wall time; process completion, not scientific adequacy or billing',
         'duration_s': native['elapsed_seconds'], 'evidence': [ref(result)]}]}
    (out / 'extraction.json').write_text(json.dumps(record, indent=2) + '\n')
    names = [('canonical-report.md', report), ('canonical-response.json', response), ('native-result.json', result)]
    for name, source in names:
        data = source.read_bytes()
        (out / name).write_bytes(data)
        assert source.read_bytes() == data
    assert all(sha(Path(value['path'])) == value['sha256'] for value in outputs.values())
    evidence = {'scope': 'Unique final-linked canonical report and response; explicit scientific-adequacy labels only. Coordinator attribution is not a native signature.',
                'native_final': ref(final), 'dispatch': ref(dispatch_path), 'allocation': ref(allocation_path),
                'sources': outputs, 'copies': {name: ref(out / name) for name, _ in names},
                'extractor': ref(Path(__file__)), 'formal_admission_expected': admission,
                'limitation': None if admission else 'Original launcher/target-integrity gate fails; raw report retained without comparison measures.'}
    (out / 'source-binding-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps({'judgment': args.judgment, 'output': str(out),
                      'adequacy_status': adequacy['extraction_status'], 'category': adequacy['category']}))


if __name__ == '__main__':
    main()
