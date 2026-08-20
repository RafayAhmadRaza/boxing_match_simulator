"""
Tests for the double-KO overwrite bug fix in simulate_exchange.
"""
import random
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
import simulator


def test_fix_single_recover_call_per_knockdown():
    """
    After fix: each knockdown event (original punch or counter) should
    call recover_from_ko exactly ONCE, not twice.
    """
    import inspect
    source = inspect.getsource(simulator.simulate_exchange)
    
    # Count recover_from_ko assignments in each KO block
    original_punch_assignments = source.count('defender_got_up, defender_stopped = recover_from_ko')
    counter_punch_assignments = source.count('attacker_got_up, attacker_stopped = recover_from_ko')
    
    print(f"Original punch recover_from_ko assignments: {original_punch_assignments}")
    print(f"Counter punch recover_from_ko assignments: {counter_punch_assignments}")
    
    # After fix: exactly 1 assignment per KO block = 2 total
    total_assignments = original_punch_assignments + counter_punch_assignments
    assert total_assignments == 2, f"Expected 2 recover_from_ko assignments (one per KO block), got {total_assignments}"
    print("FIX CONFIRMED: Only one recover_from_ko call per knockdown event")


def test_fix_no_double_if_pattern():
    """
    After fix: the old double-if pattern (two separate if statements
    both calling recover_from_ko) should be gone.
    """
    import inspect
    source = inspect.getsource(simulator.simulate_exchange)
    
    # The old pattern had two separate if statements in sequence
    # Find the original punch KO block
    original_ko_start = source.find('if defender_koed:')
    original_ko_end = source.find('if defender_got_up == True:')
    original_ko_block = source[original_ko_start:original_ko_end]
    
    # Check for old pattern: two separate if statements
    old_pattern = (
        'if defender_head <= 0:' in original_ko_block and
        'if defender_body <= 0:' in original_ko_block and
        original_ko_block.index('if defender_head <= 0:') < original_ko_block.index('if defender_body <= 0:')
    )
    
    print(f"Original punch block - Old double-if pattern present: {old_pattern}")
    assert not old_pattern, "Old double-if pattern still present in original punch block"
    
    # Check counter punch block
    counter_ko_start = source.find('if attacker_koed:')
    counter_ko_end = source.find('if attacker_got_up == True:')
    counter_ko_block = source[counter_ko_start:counter_ko_end]
    
    old_pattern_counter = (
        'if attacker_head <= 0:' in counter_ko_block and
        'if attacker_body <= 0:' in counter_ko_block and
        counter_ko_block.index('if attacker_head <= 0:') < counter_ko_block.index('if attacker_body <= 0:')
    )
    
    print(f"Counter punch block - Old double-if pattern present: {old_pattern_counter}")
    assert not old_pattern_counter, "Old double-if pattern still present in counter punch block"
    
    print("FIX CONFIRMED: No double-if pattern in either KO block")


def test_fix_uses_shot_type_for_recovery():
    """
    After fix: the recovery should use the shot_type (Head/Body) that
    actually caused the knockdown, not arbitrarily the body condition.
    """
    import inspect
    source = inspect.getsource(simulator.simulate_exchange)
    
    # Verify the fix uses shot_type to determine which condition to use
    original_ko_start = source.find('if defender_koed:')
    original_ko_end = source.find('if defender_got_up == True:')
    original_ko_block = source[original_ko_start:original_ko_end]
    
    # The fix should check shot_type == "Head" or shot_type == "Body"
    uses_shot_type = 'shot_type == "Head"' in original_ko_block and 'shot_type == "Body"' in original_ko_block
    print(f"Original punch block uses shot_type for recovery: {uses_shot_type}")
    assert uses_shot_type, "Fix should use shot_type to determine recovery condition"
    
    counter_ko_start = source.find('if attacker_koed:')
    counter_ko_end = source.find('if attacker_got_up == True:')
    counter_ko_block = source[counter_ko_start:counter_ko_end]
    
    uses_shot_type_counter = 'shot_type == "Head"' in counter_ko_block and 'shot_type == "Body"' in counter_ko_block
    print(f"Counter punch block uses shot_type for recovery: {uses_shot_type_counter}")
    assert uses_shot_type_counter, "Counter fix should use shot_type to determine recovery condition"
    
    print("FIX CONFIRMED: shot_type used to determine recovery condition")


if __name__ == "__main__":
    print("Testing double-KO bug FIX...")
    test_fix_single_recover_call_per_knockdown()
    test_fix_no_double_if_pattern()
    test_fix_uses_shot_type_for_recovery()
    print("\nAll fix verification tests PASSED!")