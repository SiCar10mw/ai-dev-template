from copy import deepcopy
from pathlib import Path

import pytest

from scripts.check_principle_tripwires import (
    check_principles_have_tripwires,
    check_standards_registry_alignment,
    load_principles,
    standards_principles,
    tripwire_is_resolvable,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("principle", load_principles(ROOT), ids=lambda principle: principle["id"])
def test_each_principle_has_tripwire_and_negative_probe(principle: dict[str, object]) -> None:
    assert principle["tripwires"]
    assert principle["negative_probe"]


@pytest.mark.parametrize("principle", load_principles(ROOT), ids=lambda principle: principle["id"])
def test_self_audit_fails_when_a_principle_loses_its_tripwire(principle: dict[str, object]) -> None:
    broken = deepcopy(load_principles(ROOT))
    for item in broken:
        if item["id"] == principle["id"]:
            item["tripwires"] = []
            break
    errors = check_principles_have_tripwires(broken)
    assert any(str(principle["id"]) in error for error in errors)


def test_standards_and_registry_are_aligned() -> None:
    assert check_standards_registry_alignment(load_principles(ROOT), standards_principles(ROOT)) == []


def test_tripwire_reference_resolution_rejects_unknown_marker() -> None:
    assert not tripwire_is_resolvable("definitely-not-a-real-tripwire", "", ROOT)
