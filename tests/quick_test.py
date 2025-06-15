# tests/quick_test.py
"""
해커톤용 빠른 테스트 스크립트
개발 중 기능 검증을 위한 스크립트
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.api.employee_api import get_employee_api
from src.api.schedule_api import get_schedule_api
from src.services.schedule_priority_service import SchedulePriorityService


def test_mock_apis():
    """Mock API 기본 테스트"""
    print("🧪 Mock API 테스트 시작...")

    # Employee API 테스트
    emp_api = get_employee_api()

    print(f"✅ 총 임직원: {len(emp_api.employees)}명")

    # 역할별 분포 확인
    executives = [emp for emp in emp_api.employees if emp.role in ["사장", "부사장", "상무", "Master"]]
    leaders = [emp for emp in emp_api.employees if emp.role in ["PL", "그룹장", "TL", "파트장"]]
    regulars = [emp for emp in emp_api.employees if emp.role == ""]

    print(f"  - 임원급: {len(executives)}명")
    print(f"  - 리더급: {len(leaders)}명")
    print(f"  - 일반직: {len(regulars)}명")

    # 검색 테스트
    kim_results = emp_api.search_by_name("김")
    print(f"✅ '김' 검색 결과: {len(kim_results)}명")

    # Schedule API 테스트
    schedule_api = get_schedule_api()
    print(f"✅ 총 일정: {len(schedule_api.schedules)}개")

    # 임원급 vs 일반직 일정 빈도 확인
    exec_schedules = [s for s in schedule_api.schedules if s.employee_id == "emp_001"]
    regular_schedules = [s for s in schedule_api.schedules if s.employee_id == "emp_020"]

    print(f"  - 임원급 일정: {len(exec_schedules)}개")
    print(f"  - 일반직 일정: {len(regular_schedules)}개")

    print("✅ Mock API 테스트 완료\n")


def test_priority_algorithm():
    """우선순위 알고리즘 테스트"""
    print("🎯 우선순위 알고리즘 테스트 시작...")

    priority_service = SchedulePriorityService()

    # 시간대별 점수 확인
    print("⏰ 시간대별 점수:")
    key_hours = [9, 10, 12, 13, 15, 17]
    for hour in key_hours:
        score = priority_service.TIME_SCORES.get(hour, 1.0)
        print(f"  - {hour:2d}시: {score}점")

    # 역할별 우선순위 확인
    print("\n👥 역할별 우선순위:")
    key_roles = ["사장", "PL", "TL", ""]
    for role in key_roles:
        priority = priority_service.ROLE_PRIORITIES.get(role, 20.0)
        role_display = "일반직" if role == "" else role
        print(f"  - {role_display}: {priority}점")

    print("✅ 우선순위 알고리즘 테스트 완료\n")


def test_time_suggestion_scenarios():
    """시간 제안 시나리오 테스트"""
    print("📅 시간 제안 시나리오 테스트 시작...")

    priority_service = SchedulePriorityService()
    emp_api = get_employee_api()

    scenarios = [
        {
            "name": "임원진 회의",
            "attendees": ["emp_001", "emp_002"],  # 사장, 부사장
            "description": "최고 경영진 회의"
        },
        {
            "name": "개발팀 전략 회의",
            "attendees": ["emp_001", "emp_005", "emp_009"],  # 사장 + 개발팀 PL + TL
            "description": "임원 + 개발팀 리더급 혼합"
        },
        {
            "name": "팀 내부 회의",
            "attendees": ["emp_020", "emp_021", "emp_022"],  # 일반직 3명
            "description": "일반 실무자 회의"
        }
    ]

    target_date = datetime.now() + timedelta(days=3)  # 3일 후

    for scenario in scenarios:
        print(f"\n📋 {scenario['name']} ({scenario['description']})")

        # 참석자 정보 출력
        attendee_info = []
        for att_id in scenario['attendees']:
            emp = emp_api.get_employee_by_id(att_id)
            role_display = emp.role if emp.role else "일반직"
            attendee_info.append(f"{emp.name}({role_display})")

        print(f"   참석자: {', '.join(attendee_info)}")

        # 시간 제안
        suggestions = priority_service.suggest_meeting_times(
            scenario['attendees'], target_date, 90  # 1.5시간 회의
        )

        if suggestions:
            print(f"   📊 제안 결과 (상위 3개):")
            for i, slot in enumerate(suggestions[:3], 1):
                availability = int(slot.availability_rate * 100)
                conflict_info = f"충돌 {len(slot.conflicts)}명" if slot.conflicts else "충돌 없음"
                print(f"     {i}. {slot.start_str}-{slot.end_str} "
                      f"(점수: {slot.score}, 가용성: {availability}%, {conflict_info})")
        else:
            print("   ❌ 적절한 시간을 찾을 수 없음")

    print("\n✅ 시간 제안 시나리오 테스트 완료\n")


def test_conflict_detection():
    """일정 충돌 감지 테스트"""
    print("⚠️  일정 충돌 감지 테스트 시작...")

    schedule_api = get_schedule_api()

    # 내일 오전 10시 회의 충돌 확인
    tomorrow = datetime.now() + timedelta(days=1)
    test_start = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    test_end = test_start + timedelta(hours=1)

    test_attendees = ["emp_001", "emp_005", "emp_010"]  # 임원 + 리더급

    conflicts = schedule_api.check_conflicts(test_attendees, test_start, test_end)

    print(f"   🕙 테스트 시간: {test_start.strftime('%m/%d %H:%M')} - {test_end.strftime('%H:%M')}")
    print(f"   👥 테스트 참석자: {len(test_attendees)}명")
    print(f"   ⚠️  충돌 발견: {len(conflicts)}명")

    if conflicts:
        for emp_id, emp_conflicts in conflicts.items():
            emp_api = get_employee_api()
            emp = emp_api.get_employee_by_id(emp_id)
            print(f"     - {emp.name}: {len(emp_conflicts)}개 일정 충돌")
    else:
        print("     ✅ 충돌 없음")

    print("✅ 일정 충돌 감지 테스트 완료\n")


def test_lunch_time_analysis():
    """점심시간 분석 테스트"""
    print("🍽️  점심시간 분석 테스트 시작...")

    priority_service = SchedulePriorityService()
    emp_api = get_employee_api()

    # 개발팀 참석자들
    dev_team = emp_api.get_team_members("개발팀")[:3]

    # 점심시간 회의 vs 일반시간 회의 비교
    lunch_slot = {
        'start_time': datetime.now().replace(hour=12, minute=30),
        'end_time': datetime.now().replace(hour=13, minute=30)
    }

    normal_slot = {
        'start_time': datetime.now().replace(hour=10, minute=0),
        'end_time': datetime.now().replace(hour=11, minute=0)
    }

    lunch_penalty = priority_service._calculate_lunch_penalty(
        lunch_slot['start_time'], lunch_slot['end_time'], dev_team
    )

    normal_penalty = priority_service._calculate_lunch_penalty(
        normal_slot['start_time'], normal_slot['end_time'], dev_team
    )

    print(f"   🕐 일반시간 (10:00-11:00) 패널티: {normal_penalty:.2f}")
    print(f"   🍽️  점심시간 (12:30-13:30) 패널티: {lunch_penalty:.2f}")
    print(f"   📊 점심시간이 {lunch_penalty - normal_penalty:.2f}점 더 높은 패널티")

    print("✅ 점심시간 분석 테스트 완료\n")


def run_comprehensive_test():
    """종합 테스트 실행"""
    print("🚀 AI Meeting Booking System - 종합 테스트 시작")
    print("=" * 60)

    try:
        test_mock_apis()
        test_priority_algorithm()
        test_time_suggestion_scenarios()
        test_conflict_detection()
        test_lunch_time_analysis()

        print("🎉 모든 테스트 통과!")
        print("✅ 해커톤 개발 준비 완료")

    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()


def demo_scenario():
    """데모용 시나리오"""
    print("\n🎬 데모 시나리오: '다음 주 수요일에 개발 전략 회의를 해야하는데 적절한 시간을 제안해줘'")
    print("=" * 80)

    emp_api = get_employee_api()
    priority_service = SchedulePriorityService()

    # 개발 전략 회의 참석자 선정
    ceo = emp_api.get_employee_by_id("emp_001")  # 사장
    dev_pl = None
    dev_tl = None

    # 개발팀에서 PL, TL 찾기
    dev_team = emp_api.get_team_members("개발팀")
    for emp in dev_team:
        if emp.role == "PL" and not dev_pl:
            dev_pl = emp
        elif emp.role == "TL" and not dev_tl:
            dev_tl = emp

    attendees = [ceo.id, dev_pl.id, dev_tl.id]

    print(f"📋 회의: 개발 전략 회의")
    print(f"👥 참석자:")
    print(f"   - {ceo.name} (사장)")
    print(f"   - {dev_pl.name} (개발팀 PL)")
    print(f"   - {dev_tl.name} (개발팀 TL)")

    # 다음 주 수요일 계산
    today = datetime.now()
    days_until_wednesday = (2 - today.weekday()) % 7
    if days_until_wednesday == 0:
        days_until_wednesday = 7

    target_wednesday = today + timedelta(days=days_until_wednesday)
    print(f"🎯 목표 날짜: {target_wednesday.strftime('%Y-%m-%d (%A)')}")

    # 시간 제안
    suggestions = priority_service.suggest_meeting_times(attendees, target_wednesday, 120)

    if suggestions:
        print(f"\n🎯 AI 추천 시간 (상위 3개):")
        for i, slot in enumerate(suggestions[:3], 1):
            availability = int(slot.availability_rate * 100)

            print(f"\n{i}순위: {slot.start_str} - {slot.end_str}")
            print(f"  📊 종합 점수: {slot.score}점")
            print(f"  ✅ 가용성: {availability}%")

            if slot.conflicts:
                print(f"  ⚠️  충돌: {len(slot.conflicts)}명")
            else:
                print(f"  🎉 충돌 없음!")

        # 최적 시간 선택
        best_slot = suggestions[0]
        print(f"\n💡 추천: {best_slot.start_str}에 회의를 잡으시는 것이 좋겠습니다!")

    else:
        print("\n😅 해당 날짜에 적절한 시간을 찾을 수 없습니다.")

    print("\n🎬 데모 시나리오 완료")


if __name__ == "__main__":
    # 기본 테스트 실행
    run_comprehensive_test()

    # 데모 시나리오 실행
    demo_scenario()

    print(f"\n📝 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
