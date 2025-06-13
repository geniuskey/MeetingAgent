"""
UI 컴포넌트 모듈
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_quill import st_quill

from config import QUILL_TOOLBAR, MAX_MEETINGS_DISPLAY, MAX_CHAT_HISTORY_DISPLAY, CONTENT_PREVIEW_LENGTH
from models import Meeting, ChatMessage, MeetingStorage, ChatStorage
from services import GeminiService, MeetingService


class HeaderComponent:
    """헤더 컴포넌트"""
    
    @staticmethod
    def render():
        """헤더 렌더링"""
        st.markdown("""
        <div class="main-header">
            <h1>📅 AI-Powered Meeting Booking System</h1>
            <p>자연어로 간편하게 회의를 예약하세요</p>
        </div>
        """, unsafe_allow_html=True)


class SidebarLogoComponent:
    """사이드바 로고 컴포넌트"""
    
    @staticmethod
    def render():
        """로고 렌더링"""
        st.markdown("""
        <div style='text-align: center;'>
            <img src="https://cdn-icons-png.flaticon.com/256/3119/3119303.png" 
                 style="width: 96px; height: 96px;">
        </div>
        """, unsafe_allow_html=True)
        st.divider()


class MeetingHistoryComponent:
    """회의 내역 컴포넌트"""
    
    def __init__(self, meeting_storage: MeetingStorage):
        self.meeting_storage = meeting_storage
    
    def render(self):
        """회의 내역 렌더링"""
        st.subheader("📋 이전 회의")
        
        meetings = self.meeting_storage.get_recent_meetings(MAX_MEETINGS_DISPLAY)
        
        if meetings:
            for i, meeting in enumerate(meetings):
                with st.container():
                    st.markdown(f"""
                    <div class="meeting-card">
                        <strong>{meeting.get_truncated_title()}</strong><br>
                        <small>{meeting.get_formatted_date()}</small>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"불러오기", key=f"load_{len(self.meeting_storage.meetings) - 1 - i}"):
                        return meeting
        else:
            st.info("저장된 회의가 없습니다.")
        
        return None


class AIAssistantComponent:
    """AI 어시스턴트 컴포넌트"""
    
    def __init__(self, gemini_service: GeminiService, chat_storage: ChatStorage):
        self.gemini_service = gemini_service
        self.chat_storage = chat_storage
    
    def render(self):
        """AI 어시스턴트 렌더링"""
        st.subheader("🤖 AI 어시스턴트")
        st.markdown('<div class="prompt-container">', unsafe_allow_html=True)

        prompt = st.text_area(
            "자연어로 회의를 예약해보세요",
            placeholder="예: 내일 오후 2시에 김철수, 이영희와 프로젝트 회의 잡아줘",
            height=100
        )

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            send_clicked = st.button("📤 전송", use_container_width=True)

        with col2:
            stream_clicked = st.button("🌊 스트림", use_container_width=True)

        with col3:
            clear_clicked = st.button("🗑️ 초기화", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        return {
            'prompt': prompt,
            'send_clicked': send_clicked,
            'stream_clicked': stream_clicked,
            'clear_clicked': clear_clicked
        }


class ChatHistoryComponent:
    """채팅 히스토리 컴포넌트"""
    
    def __init__(self, chat_storage: ChatStorage):
        self.chat_storage = chat_storage
    
    def render(self):
        """채팅 히스토리 렌더링"""
        messages = self.chat_storage.get_recent_messages(MAX_CHAT_HISTORY_DISPLAY)
        
        if messages:
            st.subheader("💬 대화 기록")
            for chat in messages:
                st.markdown(f"**사용자:** {chat.user}")
                st.markdown(f"**AI:** {chat.assistant}")
                st.markdown("---")


class MeetingFormComponent:
    """회의 폼 컴포넌트"""
    
    def render(self, current_meeting: Meeting):
        """회의 폼 렌더링"""
        st.subheader("📝 회의 예약")

        # 폼 필드들
        col1, col2 = st.columns([2, 1])

        with col1:
            title = st.text_input(
                "회의 제목",
                value=current_meeting.title,
                placeholder="회의 제목을 입력하세요"
            )

        with col2:
            attendees = st.text_input(
                "참석자 (쉼표로 구분)",
                value=current_meeting.attendees,
                placeholder="김철수, 이영희, 박민수"
            )

        # 시간 설정
        col_date, col_time = st.columns([1, 1])

        with col_date:
            start_date = st.date_input(
                "날짜",
                value=current_meeting.start_time.date()
            )

        with col_time:
            time_col1, time_col2 = st.columns(2)

            with time_col1:
                start_time = st.time_input(
                    "시작 시간", 
                    step=timedelta(minutes=30),
                    value=current_meeting.start_time.time()
                )

            with time_col2:
                end_time = st.time_input(
                    "종료 시간", 
                    step=timedelta(minutes=30),
                    value=current_meeting.end_time.time()
                )

        # 회의 내용
        content = st_quill(
            value=current_meeting.content,
            placeholder="회의 안건, 준비사항, 기타 내용을 입력하세요...",
            key="meeting_content",
            toolbar=QUILL_TOOLBAR,
            html=True,
        )

        # 업데이트된 회의 정보 반환
        return Meeting(
            title=title,
            start_time=datetime.combine(start_date, start_time),
            end_time=datetime.combine(start_date, end_time),
            attendees=attendees,
            content=content
        )


class MeetingActionsComponent:
    """회의 액션 컴포넌트"""
    
    def __init__(self, meeting_storage: MeetingStorage):
        self.meeting_storage = meeting_storage
    
    def render(self, current_meeting: Meeting):
        """액션 버튼들 렌더링"""
        col5, col6, col7 = st.columns([1, 1, 2])

        with col5:
            save_clicked = st.button("💾 회의 저장", use_container_width=True)

        with col6:
            reset_clicked = st.button("🔄 폼 초기화", use_container_width=True)

        with col7:
            view_list_clicked = st.button("📊 회의 목록 보기", use_container_width=True)

        # 저장 처리
        if save_clicked:
            is_valid, message = MeetingService.validate_meeting(current_meeting)
            if is_valid:
                self.meeting_storage.add_meeting(current_meeting)
                st.markdown("""
                <div class="success-message">
                    ✅ 회의가 성공적으로 저장되었습니다!
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="error-message">
                    ❌ {message}
                </div>
                """, unsafe_allow_html=True)

        # 회의 목록 보기 처리
        if view_list_clicked:
            self._show_meetings_list()

        return {
            'save_clicked': save_clicked,
            'reset_clicked': reset_clicked,
            'view_list_clicked': view_list_clicked
        }
    
    def _show_meetings_list(self):
        """회의 목록 표시"""
        meetings = self.meeting_storage.get_meetings()
        
        if meetings:
            st.subheader("📋 저장된 회의 목록")

            # 데이터프레임으로 표시
            meetings_df = pd.DataFrame([
                {
                    "제목": m.title,
                    "시작시간": m.get_formatted_start_time(),
                    "종료시간": m.get_formatted_end_time(),
                    "참석자": m.attendees,
                    "내용": m.get_truncated_content(CONTENT_PREVIEW_LENGTH)
                }
                for m in meetings
            ])

            st.dataframe(meetings_df, use_container_width=True)
        else:
            st.info("저장된 회의가 없습니다.")


class UsageGuideComponent:
    """사용법 안내 컴포넌트"""
    
    @staticmethod
    def render():
        """사용법 안내 렌더링"""
        with st.expander("💡 AI 어시스턴트 사용법"):
            st.markdown("""
            **자연어 명령 예시:**
            - "내일 오후 2시에 팀 미팅 잡아줘"
            - "다음 주 월요일 10시부터 12시까지 프로젝트 리뷰 회의"
            - "김철수, 이영희, 박민수와 함께 기획 회의 예약"
            - "회의 제목을 '월간 보고서 검토'로 바꿔줘"
            - "참석자에 홍길동 추가해줘"
            - "회의 시간을 1시간 연장해줘"

            **지원 기능:**
            - 회의 제목, 시간, 참석자, 내용 자동 설정
            - 자연어 시간 표현 인식 (내일, 다음 주, 오후 2시 등)
            - 기존 회의 정보 수정 및 업데이트
            - 회의 저장 및 불러오기
            """)


class MessageComponent:
    """메시지 컴포넌트"""
    
    @staticmethod
    def render_success(message: str):
        """성공 메시지 렌더링"""
        st.markdown(f"""
        <div class="success-message">
            ✅ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_error(message: str):
        """에러 메시지 렌더링"""
        st.markdown(f"""
        <div class="error-message">
            ❌ {message}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_info(message: str):
        """정보 메시지 렌더링"""
        st.info(message)