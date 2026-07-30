import pandas as pd
import random
from pathlib import Path

boxer_df = None
archetype_df = None

path_boxer_csv = Path.cwd()/"boxer.csv"
path_archtype_csv = Path.cwd()/"archetypes.csv"

initiative_wins_1 =0
initiative_wins_2=0
counter_punch_count_1=0
counter_punch_count_2=0
total_punch_count_1 = 0
total_punch_count_2 = 0
landed_punch_count_1 = 0
landed_punch_count_2 = 0
normal_punch_count_1 = 0
normal_punch_count_2 = 0
landed_counter_punch_1 = 0
landed_counter_punch_2 = 0 



def load_boxers(boxer_path,archetype_path):

    boxer_df = pd.read_csv(boxer_path)
    
    archetype_df = pd.read_csv(archetype_path)

    return boxer_df,archetype_df

def select_boxers(num1,num2,boxer_df):

    return boxer_df.iloc[num1],boxer_df.iloc[num2]

def get_archetypes(boxer_1,boxer_2,archetype_df):
    return archetype_df[archetype_df['Archetype'] == boxer_1['Archetype']],archetype_df[archetype_df['Archetype'] == boxer_2['Archetype']]

def update_counter(counter):
    return counter+1

def simulate_exchange(
    boxer_1,
    boxer_2,
    B1AType,
    B2AType,
    initiavtivewin1,
    initiavtivewin2,
    counter_win_1,
    counter_win_2,
    punch_count_1,
    punch_count_2,
    landed_punch_count_1,
    landed_punch_count_2,
    normal_punch_landed_1,
    counter_punch_landed_1,
    normal_punch_landed_2,
    counter_punch_landed_2
):
    print("Simulating Exchange")



    aggression_1 = B1AType.iloc[0]["Aggression"]
    speed_1 = boxer_1["Speed"]
    initiative_score_1 = aggression_1 + speed_1 + random.randrange(1, 100)

    aggression_2 = B2AType.iloc[0]["Aggression"]
    speed_2 = boxer_2["Speed"]
    initiative_score_2 = aggression_2 + speed_2 + random.randrange(1, 100)


    punches = [
        "Jab",
        "Cross",
        "Hook",
        "Uppercut",
        "Body_Shot",
    ]

    weights_1 = [
        B1AType.iloc[0]["Jab"],
        B1AType.iloc[0]["Cross"],
        B1AType.iloc[0]["Hook"],
        B1AType.iloc[0]["Uppercut"],
        B1AType.iloc[0]["Body_Shot"],
    ]

    weights_2 = [
        B2AType.iloc[0]["Jab"],
        B2AType.iloc[0]["Cross"],
        B2AType.iloc[0]["Hook"],
        B2AType.iloc[0]["Uppercut"],
        B2AType.iloc[0]["Body_Shot"],
    ]



    counter_value_1 = B1AType.iloc[0]["Counter_Tendency"]
    counter_value_2 = B2AType.iloc[0]["Counter_Tendency"]

    counter_chance_1 = (
        counter_value_1
        + speed_1
        - random.randrange(1, 100)
    )

    counter_chance_2 = (
        counter_value_2
        + speed_2
        - random.randrange(1, 100)
    )

    
    if initiative_score_1 > initiative_score_2:

        attacker = boxer_1
        attacker_archetype = B1AType
        attacker_weights = weights_1

        defender = boxer_2
        defender_archetype = B2AType
        defender_weights = weights_2

        initiative_winner = 1

        initiavtivewin1 += 1

        defender_counter_chance = counter_chance_2

    else:

        attacker = boxer_2
        attacker_archetype = B2AType
        attacker_weights = weights_2

        defender = boxer_1
        defender_archetype = B1AType
        defender_weights = weights_1

        initiative_winner = 2

        initiavtivewin2 += 1

        defender_counter_chance = counter_chance_1


    selected_punch = random.choices(
        punches,
        weights=attacker_weights,
        k=1
    )[0]

    print(
        f"{attacker['Name']} throws a {selected_punch} "
        f"at {defender['Name']}"
    )

    if initiative_winner == 1:
        punch_count_1 += 1
    else:
        punch_count_2 += 1

    original_landed = punch_landed(
        defender,
        defender_archetype,
        attacker,
        1000,
        1000,
        selected_punch
    )

    if original_landed:

        print("Original punch landed!")
        shot_type = random.choice(["Head","Body"])
        if selected_punch == "Body_Shot":
            shot_type = "Body"
        dmg,islivershotted = calculate_dmg(attacker['Power'],selected_punch,shot_type)
        print(dmg,islivershotted)


        if initiative_winner == 1:
            landed_punch_count_1 += 1
            normal_punch_landed_1 += 1
        else:
            landed_punch_count_2 += 1
            normal_punch_landed_2 += 1

    else:

        print("Original punch missed.")


    if defender_counter_chance >= 95:

        print(
            f"{defender['Name']} gets a counter opportunity!"
        )

        if initiative_winner == 1:
            counter_win_2 += 1
        else:
            counter_win_1 += 1
        counter_punch = random.choices(
            punches,
            weights=defender_weights,
            k=1
        )[0]

        print(
            f"{defender['Name']} counters with a "
            f"{counter_punch}!"
        )


        # Defender throws another punch.
        if initiative_winner == 1:
            punch_count_2 += 1
            counter_attempting_fighter = boxer_2
            counter_attempting_archetype = B2AType

        else:
            punch_count_1 += 1
            counter_attempting_fighter = boxer_1
            counter_attempting_archetype = B1AType

        # Check whether the COUNTER lands.
        counter_landed = punch_landed(
            attacker,
            attacker_archetype,
            counter_attempting_fighter,
            1000,
            1000,
            counter_punch
        
        )

        if counter_landed:

            print("Counter landed!")
            shot_type = random.choice(["Head","Body"])
            if counter_punch == "Body_Shot":
                shot_type = "Body"
            dmg,islivershotted = calculate_dmg(counter_attempting_fighter['Power'],counter_punch,shot_type)
            print(dmg*1.10,islivershotted)


            if initiative_winner == 1:
                landed_punch_count_2 += 1
                counter_punch_landed_2 += 1
            else:
                landed_punch_count_1 += 1
                counter_punch_landed_1 += 1

        else:

            print("Counter missed.")



    return (
        initiavtivewin1,
        initiavtivewin2,
        counter_win_1,
        counter_win_2,
        punch_count_1,
        punch_count_2,
        landed_punch_count_1,
        landed_punch_count_2,
        normal_punch_landed_1,
        counter_punch_landed_1,
        normal_punch_landed_2,
        counter_punch_landed_2,
    )
def punch_landed(boxer_to_be_hit,BTBHAType,boxer_hitting,init_head_cond,init_body_cond,punch_type):

    block_type_value = {
        "Classic": 5,
        "Cross Arm": 10
    }
    punch_acc_modifier = {
        "Jab":+5,
        "Cross":0,
        "Hook":-3,
        "Uppercut":-7,
        "Body_Shot":-5

    }
    isFlashKO = False


    speed_tbh = boxer_to_be_hit['Speed']
    chin_tbh = boxer_to_be_hit['Chin']
    body_tbh = boxer_to_be_hit['Body']
    defense_tbh = BTBHAType.iloc[-1]["Defense"]
    movement_tbh = BTBHAType.iloc[-1]["Movement"]

    speed_bth = boxer_hitting['Speed']
    agility_bth = boxer_hitting['Agility']

    init_body_cond = init_body_cond*body_tbh
    init_head_cond = init_head_cond*chin_tbh
    movement_speed = movement_tbh+speed_tbh
    block_value = defense_tbh + block_type_value[boxer_to_be_hit['Block Style']]

    defend_score = (block_value*0.6) +  (movement_speed*0.3) + random.randrange(-10,+10)

    attack_score=  (speed_bth*0.6) +(agility_bth*0.4)+ punch_acc_modifier[punch_type]+random.randrange(-10,+10)


    advantage = attack_score-defend_score 
    hit_chance = 50 + (advantage * 0.5)

    print(attack_score)
    print(defend_score)

    if hit_chance<5:
        hit_chance =5

    if hit_chance> 95:
        hit_chance= 95
        
    print(hit_chance)
    if hit_chance <= random.randint(0,100):
        print("Punch Missed")
        return False
    else:
        print("Punch landed")
        return True

def calculate_dmg(power,punch_type,shot_type):

    punch_type_damage_modifier = {
        "Head":{
        "Jab":+5,
        "Cross":+7,
        "Hook":+10,
        "Uppercut":+15,
        },
        "Body":{
        "Jab":+3,
        "Cross":+12,
        "Hook":+16,
        "Uppercut":+18,
        "Body_Shot":+6
            
        }
    }

    damage = 0
    isLiverShotted = False
    liver_shot_chance = random.randint(1,20)

    if liver_shot_chance == 20:
        damage = 400
        isLiverShotted = True
        
        return damage,isLiverShotted

    damage = (power*0.7)+(punch_type_damage_modifier[shot_type][punch_type])
    return damage,isLiverShotted



if __name__ == "__main__":


    boxer_df,archetype_df = load_boxers(path_boxer_csv,path_archtype_csv)

    print("======Current Roster======")
    print(boxer_df[['Name','Archetype']])

    first_boxer_choice = int(input("Select Boxer 1: "))
    second_boxer_choice = int(input("Select Boxer 2: "))

    boxer_1,boxer_2 = select_boxers(first_boxer_choice,second_boxer_choice,boxer_df)
    boxer_1_archetype,boxer_2_archetype = get_archetypes(boxer_1,boxer_2,archetype_df)

    print(boxer_1)
    print(boxer_1_archetype)
    print(boxer_2)
    print(boxer_2_archetype)


    print("Simulating 1000 Exchanges")
    for i in range(0,1000):
        initiative_wins_1,initiative_wins_2,counter_punch_count_1,counter_punch_count_2,total_punch_count_1,total_punch_count_2,landed_punch_count_1,landed_punch_count_2,normal_punch_count_1,landed_counter_punch_1,normal_punch_count_2,landed_counter_punch_2= simulate_exchange(boxer_1,boxer_2,boxer_1_archetype,boxer_2_archetype,initiative_wins_1,initiative_wins_2,counter_punch_count_1,counter_punch_count_2,total_punch_count_1,total_punch_count_2,landed_punch_count_1,landed_punch_count_2,normal_punch_count_1,landed_counter_punch_1,normal_punch_count_2,landed_counter_punch_2)

    print(boxer_1["Name"])
    print("Initiative wins")
    print(initiative_wins_1)
    print("Counter Chances won")
    print(counter_punch_count_1)
    print("Total Punches/Landed Punches")
    print(f"{total_punch_count_1}/{landed_punch_count_1}")
    print("Normal Punches")
    print(normal_punch_count_1)
    print("Counter Punches Landed")
    print(landed_counter_punch_1)

    print(boxer_2["Name"])
    print("Initiative wins")
    print(initiative_wins_2)
    print("Counter Chances won")
    print(counter_punch_count_2)
    print("Total Punches/Landed Punches")

    print(f"{total_punch_count_2}/{landed_punch_count_2}")

    print("Normal Punches")
    print(normal_punch_count_2)
    print("Counter Punches Landed")
    print(landed_counter_punch_2)
