"""
AI Meeting Booking System - 메인 애플리케이션
"""
import streamlit as st
from typing import Dict, Any

from src.utils.config import PAGE_CONFIG
from src.utils.styles import get_css_styles
from src.utils.session import SessionManager
from src.components.layout import HeaderComponent, MessageComponent, UsageGuideComponent
from src.components.sidebar import SidebarLogoComponent, MeetingHistoryComponent
from src.components.ai_chat import AIAssistantComponent
from src.components.meeting_form import MeetingFormComponent, MeetingActionsComponent
from src.components.attendee_table import AttendeeManagementComponent
from src.services.meeting_service import MeetingService
from src.models.chat import LLMResponse
from src.models.meeting import Meeting


class MeetingBookingApp:
    """회의 예약 애플리케이션 메인 클래스"""

    def __init__(self):
        self.session_manager = SessionManager()
        self.setup_page()
        self.load_styles()

    def setup_page(self):
        """페이지 설정"""
        st.set_page_config(**PAGE_CONFIG)

    def load_styles(self):
        """CSS 스타일 로드"""
        st.markdown(get_css_styles(), unsafe_allow_html=True)

    def create_sidebar(self):
        """사이드바 생성"""
        with st.sidebar:
            # 로고
            sidebar_logo = SidebarLogoComponent()
            sidebar_logo.render()

            # 이전 회의 내역
            meeting_history = MeetingHistoryComponent(
                self.session_manager.get_meeting_storage()
            )
            history_action = meeting_history.render()

            if history_action:
                self._handle_history_action(history_action)

            st.divider()

            # AI 어시스턴트
            ai_assistant = AIAssistantComponent(
                self.session_manager.get_ai_service(),
                self.session_manager.get_chat_storage()
            )
            ai_result = ai_assistant.render()

            # AI 어시스턴트 액션 처리
            self._handle_ai_assistant_actions(ai_result)

    def _handle_history_action(self, action: Dict[str, Any]):
        """회의 히스토리 액션 처리"""
        if action["action"] == "load":
            # 회의 수정 모드로 불러오기
            self.session_manager.load_meeting(action["meeting"])
            MessageComponent.render_success("회의 정보를 불러왔습니다!")
            st.rerun()

        elif action["action"] == "copy":
            # 회의 복사
            self.session_manager.copy_meeting(action["meeting"])
            MessageComponent.render_success("회의 정보를 복사했습니다!")
            st.rerun()

        elif action["action"] == "delete":
            # 회의 삭제
            success = self.session_manager.delete_meeting(action["meeting"])
            if success:
                MessageComponent.render_success("회의를 삭제했습니다!")
            else:
                MessageComponent.render_error("회의 삭제에 실패했습니다.")
            st.rerun()

    def _handle_ai_assistant_actions(self, ai_result: Dict[str, Any]):
        """AI 어시스턴트 액션 처리"""
        if ai_result['send_clicked'] and ai_result['prompt']:
            self._process_ai_prompt_stream(ai_result['prompt'])

        elif ai_result['clear_clicked']:
            self.session_manager.get_chat_storage().clear_messages()
            MessageComponent.render_success("채팅 히스토리를 초기화했습니다!")
            st.rerun()

    def _process_ai_prompt_stream(self, prompt: str):
        """AI 프롬프트 처리 (즉시 적용)"""
        ai_service = self.session_manager.get_ai_service()
        current_meeting = self.session_manager.get_current_meeting()

        # AI 서비스 초기화 확인
        if not ai_service.is_initialized:
            success, message = ai_service.initialize()
            if not success:
                MessageComponent.render_error(message)
                return

        try:
            result = ai_service.process_prompt_stream(prompt, current_meeting)
            if result and len(result) == 2:
                action_data, response_generator = result
            else:
                self.session_manager.add_chat_message(prompt, "응답 처리 중 오류가 발생했습니다.")
                st.rerun()
                return

            # RESPONSE 수집
            full_response = ""
            try:
                for chunk in response_generator:
                    full_response += chunk
            except Exception:
                full_response = "응답 생성 중 오류가 발생했습니다."

            # 응답 정리
            full_response = full_response.replace('```', '').strip()

            # ACTION 처리 - 즉시 적용
            if action_data and action_data.get("action") == "update" and "updates" in action_data:
                llm_response = LLMResponse(
                    action="update",
                    updates=action_data["updates"],
                    message="회의 정보가 업데이트되었습니다."
                )

                # 변경사항 분석을 위한 이전 상태 저장
                previous_meeting = current_meeting

                # 회의 정보 즉시 업데이트
                updated_meeting = MeetingService.update_meeting_from_llm_response(
                    current_meeting, llm_response
                )
                self.session_manager.set_current_meeting(updated_meeting)

                # 하이라이트 효과 적용
                self._save_highlighted_fields(action_data.get("updates", {}))

                # 변경사항 상세 분석 및 메시지 개선
                enhanced_response = self._enhance_response_with_changes(
                    full_response, previous_meeting, updated_meeting, action_data.get("updates", {})
                )

                # 개선된 응답으로 채팅에 추가
                self.session_manager.add_chat_message(prompt, enhanced_response)
            else:
                # 일반 채팅
                self.session_manager.add_chat_message(prompt, full_response)

            st.rerun()

        except Exception as e:
            error_message = f"AI 처리 중 오류가 발생했습니다: {str(e)}"
            self.session_manager.add_chat_message(prompt, error_message)
            st.rerun()

    def _enhance_response_with_changes(self, original_response: str, previous_meeting: Meeting,
                                     updated_meeting: Meeting, updates: dict) -> str:
        """변경사항을 분석하여 응답을 개선"""
        changes = []

        # 제목 변경 확인
        if 'title' in updates and previous_meeting.title != updated_meeting.title:
            if previous_meeting.title:
                changes.append(f"• 제목: '{previous_meeting.title}' → '{updated_meeting.title}'")
            else:
                changes.append(f"• 제목: '{updated_meeting.title}'로 설정")

        # 시간 변경 확인
        if ('start_time' in updates or 'end_time' in updates):
            prev_start = previous_meeting.start_time.strftime("%m/%d %H:%M")
            prev_end = previous_meeting.end_time.strftime("%H:%M")
            new_start = updated_meeting.start_time.strftime("%m/%d %H:%M")
            new_end = updated_meeting.end_time.strftime("%H:%M")

            if (previous_meeting.start_time != updated_meeting.start_time or
                previous_meeting.end_time != updated_meeting.end_time):
                changes.append(f"• 시간: {prev_start}~{prev_end} → {new_start}~{new_end}")

        # 참석자 변경 확인
        if 'attendees' in updates:
            prev_count = len(previous_meeting.attendees)
            new_count = len(updated_meeting.attendees)

            if new_count > prev_count:
                # 새로 추가된 참석자 찾기
                prev_ids = {att.employee_id for att in previous_meeting.attendees}
                new_attendees = [att for att in updated_meeting.attendees if att.employee_id not in prev_ids]
                if new_attendees:
                    names = ", ".join([att.name for att in new_attendees])
                    changes.append(f"• 참석자 추가: {names}")

        # 내용 변경 확인
        if 'content' in updates and previous_meeting.content != updated_meeting.content:
            if updated_meeting.content:
                changes.append("• 회의 안건 업데이트")

        # 변경사항이 있으면 원래 응답을 개선
        if changes:
            change_summary = "\n".join(changes)
            if "✅" not in original_response:
                # AI 응답에 체크마크가 없으면 추가
                enhanced = f"✅ 회의 정보를 업데이트했습니다:\n{change_summary}"
            else:
                # 이미 체크마크가 있으면 변경사항 추가
                enhanced = f"{original_response}\n\n**변경사항:**\n{change_summary}"
            return enhanced

        return original_response

    def _save_highlighted_fields(self, updates: dict):
        """변경된 필드들을 하이라이트용으로 저장"""
        import time
        highlighted_fields = {}
        current_time = time.time()

        for field in updates.keys():
            highlighted_fields[field] = current_time

        st.session_state.highlighted_fields = highlighted_fields
        # 3초 후 하이라이트 자동 제거를 위한 타이머 설정
        st.session_state.highlight_duration = 3.0

    def create_main_content(self):
        """메인 컨텐츠 생성"""
        current_meeting = self.session_manager.get_current_meeting()

        # 헤더
        header = HeaderComponent()
        header.render(current_meeting.is_edit_mode)

        # 회의 기본 정보 폼 (제목, 시간)
        meeting_form = MeetingFormComponent()
        updated_meeting = meeting_form.render(current_meeting, self.session_manager)

        # 참석자 관리 (먼저 표시)
        attendee_management = AttendeeManagementComponent()
        updated_meeting = attendee_management.render(updated_meeting)

        # 회의 안건 (나중에 표시)
        content = meeting_form.render_content_editor(updated_meeting, self.session_manager)

        # 최종 회의 정보 업데이트 (content 포함)
        final_meeting = Meeting(
            title=updated_meeting.title,
            start_time=updated_meeting.start_time,
            end_time=updated_meeting.end_time,
            content=content,
            attendees=updated_meeting.attendees,
            meeting_id=updated_meeting.meeting_id,
            is_edit_mode=updated_meeting.is_edit_mode
        )

        # 폼 데이터 업데이트
        self.session_manager.set_current_meeting(final_meeting)

        # 액션 버튼들
        meeting_actions = MeetingActionsComponent(
            self.session_manager.get_meeting_storage()
        )
        actions_result = meeting_actions.render(final_meeting)

        # 액션 처리
        if actions_result['reset_clicked']:
            self.session_manager.reset_current_meeting()
            self.session_manager.clear_highlighted_fields()
            MessageComponent.render_success("폼이 초기화되었습니다!")
            st.rerun()

        if actions_result['cancel_clicked']:
            # 수정 취소 - 새 회의로 전환
            new_meeting = MeetingService.create_default_meeting()
            self.session_manager.set_current_meeting(new_meeting)
            self.session_manager.clear_highlighted_fields()
            MessageComponent.render_success("수정을 취소했습니다!")
            st.rerun()
        
        # 사용법 안내
        usage_guide = UsageGuideComponent()
        usage_guide.render()
    
    def run(self):
        """애플리케이션 실행"""
        self.create_sidebar()
        self.create_main_content()


def main():
    """메인 함수"""
    app = MeetingBookingApp()
    app.run()


if __name__ == "__main__":
    main()