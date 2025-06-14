"""
회의 및 참석자 관련 데이터 모델
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid


class AttendeeRole(Enum):
    """참석자 역할"""
    ORGANIZER = "주관자"
    REQUIRED = "필수"
    OPTIONAL = "선택"


@dataclass
class Attendee:
    """참석자 데이터 모델"""
    employee_id: str
    name: str
    team: str
    role: AttendeeRole
    has_conflict: bool = False

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['role'] = self.role.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attendee':
        if isinstance(data['role'], str):
            data['role'] = AttendeeRole(data['role'])
        return cls(**data)


@dataclass
class Meeting:
    """회의 데이터 모델"""
    title: str
    start_time: datetime
    end_time: datetime
    content: str
    attendees: List[Attendee]
    meeting_id: str = None
    is_edit_mode: bool = False

    def __post_init__(self):
        if self.meeting_id is None:
            self.meeting_id = str(uuid.uuid4())
        if self.attendees is None:
            self.attendees = []

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['attendees'] = [attendee.to_dict() for attendee in self.attendees]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meeting':
        if 'attendees' in data:
            data['attendees'] = [Attendee.from_dict(a) for a in data['attendees']]
        return cls(**data)

    def get_formatted_start_time(self) -> str:
        return self.start_time.strftime('%Y-%m-%d %H:%M')

    def get_formatted_end_time(self) -> str:
        return self.end_time.strftime('%Y-%m-%d %H:%M')

    def get_formatted_date(self) -> str:
        return self.start_time.strftime('%m/%d %H:%M')

    def get_truncated_title(self, max_length: int = 20) -> str:
        if len(self.title) > max_length:
            return self.title[:max_length] + "..."
        return self.title

    def get_attendee_names(self) -> str:
        return ", ".join([attendee.name for attendee in self.attendees])

    def get_organizer(self) -> Optional[Attendee]:
        for attendee in self.attendees:
            if attendee.role == AttendeeRole.ORGANIZER:
                return attendee
        return None


class MeetingStorage:
    """회의 저장소 클래스"""

    def __init__(self):
        self.meetings: List[Meeting] = []

    def add_meeting(self, meeting: Meeting) -> None:
        self.meetings.append(meeting)

    def update_meeting(self, meeting: Meeting) -> bool:
        for i, m in enumerate(self.meetings):
            if m.meeting_id == meeting.meeting_id:
                self.meetings[i] = meeting
                return True
        return False

    def delete_meeting(self, meeting_id: str) -> bool:
        for i, m in enumerate(self.meetings):
            if m.meeting_id == meeting_id:
                del self.meetings[i]
                return True
        return False

    def get_meetings(self) -> List[Meeting]:
        return self.meetings

    def get_recent_meetings(self, count: int = 10) -> List[Meeting]:
        return list(reversed(self.meetings[-count:]))

    def clear_meetings(self) -> None:
        self.meetings.clear()

    def get_meeting_by_id(self, meeting_id: str) -> Optional[Meeting]:
        for meeting in self.meetings:
            if meeting.meeting_id == meeting_id:
                return meeting
        return None