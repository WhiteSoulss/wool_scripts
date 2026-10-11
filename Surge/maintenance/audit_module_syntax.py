#!/usr/bin/env python3
"""Audit the present ad-module grammar on VPS, without operating Surge."""
import argparse
import base64
import collections
import ctypes as C
import ctypes.util
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse
from test_config_syntax import sections, tokens, script_fields


def icu_compiler():
    library = ctypes.util.find_library('icui18n')
    assert library, 'ICU is required on VPS'
    lib = C.CDLL(library)
    version = re.search(r'\.so\.(\d+)', library)
    suffix = '_' + version.group(1) if version else ''
    op = getattr(lib, 'uregex_open' + suffix)
    op.argtypes = [C.POINTER(C.c_uint16), C.c_int32, C.c_uint32, C.c_void_p, C.POINTER(C.c_int32)]
    op.restype = C.c_void_p
    close = getattr(lib, 'uregex_close' + suffix)
    close.argtypes = [C.c_void_p]
    close.restype = None
    def compile_pattern(value):
        encoded = value.encode('utf-16-le')
        data = (C.c_uint16 * (len(encoded) // 2)).from_buffer_copy(encoded)
        status = C.c_int32()
        handle = op(data, len(data), 0, None, C.byref(status))
        assert status.value <= 0 and handle, ('Invalid ICU regex', status.value, value)
        close(handle)
    return compile_pattern, library


def top_rule_parts(row):
    """Keep quoted strings and logical parentheses intact at comma boundaries."""
    result, start, depth, quote, index = [], 0, 0, None, 0
    while index < len(row):
        char = row[index]
        if quote:
            if quote == '"' and char == '\\' and index + 1 < len(row) and row[index + 1] in ('\\', '"'):
                index += 1
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            assert depth >= 0, ('Unbalanced logical rule', row)
        elif char == ',' and depth == 0:
            result.append(row[start:index].strip())
            start = index + 1
        index += 1
    assert not quote and depth == 0, ('Unbalanced logical rule/quote', row)
    result.append(row[start:].strip())
    return result


def unwrap(value):
    assert value.startswith('(') and value.endswith(')'), ('Missing logical parentheses', value)
    return value[1:-1].strip()


def host_item(value):
    if value.startswith('-'):
        value = value[1:]
    # IP literals must be parsed before a colon is interpreted as a port.
    try:
        ipaddress.ip_address(value)
        return
    except ValueError:
        pass
    if value.startswith('['):
        match = re.fullmatch(r'\[([^]]+)\](?::(\d+))?', value)
        assert match, ('Invalid bracketed IPv6 host', value)
        assert ipaddress.ip_address(match.group(1)).version == 6, value
        assert match.group(2) is None or 0 <= int(match.group(2)) <= 65535, value
        return
    special = {'<ip-address>', '<ipv4-address>', '<ipv6-address>', '<simple-hostname>'}
    host, sep, port = value.rpartition(':')
    if sep:
        assert port.isdigit() and 0 <= int(port) <= 65535, ('Invalid host-list port', value)
        value = host
    assert value and (value in special or re.fullmatch(r'[A-Za-z0-9.*?_~-]+', value)), ('Invalid host-list item', value)


def properties(parts, allowed):
    result = {}
    for part in parts:
        key, sep, value = part.partition('=')
        assert sep and key in allowed and key not in result, ('Invalid/duplicate parameter', part)
        result[key] = value
    return result


def rule(row, compile_pattern, nested=False, depth=0):
    assert depth <= 10, ('Logical nesting exceeds documented limit', row)
    kind = row.partition(',')[0].strip()
    logical = kind in {'AND', 'OR', 'NOT'}
    fields = top_rule_parts(row) if logical else tokens(row, ',')
    minimum = 2 if nested else 3
    assert len(fields) >= minimum, ('Missing rule fields', row)
    if not nested:
        policy = fields[2]
        assert policy in {'DIRECT', 'REJECT', 'REJECT-DROP', 'REJECT-TINYGIF', 'REJECT-NO-DROP'}, ('Noninternal module policy', row)
    flags = fields[minimum:]
    assert all(flag in {'no-resolve', 'extended-matching', 'pre-matching', 'requires-resolve'} or flag.startswith(('notification-text=', 'notification-interval=', 'update-interval=', 'always-capture=')) for flag in flags), ('Invalid rule suffix', row)
    if logical:
        children = top_rule_parts(unwrap(fields[1]))
        assert children and (kind != 'NOT' or len(children) == 1), ('Invalid logical operands', row)
        for child in children:
            rule(unwrap(child), compile_pattern, True, depth + 1)
    elif kind == 'URL-REGEX':
        compile_pattern(fields[1])
    elif kind in {'DOMAIN', 'DOMAIN-SUFFIX'}:
        assert re.fullmatch(r'[A-Za-z0-9._-]+', fields[1]), ('Invalid rule hostname', row)
    elif kind in {'DOMAIN-KEYWORD', 'USER-AGENT'}:
        assert fields[1], row
    elif kind in {'IP-CIDR', 'IP-CIDR6'}:
        network = ipaddress.ip_network(fields[1], strict=False)
        assert network.version == (6 if kind == 'IP-CIDR6' else 4), row
    elif kind in {'DEST-PORT', 'SRC-PORT'}:
        assert fields[1].isdigit() and 1 <= int(fields[1]) <= 65535, row
    elif kind == 'PROTOCOL':
        assert fields[1] in {'TCP', 'UDP', 'ICMP', 'QUIC'}, row
    else:
        raise AssertionError(('Unreviewed rule type; not automatically approved', row))


def verify(repo):
    compile_pattern, library = icu_compiler()
    manifest = json.loads((repo / 'Surge/Kelee-review/manifest.json').read_text())
    entries = [{'path': 'Surge/module/blockAds.module', 'name': 'Combined module', 'sha256': manifest['bundle_sha256']}] + manifest['modules']
    allowed_sections = {'General', 'Rule', 'URL Rewrite', 'Header Rewrite', 'Body Rewrite', 'Map Local', 'Script', 'MITM'}
    errors, per_file, total, jq_expressions = [], [], collections.Counter(), set()
    for entry in entries:
        path = entry['path']
        text = (repo / path).read_text()
        assert hashlib.sha256(text.encode()).hexdigest() == entry['sha256'], path
        current, section_names = None, []
        stats = collections.Counter()
        # Header and line framing checks include non-content lines.
        metadata = collections.defaultdict(list)
        for number, row in enumerate(text.splitlines(), 1):
            value = row.strip()
            if value.startswith('#!') and '=' in value:
                key, _, content = value[2:].partition('=')
                metadata[key].append(content)
            if value.startswith('['):
                if re.fullmatch(r'\[[^]]+\]', value):
                    section_names.append(value[1:-1])
                else:
                    errors.append({'path': path, 'line': number, 'error': 'Malformed section heading', 'row': row})
        for key in ('name', 'desc', 'author'):
            if not metadata.get(key) or not all(v.strip() for v in metadata[key]):
                errors.append({'path': path, 'error': 'Missing/nonempty metadata required', 'key': key})
        if len(section_names) != len(set(section_names)) or not set(section_names).issubset(allowed_sections):
            errors.append({'path': path, 'error': 'Repeated/unreviewed section', 'sections': section_names})
        declared_arguments = {}
        for declaration in metadata.get('arguments', []):
            for item in tokens(declaration, ','):
                name, separator, default = item.partition(':')
                assert re.fullmatch(r'[A-Za-z0-9_]+', name), ('Invalid module argument name', path, name)
                assert name not in declared_arguments, ('Conflicting duplicate argument', path, name)
                declared_arguments[name] = default if separator else None
        for number, row in enumerate(text.splitlines(), 1):
            row = row.strip()
            if re.fullmatch(r'\[[^]]+\]', row):
                current = row[1:-1]
                continue
            if not row or row.startswith(('#', ';', '//')):
                continue
            try:
                assert current in allowed_sections, ('Content outside a supported section', row)
                assert '$' + '{' not in row, ('Leftover Loon parameter syntax', row)
                placeholders = re.findall(r'\{\{\{([^}]+)\}\}\}', row)
                assert all(name in declared_arguments for name in placeholders), ('Undeclared Surge module argument', placeholders, row)
                assert all(declared_arguments[name] is not None for name in placeholders), ('Module argument has no reviewed default', placeholders, row)
                stats['module_argument_references_checked'] += len(placeholders)
                if current == 'Rule':
                    rule(row, compile_pattern)
                elif current == 'URL Rewrite':
                    values = tokens(row)
                    assert len(values) in {2, 3}, ('Incorrect URL Rewrite fields', values)
                    compile_pattern(values[0])
                    assert len(values) == 2 or values[2] in {'header', '302', '307', 'reject'}, row
                elif current == 'Header Rewrite':
                    values = tokens(row)
                    index = 1 if values[0] in {'http-request', 'http-response'} else 0
                    compile_pattern(values[index])
                    action = values[index + 1]
                    wanted = {'header-add': 4, 'header-del': 3, 'header-replace': 4, 'header-replace-regex': 5}[action]
                    assert len(values) == index + wanted, row
                    if action == 'header-replace-regex':
                        compile_pattern(values[index + 3])
                elif current == 'Body Rewrite':
                    values = tokens(row)
                    assert values[0] in {'http-response', 'http-request', 'http-response-jq', 'http-request-jq'}, row
                    compile_pattern(values[1])
                    if values[0].endswith('-jq'):
                        assert len(values) == 3 and values[2], row
                        jq_expressions.add(values[2])
                    else:
                        assert len(values) >= 4 and (len(values) - 2) % 2 == 0, row
                        for index in range(2, len(values), 2):
                            compile_pattern(values[index])
                elif current == 'Map Local':
                    values = tokens(row)
                    compile_pattern(values[0])
                    fields = properties(values[1:], {'data-type', 'data', 'status-code', 'header'})
                    dtype = fields.get('data-type', 'file')
                    assert dtype in {'file', 'text', 'tiny-gif', 'base64'}, row
                    if 'status-code' in fields:
                        assert fields['status-code'].isdigit() and 200 <= int(fields['status-code']) <= 999, row
                    if dtype in {'file', 'base64'}:
                        assert fields.get('data'), ('Missing mock data', row)
                    if dtype == 'base64':
                        base64.b64decode(fields['data'], validate=True)
                    if 'header' in fields:
                        header = fields['header']
                        if ':' not in header:
                            base64.b64decode(header, validate=True)
                        else:
                            assert all(':' in part and part.partition(':')[0].strip() for part in header.split('|')), row
                    if dtype == 'text' and 'application/json' in fields.get('header', ''):
                        json.loads(fields.get('data', ''))
                        stats['json_mock_payloads_parsed'] += 1
                    data = fields.get('data', '')
                    prefix = 'https://raw.githubusercontent.com/WhiteSoulss/wool_scripts/main/'
                    if dtype == 'file' and data.startswith(prefix):
                        assert (repo / data[len(prefix):]).is_file(), data
                elif current == 'Script':
                    fields = script_fields(row)
                    assert fields.get('type', 'generic') in {'http-request', 'http-response', 'rule', 'dns', 'event', 'cron', 'generic'}, row
                    if 'pattern' in fields:
                        compile_pattern(fields['pattern'])
                    for key in {'requires-body', 'binary-body-mode', 'full-header-mode', 'debug', 'wake-system'} & fields.keys():
                        assert fields[key] in {'true', 'false'}, row
                    if 'max-size' in fields:
                        assert re.fullmatch(r'-?\d+', fields['max-size']) and int(fields['max-size']) >= -1, row
                    for key in {'timeout', 'script-update-interval'} & fields.keys():
                        assert float(fields[key]) >= 0, row
                    if 'engine' in fields:
                        assert fields['engine'] in {'auto', 'jsc', 'webview'}, row
                    url = fields['script-path']
                    prefix = 'https://raw.githubusercontent.com/WhiteSoulss/wool_scripts/main/'
                    if url.startswith(prefix):
                        assert (repo / url[len(prefix):]).is_file(), url
                    elif url.startswith(('http://', 'https://')):
                        assert urlparse(url).hostname, row
                elif current in {'MITM', 'General'}:
                    key, separator, value = row.partition('=')
                    assert separator, row
                    key = key.strip()
                    allowed = {'hostname'} if current == 'MITM' else {'always-real-ip', 'force-http-engine-hosts'}
                    assert key in allowed and value.strip().startswith(('%APPEND%', '%INSERT%')), row
                    values = re.sub(r'^\s*%(?:APPEND|INSERT)%\s*', '', value)
                    for host in tokens(values, ','):
                        host_item(host)
                        stats['host_items_checked'] += 1
                stats[current + '_rows_checked'] += 1
            except (AssertionError, ValueError, KeyError, IndexError) as error:
                errors.append({'path': path, 'line': number, 'section': current, 'error': str(error), 'row': row})
        total.update(stats)
        per_file.append({'path': path, 'sha256': entry['sha256'], 'checks': dict(stats)})
    for expression in jq_expressions:
        process = subprocess.run(['jq', '-n', 'if false then (' + expression + ') else null end'], text=True, capture_output=True, timeout=10)
        if process.returncode:
            errors.append({'error': 'Invalid JQ after config tokenization', 'expression': expression, 'detail': process.stderr})
    total['decoded_jq_expressions_compiled'] = len(jq_expressions)
    review_path = repo / 'Surge/Kelee-review/module-syntax-review-20261011.json'
    review = json.loads(review_path.read_text())
    bundle_rows = sections((repo / 'Surge/module/blockAds.module').read_text())
    for change in review['changes']:
        if change['action'] != 'Map Local JSON quoting':
            continue
        independent = sections((repo / change['path']).read_text())
        row = next(row for row in independent['Map Local'] if change['after'] in row)
        assert row in bundle_rows['Map Local'], change['path']
        decoded = properties(tokens(row)[1:], {'data-type', 'data', 'status-code', 'header'})
        assert decoded['data'] == change['payload'], ('Source payload changed', change['path'])
        assert json.loads(decoded['data']) == json.loads(change['payload'])
        try:
            old_row = row.replace(change['after'], change['before'])
            old_decoded = properties(tokens(old_row)[1:], {'data-type', 'data', 'status-code', 'header'})
            json.loads(old_decoded['data'])
        except (ValueError, AssertionError):
            total['original_invalid_mock_serializations_reproduced'] += 1
        else:
            raise AssertionError(('Original invalid quote fixture accepted', change['path']))
        total['source_mock_payload_equivalence_cases'] += 1
    def raw_defaults(text):
        values = {}
        for row in text.splitlines():
            if row.startswith('#!arguments='):
                for part in top_rule_parts(row.partition('=')[2]):
                    name, separator, value = part.partition(':')
                    assert separator, part
                    values[name] = value
        return values
    native_defaults = raw_defaults((repo / 'Surge/module/blockAds.module').read_text())
    assert native_defaults['12306_enable'] == 'true'
    for name, argument in review['inherited_argument_defaults'].items():
        assert native_defaults[name] == argument['raw_default'], name
        sources = argument.get('sources', [argument.get('source')])
        for source in sources:
            source_defaults = raw_defaults((repo / source).read_text())
            original_name = argument.get('original_argument', name)
            assert source_defaults[original_name] == argument['raw_default'], (name, source)
            total['original_argument_default_equivalence_cases'] += 1
    for change in review['changes']:
        if 'script' not in change:
            continue
        row = next(row for row in bundle_rows['Script'] if row.startswith(change['script'] + ' ='))
        assert row == change['after']
        before = script_fields(change['before'])
        after = script_fields(row)
        assert {k: v for k, v in before.items() if k != 'argument'} == {k: v for k, v in after.items() if k != 'argument'}
        total['namespaced_argument_wiring_cases'] += 1
    return {
        'status': 'failed' if errors else 'passed',
        'independent_modules': len(manifest['modules']),
        'combined_modules': 1,
        'regex_engine': library,
        'checks': dict(total),
        'errors': errors,
        'files': per_file,
        'checker_modifies_runtime_modules': False,
        'surge_client_parser_used': False,
        'surge_client_runtime_tested': False,
        'scope': 'Static grammar checks against current documented forms and Linux ICU, not the proprietary Surge parser or client functionality.',
        'known_resource_limitations': [{'module': e['filename'], 'missing_dependencies': e['missing_dependencies']} for e in manifest['modules'] if e.get('missing_dependencies')],
        'references': [
            'https://manual.nssurge.com/profile/format.html',
            'https://manual.nssurge.com/profile/module.html',
            'https://manual.nssurge.com/scripting/overview.html',
            'https://manual.nssurge.com/http/body-rewrite.html',
            'https://manual.nssurge.com/http/map-local.html',
            'https://manual.nssurge.com/http/url-rewrite.html',
            'https://manual.nssurge.com/rules/overview.html',
            'https://manual.nssurge.com/rules/logical.html',
            'https://manual.nssurge.com/profile/host-list.html',
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = verify(args.repo.resolve())
    if args.report:
        args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    compact = {key: value for key, value in result.items() if key != 'files'}
    print(json.dumps(compact, ensure_ascii=False))
    raise SystemExit(0 if result['status'] == 'passed' else 1)
