"""
테스트: tests/services/test_schedule_priority_service.py
일정 우선순위 알고리즘 테스트
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import unittest
from datetime import datetime, timedelta
from src.services.schedule_priority_service import SchedulePriorityService
from src.models.meeting import Meeting, Attendee, AttendeeRole
from src.api.employee_api import get_employee_api
from src.api.schedule_api import get_schedule_api


class TestSchedulePriorityService(unittest.TestCase):
    """일정 우선순위 서비스 테스트"""

    def setUp(self):
        """테스트 준비"""
        self.service = SchedulePriorityService()
        self.employee_api = get_employee_api()
        self.schedule_api = get_schedule_api()

        # 테스트용 회의 생성
        executives = self.employee_api.get_executives()[:2]  # 임원 2명
        leaders = self.employee_api.get_leaders()[:3]       # 리더 3명
        all_employees = self.employee_api.get_all_employees()[:5]  # 일반 직원 포함 5명

        self.test_meeting = Meeting(
            title="개발 전략 회의",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            content="개발 전략 논의",
            attendees=[
                Attendee(emp.id, emp.name, emp.team, AttendeeRole.ORGANIZER)
                if i == 0 else Attendee(emp.id, emp.name, emp.team, AttendeeRole.REQUIRED)
                for i, emp in enumerate(all_employees)
            ]
        )

    def test_suggest_meeting_times_basic(self):
        """기본 회의 시간 제안 테스트"""
        target_date = datetime.now() + timedelta(days=7)  # 다음 주
        suggestions = self.service.suggest_meeting_times(
            self.test_meeting, target_date, duration_hours=1
        )

        # 최소 5개 이상의 제안이 있어야 함
        self.assertGreaterEqual(len(suggestions), 5)

        # 첫 번째 제안이 가장 높은 점수를 가져야 함
        for i in range(1, len(suggestions)):
            self.assertGreaterEqual(
                suggestions[0].priority_score,
                suggestions[i].priority_score
            )

        print(f"\n=== 기본 회의 시간 제안 테스트 ===")
        for i, suggestion in enumerate(suggestions[:5]):
            print(f"{i+1}. {suggestion.get_description()}")

    def test_time_preference_scoring(self):
        """시간 선호도 점수 테스트"""
        target_date = datetime.now().replace(hour=10, minute=0)

        # 오전 10시 슬롯 찾기
        suggestions = self.service.suggest_meeting_times(
            self.test_meeting, target_date, duration_hours=1
        )

        morning_10_suggestions = [
            s for s in suggestions if s.start_time.hour == 10
        ]

        afternoon_3_suggestions = [
            s for s in suggestions if s.start_time.hour == 15
        ]

        # 오전 10시나 오후 3시 제안이 있어야 함
        self.assertTrue(
            len(morning_10_suggestions) > 0 or len(afternoon_3_suggestions) > 0,
            "선호 시간대 제안이 없습니다"
        )

        print(f"\n=== 시간 선호도 테스트 ===")
        if morning_10_suggestions:
            print(f"오전 10시 제안: {morning_10_suggestions[0].get_description()}")
        if afternoon_3_suggestions:
            print(f"오후 3시 제안: {afternoon_3_suggestions[0].get_description()}")

    def test_executive_weight_calculation(self):
        """임원 가중치 계산 테스트"""
        # 임원만 포함된 회의
        executives = self.employee_api.get_executives()
        executive_meeting = Meeting(
            title="임원 전략 회의",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            content="임원진 전략 회의",
            attendees=[
                Attendee(emp.id, emp.name, emp.team,
                        AttendeeRole.ORGANIZER if i == 0 else AttendeeRole.REQUIRED)
                for i, emp in enumerate(executives)
            ]
        )

        target_date = datetime.now() + timedelta(days=3)
        suggestions = self.service.suggest_meeting_times(
            executive_meeting, target_date, duration_hours=2
        )

        # 임원 회의는 더 넓은 시간대 제안이 있어야 함
        early_or_late_suggestions = [
            s for s in suggestions
            if s.start_time.hour <= 8 or s.start_time.hour >= 19
        ]

        print(f"\n=== 임원 가중치 테스트 ===")
        print(f"임원 회의 참석자: {[att.name for att in executive_meeting.attendees]}")
        print(f"연장 시간대 제안 수: {len(early_or_late_suggestions)}")

        for suggestion in suggestions[:3]:
            print(f"- {suggestion.get_description()}")

    def test_lunch_time_penalty(self):
        """점심시간 페널티 테스트"""
        target_date = datetime.now().replace(hour=12, minute=30)  # 점심시간
        suggestions = self.service.suggest_meeting_times(
            self.test_meeting, target_date, duration_hours=1
        )

        lunch_time_suggestions = [
            s for s in suggestions
            if s.lunch_time_penalty
        ]

        non_lunch_suggestions = [
            s for s in suggestions
            if not s.lunch_time_penalty
        ]

        # 점심시간이 아닌 제안이 더 높은 점수를 가져야 함
        if lunch_time_suggestions and non_lunch_suggestions:
            self.assertGreater(
                max(s.priority_score for s in non_lunch_suggestions),
                max(s.priority_score for s in lunch_time_suggestions)
            )

        print(f"\n=== 점심시간 페널티 테스트 ===")
        print(f"점심시간 제안 수: {len(lunch_time_suggestions)}")
        print(f"비점심시간 제안 수: {len(non_lunch_suggestions)}")

    def test_date_proximity_scoring(self):
        """날짜 근접도 점수 테스트"""
        base_date = datetime.now()

        # 목표 날짜별 제안 비교
        target_dates = [
            base_date + timedelta(days=1),   # 내일
            base_date + timedelta(days=7),   # 다음 주
            base_date + timedelta(days=14)   # 2주 후
        ]

        print(f"\n=== 날짜 근접도 테스트 ===")

        for i, target_date in enumerate(target_dates):
            suggestions = self.service.suggest_meeting_times(
                self.test_meeting, target_date, duration_hours=1
            )

            if suggestions:
                best_suggestion = suggestions[0]
                days_diff = (best_suggestion.start_time.date() - target_date.date()).days
                print(f"목표 {i+1}: {target_date.strftime('%Y-%m-%d')} "
                      f"-> 제안: {best_suggestion.start_time.strftime('%Y-%m-%d')} "
                      f"(차이: {abs(days_diff)}일, 점수: {best_suggestion.priority_score:.1f})")

    def test_conflict_handling(self):
        """일정 충돌 처리 테스트"""
        # 특정 시간에 일부 참석자 일정 추가
        target_time = datetime.now() + timedelta(days=5)
        target_time = target_time.replace(hour=14, minute=0, second=0, microsecond=0)

        # 첫 번째 참석자에게 해당 시간 일정 추가
        first_attendee_id = self.test_meeting.attendees[0].employee_id
        self.schedule_api.create_schedule(
            employee_id=first_attendee_id,
            title="기존 회의",
            start_datetime=target_time,
            end_datetime=target_time + timedelta(hours=1),
            content="충돌 테스트용 회의"
        )

        suggestions = self.service.suggest_meeting_times(
            self.test_meeting, target_time, duration_hours=1
        )

        # 해당 시간대 제안 찾기
        conflicted_suggestions = [
            s for s in suggestions
            if s.start_time == target_time
        ]

        print(f"\n=== 일정 충돌 처리 테스트 ===")
        if conflicted_suggestions:
            suggestion = conflicted_suggestions[0]
            print(f"충돌 시간대: {suggestion.get_description()}")
            print(f"충돌 참석자 수: {len(suggestion.conflicted_attendees)}")
            print(f"참석률: {suggestion.attendance_rate:.1%}")

        # 충돌 없는 대안 시간 확인
        no_conflict_suggestions = [
            s for s in suggestions[:5]
            if len(s.conflicted_attendees) == 0
        ]

        print(f"충돌 없는 대안 시간:")
        for suggestion in no_conflict_suggestions[:3]:
            print(f"- {suggestion.get_description()}")

    def test_comprehensive_scenario(self):
        """종합 시나리오 테스트"""
        print(f"\n=== 종합 시나리오 테스트 ===")

        # 대규모 회의 (임원 + 리더 + 일반 직원)
        all_employees = self.employee_api.get_all_employees()
        executives = self.employee_api.get_executives()
        leaders = self.employee_api.get_leaders()

        large_meeting = Meeting(
            title="전사 전략 회의",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            content="전사 전략 및 방향성 논의",
            attendees=[
                Attendee(emp.id, emp.name, emp.team, AttendeeRole.ORGANIZER)
                if emp in executives[:1] else
                Attendee(emp.id, emp.name, emp.team, AttendeeRole.REQUIRED)
                for emp in (executives + leaders + all_employees[:10])
            ]
        )

        target_date = datetime.now() + timedelta(days=7)  # 다음 주 수요일
        if target_date.weekday() != 2:  # 수요일로 조정
            days_to_add = (2 - target_date.weekday()) % 7
            target_date = target_date + timedelta(days=days_to_add)

        suggestions = self.service.suggest_meeting_times(
            large_meeting, target_date, duration_hours=2
        )

        print(f"대규모 회의 ({len(large_meeting.attendees)}명 참석)")
        print(f"목표 날짜: {target_date.strftime('%Y-%m-%d %A')}")
        print(f"회의 시간: 2시간")

        if suggestions:
            best_suggestion = suggestions[0]
            explanation = self.service.get_best_time_explanation(
                best_suggestion, large_meeting
            )
            print(f"\n{explanation}")

            # 상위 5개 제안 표시
            print(f"\n상위 5개 제안:")
            for i, suggestion in enumerate(suggestions[:5]):
                print(f"{i+1}. {suggestion.get_description()}")


def run_priority_algorithm_demo():
    """우선순위 알고리즘 데모 실행"""
    print("=" * 60)
    print("🚀 AI 회의 예약 시스템 - 일정 우선순위 알고리즘 데모")
    print("=" * 60)

    service = SchedulePriorityService()
    employee_api = get_employee_api()

    # 데모 시나리오 1: 개발팀 주간 미팅
    print("\n📋 시나리오 1: 개발팀 주간 미팅")
    dev_team = employee_api.get_team_members("개발팀")
    dev_meeting = Meeting(
        title="개발팀 주간 미팅",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        content="주간 진행사항 공유",
        attendees=[
            Attendee(emp.id, emp.name, emp.team,
                    AttendeeRole.ORGANIZER if i == 0 else AttendeeRole.REQUIRED)
            for i, emp in enumerate(dev_team[:5])
        ]
    )

    target_date = datetime.now() + timedelta(days=7)
    suggestions = service.suggest_meeting_times(dev_meeting, target_date, 1)

    print(f"참석자: {', '.join([att.name for att in dev_meeting.attendees])}")
    print(f"목표 날짜: {target_date.strftime('%Y-%m-%d')}")
    print("\n추천 시간대:")
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"{i+1}. {suggestion.get_description()}")

    # 데모 시나리오 2: 임원 전략 회의
    print("\n\n🏢 시나리오 2: 임원 전략 회의")
    executives = employee_api.get_executives()
    exec_meeting = Meeting(
        title="임원 전략 회의",
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=2),
        content="사업 전략 논의",
        attendees=[
            Attendee(emp.id, emp.name, emp.team,
                    AttendeeRole.ORGANIZER if i == 0 else AttendeeRole.REQUIRED)
            for i, emp in enumerate(executives)
        ]
    )

    suggestions = service.suggest_meeting_times(exec_meeting, target_date, 2)

    print(f"참석자: {', '.join([f'{att.name}({employee_api.get_employee_by_id(att.employee_id).role})' for att in exec_meeting.attendees])}")
    print("\n추천 시간대:")
    for i, suggestion in enumerate(suggestions[:3]):
        print(f"{i+1}. {suggestion.get_description()}")

    if suggestions:
        best_explanation = service.get_best_time_explanation(suggestions[0], exec_meeting)
        print(f"\n{best_explanation}")


if __name__ == "__main__":
    # 단위 테스트 실행
    print("🧪 단위 테스트 실행 중...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # 데모 실행
    print("\n" + "="*60)
    run_priority_algorithm_demo()
    print("="*60)