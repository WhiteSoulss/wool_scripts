#!/usr/bin/env python3
"""Validate the reviewed Tinder native JQ against pinned, inspected original JS."""
import collections
import ctypes as C
import ctypes.util
import copy
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from test_config_syntax import sections, tokens, script_fields

def icu_searcher():
    r"""Use Surge's ICU dialect, including \c escapes unsupported by Python re."""
    library = ctypes.util.find_library('icui18n')
    assert library, 'ICU required on VPS'
    lib = C.CDLL(library)
    version = re.search(r'\.so\.(\d+)', library)
    suffix = '_' + version.group(1) if version else ''
    op = getattr(lib, 'uregex_open' + suffix)
    op.argtypes = [C.POINTER(C.c_uint16), C.c_int32, C.c_uint32, C.c_void_p, C.POINTER(C.c_int32)]
    op.restype = C.c_void_p
    set_text = getattr(lib, 'uregex_setText' + suffix)
    set_text.argtypes = [C.c_void_p, C.POINTER(C.c_uint16), C.c_int32, C.POINTER(C.c_int32)]
    find = getattr(lib, 'uregex_find' + suffix)
    find.argtypes = [C.c_void_p, C.c_int32, C.POINTER(C.c_int32)]
    find.restype = C.c_int8
    close = getattr(lib, 'uregex_close' + suffix)
    close.argtypes = [C.c_void_p]
    def search(pattern, text):
        encoded = pattern.encode('utf-16-le')
        pattern_chars = (C.c_uint16 * (len(encoded) // 2)).from_buffer_copy(encoded)
        error = C.c_int32()
        handle = op(pattern_chars, len(pattern_chars), 0, None, C.byref(error))
        assert handle and error.value <= 0, ('Invalid ICU pattern', pattern, error.value)
        try:
            encoded = text.encode('utf-16-le')
            text_chars = (C.c_uint16 * (len(encoded) // 2)).from_buffer_copy(encoded)
            set_text(handle, text_chars, len(text_chars), C.byref(error))
            matched = find(handle, 0, C.byref(error))
            assert error.value <= 0, (pattern, text, error.value)
            return bool(matched)
        finally:
            close(handle)
    return search


def verify(repo):
    stats = collections.Counter()
    regex_search = icu_searcher()
    review = json.loads((repo / 'Surge/Extra-review/tinder-review-20261011.json').read_text())
    manifest = json.loads((repo / 'Surge/Extra-review/manifest.json').read_text())
    assert len(manifest['modules']) == 1
    entry = manifest['modules'][0]
    assert entry['scope'] == 'explicit-user-requested-ad-removal'
    assert review['status'] == 'manually-reviewed-and-approved'
    assert not review['script_hub_used'] and not review['automatic_conversion_used']
    def digest(path):
        return hashlib.sha256((repo / path).read_bytes()).hexdigest()
    assert digest(entry['path']) == entry['sha256'] == review['native_sha256']
    assert digest(review['source_path']) == entry['source_sha256'] == review['source_sha256']
    assert manifest['resources'] == review['dependencies']
    for resource in review['dependencies']:
        assert digest(resource['path']) == resource['sha256']
        assert resource['status'] == 200 and resource['runtime_required'] is False
    stats['tinder_hash_checks'] = 3
    source = (repo / review['source_path']).read_text()
    original_rows = sections(source)['Script']
    assert original_rows == [action['source'] for action in review['actions']]
    source_patterns = [row.split(' ', 2)[1] for row in original_rows]
    assert all('requires-body=true, timeout=10' in row for row in original_rows)
    assert sections(source)['Mitm'] == ['hostname = api.gotinder.com']
    text = (repo / entry['path']).read_text()
    native = sections(text)
    assert set(native) == {'Body Rewrite', 'MITM'} and len(native['Body Rewrite']) == 3
    assert native['MITM'] == ['hostname = %APPEND% api.gotinder.com']
    expected_rows = [review['actions'][0]['native']] + review['actions'][1]['native']
    assert native['Body Rewrite'] == expected_rows
    native_fields = [tokens(row) for row in native['Body Rewrite']]
    assert all(len(parts) == 3 and parts[0] == 'http-response-jq' for parts in native_fields)
    assert native_fields[0][2] == native_fields[1][2]
    bundle = sections((repo / 'Surge/module/blockAds.module').read_text())
    for row in native['Body Rewrite']:
        assert bundle['Body Rewrite'].count(row) == 1
        stats['tinder_combined_wiring_cases'] += 1
    assert 'api.gotinder.com' in tokens(bundle['MITM'][0].split('%APPEND%', 1)[1], ',')
    assert not any('Tinder/tinder-adblock.js' in row for row in bundle['Script'])

    meta = 'https://api.gotinder.com/v2/meta'
    profile = 'https://api.gotinder.com/v2/profile?include=feature_access,paywalls,purchase'
    cases = [
        (meta, 'meta'), (meta + '?locale=en', 'meta'),
        (meta + '?next=/v2/profile?include=purchase', 'meta'),
        (profile, 'profile'),
        (profile.replace('feature_access,paywalls,purchase', 'paywalls'), 'profile'),
        (profile.replace('feature_access,paywalls,purchase', 'purchase'), 'profile'),
        (profile + '&next=/v2/meta', 'meta'),
        (profile.replace('feature_access,paywalls,purchase', '/v2/meta,feature_access'), 'meta'),
        (profile.replace('feature_access,paywalls,purchase', 'prefixfeature_accesssuffix'), 'profile'),
        (meta.upper(), None), (profile.upper(), None),
        (meta.replace('https:', 'http:'), None),
        (meta.replace('api.gotinder.com', 'api.gotinder.com.evil.invalid'), None),
        (profile.replace('api.gotinder.com', 'other.gotinder.com'), None),
        (meta.replace('/v2/', '/v3/'), None),
        (meta + '/more', None),
        (meta + '/?locale=en', None),
        (meta.replace('.com/', '.com:443/'), None),
        ('https://api.gotinder.com/v2/profile', None),
        ('https://api.gotinder.com/v2/profile?include=other', None),
        ('https://api.gotinder.com/v2/profile?include=/v2/meta', None),
        ('https://api.gotinder.com/v2/profile?other=1&include=paywalls', None),
        ('https://api.gotinder.com/v2/profile?include=Feature_Access', None),
        ('https://api.gotinder.com/v2/profile?include=unknown&next=paywalls', 'profile'),
        ('https://api.gotinder.com/v2/profile?include=feature_access&next=%2Fv2%2Fmeta', 'profile'),
    ]
    def dispatch(url):
        original_match = any(regex_search(pattern, url) for pattern in source_patterns)
        kind = ('meta' if '/v2/meta' in url else 'profile') if original_match else None
        matches = [parts for parts in native_fields if regex_search(parts[1], url)]
        assert len(matches) <= 1, ('Duplicate Tinder JQ execution', url)
        mapped = None if not matches else ('meta' if matches[0][2] == native_fields[0][2] else 'profile')
        assert kind == mapped, ('Original URL scope or dispatch changed', url, kind, mapped)
        return matches
    for url, expected in cases:
        matches = dispatch(url)
        actual = None if not matches else ('meta' if matches[0][2] == native_fields[0][2] else 'profile')
        assert actual == expected, url
        stats['tinder_original_url_dispatch_cases'] += 1

    # This reviewed reference contains no I/O. Only inert JSON mocks, $done and a
    # disabled logger are exposed; Node network, files, process and timers are absent.
    js_path = repo / review['dependencies'][0]['path']
    js = js_path.read_text()
    off = json.loads(re.search(r'const LEVERS_OFF = (\[[\s\S]*?\]);', js).group(1).replace(',\n]', '\n]'))
    on = json.loads(re.search(r'const LEVERS_ON = (\[.*?\]);', js).group(1))
    assert len(off) == 34 and len(on) == 2
    meta_payloads = [None, False, 3, 'unknown', [], {}, {'data': None}, {'data': []},
                     {'data': 'unknown'}, {'data': {}, 'keep': {'nested': True}}]
    for value in [None, False, True, 0, 2.5, 'false', 'true', [], {}, {'value': None},
                  {'value': False, 'keep': 1}, {'value': True, 'keep': 1},
                  {'value': 0}, {'value': 'false'}, {'value': []}, {'value': {}}]:
        meta_payloads.append({'data': {'levers': {key: copy.deepcopy(value) for key in off + on},
                                      'premium': {'unlimited_likes': False, 'rewind': False}, 'keep': 8},
                              'keep': [1, 2]})
    for value in [None, False, True, 0, 2.5, '100', [], {}, {'value': 0}, {'value': 0.5},
                  {'value': -1}, {'value': '100'}, {'value': True}, {'value': None}]:
        meta_payloads.append({'data': {'levers': {'ads.cadence': copy.deepcopy(value),
                                                 'ads.secondary_cadence': copy.deepcopy(value),
                                                 'ads.nimbus_sdk_enabled': {'value': True},
                                                 'ads.rewarded_video_enabled': {'value': True},
                                                 'unlimited_likes': {'value': False}},
                                      'keep': 'preserved'}})
    for value in [None, False, 0, 'unknown', [], {}, {'card_stack': None}, {'card_stack': []},
                  {'card_stack': {}}, {'card_stack': {'cadence': 0, 'keep': 1}},
                  {'card_stack': {'cadence': 'unknown'}, 'sdk': True}]:
        meta_payloads.append({'data': {'ads': value, 'keep': 9}, 'status': 200})
    profile_payloads = copy.deepcopy(meta_payloads[:10])
    for value in [None, False, True, 0, 'unknown', [], {}, [1, 2], [{'sku': 'gold'}]]:
        profile_payloads.append({'data': {'feature_access': value, 'plus_control': value,
                                         'entrypoints': value, 'campaigns': value,
                                         'premium_entitlement': {'gold': False, 'rewind': False}},
                                 'keep': 9})
        profile_payloads.append({'data': {'feature_access': {'ad_features': value, 'passport': False},
                                         'plus_control': {'hide_ads': value, 'unlimited_likes': False},
                                         'campaigns': {'campaigns': value, 'keep': 4},
                                         'entrypoints': value, 'keep': 7}, 'keep': 8})
    both = {'data': {'ads': {'card_stack': {'cadence': 4}},
                     'levers': {**{k: {'value': True} for k in off}, **{k: {'value': False} for k in on},
                                'ads.rewarded_video_enabled': {'value': True}, 'ads.sdk_enabled': {'value': True}},
                     'feature_access': {'ad_features': {'hide_ads': False}, 'rewind': False},
                     'plus_control': {'hide_ads': False, 'passport': False},
                     'entrypoints': ['gold'], 'campaigns': {'campaigns': ['gold'], 'keep': 9}}, 'keep': 2}
    meta_payloads.append(copy.deepcopy(both)); profile_payloads.append(copy.deepcopy(both))
    jobs = [{'url': meta, 'body': json.dumps(x)} for x in meta_payloads]
    jobs += [{'url': profile, 'body': json.dumps(x)} for x in profile_payloads]
    # Preserve the source's less obvious URL-substring dispatch in profile queries.
    jobs += [{'url': profile + '&next=/v2/meta', 'body': json.dumps(x)} for x in [both, None, {'data': {}}]]
    runner = r"""
const fs=require('node:fs'),vm=require('node:vm');
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const source=new vm.Script(input.script,{filename:'reviewed-tinder-reference.js'});
const out=input.jobs.map(job=>{
 let result;source.runInNewContext({$request:{url:job.url},$response:{body:job.body},
  $done:value=>{if(result!==undefined)throw Error('Duplicate done');result=value;},
  console:{log:()=>{}}},{timeout:100});
 if(!result)throw Error('Missing done');
 return {body:result.body===undefined?job.body:result.body,modified:result.body!==undefined};
});
process.stdout.write(JSON.stringify(out));
"""
    process = subprocess.run([shutil.which('node'), '-e', runner],
                             input=json.dumps({'script': js, 'jobs': jobs}), text=True,
                             capture_output=True, timeout=30)
    assert process.returncode == 0, process.stderr
    reference = json.loads(process.stdout)
    for job, expected in zip(jobs, reference):
        match = dispatch(job['url'])
        assert len(match) == 1
        process = subprocess.run(['jq', '-c', match[0][2]], input=job['body'],
                                 text=True, capture_output=True, timeout=5)
        assert process.returncode == 0, process.stderr
        assert json.loads(process.stdout) == json.loads(expected['body']), (job, process.stdout, expected)
        stats['tinder_original_js_jq_equivalence_cases'] += 1
    output = json.loads(subprocess.check_output(['jq', '-c', native_fields[0][2]], input=json.dumps(both), text=True))
    assert output['data']['levers']['ads.rewarded_video_enabled']['value'] is True
    assert output['data']['levers']['ads.sdk_enabled']['value'] is True
    assert output['data']['feature_access']['rewind'] is False
    output = json.loads(subprocess.check_output(['jq', '-c', native_fields[2][2]], input=json.dumps(both), text=True))
    assert output['data']['plus_control']['passport'] is False
    assert output['data']['feature_access']['rewind'] is False
    stats['tinder_sdk_and_entitlement_preservation_cases'] = 5
    # Do not claim client-level malformed/large body verification: native skip
    # behavior is documented, not exercised through a real Surge client here.
    for url in [meta, profile, profile + '&next=/v2/meta']:
        other = []
        for section in ['URL Rewrite', 'Map Local', 'Header Rewrite', 'Body Rewrite']:
            for row in bundle.get(section, []):
                if row in expected_rows:
                    continue
                parts = tokens(row)
                index = 1 if section == 'Body Rewrite' or (section == 'Header Rewrite' and parts[0] in ['http-request', 'http-response']) else 0
                if regex_search(parts[index], url):
                    other.append((section, row))
        for row in bundle.get('Script', []):
            fields = script_fields(row)
            if fields.get('pattern') and regex_search(fields['pattern'], url):
                other.append(('Script', row))
        assert not other, ('Tinder overlap requires review', url, other)
        stats['tinder_combined_endpoint_overlap_cases'] += 1
    return dict(stats)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(verify(args.repo.resolve()), ensure_ascii=False))
