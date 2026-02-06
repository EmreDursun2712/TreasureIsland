"""Data-driven scene graph for Treasure Island."""

from __future__ import annotations

from models import Action, RandomEvent, Scene


def build_scenes() -> dict[str, Scene]:
    """Build and return all scene definitions."""
    return {
        "camp": Scene(
            scene_id="camp",
            title="Shore Camp",
            description=(
                "Night is fading.\n"
                "A cold firepit and a torn map lie at your feet.\n"
                "Mist drifts over the path into the forest."
            ),
            hint_text="Do not stay in camp too long. The trail is where the story starts.",
            actions=[
                Action("proceed", "Step onto the misty trail.", target="crossroad", effects={"score": 2}),
                Action(
                    "chest",
                    "Search the old camp chest.",
                    required_flags={"camp_chest_opened": False},
                    effects={
                        "add_items": ["bakir_para"],
                        "flags": {"camp_chest_opened": True},
                        "score": 4,
                    },
                    result_text="You find a copper coin and a faded note.",
                    blocked_text="The chest has nothing useful left.",
                ),
                Action(
                    "rest",
                    "Take a short rest.",
                    required_flags={"rested_once": False},
                    effects={"health": 1, "flags": {"rested_once": True}},
                    result_text="You steady your breathing. Health +1.",
                    blocked_text="If you linger longer, the mist will close in.",
                ),
            ],
        ),
        "crossroad": Scene(
            scene_id="crossroad",
            title="Fork in the Path",
            description=(
                "A cracked stone sign points in two directions.\n"
                "Water scent comes from the left. The right path is a dark cut in the earth."
            ),
            hint_text="Old tales suggest the first safe turn is left.",
            actions=[
                Action("left", "Take the left path.", target="lake_shore", effects={"score": 5}),
                Action("right", "Take the right path.", target="pitfall"),
                Action("tracks", "Follow the strange footprints.", target="marsh", effects={"score": 2}),
            ],
        ),
        "pitfall": Scene(
            scene_id="pitfall",
            title="Collapsed Ground",
            description="The ground on the right path suddenly gives way.",
            on_enter_effects={
                "end": "bad",
                "ending_text": "You fall into a deep pit. The island swallows you whole.",
            },
        ),
        "lake_shore": Scene(
            scene_id="lake_shore",
            title="Silent Lake",
            description=(
                "The forest opens to a still lake.\n"
                "In the center, an island house waits in the fog."
            ),
            hint_text="Swimming looks faster, but this water is too quiet.",
            actions=[
                Action("wait", "Wait for a boat at the shore.", target="island_dock", effects={"score": 5}),
                Action("swim", "Try to swim across.", target="drowned"),
                Action("reeds", "Move toward the reeds by the lake.", target="marsh"),
            ],
        ),
        "drowned": Scene(
            scene_id="drowned",
            title="Dark Water",
            description="The lake twists into a hungry current.",
            on_enter_effects={
                "end": "bad",
                "ending_text": "An undercurrent drags you under. Your trail vanishes.",
            },
        ),
        "island_dock": Scene(
            scene_id="island_dock",
            title="Island Dock",
            description=(
                "You step onto a rotten dock.\n"
                "A house, a tower, and a marsh path stretch ahead."
            ),
            hint_text="The doors in the house are central, but the tower hides key pieces too.",
            actions=[
                Action("house", "Head for the dim house.", target="house_hall", effects={"score": 2}),
                Action("tower", "Climb the stone tower.", target="watchtower"),
                Action("marsh", "Take the path into the marsh.", target="marsh"),
            ],
        ),
        "house_hall": Scene(
            scene_id="house_hall",
            title="Hall of Three Doors",
            description=(
                "The air turns cold.\n"
                "Three doors stand ahead: red, yellow, blue."
            ),
            hint_text="Do not assume red only means danger. Sometimes fire gives tools.",
            actions=[
                Action("red", "Enter the red door.", target="red_room"),
                Action("yellow", "Enter the yellow door.", target="yellow_room"),
                Action("blue", "Enter the blue door.", target="blue_room"),
                Action("back", "Return to the dock.", target="island_dock"),
            ],
        ),
        "red_room": Scene(
            scene_id="red_room",
            title="Ember Room",
            description=(
                "Heat drips off the walls.\n"
                "A tar-coated torch leans in the corner."
            ),
            hint_text="The torch can break through the blue door's darkness.",
            actions=[
                Action(
                    "torch",
                    "Take the torch and return to the hall.",
                    target="house_hall",
                    required_flags={"torch_taken": False},
                    effects={"add_items": ["mesale"], "flags": {"torch_taken": True}, "score": 10},
                    result_text="You grip the torch. The flame burns steady.",
                    blocked_text="The torch bracket is already empty.",
                ),
                Action("back", "Retreat before the heat takes you.", target="house_hall"),
            ],
        ),
        "blue_room": Scene(
            scene_id="blue_room",
            title="Blue Gloom",
            description=(
                "The ceiling disappears into shadow.\n"
                "A dark library corridor stretches ahead."
            ),
            hint_text="A lit torch is the only safe way through this corridor.",
            actions=[
                Action(
                    "forward",
                    "Advance into the corridor.",
                    target="library",
                    required_items=["mesale"],
                    effects={"score": 8},
                    blocked_text="Claws scrape in the dark. You need a torch first.",
                ),
                Action("touch", "Touch the hanging chain in the dark.", target="beast_den"),
                Action("back", "Return to the hall.", target="house_hall"),
            ],
        ),
        "beast_den": Scene(
            scene_id="beast_den",
            title="Hunter's Den",
            description="The chain rattle wakes something huge in the room.",
            on_enter_effects={
                "end": "bad",
                "ending_text": "A beast lunges from the dark. The blue door becomes your last step.",
            },
        ),
        "library": Scene(
            scene_id="library",
            title="Dustbound Library",
            description=(
                "Stone shelves, moss scent, and a rusted stair.\n"
                "A rune-carved book rests on a pedestal."
            ),
            hint_text="The runes in the book form the core of the vault code.",
            actions=[
                Action(
                    "book",
                    "Read the rune-marked book.",
                    required_flags={"read_riddle": False},
                    effects={"flags": {"read_riddle": True, "knows_code": True}, "score": 8},
                    result_text="A line appears: 'The moon step is 2-7-4.'",
                    blocked_text="You read the same page again. Nothing new appears.",
                ),
                Action("stairs", "Climb the rusted stair to the tower.", target="watchtower", effects={"score": 2}),
                Action("tunnel", "Take the narrow tunnel to the yellow room.", target="yellow_room"),
                Action("back", "Return to the blue room.", target="blue_room"),
            ],
        ),
        "yellow_room": Scene(
            scene_id="yellow_room",
            title="Yellow Chamber",
            description=(
                "This room feels calmer than the rest.\n"
                "There is a desk, a garden gate, and a sealed stone passage."
            ),
            hint_text="The garden hides a key, and the desk repeats a clue.",
            actions=[
                Action(
                    "desk",
                    "Inspect the etched marks on the desk.",
                    required_flags={"desk_checked": False},
                    effects={"flags": {"desk_checked": True, "knows_code": True}, "score": 6},
                    result_text="The same numbers repeat in scratches: 2, 7, 4.",
                    blocked_text="You find no new marks on the desk.",
                ),
                Action("garden", "Step into the garden.", target="garden"),
                Action(
                    "gate",
                    "Approach the stone passage.",
                    target="cave_gate",
                    required_items=["gumus_anahtar"],
                    blocked_text="The passage demands a silver key.",
                ),
                Action("back", "Return to the hall.", target="house_hall"),
            ],
        ),
        "garden": Scene(
            scene_id="garden",
            title="Moon Garden",
            description=(
                "Broken statues gleam under pale moonlight.\n"
                "The soil near one plinth looks recently disturbed."
            ),
            hint_text="Dig the loose soil. Read the statue base as well.",
            actions=[
                Action(
                    "dig",
                    "Dig into the loose soil.",
                    required_flags={"took_key": False},
                    effects={"add_items": ["gumus_anahtar"], "flags": {"took_key": True}, "score": 10},
                    result_text="You pull a silver key from the earth.",
                    blocked_text="The pit is empty now.",
                ),
                Action(
                    "statue",
                    "Read the writing on the statue base.",
                    required_flags={"moon_phrase": False},
                    effects={"flags": {"moon_phrase": True}, "score": 4},
                    result_text="It reads: 'The moon disk wakes at the silent door.'",
                    blocked_text="The phrase is already etched into your memory.",
                ),
                Action("back", "Return to the yellow chamber.", target="yellow_room"),
            ],
        ),
        "watchtower": Scene(
            scene_id="watchtower",
            title="Watchtower",
            description=(
                "Wind moans through cracked stone.\n"
                "A half-open chest and a broken spyglass face the island."
            ),
            hint_text="The chest holds a key relic. You need it for the secret ending.",
            random_events=[
                RandomEvent(
                    event_id="tower_slip",
                    text="You slip on a wet step and scrape your arm. Health -1.",
                    chance=0.25,
                    effects={"health": -1},
                    once=True,
                )
            ],
            actions=[
                Action(
                    "chest",
                    "Open the tower chest.",
                    required_flags={"took_disk": False},
                    effects={"add_items": ["ay_diski"], "flags": {"took_disk": True}, "score": 9},
                    result_text="Inside, you find a circular moon disk.",
                    blocked_text="The chest is empty.",
                ),
                Action(
                    "spyglass",
                    "Look through the spyglass toward the marsh.",
                    required_flags={"saw_mirror_signal": False},
                    effects={"flags": {"saw_mirror_signal": True}, "score": 3},
                    result_text="You spot a glint near a hidden stone gate in the marsh.",
                    blocked_text="The view shows nothing new now.",
                ),
                Action("down", "Go back down to the library stair.", target="library"),
                Action("dock", "Climb down toward the dock.", target="island_dock"),
                Action("marsh", "Take the outer trail into the marsh.", target="marsh"),
            ],
        ),
        "marsh": Scene(
            scene_id="marsh",
            title="Sinking Marsh",
            description=(
                "The mud drags at each step.\n"
                "A narrow path winds toward a stone wall."
            ),
            hint_text="The stone inscriptions may unlock the secret route.",
            random_events=[
                RandomEvent(
                    event_id="swamp_gas",
                    text="A pocket of toxic marsh gas bursts. Health -1.",
                    chance=0.45,
                    effects={"health": -1},
                    once=True,
                ),
                RandomEvent(
                    event_id="swamp_herb",
                    text="You spot a healing herb among the reeds.",
                    chance=0.35,
                    effects={"add_items": ["sifali_ot"], "score": 5},
                    once=True,
                ),
            ],
            actions=[
                Action(
                    "stone",
                    "Clean the stone slab and read it.",
                    required_flags={"moon_phrase": False},
                    effects={"flags": {"moon_phrase": True}, "score": 5},
                    result_text="The inscription repeats: 'The moon disk wakes at the silent door.'",
                    blocked_text="You already memorized the inscription.",
                ),
                Action("path", "Follow the narrow stone path.", target="cave_gate", effects={"score": 2}),
                Action("back", "Backtrack toward the fork.", target="crossroad"),
                Action("lake", "Return to the lake shore.", target="lake_shore"),
            ],
        ),
        "cave_gate": Scene(
            scene_id="cave_gate",
            title="Stone Gate",
            description=(
                "A massive stone gate is etched with runes.\n"
                "Its lock socket is lined with silver."
            ),
            hint_text="Open the gate by using the key first, then move forward.",
            actions=[
                Action(
                    "key",
                    "Insert the silver key into the lock.",
                    required_items=["gumus_anahtar"],
                    required_flags={"gate_unlocked": False},
                    effects={"flags": {"gate_unlocked": True}, "score": 7},
                    result_text="The lock teeth shift. The gate opens.",
                    blocked_text="Either you lack the key, or the gate is already unlocked.",
                ),
                Action(
                    "forward",
                    "Enter through the opened gate.",
                    target="vault_lock",
                    required_flags={"gate_unlocked": True},
                    blocked_text="The gate is still sealed.",
                ),
                Action("back", "Return to the yellow chamber.", target="yellow_room"),
                Action("marsh", "Head back into the marsh.", target="marsh"),
            ],
        ),
        "vault_lock": Scene(
            scene_id="vault_lock",
            title="Rune Lock",
            description=(
                "You enter a narrow chamber.\n"
                "A 3-digit rune panel waits ahead.\n"
                "Type 'code XXX' to input a code."
            ),
            hint_text="The code is repeated in clues scattered across the island.",
            special_handler="vault_code",
            actions=[
                Action(
                    "disk",
                    "Place the moon disk into the hidden slot below the panel.",
                    target="secret_sanctum",
                    required_items=["ay_diski"],
                    required_flags={"moon_phrase": True},
                    effects={"score": 15},
                    result_text="The disk locks in place, and a hidden wall slides open.",
                    blocked_text="You have not unlocked the phrase that activates the disk.",
                ),
                Action("back", "Return to the stone gate.", target="cave_gate"),
            ],
        ),
        "treasure_room": Scene(
            scene_id="treasure_room",
            title="Treasure Vault",
            description="The rune door opens, revealing a chamber full of gold.",
            on_enter_effects={
                "score": 30,
                "end": "win",
                "ending_text": "You found the ancient treasure. The island accepts you.",
            },
        ),
        "secret_sanctum": Scene(
            scene_id="secret_sanctum",
            title="Secret Sanctum",
            description="Beyond the vault lies a hidden moon sanctum untouched for ages.",
            on_enter_effects={
                "score": 45,
                "end": "secret",
                "ending_text": "You awakened the moon sanctum and uncovered the island's deepest secret.",
            },
        ),
    }
