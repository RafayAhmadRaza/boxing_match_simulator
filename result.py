import pandas as pd
from pathlib import Path 

class Result:

    def __init__(self,winner, loser, isKO, isDecision):
        self.winner = winner
        self.loser = loser
        self.isKO = isKO
        self.isDecision = isDecision
    def print_debug(self):
        print(self.winner,self.loser,self.isKO,self.isDecision)

    def add_result(self):

        result_csv_path = Path.cwd()/'results.csv'

        if result_csv_path.exists():
            df = pd.read_csv(result_csv_path)

            if df.loc[df['Name'] == self.winner].empty:
                initial_result = ({
                        "Name":self.winner,
                        "wins":0,
                        "losses":0,
                        "draws":0,
                        "ko wins":0,
                        "ko losses":0,
                        "decision wins":0,
                        "decision losses":0,
                        

                    
                })
                df= pd.concat([df,pd.DataFrame([initial_result])],ignore_index=True)


            if df.loc[df['Name'] == self.loser].empty:
                initial_result = ({
                        "Name":self.loser,
                        "wins":0,
                        "losses":0,
                        "draws":0,
                        "ko wins":0,
                        "ko losses":0,
                        "decision wins":0,
                        "decision losses":0,
                        

                    
                })
                df= pd.concat([df,pd.DataFrame([initial_result])],ignore_index=True)



            df.loc[df["Name"] == self.winner, "wins"] +=1
            df.loc[df["Name"] == self.loser, "losses"] +=1

            if self.isKO:
                df.loc[df["Name"] == self.winner, "ko wins"] +=1
                df.loc[df["Name"] == self.loser, "ko losses"] +=1
            if self.isDecision:
                df.loc[df["Name"] == self.winner, "decision wins"] +=1
                df.loc[df["Name"] == self.loser, "decision losses"] +=1

            df.to_csv(result_csv_path,index=0)
            print(f'Update Records Are\n{df.loc[df["Name"] == self.winner]}\n{df.loc[df["Name"] == self.loser]}')





        else:
            boxers_csv_path = Path.cwd()/"boxer.csv"
            boxer_df = pd.read_csv(boxers_csv_path)
            Names = boxer_df['Name'].to_numpy()
   
            initial_result = {}
            initial_results_list = []
            for name in Names:
                initial_result = ({
                        "Name":name,
                        "wins":0,
                        "losses":0,
                        "draws":0,
                        "ko wins":0,
                        "ko losses":0,
                        "decision wins":0,
                        "decision losses":0,
                        

                    
                })
                initial_results_list.append(initial_result)
            dataframe = pd.DataFrame(initial_results_list)
            dataframe.to_csv(result_csv_path,index=False)
                

