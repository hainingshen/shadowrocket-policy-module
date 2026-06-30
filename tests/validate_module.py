from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "policy.module"
BUILD = ROOT / "scripts" / "build.py"
ALLOWED_POLICIES = {"General", "YouTube", "Netflix", "DIRECT"}
RULE_TYPES_WITH_POLICY_AT_2 = {"GEOIP", "FINAL"}


def load_build_module():
    spec = importlib.util.spec_from_file_location("build", BUILD)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_rule(line: str) -> None:
    parts = [part.strip() for part in line.split(",")]
    rule_type = parts[0].upper()

    if rule_type in RULE_TYPES_WITH_POLICY_AT_2:
        assert len(parts) >= 2, f"Missing policy: {line}"
        policy = parts[2] if rule_type == "GEOIP" else parts[1]
    else:
        assert len(parts) >= 3, f"Missing policy: {line}"
        policy = parts[2]

    assert policy in ALLOWED_POLICIES, f"Unknown policy {policy}: {line}"


def main() -> None:
    build = load_build_module()
    expected = build.build_module()
    actual = MODULE.read_text(encoding="utf-8")
    assert actual == expected, "modules/policy.module is out of date; run python scripts/build.py"

    rule_lines = [
        line.strip()
        for line in actual.splitlines()
        if line.strip() and not line.startswith("#") and line.strip() != "[Rule]"
    ]
    assert len(rule_lines) == len(set(line.lower() for line in rule_lines)), "Duplicate rules found"
    for line in rule_lines:
        validate_rule(line)

    assert rule_lines[-1] == "FINAL,General", "FINAL rule must route to General"
    print("Module validation passed")


if __name__ == "__main__":
    main()
