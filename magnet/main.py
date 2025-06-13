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

            # 채팅 히스토리
            chat_history = ChatHistoryComponent(
                self.session_manager.get_chat_storage()
            )
            chat_history.render()

    def _handle_ai_assistant_actions(self, ai_result):
        """AI 어시스턴트 액션 처리"""
        if ai_result['send_clicked'] and ai_result['prompt'].strip():
            self._process_ai_prompt(ai_result['prompt'])

        if ai_result['stream_clicked'] and ai_result['prompt'].strip():
            self._process_ai_prompt_stream(ai_result['prompt'])

        if ai_result['clear_clicked']:
            self.session_manager.reset_current_meeting()
            MessageComponent.render_success("폼이 초기화되었습니다!")
            st.rerun()

    def _process_ai_prompt(self, prompt: str):
        """AI 프롬프트 처리 (일반)"""
        gemini_service = self.session_manager.get_gemini_service()

        # Gemini 서비스 초기화 확인
        if not gemini_service.is_initialized:
            success, message = gemini_service.initialize()
            if not success:
                MessageComponent.render_error(message)
                return

        with st.spinner("AI가 처리 중..."):
            llm_response = gemini_service.process_prompt(prompt)

        # 채팅 히스토리에 추가
        self.session_manager.add_chat_message(
            prompt,
            llm_response.message or "처리 완료"
        )

        # 결과 처리
        self._handle_llm_response(llm_response, prompt)

    def _process_ai_prompt_stream(self, prompt: str):
        """AI 프롬프트 처리 (스트리밍)"""
        gemini_service = self.session_manager.get_gemini_service()

        # Gemini 서비스 초기화 확인
        if not gemini_service.is_initialized:
            success, message = gemini_service.initialize()
            if not success:
                MessageComponent.render_error(message)
                return

        # 스트리밍 응답을 위한 플레이스홀더
        response_placeholder = st.empty()
        full_response = ""

        with st.spinner("AI가 스트리밍 중..."):
            for chunk in gemini_service.process_prompt_stream(prompt):
                full_response += chunk
                response_placeholder.markdown(f"**AI 응답:** {full_response}")

        # 채팅 히스토리에 추가
        self.session_manager.add_chat_message(prompt, full_response)

        # JSON 파싱 시도
        try:
            # 응답에서 JSON 추출
            json_text = self._extract_json_from_response(full_response)
            if json_text:
                import json
                result_dict = json.loads(json_text)
                llm_response = LLMResponse.from_dict(result_dict)
                self._handle_llm_response(llm_response, prompt)
            else:
                MessageComponent.render_info(full_response)
        except Exception as e:
            MessageComponent.render_info(full_response)

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
        """LLM 응답 처리"""
        if llm_response.is_error():
            MessageComponent.render_error(llm_response.error)
        elif llm_response.is_update():
            # 현재 회의 정보 업데이트
            current_meeting = self.session_manager.get_current_meeting()
            updated_meeting = MeetingService.update_meeting_from_llm_response(
                current_meeting, llm_response
            )
            self.session_manager.set_current_meeting(updated_meeting)
            MessageComponent.render_success(
                llm_response.message or "회의 정보가 업데이트되었습니다!"
            )
            st.rerun()
        else:
            MessageComponent.render_info(
                llm_response.message or "요청을 처리했습니다."
            )
    
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