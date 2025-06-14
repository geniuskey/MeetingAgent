"""
AI 채팅 컴포넌트
"""
import streamlit as st
from typing import Dict, Any

from src.models.chat import ChatStorage
from src.services.ai_service import AIService
from src.utils.config import MAX_CHAT_HISTORY_DISPLAY


class AIAssistantComponent:
    """AI 어시스턴트 컴포넌트"""

    def __init__(self, ai_service: AIService, chat_storage: ChatStorage):
        self.ai_service = ai_service
        self.chat_storage = chat_storage

    def render(self) -> Dict[str, Any]:
        """AI 어시스턴트 렌더링"""
        st.subheader("🤖 AI 어시스턴트")

        # 채팅 히스토리 표시
        messages = self.chat_storage.get_recent_messages(MAX_CHAT_HISTORY_DISPLAY)

        # 채팅 메시지 컨테이너 (스크롤 가능한 영역)
        chat_container = st.container(height=300)

        with chat_container:
            if messages:
                for chat in messages:
                    with st.chat_message("user"):
                        st.markdown(chat.user)
                    with st.chat_message("assistant"):
                        st.markdown(chat.assistant)
            else:
                with st.chat_message("assistant"):
                    st.markdown("""
                    안녕하세요! 회의 일정 관리를 도와드리는 AI 어시스턴트입니다. 
                    
                    **예시:**
                    - "내일 오후 2시에 팀 미팅 잡아줘"
                    - "김철수님을 참석자에 추가해줘"
                    - "회의 시간을 1시간 연장해줘"
                    - "안녕하세요" (일반 대화도 가능해요!)
                    """)

        # 채팅 입력 (채팅 컨테이너 밖에 배치)
        prompt = st.chat_input("자연어로 회의를 예약하거나 질문해주세요...")

        # 초기화 버튼
        # 고유 키 생성
        if 'clear_btn_counter' not in st.session_state:
            st.session_state.clear_btn_counter = 0
        st.session_state.clear_btn_counter += 1
        clear_clicked = st.button("🗑️ 채팅 초기화", key=f"clear_{st.session_state.clear_btn_counter}", use_container_width=True)

        return {
            'prompt': prompt,
            'send_clicked': bool(prompt),
            'clear_clicked': clear_clicked
        }