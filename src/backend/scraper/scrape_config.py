"""YAML schema validator for scrape seed configuration.

Strict parsing via dataclasses -- unknown keys raise ValueError instead
of silently passing through.
"""

from dataclasses import dataclass, field, fields
from pathlib import Path

import yaml


@dataclass
class SeedConfig:
    """A single seed URL entry."""

    url: str
    label: str


@dataclass
class CompanyConfig:
    """A company with one or more seed URLs."""

    name: str
    seeds: list[SeedConfig] = field(default_factory=list)


@dataclass
class ScrapeDefaults:
    """Default settings for scraping."""

    mode: str = "full"


@dataclass
class ScrapeConfig:
    """Top-level scrape configuration."""

    companies: list[CompanyConfig] = field(default_factory=list)
    defaults: ScrapeDefaults = field(default_factory=ScrapeDefaults)


_VALID_MODES = {"links-only", "full"}


def _check_unknown_keys(data: dict, allowed: set[str], context: str) -> None:
    """Raise ValueError if data contains keys not in allowed set.

    Args:
        data: Dict to check.
        allowed: Set of valid key names.
        context: Description for error messages.
    """
    unknown = set(data.keys()) - allowed
    if unknown:
        raise ValueError(
            f"Unknown key(s) in {context}: {sorted(unknown)}. "
            f"Allowed: {sorted(allowed)}"
        )


def load_config(path: str = "config/scrape_seeds.yaml") -> ScrapeConfig:
    """Load and validate scrape config from YAML.

    Args:
        path: Path to the YAML config file.

    Returns:
        Validated ScrapeConfig instance.

    Raises:
        ValueError: On unknown keys, missing required fields, or invalid values.
        FileNotFoundError: If config file does not exist.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError(f"Config must be a YAML mapping, got {type(raw).__name__}")

    # Top-level keys
    top_allowed = {f.name for f in fields(ScrapeConfig)}
    _check_unknown_keys(raw, top_allowed, "top level")

    # Parse defaults
    defaults_raw = raw.get("defaults", {})
    if defaults_raw:
        defaults_allowed = {f.name for f in fields(ScrapeDefaults)}
        _check_unknown_keys(defaults_raw, defaults_allowed, "defaults")

    defaults = ScrapeDefaults(**defaults_raw) if defaults_raw else ScrapeDefaults()

    if defaults.mode not in _VALID_MODES:
        raise ValueError(
            f"Invalid mode '{defaults.mode}'. Must be one of: {sorted(_VALID_MODES)}"
        )

    # Parse companies
    companies_raw = raw.get("companies", [])
    if not companies_raw:
        raise ValueError("'companies' list must not be empty")

    companies: list[CompanyConfig] = []
    for i, co_raw in enumerate(companies_raw):
        if not isinstance(co_raw, dict):
            raise ValueError(f"companies[{i}] must be a mapping")

        co_allowed = {f.name for f in fields(CompanyConfig)}
        _check_unknown_keys(co_raw, co_allowed, f"companies[{i}]")

        if "name" not in co_raw:
            raise ValueError(f"companies[{i}] missing required field 'name'")

        seeds_raw = co_raw.get("seeds", [])
        seeds: list[SeedConfig] = []
        for j, seed_raw in enumerate(seeds_raw):
            if not isinstance(seed_raw, dict):
                raise ValueError(f"companies[{i}].seeds[{j}] must be a mapping")

            seed_allowed = {f.name for f in fields(SeedConfig)}
            _check_unknown_keys(seed_raw, seed_allowed, f"companies[{i}].seeds[{j}]")

            if "url" not in seed_raw:
                raise ValueError(
                    f"companies[{i}].seeds[{j}] missing required field 'url'"
                )
            if "label" not in seed_raw:
                raise ValueError(
                    f"companies[{i}].seeds[{j}] missing required field 'label'"
                )

            seeds.append(SeedConfig(**seed_raw))

        companies.append(CompanyConfig(name=co_raw["name"], seeds=seeds))

    return ScrapeConfig(companies=companies, defaults=defaults)
