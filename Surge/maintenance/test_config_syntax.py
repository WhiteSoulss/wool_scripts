#!/usr/bin/env python3
"""Quoted-field and ICU checks on VPS; not a Surge client parser or runtime test."""
import collections
import ctypes as C
import ctypes.util
import json
import re
from pathlib import Path


def tokens(row, delimiter=None):
    """Check documented delimiters/quotes; preserve regex escapes outside quotes.

    In double quotes only \\ and \" are decoded. Other regex escapes survive.
    This models the delimiter errors from the reported client logs, not every
    proprietary Surge parser behavior.
    """
    fields, buf, quote, index = [], [], None, 0
    while index < len(row):
        char = row[index]
        if quote:
            if char == quote:
                quote = None
            elif quote == '"' and char == '\\' and index + 1 < len(row) and row[index + 1] in ('\\', '"'):
                index += 1
                buf.append(row[index])
            else:
                buf.append(char)
        elif char in ("'", '"'):
            quote = char
        elif (char == delimiter if delimiter else char.isspace()):
            if buf or delimiter:
                fields.append(''.join(buf).strip())
                buf = []
        else:
            buf.append(char)
        index += 1
    assert not quote, ('Unclosed config quote', row)
    if buf or delimiter:
        fields.append(''.join(buf).strip())
    return fields


def script_fields(row):
    _, separator, value = row.partition('=')
    assert separator, row
    pairs = tokens(value, ',')
    result = {}
    for pair in pairs:
        key, separator, val = pair.partition('=')
        assert separator and re.fullmatch(r'[\w-]+', key.strip()), ('Invalid script parameter', pair, row)
        key = key.strip()
        assert key not in result, ('Duplicate script parameter', key, row)
        result[key] = val.strip()
    assert result.get('script-path'), row
    if result.get('type') in ('http-request', 'http-response'):
        assert result.get('pattern'), row
    return result


def sections(text):
    result, section = collections.defaultdict(list), None
    for row in text.splitlines():
        row = row.strip()
        if re.fullmatch(r'\[[^]]+\]', row):
            section = row[1:-1]
        elif section and row and not row.startswith(('#', ';', '//')):
            result[section].append(row)
    return result


def verify(repo):
    library = ctypes.util.find_library('icui18n')
    assert library, 'ICU required; run on VPS'
    lib = C.CDLL(library)
    version = re.search(r'\.so\.(\d+)', library)
    suffix = '_' + version.group(1) if version else ''
    open_regex = getattr(lib, 'uregex_open' + suffix)
    open_regex.argtypes = [C.POINTER(C.c_uint16), C.c_int32, C.c_uint32, C.c_void_p, C.POINTER(C.c_int32)]
    open_regex.restype = C.c_void_p
    close = getattr(lib, 'uregex_close' + suffix)
    close.argtypes = [C.c_void_p]
    close.restype = None
    def compile_pattern(pattern):
        data = pattern.encode('utf-16-le')
        chars = (C.c_uint16 * (len(data) // 2)).from_buffer_copy(data)
        status = C.c_int32()
        handle = open_regex(chars, len(chars), 0, None, C.byref(status))
        assert status.value <= 0 and handle, ('ICU pattern failed after config tokenization', status.value, pattern)
        close(handle)
    stats = collections.Counter()
    bundle = sections((repo / 'Surge/module/blockAds.module').read_text())
    manifest = json.loads((repo / 'Surge/Kelee-review/manifest.json').read_text())
    modules = [bundle] + [sections((repo / entry['path']).read_text()) for entry in manifest['modules']]
    for section in modules:
        for row in section.get('Script', []):
            fields = script_fields(row)
            if fields.get('pattern'):
                compile_pattern(fields['pattern'])
                stats['config_script_patterns_compiled_icu'] += 1
            stats['config_script_rows_tokenized'] += 1
        for row in section.get('Body Rewrite', []):
            parts = tokens(row)
            assert parts and parts[0] in {'http-response', 'http-request', 'http-response-jq', 'http-request-jq'}, row
            if parts[0].endswith('-jq'):
                assert len(parts) == 3 and parts[2], ('Malformed JQ fields', row, parts)
            else:
                assert len(parts) >= 4 and (len(parts) - 2) % 2 == 0, ('Malformed regex rewrite fields', row, parts)
                for index in range(2, len(parts), 2):
                    compile_pattern(parts[index])
                    stats['config_body_patterns_compiled_icu'] += 1
            compile_pattern(parts[1])
            stats['config_body_url_patterns_compiled_icu'] += 1
            stats['config_body_rows_tokenized'] += 1

    original = (repo / 'Surge/Kelee-review/loon-original/BaiduSearchWebpage_remove_ads.lpx').read_text()
    pattern = re.search(r'\$\{url\} ~= /(.*)/i then', original).group(1)
    native_pattern = '(?i)' + pattern
    module = sections((repo / 'Surge/module/Kelee/BaiduSearchWebpage_remove_ads.sgmodule').read_text())
    standalone = script_fields(module['Script'][0])
    total = script_fields(next(row for row in bundle['Script'] if row.startswith('kelee_0278_BaiduSearchWebpage_remove_ads_1 =')))
    for fields in (standalone, total):
        assert fields['pattern'] == native_pattern
        assert fields['requires-body'] == 'true' and fields['max-size'] == '-1'
        assert fields['script-path'].endswith('/Surge/Script/Kelee/BaiduSearch/BaiduSearchHomePage_remove_ads.js')
        stats['baidu_original_script_wiring_cases'] += 1
    # Retain the original prefix matching: from=10 characters still matches.
    cases = [
        ('https://www.baidu.com', True), ('http://m.baidu.com/', True),
        ('HTTPS://WWW.BAIDU.COM/', True),
        ('https://m.baidu.com/?from=1234567', False),
        ('https://m.baidu.com/?from=12345678', True),
        ('https://m.baidu.com/?from=123456789', True),
        ('https://m.baidu.com/?from=1234567890', True),
        ('https://m.baidu.com/?from=12345678&keep=yes', True),
        ('https://m.baidu.com/?other=x', False),
        ('https://m.baidu.com/search?from=12345678', False),
        ('https://www.baidu.com.evil.invalid/', False),
        ('https://m.baidu.com:443/', False),
    ]
    for url, expected in cases:
        assert bool(re.search(pattern, url, re.I)) == expected, url
        assert bool(re.search(standalone['pattern'], url)) == expected, url
        assert bool(re.search(total['pattern'], url)) == expected, url
        stats['baidu_source_url_equivalence_cases'] += 1

    split = sections((repo / 'Surge/module/split/partC/Crunchyroll.sgmodule').read_text())
    row = split['Body Rewrite'][0]
    assert row in bundle['Body Rewrite']
    parts = tokens(row)
    assert parts == ['http-response', r'^https?:\/\/beta-api\.crunchyroll\.com\/cms', r'offset_ms":\d+', 'offset_ms":99999999999999']
    for before, after in [
        ('{"offset_ms":0,"keep":1}', '{"offset_ms":99999999999999,"keep":1}'),
        ('{"offset_ms":123,"items":[{"offset_ms":45}]}', '{"offset_ms":99999999999999,"items":[{"offset_ms":99999999999999}]}'),
        ('{"offset_ms":-1,"offset_ms": "42"}', '{"offset_ms":-1,"offset_ms": "42"}'),
        ('{"offset_ms":1.5}', '{"offset_ms":99999999999999.5}'),
        ('{"other":42}', '{"other":42}'),
    ]:
        assert re.sub(parts[2], parts[3], before) == after
        stats['crunchyroll_original_text_rewrite_cases'] += 1
    # Old malformed rows must be rejected by the field checks.
    old_script = 'test = type=http-response, pattern=' + native_pattern + ', script-path=test.js'
    try:
        script_fields(old_script)
    except AssertionError:
        stats['reported_invalid_script_reproduced'] += 1
    else:
        raise AssertionError('Old unquoted comma was accepted')
    old_body = r'http-response ^https?:\/\/beta-api\.crunchyroll\.com\/cms offset_ms":\d+ offset_ms":99999999999999'
    assert len(tokens(old_body)) == 3
    stats['reported_invalid_body_reproduced'] += 1
    return dict(stats)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(verify(args.repo.resolve()), ensure_ascii=False))
