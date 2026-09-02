import pandas as pd
import random
from pathlib import Path
import time
import result

boxer_df = None
archetype_df = None

path_boxer_csv = Path.cwd() / "boxer.csv"
path_archtype_csv = Path.cwd() / "archetypes.csv"


DEBUTANT_THRESHOLD = 8

STAMINA_BASE_DECAY = 0.15
STAMINA_PUNCH_COST = 0.05
STAMINA_DAMAGE_TAKEN_COST = 0.10
STAMINA_BODY_SHOT_COST = 0.20
STAMINA_MIN_FACTOR = 0.40

STAMINA_ARCHETYPE_PARAMS = {
    "Pressure Fighter": {"decay_multiplier": 1.3, "recovery_per_round": 12},
    "Swarmer": {"decay_multiplier": 1.3, "recovery_per_round": 12},
    "Slugger": {"decay_multiplier": 1.5, "recovery_per_round": 6},
    "Out Boxer": {"decay_multiplier": 0.8, "recovery_per_round": 8},
    "Technical": {"decay_multiplier": 0.8, "recovery_per_round": 8},
    "Boxer Puncher": {"decay_multiplier": 1.0, "recovery_per_round": 10},
    "Counter Puncher": {"decay_multiplier": 0.9, "recovery_per_round": 10},
    "Body Puncher": {"decay_multiplier": 1.1, "recovery_per_round": 9},
}


def get_stamina_params(archetype_name):
    return STAMINA_ARCHETYPE_PARAMS.get(
        archetype_name, {"decay_multiplier": 1.0, "recovery_per_round": 10}
    )


def _score_round_10_point_must(
    boxer_a_landed,
    boxer_b_landed,
    boxer_a_total,
    boxer_b_total,
    boxer_a_kd,
    boxer_b_kd,
    boxer_a_counters,
    boxer_b_counters,
    judge_weights,
    variance=0.0,
):
    """
    Score a single round using the 10-point must system.

    Args:
        boxer_a_landed, boxer_b_landed: Clean punches landed
        boxer_a_total, boxer_b_total: Total punches thrown
        boxer_a_kd, boxer_b_kd: Knockdowns scored
        boxer_a_counters, boxer_b_counters: Counter punches landed
        judge_weights: Dict with 'clean_punching', 'aggression', 'defense'
        variance: Random variance for this judge/round (±0.5 typical)

    Returns:
        (score_a, score_b) - each 10, 9, 8, 7, or 6 per 10-point must
    """
    # Knockdown handling - 10-point must standard
    kd_diff = boxer_a_kd - boxer_b_kd
    if kd_diff != 0:
        if kd_diff > 0:
            # Boxer A scored knockdown(s)
            if kd_diff == 1:
                score_a, score_b = 10, 8
            elif kd_diff == 2:
                score_a, score_b = 10, 7
            else:
                score_a, score_b = 10, 6  # 3+ KDs
        else:
            # Boxer B scored knockdown(s)
            kd_diff = abs(kd_diff)
            if kd_diff == 1:
                score_a, score_b = 8, 10
            elif kd_diff == 2:
                score_a, score_b = 7, 10
            else:
                score_a, score_b = 6, 10

        # Apply small variance
        score_a = max(6, min(10, score_a + random.uniform(-variance, variance)))
        score_b = max(6, min(10, score_b + random.uniform(-variance, variance)))
        return round(score_a), round(score_b)

    # No knockdowns - score based on judge's philosophy
    # Calculate metrics
    boxer_a_accuracy = (
        (boxer_a_landed / boxer_a_total * 100) if boxer_a_total > 0 else 0
    )
    boxer_b_accuracy = (
        (boxer_b_landed / boxer_b_total * 100) if boxer_b_total > 0 else 0
    )

    boxer_a_missed = boxer_a_total - boxer_a_landed
    boxer_b_missed = boxer_b_total - boxer_b_landed
    boxer_a_dodge_rate = (
        (boxer_b_missed / boxer_b_total * 100) if boxer_b_total > 0 else 0
    )
    boxer_b_dodge_rate = (
        (boxer_a_missed / boxer_a_total * 100) if boxer_a_total > 0 else 0
    )

    # Judge-specific scoring
    # Clean punching judge: prioritizes landed punches and accuracy
    clean_punch_score_a = (
        boxer_a_landed * judge_weights["clean_punching"]["landed"]
        + boxer_a_accuracy * judge_weights["clean_punching"]["accuracy"]
        + boxer_a_counters * judge_weights["clean_punching"]["counters"]
    )
    clean_punch_score_b = (
        boxer_b_landed * judge_weights["clean_punching"]["landed"]
        + boxer_b_accuracy * judge_weights["clean_punching"]["accuracy"]
        + boxer_b_counters * judge_weights["clean_punching"]["counters"]
    )

    # Aggression judge: prioritizes volume and work rate
    aggression_score_a = (
        boxer_a_landed * judge_weights["aggression"]["landed"]
        + boxer_a_total * judge_weights["aggression"]["work_rate"]
    )
    aggression_score_b = (
        boxer_b_landed * judge_weights["aggression"]["landed"]
        + boxer_b_total * judge_weights["aggression"]["work_rate"]
    )

    # Defense/ring generalship judge: prioritizes defense and counters
    defense_score_a = (
        boxer_a_dodge_rate * judge_weights["defense"]["dodge_rate"]
        + boxer_a_counters * judge_weights["defense"]["counters"]
        + boxer_a_landed * judge_weights["defense"]["clean_punching"]
    )
    defense_score_b = (
        boxer_b_dodge_rate * judge_weights["defense"]["dodge_rate"]
        + boxer_b_counters * judge_weights["defense"]["counters"]
        + boxer_b_landed * judge_weights["defense"]["clean_punching"]
    )

    # Combine based on judge type (each judge has one primary philosophy)
    total_a = clean_punch_score_a + aggression_score_a + defense_score_a
    total_b = clean_punch_score_b + aggression_score_b + defense_score_b

    # Apply variance to the comparison totals (not final scores)
    # This allows judges to disagree on close rounds
    # Scale variance by typical score magnitude (~70) to make it meaningful
    variance_scale = variance * 50
    total_a += random.uniform(-variance_scale, variance_scale)
    total_b += random.uniform(-variance_scale, variance_scale)

    # Determine round winner based on variance-adjusted totals
    if total_a > total_b:
        score_a, score_b = 10, 9
    elif total_b > total_a:
        score_a, score_b = 9, 10
    else:
        score_a, score_b = 10, 10  # Even round

    return score_a, score_b


def load_boxers(boxer_path, archetype_path):

    boxer_df = pd.read_csv(boxer_path)

    archetype_df = pd.read_csv(archetype_path)

    return boxer_df, archetype_df


def select_boxers(num1, num2, boxer_df):

    return boxer_df.iloc[num1], boxer_df.iloc[num2]


def get_archetypes(boxer_1, boxer_2, archetype_df):
    return archetype_df[
        archetype_df["Archetype"] == boxer_1["Archetype"]
    ], archetype_df[archetype_df["Archetype"] == boxer_2["Archetype"]]


def update_counter(counter):
    return counter + 1


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
    rounds,
    stamina_1,
    stamina_2,
    b1_params,
    b2_params,
    winner=None,
    knockdown_count_1=0,
    knockdown_count_2=0,
    got_up_1=True,
    got_up_2=True,
    is_koed_1=False,
    is_koed_2=False,
    Match_Over=False,
    stoppage_1=False,
    stoppage_2=False,
):
    print("Simulating Exchange")

    stamina_factor_1 = max(stamina_1 / 100.0, STAMINA_MIN_FACTOR)
    stamina_factor_2 = max(stamina_2 / 100.0, STAMINA_MIN_FACTOR)

    aggression_1 = B1AType.iloc[0]["Aggression"]
    speed_1 = boxer_1["Speed"]
    initiative_score_1 = (
        aggression_1 + (speed_1 * stamina_factor_1) + random.randrange(1, 100)
    )

    aggression_2 = B2AType.iloc[0]["Aggression"]
    speed_2 = boxer_2["Speed"]
    initiative_score_2 = (
        aggression_2 + (speed_2 * stamina_factor_2) + random.randrange(1, 100)
    )

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
        counter_value_1 + (speed_1 * stamina_factor_1) - random.randrange(1, 100)
    )

    counter_chance_2 = (
        counter_value_2 + (speed_2 * stamina_factor_2) - random.randrange(1, 100)
    )

    if initiative_score_1 > initiative_score_2:
        attacker = boxer_1
        attacker_archetype = B1AType
        attacker_weights = weights_1
        attacker_head = head_cond_1
        attacker_body = body_cond_1
        attacker_koed = is_koed_1
        attacker_got_up = got_up_1
        attacker_kd_count = knockdown_count_1
        attacker_stopped = stoppage_1
        attacker_stamina = stamina_1
        attacker_params = b1_params
        attacker_stamina_factor = stamina_factor_1

        defender = boxer_2
        defender_archetype = B2AType
        defender_weights = weights_2
        defender_head = head_cond_2
        defender_body = body_cond_2
        defender_koed = is_koed_2
        defender_got_up = got_up_2
        defender_kd_count = knockdown_count_2
        defender_stopped = stoppage_2
        defender_stamina = stamina_2
        defender_params = b2_params
        defender_stamina_factor = stamina_factor_2

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
        attacker_stopped = stoppage_2
        attacker_stamina = stamina_2
        attacker_params = b2_params
        attacker_stamina_factor = stamina_factor_2

        defender = boxer_1
        defender_archetype = B1AType
        defender_weights = weights_1
        defender_head = head_cond_1
        defender_body = body_cond_1
        defender_koed = is_koed_1
        defender_got_up = got_up_1
        defender_kd_count = knockdown_count_1
        defender_stopped = stoppage_1
        defender_stamina = stamina_1
        defender_params = b1_params
        defender_stamina_factor = stamina_factor_1

        initiative_winner = 2

        initiavtivewin2 += 1

        defender_counter_chance = counter_chance_1

    selected_punch = random.choices(punches, weights=attacker_weights, k=1)[0]

    print(f"{attacker['Name']} throws a {selected_punch} at {defender['Name']}")

    if initiative_winner == 1:
        punch_count_1 += 1
    else:
        punch_count_2 += 1

    original_landed = punch_landed(
        defender,
        defender_archetype,
        attacker,
        selected_punch,
        defender_stamina_factor,
        attacker_stamina_factor,
    )

    if original_landed:
        print("Original punch landed!")
        shot_type = random.choice(["Head", "Body"])
        if selected_punch == "Body_Shot":
            shot_type = "Body"
        dmg, islivershotted = calculate_dmg(
            attacker["Power"], selected_punch, shot_type, attacker_stamina_factor
        )
        defender_head, defender_body, defender_koed = apply_dmg(
            dmg, defender_head, defender_body, islivershotted, shot_type
        )

        if defender_koed:
            defender_kd_count += 1
            defender_heart = defender["Heart"]
            # Single knockdown event - only call recover_from_ko once
            # Determine which condition to use for recovery based on shot_type
            if shot_type == "Head" or (defender_head <= 0 and defender_body > 0):
                recovery_cond = defender_head
            elif shot_type == "Body" or (defender_body <= 0 and defender_head > 0):
                recovery_cond = defender_body
            else:
                # Both head and body <= 0 (rare: pre-existing KD + new KD on other area)
                # Default to the shot_type for recovery
                recovery_cond = defender_head if shot_type == "Head" else defender_body

            recovery_cond, defender_got_up, defender_stopped = recover_from_ko(
                defender_heart,
                recovery_cond,
                defender_kd_count,
                rounds,
                defender_stamina_factor,
            )
            # Update the condition that was used for recovery
            if shot_type == "Head" or (defender_head <= 0 and defender_body > 0):
                defender_head = recovery_cond
            else:
                defender_body = recovery_cond

        if defender_got_up == True:
            print(f"{defender['Name']} got up!")
        else:
            print(f"{defender['Name']} could not beat the count!")
            Match_Over = True
            winner = attacker

        if initiative_winner == 1:
            landed_punch_count_1 += 1
            normal_punch_landed_1 += 1
            head_cond_1 = attacker_head
            body_cond_1 = attacker_body
            head_cond_2 = defender_head
            body_cond_2 = defender_body
            stoppage_1 = defender_stopped
            stoppage_2 = attacker_stopped
            knockdown_count_1 = defender_kd_count
            knockdown_count_2 = attacker_kd_count
        else:
            landed_punch_count_2 += 1
            normal_punch_landed_2 += 1
            head_cond_2 = attacker_head
            body_cond_2 = attacker_body
            head_cond_1 = defender_head
            body_cond_1 = defender_body
            stoppage_2 = defender_stopped
            stoppage_1 = attacker_stopped

            knockdown_count_2 = defender_kd_count
            knockdown_count_1 = attacker_kd_count
    else:
        print("Original punch missed.")

    if not Match_Over and defender_counter_chance >= 95:
        print(f"{defender['Name']} gets a counter opportunity!")

        if initiative_winner == 1:
            counter_win_2 += 1
        else:
            counter_win_1 += 1
        counter_punch = random.choices(punches, weights=defender_weights, k=1)[0]

        print(f"{defender['Name']} counters with a {counter_punch}!")

        # Defender throws another punch.
        if initiative_winner == 1:
            punch_count_2 += 1
            counter_attempting_fighter = boxer_2
            counter_attempting_archetype = B2AType
            counter_attacker_stamina = stamina_2
            counter_attacker_params = b2_params
            counter_attacker_stamina_factor = stamina_factor_2
            counter_defender_stamina_factor = stamina_factor_1
        else:
            punch_count_1 += 1
            counter_attempting_fighter = boxer_1
            counter_attempting_archetype = B1AType
            counter_attacker_stamina = stamina_1
            counter_attacker_params = b1_params
            counter_attacker_stamina_factor = stamina_factor_1
            counter_defender_stamina_factor = stamina_factor_2

        # Check whether the COUNTER lands.
        counter_landed = punch_landed(
            attacker,
            attacker_archetype,
            counter_attempting_fighter,
            counter_punch,
            counter_defender_stamina_factor,
            counter_attacker_stamina_factor,
        )

        if counter_landed:
            print("Counter landed!")
            shot_type = random.choice(["Head", "Body"])
            if counter_punch == "Body_Shot":
                shot_type = "Body"
            dmg, islivershotted = calculate_dmg(
                counter_attempting_fighter["Power"],
                counter_punch,
                shot_type,
                counter_attacker_stamina_factor,
            )
            counter_dmg = dmg * 1.10
            attacker_head, attacker_body, attacker_koed = apply_dmg(
                counter_dmg, attacker_head, attacker_body, islivershotted, shot_type
            )

            if attacker_koed:
                attacker_heart = attacker["Heart"]
                attacker_kd_count += 1
                # Single knockdown event - only call recover_from_ko once
                # Determine which condition to use for recovery based on shot_type
                if shot_type == "Head" or (attacker_head <= 0 and attacker_body > 0):
                    recovery_cond = attacker_head
                elif shot_type == "Body" or (attacker_body <= 0 and attacker_head > 0):
                    recovery_cond = attacker_body
                else:
                    # Both head and body <= 0
                    recovery_cond = (
                        attacker_head if shot_type == "Head" else attacker_body
                    )

                recovery_cond, attacker_got_up, attacker_stopped = recover_from_ko(
                    attacker_heart,
                    recovery_cond,
                    attacker_kd_count,
                    rounds,
                    counter_defender_stamina_factor,
                )
                # Update the condition that was used for recovery
                if shot_type == "Head" or (attacker_head <= 0 and attacker_body > 0):
                    attacker_head = recovery_cond
                else:
                    attacker_body = recovery_cond

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
                stoppage_1 = defender_stopped
                stoppage_2 = attacker_stopped

                knockdown_count_1 = defender_kd_count
                knockdown_count_2 = attacker_kd_count

            else:
                landed_punch_count_1 += 1
                counter_punch_landed_1 += 1
                head_cond_1 = attacker_head
                body_cond_1 = attacker_body
                head_cond_2 = defender_head
                body_cond_2 = defender_body
                stoppage_2 = defender_stopped
                stoppage_1 = attacker_stopped

                knockdown_count_2 = defender_kd_count
                knockdown_count_1 = attacker_kd_count

        else:
            print("Counter missed.")

    decay_1 = STAMINA_BASE_DECAY * b1_params["decay_multiplier"]
    decay_2 = STAMINA_BASE_DECAY * b2_params["decay_multiplier"]

    stamina_1 -= decay_1
    stamina_2 -= decay_2

    if initiative_winner == 1:
        stamina_1 -= STAMINA_PUNCH_COST
        if original_landed:
            if selected_punch == "Body_Shot":
                stamina_2 -= STAMINA_BODY_SHOT_COST
            else:
                stamina_2 -= STAMINA_DAMAGE_TAKEN_COST
        if not Match_Over and defender_counter_chance >= 95:
            stamina_2 -= STAMINA_PUNCH_COST
            if "counter_landed" in locals() and counter_landed:
                if counter_punch == "Body_Shot":
                    stamina_1 -= STAMINA_BODY_SHOT_COST
                else:
                    stamina_1 -= STAMINA_DAMAGE_TAKEN_COST
    else:
        stamina_2 -= STAMINA_PUNCH_COST
        if original_landed:
            if selected_punch == "Body_Shot":
                stamina_1 -= STAMINA_BODY_SHOT_COST
            else:
                stamina_1 -= STAMINA_DAMAGE_TAKEN_COST
        if not Match_Over and defender_counter_chance >= 95:
            stamina_1 -= STAMINA_PUNCH_COST
            if "counter_landed" in locals() and counter_landed:
                if counter_punch == "Body_Shot":
                    stamina_2 -= STAMINA_BODY_SHOT_COST
                else:
                    stamina_2 -= STAMINA_DAMAGE_TAKEN_COST

    stamina_1 = max(stamina_1, 0.0)
    stamina_2 = max(stamina_2, 0.0)

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
        stoppage_1,
        stoppage_2,
        Match_Over,
        winner,
        stamina_1,
        stamina_2,
    )


def punch_landed(
    boxer_to_be_hit,
    BTBHAType,
    boxer_hitting,
    punch_type,
    defender_stamina_factor=1.0,
    attacker_stamina_factor=1.0,
):

    block_type_value = {"Classic": 5, "Cross Arm": 10}
    punch_acc_modifier = {
        "Jab": +5,
        "Cross": 0,
        "Hook": -3,
        "Uppercut": -7,
        "Body_Shot": -5,
    }
    isFlashKO = False

    speed_tbh = boxer_to_be_hit["Speed"]
    defense_tbh = BTBHAType.iloc[-1]["Defense"]
    movement_tbh = BTBHAType.iloc[-1]["Movement"]

    speed_bth = boxer_hitting["Speed"]
    agility_bth = boxer_hitting["Agility"]

    movement_speed = movement_tbh + speed_tbh
    block_value = defense_tbh + block_type_value[boxer_to_be_hit["Block Style"]]

    defend_score = (
        (block_value * 0.6) + (movement_speed * 0.3) + random.randrange(-10, +10)
    ) * defender_stamina_factor

    attack_score = (
        (speed_bth * 0.6)
        + (agility_bth * 0.4)
        + punch_acc_modifier[punch_type]
        + random.randrange(-10, +10)
    ) * attacker_stamina_factor

    advantage = attack_score - defend_score
    hit_chance = 50 + (advantage * 0.5)

    if hit_chance < 5:
        hit_chance = 5

    if hit_chance > 95:
        hit_chance = 95

    print(hit_chance)
    if hit_chance <= random.randint(0, 100):
        print("Punch Missed")
        return False
    else:
        print("Punch landed")
        return True


def calculate_dmg(power, punch_type, shot_type, stamina_factor=1.0):

    punch_type_damage_modifier = {
        "Head": {
            "Jab": +5,
            "Cross": +7,
            "Hook": +10,
            "Uppercut": +15,
        },
        "Body": {
            "Jab": +3,
            "Cross": +12,
            "Hook": +16,
            "Uppercut": +18,
            "Body_Shot": +6,
        },
    }

    damage = 0
    isLiverShotted = False
    liver_shot_chance = random.randint(1, 20)

    if liver_shot_chance == 20:
        damage = 400
        isLiverShotted = True

        return damage, isLiverShotted

    damage = (power * 0.7 * stamina_factor) + (
        punch_type_damage_modifier[shot_type][punch_type]
    )
    return damage, isLiverShotted


def apply_dmg(damage, head_cond, body_cond, isLiverShotted, shot_type):

    isKO = False

    if shot_type == "Head":
        head_cond -= damage

    if shot_type == "Body":
        body_cond -= damage

    print(f"Head Condtion: {head_cond}")
    print(f"Body Condition:{body_cond}")

    if isLiverShotted:
        body_cond -= damage

        if random.randint(0, 21) <= 10:
            isKO = set_ko(True)
        else:
            isKO = set_ko(False)

    if head_cond <= 0:
        head_cond = 0
        isKO = set_ko(True)
    if body_cond <= 0:
        body_cond = 0
        isKO = set_ko(True)

    return head_cond, body_cond, isKO


def recover_from_ko(heart, cond, ko_count, rounds, stamina_factor=1.0):
    gotUp = False
    stopped = False
    recovery_modifier = 0.5
    recovery_threshold = 40
    recovery_value = 0
    if ko_count == 0:
        recovery_value = 2
    elif ko_count == 1:
        recovery_value = 1
    elif ko_count == 2:
        recovery_value = 0.5
    else:
        recovery_value = 0.1

    if rounds == 4 and ko_count >= 2:
        return cond, False, True

    if rounds == 8 and ko_count >= 3:
        return cond, False, True

    if rounds == 10 and ko_count >= 5:
        return cond, False, True

    recovery_chance = (heart * recovery_modifier * stamina_factor) + random.randint(
        0, 20
    )

    health_recovery = (heart * recovery_value) * 0.6
    cond = cond + health_recovery

    if recovery_chance <= recovery_threshold:
        gotUp = False
        return cond, gotUp, False
    else:
        gotUp = True
        return cond, gotUp, False


def simulate_round(
    rounds, boxer_1, boxer_2, boxer_1_archetype, boxer_2_archetype, watch_mode=True
):
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

    stamina_1 = float(boxer_1["Stamina"])
    stamina_2 = float(boxer_2["Stamina"])
    b1_params = get_stamina_params(boxer_1_archetype.iloc[0]["Archetype"])
    b2_params = get_stamina_params(boxer_2_archetype.iloc[0]["Archetype"])

    KO_win = False

    for round in range(rounds):
        initiative_wins_1 = 0
        initiative_wins_2 = 0
        counter_punch_count_1 = 0
        counter_punch_count_2 = 0
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
        stoppage_1 = False
        stoppage_2 = False

        Match_Over = False
        winner = None

        print(f"---- ROUND {round + 1} -----")
        for i in range(0, 200):
            if i % 5 == 0:
                (
                    initiative_wins_1,
                    initiative_wins_2,
                    counter_punch_count_1,
                    counter_punch_count_2,
                    total_punch_count_1,
                    total_punch_count_2,
                    landed_punch_count_1,
                    landed_punch_count_2,
                    normal_punch_count_1,
                    landed_counter_punch_1,
                    normal_punch_count_2,
                    landed_counter_punch_2,
                    head_cond_1,
                    body_cond_1,
                    head_cond_2,
                    body_cond_2,
                    knockdown_counts_1,
                    knockdown_counts_2,
                    stoppage_1,
                    stoppage_2,
                    Match_Over,
                    winner,
                    stamina_1,
                    stamina_2,
                ) = simulate_exchange(
                    boxer_1,
                    boxer_2,
                    boxer_1_archetype,
                    boxer_2_archetype,
                    initiative_wins_1,
                    initiative_wins_2,
                    counter_punch_count_1,
                    counter_punch_count_2,
                    total_punch_count_1,
                    total_punch_count_2,
                    landed_punch_count_1,
                    landed_punch_count_2,
                    normal_punch_count_1,
                    landed_counter_punch_1,
                    normal_punch_count_2,
                    landed_counter_punch_2,
                    head_cond_1,
                    body_cond_1,
                    head_cond_2,
                    body_cond_2,
                    rounds=rounds,
                    knockdown_count_1=knockdown_counts_1,
                    knockdown_count_2=knockdown_counts_2,
                    stamina_1=stamina_1,
                    stamina_2=stamina_2,
                    b1_params=b1_params,
                    b2_params=b2_params,
                )
                time.sleep(delay_value)
                if Match_Over:
                    break

        stamina_1 = min(100.0, stamina_1 + b1_params["recovery_per_round"])
        stamina_2 = min(100.0, stamina_2 + b2_params["recovery_per_round"])
        rounds_summary.append(
            {
                "Round": round + 1,
                "Boxer 1": {
                    "Boxer 1": boxer_1["Name"],
                    "Boxer 1 Initiative wins": initiative_wins_1,
                    "Boxer 1 Total Punches": total_punch_count_1,
                    "Boxer 1 Landed Punches": landed_punch_count_1,
                    "Boxer 1 Normal Punches Landed": normal_punch_count_1,
                    "Boxer 1 Counter Punch Landed": landed_counter_punch_1,
                    "Boxer 1 Knockdowns": knockdown_counts_1,
                },
                "Boxer 2": {
                    "Boxer 2": boxer_2["Name"],
                    "Boxer 2 Initiative wins": initiative_wins_2,
                    "Boxer 2 Total Punches": total_punch_count_2,
                    "Boxer 2 Landed Punches": landed_punch_count_2,
                    "Boxer 2 Normal Punches Landed": normal_punch_count_2,
                    "Boxer 2 Counter Punch Landed": landed_counter_punch_2,
                    "Boxer 2 Knockdowns": knockdown_counts_2,
                },
            }
        )
        if Match_Over == True:
            if stoppage_1 or stoppage_2:
                print(
                    f"winner by Technical Knock Out in Round {round + 1} is {winner['Name']}"
                )
                KO_win = True
                break
            else:
                KO_win = True
                print(f"winner by Knock Out in Round {round + 1} is {winner['Name']}")
                break

    print(f"---- ROUND {round + 1} Summary-----")

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
    loser_name = None
    winner_name = None
    if KO_win:
        if winner["Name"] == boxer_1["Name"]:
            winner_name = winner["Name"]
            loser_name = boxer_2["Name"]
        else:
            loser_name = boxer_1["Name"]
            winner_name = winner["Name"]

    return rounds_summary, KO_win, winner_name, loser_name


def set_ko(isKOed):
    return isKOed


def go_decision(rounds_summary):
    print("Deciding On winner")
    score_1 = judge_1(rounds_summary)
    score_2 = judge_2(rounds_summary)
    score_3 = judge_3(rounds_summary)
    isDraw = False

    results = [score_1, score_2, score_3]
    print(results)

    boxer_1_judges = 0
    boxer_2_judges = 0
    draws = 0

    for result in results:
        if result[0] > result[1]:
            boxer_1_judges += 1
        elif result[1] > result[0]:
            boxer_2_judges += 1
        else:
            draws += 1
    winner = loser = None
    if boxer_1_judges == 3:
        print(
            f"Your winner by Unanimous Decision! \n {rounds_summary[0]['Boxer 1']['Boxer 1']}"
        )
        winner = rounds_summary[0]["Boxer 1"]["Boxer 1"]
        loser = rounds_summary[0]["Boxer 2"]["Boxer 2"]
    elif boxer_1_judges == 2:
        print(
            f"Your winner by Split Decision! \n {rounds_summary[0]['Boxer 1']['Boxer 1']}"
        )
        winner = rounds_summary[0]["Boxer 1"]["Boxer 1"]
        loser = rounds_summary[0]["Boxer 2"]["Boxer 2"]
    elif boxer_2_judges == 3:
        print(
            f"Your winner by Unanimous Decision! \n {rounds_summary[0]['Boxer 2']['Boxer 2']}"
        )
        loser = rounds_summary[0]["Boxer 1"]["Boxer 1"]
        winner = rounds_summary[0]["Boxer 2"]["Boxer 2"]
    elif boxer_2_judges == 2:
        print(
            f"Your winner by Split Decision! \n {rounds_summary[0]['Boxer 2']['Boxer 2']}"
        )
        loser = rounds_summary[0]["Boxer 1"]["Boxer 1"]
        winner = rounds_summary[0]["Boxer 2"]["Boxer 2"]
    elif draws == 1:
        print("Match Drawed!")
        loser = rounds_summary[0]["Boxer 1"]["Boxer 1"]
        winner = rounds_summary[0]["Boxer 2"]["Boxer 2"]
        isDraw = True
    return winner, loser, isDraw


def judge_1(rounds):
    """
    Judge 1: "Clean Punching" specialist
    - Prioritizes: Clean punches landed, accuracy, counter punching
    - Weights: landed=1.0, accuracy=0.5, counters=0.3
    - Variance: ±0.3 (moderate consistency)
    """
    judge_weights = {
        "clean_punching": {"landed": 1.0, "accuracy": 0.5, "counters": 0.3},
        "aggression": {"landed": 0.3, "work_rate": 0.1},
        "defense": {"dodge_rate": 0.1, "counters": 0.1, "clean_punching": 0.2},
    }
    variance = 0.3

    score_1 = 0
    score_2 = 0
    for i in range(len(rounds)):
        r = rounds[i]
        b1 = r["Boxer 1"]
        b2 = r["Boxer 2"]

        s1, s2 = _score_round_10_point_must(
            b1["Boxer 1 Landed Punches"],
            b2["Boxer 2 Landed Punches"],
            b1["Boxer 1 Total Punches"],
            b2["Boxer 2 Total Punches"],
            b1["Boxer 1 Knockdowns"],
            b2["Boxer 2 Knockdowns"],
            b1["Boxer 1 Counter Punch Landed"],
            b2["Boxer 2 Counter Punch Landed"],
            judge_weights,
            variance,
        )
        score_1 += s1
        score_2 += s2

    print(f"First Judge (Clean Punching) Scored it: {score_1} - {score_2}")
    return (score_1, score_2)


def judge_2(rounds):
    """
    Judge 2: "Effective Aggression" specialist
    - Prioritizes: Volume of landed punches, work rate (total thrown), forward pressure
    - Weights: landed=0.8, work_rate=0.4
    - Variance: ±0.4 (slightly more variable)
    """
    judge_weights = {
        "clean_punching": {"landed": 0.5, "accuracy": 0.2, "counters": 0.1},
        "aggression": {"landed": 0.8, "work_rate": 0.4},
        "defense": {"dodge_rate": 0.05, "counters": 0.1, "clean_punching": 0.1},
    }
    variance = 0.4

    score_1 = 0
    score_2 = 0
    for i in range(len(rounds)):
        r = rounds[i]
        b1 = r["Boxer 1"]
        b2 = r["Boxer 2"]

        s1, s2 = _score_round_10_point_must(
            b1["Boxer 1 Landed Punches"],
            b2["Boxer 2 Landed Punches"],
            b1["Boxer 1 Total Punches"],
            b2["Boxer 2 Total Punches"],
            b1["Boxer 1 Knockdowns"],
            b2["Boxer 2 Knockdowns"],
            b1["Boxer 1 Counter Punch Landed"],
            b2["Boxer 2 Counter Punch Landed"],
            judge_weights,
            variance,
        )
        score_1 += s1
        score_2 += s2

    print(f"Second Judge (Effective Aggression) Scored it: {score_1} - {score_2}")
    return (score_1, score_2)


def judge_3(rounds):
    """
    Judge 3: "Ring Generalship & Defense" specialist
    - Prioritizes: Defense (making opponent miss), counter punching, ring control
    - Also considers clean punching as secondary
    - Weights: dodge_rate=0.8, counters=0.6, clean_punching=0.3
    - Variance: ±0.5 (most variable - defense is subjective)
    """
    judge_weights = {
        "clean_punching": {"landed": 0.3, "accuracy": 0.2, "counters": 0.2},
        "aggression": {"landed": 0.2, "work_rate": 0.1},
        "defense": {"dodge_rate": 0.8, "counters": 0.6, "clean_punching": 0.3},
    }
    variance = 0.5

    score_1 = 0
    score_2 = 0
    for i in range(len(rounds)):
        r = rounds[i]
        b1 = r["Boxer 1"]
        b2 = r["Boxer 2"]

        s1, s2 = _score_round_10_point_must(
            b1["Boxer 1 Landed Punches"],
            b2["Boxer 2 Landed Punches"],
            b1["Boxer 1 Total Punches"],
            b2["Boxer 2 Total Punches"],
            b1["Boxer 1 Knockdowns"],
            b2["Boxer 2 Knockdowns"],
            b1["Boxer 1 Counter Punch Landed"],
            b2["Boxer 2 Counter Punch Landed"],
            judge_weights,
            variance,
        )
        score_1 += s1
        score_2 += s2

    print(f"Third Judge (Ring Generalship) Scored it: {score_1} - {score_2}")
    return (score_1, score_2)


if __name__ == "__main__":
    isDraw = False
    isDecision = False
    rounds_summary = []
    winner = loser = None
    boxer_df, archetype_df = load_boxers(path_boxer_csv, path_archtype_csv)
    KO_win = False
    print("======Current Roster======")
    print(boxer_df[["Name", "Nickname", "Archetype"]])

    first_boxer_choice = int(input("Select Boxer 1: "))
    second_boxer_choice = int(input("Select Boxer 2: "))

    boxer_1, boxer_2 = select_boxers(first_boxer_choice, second_boxer_choice, boxer_df)
    boxer_1_archetype, boxer_2_archetype = get_archetypes(
        boxer_1, boxer_2, archetype_df
    )

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

    # Check if this is a title fight
    # Read current champion from rankings.csv
    isTitleFight = False
    rankings_path = Path.cwd() / "rankings.csv"
    if rankings_path.exists():
        try:
            rankings_df = pd.read_csv(rankings_path, index_col=0)
            if len(rankings_df) > 0 and rankings_df.index[0] == "C":
                current_champion = rankings_df.iloc[0]["Name"]
                # If either fighter is the current champion, ask if title fight
                if (
                    boxer_1["Name"] == current_champion
                    or boxer_2["Name"] == current_champion
                ):
                    print(f"\n{current_champion} is the current champion.")
                    title_choice = (
                        input("Is this a title fight? (y/n): ").strip().lower()
                    )
                    if title_choice == "y":
                        isTitleFight = True
                        print("This match is a TITLE FIGHT!")
        except Exception:
            pass

    rounds_summary, KO_win, winner, loser = simulate_round(
        rounds, boxer_1, boxer_2, boxer_1_archetype, boxer_2_archetype, watch_mode
    )

    if not KO_win:
        winner, loser, isDraw = go_decision(rounds_summary)
        isDecision = True

    else:
        print("Bye Bye")
    # print(winner,loser)
    new_result = result.Result(winner, loser, KO_win, isDecision, isDraw, isTitleFight)
    new_result.add_result()
