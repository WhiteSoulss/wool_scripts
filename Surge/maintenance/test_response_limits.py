#!/usr/bin/env python3
"""Enforce the user-approved iOS response-body budget; no client emulation."""
import collections
import json
from pathlib import Path

MAX_RESPONSE_BYTES = 1048576


def verify(repo):
    # Import lazily to share the quote-aware script parser with the syntax gate.
    from test_config_syntax import script_fields, sections
    manifest = json.loads((repo / "Surge/Kelee-review/manifest.json").read_text())
    policy = manifest["response_body_policy"]
    assert policy["client"] == "Surge iOS"
    assert policy["max_bytes"] == MAX_RESPONSE_BYTES
    assert policy["applies_to_request_scripts"] is False
    review = json.loads((repo / policy["review_record"]).read_text())
    assert review["source_and_dependencies_unchanged"]
    assert review["all_unrelated_script_fields_unchanged"]
    paths = {"Surge/module/blockAds.module", "Surge/module/weibo.module"}
    paths.update(item["path"] for item in manifest["modules"])
    extra = repo / "Surge/Extra-review/manifest.json"
    if extra.exists():
        paths.update(item["path"] for item in json.loads(extra.read_text())["modules"])
    stats = collections.Counter()
    for rel in sorted(paths):
        text = (repo / rel).read_text()
        for row in sections(text).get("Script", []):
            fields = script_fields(row)
            if fields.get("type") != "http-response":
                continue
            if fields.get("requires-body", "false").lower() not in {"true", "1"}:
                continue
            declared = fields.get("max-size")
            cap = MAX_RESPONSE_BYTES if declared is None else int(declared)
            assert 0 < cap <= MAX_RESPONSE_BYTES, ("Response body exceeds approved iOS cap", rel, row)
            stats["response_body_budget_script_rows_checked"] += 1
            if declared is None:
                stats["response_body_budget_ios_defaults_retained"] += 1
            else:
                stats["response_body_budget_explicit_caps_checked"] += 1
        # Preserve finite limits in the disabled missing-Haro reference too.
        for row in text.splitlines():
            stripped = row.strip()
            if not stripped.startswith("# kelee_") or "EasyBike_remove_ads" not in stripped:
                continue
            fields = script_fields(stripped[2:])
            assert int(fields["max-size"]) == MAX_RESPONSE_BYTES
            stats["response_body_budget_disabled_haro_checked"] += 1
    bundle = sections((repo / "Surge/module/blockAds.module").read_text())
    total_fields = [script_fields(row) for row in bundle.get("Script", [])]
    for item in review["module_reviews"]:
        current = sections((repo / item["path"]).read_text())
        for row in current.get("Script", []):
            fields = script_fields(row)
            assert fields["type"] == "http-response"
            assert fields["requires-body"] == "true"
            assert int(fields["max-size"]) == MAX_RESPONSE_BYTES
            stats["response_body_budget_reviewed_independent_rows"] += 1
            if item["missing_dependencies"]:
                assert "EasyBike/" in fields["script-path"]
                assert fields not in total_fields
            else:
                assert total_fields.count(fields) == 1, ("Body-cap wiring mismatch", item["path"], row)
                stats["response_body_budget_independent_bundle_wiring"] += 1
    return dict(stats)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(verify(args.repo.resolve()), ensure_ascii=False))
