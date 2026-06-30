from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules" / "policy.module"
AUTO_CONFIG = ROOT / "configs" / "auto-policy.conf"
BUILD = ROOT / "scripts" / "build.py"
SOURCES = ROOT / "config" / "sources.json"
ALLOWED_POLICIES = {"General", "YouTube", "Netflix", "DIRECT"}
RULE_TYPES_WITH_POLICY_AT_2 = {"GEOIP", "FINAL"}
EXPECTED_DOMAIN_POLICIES = {
    "youtube.com": "YouTube",
    "music.youtube.com": "YouTube",
    "googlevideo.com": "YouTube",
    "netflix.com": "Netflix",
    "nflxvideo.net": "Netflix",
    "fast.com": "Netflix",
    "github.com": "General",
    "reddit.com": "General",
    "example.com": "General",
    "qq.com": "DIRECT",
    "taobao.com": "DIRECT",
    "bilibili.com": "DIRECT",
    "router.asus.com": "DIRECT",
}


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
        min_parts = 3 if rule_type == "GEOIP" else 2
        assert len(parts) >= min_parts, f"Missing policy: {line}"
        policy = parts[2] if rule_type == "GEOIP" else parts[1]
    else:
        assert len(parts) >= 3, f"Missing policy: {line}"
        policy = parts[2]

    assert policy in ALLOWED_POLICIES, f"Unknown policy {policy}: {line}"


def domain_matches(rule_type: str, value: str, domain: str) -> bool:
    if rule_type == "DOMAIN":
        return domain == value
    if rule_type == "DOMAIN-SUFFIX":
        return domain == value or domain.endswith(f".{value}")
    if rule_type == "DOMAIN-KEYWORD":
        return value in domain
    return False


def first_policy_for_domain(rule_lines: list[str], domain: str) -> str | None:
    normalized = domain.lower().rstrip(".")
    for line in rule_lines:
        parts = [part.strip() for part in line.split(",")]
        rule_type = parts[0].upper()
        if rule_type not in {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD"}:
            continue
        if len(parts) < 3:
            continue
        if domain_matches(rule_type, parts[1].lower(), normalized):
            return parts[2]
    for line in rule_lines:
        parts = [part.strip() for part in line.split(",")]
        if parts[0].upper() == "FINAL" and len(parts) >= 2:
            return parts[1]
    return None


def validate_domain_policies(rule_lines: list[str]) -> None:
    for domain, expected_policy in EXPECTED_DOMAIN_POLICIES.items():
        actual_policy = first_policy_for_domain(rule_lines, domain)
        assert actual_policy == expected_policy, (
            f"{domain} should first match {expected_policy}, got {actual_policy}"
        )


def validate_auto_config() -> None:
    text = AUTO_CONFIG.read_text(encoding="utf-8")
    assert "[Proxy Group]" in text, "auto config must define proxy groups"
    for group in ("General", "YouTube", "Netflix"):
        assert f"{group} = select" in text, f"auto config missing {group} group"
    assert "policy-regex-filter=.*" in text, "auto config should include added nodes"
    assert "FINAL,General" in text, "auto config must default to General"


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

    validate_domain_policies(rule_lines)
    validate_auto_config()
    assert rule_lines[-1] == "FINAL,General", "FINAL rule must route to General"
    assert SOURCES.exists(), "config/sources.json is required for automated updates"
    print("Module validation passed")


if __name__ == "__main__":
    main()
