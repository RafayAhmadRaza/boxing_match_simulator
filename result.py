import pandas as pd
from pathlib import Path 
import ranker
from generate_html import generate_site_html


class Result:

    def __init__(self, winner, loser, isKO, isDecision, isDraw, isTitleFight=False):
        self.winner = winner
        self.loser = loser
        self.isKO = isKO
        self.isDecision = isDecision
        self.isDraw = isDraw
        self.isTitleFight = isTitleFight
    
    def print_debug(self):
        print(self.winner, self.loser, self.isKO, self.isDecision, self.isTitleFight)

    def add_result(self):
        result_csv_path = Path.cwd() / 'results.csv'
        rankings_csv_path = Path.cwd() / 'rankings.csv'

        if result_csv_path.exists():
            df = pd.read_csv(result_csv_path)

            if df.loc[df['Name'] == self.winner].empty:
                initial_result = ({
                        "Name": self.winner,
                        "wins": 0,
                        "losses": 0,
                        "draws": 0,
                        "ko wins": 0,
                        "ko losses": 0,
                        "decision wins": 0,
                        "decision losses": 0,
                })
                df = pd.concat([df, pd.DataFrame([initial_result])], ignore_index=True)

            if df.loc[df['Name'] == self.loser].empty:
                initial_result = ({
                        "Name": self.loser,
                        "wins": 0,
                        "losses": 0,
                        "draws": 0,
                        "ko wins": 0,
                        "ko losses": 0,
                        "decision wins": 0,
                        "decision losses": 0,
                })
                df = pd.concat([df, pd.DataFrame([initial_result])], ignore_index=True)

            if self.isDraw:
                df.loc[df["Name"] == self.winner, "draws"] += 1
                df.loc[df["Name"] == self.loser, "draws"] += 1
            else:
                df.loc[df["Name"] == self.winner, "wins"] += 1
                df.loc[df["Name"] == self.loser, "losses"] += 1

                if self.isKO:
                    df.loc[df["Name"] == self.winner, "ko wins"] += 1
                    df.loc[df["Name"] == self.loser, "ko losses"] += 1
                if self.isDecision:
                    df.loc[df["Name"] == self.winner, "decision wins"] += 1
                    df.loc[df["Name"] == self.loser, "decision losses"] += 1

            df.to_csv(result_csv_path, index=False)
            print(f'Update Records Are\n{df.loc[df["Name"] == self.winner]}\n{df.loc[df["Name"] == self.loser]}')
            
            # Auto-update rankings after every match
            # If this was a title fight and challenger won, pass winner as new champion
            # Otherwise, let ranker preserve existing champion from rankings.csv
            champion_name = None
            if self.isTitleFight and not self.isDraw:
                # Title fight: winner becomes champion (could be challenger or champion defending)
                champion_name = self.winner
            
            ranker.update_rankings(result_csv_path, rankings_csv_path, champion_name)
            generate_site_html()

        else:
            boxers_csv_path = Path.cwd() / "boxer.csv"
            boxer_df = pd.read_csv(boxers_csv_path)
            Names = boxer_df['Name'].to_numpy()
    
            initial_result = {}
            initial_results_list = []
            for name in Names:
                initial_result = ({
                        "Name": name,
                        "wins": 0,
                        "losses": 0,
                        "draws": 0,
                        "ko wins": 0,
                        "ko losses": 0,
                        "decision wins": 0,
                        "decision losses": 0,
                })
                initial_results_list.append(initial_result)
            dataframe = pd.DataFrame(initial_results_list)
            dataframe.to_csv(result_csv_path, index=False)
            
            # Initialize rankings on first run
            # No champion yet - highest Score will be champion on first manual ranker run
            ranker.update_rankings(result_csv_path, rankings_csv_path)
            generate_site_html()


# For backward compatibility when ranker is run as script
if __name__ == "__main__":
    pass