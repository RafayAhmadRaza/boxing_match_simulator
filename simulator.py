import pandas as pd
import random
from pathlib import Path
import time
boxer_df = None
archetype_df = None

path_boxer_csv = Path.cwd()/"boxer.csv"
path_archtype_csv = Path.cwd()/"archetypes.csv"





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
    counter_punch_landed_2,
    head_cond_1,
    body_cond_1,
    head_cond_2,
    body_cond_2,
    winner=None,
    knockdown_count_1=0,
    knockdown_count_2=0,
    got_up_1=True,
    got_up_2=True,
    is_koed_1=False,
    is_koed_2=False,
    Match_Over = False,
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
        attacker_head = head_cond_1
        attacker_body = body_cond_1
        attacker_koed=is_koed_1
        attacker_got_up = got_up_1
        attacker_kd_count = knockdown_count_1

        defender = boxer_2
        defender_archetype = B2AType
        defender_weights = weights_2
        defender_head = head_cond_2
        defender_body = body_cond_2
        defender_koed=is_koed_2
        defender_got_up = got_up_2
        defender_kd_count = knockdown_count_2


        initiative_winner = 1

        initiavtivewin1 += 1

        defender_counter_chance = counter_chance_2

    else:

        attacker = boxer_2
        attacker_archetype = B2AType
        attacker_weights = weights_2
        attacker_head = head_cond_2
        attacker_body = body_cond_2
        attacker_koed = is_koed_2
        attacker_got_up = got_up_2
        attacker_kd_count = knockdown_count_2


        defender = boxer_1
        defender_archetype = B1AType
        defender_weights = weights_1
        defender_head = head_cond_1
        defender_body = body_cond_1
        defender_koed = is_koed_1
        defender_got_up = got_up_1
        defender_kd_count = knockdown_count_1


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
        selected_punch
    )

    if original_landed:

        print("Original punch landed!")
        shot_type = random.choice(["Head","Body"])
        if selected_punch == "Body_Shot":
            shot_type = "Body"
        dmg,islivershotted = calculate_dmg(attacker['Power'],selected_punch,shot_type)
        defender_head,defender_body,defender_koed= apply_dmg(dmg,defender_head,defender_body,islivershotted,shot_type)

        if defender_koed:
            defender_heart = defender["Heart"]
            if defender_head <=0:
                defender_head,defender_got_up= recover_from_ko(defender_heart,defender_head,defender_kd_count)
                defender_kd_count+=1
            if defender_head <=0:
                defender_head, defender_got_up = recover_from_ko(defender_heart,defender_body,defender_kd_count)
                defender_kd_count+=1

        if defender_got_up == True:
            print(f"{defender['Name']} got up!")
        else:
            print(f"{defender['Name']} could not beat the count!")
            Match_Over=True
            winner=attacker


        if initiative_winner == 1:
            landed_punch_count_1 += 1
            normal_punch_landed_1 += 1
            head_cond_1 = attacker_head
            body_cond_1 = attacker_body
            head_cond_2 = defender_head
            body_cond_2 = defender_body
        else:
            landed_punch_count_2 += 1
            normal_punch_landed_2 += 1
            head_cond_2 = attacker_head
            body_cond_2 = attacker_body
            head_cond_1 = defender_head
            body_cond_1 = defender_body

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
            counter_punch
        
        )

        if counter_landed:

            print("Counter landed!")
            shot_type = random.choice(["Head","Body"])
            if counter_punch == "Body_Shot":
                shot_type = "Body"
            dmg,islivershotted = calculate_dmg(counter_attempting_fighter['Power'],counter_punch,shot_type)
            counter_dmg = dmg * 1.10
            attacker_head,attacker_body,attacker_koed= apply_dmg(counter_dmg,attacker_head,attacker_body,islivershotted,shot_type)

            if attacker_koed:
                attacker_heart = attacker["Heart"]
            if attacker_head <=0:
                attacker_head,attacker_got_up= recover_from_ko(attacker_heart,attacker_head,attacker_kd_count)
                attacker_kd_count+=1
            if attacker_body <=0:
                attacker_body, attacker_got_up = recover_from_ko(attacker_heart,attacker_body,attacker_kd_count)
                attacker_kd_count+=1

            if attacker_got_up == True:
                print(f"{attacker['Name']} got up!")
            else:
             print(f"{attacker['Name']} could not beat the count!")
             Match_Over = True
             winner = defender

            if initiative_winner == 1:
                landed_punch_count_2 += 1
                counter_punch_landed_2 += 1
                head_cond_2 = attacker_head
                body_cond_2 = attacker_body
                head_cond_1 = defender_head
                body_cond_1 = defender_body
                
            else:
                landed_punch_count_1 += 1
                counter_punch_landed_1 += 1
                head_cond_1 = attacker_head
                body_cond_1 = attacker_body
                head_cond_2 = defender_head
                body_cond_2 = defender_body

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
        head_cond_1,
        body_cond_1,
        head_cond_2,
        body_cond_2,
        knockdown_count_1,
        knockdown_count_2,
        Match_Over,
        winner
    )
def punch_landed(boxer_to_be_hit,BTBHAType,boxer_hitting,punch_type):

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
    defense_tbh = BTBHAType.iloc[-1]["Defense"]
    movement_tbh = BTBHAType.iloc[-1]["Movement"]

    speed_bth = boxer_hitting['Speed']
    agility_bth = boxer_hitting['Agility']

    movement_speed = movement_tbh+speed_tbh
    block_value = defense_tbh + block_type_value[boxer_to_be_hit['Block Style']]

    defend_score = (block_value*0.6) +  (movement_speed*0.3) + random.randrange(-10,+10)

    attack_score=  (speed_bth*0.6) +(agility_bth*0.4)+ punch_acc_modifier[punch_type]+random.randrange(-10,+10)


    advantage = attack_score-defend_score 
    hit_chance = 50 + (advantage * 0.5)

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

def apply_dmg(damage,head_cond,body_cond,isLiverShotted,shot_type):

    isKO = False

    if shot_type == "Head":
        head_cond -=damage
    
    if shot_type == "Body":
        body_cond -= damage

    print(f"Head Condtion: {head_cond}")
    print(f"Body Condition:{body_cond}")

    if isLiverShotted:
        body_cond -= damage

        if random.randint(0,21) <= 10:
            isKO =set_ko(True);
        else:
            isKO = set_ko(False)

    if head_cond <=0:
        head_cond = 0
        isKO = set_ko(True)
    if body_cond<=0:
        body_cond = 0
        isKO = set_ko(True)

    return head_cond,body_cond,isKO

def recover_from_ko(heart,cond,ko_count):
    gotUp = False
    recovery_modifier = 0.5
    recovery_threshold = 40
    recovery_value = 0
    if ko_count == 0:
        recovery_value = 2
    elif ko_count>1:
        recovery_value = 1
    elif ko_count>=2:
        recovery_value = 0.5
    else:
        recovery_value = 0.1

    recovery_chance = heart*recovery_modifier+random.randint(0,20)
    
    health_recovery = (heart*recovery_value)*.6
    cond = cond + health_recovery

    if recovery_value<=40:
        gotUp = False
        return cond,gotUp
    else:
        gotUp = True
        return cond,gotUp



def simulate_round(rounds,boxer_1,boxer_2,boxer_1_archetype,boxer_2_archetype,watch_mode=True):
    delay_value = 0
    if watch_mode:
        delay_value = 0.25
    else:
        delay_value = 0
    
    rounds_summary = []

    head_cond_1 = 1000
    body_cond_1 = 1000
    head_cond_2 = 1000
    body_cond_2 = 1000
    KO_win = False

    for round in range(rounds):
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
        knockdown_counts_1 = 0
        knockdown_counts_2 = 0
        Match_Over = False
        winner = None

        print(f"---- ROUND {round+1} -----")
        for i in range(0,200):
            if i%5==0:
                initiative_wins_1,initiative_wins_2,counter_punch_count_1,counter_punch_count_2,total_punch_count_1,total_punch_count_2,landed_punch_count_1,landed_punch_count_2,normal_punch_count_1,landed_counter_punch_1,normal_punch_count_2,landed_counter_punch_2,head_cond_1,body_cond_1,head_cond_2,body_cond_2,knockdown_counts_1,knockdown_counts_2,Match_Over,winner= simulate_exchange(boxer_1,boxer_2,boxer_1_archetype,boxer_2_archetype,initiative_wins_1,initiative_wins_2,counter_punch_count_1,counter_punch_count_2,total_punch_count_1,total_punch_count_2,landed_punch_count_1,landed_punch_count_2,normal_punch_count_1,landed_counter_punch_1,normal_punch_count_2,landed_counter_punch_2,head_cond_1,body_cond_1,head_cond_2,body_cond_2,knockdown_counts_1,knockdown_counts_2)
                time.sleep(delay_value)
        rounds_summary.append({
            "Round":round+1,
            "Boxer 1":{
            "Boxer 1":boxer_1["Name"], 
            "Boxer 1 Initiative wins":initiative_wins_1,
            "Boxer 1 Total Punches":total_punch_count_1,
            "Boxer 1 Landed Punches":landed_punch_count_1,
            "Boxer 1 Normal Punches Landed":normal_punch_count_1,
            "Boxer 1 Counter Punch Landed": landed_counter_punch_1,
            "Boxer 1 Knockdowns": knockdown_counts_1,
            },
            "Boxer 2":{
            "Boxer 2":boxer_2["Name"], 
            "Boxer 2 Initiative wins":initiative_wins_2,  
            "Boxer 2 Total Punches":total_punch_count_2,
            "Boxer 2 Landed Punches":landed_punch_count_2,
            "Boxer 2 Normal Punches Landed":normal_punch_count_2,
            "Boxer 2 Counter Punch Landed":landed_counter_punch_2,
            "Boxer 2 Knockdowns": knockdown_counts_2}
            }
            )
        if Match_Over == True:
            print(f"winner by Knock Out in Round {round+1} is {winner['Name']}")
            KO_win = True
            break

    
    print(f"---- ROUND {round+1} Summary-----")

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

    return rounds_summary,KO_win


def set_ko(isKOed):
    return isKOed

def go_decision(rounds_summary):
    print("Deciding On winner")
    score_1 = judge_1(rounds_summary)
    score_2 =judge_2(rounds_summary)
    score_3 =judge_3(rounds_summary)



    results = [score_1,score_2,score_3]
    print(results)

    boxer_1_judges=0
    boxer_2_judges=0
    draws=0

    for result in results:
        if result[0]>result[1]:
            boxer_1_judges+=1
        elif result[1]> result[0]:
            boxer_2_judges+=1
        else:
            draws+=1

    if(boxer_1_judges == 3):
        print(f"Your winner by Unanimous Decision! \n {rounds_summary[0]['Boxer 1']['Boxer 1']}")
    elif(boxer_1_judges==2):
        print(f"Your winner by Split Decision! \n {rounds_summary[0]['Boxer 1']['Boxer 1']}")
    elif(boxer_2_judges == 3):
        print(f"Your winner by Unanimous Decision! \n {rounds_summary[0]['Boxer 2']['Boxer 2']}")
    elif(boxer_2_judges==2):
        print(f"Your winner by Split Decision! \n {rounds_summary[0]['Boxer 2']['Boxer 2']}")
    elif(draws == 1):
        print("Match Drawed!")
    


def judge_1(rounds):
    boxer_1_laned=0
    boxer_2_laned=0
    boxer_1_total_punch=0
    boxer_2_total_punch=0
    score_1 = 0
    score_2 = 0
    for i in range(len(rounds)):
        round_score_1 = 0
        round_score_2 = 0
        boxer_1_laned = rounds[i]["Boxer 1"]['Boxer 1 Landed Punches']
        boxer_2_laned = rounds[i]["Boxer 2"]['Boxer 2 Landed Punches']
        boxer_1_knockdowns = rounds[i]["Boxer 1"]['Boxer 1 Knockdowns']
        boxer_2_knockdowns = rounds[i]["Boxer 2"]['Boxer 2 Knockdowns']

        boxer_1_total_punch = rounds[i]['Boxer 1']['Boxer 1 Total Punches']
        boxer_2_total_punch = rounds[i]['Boxer 2']['Boxer 2 Total Punches']

        if(boxer_1_knockdowns==1):
            round_score_1+=10
            round_score_2+=8
            

            score_1+=round_score_1
            score_2+=round_score_2



            continue
        elif(boxer_1_knockdowns==2):
            round_score_1+=10
            round_score_2+=8
                        
    

            score_1+=round_score_1
            score_2+=round_score_2
            

            continue
        elif(boxer_2_knockdowns==1):
            round_score_1+=8
            round_score_2+=10
                        
           
            score_1+=round_score_1
            score_2+=round_score_2
            

            continue
        elif(boxer_2_knockdowns==2):
            round_score_1+=7
            round_score_2+=10
                        
           

            score_1+=round_score_1
            score_2+=round_score_2
            

            continue
        

        if(boxer_1_total_punch == 0 or boxer_2_total_punch == 0): continue
        boxer_1_accuracy = (boxer_1_laned/boxer_1_total_punch) *100
        boxer_2_accuracy = (boxer_2_laned/boxer_2_total_punch) *100

        if(boxer_1_accuracy >boxer_2_accuracy):
            round_score_1+=10
            round_score_2+=9
        elif(boxer_2_accuracy>boxer_1_accuracy):
            round_score_2+=10
            round_score_1+=9
        elif(boxer_1_accuracy == boxer_2_accuracy):
            round_score_1+=10
            round_score_2+=10
                        


        score_1+=round_score_1
        score_2+=round_score_2
        
    print(f"First Judge Scored it: {score_1} - {score_2}")

        

    

    return (score_1,score_2)

def judge_2(rounds):
    boxer_1_landed=0
    boxer_2_landed=0
    score_1 = 0
    score_2 = 0
    for i in range(len(rounds)):
        round_score_1 = 0
        round_score_2 = 0
        boxer_1_landed = rounds[i]["Boxer 1"]['Boxer 1 Landed Punches']
        boxer_2_landed = rounds[i]["Boxer 2"]['Boxer 2 Landed Punches']
        boxer_1_knockdowns = rounds[i]["Boxer 1"]['Boxer 1 Knockdowns']
        boxer_2_knockdowns = rounds[i]["Boxer 2"]['Boxer 2 Knockdowns']

        if(boxer_1_knockdowns==1):
            round_score_1+=10
            round_score_2+=8
            
         
            score_1+=round_score_1
            score_2+=round_score_2

            

            continue
        elif(boxer_1_knockdowns==2):
            round_score_1+=10
            round_score_2+=8
                        


            score_1+=round_score_1
            score_2+=round_score_2
            
          
            continue
        elif(boxer_2_knockdowns==1):
            round_score_1+=8
            round_score_2+=10
                        
            

            score_1+=round_score_1
            score_2+=round_score_2
            

            continue
        elif(boxer_2_knockdowns==2):
            round_score_1+=7
            round_score_2+=10

            score_1+=round_score_1
            score_2+=round_score_2
            
          
            continue

        if(boxer_1_landed >boxer_2_landed):
            round_score_1+=10
            round_score_2+=9
        elif(boxer_2_landed>boxer_1_landed):
            round_score_2+=10
            round_score_1+=9
        elif(boxer_1_landed == boxer_2_landed):
            round_score_1+=10
            round_score_2+=10
     

        score_1+=round_score_1
        score_2+=round_score_2
        
    print(f"Second Judge total: {score_1} - {score_2}")



    

    return (score_1,score_2)


    


def judge_3(rounds):
        boxer_1_counter_laned=0
        boxer_2_counter_laned=0
        boxer_1_missed_punch=0
        boxer_2_missed_punch=0
        score_1 = 0
        score_2 = 0
        for i in range(len(rounds)):
            round_score_1 = 0
            round_score_2 = 0
            boxer_1_counter_laned = rounds[i]["Boxer 1"]['Boxer 1 Counter Punch Landed']
            boxer_2_counter_laned = rounds[i]["Boxer 2"]['Boxer 2 Counter Punch Landed']
            boxer_2_dodged_punch = rounds[i]["Boxer 1"]['Boxer 1 Total Punches'] - rounds[i]["Boxer 1"]['Boxer 1 Landed Punches']
            boxer_1_dodged_punch = rounds[i]["Boxer 2"]['Boxer 2 Total Punches'] - rounds[i]["Boxer 2"]['Boxer 2 Landed Punches']


            if(boxer_2_dodged_punch > boxer_1_dodged_punch):
                round_score_1+=9
                round_score_2+=10
            elif(boxer_1_dodged_punch>boxer_2_dodged_punch):
                round_score_1+=10
                round_score_2+=9
            elif(boxer_1_dodged_punch== boxer_2_dodged_punch):
                round_score_1+=10
                round_score_2+=10
                            

            score_1+=round_score_1
            score_2+=round_score_2
            
        print(f"Third Judge total: {score_1} - {score_2}")

            

        

        return (score_1,score_2)




if __name__ == "__main__":

    rounds_summary = []
    boxer_df,archetype_df = load_boxers(path_boxer_csv,path_archtype_csv)
    KO_win = False
    print("======Current Roster======")
    print(boxer_df[['Name',"Nickname",'Archetype']])

    first_boxer_choice = int(input("Select Boxer 1: "))
    second_boxer_choice = int(input("Select Boxer 2: "))

    boxer_1,boxer_2 = select_boxers(first_boxer_choice,second_boxer_choice,boxer_df)
    boxer_1_archetype,boxer_2_archetype = get_archetypes(boxer_1,boxer_2,archetype_df)

    print(boxer_1)
    print(boxer_1_archetype)
    print(boxer_2)
    print(boxer_2_archetype)

    watch_mode = True
    rounds = int(input("Enter Round Numbers: "))
    print("1- watch mode or 2- debug mode?")
    mode = int(input(">"))
    match mode:
        case 1:
            watch_mode = True
        case 2:
            watch_mode = False
        case _:
            print("Invalid Input")
            exit()

    rounds_summary,KO_win = simulate_round(rounds,boxer_1,boxer_2,boxer_1_archetype,boxer_2_archetype,watch_mode)

    print(rounds_summary,KO_win)

    if not KO_win:
        go_decision(rounds_summary)
    else:
        print("Bye Bye")




