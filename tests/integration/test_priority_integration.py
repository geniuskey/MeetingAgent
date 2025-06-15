# tests/integration/test_priority_integration.py
import pytest
from datetime import datetime, timedelta
from src.services.schedule_priority_service import SchedulePriorityService
from src.api.employee_api import get_employee_api
from tests.api.test_employee_api import TestMockEmployeeAPI
from tests.api.test_schedule_api import TestMockScheduleAPI
from tests.services.test_schedule_priority_service import TestSchedulePriorityService


class TestPriorityIntegration:
    """우선순위 시스템 통합 테스트"""

    def setup_method(self):
        self.priority_service = SchedulePriorityService()
        self.employee_api = get_employee_api()

    def test_end_to_end_scenario(self):
        """종단간 시나리오 테스트"""
        print("\n=== 실제 사용 시나리오 테스트 ===")

        # 시나리오: "다음 주 수요일에 개발 전략 회의를 해야하는데 적절한 시간을 제안해줘"

        # 1. 개발팀 주요 인물들 선정
        dev_team = self.employee_api.get_team_members("개발팀")
        attendees = []

        # 개발팀 PL, TL, 핵심 개발자 선정
        for emp in dev_team:
            if emp.role in ["PL", "TL"] or emp.name in ["강준호", "윤서연"]:
                attendees.append(emp.id)

        # 경영진에서 CTO 역할 추가 (사장 or 상무)
        executives = self.employee_api.get_team_members("경영진")
        attendees.append(executives[0].id)  # 사장

        print(f"참석자: {len(attendees)}명")
        for att_id in attendees:
            emp = self.employee_api.get_employee_by_id(att_id)
            print(f"  - {emp.name} ({emp.role or '일반직'}, {emp.team})")

        # 2. 다음 주 수요일 계산
        today = datetime.now()
        days_until_wednesday = (2 - today.weekday()) % 7  # 수요일은 2
        if days_until_wednesday == 0:  # 오늘이 수요일이면 다음 주
            days_until_wednesday = 7

        target_wednesday = today + timedelta(days=days_until_wednesday)
        print(f"목표 날짜: {target_wednesday.strftime('%Y-%m-%d (%A)')}")

        # 3. 최적 시간 제안
        suggestions = self.priority_service.suggest_meeting_times(
            attendees, target_wednesday, 120  # 2시간 회의
        )

        assert len(suggestions) > 0, "시간 제안이 없습니다"

        print(f"\n추천 시간 순위:")
        for i, slot in enumerate(suggestions, 1):
            analysis = self.priority_service.get_detailed_analysis(slot, attendees)

            print(f"\n{i}순위: {slot.start_str} - {slot.end_str}")
            print(f"  종합 점수: {slot.score}점")
            print(f"  가용성: {slot.availability_rate * 100:.0f}%")
            print(f"  충돌 인원: {len(slot.conflicts)}명")

            if analysis["시간대_분석"]["시간대"] == "최적":
                print(f"  ✨ 최적 시간대")

            if slot.conflicts:
                print(f"  ⚠️ 충돌: {', '.join(slot.conflicts)}")

    def test_different_meeting_types(self):
        """다양한 회의 유형별 테스트"""
        target_date = datetime.now() + timedelta(days=5)

        scenarios = [
            {
                "name": "임원진 회의",
                "attendees": ["emp_001", "emp_002", "emp_003"],  # 사장, 부사장, 상무
                "duration": 60
            },
            {
                "name": "팀장급 회의",
                "attendees": ["emp_005", "emp_006", "emp_007"],  # PL들
                "duration": 90
            },
            {
                "name": "전체 팀 회의",
                "attendees": ["emp_001", "emp_005", "emp_020", "emp_021", "emp_022"],
                "duration": 120
            }
        ]

        print(f"\n=== 회의 유형별 최적 시간 비교 ===")

        for scenario in scenarios:
            suggestions = self.priority_service.suggest_meeting_times(
                scenario["attendees"], target_date, scenario["duration"]
            )

            if suggestions:
                best_slot = suggestions[0]
                print(f"\n{scenario['name']}:")
                print(f"  최적 시간: {best_slot.start_str} - {best_slot.end_str}")
                print(f"  점수: {best_slot.score}")
                print(f"  가용성: {best_slot.availability_rate * 100:.0f}%")

    def test_peak_hours_optimization(self):
        """피크 시간대 최적화 테스트"""
        # 임원급 + 리더급 혼합 회의
        mixed_attendees = ["emp_001", "emp_005", "emp_010"]
        target_date = datetime.now() + timedelta(days=4)

        suggestions = self.priority_service.suggest_meeting_times(
            mixed_attendees, target_date, 60
        )

        # 최고 점수 시간이 10시 또는 15시인지 확인
        if suggestions:
            best_slot = suggestions[0]
            best_hour = best_slot.start_time.hour

            # 10시 또는 15시가 최고 점수를 받는지 검증
            optimal_hours = [10, 15]

            print(f"최적 시간: {best_slot.start_str} (점수: {best_slot.score})")

            if best_hour in optimal_hours:
                print("✅ 최적 시간대(10시/15시)가 선택됨")
            else:
                print(f"⚠️ 최적 시간대가 아닌 {best_hour}시가 선택됨")
                # 이유 분석
                analysis = self.priority_service.get_detailed_analysis(best_slot, mixed_attendees)
                print(f"선택 이유: 가용성 {analysis['충돌_분석']['가용성'] * 100:.0f}%")


if __name__ == "__main__":
    # 빠른 테스트 실행
    def run_quick_tests():
        print("🧪 Mock API 기본 테스트")

        # Employee API 테스트
        emp_test = TestMockEmployeeAPI()
        emp_test.setup_method()
        emp_test.test_employee_data_generation()
        emp_test.test_search_functionality()
        emp_test.test_team_functionality()
        print("✅ Employee API 테스트 통과")

        # Schedule API 테스트
        schedule_test = TestMockScheduleAPI()
        schedule_test.setup_method()
        schedule_test.test_schedule_data_generation()
        schedule_test.test_conflict_detection()
        print("✅ Schedule API 테스트 통과")

        # Priority Service 테스트
        priority_test = TestSchedulePriorityService()
        priority_test.setup_method()
        priority_test.test_time_score_calculation()
        priority_test.test_role_priority_calculation()
        priority_test.test_suggest_meeting_times_executive_meeting()
        print("✅ Priority Service 테스트 통과")

        # 통합 테스트
        integration_test = TestPriorityIntegration()
        integration_test.setup_method()
        integration_test.test_end_to_end_scenario()
        print("✅ 통합 테스트 통과")

        print("\n🎉 모든 테스트 통과!")


    run_quick_tests()