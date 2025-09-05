import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import load_members, calculate_group_sizes, allocate_seats, print_allocation

# 간단한 한 번 실행용 스크립트
members = load_members()
group_sizes = calculate_group_sizes(len(members))
groups = allocate_seats(members, group_sizes)
print_allocation(groups)