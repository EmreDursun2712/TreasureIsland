"""PySide6 desktop GUI adapter for the Treasure Island core."""

from __future__ import annotations

import sys
from typing import Any, Mapping

try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction, QColor, QFont, QPalette
    from PySide6.QtWidgets import (
        QApplication,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenuBar,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSplitter,
        QStackedWidget,
        QTextEdit,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )
except ImportError as exc:  # pragma: no cover - runtime environment dependency
    raise SystemExit("PySide6 is not installed. Run: pip install pyside6") from exc

from core import GameCore, GameView


HOW_TO_PLAY_TEXT = (
    "Type short commands in each scene to make decisions.\n"
    "Goal: survive and find the island treasure.\n\n"
    "Global commands:\n"
    " - help\n"
    " - status\n"
    " - hint\n"
    " - save\n"
    " - load\n"
    " - quit\n"
    " - use <item>\n\n"
    "Special command in the rune lock scene:\n"
    " - code 274"
)

LIGHT_THEME_QSS = """
QWidget {
    color: #1a1a1a;
}
QMainWindow {
    background-color: #f4f1e8;
}
QLabel {
    color: #1a1a1a;
}
QGroupBox {
    color: #1a1a1a;
    border: 1px solid #bda97f;
    border-radius: 6px;
    margin-top: 10px;
    padding: 8px;
    background-color: #fffdf8;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #1a1a1a;
}
QTextEdit, QPlainTextEdit, QListWidget, QTreeView, QTableView {
    color: #1a1a1a;
    background-color: #ffffff;
    border: 1px solid #c9b892;
    border-radius: 6px;
    selection-background-color: #cfe8ff;
    selection-color: #111111;
}
QLineEdit {
    color: #1a1a1a;
    background-color: #ffffff;
    border: 1px solid #c9b892;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #cfe8ff;
    selection-color: #111111;
}
QPushButton {
    background-color: #264653;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 10px;
}
QPushButton:disabled {
    background-color: #c8d0d5;
    color: #4b5563;
}
QPushButton:hover:!disabled {
    background-color: #1f3842;
}
QMenuBar, QMenu, QToolBar, QToolButton {
    color: #1a1a1a;
    background-color: #f7f4ec;
}
QMenu::item:selected {
    background-color: #dbeafe;
    color: #111111;
}
QScrollArea {
    border: none;
}
"""


def apply_light_theme(app: QApplication) -> None:
    """Apply high-contrast light theme across platforms."""
    app.setStyle("Fusion")

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f4f1e8"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f7f4ec"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#f7f4ec"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#fffdf8"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#cfe8ff"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#111111"))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#5f6368"))
    app.setPalette(palette)

    app.setStyleSheet(LIGHT_THEME_QSS)


class TreasureIslandQt(QMainWindow):
    """Single-window GUI that talks only to GameCore."""

    def __init__(self) -> None:
        super().__init__()
        self.core = GameCore()
        self.current_view: GameView | None = None
        self.game_active = False
        self.ending_dialog_shown = False

        self._build_ui()
        self._build_menu_and_toolbar()
        self._set_game_actions_enabled(False)

        self.setWindowTitle("Treasure Island")
        self.resize(1100, 760)

    def _build_ui(self) -> None:
        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.start_page = QWidget(self)
        self.game_page = QWidget(self)
        self.stack.addWidget(self.start_page)
        self.stack.addWidget(self.game_page)

        self._build_start_page()
        self._build_game_page()
        self.stack.setCurrentWidget(self.start_page)

    def _build_start_page(self) -> None:
        layout = QVBoxLayout(self.start_page)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(16)

        title = QLabel("Treasure Island", self.start_page)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("A branching adventure powered by GameCore.", self.start_page)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        buttons_wrap = QWidget(self.start_page)
        buttons_layout = QVBoxLayout(buttons_wrap)
        buttons_layout.setSpacing(10)

        new_btn = QPushButton("New Game", buttons_wrap)
        load_btn = QPushButton("Load Game", buttons_wrap)
        how_btn = QPushButton("How to Play", buttons_wrap)
        exit_btn = QPushButton("Exit", buttons_wrap)

        for button in (new_btn, load_btn, how_btn, exit_btn):
            button.setMinimumHeight(44)
            buttons_layout.addWidget(button)

        new_btn.clicked.connect(self.start_new_game)
        load_btn.clicked.connect(self.load_game)
        how_btn.clicked.connect(self.show_how_to_play)
        exit_btn.clicked.connect(self.close)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(16)
        layout.addWidget(buttons_wrap, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()

    def _build_game_page(self) -> None:
        root = QVBoxLayout(self.game_page)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Top bar
        top_bar = QWidget(self.game_page)
        top_layout = QVBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2)

        self.game_title_label = QLabel("Treasure Island", top_bar)
        game_title_font = QFont()
        game_title_font.setPointSize(14)
        game_title_font.setBold(True)
        self.game_title_label.setFont(game_title_font)

        self.scene_title_label = QLabel("Current Scene", top_bar)
        scene_font = QFont()
        scene_font.setPointSize(22)
        scene_font.setBold(True)
        self.scene_title_label.setFont(scene_font)

        top_layout.addWidget(self.game_title_label)
        top_layout.addWidget(self.scene_title_label)
        root.addWidget(top_bar)

        # Main content
        splitter = QSplitter(Qt.Orientation.Horizontal, self.game_page)
        splitter.setChildrenCollapsible(False)

        left_panel = QWidget(splitter)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        desc_group = QGroupBox("Scene Description", left_panel)
        desc_layout = QVBoxLayout(desc_group)
        self.description_view = QTextEdit(desc_group)
        self.description_view.setReadOnly(True)
        self.description_view.setMinimumHeight(180)
        desc_layout.addWidget(self.description_view)

        log_group = QGroupBox("Adventure Log", left_panel)
        log_layout = QVBoxLayout(log_group)
        self.log_view = QTextEdit(log_group)
        self.log_view.setReadOnly(True)
        log_layout.addWidget(self.log_view)

        left_layout.addWidget(desc_group)
        left_layout.addWidget(log_group, stretch=1)

        right_panel = QWidget(splitter)
        right_layout = QVBoxLayout(right_panel)

        status_group = QGroupBox("Status", right_panel)
        status_layout = QVBoxLayout(status_group)
        self.status_view = QTextEdit(status_group)
        self.status_view.setReadOnly(True)
        self.status_view.setMinimumWidth(280)
        status_layout.addWidget(self.status_view)

        right_layout.addWidget(status_group)
        right_layout.addStretch()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, stretch=1)

        # Actions area
        actions_group = QGroupBox("Actions", self.game_page)
        actions_outer = QVBoxLayout(actions_group)

        self.actions_scroll = QScrollArea(actions_group)
        self.actions_scroll.setWidgetResizable(True)
        self.actions_container = QWidget(self.actions_scroll)
        self.actions_layout = QVBoxLayout(self.actions_container)
        self.actions_layout.setSpacing(8)
        self.actions_layout.setContentsMargins(6, 6, 6, 6)
        self.actions_scroll.setWidget(self.actions_container)
        actions_outer.addWidget(self.actions_scroll)
        root.addWidget(actions_group)

        # Command input
        cmd_row = QHBoxLayout()
        self.command_input = QLineEdit(self.game_page)
        self.command_input.setPlaceholderText("Type command (e.g. code 274, use healing_herb, help)...")
        send_btn = QPushButton("Send", self.game_page)
        send_btn.setMinimumWidth(100)

        self.command_input.returnPressed.connect(self.send_command_from_input)
        send_btn.clicked.connect(self.send_command_from_input)

        cmd_row.addWidget(self.command_input, stretch=1)
        cmd_row.addWidget(send_btn)
        root.addLayout(cmd_row)

    def _build_menu_and_toolbar(self) -> None:
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("&File")
        self.save_action = QAction("Save", self)
        self.load_action = QAction("Load", self)
        self.quit_action = QAction("Quit", self)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        help_menu = menu_bar.addMenu("&Help")
        self.how_action = QAction("How to Play", self)
        self.help_cmd_action = QAction("Submit 'help'", self)
        self.status_cmd_action = QAction("Submit 'status'", self)
        help_menu.addAction(self.how_action)
        help_menu.addSeparator()
        help_menu.addAction(self.help_cmd_action)
        help_menu.addAction(self.status_cmd_action)

        toolbar = QToolBar("Quick Actions", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.load_action)
        toolbar.addSeparator()
        toolbar.addAction(self.help_cmd_action)
        toolbar.addAction(self.status_cmd_action)

        self.save_action.triggered.connect(self.save_game)
        self.load_action.triggered.connect(self.load_game)
        self.quit_action.triggered.connect(self.close)
        self.how_action.triggered.connect(self.show_how_to_play)
        self.help_cmd_action.triggered.connect(lambda: self.submit_command("help"))
        self.status_cmd_action.triggered.connect(lambda: self.submit_command("status"))

    def _set_game_actions_enabled(self, enabled: bool) -> None:
        self.save_action.setEnabled(enabled)
        self.help_cmd_action.setEnabled(enabled)
        self.status_cmd_action.setEnabled(enabled)

    def _set_game_active(self, active: bool) -> None:
        self.game_active = active
        self._set_game_actions_enabled(active)
        if active:
            self.stack.setCurrentWidget(self.game_page)
        else:
            self.stack.setCurrentWidget(self.start_page)

    def start_new_game(self) -> None:
        name, accepted = QInputDialog.getText(self, "New Game", "Explorer name:")
        if not accepted:
            return
        self.core.new_game(name)
        self.ending_dialog_shown = False
        self._clear_log()
        self._set_game_active(True)
        self.refresh()

    def load_game(self) -> None:
        ok, message = self.core.load_game()
        if not ok:
            QMessageBox.warning(self, "Load Failed", message)
            return

        self.ending_dialog_shown = False
        self._clear_log()
        self._set_game_active(True)
        self.refresh()

    def save_game(self) -> None:
        if not self.game_active:
            QMessageBox.information(self, "Save", "Start or load a game first.")
            return

        ok, message = self.core.save_game()
        if not ok:
            self._append_log(message)
            QMessageBox.warning(self, "Save", message)
        self.refresh()

    def show_how_to_play(self) -> None:
        QMessageBox.information(self, "How to Play", HOW_TO_PLAY_TEXT)

    def send_command_from_input(self) -> None:
        raw_command = self.command_input.text().strip()
        if not raw_command:
            return
        self.command_input.clear()
        self.submit_command(raw_command)

    def submit_command(self, command: str) -> None:
        if not self.game_active:
            QMessageBox.information(self, "No Game", "Start or load a game first.")
            return
        self._append_log(f"> {command}")
        self.core.submit(command)
        self.refresh()

    def refresh(self) -> None:
        """Fetch `GameView` and redraw all UI sections."""
        if not self.game_active:
            return

        try:
            view = self.core.get_view()
        except RuntimeError as exc:
            QMessageBox.critical(self, "Game Error", str(exc))
            self._set_game_active(False)
            return

        self.current_view = view
        status = view["status"]

        self.scene_title_label.setText(view["title"])
        self.description_view.setPlainText(view["description"])
        self.status_view.setPlainText(self._format_status_text(status))

        self._rebuild_action_buttons(view["actions"])
        for message in view["new_messages"]:
            self._append_log(message)

        if view["game_over"] and not self.ending_dialog_shown:
            self.ending_dialog_shown = True
            self._show_ending_dialog(view)

    def _rebuild_action_buttons(self, actions: list[Mapping[str, Any]]) -> None:
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for action in actions:
            command = str(action.get("command", ""))
            label = str(action.get("label", command))
            enabled = bool(action.get("enabled", True))

            button = QPushButton(label, self.actions_container)
            button.setEnabled(enabled)
            if enabled:
                button.setToolTip(command)
            else:
                blocked_reason = str(action.get("blocked_reason", "Unavailable right now."))
                button.setToolTip(blocked_reason)
            button.clicked.connect(lambda _checked=False, cmd=command: self.submit_command(cmd))
            self.actions_layout.addWidget(button)

        self.actions_layout.addStretch()

    def _format_status_text(self, status: Mapping[str, Any]) -> str:
        inventory_text = str(status.get("inventory_text", "Empty"))
        lines = [
            f"Name: {status.get('name', '')}",
            f"Health: {status.get('health', 0)}",
            f"Score: {status.get('score', 0)}",
            f"Hints Left: {status.get('hints_left', 0)}",
            f"Inventory: {inventory_text}",
            f"Location: {status.get('location_title', '')}",
        ]
        return "\n".join(lines)

    def _show_ending_dialog(self, view: GameView) -> None:
        status = view["status"]
        ending_type = view["ending_type"] or "bad"
        ending_title = {
            "win": "Victory",
            "bad": "Game Over",
            "secret": "Secret Ending",
            "quit": "Journey Ended",
        }.get(ending_type, "Adventure Ended")
        ending_banner = {
            "win": "You found the treasure.",
            "bad": "Your expedition has ended.",
            "secret": "You uncovered a hidden fate of the island.",
            "quit": "You chose to leave for now.",
        }.get(ending_type, "The story has reached an ending.")

        icon = QMessageBox.Icon.Information
        if ending_type == "bad":
            icon = QMessageBox.Icon.Critical

        path_highlights = status.get("path_highlights", [])
        if not isinstance(path_highlights, list):
            path_highlights = []

        summary_lines = [
            ending_banner,
            "",
            f"Ending: {ending_type}",
            f"Score: {status.get('score', 0)}",
            f"Health Remaining: {status.get('health', 0)}",
            f"Inventory: {status.get('inventory_text', 'Empty')}",
        ]
        if path_highlights:
            summary_lines.append("Path Highlights: " + " -> ".join(str(p) for p in path_highlights))

        message_box = QMessageBox(self)
        message_box.setWindowTitle(ending_title)
        message_box.setIcon(icon)
        message_box.setText(view["ending_text"] or ending_banner)
        message_box.setInformativeText("\n".join(summary_lines))
        replay_button = message_box.addButton("Replay", QMessageBox.ButtonRole.AcceptRole)
        quit_button = message_box.addButton("Quit", QMessageBox.ButtonRole.RejectRole)
        message_box.setDefaultButton(replay_button)
        message_box.exec()

        if message_box.clickedButton() == replay_button:
            replay_name = str(status.get("name", "Explorer")).strip() or "Explorer"
            self.core.new_game(replay_name)
            self.ending_dialog_shown = False
            self._clear_log()
            self._set_game_active(True)
            self.refresh()
            return

        if message_box.clickedButton() == quit_button:
            self.close()

    def _append_log(self, text: str) -> None:
        if not text:
            return
        self.log_view.append(text)
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_log(self) -> None:
        self.log_view.clear()


def main() -> int:
    """Run the Qt desktop UI."""
    app = QApplication(sys.argv)
    apply_light_theme(app)
    window = TreasureIslandQt()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
