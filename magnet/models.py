"""
데이터 모델 모듈
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional


@dataclass
class Meeting:
    """회의 데이터 모델"""
    title: str
    start_time: datetime
    end_time: datetime
    attendees: str
    content: str
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meeting':
        """딕셔너리에서 생성"""
        return cls(**data)
    
    def get_formatted_start_time(self) -> str:
        """포맷된 시작 시간 반환"""
        return self.start_time.strftime('%Y-%m-%d %H:%M')
    
    def get_formatted_end_time(self) -> str:
        """포맷된 종료 시간 반환"""
        return self.end_time.strftime('%Y-%m-%d %H:%M')
    
    def get_formatted_date(self) -> str:
        """포맷된 날짜 반환"""
        return self.start_time.strftime('%m/%d %H:%M')
    
    def get_truncated_title(self, max_length: int = 20) -> str:
        """잘린 제목 반환"""
        if len(self.title) > max_length:
            return self.title[:max_length] + "..."
        return self.title
    
    def get_truncated_content(self, max_length: int = 50) -> str:
        """잘린 내용 반환"""
        if len(self.content) > max_length:
            return self.content[:max_length] + "..."
        return self.content


@dataclass
class ChatMessage:
    """채팅 메시지 데이터 모델"""
    user: str
    assistant: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """딕셔너리에서 생성"""
        return cls(**data)


@dataclass
class LLMResponse:
    """LLM 응답 데이터 모델"""
    action: str
    updates: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMResponse':
        """딕셔너리에서 생성"""
        return cls(**data)
    
    def is_error(self) -> bool:
        """에러 응답인지 확인"""
        return self.error is not None
    
    def is_update(self) -> bool:
        """업데이트 응답인지 확인"""
        return self.action == "update" and self.updates is not None


class MeetingStorage:
    """회의 저장소 클래스"""
    
    def __init__(self):
        self.meetings: List[Meeting] = []
    
    def add_meeting(self, meeting: Meeting) -> None:
        """회의 추가"""
        self.meetings.append(meeting)
    
    def get_meetings(self) -> List[Meeting]:
        """모든 회의 반환"""
        return self.meetings
    
    def get_recent_meetings(self, count: int = 10) -> List[Meeting]:
        """최근 회의 반환"""
        return list(reversed(self.meetings[-count:]))
    
    def clear_meetings(self) -> None:
        """모든 회의 삭제"""
        self.meetings.clear()
    
    def get_meeting_by_index(self, index: int) -> Optional[Meeting]:
        """인덱스로 회의 반환"""
        if 0 <= index < len(self.meetings):
            return self.meetings[index]
        return None


class ChatStorage:
    """채팅 저장소 클래스"""
    
    def __init__(self):
        self.chat_history: List[ChatMessage] = []
    
    def add_message(self, message: ChatMessage) -> None:
        """메시지 추가"""
        self.chat_history.append(message)
    
    def get_messages(self) -> List[ChatMessage]:
        """모든 메시지 반환"""
        return self.chat_history
    
    def get_recent_messages(self, count: int = 5) -> List[ChatMessage]:
        """최근 메시지 반환"""
        return self.chat_history[-count:]
    
    def clear_messages(self) -> None:
        """모든 메시지 삭제"""
        self.chat_history.clear()