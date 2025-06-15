# demo.py - 우선순위 알고리즘 데모
"""
AI Meeting Booking System - 우선순위 알고리즘 데모

실행 방법:
python demo.py

이 스크립트는 다음을 보여줍니다:
1. 30명 임직원의 현실적인 일정 생성
2. 역할별 우선순위 알고리즘 동작
3. 다양한 시나리오별 최적 시간 제안
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from src.api.employee_api import MockEmployeeAPI
from src.api.schedule_api import MockScheduleAPI
from src.services.schedule_priority_service import SchedulePriorityService


def main():
    print("🚀 AI Meeting Booking System - 우선순위 알고리즘 데모")
    print("=" * 60)

    # 1. 시스템 초기화
    print("\n📊 시스템 초기화 중...")
    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)
    priority_service = SchedulePriorityService(employee_api, schedule_api)

    print(f"✅ 초기화 완료:")
    print(f"   - 임직원: {len(employee_api.employees)}명")
    print(f"   - 생성된 일정: {len(schedule_api.schedules)}개")

    # 2. 임직원 구성 현황
    print("\n👥 임직원 구성 현황:")
    role_stats = {}
    for emp in employee_api.employees:
        role = emp['role'] if emp['role'] else '실무자'
        role_stats[role] = role_stats.get(role, 0) + 1

    for role, count in role_stats.items():
        print(f"   - {role}: {count}명")

    # 3. 인터랙티브 데모 시작
    print("\n" + "=" * 60)
    print("🎯 회의 시간 제안 데모")
    print("=" * 60)

    while True:
        print("\n원하는 데모를 선택하세요:")
        print("1. 임원진 회의 (최고 우선순위)")
        print("2. 대규모 혼합 회의 (15명)")
        print("3. 팀별 회의 (개발팀)")
        print("4. 사용자 정의 회의")
        print("5. 알고리즘 비교 분석")
        print("0. 종료")

        choice = input("\n선택 (0-5): ").strip()

        if choice == "0":
            print("👋 데모를 종료합니다.")
            break
        elif choice == "1":
            demo_executive_meeting(employee_api, priority_service)
        elif choice == "2":
            demo_large_meeting(employee_api, priority_service)
        elif choice == "3":
            demo_team_meeting(employee_api, priority_service)
        elif choice == "4":
            demo_custom_meeting(employee_api, priority_service)
        elif choice == "5":
            demo_algorithm_analysis(employee_api, priority_service)
        else:
            print("❌ 잘못된 선택입니다.")


def demo_executive_meeting(employee_api, priority_service):
    """임원진 회의 데모"""
    print("\n👑 임원진 회의 시간 제안")
    print("-" * 40)

    # 임원급 참석자 선정
    executives = [emp for emp in employee_api.employees if emp['priority_level'] == 1]
    attendee_ids = [emp['id'] for emp in executives]

    print(f"참석자: {len(attendee_ids)}명")
    for emp in executives:
        print(f"   - {emp['name']} ({emp['role']})")

    # 내일 기준으로 시간 제안
    target_date = datetime.now() + timedelta(days=1)
    print(f"\n목표 날짜: {target_date.strftime('%Y-%m-%d (%A)')}")

    suggestions = priority_service.suggest_meeting_times(attendee_ids, target_date, 90)

    print(f"\n📊 추천 시간 (90분 회의):")
    for i, slot in enumerate(suggestions, 1):
        conflict_count = len(slot.conflicts)
        availability_pct = int(slot.availability_rate * 100)

        print(f"{i}. {slot.start_str} - {slot.end_str}")
        print(f"   점수: {slot.score}점, 가용성: {availability_pct}%")
        if conflict_count > 0:
            print(f"   충돌: {conflict_count}명")
        print()


def demo_large_meeting(employee_api, priority_service):
    """대규모 혼합 회의 데모"""
    print("\n🏢 대규모 혼합 회의 (15명)")
    print("-" * 40)

    # 다양한 레벨의 참석자 선정
    attendees = []
    attendees.extend(employee_api.employees[:2])  # 임원 2명
    attendees.extend(employee_api.employees[4:8])  # PL급 4명
    attendees.extend(employee_api.employees[12:21])  # 중간급 9명

    attendee_ids = [emp['id'] for emp in attendees]

    print(f"참석자: {len(attendee_ids)}명")

    # 역할별 분포 표시
    role_dist = {}
    for emp in attendees:
        role = emp['role'] if emp['role'] else '실무자'
        role_dist[role] = role_dist.get(role, 0) + 1

    for role, count in role_dist.items():
        print(f"   - {role}: {count}명")

    # 다음주 기준으로 시간 제안
    target_date = datetime.now() + timedelta(days=7)
    print(f"\n목표 날짜: {target_date.strftime('%Y-%m-%d (%A)')}")

    suggestions = priority_service.suggest_meeting_times(attendee_ids, target_date, 120)

    print(f"\n📊 추천 시간 (2시간 회의):")
    for i, slot in enumerate(suggestions, 1):
        conflict_count = len(slot.conflicts)
        availability_pct = int(slot.availability_rate * 100)
        available_count = len(attendees) - conflict_count

        print(f"{i}. {slot.start_str} - {slot.end_str}")
        print(f"   점수: {slot.score}점")
        print(f"   참석 가능: {available_count}/{len(attendees)}명 ({availability_pct}%)")
        print()


def demo_team_meeting(employee_api, priority_service):
    """팀별 회의 데모"""
    print("\n💻 개발팀 회의")
    print("-" * 40)

    # 개발팀 전체 선정
    dev_team = employee_api.get_team_members("개발팀")
    attendee_ids = [emp['id'] for emp in dev_team]

    print(f"참석자: {len(attendee_ids)}명 (개발팀 전체)")
    for emp in dev_team:
        role = emp['role'] if emp['role'] else '실무자'
        print(f"   - {emp['name']} ({role})")

    # 이번 주 금요일 기준
    today = datetime.now()
    days_to_friday = (4 - today.weekday()) % 7
    if days_to_friday == 0:
        days_to_friday = 7
    target_date = today + timedelta(days=days_to_friday)

    print(f"\n목표 날짜: {target_date.strftime('%Y-%m-%d (%A)')}")

    suggestions = priority_service.suggest_meeting_times(attendee_ids, target_date, 60)

    print(f"\n📊 추천 시간 (1시간 회의):")
    for i, slot in enumerate(suggestions, 1):
        conflict_count = len(slot.conflicts)
        availability_pct = int(slot.availability_rate * 100)

        print(f"{i}. {slot.start_str} - {slot.end_str}")
        print(f"   점수: {slot.score}점, 가용성: {availability_pct}%")

        if conflict_count > 0:
            print(f"   충돌자: ", end="")
            for emp_id in list(slot.conflicts.keys())[:3]:
                emp = employee_api.get_employee_by_id(emp_id)
                print(f"{emp['name']} ", end="")
            if len(slot.conflicts) > 3:
                print(f"외 {len(slot.conflicts) - 3}명")
            else:
                print()
        print()


def demo_custom_meeting(employee_api, priority_service):
    """사용자 정의 회의 데모"""
    print("\n🎯 사용자 정의 회의")
    print("-" * 40)

    print("참석자를 선택하세요 (이름의 일부 입력):")
    attendees = []

    while True:
        name_input = input(f"참석자 이름 ({len(attendees)}명 선택됨, 완료시 엔터): ").strip()

        if not name_input:
            break

        results = employee_api.search_by_name(name_input)
        if results:
            print("검색 결과:")
            for i, emp in enumerate(results, 1):
                role = emp['role'] if emp['role'] else '실무자'
                print(f"  {i}. {emp['name']} ({emp['team']}, {role})")

            try:
                choice = int(input("선택 (번호): "))
                if 1 <= choice <= len(results):
                    selected = results[choice - 1]
                    if selected not in attendees:
                        attendees.append(selected)
                        print(f"✅ {selected['name']} 추가됨")
                    else:
                        print("❌ 이미 추가된 참석자입니다.")
                else:
                    print("❌ 잘못된 번호입니다.")
            except ValueError:
                print("❌ 숫자를 입력해주세요.")
        else:
            print("❌ 검색 결과가 없습니다.")

    if not attendees:
        print("참석자가 선택되지 않았습니다.")
        return

    attendee_ids = [emp['id'] for emp in attendees]

    print(f"\n선택된 참석자: {len(attendee_ids)}명")
    for emp in attendees:
        role = emp['role'] if emp['role'] else '실무자'
        print(f"   - {emp['name']} ({role})")

    # 날짜 입력
    try:
        days_ahead = int(input("\n며칠 후 회의? (숫자 입력): "))
        target_date = datetime.now() + timedelta(days=days_ahead)

        duration = int(input("회의 시간(분)? (기본 60분): ") or "60")

        print(f"\n목표 날짜: {target_date.strftime('%Y-%m-%d (%A)')}")

        suggestions = priority_service.suggest_meeting_times(attendee_ids, target_date, duration)

        print(f"\n📊 추천 시간 ({duration}분 회의):")
        for i, slot in enumerate(suggestions, 1):
            conflict_count = len(slot.conflicts)
            availability_pct = int(slot.availability_rate * 100)

            print(f"{i}. {slot.start_str} - {slot.end_str}")
            print(f"   점수: {slot.score}점, 가용성: {availability_pct}%")
            print()

    except ValueError:
        print("❌ 잘못된 입력입니다.")


def demo_algorithm_analysis(employee_api, priority_service):
    """알고리즘 비교 분석 데모"""
    print("\n🔍 알고리즘 분석")
    print("-" * 40)

    # 테스트 케이스들
    test_cases = [
        {
            "name": "임원급만",
            "attendees": ["emp_001", "emp_002"],  # 사장, 부사장
            "description": "최고 우선순위"
        },
        {
            "name": "실무자만",
            "attendees": ["emp_025", "emp_026", "emp_027"],  # 실무자들
            "description": "일반 우선순위"
        },
        {
            "name": "혼합 (임원+실무)",
            "attendees": ["emp_001", "emp_025", "emp_026"],  # 임원 + 실무자
            "description": "우선순위 혼합"
        }
    ]

    target_date = datetime.now() + timedelta(days=2)
    print(f"분석 기준일: {target_date.strftime('%Y-%m-%d (%A)')}")
    print(f"회의 시간: 60분\n")

    results = []

    for case in test_cases:
        print(f"📋 {case['name']} ({case['description']})")

        # 참석자 정보
        attendees_info = []
        for emp_id in case['attendees']:
            emp = employee_api.get_employee_by_id(emp_id)
            role = emp['role'] if emp['role'] else '실무자'
            attendees_info.append(f"{emp['name']}({role})")

        print(f"   참석자: {', '.join(attendees_info)}")

        # 시간 제안
        suggestions = priority_service.suggest_meeting_times(case['attendees'], target_date, 60)

        if suggestions:
            best = suggestions[0]
            results.append({
                'name': case['name'],
                'score': best.score,
                'time': best.start_str,
                'availability': int(best.availability_rate * 100)
            })

            print(f"   최적 시간: {best.start_str}")
            print(f"   점수: {best.score}점")
            print(f"   가용성: {int(best.availability_rate * 100)}%")

        print()

    # 결과 분석
    print("📊 분석 결과:")
    print("-" * 30)

    results.sort(key=lambda x: x['score'], reverse=True)

    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}: {result['score']}점 ({result['time']})")

    print(f"\n✨ 인사이트:")
    if results:
        highest = results[0]
        print(f"   - 가장 높은 점수: {highest['name']} ({highest['score']}점)")

        # 시간대별 분석
        time_analysis = {}
        for result in results:
            hour = int(result['time'].split()[1].split(':')[0])
            time_analysis[hour] = time_analysis.get(hour, []) + [result['name']]

        print(f"   - 선호 시간대 분석:")
        for hour, cases in time_analysis.items():
            period = "오전" if hour < 12 else "오후" if hour < 18 else "저녁"
            print(f"     {hour}시 ({period}): {', '.join(cases)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
        import traceback

        traceback.print_exc()


# 빠른 실행용 함수들
def quick_demo():
    """빠른 데모 실행"""
    print("⚡ 빠른 데모 실행")

    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)
    priority_service = SchedulePriorityService(employee_api, schedule_api)

    # 임원진 회의 예시
    executives = ["emp_001", "emp_002", "emp_003"]  # 사장, 부사장, 상무
    target = datetime.now() + timedelta(days=1)

    suggestions = priority_service.suggest_meeting_times(executives, target, 90)

    print(f"임원진 회의 추천 시간 (상위 3개):")
    for i, slot in enumerate(suggestions[:3], 1):
        print(f"{i}. {slot.start_str} - {slot.end_str} (점수: {slot.score})")


def performance_test():
    """성능 테스트"""
    import time

    print("⚡ 성능 테스트")

    employee_api = MockEmployeeAPI()
    schedule_api = MockScheduleAPI(employee_api)
    priority_service = SchedulePriorityService(employee_api, schedule_api)

    # 20명 대규모 회의
    large_group = [f"emp_{i:03d}" for i in range(1, 21)]
    target = datetime.now() + timedelta(days=3)

    start_time = time.time()
    suggestions = priority_service.suggest_meeting_times(large_group, target, 120)
    end_time = time.time()

    print(f"20명 회의 처리 시간: {end_time - start_time:.3f}초")
    print(f"제안 개수: {len(suggestions)}개")
    if suggestions:
        print(f"최고 점수: {suggestions[0].score}점")


# 명령줄에서 직접 실행 가능한 옵션들
if len(sys.argv) > 1:
    if sys.argv[1] == "quick":
        quick_demo()
    elif sys.argv[1] == "performance":
        performance_test()
    elif sys.argv[1] == "test":
        # 테스트 실행
        from tests.test_priority import test_priority_algorithm

        test_priority_algorithm()
    else:
        print("사용법: python demo.py [quick|performance|test]")
        print("  quick: 빠른 데모")
        print("  performance: 성능 테스트")
        print("  test: 알고리즘 테스트")
        print("  (옵션 없음): 인터랙티브 데모")