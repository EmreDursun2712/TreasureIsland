# 🏝️ Treasure Island (CLI + Qt GUI)

A text-based adventure game where you explore a mysterious island, collect items, solve a small puzzle, and hunt for the treasure — now with both **CLI** and **Qt Desktop GUI**.

## 🧠 What It Does

- Story-driven adventure with **12+ scenes**
- Multiple endings:
  - ✅ Win ending
  - 💀 Bad ending
  - 🌙 Secret ending
- Inventory system (collect & use items)
- Hint system (limited uses)
- Random events (safe randomness, doesn’t break the game)
- Save / Load support (`savegame.json`)

## 🧩 Tech Stack

- Python 3.10+
- Qt Desktop GUI:
  - **PySide6** (recommended) or **PyQt6**
- Standard library only for core game logic

## 📁 Project Structure

```text
Treasure Island/
├── app.py            # CLI entry point
├── core.py           # UI-independent game logic (no print/input)
├── engine.py         # CLI adapter (renders core state)
├── gui_qt.py         # Qt GUI entry point
├── scenes.py         # Scene graph (data-driven)
├── models.py         # Dataclasses (Player, GameState, Scene, Action)
├── persistence.py    # Save/Load JSON
├── utils.py          # Helpers
└── ui.py             # CLI rendering helpers
```

> `savegame.json` and `__pycache__/` are runtime artifacts (generated when you run the game).

## 🚀 Run It Yourself

### 1) Clone

```bash
git clone <YOUR_REPO_URL>
cd "Treasure Island"
```

### 2) Run CLI

```bash
python3 app.py
```

### 3) Run GUI (Qt)

Install Qt binding (choose one):

**PySide6 (recommended):**

```bash
pip install pyside6
python3 gui_qt.py
```

**OR PyQt6:**

```bash
pip install pyqt6
python3 gui_qt.py
```

## 🎮 How to Play (Commands)

In both CLI and GUI, you can use scene commands (e.g. `left`, `wait`, `red`) plus global commands:

- `help` → show available commands
- `status` → show player stats (health/score/inventory/hints)
- `hint` → get a hint (limited uses)
- `save` → save to `savegame.json`
- `load` → load from `savegame.json`
- `quit` → quit gracefully
- `use <item>` → use an item (example: `use healing_herb`)

> Some scenes may accept special commands like `code 274`.

## 🧾 Example

- You reach a locked rune panel and try:
  - `hint`
  - `code 274`
- If you fail too many times, you may trigger a bad ending.

## 🖼️ Screenshots (Optional)

Add your screenshots under a `screenshots/` folder and reference them here.

```md
![GUI](screenshots/gui.png)
```

### 🧑‍💻 Author 
**[Emre Dursun](https://github.com/EmreDursun2712)**
