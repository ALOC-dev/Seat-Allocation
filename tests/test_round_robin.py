"""
라운드 로빈 분배 패턴 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import *

def test_round_robin_distribution():
    """라운드 로빈 방식의 균등 분배 테스트"""
    
    print("🔄 라운드 로빈 분배 테스트")
    print("=" * 50)
    
    # 큰 그룹을 만들어서 테스트 (9명 그룹)
    test_members = [f"사람{i}" for i in range(1, 24)]  # 23명
    test_groups = {
        "큰그룹": [f"사람{i}" for i in range(1, 10)]  # 9명 그룹
    }
    
    group_sizes = calculate_group_sizes(len(test_members))
    print(f"📊 모둠 구성: {group_sizes}")
    print(f"🏷️  큰그룹 9명을 {len(group_sizes)}개 모둠에 분배")
    
    # 여러 번 테스트해서 분배 패턴 확인
    print("\n🎲 5회 테스트:")
    
    for i in range(5):
        teams = allocate_seats_with_groups(test_members, group_sizes, test_groups)
        
        # 큰그룹 멤버들의 분배 확인
        big_group_distribution = [0, 0, 0, 0]  # 4개 모둠
        
        for team_idx, team in enumerate(teams):
            count = 0
            for member in team:
                if member in test_groups["큰그룹"]:
                    count += 1
            big_group_distribution[team_idx] = count
        
        conflicts = calculate_group_conflicts(test_groups, teams)
        print(f"  시도 {i+1}: {big_group_distribution} (충돌: {conflicts}개)")
    
    print(f"\n✅ 이론적 최적 분배: [3, 2, 2, 2] 또는 [2, 3, 2, 2] 등")
    print(f"🎯 모든 분배가 균등한지 확인!")

def test_real_data_distribution():
    """실제 데이터에서 모든 그룹의 분배 패턴 확인"""
    
    print("\n" + "=" * 50)
    print("🔍 실제 데이터 그룹 분배 분석")
    
    members = load_members()
    groups = load_groups() 
    group_sizes = calculate_group_sizes(len(members))
    
    print(f"📊 모둠 구성: {group_sizes}")
    print("그룹들:")
    for group_name, group_members in groups.items():
        print(f"  - {group_name}: {len(group_members)}명")
    
    print(f"\n📋 5회 테스트 - 모든 그룹 분배 패턴:")
    
    for i in range(5):
        teams = allocate_seats_with_groups(members, group_sizes, groups)
        conflicts = calculate_group_conflicts(groups, teams)
        
        print(f"\n  === 시도 {i+1} (총 충돌: {conflicts}개) ===")
        
        for group_name, group_members in groups.items():
            distribution = [0, 0, 0, 0]
            for team_idx, team in enumerate(teams):
                count = sum(1 for member in team if member in group_members)
                distribution[team_idx] = count
            
            # 이론적 최적 분배 계산
            n = len(group_members)
            m = len(group_sizes)
            base = n // m
            extra = n % m
            optimal = [base + 1] * extra + [base] * (m - extra)
            optimal.sort(reverse=True)
            
            print(f"    {group_name}: {distribution} (최적: {optimal})")

if __name__ == "__main__":
    test_round_robin_distribution()
    test_real_data_distribution()