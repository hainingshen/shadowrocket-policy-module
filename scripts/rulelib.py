from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass


SUPPORTED_RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-KEYWORD",
    "GEOIP",
    "IP-ASN",
    "IP-CIDR",
    "IP-CIDR6",
    "URL-REGEX",
    "USER-AGENT",
}
COMMENT_PREFIXES = ("#", ";", "//")
PAYLOAD_RE = re.compile(r"^\s*-\s*(.+?)\s*$")


@dataclass(frozen=True)
class Rule:
    rule_type: str
    value: str
    options: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        normalized = [self.rule_type, self.value, *self.options]
        return ",".join(part.lower() for part in normalized)

    def render_without_policy(self) -> str:
        return ",".join([self.rule_type, self.value, *self.options])

    def render_with_policy(self, policy: str) -> str:
        if self.rule_type in {"GEOIP", "FINAL"}:
            return ",".join([self.rule_type, self.value, policy, *self.options])
        return ",".join([self.rule_type, self.value, policy, *self.options])


def strip_inline_comment(line: str) -> str:
    stripped = line.strip()
    if not stripped or stripped.startswith(COMMENT_PREFIXES):
        return ""
    return stripped


def parse_rule_line(line: str) -> Rule | None:
    cleaned = strip_inline_comment(line).lstrip("\ufeff")
    if not cleaned or cleaned.lower() == "payload:" or cleaned.startswith("["):
        return None

    parts = [part.strip() for part in cleaned.split(",")]
    if len(parts) < 2:
        return None

    rule_type = parts[0].upper()
    if rule_type not in SUPPORTED_RULE_TYPES:
        return None

    value = normalize_value(rule_type, parts[1])
    if not value:
        return None

    options = tuple(part for part in parts[2:] if part)
    if rule_type in {"IP-CIDR", "IP-CIDR6"} and "no-resolve" not in {
        option.lower() for option in options
    }:
        options = (*options, "no-resolve")

    return Rule(rule_type=rule_type, value=value, options=options)


def parse_payload_line(line: str) -> Rule | None:
    match = PAYLOAD_RE.match(line)
    if not match:
        return None

    item = unquote(match.group(1).strip())
    if not item or item.startswith(COMMENT_PREFIXES):
        return None
    if "," in item:
        return parse_rule_line(item)

    return payload_item_to_rule(item)


def parse_domain_list_line(line: str) -> Rule | None:
    item = strip_inline_comment(line).lstrip("\ufeff")
    if not item or item.lower() == "payload:":
        return None
    if "," in item:
        return parse_rule_line(item)

    item = unquote(item)
    prefixed = parse_prefixed_domain(item)
    if prefixed is not None:
        return prefixed

    cidr_rule = parse_cidr(item)
    if cidr_rule is not None:
        return cidr_rule

    if item.startswith(("+.", "*.", ".")):
        domain = normalize_domain(item)
        return Rule("DOMAIN-SUFFIX", domain) if domain else None

    domain = normalize_domain(item)
    return Rule("DOMAIN", domain) if domain else None


def parse_cidr_list_line(line: str) -> Rule | None:
    item = strip_inline_comment(line).lstrip("\ufeff")
    if not item or item.lower() == "payload:":
        return None

    match = PAYLOAD_RE.match(item)
    if match:
        item = match.group(1).strip()
    return parse_cidr(unquote(item))


def payload_item_to_rule(item: str) -> Rule | None:
    item = unquote(item)
    if not item:
        return None

    prefixed = parse_prefixed_domain(item)
    if prefixed is not None:
        return prefixed

    cidr_rule = parse_cidr(item)
    if cidr_rule is not None:
        return cidr_rule

    domain = normalize_domain(item)
    if not domain:
        return None
    return Rule("DOMAIN-SUFFIX", domain)


def parse_prefixed_domain(item: str) -> Rule | None:
    lowered = item.lower()
    prefix_map = {
        "full:": "DOMAIN",
        "domain:": "DOMAIN-SUFFIX",
        "keyword:": "DOMAIN-KEYWORD",
    }
    for prefix, rule_type in prefix_map.items():
        if lowered.startswith(prefix):
            value = item[len(prefix) :]
            if rule_type == "DOMAIN-KEYWORD":
                value = value.strip()
            else:
                value = normalize_domain(value)
            return Rule(rule_type, value) if value else None

    if lowered.startswith("regexp:") or lowered.startswith("geosite:") or lowered.startswith("geoip:"):
        return None
    return None


def parse_cidr(item: str) -> Rule | None:
    try:
        network = ipaddress.ip_network(item, strict=False)
    except ValueError:
        return None

    rule_type = "IP-CIDR6" if network.version == 6 else "IP-CIDR"
    return Rule(rule_type, str(network), ("no-resolve",))


def normalize_value(rule_type: str, value: str) -> str:
    if rule_type in {"DOMAIN", "DOMAIN-SUFFIX"}:
        return normalize_domain(value)
    if rule_type == "DOMAIN-KEYWORD":
        return value.strip().lower()
    if rule_type in {"IP-CIDR", "IP-CIDR6"}:
        rule = parse_cidr(value)
        return rule.value if rule else ""
    if rule_type == "GEOIP":
        return value.strip().upper()
    return value.strip()


def normalize_domain(value: str) -> str:
    domain = unquote(value).strip().lower()
    if " " in domain:
        domain = domain.split()[0]
    while domain.startswith("*."):
        domain = domain[2:]
    while domain.startswith("+."):
        domain = domain[2:]
    while domain.startswith("."):
        domain = domain[1:]
    domain = domain.rstrip(".")
    try:
        return domain.encode("idna").decode("ascii")
    except UnicodeError:
        return domain


def unquote(value: str) -> str:
    cleaned = value.strip()
    if " #" in cleaned:
        cleaned = cleaned.split(" #", 1)[0].strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        cleaned = cleaned[1:-1]
    return cleaned.strip()
