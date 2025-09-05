"""
랜덤성 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import load_members, calculate_group_sizes, allocate_seats
from collections import defaultdict

def test_randomness(iterations=10):
    """랜덤성을 테스트한다."""
    members = load_members()
    group_sizes = calculate_group_sizes(len(members))
    
    print(f"🎲 랜덤성 테스트 ({iterations}회 실행)")
    print("=" * 50)
    
    # 각 사람이 각 모둠에 배치된 횟수 추적
    person_group_count = defaultdict(lambda: defaultdict(int))
    
    for i in range(iterations):
        groups = allocate_seats(members, group_sizes)
        
        print(f"\n🔄 {i+1}회차:")
        for group_idx, group in enumerate(groups, 1):
            print(f"  {group_idx}모둠: {group[:3]}..." if len(group) > 3 else f"  {group_idx}모둠: {group}")
            
            # 통계 수집
            for person in group:
                person_group_count[person][group_idx] += 1
    
    # 랜덤성 분석
    print(f"\n📊 랜덤성 분석 (총 {iterations}회):")
    print("-" * 50)
    
    for person in members[:5]:  # 처음 5명만 분석
        counts = [person_group_count[person][i] for i in range(1, len(group_sizes) + 1)]
        print(f"{person}: {counts} (표준편차: {std_dev(counts):.2f})")

def std_dev(numbers):
    """표준편차 계산"""
    if not numbers:
        return 0
    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / len(numbers)
    return variance ** 0.5

if __name__ == "__main__":
    test_randomness(5)