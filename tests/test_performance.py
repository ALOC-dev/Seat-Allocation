"""
성능 비교 테스트
"""
import sys
import os
import time
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import *

def old_algorithm_simulation(members, group_sizes, groups, max_attempts=1000):
    """기존 1000번 시도 알고리즘 시뮬레이션"""
    best_assignment = None
    min_conflicts = float('inf')
    
    for attempt in range(max_attempts):
        shuffled_members = members.copy()
        random.shuffle(shuffled_members)
        
        teams = []
        start_idx = 0
        
        for size in group_sizes:
            team = shuffled_members[start_idx:start_idx + size]
            teams.append(team)
            start_idx += size
        
        conflicts = calculate_group_conflicts(groups, teams)
        
        if conflicts < min_conflicts:
            min_conflicts = conflicts
            best_assignment = teams
            
            if conflicts == 0:
                break
    
    return best_assignment

def test_performance_comparison():
    """기존 알고리즘과 새로운 그리디 알고리즘의 성능과 결과 비교"""
    
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    print("🏁 알고리즘 성능 비교")
    print("=" * 60)
    print(f"📊 테스트 조건: {len(members)}명, {len(groups)}개 그룹, {len(group_sizes)}개 모둠")
    print(f"📋 모둠 구성: {group_sizes}")
    
    # 기존 알고리즘 (1000번 시도) 테스트
    print("\n🔄 기존 알고리즘 (1000번 랜덤 시도):")
    
    start_time = time.time()
    old_result = old_algorithm_simulation(members, group_sizes, groups)
    old_time = time.time() - start_time
    old_conflicts = calculate_group_conflicts(groups, old_result)
    
    print(f"   ⏱️  실행 시간: {old_time:.4f}초")
    print(f"   ⚠️  충돌 수: {old_conflicts}개")
    
    # 새로운 그리디 알고리즘 테스트
    print("\n🎯 새로운 그리디 알고리즘:")
    
    start_time = time.time()
    new_result = allocate_seats_with_groups(members, group_sizes, groups)
    new_time = time.time() - start_time
    new_conflicts = calculate_group_conflicts(groups, new_result)
    
    print(f"   ⏱️  실행 시간: {new_time:.4f}초")
    print(f"   ⚠️  충돌 수: {new_conflicts}개")
    
    # 성능 비교
    print("\n📈 성능 비교:")
    speedup = old_time / new_time if new_time > 0 else float('inf')
    print(f"   🚀 속도 향상: {speedup:.1f}배 빠름")
    print(f"   🎯 품질: 기존 {old_conflicts}개 vs 새로운 {new_conflicts}개 충돌")

def test_consistency():
    """일관성 테스트"""
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    print("\n🔄 일관성 테스트 (10회):")
    conflict_counts = []
    times = []
    
    for i in range(10):
        start_time = time.time()
        result = allocate_seats_with_groups(members, group_sizes, groups)
        exec_time = time.time() - start_time
        conflicts = calculate_group_conflicts(groups, result)
        
        conflict_counts.append(conflicts)
        times.append(exec_time)
        print(f"   시도 {i+1}: {conflicts}개 충돌, {exec_time:.4f}초")
    
    avg_conflicts = sum(conflict_counts) / len(conflict_counts)
    avg_time = sum(times) / len(times)
    
    print(f"\n📊 평균 결과:")
    print(f"   평균 충돌: {avg_conflicts:.1f}개")
    print(f"   평균 시간: {avg_time:.4f}초")

if __name__ == "__main__":
    test_performance_comparison()
    test_consistency()