#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simple_test.py - 간단한 테스트 실행기 (Windows 호환)
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_basic_functionality():
    """기본 기능 테스트"""
    print("=" * 50)
    print("[테스트] 기본 기능 검증")
    print("=" * 50)

    try:
        # 1. Employee API 테스트
        print("\n[1] Employee API 테스트...")
        from src.api.employee_api import get_employee_api

        emp_api = get_employee_api()
        employees = emp_api.get_all_employees()
        executives = emp_api.get_executives()
        leaders = emp_api.get_leaders()

        print(f"  - 전체 임직원: {len(employees)}명")
        print(f"  - 임원급: {len(executives)}명")
        print(f"  - 리더급: {len(leaders)}명")

        # 역할 분포 확인
        role_counts = {}
        for emp in employees:
            role = emp.role if emp.role else "일반직원"
            role_counts[role] = role_counts.get(role, 0) + 1

        print(f"  - 역할 분포:")
        for role, count in sorted(role_counts.items()):
            print(f"    * {role}: {count}명")

        # 2. Schedule API 테스트
        print(f"\n[2] Schedule API 테스트...")
        from src.api.schedule_api import get_schedule_api

        schedule_api = get_schedule_api()
        schedules = schedule_api.schedules

        print(f"  - 생성된 일정: {len(schedules)}개")

        # 첫 번째 직원의 일정 확인
        if employees:
            first_emp = employees[0]
            from datetime import datetime, timedelta
            now = datetime.now()
            emp_schedules = schedule_api.get_schedules(
                first_emp.id,
                now - timedelta(days=7),
                now + timedelta(days=7)
            )
            print(f"  - {first_emp.name}님 일정: {len(emp_schedules)}개")

        # 3. Priority Service 테스트
        print(f"\n[3] Priority Service 테스트...")
        from src.services.schedule_priority_service import SchedulePriorityService
        from src.models.meeting import Meeting, Attendee, AttendeeRole

        priority_service = SchedulePriorityService()

        # 테스트 회의 생성
        test_meeting = Meeting(
            title="테스트 회의",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            content="테스트 회의입니다",
            attendees=[
                Attendee(emp.id, emp.name, emp.team, AttendeeRole.REQUIRED)
                for emp in employees[:5]
            ]
        )

        target_date = datetime.now() + timedelta(days=7)
        suggestions = priority_service.suggest_meeting_times(
            test_meeting, target_date, duration_hours=1
        )

        print(f"  - 시간 제안: {len(suggestions)}개")
        if suggestions:
            best = suggestions[0]
            print(f"  - 최적 시간: {best.start_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"  - 우선순위 점수: {best.priority_score:.1f}")
            print(f"  - 참석률: {best.attendance_rate:.1%}")

        print(f"\n[성공] 모든 기본 기능이 정상 작동합니다!")
        return True

    except Exception as e:
        print(f"\n[오류] 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_priority_algorithm():
    """우선순위 알고리즘 데모"""
    print("\n" + "=" * 50)
    print("[데모] 우선순위 알고리즘")
    print("=" * 50)

    try:
        from src.api.employee_api import get_employee_api
        from src.services.schedule_priority_service import SchedulePriorityService
        from src.models.meeting import Meeting, Attendee, AttendeeRole
        from datetime import datetime, timedelta

        emp_api = get_employee_api()
        priority_service = SchedulePriorityService()

        # 시나리오: 임원진 + 리더진 전략 회의
        executives = emp_api.get_executives()[:2]
        pls = emp_api.get_employees_by_role("PL")[:2]
        tls = emp_api.get_employees_by_role("TL")[:3]

        all_attendees = executives + pls + tls

        strategic_meeting = Meeting(
            title="전략 회의",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            content="분기 전략 수립",
            attendees=[
                Attendee(emp.id, emp.name, emp.team,
                         AttendeeRole.ORGANIZER if i == 0 else AttendeeRole.REQUIRED)
                for i, emp in enumerate(all_attendees)
            ]
        )

        print(f"\n[회의 정보]")
        print(f"- 제목: {strategic_meeting.title}")
        print(f"- 참석자: {len(strategic_meeting.attendees)}명")
        print(f"- 예상 시간: 2시간")

        print(f"\n[참석자 구성]")
        for attendee in strategic_meeting.attendees:
            emp = emp_api.get_employee_by_id(attendee.employee_id)
            role_display = emp.role if emp.role else "일반직원"
            print(f"  - {attendee.name} ({role_display}, {emp.team})")

        # 다음 주 수요일로 목표 설정
        target_date = datetime.now() + timedelta(days=7)
        target_date = target_date + timedelta(days=(2 - target_date.weekday()) % 7)

        print(f"\n[목표 날짜] {target_date.strftime('%Y년 %m월 %d일 %A')}")

        # 우선순위 알고리즘 실행
        print(f"\n[분석중] 최적 시간 계산...")
        suggestions = priority_service.suggest_meeting_times(
            strategic_meeting, target_date, duration_hours=2
        )

        if suggestions:
            best = suggestions[0]

            print(f"\n[최적 추천]")
            print(f"- 일시: {best.start_time.strftime('%m월 %d일 (%A) %H:%M')} - {best.end_time.strftime('%H:%M')}")
            print(f"- 참석률: {best.attendance_rate:.1%} ({best.available_attendees}/{best.total_required_attendees}명)")
            print(f"- 우선순위 점수: {best.priority_score:.1f}/100")

            if best.time_preference_bonus:
                print(f"- [특징] 선호 시간대 (오전 10시 또는 오후 3시)")
            if best.target_date_proximity >= 0.8:
                print(f"- [특징] 목표 날짜에 근접")
            if best.lunch_time_penalty:
                print(f"- [주의] 점심시간 겹침")
            if best.conflicted_attendees:
                print(f"- [주의] 일정 충돌: {len(best.conflicted_attendees)}명")

            print(f"\n[대안 시간]")
            for i, suggestion in enumerate(suggestions[1:4], 2):
                print(f"{i}. {suggestion.start_time.strftime('%m/%d %H:%M')}-{suggestion.end_time.strftime('%H:%M')} "
                      f"(점수: {suggestion.priority_score:.1f}, 참석률: {suggestion.attendance_rate:.1%})")

        else:
            print(f"\n[결과] 적절한 시간을 찾을 수 없습니다.")

        print(f"\n[완료] 우선순위 알고리즘 데모 완료!")
        return True

    except Exception as e:
        print(f"\n[오류] 데모 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    print("[시작] AI 회의 예약 시스템 검증")
    print(f"Python 버전: {sys.version}")
    print(f"작업 디렉토리: {os.getcwd()}")

    # 기본 기능 테스트
    test1_success = test_basic_functionality()

    # 우선순위 알고리즘 데모
    test2_success = demo_priority_algorithm()

    # 결과 요약
    print(f"\n" + "=" * 50)
    print("[결과 요약]")
    print("=" * 50)

    results = [
        ("기본 기능 테스트", test1_success),
        ("우선순위 알고리즘 데모", test2_success)
    ]

    for name, success in results:
        status = "[성공]" if success else "[실패]"
        print(f"- {name}: {status}")

    all_success = all(success for _, success in results)

    if all_success:
        print(f"\n[완료] 모든 검증이 성공적으로 완료되었습니다!")
        print(f"\n[다음 단계]")
        print(f"1. Streamlit 앱 실행: streamlit run app.py")
        print(f"2. Google API 키 설정: set GOOGLE_API_KEY=your-key")
        print(f"3. 브라우저에서 http://localhost:8501 접속")
        print(f"4. AI 어시스턴트에서 '다음 주 수요일에 적절한 시간 제안해줘' 테스트")
    else:
        print(f"\n[주의] 일부 검증이 실패했습니다.")

    return all_success


if __name__ == "__main__":
    success = main()
    input(f"\n[종료] 엔터를 누르면 종료됩니다...")
    sys.exit(0 if success else 1)
