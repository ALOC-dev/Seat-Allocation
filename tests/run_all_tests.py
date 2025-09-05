#!/usr/bin/env python3
"""
모든 테스트를 실행하는 통합 스크립트
"""
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """모든 테스트를 순서대로 실행"""
    
    print("🚀 자리배치 프로그램 전체 테스트 실행")
    print("=" * 80)
    
    test_modules = [
        ("test_basic_allocation", "기본 자리배치 알고리즘 테스트"),
        ("test_randomness", "랜덤성 테스트"), 
        ("test_group_constraints", "그룹 제약 조건 테스트"),
        ("test_performance", "성능 비교 테스트"),
        ("test_round_robin", "라운드 로빈 분배 테스트"),
        ("test_debug", "디버깅 및 상세 분석")
    ]
    
    for i, (module_name, description) in enumerate(test_modules, 1):
        print(f"\n{'='*20} {i}/{len(test_modules)}: {description} {'='*20}")
        
        try:
            module = __import__(module_name)
            # 각 모듈의 main 함수 실행
            if hasattr(module, '__main__'):
                exec(open(f"{module_name}.py").read())
            print(f"✅ {description} 완료")
        except Exception as e:
            print(f"❌ {description} 실패: {e}")
        
        if i < len(test_modules):
            input("\n⏸️  다음 테스트로 진행하려면 Enter를 누르세요...")
    
    print(f"\n🎉 모든 테스트가 완료되었습니다!")

if __name__ == "__main__":
    run_all_tests()