from random import randint,choice
import pandas as pd
from pathlib import Path

archetype_list = pd.read_csv("archetypes.csv")
archetype= 'None'
nickname = 'None'
weight_class = 'None'
weight_class_dict = {
    "Feather_weight":{
        "weight_range":(115,126),
        "height_range":[
            "5'3\"",
            "5'4\"",
            "5'5\"",
            "5'6\"",
            "5'7\"",
            "5'8\"",
            "5'9\"",
            "5'10\"",

        ]
    },
        "Light_weight":{
        "weight_range":(127,135),
        "height_range":[
            "5'4\"",
            "5'5\"",
            "5'6\"",
            "5'7\"",
            "5'8\"",
            "5'9\"",
            "5'10\"",
            "5'11\"",


        ]
    },
    "Welter_weight":{
            "weight_range":(136,147),
            "height_range":[
                "5'9\"",
                "5'10\"",
                "5'11\"",
                "6'0\"",
                "6'1\"", 
    
            ]
        },
    "Middle_weight":{
    "weight_range": (148,168), #use randint for range
    "height_range":[
    "5'8\"",
    "5'9\"",
    "5'10\"",
    "5'11\"",
    "6'0\"",
    "6'1\"",
    "6'2\"",
    "6'3\"",] #use choice for list  
    },
        "LightHeavy_weight":{
    "weight_range": (169,190), #use randint for range
    "height_range":[
    "5'7\"",
    "5'8\"",
    "5'9\"",
    "5'10\"",
    "5'11\"",
    "6'0\"",
    "6'1\"",
    "6'2\"",
    "6'3\"",
    "6'4\"",
    ] #use choice for list  
    },
            "Heavy_weight":{
    "weight_range": (191,280), #use randint for range
    "height_range":[
    "5'10\"",
    "5'11\"",
    "6'0\"",
    "6'1\"",
    "6'2\"",
    "6'3\"",
    "6'4\"",
    "6'5\"",
    "6'6\"",
    "6'7\"",
    "6'8\"",
    ] #use choice for list  
    },
    }
stance_type = {
    1:"Orthodox",
    2:"South Paw",

}

base_style_list = {
    1:"Balanced",
    2:"Speed",
    3:"Power",
    4:"Mummy",
    5:"wild",

}

punch_style_list = {
    1:"Basic",
    2:"Fast",
    3:"Slugger",
    4:"Lethal Uppercut",
    

}


block_style_list = {
    1:"Classic",
    2:"Cross Arm",

}



signature_moves_list = {
    1:"Smokin",
    2:"The Greatest",
    3:"Junior",
    4:"Lights Out",
    5:"winky",
    6:"Golden Boy",
    7:"Leonard",
    8:"Bad Intentions",
    9:"Irish",
    10:"The Destroyer",

}

Power = 80
Speed = 80
Agility = 80
Stamina = 80
Chin = 80
Body = 80
Heart = 80
Cuts = 80


def set_attribute(intial_att,roll):
    value = 0
    match roll:
        case 2:
            return intial_att -8
        case 3:
            return intial_att -6
        case 4:
            return intial_att -4
        case 5:
            return intial_att -2
        case 6:
            return intial_att -1
        case 7:
            return intial_att + 0
        case 8:
            return intial_att +1
        case 9:
            return intial_att +2
        case 10:
            return intial_att +4
        case 11:
            return intial_att +6

        case 12:
            return intial_att +8
def roll_2d6():
    return (randint(1,6) + randint(1,6))

Name = input("Enter Name Of Boxer: ")
nickname = input(f"Enter nickname of {Name}: ")

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

print("""
Choose an Archetype

1. Out Boxer
2. Boxer Puncher
3. Pressure Fighter
4. Counter Puncher
5. Slugger
6. Swarmer
7. Technical
8. Body Puncher
""")

archetype_choice = int(input(">"))

match archetype_choice:
    case 1:
        archetype = "Out Boxer"
    case 2:
        archetype = "Boxer Puncher"
    case 3:
        archetype = "Pressure Fighter"
    case 4:
        archetype = "Counter Puncher"
    case 5:
        archetype = "Slugger"
    case 6:
        archetype = "Swarmer"
    case 7:
        archetype = "Technical"
    case 8:
        archetype = 'Body Puncher'
    case _:
        print("Invalid choice.")
        exit()


print(f"----- {Name} -----")
Height = choice(weight_class_dict[weight_class]['height_range'])
weight = randint(*weight_class_dict[weight_class]['weight_range'])
print(f"Height: {Height}")
print(f"weight: {weight}")

stance = stance_type[randint(1,2)]
print(f"Stance Style: {stance}")

base_style = base_style_list[randint(1,5)]

print(f"Base Style: {base_style}")

punch_style = punch_style_list[randint(1,4)]
print(f"Punch Style: {punch_style}")

block_style = block_style_list[randint(1,2)]
print(f"Block Style: {block_style}")
signature_move = signature_moves_list[randint(1,10)]
print(f"Signature Move: {signature_move}")
print(f"------ Attributes -----")

Power = set_attribute(Power,roll_2d6())

print(f"Power: {Power}")

Speed=set_attribute(Speed,roll_2d6())

print(f"Speed: {Speed}")
Agility = set_attribute(Agility,roll_2d6())
print(f"Agility: {Agility}")

Stamina = set_attribute(Stamina,roll_2d6())
print(f"Stamina: {Stamina}")
Chin = set_attribute(Chin,roll_2d6())

print(f"Chin: {Chin}")

Body = set_attribute(Body,roll_2d6())
print(f"Body: {Body}")

Heart = set_attribute(Heart,roll_2d6())
print(f"Heart: {Heart}")

Cuts=set_attribute(Cuts,roll_2d6())
print(f"Cuts: {Cuts}")

boxer = {
    "Name":Name,
    "Nickname":nickname,
    "weight class":weight_class,
    'Height': Height,
    'weight': weight,
    'Stance Style':stance,
    'Base Stance': base_style,
    'Punch Style': punch_style,
    'Block Style': block_style,
    'Signature Move':signature_move,
    "Power":Power,
    "Speed":Speed,
    "Agility":Agility,
    "Stamina":Stamina,
    "Chin":Chin,
    "Body":Body,
    "Heart":Heart,
    "Cuts":Cuts,
    "Archetype":archetype

}
path = Path.cwd()/"boxer.csv"
if (path.exists()):
    df = pd.read_csv(path)

else:
    df = pd.DataFrame(columns=boxer.keys())

new_boxer = pd.DataFrame([boxer])
df=pd.concat([df,new_boxer],ignore_index=True)

df.to_csv(path,index=False)

print(f"{boxer['Name']} has been saved to {path.name}")
