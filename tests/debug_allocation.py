#!/usr/bin/env python3
"""
Debug version of the allocation algorithm to trace exact execution
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import (
    load_members, load_groups, calculate_group_sizes,
    find_member_groups, count_same_group_members
)
import random

def debug_allocate_seats_with_groups(members, group_sizes, groups=None):
    """Debug version with detailed tracing"""
    if not groups:
        return allocate_seats(members, group_sizes)
    
    # 랜덤으로 섞기
    shuffled_members = members.copy()
    random.shuffle(shuffled_members)
    
    print(f"Shuffled order: {shuffled_members}")
    print(f"Team sizes: {group_sizes}")
    print("-" * 80)
    
    # 팀 초기화
    teams = [[] for _ in group_sizes]
    team_capacities = group_sizes.copy()
    
    # 각 멤버를 순서대로 배치
    last_placed_team = -1
    
    for member_idx, member in enumerate(shuffled_members):
        print(f"\n=== Placing member {member_idx+1}: {member} ===")
        member_groups = find_member_groups(member, groups)
        print(f"Member groups: {member_groups}")
        
        placed = False
        
        # 이전 사람이 배치된 다음 팀부터 시작
        start_team_idx = (last_placed_team + 1) % len(teams)
        print(f"Starting from team {start_team_idx} (last_placed_team: {last_placed_team})")
        
        # 빈 자리가 있는 팀을 찾을 때까지 순환
        attempts = 0
        while team_capacities[start_team_idx] == 0 and attempts < len(teams):
            start_team_idx = (start_team_idx + 1) % len(teams)
            attempts += 1
        
        max_rounds = len(shuffled_members)
        
        for round_num in range(max_rounds):
            allowed_same_group = round_num
            print(f"  Round {round_num}: allowing up to {allowed_same_group} same-group members")
            
            # 현재 팀부터 한 바퀴 돌기
            for i in range(len(teams)):
                team_idx = (start_team_idx + i) % len(teams)
                
                # 팀이 꽉 찬 경우 건너뛰기
                if team_capacities[team_idx] == 0:
                    print(f"    Team {team_idx}: FULL (capacity: 0)")
                    continue
                
                # 같은 그룹 멤버 수 확인
                same_group_count = count_same_group_members(member, teams[team_idx], groups)
                
                print(f"    Team {team_idx}: has {same_group_count} same-group members, capacity: {team_capacities[team_idx]}")
                print(f"      Current team: {teams[team_idx]}")
                
                if same_group_count <= allowed_same_group:
                    # 배치 가능!
                    print(f"    ✅ PLACED in Team {team_idx}!")
                    teams[team_idx].append(member)
                    team_capacities[team_idx] -= 1
                    last_placed_team = team_idx
                    placed = True
                    break
                else:
                    print(f"    ❌ Cannot place: {same_group_count} > {allowed_same_group}")
            
            if placed:
                break
        
        # 정말 배치할 곳이 없으면
        if not placed:
            print(f"  🚨 FALLBACK: placing in first available team")
            for i, capacity in enumerate(team_capacities):
                if capacity > 0:
                    teams[i].append(member)
                    team_capacities[i] -= 1
                    last_placed_team = i
                    break
        
        # 현재 상태 출력
        print(f"  Current state:")
        for i, team in enumerate(teams):
            print(f"    Team {i}: {team} (capacity: {team_capacities[i]})")
    
    return teams

def run_debug_test():
    """Run one debug allocation"""
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    # Set a different random seed to reproduce failing case
    random.seed(123)
    
    print("=== DEBUG ALLOCATION TEST ===")
    teams = debug_allocate_seats_with_groups(members, group_sizes, groups)
    
    print("\n=== FINAL RESULT ===")
    for i, team in enumerate(teams):
        print(f"Team {i+1}: {team}")
    
    # Check conflicts
    from seat_allocation import calculate_group_conflicts
    conflicts = calculate_group_conflicts(groups, teams)
    print(f"\nTotal conflicts: {conflicts}")

if __name__ == "__main__":
    run_debug_test()