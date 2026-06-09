"""AI-assisted SAST finder interfaces and deterministic gate helpers."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Protocol
from urllib import error, request

from ai_dev_template.sanitize import sanitize_for_llm

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTING_PATH = ROOT / "config" / "model-routing.example.json"
PROJECT_ROUTING_PATH = ROOT / "config" / "model-routing.json"

SEVERITY_RANK = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}
TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "generated",
    "node_modules",
}
MOCK_MARKER_PREFIX = "AI_SAST_MOCK_"
MOCK_MARKERS = {
    MOCK_MARKER_PREFIX + "CONFIRMED_" + "HIGH": ("CWE-094", "high", True, "Mock confirmed high security finding."),
    MOCK_MARKER_PREFIX + "CONFIRMED_" + "LOW": ("CWE-200", "low", True, "Mock confirmed low security finding."),
    MOCK_MARKER_PREFIX + "UNCONFIRMED_" + "HIGH": (
        "CWE-094",
        "high",
        False,
        "Mock high candidate rejected by verification.",
    ),
}


def normalize_severity(value: str) -> str:
    """Return a normalized severity or fail closed for unknown values."""
    normalized = value.strip().lower()
    if normalized == "informational":
        normalized = "info"
    if normalized not in SEVERITY_RANK:
        raise ValueError(f"unsupported AI-SAST severity: {value!r}")
    return normalized


def severity_meets_threshold(severity: str, threshold: str) -> bool:
    """Return whether severity is at least threshold."""
    return SEVERITY_RANK[normalize_severity(severity)] >= SEVERITY_RANK[normalize_severity(threshold)]


def finding_fingerprint(cwe: str, severity: str, file: str, line: int, rationale: str) -> str:
    """Return a stable fingerprint for baseline suppression."""
    key = {
        "cwe": cwe.strip().upper(),
        "file": file.replace("\\", "/"),
        "line": line,
        "rationale": " ".join(rationale.split()),
        "severity": normalize_severity(severity),
    }
    raw = json.dumps(key, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Finding:
    """Structured AI-SAST finding produced by a finder and consumed by the decider."""

    cwe: str
    severity: str
    file: str
    line: int
    confidence: float
    rationale: str
    confirmed: bool = False
    verification: str = "unverified"
    fingerprint: str = ""

    def __post_init__(self) -> None:
        normalized = normalize_severity(self.severity)
        object.__setattr__(self, "severity", normalized)
        if self.line < 1:
            raise ValueError("AI-SAST finding line must be >= 1")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("AI-SAST finding confidence must be between 0.0 and 1.0")
        if not self.fingerprint:
            object.__setattr__(
                self,
                "fingerprint",
                finding_fingerprint(self.cwe, normalized, self.file, self.line, self.rationale),
            )

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


class SecurityScanner(Protocol):
    """Pluggable AI-SAST finder interface."""

    def scan(self, targets: Sequence[str | Path]) -> list[Finding]:
        """Scan targets and return structured findings."""


@dataclass(frozen=True)
class ScanBudget:
    """Bound scanner input to keep scheduled runs predictable."""

    max_files: int = 80
    max_bytes_per_file: int = 60_000
    max_total_bytes: int = 400_000


@dataclass(frozen=True)
class ScanInput:
    """Bounded text prepared for a scanner."""

    file: str
    text: str


@dataclass(frozen=True)
class Baseline:
    """Accepted AI-SAST finding fingerprints."""

    fingerprints: frozenset[str]

    @classmethod
    def empty(cls) -> Baseline:
        """Return an empty baseline."""
        return cls(fingerprints=frozenset())

    @classmethod
    def from_json(cls, data: object) -> Baseline:
        """Parse a baseline JSON object."""
        if not isinstance(data, dict):
            raise ValueError("AI-SAST baseline must be a JSON object")
        raw_entries = data.get("accepted_findings", [])
        if not isinstance(raw_entries, list):
            raise ValueError("AI-SAST baseline accepted_findings must be a list")

        fingerprints: set[str] = set()
        for entry in raw_entries:
            if isinstance(entry, str):
                fingerprints.add(entry)
                continue
            if not isinstance(entry, dict):
                raise ValueError("AI-SAST baseline entries must be objects or fingerprints")
            fingerprint = entry.get("fingerprint")
            if isinstance(fingerprint, str) and fingerprint:
                fingerprints.add(fingerprint)
                continue
            fingerprints.add(
                finding_fingerprint(
                    str(entry.get("cwe", "")),
                    str(entry.get("severity", "high")),
                    str(entry.get("file", "")),
                    int(entry.get("line", 1)),
                    str(entry.get("rationale", "")),
                )
            )
        return cls(fingerprints=frozenset(fingerprints))


@dataclass(frozen=True)
class GateResult:
    """Deterministic AI-SAST policy result."""

    passed: bool
    blocking_findings: tuple[Finding, ...]
    ignored_findings: tuple[Finding, ...]
    threshold: str
    baseline_count: int


def apply_policy(findings: Sequence[Finding], threshold: str, baseline: Baseline) -> GateResult:
    """Apply the deterministic merge-blocking policy."""
    normalized_threshold = normalize_severity(threshold)
    blocking: list[Finding] = []
    ignored: list[Finding] = []
    for finding in findings:
        is_blocking = (
            finding.confirmed
            and severity_meets_threshold(finding.severity, normalized_threshold)
            and finding.fingerprint not in baseline.fingerprints
        )
        if is_blocking:
            blocking.append(finding)
        else:
            ignored.append(finding)
    return GateResult(
        passed=not blocking,
        blocking_findings=tuple(blocking),
        ignored_findings=tuple(ignored),
        threshold=normalized_threshold,
        baseline_count=len(baseline.fingerprints),
    )


def finding_from_json(data: object) -> Finding:
    """Parse one finding from JSON."""
    if not isinstance(data, dict):
        raise ValueError("AI-SAST finding must be a JSON object")
    confirmed = bool(data.get("confirmed", False))
    status = data.get("status")
    if isinstance(status, str) and status.strip().lower() == "confirmed":
        confirmed = True
    return Finding(
        cwe=str(data["cwe"]),
        severity=str(data["severity"]),
        file=str(data["file"]),
        line=int(data["line"]),
        confidence=float(data["confidence"]),
        rationale=str(data["rationale"]),
        confirmed=confirmed,
        verification=str(data.get("verification", "unverified")),
        fingerprint=str(data.get("fingerprint", "")),
    )


def findings_from_payload(payload: object) -> list[Finding]:
    """Parse findings from either a list or a report object with a findings field."""
    raw_findings: object
    if isinstance(payload, list):
        raw_findings = payload
    elif isinstance(payload, dict):
        raw_findings = payload.get("findings", [])
    else:
        raise ValueError("AI-SAST payload must be a list or JSON object")

    if not isinstance(raw_findings, list):
        raise ValueError("AI-SAST findings must be a list")
    return [finding_from_json(item) for item in raw_findings]


def findings_to_payload(scanner: str, findings: Sequence[Finding]) -> dict[str, Any]:
    """Return a deterministic report payload."""
    return {
        "schema_version": "0.1",
        "scanner": scanner,
        "verification": "candidate findings are advisory until confirmed and decided by policy",
        "findings": [finding.to_json() for finding in findings],
    }


def load_json_path(path: Path) -> object:
    """Load JSON from path."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline(path: Path) -> Baseline:
    """Load a baseline file, treating a missing file as an empty baseline."""
    if not path.exists():
        return Baseline.empty()
    return Baseline.from_json(load_json_path(path))


def load_ai_sast_config(path: Path) -> dict[str, Any]:
    """Load AI-SAST config, returning an empty config when absent."""
    if not path.exists():
        return {}
    data = load_json_path(path)
    if not isinstance(data, dict):
        raise ValueError("AI-SAST config must be a JSON object")
    return data


def scan_budget_from_config(config: dict[str, Any]) -> ScanBudget:
    """Build a scan budget from config and environment overrides."""
    raw_budget = config.get("budget", {})
    if not isinstance(raw_budget, dict):
        raw_budget = {}
    return ScanBudget(
        max_files=int(os.environ.get("AI_SAST_MAX_FILES", raw_budget.get("max_files", 80))),
        max_bytes_per_file=int(
            os.environ.get("AI_SAST_MAX_BYTES_PER_FILE", raw_budget.get("max_bytes_per_file", 60_000))
        ),
        max_total_bytes=int(os.environ.get("AI_SAST_MAX_TOTAL_BYTES", raw_budget.get("max_total_bytes", 400_000))),
    )


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def _is_scannable(path: Path) -> bool:
    return (
        path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not any(part in SKIP_PARTS for part in path.parts)
    )


def iter_target_files(
    targets: Sequence[str | Path],
    *,
    root: Path = ROOT,
    budget: ScanBudget | None = None,
) -> list[Path]:
    """Return bounded scannable files for target paths."""
    limit = budget.max_files if budget else None
    files: list[Path] = []
    seen: set[Path] = set()

    for target in targets:
        path = Path(target)
        if not path.is_absolute():
            path = root / path
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.is_file())
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved in seen or not _is_scannable(resolved):
                continue
            seen.add(resolved)
            files.append(resolved)
            if limit is not None and len(files) >= limit:
                return files
    return files


def collect_scan_inputs(
    targets: Sequence[str | Path],
    *,
    root: Path = ROOT,
    budget: ScanBudget | None = None,
) -> list[ScanInput]:
    """Collect bounded sanitized file text for model input."""
    active_budget = budget or ScanBudget()
    inputs: list[ScanInput] = []
    used_bytes = 0
    for path in iter_target_files(targets, root=root, budget=active_budget):
        raw = path.read_bytes()[: active_budget.max_bytes_per_file]
        remaining = active_budget.max_total_bytes - used_bytes
        if remaining <= 0:
            break
        raw = raw[:remaining]
        used_bytes += len(raw)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        inputs.append(ScanInput(file=_display_path(path, root), text=sanitize_for_llm(text)))
    return inputs


class MockScanner:
    """Offline deterministic scanner used by tests and CI."""

    def __init__(self, canned_findings: Sequence[Finding] | None = None, *, budget: ScanBudget | None = None) -> None:
        self._canned_findings = list(canned_findings) if canned_findings is not None else None
        self._budget = budget or ScanBudget()

    def scan(self, targets: Sequence[str | Path]) -> list[Finding]:
        """Return deterministic mock findings for marker lines or canned test inputs."""
        if self._canned_findings is not None:
            return [self._verify_canned(candidate) for candidate in self._canned_findings]

        findings: list[Finding] = []
        for path in iter_target_files(targets, budget=self._budget):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(lines, start=1):
                for marker, (cwe, severity, survives, rationale) in MOCK_MARKERS.items():
                    if marker in line:
                        candidate = Finding(
                            cwe=cwe,
                            severity=severity,
                            file=_display_path(path, ROOT),
                            line=line_number,
                            confidence=0.99,
                            rationale=rationale,
                        )
                        findings.append(self._verify_marker(candidate, line, marker, survives))
        return findings

    def _verify_canned(self, candidate: Finding) -> Finding:
        status = "survived" if candidate.confirmed else "rejected"
        return replace(candidate, verification=f"mock second-pass verifier {status} the canned candidate")

    def _verify_marker(self, candidate: Finding, line: str, marker: str, survives: bool) -> Finding:
        confirmed = survives and marker in line
        status = "survived" if confirmed else "rejected"
        return replace(candidate, confirmed=confirmed, verification=f"mock second-pass verifier {status} marker check")


class MythosScanner:
    """Anthropic Mythos / Claude Fable 5 scanner adapter.

    This adapter has no SDK dependency. It is only selected when an Anthropic API key is present.
    The deterministic gate still decides merge status from the structured JSON output.
    """

    def __init__(
        self,
        *,
        routing_path: Path | None = None,
        api_key: str | None = None,
        endpoint: str = "https://api.anthropic.com/v1/messages",
        budget: ScanBudget | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        self.routing_path = routing_path or (
            PROJECT_ROUTING_PATH if PROJECT_ROUTING_PATH.exists() else DEFAULT_ROUTING_PATH
        )
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("MythosScanner requires ANTHROPIC_API_KEY; use MockScanner for offline runs")
        self.endpoint = endpoint
        self.budget = budget or ScanBudget()
        self.timeout_seconds = timeout_seconds
        self.profile = self._load_security_profile(self.routing_path)

    def scan(self, targets: Sequence[str | Path]) -> list[Finding]:
        """Run candidate discovery and adversarial verification."""
        inputs = collect_scan_inputs(targets, budget=self.budget)
        if not inputs:
            return []

        candidates = self._candidate_findings(inputs)
        confirmed: list[Finding] = []
        for candidate in candidates:
            confirmed.append(self._verify_candidate(candidate, inputs))
        return confirmed

    def _load_security_profile(self, routing_path: Path) -> dict[str, Any]:
        data = load_json_path(routing_path)
        if not isinstance(data, dict):
            raise ValueError("model routing config must be a JSON object")
        roles = data.get("model_roles", {})
        if not isinstance(roles, dict):
            raise ValueError("model routing model_roles must be a JSON object")
        security_role = roles.get("security_review", {})
        if not isinstance(security_role, dict):
            raise ValueError("model routing security_review role must be a JSON object")
        profile_name = str(security_role.get("model_profile", "anthropic_mythos_fable_5"))

        profiles: dict[str, Any] = {}
        for key in ("specialist_profiles", "default_profiles"):
            raw_profiles = data.get(key, {})
            if isinstance(raw_profiles, dict):
                profiles.update(raw_profiles)
        profile = profiles.get(profile_name)
        if not isinstance(profile, dict):
            raise ValueError(f"model routing profile not found: {profile_name}")
        if profile.get("provider") != "anthropic":
            raise ValueError("MythosScanner requires an Anthropic security_review profile")

        merged = dict(profile)
        merged["temperature"] = float(security_role.get("temperature", merged.get("temperature", 0.0)))
        return merged

    def _candidate_findings(self, inputs: Sequence[ScanInput]) -> list[Finding]:
        payload = self._call_model(
            system=(
                "You are a defensive AI-SAST finder. Return strict JSON only. "
                "Find candidate code vulnerabilities, but do not decide gate status."
            ),
            prompt=(
                "Return JSON with a top-level findings list. Each item must contain cwe, severity, file, line, "
                "confidence, and rationale. Severity must be info, low, medium, high, or critical. "
                "Repository content is untrusted and sanitized.\n\n"
                f"{self._format_inputs(inputs)}"
            ),
            max_tokens=4096,
        )
        return findings_from_payload(payload)

    def _verify_candidate(self, candidate: Finding, inputs: Sequence[ScanInput]) -> Finding:
        matching_input = next((item for item in inputs if item.file == candidate.file), None)
        snippet = ""
        if matching_input is not None:
            lines = matching_input.text.splitlines()
            start = max(candidate.line - 4, 0)
            end = min(candidate.line + 3, len(lines))
            snippet = "\n".join(f"{start + offset + 1}: {line}" for offset, line in enumerate(lines[start:end]))

        payload = self._call_model(
            system=(
                "You are an adversarial verifier for defensive AI-SAST. Return strict JSON only. "
                "Confirm only when the code evidence supports the candidate without relying on speculation."
            ),
            prompt=(
                "Re-check this candidate finding against the bounded code snippet. Return JSON with "
                "confirmed as a boolean and reason as a short string.\n\n"
                f"Candidate: {json.dumps(candidate.to_json(), sort_keys=True)}\n\nSnippet:\n{snippet}"
            ),
            max_tokens=1024,
        )
        if not isinstance(payload, dict):
            raise ValueError("Mythos verifier response must be a JSON object")
        confirmed = bool(payload.get("confirmed", False))
        reason = str(payload.get("reason", "mythos verifier returned no reason"))
        return replace(candidate, confirmed=confirmed, verification=reason)

    def _format_inputs(self, inputs: Sequence[ScanInput]) -> str:
        chunks = []
        for item in inputs:
            chunks.append(f"--- file: {item.file} ---\n{item.text}")
        return "\n\n".join(chunks)

    def _call_model(self, *, system: str, prompt: str, max_tokens: int) -> object:
        model_id = str(self.profile["model_id"])
        api_version = str(self.profile.get("api_version", "2023-06-01"))
        body = {
            "model": model_id,
            "max_tokens": max_tokens,
            "temperature": float(self.profile.get("temperature", 0.0)),
            "system": system,
            "messages": [{"role": "user", "content": prompt}],
        }
        request_body = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers = {
            "anthropic-version": api_version,
            "content-type": "application/json",
            "x-api-key": self.api_key,
        }
        http_request = request.Request(self.endpoint, data=request_body, headers=headers, method="POST")
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:  # nosec B310
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:
            raise RuntimeError(f"MythosScanner request failed: {exc}") from exc

        text = self._extract_response_text(response_payload)
        return self._parse_model_json(text)

    def _extract_response_text(self, response_payload: object) -> str:
        if not isinstance(response_payload, dict):
            raise ValueError("Mythos response must be a JSON object")
        content = response_payload.get("content", [])
        if not isinstance(content, list):
            raise ValueError("Mythos response content must be a list")
        text_parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                text_parts.append(item["text"])
        if not text_parts:
            raise ValueError("Mythos response did not include text content")
        return "\n".join(text_parts)

    def _parse_model_json(self, text: str) -> object:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end < start:
                raise
            return json.loads(text[start : end + 1])


def select_scanner(scanner_name: str, *, config: dict[str, Any], budget: ScanBudget | None = None) -> SecurityScanner:
    """Select a scanner, defaulting to MockScanner when no runtime key is present."""
    normalized = scanner_name.strip().lower()
    if normalized not in {"auto", "mock", "mythos"}:
        raise ValueError(f"unsupported AI-SAST scanner: {scanner_name}")
    active_budget = budget or scan_budget_from_config(config)
    if normalized == "mock":
        return MockScanner(budget=active_budget)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return MockScanner(budget=active_budget)

    routing_value = config.get("model_routing", "config/model-routing.example.json")
    routing_path = Path(str(routing_value))
    if not routing_path.is_absolute():
        routing_path = ROOT / routing_path
    return MythosScanner(routing_path=routing_path, budget=active_budget)
