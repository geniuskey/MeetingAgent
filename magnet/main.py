"""
메인 애플리케이션 모듈
"""
import streamlit as st
from typing import Optional

from config import PAGE_CONFIG
from styles import get_css_styles
from session_manager import SessionManager
from components import (
    HeaderComponent, SidebarLogoComponent, MeetingHistoryComponent,
    AIAssistantComponent, ChatHistoryComponent, MeetingFormComponent,
    MeetingActionsComponent, UsageGuideComponent, MessageComponent
)
from services import MeetingService
from models import LLMResponse


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
            loaded_meeting = meeting_history.render()

            if loaded_meeting:
                self.session_manager.set_current_meeting(loaded_meeting)
                MessageComponent.render_success("회의 정보를 불러왔습니다!")
                st.rerun()

            st.divider()

            # AI 어시스턴트
            ai_assistant = AIAssistantComponent(
                self.session_manager.get_gemini_service(),
                self.session_manager.get_chat_storage()
            )
            ai_result = ai_assistant.render()

            # AI 어시스턴트 액션 처리
            self._handle_ai_assistant_actions(ai_result)

    def _handle_ai_assistant_actions(self, ai_result):
        """AI 어시스턴트 액션 처리"""
        if ai_result['send_clicked'] and ai_result['prompt']:
            self._process_ai_prompt_stream(ai_result['prompt'])

        if ai_result['clear_clicked']:
            self.session_manager.reset_current_meeting()
            MessageComponent.render_success("폼이 초기화되었습니다!")
            st.rerun()

    def _process_ai_prompt_stream(self, prompt: str):
        """AI 프롬프트 처리 (action 분리 + response 스트리밍)"""
        gemini_service = self.session_manager.get_gemini_service()

        # Gemini 서비스 초기화 확인
        if not gemini_service.is_initialized:
            success, message = gemini_service.initialize()
            if not success:
                MessageComponent.render_error(message)
                return

        # 사용자 메시지를 먼저 채팅에 추가
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 처리
        with st.chat_message("assistant"):
            # 1단계: ACTION 처리 (st.status 사용)
            with st.status("Processing...", expanded=False) as status:
                try:
                    # 안전한 언패킹
                    result = gemini_service.process_prompt_stream_with_action(prompt)
                    if result and len(result) == 2:
                        action_data, response_generator = result
                    else:
                        status.update(label="❌ 응답 처리 오류", state="error")
                        st.error("AI 응답 처리 중 오류가 발생했습니다.")
                        return

                    if action_data:
                        status.update(label="회의 정보 업데이트 중...", state="running")

                        # ACTION 데이터로 회의 정보 업데이트
                        if action_data.get("action") == "update" and "updates" in action_data:
                            from models import LLMResponse
                            llm_response = LLMResponse(
                                action="update",
                                updates=action_data["updates"],
                                message="회의 정보가 업데이트되었습니다."
                            )

                            current_meeting = self.session_manager.get_current_meeting()
                            updated_meeting = MeetingService.update_meeting_from_llm_response(
                                current_meeting, llm_response
                            )
                            self.session_manager.set_current_meeting(updated_meeting)

                            status.update(label="✅ 회의 정보 업데이트 완료", state="complete")
                        else:
                            status.update(label="✅ 요청 처리 완료", state="complete")
                    else:
                        status.update(label="✅ 응답 준비 완료", state="complete")

                except Exception as e:
                    status.update(label=f"❌ 처리 중 오류: {str(e)}", state="error")
                    return

            # 2단계: RESPONSE 스트리밍
            full_response = ""
            message_placeholder = st.empty()

            try:
                for chunk in response_generator:
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")  # 커서 효과

                message_placeholder.markdown(full_response)  # 최종 응답

                # 채팅 히스토리에 추가 (응답 부분만)
                self.session_manager.add_chat_message(prompt, full_response)

                # 회의 정보가 업데이트된 경우 rerun
                if action_data and action_data.get("action") == "update":
                    st.rerun()

            except Exception as e:
                error_message = f"응답 스트리밍 중 오류가 발생했습니다: {str(e)}"
                message_placeholder.markdown(error_message)
                self.session_manager.add_chat_message(prompt, error_message)

    def _try_update_meeting_from_response(self, response: str, prompt: str):
        """응답에서 JSON을 추출하여 회의 정보 업데이트 시도 - 더 이상 사용하지 않음"""
        pass

    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """응답에서 JSON 추출"""
        import re
        json_patterns = [
            r'```json\n(.*?)\n```',  # ```json 블록
            r'```\n(.*?)\n```',  # ``` 블록
            r'\{.*\}',  # 중괄호로 둘러싸인 JSON
        ]

        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)

        return None

    def _handle_llm_response(self, llm_response: LLMResponse, prompt: str):
        """LLM 응답 처리 - 더 이상 사용하지 않음"""
        pass
    
    def create_main_content(self):
        """메인 컨텐츠 생성"""
        # 헤더
        header = HeaderComponent()
        header.render()
        
        # 회의 예약 폼
        meeting_form = MeetingFormComponent()
        current_meeting = self.session_manager.get_current_meeting()
        updated_meeting = meeting_form.render(current_meeting)
        
        # 폼 데이터 업데이트
        self.session_manager.set_current_meeting(updated_meeting)
        
        # 액션 버튼들
        meeting_actions = MeetingActionsComponent(
            self.session_manager.get_meeting_storage()
        )
        actions_result = meeting_actions.render(updated_meeting)
        
        # 액션 처리
        if actions_result['reset_clicked']:
            self.session_manager.reset_current_meeting()
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