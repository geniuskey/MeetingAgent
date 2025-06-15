# tests/test_priority.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.api.employee_api import MockEmployeeAPI
from src.api.schedule_api import MockScheduleAPI
from src.services.schedule_priority_service import SchedulePriorityService


def test_priority_algorithm():
    """우선순위 알고리즘 종합 테스트"""
    print("🧪 우선순위 알고리즘 테스트 시작\n")

    # 1. Mock API 초기화
    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)
    priority_service = SchedulePriorityService(employee_api, schedule_api)

    print(f"✅ Mock 데이터 생성 완료:")
    print(f"   - 임직원: {len(employee_api.employees)}명")
    print(f"   - 일정: {len(schedule_api.schedules)}개\n")

    # 2. 시나리오별 테스트
    test_scenarios = [
        {
            "name": "임원진 회의",
            "attendees": ["emp_001", "emp_002", "emp_003"],  # 사장, 부사장, 상무
            "description": "최고 우선순위 회의"
        },
        {
            "name": "PL급 회의",
            "attendees": ["emp_005", "emp_006", "emp_007"],  # PL들
            "description": "고위 리더 회의"
        },
        {
            "name": "혼합 회의",
            "attendees": ["emp_001", "emp_005", "emp_025"],  # 임원 + PL + 실무자
            "description": "다양한 레벨 혼합"
        },
        {
            "name": "대규모 회의",
            "attendees": [f"emp_{i:03d}" for i in range(1, 16)],  # 15명
            "description": "15명 대규모 회의"
        }
    ]

    target_date = datetime.now() + timedelta(days=3)  # 3일 후

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"📋 시나리오 {i}: {scenario['name']} ({scenario['description']})")
        print(f"   참석자 수: {len(scenario['attendees'])}명")

        # 참석자 정보 출력
        attendees_info = []
        for emp_id in scenario['attendees']:
            emp = employee_api.get_employee_by_id(emp_id)
            if emp:
                role_str = emp['role'] if emp['role'] else '실무자'
                attendees_info.append(f"{emp['name']}({role_str})")

        print(f"   참석자: {', '.join(attendees_info[:3])}{'...' if len(attendees_info) > 3 else ''}")

        # 최적 시간 제안
        suggestions = priority_service.suggest_meeting_times(
            scenario['attendees'], target_date, 90
        )

        print(f"   📊 추천 시간 (상위 3개):")
        for j, slot in enumerate(suggestions[:3], 1):
            conflict_count = len(slot.conflicts)
            availability_pct = int(slot.availability_rate * 100)

            print(f"      {j}. {slot.start_str} - {slot.end_str}")
            print(f"         점수: {slot.score}, 가용성: {availability_pct}%, 충돌: {conflict_count}명")

        print()

    # 3. 특정 알고리즘 동작 검증
    print("🔍 알고리즘 세부 검증\n")

    # 시간대 선호도 테스트
    print("⏰ 시간대별 선호도 테스트:")
    test_attendees = ["emp_001", "emp_005"]  # 사장 + PL

    morning_10 = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    afternoon_15 = morning_10.replace(hour=15)
    lunch_12 = morning_10.replace(hour=12)

    for time_slot, label in [(morning_10, "오전 10시"), (afternoon_15, "오후 3시"), (lunch_12, "점심 12시")]:
        suggestions = priority_service.suggest_meeting_times(test_attendees, time_slot, 60)
        if suggestions:
            best_score = suggestions[0].score
            print(f"   {label}: 최고 점수 {best_score}")

    print()

    # 참석자 우선순위 테스트
    print("👑 참석자 우선순위 테스트:")
    executive_meeting = ["emp_001", "emp_002"]  # 임원급만
    regular_meeting = ["emp_025", "emp_026"]  # 실무자만

    exec_suggestions = priority_service.suggest_meeting_times(executive_meeting, target_date, 60)
    regular_suggestions = priority_service.suggest_meeting_times(regular_meeting, target_date, 60)

    if exec_suggestions and regular_suggestions:
        print(f"   임원급 회의 최고 점수: {exec_suggestions[0].score}")
        print(f"   실무자 회의 최고 점수: {regular_suggestions[0].score}")

    print()

    # 일정 충돌 영향 테스트
    print("⚠️ 일정 충돌 영향 테스트:")
    busy_employees = ["emp_001", "emp_002", "emp_003"]  # 임원급 (바쁜 사람들)

    # 현재 시간 기준으로 테스트 (충돌 가능성 높음)
    now_suggestions = priority_service.suggest_meeting_times(busy_employees, datetime.now(), 60)

    if now_suggestions:
        for j, slot in enumerate(now_suggestions[:2], 1):
            conflict_count = len(slot.conflicts)
            print(f"   제안 {j}: 충돌 {conflict_count}명, 점수 {slot.score}")

    print("\n🎉 우선순위 알고리즘 테스트 완료!")


def test_mock_api_functionality():
    """Mock API 기본 기능 테스트"""
    print("🔧 Mock API 기능 테스트 시작\n")

    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)

    # 1. 임직원 검색 테스트
    print("👥 임직원 검색 테스트:")
    search_results = employee_api.search_by_name("김")
    print(f"   '김' 검색 결과: {len(search_results)}명")
    for emp in search_results[:3]:
        print(f"   - {emp['name']} ({emp['team']}, {emp['role']})")

    print()

    # 2. 팀별 조회 테스트
    print("🏢 팀별 조회 테스트:")
    dev_team = employee_api.get_team_members("개발팀")
    print(f"   개발팀: {len(dev_team)}명")
    for emp in dev_team:
        role_str = emp['role'] if emp['role'] else '실무자'
        print(f"   - {emp['name']} ({role_str})")

    print()

    # 3. 일정 충돌 테스트
    print("📅 일정 충돌 테스트:")
    test_time = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)
    test_end = test_time + timedelta(hours=1)

    conflicts = schedule_api.check_conflicts(
        ["emp_001", "emp_002", "emp_003"],
        test_time,
        test_end
    )

    print(f"   테스트 시간: {test_time.strftime('%m/%d %H:%M')} - {test_end.strftime('%H:%M')}")
    print(f"   충돌 발생: {len(conflicts)}명")

    for emp_id, conflict_schedules in conflicts.items():
        emp = employee_api.get_employee_by_id(emp_id)
        print(f"   - {emp['name']}: {len(conflict_schedules)}개 일정 충돌")

    print("\n✅ Mock API 테스트 완료!")


def test_performance():
    """성능 테스트"""
    import time

    print("⚡ 성능 테스트 시작\n")

    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)
    priority_service = SchedulePriorityService(employee_api, schedule_api)

    # 대규모 회의 시간 제안 성능 테스트
    large_attendees = [f"emp_{i:03d}" for i in range(1, 21)]  # 20명
    target_date = datetime.now() + timedelta(days=5)

    start_time = time.time()
    suggestions = priority_service.suggest_meeting_times(large_attendees, target_date, 90)
    end_time = time.time()

    processing_time = end_time - start_time

    print(f"📊 성능 테스트 결과:")
    print(f"   참석자 수: 20명")
    print(f"   처리 시간: {processing_time:.3f}초")
    print(f"   제안 개수: {len(suggestions)}개")
    print(f"   목표: 1초 이내 {'✅' if processing_time < 1.0 else '❌'}")

    if suggestions:
        print(f"   최고 점수: {suggestions[0].score}")

    print()


if __name__ == "__main__":
    test_mock_api_functionality()
    print("=" * 50)
    test_priority_algorithm()
    print("=" * 50)
    test_performance()


# tests/test_integration.py
def test_full_integration():
    """전체 시스템 통합 테스트"""
    print("🔄 전체 시스템 통합 테스트\n")

    # 실제 사용 시나리오 시뮬레이션
    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)
    priority_service = SchedulePriorityService(employee_api, schedule_api)

    # 시나리오: "다음 주 수요일에 개발 전략 회의를 해야하는데 적절한 시간을 제안해줘"
    print("📋 시나리오: 개발 전략 회의 시간 제안")

    # 1. 참석자 선정 (임원 + 개발팀)
    attendees = []
    attendees.extend(["emp_001", "emp_004"])  # 사장, Master
    attendees.extend(["emp_005", "emp_011", "emp_012"])  # 개발팀 PL, TL, 파트장

    print(f"   선정된 참석자: {len(attendees)}명")
    for emp_id in attendees:
        emp = employee_api.get_employee_by_id(emp_id)
        role_str = emp['role'] if emp['role'] else '실무자'
        print(f"   - {emp['name']} ({emp['team']}, {role_str})")

    # 2. 다음 주 수요일 계산
    today = datetime.now()
    days_ahead = 2 - today.weekday()  # 수요일까지 남은 날
    if days_ahead <= 0:
        days_ahead += 7
    next_wednesday = today + timedelta(days=days_ahead + 7)  # 다음 주 수요일

    print(f"\n   목표 날짜: {next_wednesday.strftime('%Y-%m-%d (%A)')}")

    # 3. 최적 시간 제안
    suggestions = priority_service.suggest_meeting_times(attendees, next_wednesday, 120)

    print(f"\n   📊 추천 시간 순위:")
    for i, slot in enumerate(suggestions, 1):
        conflict_count = len(slot.conflicts)
        availability_pct = int(slot.availability_rate * 100)

        print(f"   {i}순위: {slot.start_str} - {slot.end_str}")
        print(f"      점수: {slot.score}점")
        print(f"      가용성: {availability_pct}% ({len(attendees) - conflict_count}/{len(attendees)}명 참석 가능)")

        if conflict_count > 0:
            print(f"      충돌자: ", end="")
            for emp_id in slot.conflicts.keys():
                emp = employee_api.get_employee_by_id(emp_id)
                print(f"{emp['name']} ", end="")
            print()
        print()

    # 4. 최적 시간 선택 및 회의 생성
    if suggestions:
        best_slot = suggestions[0]
        print(f"   ✅ 최종 선택: {best_slot.start_str} - {best_slot.end_str}")

        # 회의 일정 생성
        schedule_ids = schedule_api.create_meeting_schedules(
            attendees,
            "개발 전략 회의",
            best_slot.start_time,
            best_slot.end_time,
            "개발팀 전략 방향 논의"
        )

        print(f"   📅 생성된 일정 ID: {len(schedule_ids)}개")
        print("   🎉 회의 예약 완료!")

    print("\n✅ 통합 테스트 완료!")


if __name__ == "__main__":
    test_full_integration()