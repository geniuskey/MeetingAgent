"""
일정 관리 Mock API
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from src.models.employee import Schedule
from src.api.employee_api import get_employee_api


class MockScheduleAPI:
    """임직원 일정 관리 시스템 Mock API"""

    def __init__(self):
        self.schedules: List[Schedule] = []
        self._generate_sample_schedules()

    def _generate_sample_schedules(self):
        """샘플 일정 데이터 생성"""
        emp_api = get_employee_api()
        employees = emp_api.get_all_employees()

        # 최근 1주일과 앞으로 2주일 일정 생성
        start_date = datetime.now() - timedelta(days=7)

        meeting_types = [
            "팀 미팅", "프로젝트 회의", "1:1 미팅", "전체 회의", "워크샵",
            "브레인스토밍", "스프린트 계획", "코드 리뷰", "디자인 리뷰",
            "고객 미팅", "데모 미팅", "교육", "면접", "온보딩"
        ]

        for emp in employees[:10]:  # 처음 10명만 일정 생성
            for _ in range(random.randint(5, 15)):  # 각자 5-15개 일정
                # 랜덤 시간 생성 (10분 단위)
                random_date = start_date + timedelta(
                    days=random.randint(0, 21),
                    hours=random.randint(9, 17),
                    minutes=random.choice([0, 10, 20, 30, 40, 50])
                )

                # 일정 길이 (30분~2시간)
                duration = random.choice([30, 60, 90, 120])
                end_time = random_date + timedelta(minutes=duration)

                # 주말 제외
                if random_date.weekday() < 5:  # 월-금만
                    self.schedules.append(Schedule(
                        schedule_id=str(uuid.uuid4()),
                        employee_id=emp.id,
                        title=random.choice(meeting_types),
                        start_datetime=random_date,
                        end_datetime=end_time,
                        content=f"{random.choice(meeting_types)} 관련 내용",
                        attendees=[emp.id]
                    ))

    def get_schedules(self, employee_id: str, start_datetime: datetime,
                     end_datetime: datetime) -> List[Schedule]:
        """특정 기간의 일정 조회"""
        return [
            schedule for schedule in self.schedules
            if (schedule.employee_id == employee_id and
                schedule.start_datetime >= start_datetime and
                schedule.end_datetime <= end_datetime)
        ]

    def create_schedule(self, employee_id: str, title: str,
                       start_datetime: datetime, end_datetime: datetime,
                       content: str = "", attendees: List[str] = None) -> str:
        """일정 생성"""
        schedule_id = str(uuid.uuid4())
        schedule = Schedule(
            schedule_id=schedule_id,
            employee_id=employee_id,
            title=title,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            content=content,
            attendees=attendees or [employee_id]
        )
        self.schedules.append(schedule)
        print(f"[MOCK API] 일정 생성: {title} ({start_datetime} ~ {end_datetime})")
        return schedule_id

    def update_schedule(self, schedule_id: str, **kwargs) -> bool:
        """일정 수정"""
        for schedule in self.schedules:
            if schedule.schedule_id == schedule_id:
                for key, value in kwargs.items():
                    if hasattr(schedule, key):
                        setattr(schedule, key, value)
                print(f"[MOCK API] 일정 수정: {schedule_id}")
                return True
        return False

    def delete_schedule(self, schedule_id: str) -> bool:
        """일정 삭제"""
        for i, schedule in enumerate(self.schedules):
            if schedule.schedule_id == schedule_id:
                del self.schedules[i]
                print(f"[MOCK API] 일정 삭제: {schedule_id}")
                return True
        return False

    def check_conflicts(self, employee_ids: List[str], start_datetime: datetime,
                       end_datetime: datetime, exclude_schedule_id: str = None) -> Dict[str, List[Schedule]]:
        """일정 충돌 확인"""
        conflicts = {}

        for emp_id in employee_ids:
            emp_conflicts = []
            for schedule in self.schedules:
                if (schedule.employee_id == emp_id and
                    schedule.schedule_id != exclude_schedule_id):
                    # 시간 겹침 확인
                    if (start_datetime < schedule.end_datetime and
                        end_datetime > schedule.start_datetime):
                        emp_conflicts.append(schedule)

            if emp_conflicts:
                conflicts[emp_id] = emp_conflicts

        return conflicts

    def create_meeting_schedules(self, attendee_ids: List[str], title: str,
                               start_datetime: datetime, end_datetime: datetime,
                               content: str = "") -> List[str]:
        """회의 참석자 전원의 일정 생성"""
        schedule_ids = []

        for emp_id in attendee_ids:
            schedule_id = self.create_schedule(
                employee_id=emp_id,
                title=title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                content=content,
                attendees=attendee_ids
            )
            schedule_ids.append(schedule_id)

        return schedule_ids

    def get_employee_schedules_for_period(self, employee_id: str, days: int = 7) -> List[Schedule]:
        """특정 임직원의 최근/향후 일정 조회"""
        now = datetime.now()
        start_date = now - timedelta(days=days//2)
        end_date = now + timedelta(days=days//2)

        return self.get_schedules(employee_id, start_date, end_date)

    def get_all_schedules_for_date(self, target_date: datetime) -> List[Schedule]:
        """특정 날짜의 모든 일정 조회"""
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        return [
            schedule for schedule in self.schedules
            if (schedule.start_datetime >= start_of_day and
                schedule.start_datetime < end_of_day)
        ]

    def get_conflict_details(self, employee_id: str, start_datetime: datetime,
                           end_datetime: datetime) -> List[Dict]:
        """충돌 상세 정보 조회"""
        conflicts = self.check_conflicts([employee_id], start_datetime, end_datetime)

        if employee_id not in conflicts:
            return []

        conflict_details = []
        for schedule in conflicts[employee_id]:
            conflict_details.append({
                "title": schedule.title,
                "start_time": schedule.start_datetime.strftime("%H:%M"),
                "end_time": schedule.end_datetime.strftime("%H:%M"),
                "duration_minutes": int((schedule.end_datetime - schedule.start_datetime).total_seconds() / 60),
                "overlap_start": max(start_datetime, schedule.start_datetime),
                "overlap_end": min(end_datetime, schedule.end_datetime)
            })

        return conflict_details

    def suggest_alternative_times(self, attendee_ids: List[str], duration_minutes: int,
                                target_date: datetime, business_hours: tuple = (9, 18)) -> List[Dict]:
        """대체 시간 제안"""
        suggestions = []
        start_hour, end_hour = business_hours

        # 30분 간격으로 체크
        for hour in range(start_hour, end_hour):
            for minute in [0, 30]:
                proposed_start = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                proposed_end = proposed_start + timedelta(minutes=duration_minutes)

                # 업무시간 내에서만 제안
                if proposed_end.hour <= end_hour:
                    conflicts = self.check_conflicts(attendee_ids, proposed_start, proposed_end)

                    if not conflicts:  # 충돌이 없는 시간
                        suggestions.append({
                            "start_time": proposed_start,
                            "end_time": proposed_end,
                            "start_str": proposed_start.strftime("%H:%M"),
                            "end_str": proposed_end.strftime("%H:%M"),
                            "conflicts": 0
                        })
                    else:
                        # 부분 충돌 정보도 포함
                        conflict_count = sum(len(conflicts[emp_id]) for emp_id in conflicts)
                        suggestions.append({
                            "start_time": proposed_start,
                            "end_time": proposed_end,
                            "start_str": proposed_start.strftime("%H:%M"),
                            "end_str": proposed_end.strftime("%H:%M"),
                            "conflicts": conflict_count
                        })

        # 충돌이 적은 순으로 정렬
        suggestions.sort(key=lambda x: x["conflicts"])
        return suggestions[:5]  # 상위 5개만 반환


# 싱글톤 인스턴스
_schedule_api_instance = None

def get_schedule_api() -> MockScheduleAPI:
    """일정 API 인스턴스 반환"""
    global _schedule_api_instance
    if _schedule_api_instance is None:
        _schedule_api_instance = MockScheduleAPI()
    return _schedule_api_instance
