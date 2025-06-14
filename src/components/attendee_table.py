"""
참석자 테이블 컴포넌트
"""
import streamlit as st
import pandas as pd
from typing import List

from src.models.meeting import Meeting, AttendeeRole
from src.services.attendee_service import AttendeeService
from src.services.meeting_service import MeetingService
from src.utils.config import CONFLICT_ICONS


class AttendeeManagementComponent:
    """참석자 관리 컴포넌트"""

    def render(self, meeting: Meeting) -> Meeting:
        """참석자 관리 UI 렌더링"""
        st.subheader("👥 참석자 관리")

        # 참석자 추가 UI
        self._render_add_attendee_ui(meeting)

        # 참석자 목록 테이블
        if meeting.attendees:
            self._render_attendee_table(meeting)
        else:
            st.info("참석자를 추가해주세요.")

        return meeting

    def _render_add_attendee_ui(self, meeting: Meeting):
        """참석자 추가 UI"""
        with st.expander("➕ 참석자 추가", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                search_query = st.text_input(
                    "이름 또는 팀 검색",
                    placeholder="김철수 또는 개발팀",
                    key="attendee_search"
                )

            with col2:
                role = st.selectbox(
                    "역할",
                    options=[role.value for role in AttendeeRole],
                    index=1,  # "필수"가 기본값 (AttendeeRole.REQUIRED)
                    key="attendee_role"
                )

            with col3:
                st.write("")  # 높이 맞추기
                # 고유 키 생성
                if 'search_btn_counter' not in st.session_state:
                    st.session_state.search_btn_counter = 0
                st.session_state.search_btn_counter += 1
                search_clicked = st.button("🔍 검색", key=f"search_{st.session_state.search_btn_counter}", use_container_width=True)

            # 검색 결과 표시 및 추가
            if search_clicked and search_query:
                self._show_search_results(meeting, search_query, AttendeeRole(role))

    def _show_search_results(self, meeting: Meeting, query: str, role: AttendeeRole):
        """검색 결과 표시"""
        results = AttendeeService.search_employees(query)

        if results:
            st.write("**검색 결과:**")
            for i, emp_data in enumerate(results[:5]):  # 최대 5개만 표시
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    st.write(f"**{emp_data['name']}**")

                with col2:
                    st.write(emp_data['team'])

                with col3:
                    # 이미 추가된 참석자인지 확인
                    is_already_added = any(
                        att.employee_id == emp_data['id'] for att in meeting.attendees
                    )
                    if is_already_added:
                        st.write("✅ 추가됨")
                    else:
                        st.write("")

                with col4:
                    if not is_already_added:
                        if st.button(
                            "추가",
                            key=f"add_emp_{emp_data['id']}_{i}",
                            use_container_width=True
                        ):
                            success = AttendeeService.add_attendee(meeting, emp_data['id'], role)
                            if success:
                                st.success(f"{emp_data['name']}님을 참석자로 추가했습니다!")
                                # 검색창 초기화
                                if 'attendee_search' in st.session_state:
                                    st.session_state.attendee_search = ""
                                st.rerun()
                            else:
                                st.error("참석자 추가에 실패했습니다.")
        else:
            st.warning("검색 결과가 없습니다.")

    def _render_attendee_table(self, meeting: Meeting):
        """참석자 테이블 렌더링"""
        # 일정 충돌 확인
        MeetingService.check_attendee_conflicts(meeting)

        # 테이블 데이터 준비
        attendee_data = []
        for i, attendee in enumerate(meeting.attendees):
            attendee_data.append({
                "선택": False,
                "이름": attendee.name,
                "팀": attendee.team,
                "역할": attendee.role.value,
                "일정 충돌": CONFLICT_ICONS[attendee.has_conflict],
                "_employee_id": attendee.employee_id,
                "_index": i
            })

        # 데이터프레임으로 표시
        if attendee_data:
            df = pd.DataFrame(attendee_data)

            # 체크박스를 위한 editable dataframe
            edited_df = st.data_editor(
                df.drop(columns=["_employee_id", "_index"]),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "선택": st.column_config.CheckboxColumn(
                        "선택",
                        help="삭제할 참석자를 선택하세요",
                        default=False,
                    ),
                    "역할": st.column_config.SelectboxColumn(
                        "역할",
                        help="참석자 역할을 선택하세요",
                        options=[role.value for role in AttendeeRole],
                        required=True,
                    ),
                    "일정 충돌": st.column_config.TextColumn(
                        "일정 충돌",
                        help="해당 시간에 다른 일정이 있는지 표시",
                        disabled=True,
                    )
                },
                key="attendee_table"
            )

            # 역할 변경 처리
            for i, (original, edited) in enumerate(zip(df.itertuples(), edited_df.itertuples())):
                if original.역할 != edited.역할:
                    new_role = AttendeeRole(edited.역할)
                    AttendeeService.update_attendee_role(
                        meeting,
                        attendee_data[i]["_employee_id"],
                        new_role
                    )

            # 삭제 버튼
            col1, col2 = st.columns([1, 4])
            with col1:
                # 고유 키 생성
                if 'delete_btn_counter' not in st.session_state:
                    st.session_state.delete_btn_counter = 0
                st.session_state.delete_btn_counter += 1
                if st.button("🗑️ 선택 삭제", key=f"delete_{st.session_state.delete_btn_counter}", use_container_width=True):
                    selected_indices = [
                        attendee_data[i]["_employee_id"]
                        for i, row in enumerate(edited_df.itertuples())
                        if row.선택
                    ]
                    if selected_indices:
                        removed_count = AttendeeService.remove_attendees(meeting, selected_indices)
                        st.success(f"{removed_count}명의 참석자를 삭제했습니다.")
                        st.rerun()
                    else:
                        st.warning("삭제할 참석자를 선택해주세요.")

            # 참석자 요약 정보
            organizers = [att for att in meeting.attendees if att.role == AttendeeRole.ORGANIZER]
            required = [att for att in meeting.attendees if att.role == AttendeeRole.REQUIRED]
            optional = [att for att in meeting.attendees if att.role == AttendeeRole.OPTIONAL]
            conflicts = [att for att in meeting.attendees if att.has_conflict]

            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("주관자", len(organizers))
            with col2:
                st.metric("필수 참석자", len(required))
            with col3:
                st.metric("선택 참석자", len(optional))
            with col4:
                st.metric("일정 충돌", len(conflicts), delta=f"-{len(conflicts)}" if conflicts else None)