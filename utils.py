"""Utility helpers for command parsing and display formatting."""

from __future__ import annotations

from typing import Iterable

ITEM_LABELS: dict[str, str] = {
    "bakir_para": "Copper Coin",
    "mesale": "Torch",
    "gumus_anahtar": "Silver Key",
    "ay_diski": "Moon Disk",
    "sifali_ot": "Healing Herb",
}


def normalize_command(raw: str) -> str:
    """Normalize command text for matching."""
    return " ".join(raw.strip().lower().split())


def clamp(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer into [minimum, maximum]."""
    return max(minimum, min(maximum, value))


def format_inventory(items: Iterable[str]) -> str:
    """Return readable inventory text."""
    item_list = list(items)
    if not item_list:
        return "Empty"
    return ", ".join(ITEM_LABELS.get(item, item.replace("_", " ").title()) for item in item_list)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    """Remove duplicates while preserving first-seen order."""
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
