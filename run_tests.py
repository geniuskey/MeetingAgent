#!/usr/bin/env python3
"""
run_tests.py - 테스트 실행 스크립트
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """명령어 실행"""
    print(f"\n{'=' * 60}")
    print(f"[실행] {description}")
    print(f"{'=' * 60}")

    try:
        # Windows 인코딩 문제 해결
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        print(result.stdout)
        if result.stderr:
            print(f"[경고/오류]:\n{result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"[실행 실패]: {e}")
        return False


def main():
    """메인 실행 함수"""
    print("[시작] AI 회의 예약 시스템 - 테스트 및 데모 실행")

    # 프로젝트 루트로 이동
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Python 경로 설정
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 1. Mock API 테스트
    success1 = run_command(
        "python tests/api/test_mock_apis.py",
        "Mock API 기능 검증 및 종합 데모"
    )

    # 2. 우선순위 알고리즘 테스트
    success2 = run_command(
        "python tests/services/test_schedule_priority_service.py",
        "일정 우선순위 알고리즘 테스트 및 데모"
    )

    # 3. 결과 요약
    print(f"\n{'=' * 60}")
    print("[결과] 테스트 결과 요약")
    print(f"{'=' * 60}")

    results = [
        ("Mock API 테스트", success1),
        ("우선순위 알고리즘 테스트", success2)
    ]

    for name, success in results:
        status = "[성공]" if success else "[실패]"
        print(f"- {name}: {status}")

    all_success = all(success for _, success in results)

    if all_success:
        print(f"\n[완료] 모든 테스트가 성공적으로 완료되었습니다!")
        print(f"\n[준비사항] 개발 준비 완료:")
        print(f"- Mock API: 30명 임직원, 역할별 분배 완료")
        print(f"- 우선순위 알고리즘: 시간/참석률/임원 가중치 적용")
        print(f"- AI 서비스: 자연어 시간 제안 기능 통합")

        print(f"\n[다음단계]:")
        print(f"1. Streamlit 앱 실행: streamlit run app.py")
        print(f"2. Google API 키 설정: set GOOGLE_API_KEY=your-key")
        print(f"3. AI 어시스턴트에서 시간 제안 테스트")
        print(f"4. 실제 API 연동 준비")

    else:
        print(f"\n[주의] 일부 테스트가 실패했습니다. 로그를 확인해주세요.")

    return 0 if all_success else 1


if __name__ == "__main__":
    exit(main())