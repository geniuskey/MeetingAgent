"""
AI/LLM 서비스
"""
from google import genai
from datetime import datetime
import json
import re
from typing import Optional, Iterator, Tuple

from src.utils.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, SYSTEM_PROMPT
from src.models.meeting import Meeting


class AIService:
    """AI/LLM 서비스 클래스"""

    def __init__(self):
        self.client = None
        self.is_initialized = False
        self.error_message = None

    def initialize(self) -> tuple[bool, str]:
        """AI API 초기화"""
        if not GOOGLE_API_KEY:
            self.error_message = "환경변수 GOOGLE_API_KEY가 설정되지 않았습니다."
            return False, self.error_message

        try:
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
            self.is_initialized = True
            return True, "AI 모델이 성공적으로 초기화되었습니다."
        except Exception as e:
            self.error_message = f"Google GenAI 클라이언트 설정 오류: {str(e)}"
            return False, self.error_message

    def process_prompt_stream(self, prompt: str, current_meeting: Meeting) -> tuple[Optional[dict], Iterator[str]]:
        """프롬프트 처리 (action 분리 + response 스트리밍)"""
        if not self.client:
            def error_generator():
                yield "AI 클라이언트가 초기화되지 않았습니다."

            return None, error_generator()

        try:
            # 현재 회의 정보를 컨텍스트에 포함
            meeting_context = self._get_meeting_context(current_meeting)

            full_prompt = SYSTEM_PROMPT.format(
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                current_meeting=meeting_context
            ) + f"\n\n사용자 입력: {prompt}"

            # Google GenAI 스트리밍 API 호출
            full_response = ""
            for chunk in self.client.models.generate_content_stream(
                    model=GEMINI_MODEL_NAME,
                    contents=full_prompt
            ):
                if chunk.text:
                    full_response += chunk.text

            # ACTION과 RESPONSE 분리
            action_data = None
            response_text = ""

            if "ACTION:" in full_response and "RESPONSE:" in full_response:
                parts = full_response.split("RESPONSE:")
                action_part = parts[0].replace("ACTION:", "").strip()
                response_text = parts[1].strip()

                # ACTION JSON 파싱
                try:
                    json_text = self._extract_json(action_part)
                    if json_text:
                        action_data = json.loads(json_text)
                except json.JSONDecodeError:
                    pass
            else:
                # 구분자가 없으면 전체를 response로 처리
                response_text = full_response

            # RESPONSE 부분을 단어별로 스트리밍
            def response_generator():
                import time
                if response_text:
                    words = response_text.split()
                    for word in words:
                        yield word + " "
                        time.sleep(0.05)  # 타이핑 효과
                else:
                    yield "응답을 처리했습니다."

            return action_data, response_generator()

        except Exception as e:
            def error_generator():
                yield f"AI 처리 중 오류가 발생했습니다: {str(e)}"

            return None, error_generator()

    def _get_meeting_context(self, meeting: Meeting) -> str:
        """현재 회의 컨텍스트 생성"""
        attendees_info = []
        for attendee in meeting.attendees:
            attendees_info.append(f"- {attendee.name} ({attendee.team}, {attendee.role.value})")

        attendees_str = "\n".join(attendees_info) if attendees_info else "없음"

        return f"""
현재 회의 정보:
- 제목: {meeting.title}
- 시작시간: {meeting.get_formatted_start_time()}
- 종료시간: {meeting.get_formatted_end_time()}
- 참석자:
{attendees_str}
- 내용: {meeting.content[:100]}...
- 편집모드: {'수정' if meeting.is_edit_mode else '신규'}
"""

    def _extract_json(self, text: str) -> Optional[str]:
        """텍스트에서 JSON 블록 추출"""
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