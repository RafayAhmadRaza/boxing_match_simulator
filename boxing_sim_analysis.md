# Boxing Simulator Analysis

## 1. Fighter Attributes/Stats Representation

**File:** `boxer_creator.py`, `boxer.csv`

Each fighter has the following attributes (base 80 ± 2d6 roll modifier):

| Attribute | Range (typical) | Purpose |
|-----------|----------------|---------|
| Power | ~72–88 | Damage multiplier (×0.7 in `calculate_dmg`) |
| Speed | ~72–88 | Initiative, attack score, counter chance |
| Agility | ~72–88 | Attack score (×0.4 weight) |
| Stamina | ~72–88 | **UNUSED** in simulation |
| Chin | ~72–88 | Only used in `recover_from_ko` via Heart |
| Body | ~72–88 | **UNUSED** (separate from body_cond) |
| Heart | ~72–88 | Recovery from knockdown (`recover_from_ko`) |
| Cuts | ~72–88 | **UNUSED** |

**Archetype modifiers** (`archetypes.csv`, loaded in `simulator.py:get_archetypes`):
- Punch selection weights (Jab/Cross/Hook/Uppercut/Body_Shot)
- Aggression, Counter_Tendency, Defense, Movement, Pressure, Risk_Taking
- Head_Target, Body_Target percentages

**Style modifiers** (from `boxer_creator.py`, partially used):
- Block Style: Classic (+5 defense), Cross Arm (+10 defense) — used in `punch_landed`
- Stance, Base Stance, Punch Style, Signature Move — **UNUSED** in simulation

---

## 2. Fight Simulation Flow (Start to Finish)

**File:** `simulator.py`

### Entry Point: `__main__` (lines 885–926)
1. Load boxers & archetypes (`load_boxers`)
2. User selects two boxers by index (`select_boxers`)
3. User selects rounds (4/8/10/12) and watch/debug mode
4. Call `simulate_round(rounds, boxer_1, boxer_2, archetype_1, archetype_2, watch_mode)`

### Round Simulation: `simulate_round` (lines 534–648)
- Each round: 200 exchanges (loop `for i in range(0,200)`)
- Every 5th exchange: `simulate_exchange` called
- Head/body condition starts at 1000 each fighter
- Tracks: initiative wins, punch counts, landed punches, counters, knockdowns
- Early exit if `Match_Over` (KO/TKO)

### Exchange Simulation: `simulate_exchange` (lines 33–383)
1. **Initiative**: `aggression + speed + random(1,100)` for each fighter (lines 70–76)
2. Higher initiative = attacker; other = defender
3. **Punch selection**: `random.choices(punches, weights=attacker_archetype_weights)` (lines 183–187)
4. **Landing check**: `punch_landed(defender, defender_archetype, attacker, punch_type)` (line 199)
5. **If landed**:
   - Random head/body target (forced body for Body_Shot)
   - `calculate_dmg(attacker['Power'], punch_type, shot_type)` (line 212)
   - `apply_dmg(dmg, defender_head, defender_body, ...)` (line 213)
   - If `defender_koed`: knockdown count++, `recover_from_ko` (lines 215–221)
   - If defender fails to rise: `Match_Over=True`, winner=attacker
6. **Counter opportunity**: If `defender_counter_chance >= 95` (line 261)
   - Counter punch selected from defender's archetype weights
   - `punch_landed(attacker, attacker_archetype, counter_fighter, counter_punch)` (lines 295–301)
   - If landed: 1.10× damage bonus, same KO/recovery logic

### Decision (if no KO): `go_decision` (lines 654–699)
- Three judges score round-by-round (`judge_1`, `judge_2`, `judge_3`)
- Majority of judges determines winner (UD/SD/Draw)

### Record Update: `result.py:Result.add_result()` (lines 15–71)
- Updates `results.csv` with wins/losses/draws/KO wins/KO losses/decision wins/decision losses

---

## 3. Punch Accuracy, Damage, Defense, Power Calculations

### 3.1 Punch Landing (`punch_landed`, lines 384–431)

```python
# DEFENDER stats
speed_tbh      = boxer_to_be_hit['Speed']           # defender's Speed
defense_tbh    = BTBHAType.iloc[-1]["Defense"]      # archetype Defense
movement_tbh   = BTBHAType.iloc[-1]["Movement"]     # archetype Movement
block_value    = defense_tbh + block_type_value[boxer_to_be_hit['Block Style']]
movement_speed = movement_tbh + speed_tbh

defend_score = (block_value * 0.6) + (movement_speed * 0.3) + random.randrange(-10, +10)

# ATTACKER stats
speed_bth      = boxer_hitting['Speed']
agility_bth    = boxer_hitting['Agility']

attack_score = (speed_bth * 0.6) + (agility_bth * 0.4) + punch_acc_modifier[punch_type] + random.randrange(-10, +10)

advantage    = attack_score - defend_score
hit_chance   = 50 + (advantage * 0.5)
hit_chance   = clamp(hit_chance, 5, 95)

# Landed if: hit_chance > random.randint(0, 100)
```

**Weights:**
- Defender: Block Value (archetype Defense + Block Style) × **0.6**, Movement+Speed × **0.3**
- Attacker: Speed × **0.6**, Agility × **0.4**, Punch Accuracy Modifier (Jab +5, Cross 0, Hook -3, Uppercut -7, Body_Shot -5)
- Random variance: ±10 on both sides

**Chin is NOT used anywhere in punch_landed.**

### 3.2 Damage Calculation (`calculate_dmg`, lines 433–463)

```python
# Base damage
damage = (power * 0.7) + punch_type_damage_modifier[shot_type][punch_type]

# Liver shot: 1/20 chance, 400 damage (instant KO trigger)
if random.randint(1,20) == 20:
    damage = 400
    isLiverShotted = True
```

**Punch Type Damage Modifiers:**
| Punch | Head | Body |
|-------|------|------|
| Jab | +5 | +3 |
| Cross | +7 | +12 |
| Hook | +10 | +16 |
| Uppercut | +15 | +18 |
| Body_Shot | N/A | +6 |

### 3.3 Damage Application (`apply_dmg`, lines 465–493)

```python
if shot_type == "Head":  head_cond -= damage
if shot_type == "Body":  body_cond -= damage

if head_cond <= 0:  head_cond = 0; isKO = True
if body_cond <= 0:  body_cond = 0; isKO = True

# Liver shot: additional body damage + 10/21 chance of KO
if isLiverShotted:
    body_cond -= damage
    isKO = (random.randint(0,21) <= 10)
```

### 3.4 Knockout Recovery (`recover_from_ko`, lines 495–530)

```python
recovery_chance = heart * 0.5 + random.randint(0, 20)
recovery_threshold = 40

# Diminishing returns by knockdown count
if ko_count == 0: recovery_value = 2
elif ko_count == 1: recovery_value = 1
elif ko_count == 2: recovery_value = 0.5
else: recovery_value = 0.1

health_recovery = (heart * recovery_value) * 0.6
cond = cond + health_recovery

if recovery_chance <= recovery_threshold:  # FAIL to rise
    gotUp = False
else:  # RISE
    gotUp = True

# Mandatory stoppage rules
if rounds == 4 and ko_count >= 2:  return cond, False, True
if rounds == 8 and ko_count >= 3:  return cond, False, True
if rounds == 10 and ko_count >= 5: return cond, False, True
```

**Key insight:** Chin stat is **never read** in `recover_from_ko`. Only **Heart** is used. The fighter's `Chin` attribute from `boxer.csv` is completely ignored by the simulation.

---

## 4. Stamina/Fatigue System

**Current State: NON-EXISTENT**

- `Stamina` attribute exists in `boxer.csv` (generated in `boxer_creator.py`)
- **Never referenced** anywhere in `simulator.py`
- No decay, no effect on accuracy/power/defense, no round-by-round fatigue
- Head/body condition starts at 1000 and only decreases — never recovers between rounds

**Where it would plug in:**
- `simulate_round`: Initialize stamina, decay per exchange/round
- `punch_landed`: Attack score reduced by low stamina
- `calculate_dmg`: Power reduced by low stamina
- `recover_from_ko`: Recovery chance reduced by low stamina
- Between rounds: Partial stamina recovery

---

## 5. KO vs Decision Outcomes

**KO/TKO Path:**
- `apply_dmg` sets `isKO=True` when head_cond ≤ 0 or body_cond ≤ 0 (or liver shot)
- `recover_from_ko` determines if fighter rises
- If `gotUp == False` → `Match_Over=True`, `winner=attacker`
- `simulate_round` returns `KO_win=True`, `winner_name`, `loser_name`

**Decision Path:**
- If all rounds complete without `KO_win`:
- `go_decision(rounds_summary)` called (line 919)
- Three judges score independently:
  - **Judge 1** (`judge_1`, lines 702–790): Accuracy % + knockdowns
  - **Judge 2** (`judge_2`, lines 792–837): Total landed punches + knockdowns
  - **Judge 3** (`judge_3`, lines 843–880): Dodged punches (defensive) + counter punches landed
- Majority decision (2/3 or 3/3) → UD/SD; 1-1-1 → Draw

---

## 6. Championship Fights

**Current Implementation: NONE**

- `ranker.py` (lines 11–21): Accepts champion name input, places them at rank "C" regardless of score
- No mandatory defense mechanic
- No title fight scheduling logic
- No champion vs. #1 contender enforcement
- Champion could theoretically never fight again — no code prevents this

---

## 7. Champion Determination

**File:** `ranker.py` (lines 11–25)

```python
current_champion_name = input("Enter you current champion name: ").strip()
df_sorted = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
champ_df = df_sorted[df_sorted["Name"].str.lower() == current_champion_name.lower()].copy()
# Champion forced to rank "C" (index "C") regardless of Score
```

- Champion is **manually designated** by user input
- No automatic champion recognition from results
- No title lineage tracking
- Champion retains "C" rank even if their Score drops below contenders

---

## 8. Rankings & Ranking Score Calculation

**File:** `ranker.py` (line 9)

```python
df["Score"] = (df["wins"] * 10) + (df['ko wins'] * 5) - (df['losses'] * 6) - (df["ko losses"] * 2)
```

**Effective weights per fight outcome:**
| Outcome | Score Delta |
|---------|-------------|
| KO Win | +15 (10 + 5) |
| Decision Win | +10 |
| KO Loss | -8 (-6 -2) |
| Decision Loss | -6 |
| Draw | 0 (not in formula) |

**Ranking sort:** Descending by Score, champion forced to top.

**Legoras example:** 24W/2L, 17KO/0KO-L, 7Dec/2Dec-L
= 24×10 + 17×5 - 2×6 - 0×2 = 240 + 85 - 12 = **313** (matches CSV)

---

## 9. Randomness Usage

| Location | Function | Range | Purpose |
|----------|----------|-------|---------|
| `simulate_exchange` L72,76 | `random.randrange(1,100)` | 1–99 | Initiative roll |
| `simulate_exchange` L109,115 | `random.randrange(1,100)` | 1–99 | Counter chance roll |
| `simulate_exchange` L183 | `random.choices(weights)` | — | Punch type selection |
| `simulate_exchange` L209 | `random.choice(["Head","Body"])` | — | Target selection |
| `punch_landed` L411 | `random.randrange(-10,+10)` | -10 to +9 | Defend score variance |
| `punch_landed` L413 | `random.randrange(-10,+10)` | -10 to +9 | Attack score variance |
| `punch_landed` L426 | `random.randint(0,100)` | 0–100 | Hit/miss roll |
| `calculate_dmg` L454 | `random.randint(1,20)` | 1–20 | Liver shot (5% chance) |
| `apply_dmg` L481 | `random.randint(0,21)` | 0–21 | Liver shot KO (10/22 ≈ 45%) |
| `recover_from_ko` L520 | `random.randint(0,20)` | 0–20 | Recovery roll |
| `simulate_round` L571 | Loop 200, every 5th | — | Exchange frequency |

---

## 10. Previous Success Feedback Loop

**NONE EXISTS**

- `results.csv` only accumulates: wins, losses, draws, ko wins, ko losses, decision wins, decision losses
- `simulator.py` **never reads** `results.csv` or `rankings.csv`
- No momentum, confidence, ranking bonus, or form modifier applied in:
  - Initiative calculation
  - Punch landing
  - Damage
  - Recovery
  - Judging
- Fighters fight identically regardless of record

---

# Legoras Investigation: Why 0 KO Losses in 26 Fights?

## 1. Exact Punch Landing Function (`simulator.py:punch_landed`, lines 384–431)

```python
def punch_landed(boxer_to_be_hit, BTBHAType, boxer_hitting, punch_type):
    block_type_value = {"Classic": 5, "Cross Arm": 10}
    punch_acc_modifier = {"Jab":+5, "Cross":0, "Hook":-3, "Uppercut":-7, "Body_Shot":-5}

    speed_tbh     = boxer_to_be_hit['Speed']
    defense_tbh   = BTBHAType.iloc[-1]["Defense"]      # ARCHETYPE Defense
    movement_tbh  = BTBHAType.iloc[-1]["Movement"]     # ARCHETYPE Movement
    speed_bth     = boxer_hitting['Speed']
    agility_bth   = boxer_hitting['Agility']

    movement_speed = movement_tbh + speed_tbh
    block_value    = defense_tbh + block_type_value[boxer_to_be_hit['Block Style']]

    defend_score = (block_value * 0.6) + (movement_speed * 0.3) + random.randrange(-10, +10)
    attack_score = (speed_bth * 0.6) + (agility_bth * 0.4) + punch_acc_modifier[punch_type] + random.randrange(-10, +10)

    advantage = attack_score - defend_score
    hit_chance = 50 + (advantage * 0.5)
    hit_chance = clamp(hit_chance, 5, 95)

    return hit_chance > random.randint(0, 100)
```

**Inputs & Weights:**
| Component | Source | Weight |
|-----------|--------|--------|
| Archetype Defense | `BTBHAType["Defense"]` | ×0.6 (via block_value) |
| Block Style | `block_type_value[Block Style]` | ×0.6 (added to Defense) |
| Archetype Movement | `BTBHAType["Movement"]` | ×0.3 (via movement_speed) |
| Fighter Speed (defender) | `boxer_to_be_hit['Speed']` | ×0.3 (via movement_speed) |
| Fighter Speed (attacker) | `boxer_hitting['Speed']` | ×0.6 |
| Fighter Agility (attacker) | `boxer_hitting['Agility']` | ×0.4 |
| Punch Type | `punch_acc_modifier[punch_type]` | Flat ±5 to -7 |

**Chin stat: NOT USED. Fighter's individual Chin is completely absent.**

---

## 2. Knockdown/KO Determination Chain

**Landing → Damage → Condition ≤ 0 → KO Flag → Recovery**

1. **Punch lands** → `punch_landed` returns True (defender's Defense/Movement/Speed/Block Style vs attacker's Speed/Agility)
2. **Damage calculated** → `calculate_dmg`: `(Power × 0.7) + punch_modifier` (Liver shot: 400 dmg, 5% chance)
3. **Condition reduced** → `apply_dmg`: `head_cond -= damage` or `body_cond -= damage`
4. **KO triggered** → If `head_cond ≤ 0` or `body_cond ≤ 0` → `isKO = True`
5. **Recovery** → `recover_from_ko(heart, cond, ko_count, rounds)` — **uses Heart only, not Chin**

**Critical finding:** The **individual Chin stat is never read** in the entire KO chain. It exists in `boxer.csv` but is **dead code**.

---

## 3. Per-Fighter Momentum/Confidence Modifier

**SEARCH RESULT: NO SUCH CODE EXISTS**

Grepped `simulator.py` for: `momentum`, `confidence`, `streak`, `ranking`, `Score`, `wins`, `losses`, `form`, `previous` — **zero matches**.

The simulation is **memoryless**. Every fight starts with pristine 1000 head/body condition, no carryover.

---

## 4. Opponent Selection/Matching

**File:** `tournament_creator.py` (lines 39–68)

```python
def random_matchups(boxerList):
    boxers = boxerList.tolist()
    shuffle(boxers)                    # RANDOM SHUFFLE
    for i in range(0, len(boxers)-1, 2):
        print(f"{boxers[i]} VS {boxers[i+1]}")
```

- **Pure random shuffle** within weight class
- No seeding, no ranking-based matching, no protective matchmaking
- `simulator.py` main: manual user selection (lines 896–899)

**Legoras's opponents:** Since the user manually picks fights in `simulator.py`, Legoras's 26-fight record could be cherry-picked. The tournament creator would match randomly.

---

## 5. Why Legoras (Chin 74, 2nd-worst) Has 0 KO Losses

### The Defensive Fortress

**Legoras's defensive profile:**
- Archetype: **Technical** → Defense **90**, Movement **85** (highest Defense, 2nd-highest Movement)
- Block Style: **Cross Arm** → +10 defense
- Speed: **78**

**Defend Score Calculation (vs typical opponent):**
```
block_value      = 90 (archetype) + 10 (Cross Arm) = 100
movement_speed   = 85 (archetype) + 78 (Speed) = 163
defend_score     = (100 × 0.6) + (163 × 0.3) + random(-10,10)
                 = 60 + 48.9 + random
                 ≈ 109 ± 10
```

**Typical Attacker (avg stats ~80):**
```
attack_score = (80 × 0.6) + (80 × 0.4) + punch_modifier + random(-10,10)
             = 48 + 32 + (~0) + random
             ≈ 80 ± 10
```

**Advantage = 80 - 109 = -29**
**Hit Chance = 50 + (-29 × 0.5) = 35.5%** (clamped 5–95%)

→ **Opponents land ~35% of punches on Legoras**

### The Offensive Edge

**Legoras as attacker (Technical archetype punch weights):**
- Jab 35% (+5 acc), Cross 25% (0), Hook 15% (-3), Uppercut 10% (-7), Body 15% (-5)
- **Weighted avg accuracy modifier** ≈ 35%×5 + 25%×0 + 15%×(-3) + 10%×(-7) + 15%×(-5) = **+0.55**
- Mostly high-accuracy punches (jab/cross = 60% of throws)

**Typical opponent as attacker (e.g., Slugger):**
- Jab 10% (+5), Cross 25% (0), Hook 35% (-3), Uppercut 20% (-7), Body 10% (-5)
- **Weighted avg** ≈ -3.15 — **significantly less accurate**

### The KO Chain Breakdown

For Legoras to be KO'd:
1. Opponent must land a punch (35% chance)
2. Damage must reduce head_cond/body_cond from 1000 to ≤0
   - Avg damage per landed punch: `Power×0.7 + modifier` ≈ 56 + 10 = ~66
   - Requires ~15 clean head shots or ~10 clean body shots
3. At 35% land rate over 200 exchanges/round → ~14 landed punches/round
4. But damage accumulates across rounds — head_cond doesn't reset
5. **However**: Legoras's high defense means fewer landed punches per round
6. **And**: If knocked down, recovery uses **Heart (82)** not Chin (74)
   - `recovery_chance = 82 × 0.5 + random(0,20) = 41 + random(0,20)` vs threshold 40
   - **~50-60% chance to rise** even on first knockdown
   - Chin 74 is **irrelevant** — Heart 82 carries recovery

### Summary

| Factor | Effect |
|--------|--------|
| Technical archetype Defense 90 + Cross Arm +10 | Massive block_value (100) × 0.6 weight |
| Technical archetype Movement 85 + Speed 78 | High movement_speed (163) × 0.3 weight |
| **Combined defend_score ~109** vs typical attack ~80 | **Hit chance ~35%** (vs ~50% baseline) |
| Technical punch selection (60% jab/cross) | High accuracy on offense |
| Chin stat **unused** in KO avoidance | Low Chin (74) has **zero penalty** |
| Recovery uses Heart (82) | Good recovery chance despite low Chin |
| No stamina/fatigue | Defense never degrades over rounds |

**Result:** Legoras is a defensive maestro whose archetype gives him elite avoidability. His "glass chin" is a **phantom stat** — the simulation doesn't read it. He gets hit rarely, and when he does, his Heart saves him.

---

## Stamina System: Design Considerations

### How Stamina Would Interact with Existing Calculations

| Current Calculation | Stamina Integration Point |
|---------------------|---------------------------|
| `attack_score = speed×0.6 + agility×0.4 + ...` | Multiply by `stamina_factor` (1.0 → 0.5) |
| `defend_score = block_value×0.6 + movement_speed×0.3 + ...` | Multiply by `stamina_factor` |
| `damage = power×0.7 + modifier` | Multiply power by `stamina_factor` |
| `recovery_chance = heart×0.5 + random` | Reduce heart contribution by fatigue |
| `initiative = aggression + speed + random` | Reduce speed by fatigue |

### Is Current Lack of Stamina Part of Legoras's Dominance?

**YES, critically.**

- Legoras's defense is **static** — 109 defend_score every exchange, all 12 rounds
- No fatigue means his Movement/Defense/Speed never degrade
- High-workrate pressure fighters (who'd normally wear down a defender) lose their primary weapon
- Legoras's Stamina = 81 (above avg) would be an advantage if implemented, but currently irrelevant
- The 200 exchanges/round with no decay = infinite gas tank for everyone, favoring static defensive stats

### High-Level Implementation Approach

**State to Track (per fighter, per round):**
```python
current_stamina = base_stamina  # 0-100 scale
stamina_per_exchange = 0.15     # tuned per archetype Pressure/Workrate
stamina_recovery_per_round = 8  # between rounds
min_stamina_factor = 0.4        # floor at 40% effectiveness
```

**Decay Triggers:**
- Every exchange: `current_stamina -= stamina_per_exchange * (1 + pressure_modifier)`
- Throwing a punch: additional `-0.05`
- Getting hit: additional `-0.1` (body shots `-0.2`)
- Clinching/holding (if added): recovery `+0.5`

**Influences (stamina_factor = max(current_stamina/100, min_stamina_factor)):**
1. **Initiative**: `speed * stamina_factor` in initiative roll
2. **Attack Score**: `(speed×0.6 + agility×0.4) * stamina_factor`
3. **Defend Score**: `(block_value×0.6 + movement_speed×0.3) * stamina_factor`
4. **Damage**: `power * 0.7 * stamina_factor + modifier`
5. **Recovery**: `heart * stamina_factor * 0.5 + random`
6. **Counter Chance**: `counter_tendency + speed * stamina_factor - random`

**Fight Loop Integration Points:**
- `simulate_round`: Initialize `stamina_1 = stamina_2 = boxer['Stamina']` at round start
- `simulate_exchange`: Apply decay at start of exchange; compute `stamina_factor`
- `punch_landed`: Pass `stamina_factor` for both attacker/defender
- `calculate_dmg`: Pass attacker's `stamina_factor`
- `recover_from_ko`: Pass defender's `stamina_factor`
- End of round: `stamina = min(100, stamina + stamina_recovery_per_round)`

**Archetype Differentiation:**
- Pressure Fighter/Swarmer: Higher `stamina_per_exchange` cost but higher `stamina_recovery_per_round`
- Out Boxer/Technical: Lower decay, lower recovery (efficient movement)
- Slugger: High decay, low recovery (explosive but fades)

This would make Legoras's 81 Stamina meaningful, cause his defense to fade in later rounds against high-pressure opponents, and create the "championship rounds" dynamic that currently doesn't exist.