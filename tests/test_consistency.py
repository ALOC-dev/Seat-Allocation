#!/usr/bin/env python3
"""
Algorithm consistency test - check if group constraints are consistently satisfied
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import (
    load_members, load_groups, calculate_group_sizes,
    allocate_seats_with_groups, calculate_group_conflicts
)

def test_consistency(num_runs=10):
    """Run the algorithm multiple times and check consistency"""
    
    # Load data
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    print(f"Testing with {len(members)} members, {len(groups)} groups, team sizes: {group_sizes}")
    print(f"Groups: {list(groups.keys())}")
    print("-" * 60)
    
    conflict_counts = []
    
    for i in range(num_runs):
        teams = allocate_seats_with_groups(members, group_sizes, groups)
        conflicts = calculate_group_conflicts(groups, teams)
        conflict_counts.append(conflicts)
        
        print(f"Run {i+1:2d}: {conflicts} conflicts {'✅' if conflicts == 0 else '❌'}")
        
        # Show group distribution for first few runs
        if i < 3 or conflicts > 0:
            print(f"        Group distributions:")
            for group_name, group_members in groups.items():
                team_distribution = {}
                for member in group_members:
                    for team_idx, team in enumerate(teams):
                        if member in team:
                            if team_idx not in team_distribution:
                                team_distribution[team_idx] = []
                            team_distribution[team_idx].append(member)
                            break
                
                distribution_str = []
                for team_idx, members_in_team in team_distribution.items():
                    if len(members_in_team) > 1:
                        distribution_str.append(f"Team{team_idx+1}({len(members_in_team)})")
                    else:
                        distribution_str.append(f"Team{team_idx+1}")
                
                print(f"          {group_name}: {' '.join(distribution_str)}")
            print()
    
    print("-" * 60)
    print(f"Summary:")
    print(f"  Total runs: {num_runs}")
    print(f"  Perfect runs (0 conflicts): {sum(1 for c in conflict_counts if c == 0)}")
    print(f"  Runs with conflicts: {sum(1 for c in conflict_counts if c > 0)}")
    print(f"  Average conflicts: {sum(conflict_counts) / len(conflict_counts):.2f}")
    print(f"  Min conflicts: {min(conflict_counts)}")
    print(f"  Max conflicts: {max(conflict_counts)}")

if __name__ == "__main__":
    test_consistency(20)