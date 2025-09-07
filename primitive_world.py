import random
import argparse
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

WATER = "~"

def generate_world(width: int, height: int, continents: int):
    """Generate a grid map with a given number of continents."""
    grid = [[WATER for _ in range(width)] for _ in range(height)]
    continent_cells: List[List[Tuple[int, int]]] = []

    for _ in range(continents):
        size = random.randint(width * height // 30, width * height // 15)
        # pick start cell
        while True:
            x = random.randrange(width)
            y = random.randrange(height)
            if grid[y][x] == WATER:
                break
        cells = {(x, y)}
        grid[y][x] = "0"  # temporary marker
        frontier = [(x, y)]
        while len(cells) < size and frontier:
            cx, cy = random.choice(frontier)
            nx = cx + random.randint(-1, 1)
            ny = cy + random.randint(-1, 1)
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] == WATER:
                grid[ny][nx] = "0"
                cells.add((nx, ny))
                frontier.append((nx, ny))
            else:
                frontier.remove((cx, cy))
        continent_cells.append(list(cells))

    # assign letters
    for idx, cells in enumerate(continent_cells):
        letter = chr(ord('A') + idx)
        for x, y in cells:
            grid[y][x] = letter

    return grid, continent_cells

@dataclass
class Society:
    ident: int
    name: str
    cells: List[Tuple[int, int]]
    population: int = 100
    resources: int = 100
    government: str = field(default_factory=lambda: random.choice(["tribal", "chiefdom"]))
    economy: str = field(default_factory=lambda: random.choice(["barter", "gift"]))
    tech_level: int = 1  # stone age
    neighbors: List[int] = field(default_factory=list)

    def grow(self):
        gained = random.randint(5, 15)
        self.resources += gained
        if self.resources > self.population:
            self.population += random.randint(0, 3)

    def summary(self) -> str:
        return (f"{self.name} - pop:{self.population} res:{self.resources} "
                f"gov:{self.government} eco:{self.economy} tech:{self.tech_level}")


def find_neighbors(societies: List[Society], width: int, height: int):
    pos_owner: Dict[Tuple[int, int], int] = {}
    for soc in societies:
        for x, y in soc.cells:
            pos_owner[(x, y)] = soc.ident
    for soc in societies:
        neighbor_ids = set()
        for x, y in soc.cells:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < width and 0 <= ny < height:
                    owner = pos_owner.get((nx, ny))
                    if owner is not None and owner != soc.ident:
                        neighbor_ids.add(owner)
        soc.neighbors = sorted(neighbor_ids)


def print_map(grid: List[List[str]]):
    for row in grid:
        print("".join(row))


def perform_attack(attacker: Society, defender: Society):
    if defender.ident not in attacker.neighbors:
        print("Target not adjacent.")
        return
    atk_power = attacker.resources + random.randint(0, attacker.population)
    def_power = defender.resources + random.randint(0, defender.population)
    if atk_power > def_power:
        print(f"{attacker.name} raids {defender.name} successfully!")
        loot = def_power // 2
        attacker.resources += loot
        defender.resources = max(0, defender.resources - loot)
        defender.population = max(0, defender.population - random.randint(5, 15))
    else:
        print(f"{attacker.name} fails to raid {defender.name}.")
        attacker.resources = max(0, attacker.resources - atk_power // 2)


def npc_turns(societies: List[Society], player_id: int, society_map: Dict[int, Society]):
    for soc in societies:
        if soc.ident == player_id:
            continue
        soc.grow()
        if soc.resources > 120 and soc.neighbors:
            target_id = random.choice(soc.neighbors)
            target = society_map[target_id]
            perform_attack(soc, target)


def run_game(width: int, height: int, continents: int, autoplay: int = 0):
    grid, cont_cells = generate_world(width, height, continents)
    societies = [Society(i, f"Society {chr(ord('A') + i)}", cells) for i, cells in enumerate(cont_cells)]
    find_neighbors(societies, width, height)
    society_map = {soc.ident: soc for soc in societies}

    player_id = 0
    if autoplay == 0:
        print("Select your society:")
        for soc in societies:
            print(f"{soc.ident}: {soc.name}")
        player_id = int(input("Enter id: "))
    player = society_map[player_id]

    turn = 1
    while True:
        if autoplay and turn > autoplay:
            break
        print(f"\nTurn {turn}")
        print_map(grid)
        print("\nYour society:")
        print(player.summary())
        if autoplay == 0:
            cmd = input("Command (enter to end, attack <id>, stats, quit): ").strip()
            if cmd == "quit":
                break
            if cmd.startswith("attack"):
                parts = cmd.split()
                if len(parts) == 2:
                    try:
                        target = society_map[int(parts[1])]
                        perform_attack(player, target)
                    except (KeyError, ValueError):
                        print("Invalid target")
            elif cmd == "stats":
                for soc in societies:
                    print(soc.summary())
        player.grow()
        npc_turns(societies, player_id, society_map)
        turn += 1


def main():
    parser = argparse.ArgumentParser(description="Stone age world simulation")
    parser.add_argument("--width", type=int, default=40)
    parser.add_argument("--height", type=int, default=20)
    parser.add_argument("--continents", type=int, default=3)
    parser.add_argument("--autoplay", type=int, default=0,
                        help="number of turns to run without user input")
    args = parser.parse_args()
    run_game(args.width, args.height, args.continents, args.autoplay)

if __name__ == "__main__":
    main()
