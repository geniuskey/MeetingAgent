"""
서비스 로직 모듈
"""
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import json
import re
from typing import Optional, Iterator, Tuple

from config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, SYSTEM_PROMPT, DEFAULT_MEETING_DURATION, TIME_STEP
from models import Meeting, LLMResponse


class GeminiService:
    """Gemini AI 서비스 클래스"""

    def __init__(self):
        self.client = None
        self.is_initialized = False
        self.error_message = None

    def initialize(self) -> tuple[bool, str]:
        """Gemini API 초기화"""
        if not GOOGLE_API_KEY:
            self.error_message = "환경변수 GOOGLE_API_KEY가 설정되지 않았습니다."
            return False, self.error_message

        try:
            self.client = genai.Client(api_key=GOOGLE_API_KEY)
            self.is_initialized = True
            return True, "모델이 성공적으로 초기화되었습니다."
        except Exception as e:
            self.error_message = f"Google GenAI 클라이언트 설정 오류: {str(e)}"
            return False, self.error_message

    def get_client(self):
        """클라이언트 반환"""
        if not self.is_initialized:
            self.initialize()
        return self.client if self.is_initialized else None

    def process_prompt(self, prompt: str) -> LLMResponse:
        """프롬프트 처리 (non-streaming)"""
        if not self.client:
            return LLMResponse(action="error", error="Google GenAI 클라이언트가 초기화되지 않았습니다.")

        try:
            full_prompt = SYSTEM_PROMPT.format(
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M")
            ) + f"\n\n사용자 입력: {prompt}"

            # Google GenAI API 호출
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=full_prompt
            )

            if not response or not response.text:
                return LLMResponse(action="error", error="AI로부터 응답을 받지 못했습니다.")

            # JSON 응답 파싱
            response_text = response.text.strip()
            json_text = self._extract_json(response_text)

            if not json_text:
                json_text = response_text

            # JSON 파싱 시도
            try:
                result_dict = json.loads(json_text)
                return LLMResponse.from_dict(result_dict)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트 응답으로 처리
                return LLMResponse(action="message", message=response_text)

        except Exception as e:
            return LLMResponse(action="error", error=f"LLM 처리 중 오류가 발생했습니다: {str(e)}")

    def process_prompt_stream_with_action(self, prompt: str) -> tuple[Optional[dict], Iterator[str]]:
        """프롬프트 처리 (action 분리 + response 스트리밍)"""
        if not self.client:
            def error_generator():
                yield "Google GenAI 클라이언트가 초기화되지 않았습니다."
            return None, error_generator()

        try:
            full_prompt = SYSTEM_PROMPT.format(
                current_time=datetime.now().strftime("%Y-%m-%d %H:%M")
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
                yield f"LLM 처리 중 오류가 발생했습니다: {str(e)}"

            return None, error_generator()
    
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


class MeetingService:
    """회의 관리 서비스 클래스"""
    
    @staticmethod
    def create_default_meeting() -> Meeting:
        """기본 회의 생성"""
        now = datetime.now()
        current_minute = now.minute
        
        # 30분 단위로 반올림
        if current_minute < 30:
            rounded_minute = 0
        else:
            rounded_minute = 30

        start_time = now.replace(minute=rounded_minute, second=0, microsecond=0)
        end_time = start_time + DEFAULT_MEETING_DURATION

        return Meeting(
            title='',
            start_time=start_time,
            end_time=end_time,
            attendees='',
            content=''
        )
    
    @staticmethod
    def update_meeting_from_llm_response(meeting: Meeting, llm_response: LLMResponse) -> Meeting:
        """LLM 응답으로 회의 업데이트"""
        if not llm_response.is_update():
            return meeting
        
        updates = llm_response.updates
        updated_meeting = Meeting(
            title=updates.get('title', meeting.title),
            start_time=meeting.start_time,
            end_time=meeting.end_time,
            attendees=updates.get('attendees', meeting.attendees),
            content=updates.get('content', meeting.content)
        )
        
        # 시간 필드 업데이트
        if 'start_time' in updates:
            try:
                updated_meeting.start_time = datetime.strptime(updates['start_time'], "%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                pass
        
        if 'end_time' in updates:
            try:
                updated_meeting.end_time = datetime.strptime(updates['end_time'], "%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                pass
        
        return updated_meeting
    
    @staticmethod
    def validate_meeting(meeting: Meeting) -> tuple[bool, str]:
        """회의 유효성 검사"""
        if not meeting.title.strip():
            return False, "회의 제목을 입력해주세요."
        
        if meeting.start_time >= meeting.end_time:
            return False, "종료 시간은 시작 시간보다 늦어야 합니다."
        
        return True, "유효한 회의입니다."


class TimeService:
    """시간 관리 서비스 클래스"""
    
    @staticmethod
    def round_to_nearest_30_minutes(dt: datetime) -> datetime:
        """30분 단위로 반올림"""
        minute = dt.minute
        if minute < 30:
            rounded_minute = 0
        else:
            rounded_minute = 30
        
        return dt.replace(minute=rounded_minute, second=0, microsecond=0)
    
    @staticmethod
    def get_default_end_time(start_time: datetime) -> datetime:
        """시작 시간에서 기본 종료 시간 계산"""
        return start_time + DEFAULT_MEETING_DURATION
    
    @staticmethod
    def format_datetime_for_display(dt: datetime) -> str:
        """표시용 날짜/시간 포맷"""
        return dt.strftime('%Y-%m-%d %H:%M')
    
    @staticmethod
    def format_time_for_display(dt: datetime) -> str:
        """표시용 시간 포맷"""
        return dt.strftime('%H:%M')