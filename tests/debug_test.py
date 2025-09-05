#!/usr/bin/env python3
"""
간단한 디버그 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import (
    load_members, load_groups, calculate_group_sizes,
    allocate_seats_with_groups, calculate_group_conflicts
)
import random

def run_debug_test():
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    print(f"=== 디버그 테스트 ===")
    print(f"멤버 수: {len(members)}")
    print(f"그룹: {groups}")
    print(f"팀 크기: {group_sizes}")
    print(f"멤버들: {members}")
    
    # 고정 시드로 테스트
    random.seed(0)
    
    teams = allocate_seats_with_groups(members, group_sizes, groups)
    conflicts = calculate_group_conflicts(groups, teams)
    
    print(f"\n=== 최종 결과 ===")
    for i, team in enumerate(teams):
        print(f"팀 {i}: {team}")
    
    print(f"\n총 충돌: {conflicts}")

if __name__ == "__main__":
    run_debug_test()