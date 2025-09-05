"""
다중 그룹 소속 시나리오에서 라운드 로빈 분배 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import *

def test_multi_group_scenario():
    """한 사람이 여러 그룹에 속하는 경우 테스트"""
    
    print("🔄 다중 그룹 소속 시나리오 테스트")
    print("=" * 60)
    
    # 테스트 케이스: 일부 사람들이 여러 그룹에 소속
    test_members = [f"사람{i}" for i in range(1, 17)]  # 16명
    
    test_groups = {
        "그룹A": ["사람1", "사람2", "사람3", "사람4"],           # 4명
        "그룹B": ["사람3", "사람4", "사람5", "사람6"],           # 4명 (사람3,4 중복)
        "그룹C": ["사람7", "사람8", "사람9"],                    # 3명
        "그룹D": ["사람1", "사람10", "사람11"]                   # 3명 (사람1 중복)
    }
    
    group_sizes = calculate_group_sizes(len(test_members))
    
    print(f"📊 멤버: {len(test_members)}명")
    print(f"📊 모둠 구성: {group_sizes}")
    print(f"🏷️  그룹 구성:")
    for group_name, members in test_groups.items():
        print(f"   - {group_name}: {members}")
    
    # 중복 소속 확인
    print(f"\n🔗 다중 그룹 소속자:")
    all_members_in_groups = []
    for members in test_groups.values():
        all_members_in_groups.extend(members)
    
    from collections import Counter
    member_counts = Counter(all_members_in_groups)
    multi_group_members = {member: count for member, count in member_counts.items() if count > 1}
    
    for member, count in multi_group_members.items():
        member_groups = find_member_groups(member, test_groups)
        print(f"   - {member}: {count}개 그룹 ({member_groups})")
    
    print(f"\n🎲 5회 테스트 결과:")
    
    for i in range(5):
        teams = allocate_seats_with_groups(test_members, group_sizes, test_groups)
        conflicts = calculate_group_conflicts(test_groups, teams)
        
        print(f"\n=== 시도 {i+1} (총 충돌: {conflicts}개) ===")
        
        # 각 그룹별 분배 확인
        for group_name, group_members in test_groups.items():
            distribution = [0, 0, 0, 0]  # 4개 모둠
            for team_idx, team in enumerate(teams):
                count = sum(1 for member in team if member in group_members)
                distribution[team_idx] = count
            
            # 이론적 최적 분배
            n = len(group_members)
            m = len(group_sizes)
            base = n // m
            extra = n % m
            optimal = [base + 1] * extra + [base] * (m - extra)
            optimal.sort(reverse=True)
            
            print(f"  {group_name}: {distribution} (최적: {optimal})")
        
        # 다중 소속자들이 어느 모둠에 배치되었는지 확인
        print(f"  다중소속자 배치:")
        for member in multi_group_members.keys():
            for team_idx, team in enumerate(teams):
                if member in team:
                    print(f"    {member} → {team_idx+1}모둠")
                    break

def test_extreme_overlap():
    """극단적인 중복 상황 테스트"""
    
    print(f"\n" + "=" * 60)
    print("🚨 극단적 중복 시나리오 테스트")
    
    # 모든 사람이 여러 그룹에 속하는 극단적 케이스
    test_members = ["A", "B", "C", "D", "E", "F", "G", "H"]  # 8명
    
    test_groups = {
        "그룹1": ["A", "B", "C", "D"],      # 4명
        "그룹2": ["A", "B", "E", "F"],      # 4명 (A,B 중복)  
        "그룹3": ["C", "D", "G", "H"],      # 4명 (C,D 중복)
        "그룹4": ["E", "F", "G", "H"]       # 4명 (E,F,G,H 중복)
    }
    
    group_sizes = [2, 2, 2, 2]  # 4개 모둠, 각 2명
    
    print(f"📊 멤버: {len(test_members)}명 → {group_sizes}")
    print(f"🏷️  모든 사람이 2개씩 그룹에 소속")
    
    # 1회 테스트
    teams = allocate_seats_with_groups(test_members, group_sizes, test_groups)
    conflicts = calculate_group_conflicts(test_groups, teams)
    
    print(f"\n🎯 결과 (충돌: {conflicts}개):")
    
    for i, team in enumerate(teams):
        print(f"  {i+1}모둠: {team}")
    
    print(f"\n📊 그룹별 분배:")
    for group_name, group_members in test_groups.items():
        distribution = [0, 0, 0, 0]
        for team_idx, team in enumerate(teams):
            count = sum(1 for member in team if member in group_members)
            distribution[team_idx] = count
        print(f"  {group_name}: {distribution}")
    
    # 이론적으로 완벽한 분배가 가능한지 분석
    print(f"\n🤔 분석:")
    print(f"   각 그룹 4명을 4개 모둠에 분배 → 이론적 최적: [1,1,1,1]")
    print(f"   하지만 중복 소속으로 인한 제약으로 완벽한 분배는 불가능할 수 있음")

if __name__ == "__main__":
    test_multi_group_scenario()
    test_extreme_overlap()