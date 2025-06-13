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
        
        # 채팅 저장소 초기화
        if 'chat_storage' not in st.session_state:
            st.session_state.chat_storage = ChatStorage()
        
        # 현재 회의 초기화
        if 'current_meeting' not in st.session_state:
            st.session_state.current_meeting = MeetingService.create_default_meeting()
        
        # Gemini 서비스 초기화
        if 'gemini_service' not in st.session_state:
            st.session_state.gemini_service = GeminiService()
    
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