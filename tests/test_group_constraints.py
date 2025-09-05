"""
그룹 제약 조건 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import (
    load_members, load_groups, calculate_group_sizes, 
    allocate_seats_with_groups, allocate_seats, 
    print_allocation, calculate_group_conflicts
)

def test_group_constraints():
    """그룹 제약 조건 기능을 테스트한다."""
    print("🧪 그룹 제약 조건 테스트")
    print("=" * 60)
    
    # 멤버 및 그룹 로드
    members = load_members()
    groups = load_groups()
    
    print(f"📝 총 {len(members)}명의 멤버")
    print(f"🏷️  {len(groups)}개의 그룹:")
    for group_name, group_members in groups.items():
        print(f"   - {group_name}: {group_members}")
    
    # 모둠 크기 계산
    group_sizes = calculate_group_sizes(len(members))
    print(f"\n📊 모둠 구성: {group_sizes}")
    
    # 그룹 제약 조건 없이 배치 (비교용)
    print("\n" + "="*60)
    print("🎲 그룹 제약 조건 없이 랜덤 배치:")
    random_teams = allocate_seats(members, group_sizes)
    print_allocation(random_teams, groups)
    
    # 그룹 제약 조건 고려한 배치
    print("\n" + "="*60)
    print("🎯 그룹 제약 조건을 고려한 배치:")
    optimized_teams = allocate_seats_with_groups(members, group_sizes, groups)
    print_allocation(optimized_teams, groups)

def test_optimization_performance():
    """최적화 성능 테스트"""
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    print("\n" + "="*60)
    print("📈 최적화 성능 테스트 (5회 시도):")
    
    for i in range(5):
        teams = allocate_seats_with_groups(members, group_sizes, groups)
        conflicts = calculate_group_conflicts(groups, teams)
        print(f"  시도 {i+1}: 충돌 {conflicts}개")

if __name__ == "__main__":
    test_group_constraints()
    test_optimization_performance()