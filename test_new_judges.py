"""
Tests for the NEW judge scoring system - demonstrates improvements over old system.
"""
import simulator


def create_mock_rounds(boxer1_landed, boxer2_landed, boxer1_total, boxer2_total, 
                        boxer1_kd=0, boxer2_kd=0, boxer1_counters=0, boxer2_counters=0,
                        num_rounds=1):
    rounds = []
    for i in range(num_rounds):
        rounds.append({
            'Round': i+1,
            'Boxer 1': {
                'Boxer 1': 'Boxer1',
                'Boxer 1 Landed Punches': boxer1_landed,
                'Boxer 1 Total Punches': boxer1_total,
                'Boxer 1 Knockdowns': boxer1_kd,
                'Boxer 1 Counter Punch Landed': boxer1_counters,
            },
            'Boxer 2': {
                'Boxer 2': 'Boxer2',
                'Boxer 2 Landed Punches': boxer2_landed,
                'Boxer 2 Total Punches': boxer2_total,
                'Boxer 2 Knockdowns': boxer2_kd,
                'Boxer 2 Counter Punch Landed': boxer2_counters,
            }
        })
    return rounds


def test_new_judge_1_clean_punching():
    """
    NEW Judge 1: "Clean Punching" specialist
    - Prioritizes: Clean punches landed, accuracy, counter punching
    - 10-point must knockdowns: 1 KD = 10-8, 2 KD = 10-7, 3+ KD = 10-6
    - Variance: ±0.3 (moderate consistency)
    """
    print("=== Judge 1 (Clean Punching) Tests ===")
    
    # Clear round - Boxer1 lands more clean punches
    rounds = create_mock_rounds(50, 30, 100, 100)
    score = simulator.judge_1(rounds)
    assert score[0] > score[1], f"Clear round should favor Boxer1, got {score}"
    print(f"Clear round: {score} ✓")
    
    # Even round - variance may cause slight deviation
    rounds = create_mock_rounds(40, 40, 100, 100)
    score = simulator.judge_1(rounds)
    assert score in [(10, 10), (10, 9), (9, 10)], f"Even round should be ~10-10, got {score}"
    print(f"Even round: {score} ✓")
    
    # 1 Knockdown = 10-8
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=1)
    score = simulator.judge_1(rounds)
    assert score == (10, 8), f"Expected (10, 8), got {score}"
    print(f"1 KD: {score} ✓")
    
    # 2 Knockdowns = 10-7 (FIXED: old was 10-8)
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=2)
    score = simulator.judge_1(rounds)
    assert score == (10, 7), f"Expected (10, 7), got {score}"
    print(f"2 KDs: {score} ✓")
    
    # 3 Knockdowns = 10-6
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=3)
    score = simulator.judge_1(rounds)
    assert score == (10, 6), f"Expected (10, 6), got {score}"
    print(f"3 KDs: {score} ✓")


def test_new_judge_2_effective_aggression():
    """
    NEW Judge 2: "Effective Aggression" specialist
    - Prioritizes: Volume of landed punches, work rate (total thrown)
    - 10-point must knockdowns: 1 KD = 10-8, 2 KD = 10-7, 3+ KD = 10-6
    - Variance: ±0.4 (slightly more variable)
    """
    print("\n=== Judge 2 (Effective Aggression) Tests ===")
    
    # Clear round - more landed punches
    rounds = create_mock_rounds(50, 30, 100, 100)
    score = simulator.judge_2(rounds)
    assert score[0] > score[1], f"Clear round should favor Boxer1, got {score}"
    print(f"Clear round: {score} ✓")
    
    # Even round - variance may cause slight deviation
    rounds = create_mock_rounds(40, 40, 100, 100)
    score = simulator.judge_2(rounds)
    assert score in [(10, 10), (10, 9), (9, 10)], f"Even round should be ~10-10, got {score}"
    print(f"Even round: {score} ✓")
    
    # 1 Knockdown = 10-8
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=1)
    score = simulator.judge_2(rounds)
    assert score == (10, 8), f"Expected (10, 8), got {score}"
    print(f"1 KD: {score} ✓")
    
    # 2 Knockdowns = 10-7 (FIXED: old was 10-6)
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=2)
    score = simulator.judge_2(rounds)
    assert score == (10, 7), f"Expected (10, 7), got {score}"
    print(f"2 KDs: {score} ✓")


def test_new_judge_3_ring_generalship():
    """
    NEW Judge 3: "Ring Generalship & Defense" specialist
    - Prioritizes: Defense (making opponent miss), counter punching, ring control
    - Also considers clean punching as secondary
    - 10-point must knockdowns: 1 KD = 10-8, 2 KD = 10-7, 3+ KD = 10-6
    - Variance: ±0.5 (most variable - defense is subjective)
    """
    print("\n=== Judge 3 (Ring Generalship) Tests ===")
    
    # Defense matters - Boxer1 makes Boxer2 miss more
    rounds = create_mock_rounds(30, 10, 100, 100)  # Boxer2 misses 90, Boxer1 misses 70
    score = simulator.judge_3(rounds)
    assert score[0] > score[1], f"Defense should favor Boxer1, got {score}"
    print(f"Defense matters: {score} ✓")
    
    # 1 Knockdown = 10-8 (FIXED: old judge_3 ignored KDs!)
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=1)
    score = simulator.judge_3(rounds)
    assert score == (10, 8), f"Expected (10, 8), got {score}"
    print(f"1 KD: {score} ✓")
    
    # 2 Knockdowns = 10-7
    rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=2)
    score = simulator.judge_3(rounds)
    assert score == (10, 7), f"Expected (10, 7), got {score}"
    print(f"2 KDs: {score} ✓")


def test_judge_disagreement_variance():
    """
    Test that judges can disagree on close fights due to variance
    and different philosophies
    """
    print("\n=== Judge Disagreement / Variance Tests ===")
    
    def run_fight(landed1, landed2, total1, total2, rounds=12):
        round_list = []
        for i in range(rounds):
            round_list.append({
                'Round': i+1,
                'Boxer 1': {
                    'Boxer 1': 'Boxer1',
                    'Boxer 1 Landed Punches': landed1,
                    'Boxer 1 Total Punches': total1,
                    'Boxer 1 Knockdowns': 0,
                    'Boxer 1 Counter Punch Landed': 0,
                },
                'Boxer 2': {
                    'Boxer 2': 'Boxer2',
                    'Boxer 2 Landed Punches': landed2,
                    'Boxer 2 Total Punches': total2,
                    'Boxer 2 Knockdowns': 0,
                    'Boxer 2 Counter Punch Landed': 0,
                }
            })
        return round_list
    
    # Run multiple VERY close fights (22 vs 20) - should get mix of winners
    boxer1_wins = 0
    boxer2_wins = 0
    draws = 0
    sd_count = 0
    ud_count = 0
    
    for _ in range(50):
        round_list = run_fight(22, 20, 50, 50, 12)  # Very close fight
        winner, loser, is_draw = simulator.go_decision(round_list)
        if is_draw:
            draws += 1
        elif winner == 'Boxer1':
            boxer1_wins += 1
        else:
            boxer2_wins += 1
        
        # Check decision type by looking at judge scores
        j1 = simulator.judge_1(round_list)
        j2 = simulator.judge_2(round_list)
        j3 = simulator.judge_3(round_list)
        
        judges_for_1 = sum(1 for s in [j1, j2, j3] if s[0] > s[1])
        judges_for_2 = sum(1 for s in [j1, j2, j3] if s[1] > s[0])
        
        if judges_for_1 == 2 and judges_for_2 == 1:
            sd_count += 1
        elif judges_for_1 == 3 or judges_for_2 == 3:
            ud_count += 1
    
    print(f"Results over 50 VERY close fights (22 vs 20):")
    print(f"  Boxer1 wins: {boxer1_wins}, Boxer2 wins: {boxer2_wins}, Draws: {draws}")
    print(f"  Unanimous Decisions: {ud_count}, Split Decisions: {sd_count}")
    
    # Should have some split decisions and not all unanimous
    assert sd_count > 0, "Should have some Split Decisions due to variance"
    assert ud_count > 0, "Should have some Unanimous Decisions"
    # With very close fight, both should win sometimes
    assert boxer1_wins > 0 and boxer2_wins > 0, "Both should win sometimes in very close fight"
    print(f"✓ Meaningful judge disagreement exists")


def test_knockdown_scoring_consistency():
    """
    All three judges should now score knockdowns consistently per 10-point must
    """
    print("\n=== Knockdown Scoring Consistency ===")
    
    for kd in [1, 2, 3]:
        rounds = create_mock_rounds(10, 0, 20, 20, boxer1_kd=kd)
        j1 = simulator.judge_1(rounds)
        j2 = simulator.judge_2(rounds)
        j3 = simulator.judge_3(rounds)
        
        expected = {1: (10, 8), 2: (10, 7), 3: (10, 6)}[kd]
        
        assert j1 == expected, f"J1 {kd} KD: expected {expected}, got {j1}"
        assert j2 == expected, f"J2 {kd} KD: expected {expected}, got {j2}"
        assert j3 == expected, f"J3 {kd} KD: expected {expected}, got {j3}"
        print(f"{kd} KD: All judges score {expected} ✓")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING NEW JUDGE SCORING SYSTEM")
    print("=" * 60)
    
    test_new_judge_1_clean_punching()
    test_new_judge_2_effective_aggression()
    test_new_judge_3_ring_generalship()
    test_knockdown_scoring_consistency()
    test_judge_disagreement_variance()
    
    print("\n" + "=" * 60)
    print("ALL NEW JUDGE TESTS PASSED!")
    print("=" * 60)