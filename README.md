# Boxing Simulator

A small Python boxing simulator I built to experiment with turning boxing into a rules-based simulation.

The idea started pretty simply: create boxers with different stats and styles, then let them fight each other. It has since grown into a full little boxing system with exchanges, counters, damage, knockdowns, rounds, judges, decisions, records, and rankings.

This is mainly a personal programming project, so the goal is not to perfectly reproduce real boxing. Instead, I am trying to make something that produces believable and sometimes unpredictable fights while giving different boxer styles a reason to behave differently.

## What it currently does

* Loads boxers and archetypes from CSV files using pandas.
* Gives each boxer attributes such as Power, Speed, Agility, Stamina, Chin, Body, Heart, and Cuts.
* Uses archetypes to influence aggression, punch selection, defense, movement, counters, and other tendencies.
* Simulates who gets the initiative during an exchange.
* Simulates normal punches and counter opportunities.
* Calculates whether punches land using attack and defense scores with some randomness.
* Calculates damage depending on power, punch type, and target area.
* Separates head and body condition.
* Includes liver shots and increased counter-punch damage.
* Tracks knockdowns and whether a boxer gets back up.
* Supports different fight lengths such as 4, 8, 10, and 12 rounds.
* Stores statistics for every round.
* Uses three different judges with different scoring approaches.
* Produces unanimous, split, or drawn decisions.
* Keeps boxer records and an unofficial ranking system.

## Boxer system

Each boxer is stored in `boxer.csv` and has their own basic attributes and style information.

The current boxer data includes things such as:

* Name and nickname
* Weight class
* Height and weight
* Stance and base stance
* Punch style
* Block style
* Signature move
* Power
* Speed
* Agility
* Stamina
* Chin
* Body
* Heart
* Cuts
* Archetype

Archetypes are stored separately in `archetypes.csv`. They determine things like punch selection, aggression, counter tendency, defense, movement, pressure, risk taking, and targeting.

## Fight simulation

A fight is built from exchanges. During an exchange, the simulator determines which boxer gets the initiative, selects a punch, and checks whether it lands.

If the defender has a counter opportunity, they can throw another punch immediately. Counters use the defender's own stats and punch tendencies, and successful counters currently receive a small damage bonus.

Damage is then applied to the appropriate head or body condition. Once a boxer is badly hurt, they can be knocked down and must try to beat the count.

## Rounds and judges

Rounds are simulated separately so the statistics can be used later by the judges.

The simulator currently has three simple judges:

### Judge 1

Looks primarily at punch accuracy and knockdowns.

### Judge 2

Looks at total landed punches and knockdowns.

### Judge 3

Currently focuses on defensive performance by looking at how many of the opponent's punches did not land. Counter punching is also tracked and can be expanded into this judge later.

Each judge returns a scorecard for the entire fight. The three scorecards are then compared to determine the final decision.

## Example

A fight might produce something like:

```text
Judge 1: 74 - 78
Judge 2: 74 - 79
Judge 3: 79 - 73

Winner by Split Decision: Legoras
```

Because the judges use different criteria, they do not necessarily agree with each other. That is intentional.

## Rankings

The project also has a simple unofficial ranking table that tracks each boxer's record, knockout wins, and decision wins.

The long-term idea is to make the rankings update automatically as more fights are simulated.

## Project structure

```text
boxing_simulator/
├── simulator.py
├── boxer.csv
├── archetypes.csv
└── README.md
```

## Running it

Make sure Python and the required packages are installed. The simulator currently uses pandas.

```bash
python simulator.py
```

The program will ask you to select two boxers, choose the number of rounds, and select watch/debug mode.

Watch mode adds a small delay so the fight is easier to follow. Debug mode removes the delay and is useful when testing the simulation.

## Current state

This project is still being developed. A lot of the numbers and rules are experimental, and I am still tuning them to make different boxer archetypes feel distinct without making the results completely predictable.

Some parts are intentionally simplified. For example, the simulator currently treats unsuccessful punches as defensive avoidance for one of the judges, even though a punch could eventually be classified more specifically as blocked, dodged, or simply missed.

Future improvements will probably include better damage tracking, more detailed defensive outcomes, more realistic judging, automatic ranking updates, tournament support, and additional fight-ending situations.

## Why I made it

I wanted a project where I could keep adding systems and see them interact with each other. It has been a fun way to practice Python, probability, data handling, simulation design, and organizing a larger program without following a tutorial for every step.
