import pandas as pd
from pathlib import Path
from random import choice,shuffle

path = Path.cwd()/"boxer.csv"
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

def random_matchups(boxerList):
    boxers = boxerList.tolist()
    shuffle(boxers)
    for i in range(0,len(boxers)-1,2):
        print(f"-------- Match {(i//2)+1} ---------- \n {boxers[i]} VS {boxers[i+1]}")
        print("-"*27)





if path.exists():
    print("Generating Tournament")
    df = pd.read_csv(path)
    filtered_df = df[df['weight class']==weight_class]
    boxers = filtered_df["Name"]

    if len(boxers)==0 or len(boxers) <=1:
        print("No Boxers or Only One Boxer in weight class")
        exit()
    
    if len(boxers)%2==1:
        print("ODD Number of Boxers Detected")
        bye_index = choice(boxers.index)
        bye = boxers.loc[bye_index] 
        print(bye +" Moves To Round 2")
        boxers = boxers.drop(bye_index)
        random_matchups(boxers)
    else:
        random_matchups(boxers)
else:
    print("CSV is not present")