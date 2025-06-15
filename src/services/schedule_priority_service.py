"""
일정 우선순위 알고리즘 서비스
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dataclasses import dataclass

from src.models.employee import Employee
from src.models.meeting import Meeting, AttendeeRole
from src.api.employee_api import get_employee_api
from src.api.schedule_api import get_schedule_api


@dataclass
class TimeSlotSuggestion:
    """시간대 제안 데이터 모델"""
    start_time: datetime
    end_time: datetime
    priority_score: float
    available_attendees: int
    total_required_attendees: int
    conflicted_attendees: List[str]
    lunch_time_penalty: bool
    time_preference_bonus: bool
    target_date_proximity: float

    @property
    def attendance_rate(self) -> float:
        """참석률 계산"""
        if self.total_required_attendees == 0:
            return 1.0
        return self.available_attendees / self.total_required_attendees

    def get_description(self) -> str:
        """제안 설명 생성"""
        desc = f"{self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')}"
        desc += f" (참석률: {self.attendance_rate:.1%}, 점수: {self.priority_score:.1f})"
        if self.conflicted_attendees:
            desc += f" [충돌: {len(self.conflicted_attendees)}명]"
        return desc


class SchedulePriorityService:
    """일정 우선순위 결정 서비스"""

    def __init__(self):
        self.employee_api = get_employee_api()
        self.schedule_api = get_schedule_api()

    def suggest_meeting_times(self, meeting: Meeting, target_date: datetime,
                              duration_hours: int = 1) -> List[TimeSlotSuggestion]:
        """회의 시간 제안 (우선순위 순)"""

        # 검색 범위 설정: max(현재, target-1주) ~ target+1주
        now = datetime.now()
        search_start = max(now, target_date - timedelta(weeks=1))
        search_end = target_date + timedelta(weeks=1)

        # 30분 단위로 시간대 생성
        time_slots = self._generate_time_slots(search_start, search_end, duration_hours)

        # 각 시간대별 우선순위 계산
        suggestions = []
        for start_time, end_time in time_slots:
            suggestion = self._evaluate_time_slot(
                meeting, start_time, end_time, target_date
            )
            suggestions.append(suggestion)

        # 우선순위 점수순으로 정렬
        suggestions.sort(key=lambda x: x.priority_score, reverse=True)

        return suggestions[:10]  # 상위 10개 제안

    def _generate_time_slots(self, start_date: datetime, end_date: datetime,
                             duration_hours: int) -> List[Tuple[datetime, datetime]]:
        """30분 단위 시간대 생성"""
        slots = []
        current = start_date.replace(hour=8, minute=0, second=0, microsecond=0)

        while current.date() <= end_date.date():
            # 주말 제외
            if current.weekday() >= 5:
                current += timedelta(days=1)
                current = current.replace(hour=8, minute=0)
                continue

            # 8시~20시 사이 30분 간격
            for hour in range(8, 21):
                for minute in [0, 30]:
                    slot_start = current.replace(hour=hour, minute=minute)
                    slot_end = slot_start + timedelta(hours=duration_hours)

                    # 20시 이후로 넘어가지 않도록
                    if slot_end.hour <= 20:
                        slots.append((slot_start, slot_end))

            current += timedelta(days=1)
            current = current.replace(hour=8, minute=0)

        return slots

    def _evaluate_time_slot(self, meeting: Meeting, start_time: datetime,
                            end_time: datetime, target_date: datetime) -> TimeSlotSuggestion:
        """시간대 평가 및 점수 계산"""

        # 필수 참석자들의 정보 수집
        required_attendees = [att for att in meeting.attendees
                              if att.role in [AttendeeRole.ORGANIZER, AttendeeRole.REQUIRED]]

        # 충돌 확인
        employee_ids = [att.employee_id for att in required_attendees]
        conflicts = self.schedule_api.check_conflicts(employee_ids, start_time, end_time)
        conflicted_attendees = list(conflicts.keys())

        available_attendees = len(required_attendees) - len(conflicted_attendees)

        # 기본 점수 계산
        priority_score = 0.0

        # 1. 참석률 점수 (가중치 40%)
        attendance_rate = available_attendees / len(required_attendees) if required_attendees else 1.0
        priority_score += attendance_rate * 40

        # 2. 시간 선호도 점수 (가중치 25%)
        time_preference_bonus = self._calculate_time_preference(start_time, required_attendees)
        priority_score += time_preference_bonus * 25

        # 3. 목표 날짜 근접도 점수 (가중치 20%)
        proximity_score = self._calculate_date_proximity(start_time.date(), target_date.date())
        priority_score += proximity_score * 20

        # 4. 임원 가중치 (가중치 10%)
        executive_weight = self._calculate_executive_weight(required_attendees, conflicted_attendees)
        priority_score += executive_weight * 10

        # 5. 점심시간 페널티 (가중치 5%)
        lunch_penalty = self._is_lunch_time(start_time, end_time)
        if lunch_penalty:
            priority_score -= 5

        return TimeSlotSuggestion(
            start_time=start_time,
            end_time=end_time,
            priority_score=priority_score,
            available_attendees=available_attendees,
            total_required_attendees=len(required_attendees),
            conflicted_attendees=conflicted_attendees,
            lunch_time_penalty=lunch_penalty,
            time_preference_bonus=time_preference_bonus > 0.8,
            target_date_proximity=proximity_score
        )

    def _calculate_time_preference(self, start_time: datetime,
                                   required_attendees: List) -> float:
        """시간 선호도 계산"""
        hour = start_time.hour

        # 오전 10시, 오후 3시가 최고 점수
        if hour == 10 or hour == 15:
            return 1.0

        # 오전 9시, 11시, 오후 2시, 4시가 차선
        elif hour in [9, 11, 14, 16]:
            return 0.8

        # 일반 업무시간 (오전 8시~오후 6시)
        elif 8 <= hour <= 18:
            return 0.6

        # 리더급이 포함된 경우 연장 시간 허용
        has_leaders = any(
            self.employee_api.get_employee_by_id(att.employee_id).is_leader()
            for att in required_attendees
        )

        if has_leaders and (hour == 8 or hour == 19):
            return 0.4

        return 0.2

    def _calculate_date_proximity(self, slot_date, target_date) -> float:
        """목표 날짜 근접도 계산"""
        diff = abs((slot_date - target_date).days)

        if diff == 0:
            return 1.0
        elif diff <= 2:
            return 0.8
        elif diff <= 5:
            return 0.6
        elif diff <= 7:
            return 0.4
        else:
            return 0.2

    def _calculate_executive_weight(self, required_attendees: List,
                                    conflicted_attendees: List[str]) -> float:
        """임원 가중치 계산"""
        total_weight = 0.0
        available_weight = 0.0

        for attendee in required_attendees:
            employee = self.employee_api.get_employee_by_id(attendee.employee_id)
            if employee:
                # 역할별 가중치
                role_weight = {
                    "사장": 10,
                    "부사장": 8,
                    "상무": 6,
                    "Master": 5,
                    "PL": 3,
                    "그룹장": 3,
                    "TL": 2,
                    "파트장": 2,
                    "": 1
                }.get(employee.role, 1)

                total_weight += role_weight

                if attendee.employee_id not in conflicted_attendees:
                    available_weight += role_weight

        return available_weight / total_weight if total_weight > 0 else 1.0

    def _is_lunch_time(self, start_time: datetime, end_time: datetime) -> bool:
        """점심시간 겹침 확인"""
        # 일반적인 점심시간: 12:00~13:30
        lunch_start = start_time.replace(hour=12, minute=0)
        lunch_end = start_time.replace(hour=13, minute=30)

        # 회의 시간이 점심시간과 겹치는지 확인
        return (start_time < lunch_end and end_time > lunch_start)

    def get_best_time_explanation(self, suggestion: TimeSlotSuggestion,
                                  meeting: Meeting) -> str:
        """최적 시간 선택 이유 설명"""
        explanation = f"추천 시간: {suggestion.get_description()}\n\n"

        explanation += "선택 이유:\n"

        if suggestion.attendance_rate >= 0.9:
            explanation += f"✅ 높은 참석률 ({suggestion.attendance_rate:.1%})\n"
        elif suggestion.attendance_rate >= 0.7:
            explanation += f"⚠️ 양호한 참석률 ({suggestion.attendance_rate:.1%})\n"
        else:
            explanation += f"❌ 낮은 참석률 ({suggestion.attendance_rate:.1%})\n"

        if suggestion.time_preference_bonus:
            explanation += "✅ 선호 시간대 (오전 10시 또는 오후 3시)\n"

        if suggestion.target_date_proximity >= 0.8:
            explanation += "✅ 목표 날짜에 근접\n"

        if suggestion.lunch_time_penalty:
            explanation += "⚠️ 점심시간과 겹침\n"

        if suggestion.conflicted_attendees:
            explanation += f"⚠️ 일정 충돌 참석자: {len(suggestion.conflicted_attendees)}명\n"

        return explanation
