"""
레이아웃 컴포넌트
"""
import streamlit as st


class HeaderComponent:
    """헤더 컴포넌트"""

    @staticmethod
    def render(is_edit_mode: bool = False):
        """헤더 렌더링"""
        title = "📝 회의 수정" if is_edit_mode else "📝 회의 예약"
        st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
        </div>
        """, unsafe_allow_html=True)


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