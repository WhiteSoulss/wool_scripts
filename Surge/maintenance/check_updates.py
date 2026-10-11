#!/usr/bin/env python3
"""Archive upstream changes for human/agent review; never convert or approve."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

UA = 'Loon/983 CFNetwork/3860.500.111.2.2 Darwin/25.0.0'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def download(url):
    request = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept': '*/*', 'Accept-Encoding': 'identity'})
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            data = response.read(20 * 1024 * 1024 + 1)
            if len(data) > 20 * 1024 * 1024:
                raise ValueError('Download exceeds 20 MiB')
            if not data:
                raise ValueError('Empty download')
            return {'status': response.status, 'data': data}
    except urllib.error.HTTPError as error:
        return {'status': error.code, 'error': str(error)}
    except Exception as error:
        return {'status': None, 'error': str(error)}


def catalog_items(value):
    if isinstance(value, dict):
        if str(value.get('url', '')).startswith('loon://import?plugin='):
            yield value
        for child in value.values():
            yield from catalog_items(child)
    elif isinstance(value, list):
        for child in value:
            yield from catalog_items(child)


def source_url(item):
    return urllib.parse.parse_qs(urllib.parse.urlsplit(item['url']).query)['plugin'][0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    repo, work = args.repo.resolve(), args.work_dir.resolve()
    # Upstream candidates must never be written over approved repository files.
    if work == repo or repo in work.parents:
        raise SystemExit('--work-dir must be outside the repository')
    work.mkdir(parents=True, exist_ok=False)
    review = repo / 'Surge/Kelee-review'
    manifest = json.loads((review / 'manifest.json').read_text())
    deps = json.loads((review / 'dependency-baseline.json').read_text())['resources']
    catalog_before = json.loads((review / 'catalog-ad-baseline.json').read_text())
    report = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'status': 'unchanged', 'sources': [], 'dependencies': [],
              'catalog_changes': [], 'errors': [], 'approved_changes': [],
              'automatic_conversion_used': False, 'approves_updates': False}
    result = download('https://hub.kelee.one/list.json')
    current_ad = {}
    if result['status'] == 200:
        try:
            catalog = json.loads(result['data'])
            items = list(catalog_items(catalog))
            if not items:
                raise ValueError('No Loon plugins in catalog')
            current_ad = {source_url(x): x for x in items if '去广告' in x.get('tag', [])}
            (work / 'catalog.json').write_bytes(result['data'])
            old = {x['source_url']: x for x in catalog_before}
            for url in sorted(set(old) | set(current_ad)):
                before, now = old.get(url), current_ad.get(url)
                if before is None or now is None or any(
                    before.get(key) != now.get(key) for key in ('name', 'desc', 'date', 'tag')):
                    report['catalog_changes'].append({'source_url': url, 'before': before,
                                                       'after': now})
        except Exception as error:
            report['errors'].append({'url': 'https://hub.kelee.one/list.json', 'error': str(error)})
    else:
        report['errors'].append({'url': 'https://hub.kelee.one/list.json',
                                  'status': result['status'], 'error': result.get('error')})

    jobs = [('source', x['source_url'], x) for x in manifest['modules']]
    jobs += [('dependency', x['source_url'], x) for x in deps]

    def inspect(job):
        kind, url, baseline = job
        fetched = download(url)
        entry = {'source_url': url, 'status': fetched['status'],
                 'changed': False, 'sha256': None}
        if fetched['status'] == 200:
            data = fetched['data']
            entry['sha256'] = digest(data)
            expected = baseline['source_sha256'] if kind == 'source' else baseline['sha256']
            if kind == 'source':
                text = data.decode('utf-8-sig')
                if not text.strip().startswith(('#', '[')) or '<html' in text.lower():
                    raise ValueError('Invalid LPX response: ' + url)
                target = work / 'loon-original' / (Path(baseline['filename']).stem + '.lpx')
                if url not in current_ad:
                    entry['scope_review_required'] = True
            else:
                target = work / 'dependencies' / hashlib.sha256(url.encode()).hexdigest()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            entry['archive_path'] = str(target.relative_to(work))
            entry['changed'] = entry['sha256'] != expected
        elif kind == 'dependency' and fetched['status'] == baseline.get('status') == 404:
            entry['known_missing'] = True
        else:
            entry['error'] = fetched.get('error', 'Unexpected download status')
        return kind, entry

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(inspect, job): job for job in jobs}
        for future in concurrent.futures.as_completed(futures):
            try:
                kind, entry = future.result()
            except Exception as error:
                report['errors'].append({'url': futures[future][1], 'error': str(error)})
                continue
            report['sources' if kind == 'source' else 'dependencies'].append(entry)
            if entry.get('error'):
                report['errors'].append(entry)

    try:
        raw = subprocess.check_output(
            ['git', 'ls-remote', 'https://github.com/fmz200/wool_scripts.git', 'refs/heads/main'],
            text=True, timeout=60)
        sha = raw.split()[0]
        if len(sha) != 40 or any(c not in '0123456789abcdef' for c in sha):
            raise ValueError('Invalid upstream commit')
        report['fmz_upstream'] = {'commit': sha, 'previous': manifest['upstream_commit'],
                                  'changed': sha != manifest['upstream_commit']}
    except Exception as error:
        report['errors'].append({'upstream': 'fmz200/wool_scripts', 'error': str(error)})
    for key in ('sources', 'dependencies'):
        report[key].sort(key=lambda x: x['source_url'])
    changes = [x for key in ('sources', 'dependencies') for x in report[key]
               if x['changed'] or x.get('scope_review_required')]
    if changes or report['catalog_changes'] or report.get('fmz_upstream', {}).get('changed'):
        report['status'] = 'pending-review'
    if report['errors']:
        report['status'] = 'download-failed'
    (work / 'pending-review.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'source_checks': len(report['sources']),
                      'dependency_checks': len(report['dependencies']),
                      'changed_artifacts': len(changes), 'catalog_changes': len(report['catalog_changes']),
                      'errors': len(report['errors']), 'report': str(work / 'pending-review.json')},
                     ensure_ascii=False))
    if report['errors']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
