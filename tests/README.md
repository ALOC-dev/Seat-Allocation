# 테스트 패키지

자리배치 프로그램의 다양한 테스트를 포함합니다.

## 📁 테스트 파일 구성

### 🔧 `test_basic_allocation.py`
- **목적**: 기본 자리배치 알고리즘 테스트
- **내용**: 
  - 다양한 인원수별 모둠 구성 테스트
  - 실제 멤버 데이터로 배치 테스트
- **실행**: `python test_basic_allocation.py`

### 🎲 `test_randomness.py`
- **목적**: 랜덤 배치의 균등성 검증
- **내용**:
  - 여러 번 실행 시 각 사람의 모둠 분포 분석
  - 표준편차를 통한 랜덤성 정량 측정
- **실행**: `python test_randomness.py`

### 🏷️ `test_group_constraints.py`
- **목적**: 그룹 제약 조건 기능 테스트
- **내용**:
  - 그룹 제약 조건 유/무 비교
  - 최적화 성능 측정
  - 충돌 수 분석
- **실행**: `python test_group_constraints.py`

### ⚡ `test_performance.py`
- **목적**: 알고리즘 성능 비교
- **내용**:
  - 기존 1000번 시도 vs 새로운 그리디 알고리즘
  - 실행 시간 및 품질 비교
  - 일관성 테스트
- **실행**: `python test_performance.py`

### 🔄 `test_round_robin.py`  
- **목적**: 라운드 로빈 분배 패턴 검증
- **내용**:
  - 큰 그룹의 균등 분배 확인
  - 실제 데이터에서 모든 그룹의 분배 패턴 분석
  - 이론적 최적 분배와 비교
- **실행**: `python test_round_robin.py`

### 🔍 `test_debug.py`
- **목적**: 디버깅 및 상세 분석
- **내용**:
  - 간단한 케이스의 배치 과정 추적
  - 실제 데이터에서 그룹별 분배 상세 분석
  - 알고리즘 동작 검증
- **실행**: `python test_debug.py`

## 🚀 전체 테스트 실행

### 통합 실행
```bash
python tests/run_all_tests.py
```

### 개별 실행
```bash
cd tests
python test_basic_allocation.py
python test_randomness.py
python test_group_constraints.py
python test_performance.py  
python test_round_robin.py
python test_debug.py
```

## 📊 테스트 결과 해석

### ✅ **성공적인 결과**
- **기본 배치**: 모든 인원이 올바른 모둠 수에 배치
- **랜덤성**: 표준편차가 낮고 고른 분포
- **그룹 제약**: 충돌 수가 0 또는 최소값
- **성능**: 기존 대비 10배 이상 빠른 속도
- **라운드 로빈**: [3,2,2,2] 같은 균등한 분배

### ⚠️ **문제 신호**
- **충돌 수 급증**: 그룹 제약 조건 위반 다수 발생
- **편향된 분배**: [4,1,1,1] 같은 불균등한 분배
- **성능 저하**: 예상보다 느린 실행 시간

## 🛠️ 새로운 테스트 추가

새로운 테스트를 추가할 때는:

1. `test_*.py` 형식으로 파일명 작성
2. 상단에 경로 추가 코드 포함:
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```
3. `run_all_tests.py`에 새 테스트 모듈 추가