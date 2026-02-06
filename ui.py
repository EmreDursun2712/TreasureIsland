"""Console rendering and input helpers."""

from __future__ import annotations

from typing import Any, Mapping

from utils import format_inventory, normalize_command

GLOBAL_COMMANDS: tuple[str, ...] = ("help", "status", "hint", "save", "load", "quit", "use <item>")


def print_logo() -> None:
    """Render title art."""
    print(
        r"""
  _____                                _____     _                 _ 
 |_   _|                              |_   _|   | |               | |
   | | _ __ ___  __ _ ___ _   _ _ __    | |  ___| | __ _ _ __   __| |
   | || '__/ _ \/ _` / __| | | | '__|   | | / __| |/ _` | '_ \ / _` |
  _| || | |  __/ (_| \__ \ |_| | |     _| |_\__ \ | (_| | | | | (_| |
  \___/_|  \___|\__,_|___/\__,_|_|     \___/|___/_|\__,_|_| |_|\__,_|
        """
    )
    print("Welcome to the misty island. Will you find the treasure?\n")


def print_divider() -> None:
    """Print a visual divider."""
    print("-" * 72)


def print_message(text: str) -> None:
    """Print a plain message line."""
    print(text)


def prompt_input(prompt: str = "> ") -> str:
    """Read input safely without crashing on EOF/interrupt."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return "quit"


def ask_player_name() -> str:
    """Prompt player name with fallback."""
    print_divider()
    name = prompt_input("Explorer, what is your name? ").strip()
    return name if name else "Wanderer"


def show_start_menu() -> str:
    """Render and resolve main menu selection."""
    options = {
        "1": "new",
        "2": "load",
        "3": "how",
        "4": "exit",
        "new": "new",
        "load": "load",
        "how": "how",
        "exit": "exit",
    }

    while True:
        print_divider()
        print("1) New Game")
        print("2) Load Game")
        print("3) How to Play")
        print("4) Exit")
        choice = normalize_command(prompt_input("Select > "))
        selected = options.get(choice)
        if selected:
            return selected
        print("Invalid selection. Enter a value between 1 and 4.")


def show_how_to_play() -> None:
    """Display quick instructions."""
    print_divider()
    print("HOW TO PLAY")
    print("Type short commands in each scene to make decisions.")
    print("Your goal is to survive and find the island treasure.")
    print("Global commands:")
    for command in GLOBAL_COMMANDS:
        print(f" - {command}")
    print("Extra command: use healing_herb (if in inventory, restores 1 health).")
    print("Hints are limited, so use them wisely.\n")


def render_scene(title: str, description: str, actions: list[Mapping[str, Any]]) -> None:
    """Render current scene and available local actions."""
    print_divider()
    print(f"[{title}]")
    print(description)
    print()
    print("Commands you can try in this scene:")
    for action in actions:
        command = str(action.get("command", ""))
        label = str(action.get("label", ""))
        enabled = bool(action.get("enabled", True))
        if enabled:
            print(f" - {command}: {label}")
        else:
            print(f" - {command}: {label} [blocked]")
    print()


def render_status_bar(status: Mapping[str, Any]) -> None:
    """Render compact status line from the core view-model."""
    name = str(status.get("name", ""))
    health = status.get("health", 0)
    score = status.get("score", 0)
    hints_left = status.get("hints_left", 0)
    location = str(status.get("location_title", ""))
    inventory_text = status.get("inventory_text")
    if not isinstance(inventory_text, str):
        inventory_text = format_inventory(status.get("inventory", []))
    print(f"Status | {name} | HP {health} | Score {score} | Hints {hints_left} | {location}")
    print(f"Inventory: {inventory_text}")
    print()


def show_ending(ending_type: str, ending_text: str, status: Mapping[str, Any], path_highlights: list[str]) -> None:
    """Render ending splash and summary."""
    banner_map = {
        "win": "== VICTORY ==",
        "bad": "== GAME OVER ==",
        "secret": "== SECRET ENDING ==",
        "quit": "== JOURNEY ENDED ==",
    }
    print_divider()
    print(banner_map.get(ending_type, "== END =="))
    print(ending_text)
    print()
    print(f"Score: {status.get('score', 0)}")
    print(f"Health Remaining: {status.get('health', 0)}")
    inventory_text = status.get("inventory_text")
    if not isinstance(inventory_text, str):
        inventory_text = format_inventory(status.get("inventory", []))
    print(f"Inventory: {inventory_text}")
    if path_highlights:
        print("Path Summary: " + " -> ".join(path_highlights))
    print()


def ask_replay() -> bool:
    """Ask if the player wants to replay."""
    while True:
        answer = normalize_command(prompt_input("Do you want to play again? (yes/no) > "))
        if answer in {"yes", "y"}:
            return True
        if answer in {"no", "n"}:
            return False
        print("Please type yes or no.")


def print_goodbye() -> None:
    """Render closing line."""
    print("\nThe wind swallows your footsteps. Until next time.")
