"""
Ranking module - provides functions to calculate and update rankings.
Can be used both as a script (for manual use) and as a module (for auto-updates).
"""
import pandas as pd
from pathlib import Path


def calculate_scores(df):
    """Calculate Score column for a results DataFrame."""
    df = df.copy()
    df["Score"] = (df["wins"] * 10) + (df['ko wins'] * 5) - (df['losses'] * 6) - (df["ko losses"] * 2)
    return df


def get_previous_champion(rankings_path):
    """
    Read previous rankings.csv to determine current champion.
    Returns champion name if found, None otherwise.
    """
    if not rankings_path.exists():
        return None
    
    try:
        df = pd.read_csv(rankings_path, index_col=0)
        if len(df) > 0 and df.index[0] == "C":
            return df.iloc[0]["Name"]
    except Exception:
        pass
    return None


def compute_rankings(results_df, champion_name=None):
    """
    Compute rankings from results DataFrame.
    
    Args:
        results_df: DataFrame with fight results
        champion_name: Name of current champion (if any). If None, will try to 
                       read from previous rankings.csv.
    
    Returns:
        DataFrame with rankings, with champion at index "C" if champion_name provided
    """
    df = calculate_scores(results_df)
    df_sorted = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
    
    if champion_name:
        # Preserve champion status regardless of Score
        champ_df = df_sorted[df_sorted["Name"].str.lower() == champion_name.lower()].copy()
        contenders_df = df_sorted[df_sorted["Name"].str.lower() != champion_name.lower()].copy()
        
        if not champ_df.empty:
            champ_df.index = ["C"]
            contenders_df.index = range(1, len(contenders_df) + 1)
            final_rankings = pd.concat([champ_df, contenders_df])
        else:
            # Champion not found in results (shouldn't happen), treat as no champion
            contenders_df.index = range(1, len(contenders_df) + 1)
            final_rankings = contenders_df
    else:
        # No champion specified - try to read from previous rankings
        # If no previous rankings, highest Score becomes champion by default
        # For now, just return sorted rankings without champion flag
        contenders_df = df_sorted
        contenders_df.index = range(1, len(contenders_df) + 1)
        final_rankings = contenders_df
    
    return final_rankings


def update_rankings(results_path, rankings_path, champion_name=None):
    """
    Update rankings.csv based on results.csv.
    
    Args:
        results_path: Path to results.csv
        rankings_path: Path to rankings.csv (read for previous champion, write new rankings)
        champion_name: Optional explicit champion name (for title fights)
    
    Returns:
        (new_rankings_df, champion_name_used)
    """
    results_df = pd.read_csv(results_path)
    
    # Determine champion: use explicit, or read from previous rankings
    if champion_name is None:
        champion_name = get_previous_champion(rankings_path)
    
    final_rankings = compute_rankings(results_df, champion_name)
    # Write with index=True to preserve champion flag (index 'C')
    final_rankings.to_csv(rankings_path, index=True)
    
    return final_rankings, champion_name


def print_rankings(final_rankings):
    """Print formatted rankings."""
    print("\n ==== OFFICIAL DIVISION RANKINGS ====")
    print(final_rankings[["Name", 'wins', 'losses', 'ko wins', 'Score']].to_string())


# Script mode - backward compatibility
if __name__ == "__main__":
    results_path = Path.cwd() / 'results.csv'
    rankings_path = Path.cwd() / 'rankings.csv'
    
    results_df = pd.read_csv(results_path)
    
    # Get champion from previous rankings
    champion_name = get_previous_champion(rankings_path)
    
    if champion_name is None:
        # First run - ask user
        champion_name = input("Enter current champion name (or press Enter for none): ").strip()
        if not champion_name:
            champion_name = None
    
    final_rankings = compute_rankings(results_df, champion_name)
    print_rankings(final_rankings)
    final_rankings.to_csv(rankings_path)