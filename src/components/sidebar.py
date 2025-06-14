"""
사이드바 컴포넌트들
"""
import streamlit as st
from typing import Optional, Dict, Any

from src.models.meeting import MeetingStorage


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

    def render(self) -> Optional[Dict[str, Any]]:
        """회의 내역 렌더링 (expander + 카드 방식)"""
        meetings = self.meeting_storage.get_meetings()

        # expander 제목에 회의 개수 표시
        expander_title = f"📋 이전 회의 ({len(meetings)}개)" if meetings else "📋 이전 회의"

        with st.expander(expander_title, expanded=False):
            if meetings:
                # 최대 6개 회의만 표시
                displayed_meetings = meetings[:6]

                for i, meeting in enumerate(displayed_meetings):
                    # 각 회의를 카드 형태로 표시
                    organizer = meeting.get_organizer()
                    organizer_name = organizer.name if organizer else "미지정"

                    st.markdown(f"""
                    <div class="meeting-card-expanded">
                        <div class="meeting-card-header">
                            <div class="meeting-title">{meeting.get_truncated_title(22)}</div>
                            <div class="meeting-date-badge">{meeting.start_time.strftime('%m/%d')}</div>
                        </div>
                        <div class="meeting-card-content">
                            <div class="meeting-info-row">
                                <span class="meeting-icon">🕐</span>
                                <span>{meeting.start_time.strftime('%H:%M')} - {meeting.end_time.strftime('%H:%M')}</span>
                            </div>
                            <div class="meeting-info-row">
                                <span class="meeting-icon">👤</span>
                                <span>{organizer_name} 외 {len(meeting.attendees)-1}명</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 액션 버튼들
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button(
                            "📥 수정",
                            key=f"load_meeting_{meeting.meeting_id}",
                            help=f"'{meeting.title}' 회의를 불러와서 수정합니다"
                        ):
                            return {"action": "load", "meeting": meeting}

                    with col2:
                        if st.button(
                            "📋 복사",
                            key=f"copy_meeting_{meeting.meeting_id}",
                            help=f"'{meeting.title}' 회의를 복사해서 새 회의를 만듭니다"
                        ):
                            return {"action": "copy", "meeting": meeting}

                    with col3:
                        if st.button(
                            "🗑️ 삭제",
                            key=f"delete_meeting_{meeting.meeting_id}",
                            help=f"'{meeting.title}' 회의를 삭제합니다"
                        ):
                            return {"action": "delete", "meeting": meeting}

                    # 마지막이 아니면 구분선
                    if i < len(displayed_meetings) - 1:
                        st.markdown('<hr class="meeting-separator">', unsafe_allow_html=True)

                # 더 많은 회의가 있는 경우 안내
                if len(meetings) > 6:
                    st.info(f"💡 총 {len(meetings)}개 회의 중 최근 6개를 표시합니다")
            else:
                st.info("저장된 회의가 없습니다.")

        return None