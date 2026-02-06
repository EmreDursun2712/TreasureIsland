"""CLI adapter for the UI-independent Treasure Island game core."""

from __future__ import annotations

from core import GameCore, GameView
import ui


class GameEngine:
    """Coordinate CLI menus, rendering, and player input."""

    def __init__(self) -> None:
        self.core = GameCore()
        self.exit_requested = False

    def run(self) -> None:
        """Start the application menu loop."""
        ui.print_logo()

        while not self.exit_requested:
            choice = ui.show_start_menu()
            if choice == "new":
                self._start_new_game()
                self._play_session_cycle()
            elif choice == "load":
                self._load_game_from_menu()
            elif choice == "how":
                ui.show_how_to_play()
            elif choice == "exit":
                self.exit_requested = True

        ui.print_goodbye()

    def _start_new_game(self) -> None:
        name = ui.ask_player_name()
        self.core.new_game(name)

    def _load_game_from_menu(self) -> None:
        success, message = self.core.load_game()
        if not success:
            ui.print_message(message)
            return
        self._play_session_cycle()

    def _play_session_cycle(self) -> None:
        """Play until game over, replay, or global quit."""
        while not self.exit_requested:
            final_view = self._play_until_end_or_exit()
            if final_view is None:
                return

            if final_view["ending_type"] == "quit":
                self.exit_requested = True
                return

            self._show_ending_summary(final_view)
            if ui.ask_replay():
                self._start_new_game()
                continue
            return

    def _play_until_end_or_exit(self) -> GameView | None:
        """Run loop until game over or the adapter exits."""
        while not self.exit_requested:
            view = self.core.get_view()
            self._render_view(view)
            if view["game_over"]:
                return view

            command = ui.prompt_input("> ")
            self.core.submit(command)

        return None

    def _render_view(self, view: GameView) -> None:
        ui.render_scene(view["title"], view["description"], view["actions"])
        ui.render_status_bar(view["status"])
        for message in view["new_messages"]:
            ui.print_message(message)

    def _show_ending_summary(self, view: GameView) -> None:
        status = view["status"]
        path_highlights = status.get("path_highlights", [])
        if not isinstance(path_highlights, list):
            path_highlights = []
        ui.show_ending(
            ending_type=view["ending_type"] or "bad",
            ending_text=view["ending_text"],
            status=status,
            path_highlights=[str(item) for item in path_highlights],
        )
