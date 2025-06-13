"""
세션 상태 관리 모듈
"""
import streamlit as st
from datetime import datetime

from models import Meeting, ChatMessage, MeetingStorage, ChatStorage
from services import MeetingService, GeminiService


class SessionManager:
    """세션 상태 관리 클래스"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        # 회의 저장소 초기화
        if 'meeting_storage' not in st.session_state:
            st.session_state.meeting_storage = MeetingStorage()
            # 샘플 회의 3개 추가
            self._add_sample_meetings()

        # 채팅 저장소 초기화
        if 'chat_storage' not in st.session_state:
            st.session_state.chat_storage = ChatStorage()

        # 현재 회의 초기화
        if 'current_meeting' not in st.session_state:
            st.session_state.current_meeting = MeetingService.create_default_meeting()

        # Gemini 서비스 초기화
        if 'gemini_service' not in st.session_state:
            st.session_state.gemini_service = GeminiService()

    def _add_sample_meetings(self):
        """샘플 회의 3개 추가"""
        from datetime import datetime, timedelta

        sample_meetings = [
            Meeting(
                title="팀 주간 미팅",
                start_time=datetime(2024, 12, 18, 14, 0),
                end_time=datetime(2024, 12, 18, 15, 0),
                attendees="김철수, 이영희, 박민수",
                content="<p>이번 주 진행사항 공유 및 다음 주 계획 논의</p><ul><li>프로젝트 A 진행률 확인</li><li>신규 기능 개발 일정 조율</li><li>리소스 할당 검토</li></ul>"
            ),
            Meeting(
                title="프로젝트 킥오프 미팅",
                start_time=datetime(2024, 12, 20, 10, 0),
                end_time=datetime(2024, 12, 20, 12, 0),
                attendees="전체 개발팀, 기획팀, 디자인팀",
                content="<p>새로운 프로젝트 시작을 위한 킥오프 미팅</p><ul><li>프로젝트 목표 및 범위 설정</li><li>팀 역할 분담</li><li>일정 계획 수립</li><li>커뮤니케이션 방식 결정</li></ul>"
            ),
            Meeting(
                title="고객사 데모 미팅",
                start_time=datetime(2024, 12, 22, 16, 0),
                end_time=datetime(2024, 12, 22, 17, 30),
                attendees="홍길동, 고객사 담당자",
                content="<p>개발된 기능 데모 및 피드백 수집</p><ul><li>신기능 시연</li><li>고객 요구사항 확인</li><li>추가 개발 사항 논의</li><li>다음 스프린트 계획</li></ul>"
            )
        ]

        for meeting in sample_meetings:
            st.session_state.meeting_storage.add_meeting(meeting)
    
    def get_meeting_storage(self) -> MeetingStorage:
        """회의 저장소 반환"""
        return st.session_state.meeting_storage
    
    def get_chat_storage(self) -> ChatStorage:
        """채팅 저장소 반환"""
        return st.session_state.chat_storage
    
    def get_current_meeting(self) -> Meeting:
        """현재 회의 반환"""
        return st.session_state.current_meeting
    
    def set_current_meeting(self, meeting: Meeting):
        """현재 회의 설정"""
        st.session_state.current_meeting = meeting
    
    def get_gemini_service(self) -> GeminiService:
        """Gemini 서비스 반환"""
        return st.session_state.gemini_service
    
    def reset_current_meeting(self):
        """현재 회의 초기화"""
        st.session_state.current_meeting = MeetingService.create_default_meeting()
    
    def add_chat_message(self, user_message: str, assistant_message: str):
        """채팅 메시지 추가"""
        chat_message = ChatMessage(
            user=user_message,
            assistant=assistant_message,
            timestamp=datetime.now()
        )
        self.get_chat_storage().add_message(chat_message)
    
    def save_current_meeting(self):
        """현재 회의 저장"""
        current_meeting = self.get_current_meeting()
        self.get_meeting_storage().add_meeting(current_meeting)
    
    def load_meeting(self, meeting: Meeting):
        """회의 불러오기"""
        self.set_current_meeting(meeting)
        st.rerun()