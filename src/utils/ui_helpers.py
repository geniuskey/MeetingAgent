# src/utils/ui_helpers.py
"""
UI 헬퍼 함수들
"""
import streamlit as st


def render_success_message(message: str):
    """성공 메시지 렌더링"""
    st.markdown(f"""
    <div class="success-message">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)


def render_error_message(message: str):
    """에러 메시지 렌더링"""
    st.markdown(f"""
    <div class="error-message">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)


def render_info_message(message: str):
    """정보 메시지 렌더링"""
    st.info(message)


def render_header(is_edit_mode: bool = False):
    """헤더 렌더링"""
    title = "📝 회의 수정" if is_edit_mode else "📝 회의 예약"
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
    </div>
    """, unsafe_allow_html=True)
