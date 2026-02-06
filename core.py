"""UI-independent gameplay core for Treasure Island."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict

import random

import persistence
from models import Action, GameState, Player, Scene
from scenes import build_scenes
from utils import ITEM_LABELS, clamp, dedupe_preserve_order, format_inventory, normalize_command


MAX_HEALTH = 5
MAX_HINTS = 3


class ViewAction(TypedDict, total=False):
    command: str
    label: str
    enabled: bool
    blocked_reason: str


class GameView(TypedDict):
    scene_id: str
    title: str
    description: str
    actions: list[ViewAction]
    status: dict[str, Any]
    game_over: bool
    ending_type: str | None
    ending_text: str
    new_messages: list[str]


@dataclass
class GameCore:
    """
    UI-independent game core.
    No print(), no input(), no ui.py import.
    The UI layer calls:
      - new_game()
      - load_game()
      - save_game()
      - get_view()
      - submit()
    and then renders `GameView` + `new_messages`.
    """

    scenes: dict[str, Scene] = field(default_factory=build_scenes)
    player: Player | None = None
    state: GameState | None = None
    rng: random.Random = field(default_factory=random.Random)

    # internal message queue (UI will display these)
    _messages: list[str] = field(default_factory=list)

    def new_game(self, player_name: str) -> None:
        """Initialize a fresh game and enter the starting scene."""
        name = (player_name or "").strip() or "Explorer"
        self.player = Player(name=name, health=3, inventory=[], score=0, hints_left=MAX_HINTS)
        self.state = GameState(current_scene_id="camp")
        # Ensure flags needed by existing scene requirements are initialized
        self._ensure_default_flags()
        self._enter_scene("camp")
        self._push("Welcome to Treasure Island. Your mission is to find the treasure.")

    def load_game(self) -> tuple[bool, str]:
        """Load from savegame.json via persistence.py. Return (success, message)."""
        p, s, message = persistence.load_game()
        if p is None or s is None:
            return False, message

        # Validate scene id
        if s.current_scene_id not in self.scenes:
            return False, "Save invalid: unknown scene id."

        # Clamp numeric fields
        p.health = clamp(p.health, 0, MAX_HEALTH)
        p.hints_left = clamp(p.hints_left, 0, MAX_HINTS)

        # Repair state
        if s.current_scene_id not in s.visited_scenes:
            s.visited_scenes.add(s.current_scene_id)
        if not s.history:
            s.history.append(s.current_scene_id)

        self.player, self.state = p, s
        self._ensure_default_flags()
        self._push(message)
        return True, message

    def save_game(self) -> tuple[bool, str]:
        """Save to savegame.json via persistence.py. Return (success, message)."""
        if not self.player or not self.state:
            return False, "Nothing to save."
        ok, msg = persistence.save_game(self.player, self.state)
        self._push(msg if ok else f"Save failed: {msg}")
        return ok, msg

    def get_view(self) -> GameView:
        """
        Return a UI-ready snapshot. Must not print.
        Includes only NEW messages since the last get_view() call.
        """
        scene = self._current_scene()
        actions_view = self._build_actions_view(scene)

        status = {
            "name": self.player.name if self.player else "",
            "health": self.player.health if self.player else 0,
            "score": self.player.score if self.player else 0,
            "hints_left": self.player.hints_left if self.player else 0,
            "inventory": list(self.player.inventory) if self.player else [],
            "inventory_text": format_inventory(self.player.inventory) if self.player else "Empty",
            "location_title": scene.title,
            "visited_count": len(self.state.visited_scenes) if self.state else 0,
            "path_highlights": self._build_path_highlights(limit=8),
        }

        new_messages = self._drain_messages()

        return {
            "scene_id": scene.scene_id,
            "title": scene.title,
            "description": scene.description,
            "actions": actions_view,
            "status": status,
            "game_over": bool(self.state.game_over) if self.state else False,
            "ending_type": self.state.ending if self.state else None,
            "ending_text": self.state.ending_text if self.state else "",
            "new_messages": new_messages,
        }

    def get_new_messages(self) -> list[str]:
        """Return and clear queued messages."""
        return self._drain_messages()

    def submit(self, raw_command: str) -> None:
        """
        Process exactly one command. Update internal state. Push messages.
        This method must implement:
          - global commands: help, status, hint, save, load, quit, use <item>
          - scene actions
          - puzzle command: code XXX (vault lock)
        For 'quit', do NOT exit the program (core must be UI-agnostic). Instead:
          - set state.game_over = True and ending_type = "quit" (or set a flag).
        """
        if not self.player or not self.state:
            self._push("Game not started.")
            return

        command = normalize_command(raw_command)
        if not command:
            return

        scene = self._current_scene()

        # 1) Global commands
        if self._handle_global(command, scene):
            return

        # 2) Special handler (puzzle)
        if scene.special_handler == "vault_code" and command.startswith("code"):
            self._handle_vault_code(command)
            return

        # 3) Scene command -> Action
        action = self._find_action(scene, command)
        if action is None:
            self._push("Unknown command. Type 'help' to see options.")
            return

        if not self._requirements_met(action):
            self._push(action.blocked_text)
            return

        if action.effects:
            self._apply_effects(action.effects)
            if self.state.game_over:
                return

        if action.result_text:
            self._push(action.result_text)

        if action.target and not self.state.game_over:
            self._enter_scene(action.target)

    # --------------------
    # INTERNAL HELPERS
    # --------------------

    def _push(self, text: str) -> None:
        self._messages.append(text)

    def _drain_messages(self) -> list[str]:
        msgs = self._messages[:]
        self._messages.clear()
        return msgs

    def _ensure_default_flags(self) -> None:
        """Ensure flags used by scenes exist with safe defaults."""
        if not self.state:
            return
        defaults = {
            "camp_chest_opened": False,
            "rested_once": False,
            "torch_taken": False,
            "read_riddle": False,
            "desk_checked": False,
            "took_key": False,
            "moon_phrase": False,
            "gate_unlocked": False,
            "took_disk": False,
            "saw_mirror_signal": False,
            "knows_code": False,
            "vault_solved": False,
            "wrong_code_attempts": 0,
        }
        for k, v in defaults.items():
            self.state.flags.setdefault(k, v)

    def _current_scene(self) -> Scene:
        if not self.state:
            raise RuntimeError("State not initialized.")
        scene = self.scenes.get(self.state.current_scene_id)
        if not scene:
            raise RuntimeError(f"Unknown scene: {self.state.current_scene_id}")
        return scene

    def _build_actions_view(self, scene: Scene) -> list[ViewAction]:
        out: list[ViewAction] = []
        for a in scene.actions:
            enabled = self._requirements_met(a)
            va: ViewAction = {"command": a.command, "label": a.label, "enabled": enabled}
            if not enabled:
                va["blocked_reason"] = a.blocked_text
            out.append(va)
        # Optionally expose puzzle helper in UI:
        if scene.special_handler == "vault_code":
            out.append({"command": "code XXX", "label": "Enter a 3-digit code (example: code 274)", "enabled": True})
        return out

    def _find_action(self, scene: Scene, command: str) -> Action | None:
        for a in scene.actions:
            if a.matches(command):
                return a
        return None

    def _requirements_met(self, action: Action) -> bool:
        if not self.player or not self.state:
            return False
        for item_id in action.required_items:
            if not self.player.has_item(item_id):
                return False
        for flag_name, expected in action.required_flags.items():
            current = self.state.flags.get(flag_name)
            if current != expected:
                return False
        return True

    def _apply_effects(self, effects: dict[str, Any]) -> None:
        """Apply effects to player/state, push user-facing messages. Must not print."""
        if not self.player or not self.state:
            return

        # score
        score_delta = int(effects.get("score", 0) or 0)
        if score_delta:
            self.player.score += score_delta

        # items
        for item in effects.get("add_items", []) or []:
            item_id = str(item)
            if self.player.add_item(item_id):
                self._push(f"Item acquired: {ITEM_LABELS.get(item_id, item_id)}")

        for item in effects.get("remove_items", []) or []:
            item_id = str(item)
            if self.player.remove_item(item_id):
                self._push(f"Item used: {ITEM_LABELS.get(item_id, item_id)}")

        # health
        health_delta = int(effects.get("health", 0) or 0)
        if health_delta:
            before = self.player.health
            self.player.health = clamp(self.player.health + health_delta, 0, MAX_HEALTH)
            diff = self.player.health - before
            if diff > 0:
                self._push(f"Health +{diff}")
            elif diff < 0:
                self._push(f"Health {diff}")

        # flags
        flags_update = effects.get("flags", {}) or {}
        if isinstance(flags_update, dict):
            self.state.flags.update(flags_update)

        # ending
        ending_type = effects.get("end")
        if isinstance(ending_type, str):
            self.state.game_over = True
            self.state.ending = ending_type
            self.state.ending_text = str(effects.get("ending_text", "The story ends here."))
            return

        if self.player.health <= 0 and not self.state.game_over:
            self.state.game_over = True
            self.state.ending = "bad"
            self.state.ending_text = "You collapse from your wounds. The island falls silent."

    def _enter_scene(self, scene_id: str) -> None:
        if not self.state:
            return
        scene = self.scenes.get(scene_id)
        if not scene:
            self.state.game_over = True
            self.state.ending = "bad"
            self.state.ending_text = "You wander into a path that shouldn't exist."
            return

        self.state.current_scene_id = scene_id
        self.state.visited_scenes.add(scene_id)
        self.state.history.append(scene_id)

        if scene.on_enter_effects:
            self._apply_effects(scene.on_enter_effects)
            if self.state.game_over:
                return

        # random events
        for ev in scene.random_events:
            flag_key = f"_event_{scene.scene_id}_{ev.event_id}"
            if ev.once and self.state.flags.get(flag_key, False):
                continue
            if self.rng.random() < ev.chance:
                self._push(ev.text)
                self._apply_effects(ev.effects)
                if self.state.game_over:
                    return
            if ev.once:
                self.state.flags[flag_key] = True

    def _handle_vault_code(self, command: str) -> None:
        """Puzzle: 'code 274'."""
        if not self.player or not self.state:
            return
        parts = command.split()
        if len(parts) != 2 or not parts[1].isdigit() or len(parts[1]) != 3:
            self._push("Invalid format. Example: code 274")
            return
        if parts[1] == "274":
            bonus = 12 if self.state.flags.get("knows_code") else 6
            self._apply_effects({"score": bonus, "flags": {"vault_solved": True}})
            self._push("The rune panel trembles. The lock clicks open.")
            self._enter_scene("treasure_room")
            return

        attempts = int(self.state.flags.get("wrong_code_attempts", 0)) + 1
        self.state.flags["wrong_code_attempts"] = attempts
        self._push("Wrong code. Needles snap out of the panel.")
        self._apply_effects({"health": -1, "score": -2})
        if not self.state.game_over and attempts >= 3:
            self.state.game_over = True
            self.state.ending = "bad"
            self.state.ending_text = "After three failures, the mechanism detonates and the chamber collapses."

    def _handle_global(self, command: str, scene: Scene) -> bool:
        """
        Implement global commands here, in the core, by pushing messages:
          - help -> push contextual + global command list
          - status -> push a formatted status block
          - hint -> consume hint and push hint text
          - save/load -> call persistence via save_game/load_game
          - quit -> set game_over + ending_type="quit"
          - use <item> -> apply item effects (healing herb)
        Return True if handled.
        """
        if not self.player or not self.state:
            return False

        if command == "help":
            lines = [f"Help - {scene.title}", "Scene commands:"]
            for action in self._build_actions_view(scene):
                line = f" - {action['command']}: {action['label']}"
                if not action.get("enabled", True):
                    line += f" [blocked: {action.get('blocked_reason', 'Unavailable')}]"
                lines.append(line)
            lines.extend(
                [
                    "Global commands:",
                    " - help",
                    " - status",
                    " - hint",
                    " - save",
                    " - load",
                    " - quit",
                    " - use <item>",
                ]
            )
            self._push("\n".join(lines))
            return True

        if command == "status":
            path = self._build_path_highlights(limit=8)
            lines = [
                "STATUS",
                f"Name: {self.player.name}",
                f"Health: {self.player.health}",
                f"Score: {self.player.score}",
                f"Hints left: {self.player.hints_left}",
                f"Location: {scene.title}",
                f"Inventory: {format_inventory(self.player.inventory)}",
                f"Visited areas: {len(self.state.visited_scenes)}",
            ]
            if path:
                lines.append("Path Summary: " + " -> ".join(path))
            self._push("\n".join(lines))
            return True

        if command == "hint":
            if self.player.hints_left <= 0:
                self._push("You have no hints left.")
                return True
            if not scene.hint_text:
                self._push("No hint is available for this area.")
                return True
            self.player.hints_left -= 1
            self._push(f"Hint: {scene.hint_text}\nHints remaining: {self.player.hints_left}")
            return True

        if command == "save":
            self.save_game()
            return True

        if command == "load":
            loaded, message = self.load_game()
            if loaded:
                self._push("Save loaded. Adventure resumed.")
            else:
                self._push(message)
            return True

        if command == "quit":
            self.state.game_over = True
            self.state.ending = "quit"
            self.state.ending_text = "You leave the island before its secrets are revealed."
            self._push("Closing game...")
            return True

        if command == "use" or command.startswith("use "):
            parts = command.split(maxsplit=1)
            if len(parts) != 2:
                self._push("Usage: use healing_herb")
                return True

            item_key = parts[1].strip().replace(" ", "_")
            if item_key in {"healing_herb", "herb"}:
                item_key = "sifali_ot"

            if item_key != "sifali_ot":
                self._push("That item cannot be used here.")
                return True

            if not self.player.has_item(item_key):
                self._push("You do not have a healing herb.")
                return True

            self.player.remove_item(item_key)
            previous = self.player.health
            self.player.health = clamp(self.player.health + 1, 0, MAX_HEALTH)
            gained = self.player.health - previous
            self._push(f"You used a healing herb. Health +{gained}.")
            return True

        return False

    def _build_path_highlights(self, limit: int = 8) -> list[str]:
        if not self.state:
            return []
        titles: list[str] = []
        for scene_id in dedupe_preserve_order(self.state.history):
            scene = self.scenes.get(scene_id)
            if scene:
                titles.append(scene.title)
            if len(titles) >= limit:
                break
        return titles
