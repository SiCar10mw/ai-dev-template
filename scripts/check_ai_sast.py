#!/usr/bin/env python3
"""Deterministically gate AI-SAST findings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_dev_template.ai_sast import (
    ROOT,
    apply_policy,
    findings_from_payload,
    findings_to_payload,
    load_ai_sast_config,
    load_baseline,
    load_json_path,
    scan_budget_from_config,
    select_scanner,
)

DEFAULT_TARGETS = ["ai_dev_template", "scripts", "skills"]


def _read_targets_from_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _scanner_label(scanner: object) -> str:
    return scanner.__class__.__name__


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config/ai-sast.example.json", help="AI-SAST policy config path.")
    parser.add_argument("--findings", help="Existing findings JSON to evaluate instead of running a scanner.")
    parser.add_argument("--output", help="Write the findings report JSON to this path.")
    parser.add_argument("--baseline", help="Accepted findings baseline path.")
    parser.add_argument("--threshold", help="Minimum confirmed severity that blocks.")
    parser.add_argument("--scanner", choices=["auto", "mock", "mythos"], help="Finder implementation to use.")
    parser.add_argument("--targets", nargs="*", help="Files or directories to scan when --findings is absent.")
    parser.add_argument(
        "--targets-from",
        action="append",
        default=[],
        help="File containing newline-delimited targets.",
    )
    parser.add_argument("--max-files", type=int, help="Scanner file budget override.")
    parser.add_argument("--max-bytes-per-file", type=int, help="Scanner per-file byte budget override.")
    parser.add_argument("--max-total-bytes", type=int, help="Scanner total byte budget override.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = ROOT / config_path
    config = load_ai_sast_config(config_path)

    threshold = args.threshold or str(config.get("threshold", "high"))
    baseline_value = args.baseline or str(config.get("baseline", ".ai-sast-baseline.json"))
    baseline_path = Path(baseline_value)
    if not baseline_path.is_absolute():
        baseline_path = ROOT / baseline_path
    baseline = load_baseline(baseline_path)

    scanner_label = "loaded-json"
    if args.findings:
        findings_path = Path(args.findings)
        if not findings_path.is_absolute():
            findings_path = ROOT / findings_path
        findings = findings_from_payload(load_json_path(findings_path))
    else:
        explicit_targets = args.targets is not None or bool(args.targets_from)
        target_values = list(args.targets or [])
        for targets_file in args.targets_from:
            target_path = Path(targets_file)
            if not target_path.is_absolute():
                target_path = ROOT / target_path
            target_values.extend(_read_targets_from_file(target_path))
        if not target_values and not explicit_targets:
            target_values = [str(target) for target in config.get("targets", DEFAULT_TARGETS)]

        budget = scan_budget_from_config(config)
        if args.max_files is not None or args.max_bytes_per_file is not None or args.max_total_bytes is not None:
            budget = type(budget)(
                max_files=args.max_files if args.max_files is not None else budget.max_files,
                max_bytes_per_file=(
                    args.max_bytes_per_file if args.max_bytes_per_file is not None else budget.max_bytes_per_file
                ),
                max_total_bytes=args.max_total_bytes if args.max_total_bytes is not None else budget.max_total_bytes,
            )
        scanner_name = args.scanner or str(config.get("scanner", "auto"))
        scanner = select_scanner(scanner_name, config=config, budget=budget)
        scanner_label = _scanner_label(scanner)
        findings = scanner.scan(target_values)

    report = findings_to_payload(scanner_label, findings)
    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        _write_json(output_path, report)

    result = apply_policy(findings, threshold, baseline)
    if result.passed:
        print(
            "AI-SAST passed: "
            f"0 blocking findings, {len(result.ignored_findings)} ignored "
            f"(threshold={result.threshold}, baseline={result.baseline_count})"
        )
        return 0

    print(
        "AI-SAST failed: "
        f"{len(result.blocking_findings)} blocking finding(s) "
        f"(threshold={result.threshold}, baseline={result.baseline_count})",
        file=sys.stderr,
    )
    for finding in result.blocking_findings:
        print(
            "FAIL: "
            f"{finding.file}:{finding.line}: {finding.severity.upper()} {finding.cwe} "
            f"fingerprint={finding.fingerprint} {finding.rationale}",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
