import csv


ARCHETYPES = [
    {
        "Archetype": "Out Boxer",
        "Jab": 45,
        "Cross": 25,
        "Hook": 15,
        "Uppercut": 5,
        "Body_Shot": 10,
        "Aggression": 35,
        "Counter_Tendency": 35,
        "Defense": 85,
        "Movement": 90,
        "Pressure": 20,
        "Risk_Taking": 25,
        "Head_Target": 75,
        "Body_Target": 25,
    },
    {
        "Archetype": "Boxer Puncher",
        "Jab": 30,
        "Cross": 30,
        "Hook": 20,
        "Uppercut": 10,
        "Body_Shot": 10,
        "Aggression": 60,
        "Counter_Tendency": 40,
        "Defense": 70,
        "Movement": 65,
        "Pressure": 55,
        "Risk_Taking": 45,
        "Head_Target": 70,
        "Body_Target": 30,
    },
    {
        "Archetype": "Pressure Fighter",
        "Jab": 20,
        "Cross": 25,
        "Hook": 30,
        "Uppercut": 15,
        "Body_Shot": 10,
        "Aggression": 90,
        "Counter_Tendency": 20,
        "Defense": 55,
        "Movement": 35,
        "Pressure": 90,
        "Risk_Taking": 75,
        "Head_Target": 60,
        "Body_Target": 40,
    },
    {
        "Archetype": "Counter Puncher",
        "Jab": 20,
        "Cross": 30,
        "Hook": 25,
        "Uppercut": 15,
        "Body_Shot": 10,
        "Aggression": 30,
        "Counter_Tendency": 90,
        "Defense": 85,
        "Movement": 75,
        "Pressure": 20,
        "Risk_Taking": 35,
        "Head_Target": 70,
        "Body_Target": 30,
    },
    {
        "Archetype": "Slugger",
        "Jab": 10,
        "Cross": 25,
        "Hook": 35,
        "Uppercut": 20,
        "Body_Shot": 10,
        "Aggression": 85,
        "Counter_Tendency": 25,
        "Defense": 40,
        "Movement": 25,
        "Pressure": 80,
        "Risk_Taking": 90,
        "Head_Target": 60,
        "Body_Target": 40,
    },
    {
        "Archetype": "Swarmer",
        "Jab": 20,
        "Cross": 20,
        "Hook": 35,
        "Uppercut": 15,
        "Body_Shot": 10,
        "Aggression": 95,
        "Counter_Tendency": 35,
        "Defense": 60,
        "Movement": 70,
        "Pressure": 95,
        "Risk_Taking": 70,
        "Head_Target": 55,
        "Body_Target": 45,
    },
    {
        "Archetype": "Technical Boxer",
        "Jab": 35,
        "Cross": 25,
        "Hook": 15,
        "Uppercut": 10,
        "Body_Shot": 15,
        "Aggression": 45,
        "Counter_Tendency": 55,
        "Defense": 90,
        "Movement": 85,
        "Pressure": 30,
        "Risk_Taking": 20,
        "Head_Target": 65,
        "Body_Target": 35,
    },
    {
        "Archetype": "Body Puncher",
        "Jab": 20,
        "Cross": 20,
        "Hook": 25,
        "Uppercut": 15,
        "Body_Shot": 20,
        "Aggression": 70,
        "Counter_Tendency": 40,
        "Defense": 60,
        "Movement": 45,
        "Pressure": 75,
        "Risk_Taking": 60,
        "Head_Target": 40,
        "Body_Target": 60,
    },
]


def generate_csv(filename="archetypes.csv"):
    if not ARCHETYPES:
        raise ValueError("No archetypes were defined.")

    fieldnames = list(ARCHETYPES[0].keys())

    # Validate punch percentages.
    for archetype in ARCHETYPES:
        punch_total = (
            archetype["Jab"]
            + archetype["Cross"]
            + archetype["Hook"]
            + archetype["Uppercut"]
            + archetype["Body_Shot"]
        )

        if punch_total != 100:
            raise ValueError(
                f'{archetype["Archetype"]} punch percentages add up to '
                f"{punch_total}, not 100."
            )

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ARCHETYPES)

    print(f"Created {filename}")
    print(f"Archetypes written: {len(ARCHETYPES)}")


if __name__ == "__main__":
    generate_csv()