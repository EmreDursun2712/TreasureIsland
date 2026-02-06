"""Data models for the Treasure Island CLI game."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Action:
    """A command the player can execute inside a scene."""

    command: str
    label: str
    target: str | None = None
    aliases: list[str] = field(default_factory=list)
    required_items: list[str] = field(default_factory=list)
    required_flags: dict[str, Any] = field(default_factory=dict)
    blocked_text: str = "You cannot do that right now."
    effects: dict[str, Any] = field(default_factory=dict)
    result_text: str = ""

    def matches(self, user_command: str) -> bool:
        """Return True when the command string matches this action."""
        return user_command == self.command or user_command in self.aliases


@dataclass(slots=True)
class RandomEvent:
    """A random event triggered on scene entry."""

    event_id: str
    text: str
    chance: float
    effects: dict[str, Any] = field(default_factory=dict)
    once: bool = True


@dataclass(slots=True)
class Scene:
    """A location in the world graph."""

    scene_id: str
    title: str
    description: str
    actions: list[Action] = field(default_factory=list)
    hint_text: str = ""
    on_enter_effects: dict[str, Any] = field(default_factory=dict)
    random_events: list[RandomEvent] = field(default_factory=list)
    special_handler: str | None = None


@dataclass(slots=True)
class Player:
    """Mutable player state."""

    name: str
    health: int = 3
    inventory: list[str] = field(default_factory=list)
    score: int = 0
    hints_left: int = 3

    def has_item(self, item_id: str) -> bool:
        """Return True if the player has the item."""
        return item_id in self.inventory

    def add_item(self, item_id: str) -> bool:
        """Add item if missing. Returns True if the item was added."""
        if item_id in self.inventory:
            return False
        self.inventory.append(item_id)
        return True

    def remove_item(self, item_id: str) -> bool:
        """Remove item if present. Returns True when removed."""
        if item_id not in self.inventory:
            return False
        self.inventory.remove(item_id)
        return True

    def to_dict(self) -> dict[str, Any]:
        """Serialize player data into JSON-safe dictionary."""
        return {
            "name": self.name,
            "health": self.health,
            "inventory": list(self.inventory),
            "score": self.score,
            "hints_left": self.hints_left,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Player":
        """Create a Player instance from a dictionary payload."""
        name = str(payload.get("name", "Wanderer")) or "Wanderer"
        health = int(payload.get("health", 3))
        inventory_data = payload.get("inventory", [])
        inventory = [str(item) for item in inventory_data] if isinstance(inventory_data, list) else []
        score = int(payload.get("score", 0))
        hints_left = int(payload.get("hints_left", 3))
        return cls(name=name, health=health, inventory=inventory, score=score, hints_left=hints_left)


@dataclass(slots=True)
class GameState:
    """Mutable world state."""

    current_scene_id: str
    flags: dict[str, Any] = field(default_factory=dict)
    visited_scenes: set[str] = field(default_factory=set)
    history: list[str] = field(default_factory=list)
    game_over: bool = False
    ending: str | None = None
    ending_text: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize world data into JSON-safe dictionary."""
        return {
            "current_scene_id": self.current_scene_id,
            "flags": dict(self.flags),
            "visited_scenes": sorted(self.visited_scenes),
            "history": list(self.history),
            "game_over": self.game_over,
            "ending": self.ending,
            "ending_text": self.ending_text,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GameState":
        """Create game state instance from dictionary payload."""
        current_scene_id = str(payload.get("current_scene_id", "camp"))
        flags_data = payload.get("flags", {})
        flags = dict(flags_data) if isinstance(flags_data, dict) else {}
        visited_raw = payload.get("visited_scenes", [])
        visited = {str(item) for item in visited_raw} if isinstance(visited_raw, list) else set()
        history_raw = payload.get("history", [])
        history = [str(item) for item in history_raw] if isinstance(history_raw, list) else []
        game_over = bool(payload.get("game_over", False))
        ending = payload.get("ending")
        ending_text = str(payload.get("ending_text", ""))
        return cls(
            current_scene_id=current_scene_id,
            flags=flags,
            visited_scenes=visited,
            history=history,
            game_over=game_over,
            ending=str(ending) if ending is not None else None,
            ending_text=ending_text,
        )
