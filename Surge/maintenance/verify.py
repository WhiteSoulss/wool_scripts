#!/usr/bin/env python3
"""Portable semantic and integrity checks; never approves source changes."""
import argparse
import shutil
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path
from test_config_syntax import verify as verify_config_syntax
from audit_module_syntax import verify as audit_module_syntax
from test_tinder import verify as verify_tinder

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT
NODE = shutil.which('node')


def sec(text):
    result = collections.defaultdict(list)
    current = None
    for row in text.splitlines():
        row = row.strip()
        if re.fullmatch(r'\[[^\]]+\]', row):
            current = row[1:-1]
        elif current and row and not row.startswith(('#', ';', '//')):
            result[current].append(row)
    return result


def jq(expression, payload):
    p = subprocess.run(['jq', '-c', expression], input=json.dumps(payload), text=True, capture_output=True, timeout=10)
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


def path_keys(path):
    # Independent JSON-path reader used to build real input/output fixtures.
    tokens = re.findall(r'\[([^]]+)\]|([^.[\]]+)', path)
    return [json.loads(bracket) if bracket else key for bracket, key in tokens]

def fixture_set(root, keys, value):
    node = root
    for index, key in enumerate(keys):
        if isinstance(node, list):
            while len(node) <= key:
                node.append(None)
        if index == len(keys) - 1:
            node[key] = value
        else:
            if (node.get(key) if isinstance(node, dict) else node[key]) is None:
                node[key] = [] if isinstance(keys[index + 1], int) else {'native_keep': 'preserved'}
            node = node[key]

def fixture_delete(root, keys):
    node = root
    for key in keys[:-1]:
        node = node[key]
    key = keys[-1]
    if isinstance(node, list):
        if 0 <= key < len(node):
            node.pop(key)
    else:
        node.pop(key, None)

def main():
    global ROOT, OUT, NODE
    parser = argparse.ArgumentParser(description='Verify reviewed Surge artifacts without approving source changes')
    parser.add_argument('--repo', type=Path, default=ROOT)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    ROOT = OUT = args.repo.resolve()
    if not NODE or not shutil.which('jq'):
        raise SystemExit('Node and jq are required')
    manifest_path = OUT / 'Surge/Kelee-review/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    reviewed = json.loads((ROOT / 'Surge/Kelee-review/native-ledger.json').read_text())
    by_review = {x['filename']: x for x in reviewed['plugins']}
    ns = {'path_keys': path_keys, 'fixture_set': fixture_set, 'fixture_delete': fixture_delete}
    selection = json.loads((ROOT / 'Surge/Kelee-review/ad-selection.json').read_text())
    assert len(selection) == len(manifest['modules']) > 0
    assert all('去广告' in x['tag'] for x in selection)
    assert {x['filename'] for x in selection} == {x['filename'] for x in manifest['modules']}
    assert {x['filename'] for x in reviewed['plugins']} == {x['filename'] for x in manifest['modules']}
    stats = collections.Counter()
    native_json_rows = set()
    for entry in manifest['modules']:
        text = (OUT / entry['path']).read_text()
        assert hashlib.sha256(text.encode()).hexdigest() == entry['sha256']
        assert text.splitlines()[0].startswith('#!name=') and text.splitlines()[1].startswith('#!desc=')
        assert not re.search(r'\$\{(?!\{)', text), entry['filename']
        assert 'ad.quietvales.com' not in text
        source = (ROOT / 'Surge/Kelee-review/loon-original' / entry['filename'].replace('.sgmodule', '.lpx')).read_text()
        record = by_review[entry['filename']]
        assert hashlib.sha256(source.encode()).hexdigest() == entry['source_sha256']
        source_actions = [row for key, rows in sec(source).items() if key in {'Rule', 'Rewrite', 'Script', 'General'} for row in rows]
        assert source_actions == [e['source'] for e in record['ledger']], entry['filename']
        native = sec(text)
        for action in record['ledger']:
            source_json = re.search(r'\b((?:request|response)\.json\.\w+)\(', action['source'])
            if source_json:
                assert action.get('native') == 'Body Rewrite.jq', (entry['filename'], action['source'])
                assert action.get('action') == source_json.group(1), entry['filename']
                phase = source_json.group(1).split('.', 1)[0]
                row = "http-" + phase + "-jq " + action['pattern'] + " '" + action['jq'] + "'"
                assert row in native.get('Body Rewrite', []), (entry['filename'], row)
                native_json_rows.add(row)
                stats['source_json_native_jq_gate'] += 1
            if 'pattern' in action:
                re.compile(action['pattern'])
                stats['native_patterns_compiled'] += 1
            if action.get('native') == 'Map Local' and action.get('action') in {'reject_dict', 'reject', 'response.body.mock'}:
                lines = [l for l in native.get('Map Local', []) if l.startswith(action['pattern'] + ' ')]
                assert lines, entry['filename']
                for line in lines:
                    assert re.search(r'\bstatus-code=\d+\b', line), line
                    stats['inline_mock_checks'] += 1
            if action.get('native') != 'Body Rewrite.jq':
                continue
            expression = action['jq']
            assert any("'" + expression + "'" in l for l in native.get('Body Rewrite', [])), entry['filename']
            stats['native_jq_actions_retained'] += 1
            if action['action'] not in {'response.json.delete', 'response.json.replace'}:
                continue
            paths = action['arguments'][0]
            paths = paths if isinstance(paths, list) else [paths]
            keys = [ns['path_keys'](path) for path in paths]
            fixture = {'native_keep': 'preserved'}
            for path in sorted(keys, key=len):
                ns['fixture_set'](fixture, path, 'remove-this')
            expected = json.loads(json.dumps(fixture))
            if action['action'].endswith('delete'):
                for path in sorted(keys, key=lambda k: (len(k), json.dumps(k[:-1]), k[-1] if isinstance(k[-1], int) else -1), reverse=True):
                    ns['fixture_delete'](expected, path)
            else:
                values = action['arguments'][1] if isinstance(action['arguments'][0], list) else [action['arguments'][1]]
                for path, value in zip(keys, values):
                    ns['fixture_set'](expected, path, value)
            assert jq(expression, fixture) == expected, entry['filename']
            stats['json_semantic_fixtures'] += 1
        stats['modules_verified'] += 1

    bundle = (OUT / 'Surge/module/blockAds.module').read_text()
    sections = sec(bundle)
    stats['merged_active_rows'] = sum(len(v) for v in sections.values())
    assert hashlib.sha256(bundle.encode()).hexdigest() == manifest['bundle_sha256']
    assert not any(re.search(r'(?:script-path|url)=[^, ]*(?:scripthub|script-hub)', row, re.I) for rows in sections.values() for row in rows)
    assert len(re.findall(r'^\[MITM\]$', bundle, re.M)) == 1
    assert native_json_rows.issubset(set(sections['Body Rewrite'])), 'Missing original JSON action in total module'
    assert not any('LZMH/remove-config.js' in l for l in sections['Script'])
    stats.update(verify_config_syntax(OUT))
    syntax_audit = audit_module_syntax(OUT)
    assert syntax_audit['status'] == 'passed', syntax_audit['errors']
    stats.update({'full_syntax_' + key: value for key, value in syntax_audit['checks'].items()})
    script_names = [l.split('=', 1)[0].strip() for l in sections['Script']]
    assert len(script_names) == len(set(script_names))
    assert not any('EasyBike/mobileconfig-gateway.js' in l for l in sections['Script'])
    assert not any('a\\.qiumibao\\.com\\/ios\\/config\\/\\?version_code=' in l for l in sections['URL Rewrite'])
    assert 'lzmh.lz-qs.com:6025' in sections['MITM'][0]
    assert 'yuudnn.lz-qs.com:9220' in sections['MITM'][0]
    assert 'open-cms-api.uc.cn' in sections['MITM'][0] and 'scan-order.quark.cn' in sections['MITM'][0]
    assert 'lzmh.lz-qs.com:5090' in '\n'.join(sections['General'])
    jq_expressions = set()
    for line in sections['Body Rewrite']:
        if not line.startswith(('http-response-jq ', 'http-request-jq ')):
            continue
        expression = line.split(' ', 2)[2].strip()
        if expression.startswith("'") and expression.endswith("'"):
            expression = expression[1:-1]
        jq_expressions.add(expression)
    for expression in jq_expressions:
        p = subprocess.run(['jq', '-n', 'if false then (' + expression + ') else null end'], text=True, capture_output=True)
        assert p.returncode == 0, p.stderr
    stats['merged_unique_jq_expressions_compiled'] = len(jq_expressions)
    for r in manifest['resources']:
        assert hashlib.sha256((OUT / r['path']).read_bytes()).hexdigest() == r['sha256']
    own_urls = set(re.findall(r'https://raw\.githubusercontent\.com/WhiteSoulss/wool_scripts/main/[^\s,"\\]+', bundle))
    for url in own_urls:
        assert (OUT / url.split('/main/', 1)[1]).is_file(), url
    stats['own_runtime_urls_resolved'] = len(own_urls)

    sources = {str(f): f.read_text() for f in (OUT / 'Surge/Script/Kelee').rglob('*.js')}
    runner = 'const vm=require("node:vm"),fs=require("node:fs");for(const [name,source] of Object.entries(JSON.parse(fs.readFileSync(0,"utf8"))))new vm.Script(source,{filename:name});'
    p = subprocess.run([NODE, '-e', runner], input=json.dumps(sources), text=True, capture_output=True, timeout=30)
    assert p.returncode == 0, p.stderr
    stats['scripts_compiled_without_execution'] = len(sources)
    behavior = r'''
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const root=process.argv[1];
function run(file,ctx){let result;vm.runInNewContext(fs.readFileSync(path.join(root,file),'utf8'),{...ctx,$done:v=>result=v,console},{timeout:1000});return result;}
const body='a=1&sppreviewtype=9&b=x&spsrt=3';
const r=run('CommonScript/replace-body.js',{$request:{body},$argument:'&sppreviewtype=\\d(.*)&spsrt=\\d->&sppreviewtype=0$1&spsrt=0'});
if(r.body!=='a=1&sppreviewtype=0&b=x&spsrt=0')throw Error('Tencent replace');
console.log(JSON.stringify({native_adapter_cases:1}));
'''
    p = subprocess.run([NODE, '-e', behavior, str(OUT / 'Surge/Script/Kelee')], text=True, capture_output=True, timeout=10)
    assert p.returncode == 0, p.stderr
    stats.update(json.loads(p.stdout))
    lzmh = sec((OUT / 'Surge/module/Kelee/LZMH_remove_ads.sgmodule').read_text())
    assert len(lzmh['Body Rewrite']) == 1 and not lzmh.get('Script')
    lzmh_row = lzmh['Body Rewrite'][0]
    kind, pattern, quoted = lzmh_row.split(' ', 2)
    assert kind == 'http-response-jq' and quoted == "'del(.value.config)'"
    cases = [
        ({'value': {'config': {'ad': True}, 'keep': 7}, 'keep': True},
         {'value': {'keep': 7}, 'keep': True}),
        ({'value': {'config': None, 'keep': 7}}, {'value': {'keep': 7}}),
        ({'value': {'config': [], 'other': {'config': 'preserve'}}},
         {'value': {'other': {'config': 'preserve'}}}),
        ({'value': {'keep': 8}, 'keep': True}, {'value': {'keep': 8}, 'keep': True}),
        ({'keep': 9}, {'keep': 9}),
        ({'value': None, 'keep': 9}, {'value': None, 'keep': 9}),
        ({'value': {}, 'keep': 9}, {'value': {}, 'keep': 9}),
        (None, None),
    ]
    for payload, expected in cases:
        assert jq('del(.value.config)', payload) == expected
        stats['lzmh_native_json_cases'] += 1
    endpoint = 'https://lzmh.lz-qs.com:6025/lzmh_app_api/api/v2/user/getUserBaseInfoAndConfig?'
    for url, expected in [
        (endpoint, True), (endpoint + 'token=test', True), (endpoint.upper(), True),
        (endpoint.replace('https:', 'http:'), False),
        (endpoint.replace(':6025', ''), False),
        (endpoint.replace(':6025', ':9220'), False),
        (endpoint.replace('api/v2', 'api/v1'), False),
        (endpoint[:-1], False),
        (endpoint.replace('lzmh.lz-qs.com', 'lzmh.lz-qs.com.evil.invalid'), False),
    ]:
        assert bool(re.search(pattern, url)) == expected, url
        stats['lzmh_url_scope_cases'] += 1
    pinterest_test = OUT / 'Surge/maintenance/test_pinterest.js'
    p = subprocess.run([NODE, str(pinterest_test), str(OUT)], text=True, capture_output=True, timeout=10)
    assert p.returncode == 0, p.stderr
    stats.update(json.loads(p.stdout))
    stats.update(verify_tinder(OUT))
    report = {'status': 'passed', 'checks': dict(stats), 'script_hub_used': False,
              'surge_client_runtime_tested': False, 'scope': 'VPS 静态编译、实际原版/依赖哈希、原生 JSON 行为样例与合并冲突门禁。'}
    report['scope'] = '可携带静态/语义基线检查；不转换、不自动批准原版更新，不代表客户端去广告验证。'
    report['approves_source_changes'] = False
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
