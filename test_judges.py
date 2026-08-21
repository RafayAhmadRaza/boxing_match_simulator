"""
Tests for the judge scoring system - documents current behavior and weaknesses.
"""
import simulator


def create_mock_rounds(boxer1_landed, boxer2_landed, boxer1_total, boxer2_total, 
                        boxer1_kd=0, boxer2_kd=0, boxer1_counters=0, boxer2_counters=0):
    """Create a mock rounds_summary for testing."""
    return [{
        "Round": 1,
        "Boxer 1": {
            "Boxer 1": "Boxer1",
            "Boxer 1 Landed Punches": boxer1_landed,
            "Boxer 1 Total Punches": boxer1_total,
            "Boxer 1 Knockdowns": boxer1_kd,
            "Boxer 1 Counter Punch Landed": boxer1_counters,
        },
        "Boxer 2": {
            "Boxer 2": "Boxer2",
            "Boxer 2 Landed Punches": boxer2_landed,
            "Boxer 2 Total Punches": boxer2_total,
            "Boxer 2 Knockdowns": boxer2_kd,
            "Boxer 2 Counter Punch Landed": boxer2_counters,
        }
    }]


def test_current_judge_1_logic():
    """
    Judge 1 CURRENT logic:
    - If knockdown: 10-8 (1 KD) or 10-8 (2 KD) - note: 2 KD same as 1 KD!
    - Else: compare accuracy % -> 10-9 for higher accuracy, 10-10 if equal
    
    WEAKNESSES:
    1. 2 knockdowns scored same as 1 knockdown (both 10-8)
    2. Only uses accuracy %, ignores total volume
    3. No distinction between close round and dominant round (both 10-9)
    4. No variance - deterministic
    """
    rounds = create_mock_rounds(50, 30, 100, 100)  # Boxer1 50% accuracy, Boxer2 30%
    score = simulator.judge_1(rounds)
    print(f"Judge 1 - Clear round (50% vs 30% accuracy): {score}")
    # Expect Boxer1 to win 10-9
    
    rounds = create_mock_rounds(40, 40, 100, 100)  # Even accuracy
    score = simulator.judge_1(rounds)
    print(f"Judge 1 - Even round (40% vs 40%): {score}")
    # Expect 10-10
    
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=1)  # Boxer1 KD
    score = simulator.judge_1(rounds)
    print(f"Judge 1 - 1 Knockdown: {score}")
    # Expect 10-8
    
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=2)  # Boxer1 2 KDs
    score = simulator.judge_1(rounds)
    print(f"Judge 1 - 2 Knockdowns: {score}")
    # BUG: Also 10-8 (same as 1 KD!)
    
    return score


def test_current_judge_2_logic():
    """
    Judge 2 CURRENT logic:
    - If knockdown diff != 0: 10 vs (10 - 2*kd_diff), min 6
    - Else: compare total landed punches -> 10-9 for more landed, 10-10 if equal
    
    WEAKNESSES:
    1. Ignores accuracy completely - just raw landed count
    2. KD scoring: 1 KD = 10-8, 2 KD = 10-6, 3 KD = 10-6 (capped)
    3. No distinction between close and dominant rounds
    4. No variance - deterministic
    """
    rounds = create_mock_rounds(50, 30, 100, 100)
    score = simulator.judge_2(rounds)
    print(f"Judge 2 - Clear round (50 vs 30 landed): {score}")
    
    rounds = create_mock_rounds(40, 40, 100, 100)
    score = simulator.judge_2(rounds)
    print(f"Judge 2 - Even round: {score}")
    
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=1)
    score = simulator.judge_2(rounds)
    print(f"Judge 2 - 1 Knockdown: {score}")
    # Expect 10-8
    
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=2)
    score = simulator.judge_2(rounds)
    print(f"Judge 2 - 2 Knockdowns: {score}")
    # Expect 10-6
    
    return score


def test_current_judge_3_logic():
    """
    Judge 3 CURRENT logic:
    - Compares "dodged punches" (total - landed) -> 10-9 for more dodged
    - Also has counter_punch_landed data but DOESN'T USE IT!
    
    WEAKNESSES:
    1. Only looks at defense (dodged), ignores offense completely
    2. Counter punch data tracked but NOT USED in scoring
    3. No knockdown consideration at all!
    4. No variance - deterministic
    """
    rounds = create_mock_rounds(50, 30, 100, 100)  # Boxer1 threw 100, landed 50 (missed 50); Boxer2 threw 100, landed 30 (missed 70)
    # Boxer2 "dodged" more (70 vs 50) -> Judge 3 favors Boxer2!
    score = simulator.judge_3(rounds)
    print(f"Judge 3 - Clear offense round but more misses: {score}")
    # Expect Boxer2 to win 10-9 (because Boxer2 missed more = "dodged more")
    
    rounds = create_mock_rounds(40, 40, 100, 100)
    score = simulator.judge_3(rounds)
    print(f"Judge 3 - Even round: {score}")
    
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=1)
    score = simulator.judge_3(rounds)
    print(f"Judge 3 - 1 Knockdown (ignored!): {score}")
    # KD completely ignored!
    
    return score


def test_judges_are_deterministic_and_similar():
    """
    WEAKNESS: All three judges are deterministic (no randomness/variance).
    Given same input, they always produce same output.
    This means Split Decisions can only happen if judges have DIFFERENT
    deterministic criteria, not because they "see the fight differently".
    """
    rounds = create_mock_rounds(50, 30, 100, 100)
    s1 = simulator.judge_1(rounds)
    s2 = simulator.judge_2(rounds)
    s3 = simulator.judge_3(rounds)
    print(f"All three judges on same round: J1={s1}, J2={s2}, J3={s3}")
    
    # They often disagree because of different criteria, not variance
    # But the disagreement is structural, not realistic


def test_current_go_decision():
    """
    Test the overall decision logic.
    """
    rounds = create_mock_rounds(50, 30, 100, 100)
    winner, loser, is_draw = simulator.go_decision(rounds)
    print(f"Decision - Clear round: winner={winner}, loser={loser}, draw={is_draw}")
    
    rounds = create_mock_rounds(40, 40, 100, 100)
    winner, loser, is_draw = simulator.go_decision(rounds)
    print(f"Decision - Even round: winner={winner}, loser={loser}, draw={is_draw}")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING CURRENT JUDGE SCORING SYSTEM")
    print("=" * 60)
    
    print("\n--- Judge 1 (Accuracy-based) ---")
    test_current_judge_1_logic()
    
    print("\n--- Judge 2 (Landed punches + KD) ---")
    test_current_judge_2_logic()
    
    print("\n--- Judge 3 (Defense/dodged only) ---")
    test_current_judge_3_logic()
    
    print("\n--- Judges are deterministic ---")
    test_judges_are_deterministic_and_similar()
    
    print("\n--- go_decision ---")
    test_current_go_decision()
    
    print("\n" + "=" * 60)
    print("CURRENT WEAKNESSES SUMMARY:")
    print("=" * 60)
    print("1. Judge 1: 2 KDs scored same as 1 KD (both 10-8)")
    print("2. Judge 1: Only accuracy, ignores volume/dominance")
    print("3. Judge 2: Ignores accuracy, only raw landed count")
    print("4. Judge 2: KD scoring caps at 10-6 (2+ KDs same)")
    print("5. Judge 3: ONLY defense, ignores offense AND knockdowns!")
    print("6. Judge 3: Counter punch data tracked but UNUSED")
    print("7. ALL: No variance - deterministic, no realistic judge disagreement")
    print("8. ALL: No 10-point must nuance (10-8, 10-9, 10-10 only)")
    print("9. ALL: No round-by-round 10-point must, just cumulative")