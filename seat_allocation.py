import random
import math
from collections import defaultdict

def load_members(filename="members.txt"):
    """멤버 파일에서 이름 목록을 읽어온다."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            members = [line.strip() for line in file if line.strip()]
        return members
    except FileNotFoundError:
        print(f"파일 '{filename}'을 찾을 수 없습니다.")
        return []

def calculate_group_sizes(total_members, max_per_group=6):
    """총 인원에 따라 모둠별 인원수를 계산한다."""
    if total_members <= 0:
        return []
    
    # n명이 6이하면 모둠은 1개
    if total_members <= max_per_group:
        return [total_members]
    
    # 모둠당 평균 6명이 넘지 않는 최소한의 모둠 수 찾기
    num_groups = 1
    while total_members / num_groups > max_per_group:
        num_groups += 1
    
    # 평균 인원수 계산
    avg_per_group = total_members / num_groups
    
    # 평균이 정수면 모든 모둠이 같은 크기
    if avg_per_group.is_integer():
        return [int(avg_per_group)] * num_groups
    
    # 평균이 정수가 아니면 floor와 ceil 값으로 구성
    floor_size = int(avg_per_group)  # 내림
    ceil_size = floor_size + 1       # 올림
    
    # ceil_size인 모둠 수 계산
    num_ceil_groups = total_members - (floor_size * num_groups)
    num_floor_groups = num_groups - num_ceil_groups
    
    # 결과 배열 생성 (큰 수부터 배치)
    result = [ceil_size] * num_ceil_groups + [floor_size] * num_floor_groups
    
    return result

def load_groups(filename="groups.txt"):
    """그룹 파일에서 그룹 정보를 읽어온다."""
    groups = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if ':' in line:
                    group_name, members_str = line.split(':', 1)
                    members = [m.strip() for m in members_str.split(',') if m.strip()]
                    groups[group_name.strip()] = members
        return groups
    except FileNotFoundError:
        print(f"그룹 파일 '{filename}'을 찾을 수 없습니다. 그룹 제약 조건 없이 진행합니다.")
        return {}

def calculate_group_conflicts(groups, team_assignment):
    """그룹 제약 조건 위반 수를 계산한다."""
    conflicts = 0
    
    for group_name, group_members in groups.items():
        # 각 팀별로 이 그룹의 멤버가 몇 명씩 있는지 계산
        team_counts = defaultdict(int)
        for member in group_members:
            for team_idx, team in enumerate(team_assignment):
                if member in team:
                    team_counts[team_idx] += 1
                    break
        
        # 같은 팀에 2명 이상 있으면 위반
        for count in team_counts.values():
            if count > 1:
                conflicts += count - 1  # n명이 같은 팀에 있으면 n-1개의 위반
    
    return conflicts

def find_member_groups(member, groups):
    """멤버가 속한 모든 그룹을 찾는다."""
    member_groups = []
    for group_name, group_members in groups.items():
        if member in group_members:
            member_groups.append(group_name)
    return member_groups

def count_same_group_members(member, team, groups):
    """해당 팀에 있는 같은 그룹 멤버 수를 센다."""
    if not team:
        return 0
    
    member_groups = find_member_groups(member, groups)
    if not member_groups:
        return 0
    
    count = 0
    for team_member in team:
        team_member_groups = find_member_groups(team_member, groups)
        # 공통 그룹이 있으면 같은 그룹
        if any(group in member_groups for group in team_member_groups):
            count += 1
    
    return count

def allocate_seats_with_groups(members, group_sizes, groups=None):
    """그룹 제약 조건을 고려하여 멤버들을 그리디 + 라운드로빈으로 배치한다."""
    if not groups:
        return allocate_seats(members, group_sizes)
    
    # 그룹 기반 섞기: 그룹별로 연속 배치하여 라운드로빈 효과 극대화
    # 1. 그룹 순서를 랜덤하게 섞기
    group_names = list(groups.keys())
    random.shuffle(group_names)
    
    # 2. 각 그룹 내에서 멤버들을 섞고, 그룹 순서대로 연속 배치
    shuffled_members = []
    
    # 그룹에 속한 멤버들을 그룹별로 연속 배치
    added_members = set()  # 이미 추가된 멤버 추적
    
    for group_name in group_names:
        group_members = groups[group_name].copy()
        random.shuffle(group_members)
        # 중복 제거하며 추가
        for member in group_members:
            if member not in added_members:
                shuffled_members.append(member)
                added_members.add(member)
    
    # 그룹에 속하지 않은 멤버들을 마지막에 추가
    ungrouped_members = []
    for member in members:
        if member not in added_members:  # 아직 추가되지 않은 멤버만
            ungrouped_members.append(member)
    random.shuffle(ungrouped_members)
    shuffled_members.extend(ungrouped_members)
    
    
    # 팀 초기화
    teams = [[] for _ in group_sizes]
    
    # 라운드로빈 시작 지점 초기화 (0모둠부터 시작)
    round_robin_start = 0
    
    for member in shuffled_members:
        placed = False

        for lap in range(len(shuffled_members)):
            for i in range(len(group_sizes)):
                team = (round_robin_start + i) % len(group_sizes)
                
                # 팀 용량 체크
                if len(teams[team]) >= group_sizes[team]:
                    continue
                
                count = count_same_group_members(member, teams[team], groups)
                
                if count <= lap:
                    teams[team].append(member)
                    # 다음 사람은 다음 팀부터 시작
                    round_robin_start = (team + 1) % len(group_sizes)
                    placed = True
                    break

            if placed:
                break



    
    # # 라운드로빈 시작 위치를 회전시키기 위한 변수
    # round_robin_start = 0
    # 
    # # 각 멤버를 배치
    # for member_idx, member in enumerate(shuffled_members):
    #     placed = False
    #     
    #     # 이번 멤버의 라운드로빈 시작 위치 계산 (매번 회전)
    #     start_team = (round_robin_start + member_idx) % len(teams)
    #     
    #     # 라운드별 시도 (0라운드: 충돌 0개 허용, 1라운드: 1개 허용, ...)
    #     for allowed_conflicts in range(len(teams)):
    #         
    #         # 시작 팀부터 라운드로빈으로 모든 팀 시도
    #         for team_offset in range(len(teams)):
    #             team_idx = (start_team + team_offset) % len(teams)
    #             
    #             # 팀 용량 초과 체크
    #             if len(teams[team_idx]) >= group_sizes[team_idx]:
    #                 continue
    #             
    #             # 충돌 계산
    #             conflicts = count_same_group_members(member, teams[team_idx], groups)
    #             
    #             # 허용 범위 내면 배치
    #             if conflicts <= allowed_conflicts:
    #                 teams[team_idx].append(member)
    #                 placed = True
    #                 break
    #         
    #         if placed:
    #             break
    #     
    #     # 배치 실패시 강제 배치 (이론적으로 발생하지 않아야 함)
    #     if not placed:
    #         for team_idx, team in enumerate(teams):
    #             if len(team) < group_sizes[team_idx]:
    #                 teams[team_idx].append(member)
    #                 break
    
    return teams

def allocate_seats(members, group_sizes):
    """멤버들을 모둠에 랜덤하게 배치한다."""
    shuffled_members = members.copy()
    random.shuffle(shuffled_members)
    
    groups = []
    start_idx = 0
    
    for size in group_sizes:
        group = shuffled_members[start_idx:start_idx + size]
        groups.append(group)
        start_idx += size
    
    return groups

def print_allocation(teams, groups=None):
    """배치 결과를 출력한다."""
    print("=" * 50)
    print("🪑 동아리 자리 배치 결과 🪑")
    print("=" * 50)
    
    for i, team in enumerate(teams, 1):
        print(f"\n📋 {i}모둠 ({len(team)}명):")
        for j, member in enumerate(team, 1):
            print(f"  {j}. {member}")
    
    print(f"\n✅ 총 {len(teams)}개 모둠, 총 인원: {sum(len(team) for team in teams)}명")
    
    # 그룹 제약 조건 위반 분석
    if groups:
        conflicts = calculate_group_conflicts(groups, teams)
        if conflicts == 0:
            print("🎉 모든 그룹 제약 조건이 완벽히 지켜졌습니다!")
        else:
            print(f"⚠️  그룹 제약 조건 위반: {conflicts}개")
            
        # 위반 상세 분석
        print("\n📊 그룹별 배치 현황:")
        for group_name, group_members in groups.items():
            team_distribution = defaultdict(list)
            for member in group_members:
                for team_idx, team in enumerate(teams):
                    if member in team:
                        team_distribution[team_idx + 1].append(member)
                        break
            
            print(f"  🏷️  {group_name}: ", end="")
            for team_num, members in team_distribution.items():
                if len(members) > 1:
                    print(f"{team_num}모둠({len(members)}명) ", end="")
                else:
                    print(f"{team_num}모둠 ", end="")
            print()
    
    print("=" * 50)

def main():
    print("🎯 동아리 자리배치 프로그램")
    print("-" * 30)
    
    # 멤버 로드
    members = load_members()
    if not members:
        return
    
    print(f"📝 총 {len(members)}명의 멤버를 불러왔습니다.")
    
    # 그룹 로드
    groups = load_groups()
    if groups:
        print(f"🏷️  {len(groups)}개 그룹을 불러왔습니다:")
        for group_name, group_members in groups.items():
            print(f"   - {group_name}: {len(group_members)}명")
    
    # 모둠 크기 계산
    group_sizes = calculate_group_sizes(len(members))
    print(f"📊 모둠 구성: {group_sizes}")
    
    # 자리 배치 (그룹 제약 조건 고려)
    teams = allocate_seats_with_groups(members, group_sizes, groups)
    
    # 결과 출력
    print_allocation(teams, groups)
    
    # 다시 섞기 옵션
    while True:
        retry = input("\n🔄 다시 섞으시겠습니까? (y/n): ").lower()
        if retry == 'y':
            teams = allocate_seats_with_groups(members, group_sizes, groups)
            print_allocation(teams, groups)
        elif retry == 'n':
            print("👋 프로그램을 종료합니다.")
            break
        else:
            print("y 또는 n을 입력해주세요.")

if __name__ == "__main__":
    main()