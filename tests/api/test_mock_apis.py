"""
테스트: tests/api/test_mock_apis.py
Mock API 기능 검증 테스트
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import unittest
from datetime import datetime, timedelta
from src.api.employee_api import get_employee_api
from src.api.schedule_api import get_schedule_api


class TestMockEmployeeAPI(unittest.TestCase):
    """임직원 Mock API 테스트"""

    def setUp(self):
        """테스트 준비"""
        self.api = get_employee_api()

    def test_employee_generation(self):
        """임직원 데이터 생성 테스트"""
        employees = self.api.get_all_employees()

        # 30명의 임직원이 생성되어야 함
        self.assertEqual(len(employees), 30)

        # 모든 임직원이 고유 ID를 가져야 함
        ids = [emp.id for emp in employees]
        self.assertEqual(len(ids), len(set(ids)))

        print(f"✅ 총 {len(employees)}명의 임직원 생성 완료")

    def test_role_distribution(self):
        """역할 분배 테스트"""
        employees = self.api.get_all_employees()

        role_counts = {}
        for emp in employees:
            role = emp.role if emp.role else "일반직원"
            role_counts[role] = role_counts.get(role, 0) + 1

        print(f"\n📊 역할별 분배:")
        for role, count in sorted(role_counts.items()):
            print(f"- {role}: {count}명")

        # 임원급 확인
        executives = self.api.get_executives()
        leaders = self.api.get_leaders()

        print(f"\n👥 조직 구성:")
        print(f"- 임원급: {len(executives)}명")
        print(f"- 리더급 (임원 포함): {len(leaders)}명")

        # 최소 1명의 사장과 부사장이 있어야 함
        ceo = self.api.get_employees_by_role("사장")
        vice_ceo = self.api.get_employees_by_role("부사장")

        self.assertGreaterEqual(len(ceo), 1)
        self.assertGreaterEqual(len(vice_ceo), 1)

    def test_team_distribution(self):
        """팀 분배 테스트"""
        teams = self.api.get_all_teams()

        print(f"\n🏢 팀 구성:")
        for team in sorted(teams):
            members = self.api.get_team_members(team)
            print(f"- {team}: {len(members)}명")

            # 각 팀의 멤버 역할 분포
            roles = [emp.role if emp.role else "일반직원" for emp in members]
            role_set = set(roles)
            if len(role_set) > 1:
                print(f"  └ 역할: {', '.join(sorted(role_set))}")

    def test_search_functionality(self):
        """검색 기능 테스트"""
        # 이름 검색
        search_results = self.api.search_by_name("김")
        print(f"\n🔍 '김'으로 검색: {len(search_results)}명")
        for emp in search_results[:3]:
            print(f"- {emp.name} ({emp.team}, {emp.role or '일반직원'})")

        # 특정 팀 검색
        dev_team = self.api.get_team_members("개발팀")
        print(f"\n💻 개발팀: {len(dev_team)}명")
        for emp in dev_team:
            print(f"- {emp.name} ({emp.role or '일반직원'})")


class TestMockScheduleAPI(unittest.TestCase):
    """일정 Mock API 테스트"""

    def setUp(self):
        """테스트 준비"""
        self.api = get_schedule_api()
        self.employee_api = get_employee_api()

    def test_schedule_generation(self):
        """일정 데이터 생성 테스트"""
        schedules = self.api.schedules

        # 일정이 생성되어야 함
        self.assertGreater(len(schedules), 0)

        print(f"✅ 총 {len(schedules)}개의 일정 생성 완료")

        # 날짜별 일정 수 확인
        today = datetime.now().date()
        date_counts = {}

        for schedule in schedules:
            date = schedule.start_datetime.date()
            date_counts[date] = date_counts.get(date, 0) + 1

        print(f"\n📅 일정 분포 (최근 5일):")
        for date in sorted(date_counts.keys())[:5]:
            if date >= today - timedelta(days=5):
                print(f"- {date}: {date_counts[date]}개 일정")

    def test_conflict_detection(self):
        """충돌 감지 테스트"""
        employees = self.employee_api.get_all_employees()[:5]
        employee_ids = [emp.id for emp in employees]

        # 특정 시간에 일정 추가
        test_time = datetime.now() + timedelta(days=1)
        test_time = test_time.replace(hour=14, minute=0, second=0, microsecond=0)

        # 첫 번째 직원에게 일정 추가
        self.api.create_schedule(
            employee_id=employee_ids[0],
            title="테스트 회의",
            start_datetime=test_time,
            end_datetime=test_time + timedelta(hours=1)
        )

        # 충돌 확인
        conflicts = self.api.check_conflicts(
            employee_ids,
            test_time,
            test_time + timedelta(hours=1)
        )

        print(f"\n⚠️ 일정 충돌 테스트:")
        print(f"- 테스트 시간: {test_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"- 충돌 감지: {len(conflicts)}명")

        # 충돌이 감지되어야 함
        self.assertGreater(len(conflicts), 0)
        self.assertIn(employee_ids[0], conflicts)

    def test_alternative_time_suggestion(self):
        """대체 시간 제안 테스트"""
        employees = self.employee_api.get_all_employees()[:3]
        employee_ids = [emp.id for emp in employees]

        target_date = datetime.now() + timedelta(days=1)
        suggestions = self.api.suggest_alternative_times(
            employee_ids,
            duration_minutes=60,
            target_date=target_date
        )

        print(f"\n💡 대체 시간 제안 (상위 5개):")
        for i, suggestion in enumerate(suggestions[:5]):
            print(f"{i + 1}. {suggestion['start_str']}-{suggestion['end_str']} "
                  f"(충돌: {suggestion['conflicts']}건)")

        # 제안이 있어야 함
        self.assertGreater(len(suggestions), 0)

    def test_meeting_schedule_creation(self):
        """회의 일정 생성 테스트"""
        employees = self.employee_api.get_all_employees()[:5]
        employee_ids = [emp.id for emp in employees]

        meeting_time = datetime.now() + timedelta(days=2)
        meeting_time = meeting_time.replace(hour=10, minute=0, second=0, microsecond=0)

        schedule_ids = self.api.create_meeting_schedules(
            attendee_ids=employee_ids,
            title="테스트 전체 회의",
            start_datetime=meeting_time,
            end_datetime=meeting_time + timedelta(hours=1),
            content="전체 회의 테스트"
        )

        print(f"\n📝 회의 일정 생성 테스트:")
        print(f"- 참석자: {len(employee_ids)}명")
        print(f"- 생성된 일정: {len(schedule_ids)}개")
        print(f"- 회의 시간: {meeting_time.strftime('%Y-%m-%d %H:%M')}")

        # 각 참석자마다 일정이 생성되어야 함
        self.assertEqual(len(schedule_ids), len(employee_ids))

        # 생성된 일정 확인
        for emp_id in employee_ids:
            emp_schedules = self.api.get_schedules(
                emp_id, meeting_time, meeting_time + timedelta(hours=1)
            )
            meeting_schedules = [s for s in emp_schedules if s.title == "테스트 전체 회의"]
            self.assertGreater(len(meeting_schedules), 0)


def run_comprehensive_demo():
    """종합 데모 실행"""
    print("=" * 70)
    print("🚀 AI 회의 예약 시스템 - Mock API 및 우선순위 알고리즘 종합 데모")
    print("=" * 70)

    from src.services.schedule_priority_service import SchedulePriorityService
    from src.models.meeting import Meeting, Attendee, AttendeeRole

    employee_api = get_employee_api()
    schedule_api = get_schedule_api()
    priority_service = SchedulePriorityService()

    print("\n📊 시스템 현황")
    print(f"- 등록된 임직원: {len(employee_api.get_all_employees())}명")
    print(f"- 생성된 일정: {len(schedule_api.schedules)}개")
    print(f"- 임원급: {len(employee_api.get_executives())}명")
    print(f"- 리더급: {len(employee_api.get_leaders())}명")

    # 시나리오: 대규모 전략 회의
    print("\n" + "=" * 50)
    print("📋 시나리오: 전사 분기별 전략 회의")
    print("=" * 50)

    # 다양한 레벨의 참석자 선별
    executives = employee_api.get_executives()[:2]  # 임원 2명
    pls = employee_api.get_employees_by_role("PL")[:2]  # PL 2명
    tls = employee_api.get_employees_by_role("TL")[:3]  # TL 3명
    regular_employees = [emp for emp in employee_api.get_all_employees()
                         if emp.role == ""][:5]  # 일반 직원 5명

    all_attendees = executives + pls + tls + regular_employees

    strategic_meeting = Meeting(
        title="전사 분기별 전략 회의",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=3),
        content="분기 성과 검토 및 차기 분기 전략 수립",
        attendees=[
            Attendee(emp.id, emp.name, emp.team,
                     AttendeeRole.ORGANIZER if emp in executives[:1] else AttendeeRole.REQUIRED)
            for emp in all_attendees
        ]
    )

    print(f"📌 회의 정보:")
    print(f"- 제목: {strategic_meeting.title}")
    print(f"- 참석자: {len(strategic_meeting.attendees)}명")
    print(f"- 예상 시간: 3시간")

    print(f"\n👥 참석자 구성:")
    role_composition = {}
    for attendee in strategic_meeting.attendees:
        emp = employee_api.get_employee_by_id(attendee.employee_id)
        role = emp.role if emp.role else "일반직원"
        role_composition[role] = role_composition.get(role, 0) + 1

    for role, count in sorted(role_composition.items(),
                              key=lambda x: {"사장": 1, "부사장": 2, "상무": 3, "Master": 4,
                                             "PL": 5, "그룹장": 6, "TL": 7, "파트장": 8,
                                             "일반직원": 9}.get(x[0], 9)):
        print(f"  - {role}: {count}명")

    # 목표 날짜: 다음 주 수요일
    target_date = datetime.now() + timedelta(days=7)
    target_date = target_date + timedelta(days=(2 - target_date.weekday()) % 7)

    print(f"\n🎯 목표 일정:")
    print(f"- 날짜: {target_date.strftime('%Y년 %m월 %d일 %A')}")
    print(f"- 기간: {target_date.strftime('%Y-%m-%d')} 전후 1주일")

    # 우선순위 알고리즘 실행
    print(f"\n🔄 최적 시간 분석 중...")
    suggestions = priority_service.suggest_meeting_times(
        strategic_meeting, target_date, duration_hours=3
    )

    if suggestions:
        best_suggestion = suggestions[0]

        print(f"\n🏆 최적 추천 시간:")
        print(
            f"- 일시: {best_suggestion.start_time.strftime('%Y년 %m월 %d일 (%A) %H:%M')} - {best_suggestion.end_time.strftime('%H:%M')}")
        print(
            f"- 참석률: {best_suggestion.attendance_rate:.1%} ({best_suggestion.available_attendees}/{best_suggestion.total_required_attendees}명)")
        print(f"- 우선순위 점수: {best_suggestion.priority_score:.1f}/100")

        if best_suggestion.time_preference_bonus:
            print(f"- ✨ 선호 시간대 (오전 10시 또는 오후 3시)")

        if best_suggestion.target_date_proximity >= 0.8:
            print(f"- 📅 목표 날짜에 근접")

        if best_suggestion.lunch_time_penalty:
            print(f"- ⚠️ 점심시간 겹침 주의")

        if best_suggestion.conflicted_attendees:
            print(f"- ⚠️ 일정 충돌: {len(best_suggestion.conflicted_attendees)}명")

            # 충돌 참석자 상세 정보
            print(f"\n📋 일정 충돌 참석자:")
            for emp_id in best_suggestion.conflicted_attendees:
                emp = employee_api.get_employee_by_id(emp_id)
                if emp:
                    conflicts = schedule_api.check_conflicts(
                        [emp_id], best_suggestion.start_time, best_suggestion.end_time
                    )
                    if emp_id in conflicts:
                        conflict_schedule = conflicts[emp_id][0]
                        print(f"  - {emp.name} ({emp.role or '일반직원'}): '{conflict_schedule.title}' "
                              f"{conflict_schedule.start_datetime.strftime('%H:%M')}-"
                              f"{conflict_schedule.end_datetime.strftime('%H:%M')}")

        print(f"\n📊 대안 시간 후보:")
        for i, suggestion in enumerate(suggestions[1:6], 2):
            status_icons = []
            if suggestion.attendance_rate >= 0.9:
                status_icons.append("✅")
            elif suggestion.attendance_rate >= 0.7:
                status_icons.append("⚠️")
            else:
                status_icons.append("❌")

            if suggestion.time_preference_bonus:
                status_icons.append("⭐")

            if suggestion.lunch_time_penalty:
                status_icons.append("🍽️")

            icons_str = " ".join(status_icons) if status_icons else ""

            print(f"{i}. {suggestion.start_time.strftime('%m/%d %H:%M')}-{suggestion.end_time.strftime('%H:%M')} "
                  f"(점수: {suggestion.priority_score:.1f}, 참석률: {suggestion.attendance_rate:.1%}) {icons_str}")

        # 최적화 제안
        print(f"\n💡 최적화 제안:")

        if best_suggestion.attendance_rate < 0.8:
            print(f"- 참석률이 낮습니다. 필수 참석자를 줄이거나 다른 시간을 고려하세요.")

        if best_suggestion.conflicted_attendees:
            high_priority_conflicts = []
            for emp_id in best_suggestion.conflicted_attendees:
                emp = employee_api.get_employee_by_id(emp_id)
                if emp and emp.is_executive():
                    high_priority_conflicts.append(emp)

            if high_priority_conflicts:
                print(f"- 임원급 충돌이 있습니다. 시간 조정을 권장합니다.")

        if best_suggestion.lunch_time_penalty:
            print(f"- 점심시간을 피해 오전 10시나 오후 3시를 고려하세요.")

        # 실제 일정 생성 시뮬레이션
        print(f"\n📝 일정 생성 시뮬레이션:")
        attendee_ids = [att.employee_id for att in strategic_meeting.attendees]

        # 실제로는 생성하지 않고 시뮬레이션만
        print(f"- {len(attendee_ids)}명의 참석자에게 일정 생성 예정")
        print(f"- 예상 일정 ID: {len(attendee_ids)}개 생성")
        print(f"- 회의실 예약: 대회의실 (30명 수용 가능)")
        print(f"- 알림 발송: 회의 1일 전, 1시간 전")

        explanation = priority_service.get_best_time_explanation(best_suggestion, strategic_meeting)
        print(f"\n📋 상세 분석:")
        print(explanation)

    else:
        print(f"\n❌ 해당 기간에 적절한 시간을 찾을 수 없습니다.")
        print(f"- 참석자 수를 줄이거나 기간을 연장해보세요.")


if __name__ == "__main__":
    # Mock API 테스트 실행
    print("🧪 Mock API 테스트 실행 중...")
    unittest.main(argv=[''], exit=False, verbosity=1)

    # 종합 데모 실행
    print("\n" + "=" * 70)
    run_comprehensive_demo()
    print("=" * 70)
    