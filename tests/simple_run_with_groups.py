import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import load_members, load_groups, calculate_group_sizes, allocate_seats_with_groups, print_allocation

# 그룹 제약 조건을 고려한 간단한 실행 스크립트
members = load_members()
groups = load_groups()
group_sizes = calculate_group_sizes(len(members))

print(f"📝 총 {len(members)}명의 멤버")
if groups:
    print(f"🏷️  {len(groups)}개 그룹 제약 조건 적용")

teams = allocate_seats_with_groups(members, group_sizes, groups)
print_allocation(teams, groups)