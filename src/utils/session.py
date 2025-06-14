"""
세션 상태 관리
"""
import streamlit as st
from datetime import datetime

from src.models.meeting import Meeting, MeetingStorage, AttendeeRole, Attendee
from src.models.chat import ChatMessage, ChatStorage
from src.services.meeting_service import MeetingService
from src.services.ai_service import AIService


class SessionManager:
    """세션 상태 관리 클래스"""

    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """세션 상태 초기화"""
        # 회의 저장소 초기화
        if 'meeting_storage' not in st.session_state:
            st.session_state.meeting_storage = MeetingStorage()
            self._add_sample_meetings()

        # 채팅 저장소 초기화
        if 'chat_storage' not in st.session_state:
            st.session_state.chat_storage = ChatStorage()

        # 현재 회의 초기화
        if 'current_meeting' not in st.session_state:
            st.session_state.current_meeting = MeetingService.create_default_meeting()

        # AI 서비스 초기화
        if 'ai_service' not in st.session_state:
            st.session_state.ai_service = AIService()

        # 하이라이트된 필드 초기화
        if 'highlighted_fields' not in st.session_state:
            st.session_state.highlighted_fields = {}

        if 'highlight_duration' not in st.session_state:
            st.session_state.highlight_duration = 3.0

    def _add_sample_meetings(self):
        """샘플 회의 3개 추가"""
        from datetime import datetime, timedelta

        sample_meetings = [
            Meeting(
                title="팀 주간 미팅",
                start_time=datetime(2024, 12, 18, 14, 0),
                end_time=datetime(2024, 12, 18, 15, 0),
                content="<p>이번 주 진행사항 공유 및 다음 주 계획 논의</p>",
                attendees=[
                    Attendee("emp_001", "김철수", "개발팀", AttendeeRole.ORGANIZER),
                    Attendee("emp_002", "이영희", "기획팀", AttendeeRole.REQUIRED),
                    Attendee("emp_003", "박민수", "디자인팀", AttendeeRole.REQUIRED)
                ]
            ),
            Meeting(
                title="프로젝트 킥오프 미팅",
                start_time=datetime(2024, 12, 20, 10, 0),
                end_time=datetime(2024, 12, 20, 12, 0),
                content="<p>새로운 프로젝트 시작을 위한 킥오프 미팅</p>",
                attendees=[
                    Attendee("emp_004", "정지영", "개발팀", AttendeeRole.ORGANIZER),
                    Attendee("emp_005", "최윤호", "기획팀", AttendeeRole.REQUIRED),
                    Attendee("emp_006", "한소영", "디자인팀", AttendeeRole.OPTIONAL)
                ]
            ),
            Meeting(
                title="고객사 데모 미팅",
                start_time=datetime(2024, 12, 22, 16, 0),
                end_time=datetime(2024, 12, 22, 17, 30),
                content="<p>개발된 기능 데모 및 피드백 수집</p>",
                attendees=[
                    Attendee("emp_007", "임대현", "영업팀", AttendeeRole.ORGANIZER),
                    Attendee("emp_001", "김철수", "개발팀", AttendeeRole.REQUIRED)
                ]
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
        # st_quill 강제 업데이트를 위해 관련 키 삭제
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith('meeting_content')]
        for key in keys_to_delete:
            del st.session_state[key]

    def get_ai_service(self) -> AIService:
        """AI 서비스 반환"""
        return st.session_state.ai_service

    def reset_current_meeting(self):
        """현재 회의 초기화"""
        st.session_state.current_meeting = MeetingService.create_default_meeting()
        # st_quill 강제 업데이트를 위해 관련 키 삭제
        keys_to_delete = [key for key in st.session_state.keys() if key.startswith('meeting_content')]
        for key in keys_to_delete:
            del st.session_state[key]

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
        meeting.is_edit_mode = True
        self.set_current_meeting(meeting)

    def copy_meeting(self, meeting: Meeting):
        """회의 복사"""
        copied_meeting = MeetingService.copy_meeting_for_new(meeting)
        self.set_current_meeting(copied_meeting)

    def delete_meeting(self, meeting: Meeting):
        """회의 삭제"""
        return self.get_meeting_storage().delete_meeting(meeting.meeting_id)

    def get_highlighted_fields(self):
        """하이라이트된 필드 반환"""
        return st.session_state.get('highlighted_fields', {})

    def clear_highlighted_fields(self):
        """하이라이트된 필드 초기화"""
        st.session_state.highlighted_fields = {}

    def is_field_highlighted(self, field_name: str) -> bool:
        """특정 필드가 하이라이트되어야 하는지 확인"""
        import time
        highlighted_fields = st.session_state.get('highlighted_fields', {})
        highlight_duration = st.session_state.get('highlight_duration', 3.0)

        if field_name in highlighted_fields:
            # 하이라이트 시작 시간에서 지정된 시간이 지났는지 확인
            elapsed_time = time.time() - highlighted_fields[field_name]
            if elapsed_time <= highlight_duration:
                return True
            else:
                # 시간이 지나면 해당 필드 하이라이트 제거
                if 'highlighted_fields' in st.session_state and field_name in st.session_state.highlighted_fields:
                    del st.session_state.highlighted_fields[field_name]

        return False