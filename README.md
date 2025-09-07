# Primitive World Simulation

This is a minimal text-based world simulation game set in the stone age. Each new run generates a random world map with multiple continents. Every continent hosts a society that grows resources and population. NPC societies can raid their neighbors, and you can control one society to interact with others.

## Requirements

- Python 3.11+

## How to Play

Run the game:

```bash
python primitive_world.py
```

Follow the prompts to choose a society and issue commands each turn:
- `attack <id>` – raid a neighboring society.
- `stats` – view statistics for all societies.
- `quit` – exit the game.

For automated demonstration without interaction, run:

```bash
python primitive_world.py --autoplay 5
```

This will simulate five turns controlling the first society.

## Notes

This is a very lightweight prototype without graphics. It focuses on the core mechanics of map generation and simple societal interactions.
