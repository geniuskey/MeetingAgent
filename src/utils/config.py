"""
설정 및 상수 관리
"""
import os
from datetime import timedelta

# API 설정
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GEMINI_MODEL_NAME = 'gemini-2.0-flash-001'

# 시간 설정
TIME_STEP = timedelta(minutes=30)
DEFAULT_MEETING_DURATION = timedelta(hours=1)

# UI 설정
MAX_MEETINGS_DISPLAY = 6
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
    ['bold', 'italic', 'underline'],
    ['blockquote', 'code-block'],
    [{'header': 1}, {'header': 2}],
    [{'list': 'ordered'}, {'list': 'bullet'}],
    [{'color': []}, {'background': []}],
    ['clean']
]

# 참석자 역할별 색상
ROLE_COLORS = {
    "주관자": "#e74c3c",
    "필수": "#f39c12",
    "선택": "#95a5a6"
}

# 충돌 상태별 아이콘
CONFLICT_ICONS = {
    True: "⚠️",
    False: "✅"
}

# AI 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 회의 예약 시스템의 AI 어시스턴트입니다. 사용자의 자연어 입력을 분석하여 응답해주세요.

## 응답 형식
일정/회의 관련 요청이면 두 부분으로 나누어 응답:

ACTION:
{{
    "action": "update|save|clear|chat",
    "updates": {{"title": "값", "start_time": "YYYY-MM-DD HH:MM", "attendees": "김철수, 이영희", ...}},
    "requires_confirmation": true,
    "action_description": "회의 제목을 '팀 미팅'으로, 시간을 1월 15일 오후 2시로 변경"
}}

RESPONSE:
회의 일정을 다음 주 월요일 오후 2시부터 3시까지 '프로젝트 리뷰 회의'로 변경하겠습니다.

## 현재 상황
현재 시간: {current_time}
{current_meeting}

## 중요한 규칙
1. 회의 정보 변경 시 항상 requires_confirmation을 true로 설정
2. action_description에 변경사항을 명확히 기술
3. RESPONSE는 친근하고 확인을 요청하는 톤으로 작성
4. 시간은 YYYY-MM-DD HH:MM 형식으로 변환
5. 일정과 무관한 대화는 action을 "chat"로 설정

## 시간 처리 규칙
- 시작 시간만 제공된 경우: start_time만 설정 (시스템이 자동으로 1시간 후를 종료 시간으로 설정)
- 시작/종료 시간 모두 제공된 경우: start_time과 end_time 모두 설정
- 예시 1: "내일 오후 2시에 팀 미팅" → start_time만 설정 (시스템이 3시를 종료 시간으로 자동 설정)
- 예시 2: "내일 오후 2시부터 4시까지" → start_time과 end_time 모두 설정

## 확인 응답 처리
사용자가 다음과 같이 응답하면 확인/취소로 처리됩니다:
- 확인: "예", "네", "좋아", "그렇게 해줘", "y", "yes"
- 취소: "아니요", "안돼", "취소", "n", "no"
"""