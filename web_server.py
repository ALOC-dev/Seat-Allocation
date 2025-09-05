"""
웹 서버 및 API 엔드포인트
Flask를 사용한 백엔드 서버
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import time
from seat_allocation import (
    load_members, load_groups, calculate_group_sizes,
    allocate_seats_with_groups, calculate_group_conflicts
)

app = Flask(__name__)
CORS(app)  # CORS 허용

# 서버 시작 시간 기록
SERVER_START_TIME = str(int(time.time() * 1000))

# 정적 파일 경로
WEB_UI_PATH = os.path.join(os.path.dirname(__file__), 'web_ui')

@app.route('/')
def serve_index():
    """메인 페이지 서빙"""
    return send_from_directory(WEB_UI_PATH, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """정적 파일 서빙"""
    return send_from_directory(WEB_UI_PATH, filename)

@app.route('/api/members', methods=['GET'])
def get_members():
    """멤버 목록 조회"""
    try:
        members = load_members()
        return jsonify({
            'success': True,
            'members': members,
            'count': len(members)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/members', methods=['POST'])
def update_members():
    """멤버 목록 업데이트"""
    try:
        data = request.json
        members = data.get('members', [])
        
        # 멤버 파일 업데이트
        with open('members.txt', 'w', encoding='utf-8') as f:
            for member in members:
                f.write(f"{member.strip()}\n")
        
        return jsonify({
            'success': True,
            'members': members,
            'count': len(members)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """그룹 정보 조회"""
    try:
        groups = load_groups()
        return jsonify({
            'success': True,
            'groups': groups,
            'count': len(groups)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/groups', methods=['POST'])
def update_groups():
    """그룹 정보 업데이트"""
    try:
        data = request.json
        groups = data.get('groups', {})
        
        # 그룹 파일 업데이트
        with open('groups.txt', 'w', encoding='utf-8') as f:
            f.write("# 그룹 설정 파일\n")
            f.write("# 같은 그룹의 멤버들은 가능한 한 다른 모둠에 배치됩니다.\n")
            f.write("# 형식: 각 줄에 그룹명:멤버1,멤버2,멤버3 형식으로 작성\n")
            f.write("# '#'으로 시작하는 줄은 주석입니다.\n\n")
            
            for group_name, group_members in groups.items():
                if group_members:
                    f.write(f"{group_name}:{','.join(group_members)}\n")
        
        return jsonify({
            'success': True,
            'groups': groups,
            'count': len(groups)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/allocate', methods=['POST'])
def allocate_seats():
    """자리 배치 실행"""
    try:
        data = request.json
        members = data.get('members')
        groups = data.get('groups', {})
        
        # 데이터가 없으면 파일에서 로드
        if not members:
            members = load_members()
        if not groups:
            groups = load_groups()
        
        if not members:
            return jsonify({
                'success': False,
                'error': '멤버가 없습니다.'
            }), 400
        
        # 모둠 크기 계산
        group_sizes = calculate_group_sizes(len(members))
        
        # 자리 배치
        teams = allocate_seats_with_groups(members, group_sizes, groups)
        
        # 충돌 계산
        conflicts = calculate_group_conflicts(groups, teams)
        
        # 그룹별 분배 정보 계산
        group_distributions = {}
        for group_name, group_members in groups.items():
            distribution = [0] * len(teams)
            for member in group_members:
                for team_idx, team in enumerate(teams):
                    if member in team:
                        distribution[team_idx] += 1
                        break
            group_distributions[group_name] = distribution
        
        return jsonify({
            'success': True,
            'teams': teams,
            'group_sizes': group_sizes,
            'conflicts': conflicts,
            'group_distributions': group_distributions,
            'stats': {
                'total_members': len(members),
                'total_teams': len(teams),
                'group_constraints': len(groups),
                'conflict_count': conflicts
            }
        })
        
    except Exception as e:
        import traceback
        print(f"자리 배치 오류: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_algorithm():
    """알고리즘 테스트"""
    try:
        # 테스트 데이터
        test_members = [f"사람{i}" for i in range(1, 24)]
        test_groups = {
            "그룹A": ["사람1", "사람2", "사람3"],
            "그룹B": ["사람4", "사람5", "사람6"],
            "그룹C": ["사람7", "사람8", "사람9", "사람10"]
        }
        
        group_sizes = calculate_group_sizes(len(test_members))
        teams = allocate_seats_with_groups(test_members, group_sizes, test_groups)
        conflicts = calculate_group_conflicts(test_groups, teams)
        
        return jsonify({
            'success': True,
            'test_result': {
                'members_count': len(test_members),
                'teams': teams,
                'group_sizes': group_sizes,
                'conflicts': conflicts,
                'groups': test_groups
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    response = jsonify({
        'success': True,
        'message': 'Smart Seat Allocation API Server is running!',
        'version': '1.0.0',
        'server_start_time': SERVER_START_TIME
    })
    response.headers['X-Server-Start-Time'] = SERVER_START_TIME
    return response

if __name__ == '__main__':
    # 사용 가능한 포트 찾기
    import socket
    
    def find_free_port(start_port=8000):
        for port in range(start_port, start_port + 100):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('0.0.0.0', port))  # localhost -> 0.0.0.0으로 변경
                    return port
                except OSError:
                    continue
        return 8000  # fallback
    
    port = find_free_port()
    
    print("🚀 Smart Seat Allocation 웹 서버 시작")
    print(f"📱 브라우저에서 http://localhost:{port} 접속")
    print("🔧 개발자 도구에서 네트워크 탭을 확인하세요")
    print("-" * 50)
    
    # 개발 모드로 실행
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port,
        use_reloader=False  # reloader 비활성화로 포트 충돌 방지
    )