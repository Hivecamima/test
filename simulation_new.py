import csv
import random

# Define constants
NUM_POSSESSIONS = 100

# Load player data from file
players = []
with open("output.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        players.append(row)

# Display team names and return the set of team names
def display_teams(players):
    teams = set(player["team"] for player in players)
    for team in sorted(teams):
        print(team)
    return teams

# Prompt the user to select a team and return the selected team name
def select_team(teams, prompt):
    while True:
        team_name = input(prompt)
        if team_name in teams:
            return team_name
        print("Invalid team name. Please try again.")

# Display the starters for a given team and return a list of the selected starters
def select_starters(team_name, players):
    team_players = [player for player in players if player["team"] == team_name]
    for idx, player in enumerate(team_players):
        print(f"{idx + 1}. {player['name']} ({player['overallAttribute']})")

    starters = []
    for i in range(5):
        starter_idx = int(input(f"Select starter {i + 1}: ")) - 1
        starters.append(team_players[starter_idx])
    return starters

# Define Stat Names for Dictionary
def initialize_player_stats():
    return {
        "points": 0,
        "rebounds": 0,
        "assists": 0,
        "steals": 0,
        "blocks": 0,
        "field_goals_attempted": 0,
        "field_goals_made": 0,
        "three_points_attempted": 0,
        "three_points_made": 0,
        "free_throws_attempted": 0,
        "free_throws_made": 0,
        "field_goal_percentage": 0,
        "three_point_percentage": 0,
        "free_throw_percentage": 0
}

# Calculate the probability that a player will score on a given possession
def calculate_scoring_probability(player):
    shot_types = ["closeShot", "midRangeShot", "threePointShot"]
    probabilities = [float(player[shot_type]) for shot_type in shot_types]
    total_shot_iq = sum(probabilities)
    scoring_prob = sum(prob * float(player["shotIQ"]) for prob in probabilities) / (total_shot_iq * 100)
    return scoring_prob

# Calculate the defensive impact of a player
def calculate_defensive_impact(defense):
    defense_attributes = ["interiorDefense", "perimeterDefense", "steal", "block"]
    impact = sum(float(defense[attr]) for attr in defense_attributes) / (4 * 100)
    return impact

# Update a player's defensive stats
def update_defensive_stats(game_result, defense, offense, success):
    # Update defensive player's stats
    game_result[defense["team"]][defense["name"]]["rebounds_defended"] += 1
    game_result[defense["team"]][defense["name"]]["steals"] += 1 if not success else 0
    game_result[defense["team"]][defense["name"]]["blocks"] += 1 if not success else 0

    # Update team defensive stats
    team_defense = game_result[defense["team"]]
    team_defense["points_allowed"] = team_defense.get("points_allowed", 0) + 1 if not success else team_defense.get("points_allowed", 0)
    team_defense["field_goals_attempted_defended"] = team_defense.get("field_goals_attempted_defended", 0) + 1
    team_defense["field_goals_made_defended"] = team_defense.get("field_goals_made_defended", 0) + 1 if not success else team_defense.get("field_goals_made_defended", 0)
    team_defense["three_points_attempted_defended"] = team_defense.get("three_points_attempted_defended", 0) + 1 if offense["three_point_shot"] else team_defense.get("three_points_attempted_defended", 0)
    team_defense["three_points_made_defended"] = team_defense.get("three_points_made_defended", 0) + 1 if success and offense["three_point_shot"] else team_defense.get("three_points_made_defended", 0)
    team_defense["free_throws_attempted_defended"] = team_defense.get("free_throws_attempted_defended", 0) + 1 if offense["foul_shot"] else team_defense.get("free_throws_attempted_defended", 0)
    team_defense["free_throws_made_defended"] = team_defense.get("free_throws_made_defended", 0) + 1 if success and offense["foul_shot"] else team_defense.get("free_throws_made_defended", 0)
    team_defense["rebounds_defended"] = team_defense.get("rebounds_defended", 0) + 1 if not success else team_defense.get("rebounds_defended", 0)
        
    defense_attributes = ["interiorDefense", "perimeterDefense", "steal", "block"]
    defensive_stats = sum(float(defense[attr]) for attr in defense_attributes) / (4 * 100)
    return defensive_stats

# Calculate the number of points scored on a given possession
def calculate_points_scored(player):
    shot_probabilities = {
        "closeShot": (float(player["closeShot"]) + float(player["layup"]) + float(player["standingDunk"]) + float(player["drivingDunk"])) / 400,
        "midRangeShot": float(player["midRangeShot"]) / 100,
        "threePointShot": float(player["threePointShot"]) / 100
        }

    shot_type = random.choices(list(shot_probabilities.keys()), weights=list(shot_probabilities.values()))[0]
    if shot_type in ["closeShot", "midRangeShot"]:
        return 2
    else:
        return 3

# Simulate a single offensive possession and return whether it was successful or not
def run_offensive_possession(offense, defense):
    scoring_probability = calculate_scoring_probability(offense)
    defensive_impact = calculate_defensive_impact(defense)
    
    success_probability = scoring_probability * (1 - defensive_impact)
    
    success = random.random() < success_probability
    return success

# Update game result based on the outcome of an offensive possession
def update_offensive_stats(game_result, offense, defense, success):
    points = calculate_points_scored(offense) if success else 0

# Update offensive stats for the scoring player
    if offense["team"] not in game_result:
        game_result[offense["team"]] = {}
    if offense["name"] not in game_result[offense["team"]]:
        game_result[offense["team"]][offense["name"]] = {"points": 0, "rebounds": 0, "assists": 0, "steals": 0, "blocks": 0, "field_goals_attempted": 0, "field_goals_made": 0}
    
    game_result[offense["team"]][offense["name"]]["points"] += points
    game_result[offense["team"]][offense["name"]]["field_goals_attempted"] += 1

    if points == 2:
        game_result[offense["team"]][offense["name"]]["field_goals_made"] += 1

    if points == 3:
        game_result[offense["team"]][offense["name"]]["field_goals_made"] += 1
        game_result[offense["team"]][offense["name"]]["three_points_attempted"] += 1
        game_result[offense["team"]][offense["name"]]["three_points_made"] += 1

# Update defensive stats for the defending player
    if defense["team"] not in game_result:
        game_result[defense["team"]] = {}   
    if defense["name"] not in game_result[defense["team"]]:
        game_result[defense["team"]][defense["name"]] = {"points": 0, "rebounds": 0, "assists": 0, "steals": 0, "blocks": 0}
        game_result[defense["team"]][defense["name"]]["rebounds"] += 1
        game_result[defense["team"]][defense["name"]]["steals"] += 1 if not success else 0
        game_result[defense["team"]][defense["name"]]["blocks"] += 1 if not success and (points == 2 or points == 3) else 0
	
# Simulate a single game and return the game result
def play_game(team1_starters, team2_starters):
    game_result = {"team1": {}, "team2": {}}
    for possession in range(NUM_POSSESSIONS):
        # Offensive possession
        offense = random.choice(team1_starters)
        defense = random.choice(team2_starters)
        success = run_offensive_possession(offense, defense)
        update_offensive_stats(game_result, offense, defense, success)
        update_defensive_stats(game_result, defense, offense, success)

        # Defensive possession
        offense = random.choice(team2_starters)
        defense = random.choice(team1_starters)
        success = run_offensive_possession(offense, defense)
        update_offensive_stats(game_result, offense, defense, success)
        update_defensive_stats(game_result, defense, offense, success)

    # Calculate final score
    team1_score = sum(player["points"] for player in game_result["team1"].values())
    team2_score = sum(player["points"] for player in game_result["team2"].values())
    game_result["team1_score"] = team1_score
    game_result["team2_score"] = team2_score

    # Determine the winner
    if team1_score > team2_score:
        game_result["winner"] = "team1"
    elif team2_score > team1_score:
        game_result["winner"] = "team2"
    else:
        game_result["winner"] = "tie"

    return game_result


# Set default values for stats if they don't exist
    for stat in ["points", "rebounds", "assists", "steals", "blocks", "field_goals_attempted", "field_goals_made", "three_points_attempted", "three_points_made", "free_throws_attempted", "free_throws_made", "field_goal_percentage", "three_point_percentage", "free_throw_percentage"]:
        game_result.setdefault(offense["team"], {}).setdefault(offense["name"], {}).setdefault(stat, 0)


# Swap offense and defense and repeat the process for the second half of the possession
    offense, defense = defense, offense
    success = run_offensive_possession(offense, defense)
    update_offensive_stats(game_result, offense, defense, success)

# Calculate final score
    team1_score = sum(player["points"] for player in game_result["team1"].values())
    team2_score = sum(player["points"] for player in game_result["team2"].values())
    game_result["team1_score"] = team1_score
    game_result["team2_score"] = team2_score

# Determine the winner
    if team1_score > team2_score:
        game_result["winner"] = "team1"
    elif team2_score > team1_score:
        game_result["winner"] = "team2"
    else:
        game_result["winner"] = "tie"

    return game_result

# Update the game results with the stats from a single game
def update_game_results(game_result, game_results):
    game_results["num_games"] += 1
    game_results[game_result["winner"]]["num_wins"] += 1
    game_results["team1_score"] += game_result["team1_score"]
    game_results["team2_score"] += game_result["team2_score"]
    for team_key in ["team1", "team2"]:
        for player_name in game_result[team_key].keys():
            for stat_key in game_result[team_key][player_name].keys():
                # Add the stats from the current game to the player's overall stats
                for overall_stat_key in ["points", "rebounds", "assists", "steals", "blocks"]:
                    game_results[team_key][player_name][overall_stat_key] += game_result[team_key][player_name][overall_stat_key]

                # Update shooting stats
                player_stats = game_results[team_key][player_name]
                field_goals_attempted = player_stats["field_goals_attempted"]
                field_goals_made = player_stats["field_goals_made"]
                three_points_attempted = player_stats["three_points_attempted"]
                three_points_made = player_stats["three_points_made"]
                free_throws_attempted = player_stats["free_throws_attempted"]
                free_throws_made = player_stats["free_throws_made"]

                if field_goals_attempted > 0:
                    player_stats["field_goal_percentage"] = field_goals_made / field_goals_attempted

                if three_points_attempted > 0:
                    player_stats["three_point_percentage"] = three_points_made / three_points_attempted

                if free_throws_attempted > 0:
                    player_stats["free_throw_percentage"] = free_throws_made / free_throws_attempted

# Run a simulation of multiple games and return the aggregated game results
def run_simulation(team1_starters, team2_starters, num_simulations):
    game_results = {
        "num_games": 0,
        "team1": {player["name"]: {"points": 0, "rebounds": 0, "assists": 0, "steals": 0, "blocks": 0, "field_goals_attempted": 0, "field_goals_made": 0, "three_points_attempted": 0, "three_points_made": 0, "free_throws_attempted": 0, "free_throws_made": 0, "field_goal_percentage": 0, "three_point_percentage": 0, "free_throw_percentage": 0} for player in team1_starters},
        "team2": {player["name"]: {"points": 0, "rebounds": 0, "assists": 0, "steals": 0, "blocks": 0, "field_goals_attempted": 0, "field_goals_made": 0, "three_points_attempted": 0, "three_points_made": 0, "free_throws_attempted": 0, "free_throws_made": 0, "field_goal_percentage": 0, "three_point_percentage": 0, "free_throw_percentage": 0} for player in team2_starters},
        "team1_score": 0,
        "team2_score": 0,
        "team1_wins": 0,
        "team2_wins": 0,
        "tie_games": 0
    }
    for i in range(num_simulations):
        game_result = play_game(team1_starters, team2_starters)
        update_game_results(game_result, game_results)

        # Update win counts
        if game_result["winner"] == "team1":
            game_results["team1_wins"] += 1
        elif game_result["winner"] == "team2":
            game_results["team2_wins"] += 1
        else:
            game_results["tie_games"] += 1

        # Calculate overall shooting percentages
        for team_key in ["team1", "team2"]:
            for player_name in game_results[team_key].keys():
                player_stats = game_results[team_key][player_name]
                field_goals_attempted = player_stats["field_goals_attempted"]
                field_goals_made = player_stats["field_goals_made"]
                three_points_attempted = player_stats["three_points_attempted"]
                three_points_made = player_stats["three_points_made"]
                free_throws_attempted = player_stats["free_throws_attempted"]
                free_throws_made = player_stats["free_throws_made"]

                if field_goals_attempted > 0:
                    player_stats["field_goal_percentage"] = field_goals_made / field_goals_attempted

                if three_points_attempted > 0:
                    player_stats["three_point_percentage"] = three_points_made / three_points_attempted

                if free_throws_attempted > 0:
                    player_stats["free_throw_percentage"] = free_throws_made / free_throws_attempted

    game_results["num_games"] = num_simulations
    return game_results

# defining the game results teamplate
# defining the game results template
def initialize_game_results(team1_starters, team2_starters):
    game_results = {
        "num_games": 0,
        "team1": {player["name"]: {"points": 0, "rebounds": 0, "assists": 0, "steals": 0, "blocks": 0, "field_goals_attempted": 0, "field_goals_made": 0, "three_points_attempted": 0, "three_points_made": 0, "free_throws_attempted": 0, "free_throws_made": 0, "field_goal_percentage": 0, "three_point_percentage": 0, "free_throw_percentage": 0, "rebounds_defended": 0} for player in team1_starters},
        "team2": {player["name"]: {"points": 0, "rebounds": 0, "assists": 0, "steals": 0, "blocks": 0, "field_goals_attempted": 0, "field_goals_made": 0, "three_points_attempted": 0, "three_points_made": 0, "free_throws_attempted": 0, "free_throws_made": 0, "field_goal_percentage": 0, "three_point_percentage": 0, "free_throw_percentage": 0, "rebounds_defended": 0} for player in team2_starters},
        "team1_score": 0,
        "team2_score": 0,
        "team1_wins": 0,
        "team2_wins": 0,
        "tie_games": 0
    }

    # Set all keys for offensive stats
    for team_key in ["team1", "team2"]:
        for player_name in game_results[team_key]:
            game_results[team_key][player_name].setdefault("points", 0)
            game_results[team_key][player_name].setdefault("rebounds", 0)
            game_results[team_key][player_name].setdefault("assists", 0)
            game_results[team_key][player_name].setdefault("steals", 0)
            game_results[team_key][player_name].setdefault("blocks", 0)
            game_results[team_key][player_name].setdefault("field_goals_attempted", 0)
            game_results[team_key][player_name].setdefault("field_goals_made", 0)
            game_results[team_key][player_name].setdefault("three_points_attempted", 0)
            game_results[team_key][player_name].setdefault("three_points_made", 0)
            game_results[team_key][player_name].setdefault("free_throws_attempted", 0)
            game_results[team_key][player_name].setdefault("free_throws_made", 0)
            game_results[team_key][player_name].setdefault("field_goal_percentage", 0)
            game_results[team_key][player_name].setdefault("three_point_percentage", 0)
            game_results[team_key][player_name].setdefault("free_throw_percentage", 0)

    return game_results

# Display Box Score of simulation
def display_box_score(game_results):
    for team_key in ["team1", "team2"]:
        print(f"{team_key} box score:")
        for player_name, stats in game_results[team_key].items():
            field_goal_percentage = stats["field_goal_percentage"] * 100 if stats["field_goals_attempted"] > 0 else 0
            three_point_percentage = stats["three_point_percentage"] * 100 if stats["three_points_attempted"] > 0 else 0
            free_throw_percentage = stats["free_throw_percentage"] * 100 if stats["free_throws_attempted"] > 0 else 0

            print(f"{player_name}: {stats['points']} points, {stats['rebounds']} rebounds, {stats['assists']} assists, {stats['steals']} steals, {stats['blocks']} blocks, {field_goal_percentage:.1f}% FG, {three_point_percentage:.1f}% 3PT, {free_throw_percentage:.1f}% FT")
        print()

    print(f"Final score: Team 1 - {game_results['team1_score']}, Team 2 - {game_results['team2_score']}")
    print(f"Team 1 wins: {game_results['team1_wins']}, Team 2 wins: {game_results['team2_wins']}, Tie games: {game_results['tie_games']}")

def main():
    # Load player data from CSV file
    players = []
    with open("output.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            players.append(row)

# Get team names and select starters for each team
    teams = display_teams(players)
    print("Select Team 1:")
    team1_name = select_team(teams, "Enter team name: ")
    team1_starters = select_starters(team1_name, players)
    print("\nSelect Team 2:")
    team2_name = select_team(teams, "Enter team name: ")
    team2_starters = select_starters(team2_name, players)

# Run the simulation and display results
    num_simulations = 10000
    print(f"\nSimulating {num_simulations} games...")
    game_results = run_simulation(team1_starters, team2_starters, num_simulations)
    print("\nSimulation results:")
    display_box_score(game_results)


if __name__ == "__main__":
    main()
