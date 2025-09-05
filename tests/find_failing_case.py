#!/usr/bin/env python3
"""
Find a failing random seed case
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import (
    load_members, load_groups, calculate_group_sizes,
    allocate_seats_with_groups, calculate_group_conflicts
)
import random

def test_with_seed(seed):
    """Test allocation with a specific seed"""
    random.seed(seed)
    
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    teams = allocate_seats_with_groups(members, group_sizes, groups)
    conflicts = calculate_group_conflicts(groups, teams)
    
    return conflicts, teams

def find_failing_cases():
    """Find random seeds that produce conflicts"""
    print("Searching for failing cases...")
    
    failing_cases = []
    
    for seed in range(1000):
        conflicts, teams = test_with_seed(seed)
        
        if conflicts > 0:
            failing_cases.append((seed, conflicts, teams))
            print(f"FOUND FAILING CASE: seed={seed}, conflicts={conflicts}")
            
            # Show the conflicting groups
            members = load_members()
            groups = load_groups()
            
            for group_name, group_members in groups.items():
                team_distribution = {}
                for member in group_members:
                    for team_idx, team in enumerate(teams):
                        if member in team:
                            if team_idx not in team_distribution:
                                team_distribution[team_idx] = []
                            team_distribution[team_idx].append(member)
                            break
                
                # Check if any team has multiple members from this group
                for team_idx, members_in_team in team_distribution.items():
                    if len(members_in_team) > 1:
                        print(f"  Group '{group_name}' has {len(members_in_team)} members in Team {team_idx+1}: {members_in_team}")
            
            print()
            
            if len(failing_cases) >= 5:  # Stop after finding 5 cases
                break
        
        if seed % 100 == 0:
            print(f"  Tested up to seed {seed}...")
    
    print(f"\nFound {len(failing_cases)} failing cases out of {seed+1} tested")
    return failing_cases

if __name__ == "__main__":
    find_failing_cases()