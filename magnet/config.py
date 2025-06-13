"""
설정 및 상수 모듈
"""
import os
from datetime import timedelta

# API 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # google-genai 라이브러리는 GOOGLE_API_KEY를 사용
GEMINI_MODEL_NAME = 'gemini-2.0-flash-001'

# 시간 설정
TIME_STEP = timedelta(minutes=30)
DEFAULT_MEETING_DURATION = timedelta(hours=1)

# UI 설정
MAX_MEETINGS_DISPLAY = 10
MAX_CHAT_HISTORY_DISPLAY = 5
CONTENT_PREVIEW_LENGTH = 50

# 페이지 설정
PAGE_CONFIG = {
    "page_title": "AI Meeting Booking System",
    "page_icon": "📅",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Quill 에디터 툴바 설정
QUILL_TOOLBAR = [
    ['bold', 'italic', 'underline', 'strike'],
    ['blockquote', 'code-block'],
    [{'header': 1}, {'header': 2}],
    [{'list': 'ordered'}, {'list': 'bullet'}],
    [{'script': 'sub'}, {'script': 'super'}],
    [{'indent': '-1'}, {'indent': '+1'}],
    [{'direction': 'rtl'}],
    [{'size': ['small', False, 'large', 'huge']}],
    [{'header': [1, 2, 3, 4, 5, 6, False]}],
    [{'color': []}, {'background': []}],
    [{'font': []}],
    [{'align': []}],
    ['clean']
]

# LLM 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 회의 예약 시스템의 AI 어시스턴트입니다. 사용자의 자연어 입력을 분석하여 두 부분으로 응답해주세요:

1. ACTION 부분: 회의 예약 폼의 필드를 업데이트하는 JSON (사용자에게 보이지 않음)
2. RESPONSE 부분: 사용자에게 보여줄 친근한 답변 (스트리밍으로 표시됨)

사용 가능한 필드:
- title: 회의 제목
- start_time: 시작 시간 (YYYY-MM-DD HH:MM 형식)
- end_time: 종료 시간 (YYYY-MM-DD HH:MM 형식)
- attendees: 참석자 목록 (쉼표로 구분)
- content: 회의 내용/안건
- action: 수행할 작업 ("update", "clear", "save", "load")

응답 형식:
ACTION:
{{
    "action": "update",
    "updates": {{
        "title": "값",
        "start_time": "2024-01-01 14:00",
        "end_time": "2024-01-01 15:00",
        "attendees": "김철수, 이영희",
        "content": "회의 내용"
    }}
}}

RESPONSE:
네, 회의 정보를 업데이트했습니다. [사용자에게 보여줄 친근한 답변]

현재 시간: {current_time}
"""