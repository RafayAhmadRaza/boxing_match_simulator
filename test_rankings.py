"""
Tests for Auto-Update Rankings and Champion Preservation features.
These tests verify the NEW behavior after implementation.
"""
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import os
import sys
import importlib

# Add the project directory to path
sys.path.insert(0, '/home/rafayahmadraza/Projects/boxing_simulator')


def create_test_environment():
    """Create a temporary directory with test CSV files."""
    temp_dir = tempfile.mkdtemp()
    
    # Create boxer.csv
    boxer_data = pd.DataFrame([
        {"Name": "Champion", "Nickname": "Champ", "weight class": "Middle_weight", "Height": "6'0\"", "weight": 160, "Stance Style": "Orthodox", "Base Stance": "Balanced", "Punch Style": "Basic", "Block Style": "Classic", "Signature Move": "Test", "Power": 80, "Speed": 80, "Agility": 80, "Stamina": 80, "Chin": 80, "Body": 80, "Heart": 80, "Cuts": 80, "Archetype": "Technical"},
        {"Name": "Challenger", "Nickname": "Chall", "weight class": "Middle_weight", "Height": "6'0\"", "weight": 160, "Stance Style": "Orthodox", "Base Stance": "Balanced", "Punch Style": "Basic", "Block Style": "Classic", "Signature Move": "Test", "Power": 80, "Speed": 80, "Agility": 80, "Stamina": 80, "Chin": 80, "Body": 80, "Heart": 80, "Cuts": 80, "Archetype": "Technical"},
        {"Name": "Other1", "Nickname": "O1", "weight class": "Middle_weight", "Height": "6'0\"", "weight": 160, "Stance Style": "Orthodox", "Base Stance": "Balanced", "Punch Style": "Basic", "Block Style": "Classic", "Signature Move": "Test", "Power": 80, "Speed": 80, "Agility": 80, "Stamina": 80, "Chin": 80, "Body": 80, "Heart": 80, "Cuts": 80, "Archetype": "Technical"},
        {"Name": "Other2", "Nickname": "O2", "weight class": "Middle_weight", "Height": "6'0\"", "weight": 160, "Stance Style": "Orthodox", "Base Stance": "Balanced", "Punch Style": "Basic", "Block Style": "Classic", "Signature Move": "Test", "Power": 80, "Speed": 80, "Agility": 80, "Stamina": 80, "Chin": 80, "Body": 80, "Heart": 80, "Cuts": 80, "Archetype": "Technical"},
    ])
    
    # Create results.csv with initial records
    # Champion: 10 wins, 0 losses, 5 KO = Score: 10*10 + 5*5 = 125
    # Challenger: 8 wins, 2 losses, 4 KO = Score: 8*10 + 4*5 - 2*6 = 88
    results_data = pd.DataFrame([
        {"Name": "Champion", "wins": 10, "losses": 0, "draws": 0, "ko wins": 5, "ko losses": 0, "decision wins": 5, "decision losses": 0},
        {"Name": "Challenger", "wins": 8, "losses": 2, "draws": 0, "ko wins": 4, "ko losses": 1, "decision wins": 4, "decision losses": 1},
        {"Name": "Other1", "wins": 5, "losses": 5, "draws": 0, "ko wins": 2, "ko losses": 3, "decision wins": 3, "decision losses": 2},
        {"Name": "Other2", "wins": 3, "losses": 7, "draws": 0, "ko wins": 1, "ko losses": 4, "decision wins": 2, "decision losses": 3},
    ])
    
    # Create rankings.csv with champion designated
    # Champion is "Champion" with index "C"
    rankings_data = pd.DataFrame({
        "Name": ["Champion", "Challenger", "Other1", "Other2"],
        "wins": [10, 8, 5, 3],
        "losses": [0, 2, 5, 7],
        "draws": [0, 0, 0, 0],
        "ko wins": [5, 4, 2, 1],
        "ko losses": [0, 1, 3, 4],
        "decision wins": [5, 4, 3, 2],
        "decision losses": [0, 1, 2, 3],
        "Score": [125, 88, 14, -15]
    }, index=["C", 1, 2, 3])
    
    boxer_path = Path(temp_dir) / "boxer.csv"
    results_path = Path(temp_dir) / "results.csv"
    rankings_path = Path(temp_dir) / "rankings.csv"
    archetypes_path = Path(temp_dir) / "archetypes.csv"
    
    boxer_data.to_csv(boxer_path, index=False)
    results_data.to_csv(results_path, index=False)
    rankings_data.to_csv(rankings_path, index=True)
    
    # Copy archetypes.csv
    shutil.copy2("/home/rafayahmadraza/Projects/boxing_simulator/archetypes.csv", archetypes_path)
    
    return temp_dir, boxer_path, results_path, rankings_path, archetypes_path


def test_ranker_module_imports():
    """Test that ranker module can be imported and has the expected functions."""
    import ranker
    importlib.reload(ranker)
    
    assert hasattr(ranker, 'calculate_scores'), "Missing calculate_scores"
    assert hasattr(ranker, 'get_previous_champion'), "Missing get_previous_champion"
    assert hasattr(ranker, 'compute_rankings'), "Missing compute_rankings"
    assert hasattr(ranker, 'update_rankings'), "Missing update_rankings"
    assert hasattr(ranker, 'print_rankings'), "Missing print_rankings"
    print("✓ ranker module has all expected functions")


def test_get_previous_champion():
    """Test reading champion from rankings.csv."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import ranker
        importlib.reload(ranker)
        
        champion = ranker.get_previous_champion(Path("rankings.csv"))
        assert champion == "Champion", f"Expected 'Champion', got '{champion}'"
        print("✓ get_previous_champion reads champion correctly")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_compute_rankings_preserves_champion():
    """Test that compute_rankings keeps champion at top regardless of Score."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import ranker
        importlib.reload(ranker)
        
        results_df = pd.read_csv(results_path)
        
        # Compute rankings with champion specified
        final_rankings = ranker.compute_rankings(results_df, champion_name="Champion")
        
        # Champion should be at index "C"
        assert final_rankings.index[0] == "C", f"Champion should be at index 'C', got {final_rankings.index[0]}"
        assert final_rankings.iloc[0]["Name"] == "Champion", f"First row should be Champion, got {final_rankings.iloc[0]['Name']}"
        
        # Even if Challenger has higher Score after manual edit, Champion stays at top
        # (In our test data Champion has higher Score anyway, but the logic should work)
        print("✓ compute_rankings preserves champion at index 'C'")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_compute_rankings_without_champion():
    """Test compute_rankings when no champion specified."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import ranker
        importlib.reload(ranker)
        
        results_df = pd.read_csv(results_path)
        
        # Compute rankings WITHOUT champion
        final_rankings = ranker.compute_rankings(results_df, champion_name=None)
        
        # Should be sorted by Score with numeric index starting at 1
        assert final_rankings.index[0] == 1, f"First index should be 1, got {final_rankings.index[0]}"
        assert final_rankings.iloc[0]["Name"] == "Champion", f"Highest Score should be first"
        print("✓ compute_rankings without champion works")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_update_rankings_auto_updates():
    """Test that update_rankings writes rankings.csv automatically."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import ranker
        importlib.reload(ranker)
        
        # Call update_rankings with champion
        final_rankings, champ_used = ranker.update_rankings(
            Path("results.csv"), Path("rankings.csv"), champion_name="Champion"
        )
        
        # Verify file was written
        assert rankings_path.exists(), "rankings.csv should be created"
        
        # Read back and verify
        df = pd.read_csv(rankings_path, index_col=0)
        assert df.index[0] == "C", "Champion should be at index 'C'"
        assert df.iloc[0]["Name"] == "Champion", "Champion should be first"
        print("✓ update_rankings writes rankings.csv correctly")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_result_class_has_title_fight_flag():
    """Test that Result class has isTitleFight parameter."""
    import result
    importlib.reload(result)
    
    # Create Result with title fight flag
    res = result.Result("Winner", "Loser", isKO=True, isDecision=False, isDraw=False, isTitleFight=True)
    assert res.isTitleFight == True, "isTitleFight should be True"
    
    # Default should be False
    res2 = result.Result("Winner", "Loser", isKO=True, isDecision=False, isDraw=False)
    assert res2.isTitleFight == False, "isTitleFight should default to False"
    print("✓ Result class has isTitleFight parameter")


def test_result_add_result_calls_ranker():
    """Test that Result.add_result() calls ranker.update_rankings."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import result
        importlib.reload(result)
        
        # Add a regular (non-title) result
        res = result.Result("Challenger", "Other1", isKO=False, isDecision=True, isDraw=False, isTitleFight=False)
        res.add_result()
        
        # Verify rankings.csv was updated
        assert rankings_path.exists(), "rankings.csv should exist"
        
        df = pd.read_csv(rankings_path, index_col=0)
        assert df.index[0] == "C", "Champion should still be at index 'C'"
        assert df.iloc[0]["Name"] == "Champion", "Champion should still be first"
        print("✓ Result.add_result() auto-updates rankings and preserves champion")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_title_fight_changes_champion():
    """Test that title fight result changes champion."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import result
        importlib.reload(result)
        
        # Add a TITLE FIGHT result where Challenger beats Champion
        res = result.Result("Challenger", "Champion", isKO=False, isDecision=True, isDraw=False, isTitleFight=True)
        res.add_result()
        
        # Verify rankings.csv was updated with new champion
        df = pd.read_csv(rankings_path, index_col=0)
        assert df.index[0] == "C", "New champion should be at index 'C'"
        assert df.iloc[0]["Name"] == "Challenger", f"Challenger should be new champion, got {df.iloc[0]['Name']}"
        print("✓ Title fight correctly changes champion")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_title_fight_champion_defends():
    """Test that champion defending title stays champion."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import result
        importlib.reload(result)
        
        # Add a TITLE FIGHT result where Champion beats Challenger
        res = result.Result("Champion", "Challenger", isKO=True, isDecision=False, isDraw=False, isTitleFight=True)
        res.add_result()
        
        # Champion should remain champion
        df = pd.read_csv(rankings_path, index_col=0)
        assert df.index[0] == "C", "Champion should be at index 'C'"
        assert df.iloc[0]["Name"] == "Champion", f"Champion should remain champion, got {df.iloc[0]['Name']}"
        print("✓ Champion defending title stays champion")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_non_title_fight_preserves_champion_even_if_challenger_wins():
    """Test that non-title fight preserves champion even if challenger overtakes in Score."""
    temp_dir, boxer_path, results_path, rankings_path, archetypes_path = create_test_environment()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        import result
        importlib.reload(result)
        
        # Simulate challenger winning many non-title fights to overtake in Score
        results_df = pd.read_csv(results_path)
        idx = results_df[results_df["Name"] == "Challenger"].index[0]
        results_df.loc[idx, "wins"] += 10
        results_df.loc[idx, "decision wins"] += 10
        results_df.to_csv(results_path, index=False)
        
        # Now add a regular (non-title) result where Challenger beats Other1
        res = result.Result("Challenger", "Other1", isKO=False, isDecision=True, isDraw=False, isTitleFight=False)
        res.add_result()
        
        # Champion should STILL be champion because it wasn't a title fight
        df = pd.read_csv(rankings_path, index_col=0)
        assert df.index[0] == "C", "Champion should be at index 'C'"
        assert df.iloc[0]["Name"] == "Champion", f"Champion should remain champion after non-title fight, got {df.iloc[0]['Name']}"
        print("✓ Non-title fight preserves champion even if challenger has higher Score")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


def test_bootstrap_champion_when_none_exists():
    """Test that first run (no rankings.csv) works - no champion designated yet."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        # Create minimal results.csv only (no rankings.csv)
        results_data = pd.DataFrame([
            {"Name": "FighterA", "wins": 5, "losses": 0, "draws": 0, "ko wins": 3, "ko losses": 0, "decision wins": 2, "decision losses": 0},
            {"Name": "FighterB", "wins": 3, "losses": 2, "draws": 0, "ko wins": 1, "ko losses": 1, "decision wins": 2, "decision losses": 1},
        ])
        results_path = Path("results.csv")
        rankings_path = Path("rankings.csv")
        results_data.to_csv(results_path, index=False)
        
        import ranker
        importlib.reload(ranker)
        
        # Update rankings without existing rankings.csv and no champion specified
        # Should work without error (bootstrap case)
        final_rankings, champ = ranker.update_rankings(results_path, rankings_path, champion_name=None)
        
        assert rankings_path.exists(), "rankings.csv should be created"
        assert champ is None, "No champion should be set on bootstrap"
        
        # Should be sorted by Score with FighterA first
        df = pd.read_csv(rankings_path, index_col=0)
        assert df.index[0] == 1, "First index should be 1 (no champion flag)"
        assert df.iloc[0]["Name"] == "FighterA", "Highest Score should be first"
        print("✓ Bootstrap case works - no champion designated on first run")
        
    finally:
        os.chdir(old_cwd)
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("Running tests for NEW ranking features...")
    print("=" * 60)
    
    tests = [
        ("ranker module imports", test_ranker_module_imports),
        ("get_previous_champion", test_get_previous_champion),
        ("compute_rankings preserves champion", test_compute_rankings_preserves_champion),
        ("compute_rankings without champion", test_compute_rankings_without_champion),
        ("update_rankings auto-updates", test_update_rankings_auto_updates),
        ("Result has title fight flag", test_result_class_has_title_fight_flag),
        ("Result.add_result calls ranker", test_result_add_result_calls_ranker),
        ("Title fight changes champion", test_title_fight_changes_champion),
        ("Champion defends title", test_title_fight_champion_defends),
        ("Non-title preserves champion", test_non_title_fight_preserves_champion_even_if_challenger_wins),
        ("Bootstrap champion", test_bootstrap_champion_when_none_exists),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\nTesting: {name}...")
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"   FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED")