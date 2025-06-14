"""
회의 관리 서비스
"""
from datetime import datetime
from typing import Tuple

from src.utils.config import DEFAULT_MEETING_DURATION
from src.models.meeting import Meeting, AttendeeRole
from src.models.chat import LLMResponse
from src.api.schedule_api import get_schedule_api


class MeetingService:
    """회의 관리 서비스 클래스"""

    @staticmethod
    def create_default_meeting() -> Meeting:
        """기본 회의 생성"""
        now = datetime.now()
        current_minute = now.minute

        # 30분 단위로 반올림
        if current_minute < 30:
            rounded_minute = 0
        else:
            rounded_minute = 30

        start_time = now.replace(minute=rounded_minute, second=0, microsecond=0)
        end_time = start_time + DEFAULT_MEETING_DURATION

        return Meeting(
            title='',
            start_time=start_time,
            end_time=end_time,
            content='',
            attendees=[],
            is_edit_mode=False
        )

    @staticmethod
    def copy_meeting_for_new(original_meeting: Meeting) -> Meeting:
        """기존 회의를 복사하여 새 회의 생성"""
        new_meeting = Meeting(
            title=f"{original_meeting.title} (복사본)",
            start_time=original_meeting.start_time,
            end_time=original_meeting.end_time,
            content=original_meeting.content,
            attendees=original_meeting.attendees.copy(),
            is_edit_mode=False
        )
        return new_meeting

    @staticmethod
    def update_meeting_from_llm_response(meeting: Meeting, llm_response: LLMResponse) -> Meeting:
        """LLM 응답으로 회의 업데이트"""
        if not llm_response.is_update():
            return meeting

        updates = llm_response.updates
        updated_meeting = Meeting(
            title=updates.get('title', meeting.title),
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            content=updates.get('content', meeting.content),
            attendees=meeting.attendees.copy(),
            meeting_id=meeting.meeting_id,
            is_edit_mode=meeting.is_edit_mode
        )

        # 시작 시간 업데이트
        start_time_updated = False
        if 'start_time' in updates:
            try:
                new_start_time = datetime.strptime(updates['start_time'], "%Y-%m-%d %H:%M")
                updated_meeting.start_time = new_start_time
                start_time_updated = True
            except (ValueError, TypeError):
                pass

        # 종료 시간 업데이트
        if 'end_time' in updates:
            try:
                updated_meeting.end_time = datetime.strptime(updates['end_time'], "%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                pass
        else:
            # 종료 시간이 명시적으로 제공되지 않았고 시작 시간이 업데이트된 경우
            # 시작 시간에서 1시간 후를 기본 종료 시간으로 설정
            if start_time_updated:
                updated_meeting.end_time = updated_meeting.start_time + DEFAULT_MEETING_DURATION

        # 참석자 업데이트
        if 'attendees' in updates:
            MeetingService._update_attendees(updated_meeting, updates['attendees'])

        return updated_meeting

    @staticmethod
    def _update_attendees(meeting: Meeting, attendees_data):
        """참석자 정보 업데이트"""
        if isinstance(attendees_data, str):
            # 문자열인 경우 이름으로 검색해서 추가
            from src.api.employee_api import get_employee_api
            from src.models.meeting import Attendee

            emp_api = get_employee_api()
            names = [name.strip() for name in attendees_data.split(',')]

            for name in names:
                employees = emp_api.search_by_name(name)
                if employees:
                    emp = employees[0]  # 첫 번째 결과 사용
                    # 이미 있는지 확인
                    if not any(att.employee_id == emp.id for att in meeting.attendees):
                        attendee = Attendee(
                            employee_id=emp.id,
                            name=emp.name,
                            team=emp.team,
                            role=AttendeeRole.REQUIRED
                        )
                        meeting.attendees.append(attendee)

    @staticmethod
    def validate_meeting(meeting: Meeting) -> Tuple[bool, str]:
        """회의 유효성 검사"""
        if not meeting.title.strip():
            return False, "회의 제목을 입력해주세요."

        if meeting.start_time >= meeting.end_time:
            return False, "종료 시간은 시작 시간보다 늦어야 합니다."

        if not meeting.attendees:
            return False, "최소 한 명의 참석자를 추가해주세요."

        # 주관자 확인
        organizers = [att for att in meeting.attendees if att.role == AttendeeRole.ORGANIZER]
        if not organizers:
            return False, "주관자를 지정해주세요."

        return True, "유효한 회의입니다."

    @staticmethod
    def check_attendee_conflicts(meeting: Meeting) -> None:
        """참석자 일정 충돌 확인"""
        schedule_api = get_schedule_api()
        employee_ids = [att.employee_id for att in meeting.attendees]

        conflicts = schedule_api.check_conflicts(
            employee_ids,
            meeting.start_time,
            meeting.end_time
        )

        # 충돌 정보 업데이트
        for attendee in meeting.attendees:
            attendee.has_conflict = attendee.employee_id in conflicts

    @staticmethod
    def save_meeting_to_api(meeting: Meeting) -> bool:
        """회의를 API에 저장"""
        try:
            schedule_api = get_schedule_api()
            attendee_ids = [att.employee_id for att in meeting.attendees]

            if meeting.is_edit_mode:
                # 수정 모드: 기존 일정 업데이트
                print(f"[MOCK API] 회의 수정: {meeting.title}")
            else:
                # 신규 생성
                schedule_ids = schedule_api.create_meeting_schedules(
                    attendee_ids=attendee_ids,
                    title=meeting.title,
                    start_datetime=meeting.start_time,
                    end_datetime=meeting.end_time,
                    content=meeting.content
                )
                print(f"[MOCK API] 회의 생성 완료: {len(schedule_ids)}개 일정 생성")

            return True
        except Exception as e:
            print(f"[MOCK API] 저장 실패: {str(e)}")
            return False