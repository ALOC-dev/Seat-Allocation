"""
디버깅 및 상세 분석 테스트
"""
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seat_allocation import *

def debug_simple_case():
    """간단한 케이스에서 배치 과정 상세 분석"""
    
    print("🔍 간단한 케이스 디버깅")
    print("=" * 50)
    
    # 간단한 테스트 케이스 생성
    members = ["김정훈", "배인수", "송희영", "이도권", "기타1", "기타2", "기타3"]  # 7명
    groups = {
        "스터디그룹": ["김정훈", "배인수", "송희영", "이도권"]  # 4명
    }
    group_sizes = [2, 2, 2, 1]  # 4개 모둠
    
    print(f"멤버: {members}")
    print(f"그룹: {groups}")
    print(f"모둠 구성: {group_sizes}")
    
    # 알고리즘 실행하면서 추적
    shuffled_members = members.copy()
    random.seed(42)  # 재현 가능한 결과를 위해
    random.shuffle(shuffled_members)
    
    print(f"\n섞인 순서: {shuffled_members}")
    
    teams = [[] for _ in group_sizes]
    team_capacities = group_sizes.copy()
    last_placed_team = -1
    
    print(f"\n📋 배치 과정:")
    
    for i, member in enumerate(shuffled_members):
        print(f"\n{i+1}. '{member}' 배치:")
        
        # 스터디그룹 멤버인지 확인
        is_study_member = member in groups["스터디그룹"]
        print(f"   스터디그룹: {is_study_member}")
        
        if is_study_member:
            # 현재 각 모둠의 스터디그룹 멤버 수 확인
            study_counts = []
            for team in teams:
                count = sum(1 for m in team if m in groups["스터디그룹"])
                study_counts.append(count)
            print(f"   현재 분배: {study_counts}")
        
        start_team_idx = (last_placed_team + 1) % len(teams)
        attempts = 0
        while team_capacities[start_team_idx] == 0 and attempts < len(teams):
            start_team_idx = (start_team_idx + 1) % len(teams)
            attempts += 1
        
        print(f"   시작 모둠: {start_team_idx}")
        print(f"   모둠 여유: {team_capacities}")
        
        # 실제 배치
        placed = False
        max_rounds = max(len(group_members) for group_members in groups.values())
        
        for round_num in range(max_rounds):
            allowed_same_group = round_num
            print(f"   {round_num}바퀴: 허용={allowed_same_group}")
            
            for j in range(len(teams)):
                team_idx = (start_team_idx + j) % len(teams)
                
                if team_capacities[team_idx] == 0:
                    continue
                
                same_group_count = count_same_group_members(member, teams[team_idx], groups)
                print(f"     모둠{team_idx}: 같은그룹={same_group_count}")
                
                if same_group_count <= allowed_same_group:
                    teams[team_idx].append(member)
                    team_capacities[team_idx] -= 1
                    last_placed_team = team_idx
                    print(f"     ✅ 모둠{team_idx}에 배치!")
                    placed = True
                    break
            
            if placed:
                break
        
        print(f"   결과: {[len(team) for team in teams]}")
    
    print(f"\n🎯 최종 결과:")
    for i, team in enumerate(teams):
        study_count = sum(1 for m in team if m in groups["스터디그룹"])
        print(f"   모둠{i}: {team} (스터디그룹: {study_count}명)")
    
    conflicts = calculate_group_conflicts(groups, teams)
    print(f"\n충돌 수: {conflicts}개")

def debug_real_data():
    """실제 데이터에서 특정 그룹 분배 과정 분석"""
    
    print("\n" + "=" * 50)
    print("🔍 실제 데이터 분석")
    
    members = load_members()
    groups = load_groups()
    group_sizes = calculate_group_sizes(len(members))
    
    print(f"전체 멤버: {len(members)}명")
    print(f"모둠 구성: {group_sizes}")
    
    # 3회 테스트해서 일관성 확인
    print(f"\n📊 3회 테스트:")
    
    for i in range(3):
        teams = allocate_seats_with_groups(members, group_sizes, groups)
        conflicts = calculate_group_conflicts(groups, teams)
        
        print(f"\n시도 {i+1} (충돌: {conflicts}개):")
        for group_name, group_members in groups.items():
            distribution = [0, 0, 0, 0]
            for team_idx, team in enumerate(teams):
                count = sum(1 for member in team if member in group_members)
                distribution[team_idx] = count
            print(f"  {group_name}: {distribution}")

if __name__ == "__main__":
    debug_simple_case()
    debug_real_data()