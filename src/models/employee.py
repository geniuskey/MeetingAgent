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
    role: str = ""  # 상무/Master/부사장/사장/PL/TL/파트장/그룹장 등
    email: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        return cls(**data)

    def get_role_priority(self) -> int:
        """역할별 우선순위 반환 (낮을수록 높은 우선순위)"""
        role_priorities = {
            "사장": 1,
            "부사장": 2,
            "상무": 3,
            "Master": 4,
            "PL": 5,
            "그룹장": 6,
            "TL": 7,
            "파트장": 8,
            "": 9  # 일반 실무자
        }
        return role_priorities.get(self.role, 9)

    def is_executive(self) -> bool:
        """임원급인지 확인"""
        return self.role in ["사장", "부사장", "상무", "Master"]

    def is_leader(self) -> bool:
        """리더급인지 확인 (임원 + PL + 그룹장)"""
        return self.role in ["사장", "부사장", "상무", "Master", "PL", "그룹장"]


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
