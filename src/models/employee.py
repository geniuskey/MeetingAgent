"""
임직원 및 일정 관련 데이터 모델
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any
import uuid


@dataclass
class Employee:
    """임직원 데이터 모델"""
    id: str
    name: str
    team: str
    email: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        return cls(**data)


@dataclass
class Schedule:
    """일정 데이터 모델"""
    schedule_id: str
    employee_id: str
    title: str
    start_datetime: datetime
    end_datetime: datetime
    content: str = ""
    attendees: List[str] = None

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []
        if self.schedule_id is None:
            self.schedule_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        return cls(**data)