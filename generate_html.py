import pandas as pd
from pathlib import Path
from datetime import datetime
import subprocess
SITE_PATH = Path.home() / "Projects" / "boxing_rankings_site"

import subprocess

def push_to_github():
    try:
        subprocess.run(["git", "add", "."], cwd=SITE_PATH, check=True)
        
        # Check if there's actually anything to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=SITE_PATH
        )
        if result.returncode == 0:
            print("No changes to push.")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run(
            ["git", "commit", "-m", f"Update rankings {timestamp}"],
            cwd=SITE_PATH, check=True
        )
        subprocess.run(["git", "push"], cwd=SITE_PATH, check=True)
        print("Pushed rankings update to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git push failed: {e}")

def generate_site_html(rankings_csv_path="rankings.csv"):
    df = pd.read_csv(rankings_csv_path)

    if "Champion" in df.columns:
        df["Rank"] = df.apply(
            lambda row: f'{row.get("Name", "")} <span class="champion-tag">Champion</span>'
            if row["Champion"] else row.get("Name", ""),
            axis=1
        )
        df = df.drop(columns=["Name"]).rename(columns={"Rank": "Name"})

    html_table = df.to_html(index=False, classes="rankings-table", border=0, escape=False)
    timestamp = datetime.now().strftime("%B %d, %Y")

    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CBF Rankings</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="masthead">
  <div class="org">CBF</div>
  <h1>Official Rankings</h1>
</div>
{html_table}
<p class="updated">Last updated: {timestamp}</p>
</body>
</html>"""

    SITE_PATH.mkdir(exist_ok=True)
    (SITE_PATH / "index.html").write_text(page)
    push_to_github()

if __name__ == "__main__":
    generate_site_html()