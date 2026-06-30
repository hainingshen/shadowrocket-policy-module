from __future__ import annotations

from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RULES = [
    ("youtube.list", "YouTube"),
    ("netflix.list", "Netflix"),
    ("direct.list", "DIRECT"),
]
OUTPUT = ROOT / "modules" / "policy.module"


def iter_rules(path: Path) -> list[str]:
    rules: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        rules.append(line)
    return rules


def with_policy(rule: str, policy: str) -> str:
    parts = [part.strip() for part in rule.split(",")]
    rule_type = parts[0].upper()

    if rule_type == "GEOIP":
        if len(parts) != 2:
            raise ValueError(f"GEOIP rules must be TYPE,COUNTRY: {rule}")
        return f"{parts[0]},{parts[1]},{policy}"

    if len(parts) < 2:
        raise ValueError(f"Rule must include a value: {rule}")

    return ",".join(parts[:2] + [policy] + parts[2:])


def build_module() -> str:
    lines = [
        "#!name=Shadowrocket Policy Module",
        "#!desc=Route normal traffic, YouTube, Netflix, and direct traffic to separate policies.",
        "#!author=hainingshen",
        "#!homepage=https://github.com/hainingshen/shadowrocket-policy-module",
        f"#!date={date.today().isoformat()}",
        "",
        "[Rule]",
    ]

    seen: set[str] = set()
    for filename, policy in RULES:
        lines.append("")
        lines.append(f"# {filename} -> {policy}")
        for rule in iter_rules(ROOT / "rules" / filename):
            rendered = with_policy(rule, policy)
            dedupe_key = rendered.lower()
            if dedupe_key in seen:
                raise ValueError(f"Duplicate generated rule: {rendered}")
            seen.add(dedupe_key)
            lines.append(rendered)

    lines.extend(["", "# Default proxy policy.", "FINAL,General"])
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_module(), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
