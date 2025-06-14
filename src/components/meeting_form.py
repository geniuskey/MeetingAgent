"""
회의 폼 컴포넌트
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_quill import st_quill
from typing import Dict

from src.models.meeting import Meeting, MeetingStorage
from src.services.meeting_service import MeetingService
from src.utils.config import QUILL_TOOLBAR


class MeetingFormComponent:
    """회의 폼 컴포넌트"""

    def render(self, current_meeting: Meeting, session_manager) -> Meeting:
        """회의 폼 렌더링"""
        # 하이라이트 CSS 추가
        self._add_highlight_css()

        # 제목 필드 (하이라이트 체크)
        title_highlight = "highlight-field" if session_manager.is_field_highlighted("title") else ""
        st.markdown(f'<div class="{title_highlight}">', unsafe_allow_html=True)
        title = st.text_input(
            "회의 제목",
            value=current_meeting.title,
            placeholder="회의 제목을 입력하세요"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 시간 설정
        col_date, col_time = st.columns([1, 1])

        with col_date:
            # 날짜 하이라이트 체크 (start_time 또는 end_time 변경 시)
            date_highlight = ("highlight-field" if
                             (session_manager.is_field_highlighted("start_time") or
                              session_manager.is_field_highlighted("end_time")) else "")
            st.markdown(f'<div class="{date_highlight}">', unsafe_allow_html=True)
            start_date = st.date_input(
                "날짜",
                value=current_meeting.start_time.date()
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col_time:
            time_col1, time_col2 = st.columns(2)

            with time_col1:
                # 시작 시간 하이라이트
                start_time_highlight = "highlight-field" if session_manager.is_field_highlighted("start_time") else ""
                st.markdown(f'<div class="{start_time_highlight}">', unsafe_allow_html=True)
                start_time = st.time_input(
                    "시작 시간",
                    step=timedelta(minutes=30),
                    value=current_meeting.start_time.time()
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with time_col2:
                # 종료 시간 하이라이트
                end_time_highlight = "highlight-field" if session_manager.is_field_highlighted("end_time") else ""
                st.markdown(f'<div class="{end_time_highlight}">', unsafe_allow_html=True)
                end_time = st.time_input(
                    "종료 시간",
                    step=timedelta(minutes=30),
                    value=current_meeting.end_time.time()
                )
                st.markdown('</div>', unsafe_allow_html=True)

        # 업데이트된 회의 정보 반환 (참석자는 유지)
        updated_meeting = Meeting(
            title=title,
            start_time=datetime.combine(start_date, start_time),
            end_time=datetime.combine(start_date, end_time),
            content=current_meeting.content,  # content는 나중에 별도로 렌더링
            attendees=current_meeting.attendees,
            meeting_id=current_meeting.meeting_id,
            is_edit_mode=current_meeting.is_edit_mode
        )

        return updated_meeting

    def render_content_editor(self, current_meeting: Meeting, session_manager) -> str:
        """회의 안건 에디터 별도 렌더링"""
        # 내용 하이라이트 체크
        content_highlight = "highlight-field" if session_manager.is_field_highlighted("content") else ""

        st.subheader("📝 회의 안건")
        st.markdown(f'<div class="{content_highlight}">', unsafe_allow_html=True)
        content_key = f"meeting_content_{abs(hash(current_meeting.content))}"
        content = st_quill(
            value=current_meeting.content if current_meeting.content else "",
            placeholder="회의 안건, 준비사항, 기타 내용을 입력하세요...",
            key=content_key,
            toolbar=QUILL_TOOLBAR,
            html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        return content if content else ""

    def _add_highlight_css(self):
        """하이라이트 CSS 추가"""
        st.markdown("""
        <style>
        .highlight-field {
            animation: highlightPulse 3s ease-in-out;
            border-radius: 8px;
            padding: 4px;
        }
        
        @keyframes highlightPulse {
            0% { 
                background-color: rgba(102, 126, 234, 0.3);
                box-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
            }
            50% { 
                background-color: rgba(102, 126, 234, 0.1);
                box-shadow: 0 0 5px rgba(102, 126, 234, 0.3);
            }
            100% { 
                background-color: transparent;
                box-shadow: none;
            }
        }
        
        .highlight-field .stTextInput > div > div > input,
        .highlight-field .stDateInput > div > div > input,
        .highlight-field .stTimeInput > div > div > input {
            border-color: #667eea !important;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
        }
        </style>
        """, unsafe_allow_html=True)


class MeetingActionsComponent:
    """회의 액션 컴포넌트"""

    def __init__(self, meeting_storage: MeetingStorage):
        self.meeting_storage = meeting_storage

    def render(self, current_meeting: Meeting) -> Dict[str, bool]:
        """액션 버튼들 렌더링"""
        # 세션 상태에서 버튼 카운터 초기화
        if 'button_counter' not in st.session_state:
            st.session_state.button_counter = 0

        # 고유 버튼 ID 생성
        st.session_state.button_counter += 1
        button_id = st.session_state.button_counter

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            save_label = "💾 회의 수정" if current_meeting.is_edit_mode else "💾 회의 저장"
            save_clicked = st.button(save_label, key=f"save_{button_id}", use_container_width=True)

        with col2:
            reset_clicked = st.button("🔄 폼 초기화", key=f"reset_{button_id}", use_container_width=True)

        with col3:
            view_list_clicked = st.button("📊 회의 목록", key=f"list_{button_id}", use_container_width=True)

        with col4:
            if current_meeting.is_edit_mode:
                cancel_clicked = st.button("❌ 수정 취소", key=f"cancel_{button_id}", use_container_width=True)
            else:
                cancel_clicked = False

        # 저장 처리
        if save_clicked:
            is_valid, message = MeetingService.validate_meeting(current_meeting)
            if is_valid:
                # API에 저장
                api_success = MeetingService.save_meeting_to_api(current_meeting)

                if api_success:
                    if current_meeting.is_edit_mode:
                        # 수정 모드
                        self.meeting_storage.update_meeting(current_meeting)
                        st.markdown("""
                        <div class="success-message">
                            ✅ 회의가 성공적으로 수정되었습니다!
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # 신규 저장
                        self.meeting_storage.add_meeting(current_meeting)
                        st.markdown("""
                        <div class="success-message">
                            ✅ 회의가 성공적으로 저장되었습니다!
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="error-message">
                        ❌ 회의 저장 중 오류가 발생했습니다.
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
            'view_list_clicked': view_list_clicked,
            'cancel_clicked': cancel_clicked
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
                    "참석자": m.get_attendee_names(),
                    "주관자": m.get_organizer().name if m.get_organizer() else "미지정"
                }
                for m in meetings
            ])

            st.dataframe(meetings_df, use_container_width=True)
        else:
            st.info("저장된 회의가 없습니다.")