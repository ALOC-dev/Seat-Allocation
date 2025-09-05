"""
기본 자리배치 알고리즘 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import calculate_group_sizes, load_members, allocate_seats, print_allocation

def test_different_sizes():
    """다양한 인원수에 대한 모둠 배치를 테스트한다."""
    test_cases = [19, 22, 24, 25, 30, 35]
    
    print("🧪 다양한 인원수별 모둠 배치 테스트")
    print("=" * 60)
    
    for total in test_cases:
        sizes = calculate_group_sizes(total)
        print(f"👥 {total}명 → 모둠 구성: {sizes}")
        print(f"   검증: 총합 = {sum(sizes)}, 모둠수 = {len(sizes)}, 최대차이 = {max(sizes) - min(sizes) if sizes else 0}")
        print()

def test_with_real_members():
    """실제 멤버 데이터로 배치 테스트"""
    print("\n" + "=" * 60)
    print("실제 멤버 데이터로 배치 테스트")
    members = load_members()
    if members:
        group_sizes = calculate_group_sizes(len(members))
        groups = allocate_seats(members, group_sizes)
        print_allocation(groups)

if __name__ == "__main__":
    test_different_sizes()
    test_with_real_members()