import pandas as pd
from pathlib import Path
from random import choice, shuffle

DEBUTANT_THRESHOLD = 8

path = Path.cwd() / "boxer.csv"
results_path = Path.cwd() / "results.csv"
bye = None
weight_class = ""

print("""
Choose a Weight Class

1. Feather Weight
2. Lightweight
3. Welterweight
4. Middleweight
5. Light Heavyweight
6. Heavyweight

""")

weight_choice = int(input("Enter your choice: "))

match weight_choice:
    case 1:
        weight_class = "Feather_weight"
    case 2:
        weight_class = "Light_weight"
    case 3:
        weight_class = "Welter_weight"
    case 4:
        weight_class = "Middle_weight"
    case 5:
        weight_class = "LightHeavy_weight"
    case 6:
        weight_class = "Heavy_weight"
    case _:
        print("Invalid choice.")
        exit()


def random_matchup_maker(boxer_names):
    """Randomly pair boxers for bouts. Returns list of (name1, name2) tuples."""
    boxers = boxer_names.tolist()
    shuffle(boxers)
    matchups = []
    for i in range(0, len(boxers) - 1, 2):
        matchups.append((boxers[i], boxers[i + 1]))
    return matchups


def print_matchups(matchups):
    """Print formatted matchups."""
    for i, (name1, name2) in enumerate(matchups):
        print(f"-------- Match {i + 1} ---------- \n {name1} VS {name2}")
        print("-" * 27)


def get_fighter_total_fights(name, results_df):
    """Get total fights (wins + losses + draws) for a fighter from results.csv."""
    if results_df.empty:
        return 0
    fighter_row = results_df[results_df["Name"] == name]
    if fighter_row.empty:
        return 0
    row = fighter_row.iloc[0]
    return int(row["wins"]) + int(row["losses"]) + int(row["draws"])


def filter_pool_by_experience(boxer_names, results_df, pool_type):
    """Filter boxers by experience level.
    
    Args:
        boxer_names: Series of boxer names
        results_df: DataFrame with fight results
        pool_type: "debutants" or "veterans"
    
    Returns:
        Filtered Series of boxer names
    """
    if pool_type == "debutants":
        return boxer_names[boxer_names.apply(lambda n: get_fighter_total_fights(n, results_df) < DEBUTANT_THRESHOLD)]
    elif pool_type == "veterans":
        return boxer_names[boxer_names.apply(lambda n: get_fighter_total_fights(n, results_df) >= DEBUTANT_THRESHOLD)]
    else:
        return boxer_names


def select_pool_and_generate_matchups(filtered_df, results_df):
    """Let user select pool type and generate matchups within that pool."""
    print("""
Select Fighter Pool for Tournament:

1. Debutants (fewer than 8 total fights)
2. Contenders/Veterans (8 or more total fights)
3. All Fighters (no experience filter)

""")
    pool_choice = int(input("Enter your choice: "))

    boxers = filtered_df["Name"]

    match pool_choice:
        case 1:
            pool_name = "Debutants"
            boxers = filter_pool_by_experience(boxers, results_df, "debutants")
        case 2:
            pool_name = "Contenders/Veterans"
            boxers = filter_pool_by_experience(boxers, results_df, "veterans")
        case 3:
            pool_name = "All Fighters"
        case _:
            print("Invalid choice. Using All Fighters.")
            pool_name = "All Fighters"

    print(f"\nGenerating Tournament for {pool_name} Pool in {weight_class.replace('_', ' ')}")
    print(f"Fighters in pool: {len(boxers)}")

    if len(boxers) == 0:
        print("No fighters in selected pool.")
        return
    if len(boxers) == 1:
        print("Only one fighter in selected pool. Cannot generate matchups.")
        return

    if len(boxers) % 2 == 1:
        print("ODD Number of Boxers Detected")
        bye_index = choice(boxers.index)
        bye_name = boxers.loc[bye_index]
        print(f"{bye_name} Moves To Round 2 (Bye)")
        boxers = boxers.drop(bye_index)

    matchups = random_matchup_maker(boxers)
    print_matchups(matchups)


if path.exists():
    print("Generating Tournament")
    df = pd.read_csv(path)
    filtered_df = df[df['weight class'] == weight_class]

    if results_path.exists():
        results_df = pd.read_csv(results_path)
    else:
        results_df = pd.DataFrame(columns=["Name", "wins", "losses", "draws", "ko wins", "ko losses", "decision wins", "decision losses"])

    if len(filtered_df) == 0:
        print("No Boxers in weight class")
        exit()

    select_pool_and_generate_matchups(filtered_df, results_df)
else:
    print("CSV is not present")