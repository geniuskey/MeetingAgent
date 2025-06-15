# tests/api/test_schedule_api.py
import pytest
from datetime import datetime, timedelta
from src.api.schedule_api import get_schedule_api


class TestMockScheduleAPI:

    def setup_method(self):
        """테스트 설정"""
        self.api = get_schedule_api()

    def test_schedule_data_generation(self):
        """일정 데이터 생성 테스트"""
        schedules = self.api.schedules

        # 충분한 일정 데이터 생성 확인
        assert len(schedules) > 100, f"일정이 {len(schedules)}개만 생성됨"

        # 임원급과 일반직의 일정 빈도 차이 확인
        executive_schedules = [s for s in schedules if s.employee_id == "emp_001"]  # 사장
        regular_schedules = [s for s in schedules if s.employee_id == "emp_020"]  # 일반직

        # 임원급이 더 많은 일정을 가져야 함
        exec_daily_avg = len(executive_schedules) / 21  # 3주
        regular_daily_avg = len(regular_schedules) / 21

        assert exec_daily_avg > regular_daily_avg, "임원급이 일반직보다 일정이 많아야 합니다"

        print(f"임원급 일평균 일정: {exec_daily_avg:.1f}개")
        print(f"일반직 일평균 일정: {regular_daily_avg:.1f}개")

    def test_conflict_detection(self):
        """일정 충돌 감지 테스트"""
        # 테스트용 시간 설정 (내일 오전 10시)
        tomorrow = datetime.now() + timedelta(days=1)
        test_start = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
        test_end = test_start + timedelta(hours=1)

        # 여러 임직원의 충돌 확인
        test_attendees = ["emp_001", "emp_002", "emp_005"]
        conflicts = self.api.check_conflicts(test_attendees, test_start, test_end)

        print(f"충돌 확인 결과: {len(conflicts)}명이 충돌")

        # 충돌 상세 정보 확인
        for emp_id, emp_conflicts in conflicts.items():
            print(f"{emp_id}: {len(emp_conflicts)}개 일정 충돌")

    def test_schedule_creation(self):
        """일정 생성 테스트"""
        # 새 일정 생성
        title = "테스트 회의"
        start_time = datetime.now() + timedelta(days=1, hours=2)
        end_time = start_time + timedelta(hours=1)

        schedule_id = self.api.create_schedule(
            employee_id="emp_001",
            title=title,
            start_datetime=start_time,
            end_datetime=end_time,
            content="테스트 회의 내용"
        )

        assert schedule_id is not None, "일정 생성에 실패했습니다"

        # 생성된 일정 확인
        created_schedules = [s for s in self.api.schedules if s.schedule_id == schedule_id]
        assert len(created_schedules) == 1, "생성된 일정을 찾을 수 없습니다"
        assert created_schedules[0].title == title

    def test_meeting_schedules_creation(self):
        """회의 일정 일괄 생성 테스트"""
        attendee_ids = ["emp_001", "emp_002", "emp_003"]
        title = "팀 전략 회의"
        start_time = datetime.now() + timedelta(days=2)
        end_time = start_time + timedelta(hours=2)

        schedule_ids = self.api.create_meeting_schedules(
            attendee_ids=attendee_ids,
            title=title,
            start_datetime=start_time,
            end_datetime=end_time,
            content="전략 회의 안건"
        )

        assert len(schedule_ids) == len(attendee_ids), "참석자별 일정이 모두 생성되지 않았습니다"

        # 각 참석자의 일정 확인
        for schedule_id in schedule_ids:
            schedules = [s for s in self.api.schedules if s.schedule_id == schedule_id]
            assert len(schedules) == 1, f"일정 {schedule_id}를 찾을 수 없습니다"

