import pandas as pd
from pathlib import Path

path = Path.cwd()/'results.csv'
df = pd.read_csv(path)



df["Score"] = (df["wins"] * 10) + (df['ko wins'] * 5) - (df['losses'] * 6) - (df["ko losses"] * 2)

current_champion_name = input("Enter you current champion name: ").strip()

df_sorted = df.sort_values(by="Score",ascending=False).reset_index(drop=True)

champ_df = df_sorted[df_sorted["Name"].str.lower() == current_champion_name.lower()].copy()
contenders_df = df_sorted[df_sorted["Name"].str.lower() != current_champion_name.lower()].copy()

if not champ_df.empty:
    champ_df.index = ["C"]
    contenders_df.index = range(1,len(contenders_df)+1)
    final_rankings = pd.concat([champ_df,contenders_df])
else:
    print(f"Fighter '{current_champion_name}' not found. Showing Standard Rankings.")
    contenders_df.index = range(1,len(contenders_df)+1)
    final_rankings = contenders_df

print("\n ==== OFFICIAL DIVISION RANKINGS ====")
print(final_rankings[["Name",'wins','losses','ko wins','Score']].to_string())

final_rankings.to_csv((Path.cwd()/"rankings.csv"))