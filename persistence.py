"""Persistence helpers for save/load operations."""

from __future__ import annotations

import json
from pathlib import Path

from models import GameState, Player

SAVE_PATH = Path("savegame.json")


def save_game(player: Player, state: GameState, save_path: Path = SAVE_PATH) -> tuple[bool, str]:
    """Persist player and game state as JSON."""
    payload = {
        "version": 1,
        "player": player.to_dict(),
        "state": state.to_dict(),
    }
    try:
        save_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return False, "Save file could not be written."
    return True, f"Game saved: {save_path.name}"


def load_game(save_path: Path = SAVE_PATH) -> tuple[Player | None, GameState | None, str]:
    """Load state from JSON file if it exists and is valid."""
    if not save_path.exists():
        return None, None, "Save file was not found."

    try:
        raw_data = save_path.read_text(encoding="utf-8")
        payload = json.loads(raw_data)
    except (OSError, json.JSONDecodeError):
        return None, None, "Save file is corrupted or unreadable."

    if not isinstance(payload, dict):
        return None, None, "Save file format is invalid."

    try:
        player_payload = payload["player"]
        state_payload = payload["state"]
        if not isinstance(player_payload, dict) or not isinstance(state_payload, dict):
            return None, None, "Save file is missing required fields."
        player = Player.from_dict(player_payload)
        state = GameState.from_dict(state_payload)
    except (KeyError, TypeError, ValueError):
        return None, None, "Save file is invalid. Start a new game."

    return player, state, f"Save loaded: {save_path.name}"
