"""
채팅 및 AI 응답 관련 데이터 모델
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class ChatMessage:
    """채팅 메시지 데이터 모델"""
    user: str
    assistant: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        return cls(**data)


@dataclass
class LLMResponse:
    """LLM 응답 데이터 모델"""
    action: str
    updates: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    action_description: Optional[str] = None
    requires_confirmation: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMResponse':
        return cls(**data)

    def is_error(self) -> bool:
        return self.error is not None

    def is_update(self) -> bool:
        return self.action == "update" and self.updates is not None

    def is_general_chat(self) -> bool:
        return self.action == "chat"


class ChatStorage:
    """채팅 저장소 클래스"""

    def __init__(self):
        self.chat_history: List[ChatMessage] = []

    def add_message(self, message: ChatMessage) -> None:
        self.chat_history.append(message)

    def get_messages(self) -> List[ChatMessage]:
        return self.chat_history

    def get_recent_messages(self, count: int = 5) -> List[ChatMessage]:
        return self.chat_history[-count:]

    def clear_messages(self) -> None:
        self.chat_history.clear()