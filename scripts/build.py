from __future__ import annotations

from pathlib import Path
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from rulelib import Rule, parse_rule_line


ROOT = Path(__file__).resolve().parents[1]
RULES = [
    ("youtube.list", "YouTube"),
    ("generated/youtube.list", "YouTube"),
    ("netflix.list", "Netflix"),
    ("generated/netflix.list", "Netflix"),
    ("general.list", "General"),
    ("generated/general.list", "General"),
    ("direct.list", "DIRECT"),
    ("generated/direct.list", "DIRECT"),
]
OUTPUT = ROOT / "modules" / "policy.module"


def iter_rules(path: Path) -> list[Rule]:
    if not path.exists():
        return []

    rules: list[Rule] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        rule = parse_rule_line(raw_line)
        if rule is not None:
            rules.append(rule)
    return rules


def build_module() -> str:
    lines = [
        "#!name=Shadowrocket Policy Module",
        "#!desc=Route normal traffic, YouTube, Netflix, and direct traffic to separate policies.",
        "#!author=hainingshen",
        "#!homepage=https://github.com/hainingshen/shadowrocket-policy-module",
        "",
        "[Rule]",
    ]

    seen: set[str] = set()
    for filename, policy in RULES:
        path = ROOT / "rules" / filename
        rules = iter_rules(path)
        if not rules:
            continue

        lines.append("")
        lines.append(f"# {filename} -> {policy}")
        for rule in rules:
            if rule.key in seen:
                continue
            seen.add(rule.key)
            rendered = rule.render_with_policy(policy)
            lines.append(rendered)

    lines.extend(["", "# Default proxy policy.", "FINAL,General"])
    return "\n".join(lines) + "\n"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_module(), encoding="utf-8", newline="\n")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
