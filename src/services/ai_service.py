"""
AI/LLM 서비스 (우선순위 알고리즘 통합)
"""
from google import genai
from datetime import datetime, timedelta
import json
import re
from typing import Optional, Iterator, Tuple

from src.utils.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, SYSTEM_PROMPT
from src.models.meeting import Meeting
from src.services.schedule_priority_service import SchedulePriorityService


class AIService:
    """AI/LLM 서비스 클래스"""

    def __init__(self):
        self.client = None
        self.is_initialized = False
        self.error_message = None
        self.priority_service = SchedulePriorityService()

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
        """프롬프트 처리 (우선순위 알고리즘 통합)"""
        if not self.client:
            def error_generator():
                yield "AI 클라이언트가 초기화되지 않았습니다."

            return None, error_generator()

        # 일정 제안 요청인지 확인
        if self._is_time_suggestion_request(prompt):
            return self._handle_time_suggestion(prompt, current_meeting)

        try:
            # 기존 프롬프트 처리 로직
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
                response_text = full_response

            # RESPONSE 부분을 단어별로 스트리밍
            def response_generator():
                import time
                if response_text:
                    words = response_text.split()
                    for word in words:
                        yield word + " "
                        time.sleep(0.05)
                else:
                    yield "응답을 처리했습니다."

            return action_data, response_generator()

        except Exception as e:
            def error_generator():
                yield f"AI 처리 중 오류가 발생했습니다: {str(e)}"

            return None, error_generator()

    def _is_time_suggestion_request(self, prompt: str) -> bool:
        """시간 제안 요청인지 확인"""
        suggestion_keywords = [
            "시간 제안", "언제", "적절한 시간", "최적 시간", "시간 추천",
            "일정 제안", "가능한 시간", "시간을 잡아", "언제가 좋을까"
        ]
        return any(keyword in prompt for keyword in suggestion_keywords)

    def _handle_time_suggestion(self, prompt: str, current_meeting: Meeting) -> tuple[dict, Iterator[str]]:
        """시간 제안 처리"""
        try:
            # 목표 날짜 추출 (기본값: 1주일 후)
            target_date = self._extract_target_date(prompt)

            # 회의 시간 추출 (기본값: 1시간)
            duration = self._extract_duration(prompt)

            # 우선순위 알고리즘으로 시간 제안
            suggestions = self.priority_service.suggest_meeting_times(
                current_meeting, target_date, duration
            )

            if not suggestions:
                def no_suggestion_generator():
                    yield "죄송합니다. 해당 기간에 적절한 시간을 찾을 수 없습니다."

                return None, no_suggestion_generator()

            best_suggestion = suggestions[0]

            # ACTION 데이터 생성
            action_data = {
                "action": "update",
                "updates": {
                    "start_time": best_suggestion.start_time.strftime("%Y-%m-%d %H:%M"),
                    "end_time": best_suggestion.end_time.strftime("%Y-%m-%d %H:%M")
                },
                "requires_confirmation": True,
                "action_description": f"회의 시간을 {best_suggestion.start_time.strftime('%m월 %d일 %H:%M')}로 설정"
            }

            # 응답 생성
            def suggestion_generator():
                import time

                response_parts = [
                    f"✅ 최적의 회의 시간을 찾았습니다!\n\n",
                    f"🕐 **추천 시간**: {best_suggestion.start_time.strftime('%Y년 %m월 %d일 %H:%M')} - {best_suggestion.end_time.strftime('%H:%M')}\n",
                    f"📊 **참석률**: {best_suggestion.attendance_rate:.1%} ({best_suggestion.available_attendees}/{best_suggestion.total_required_attendees}명)\n",
                    f"⭐ **우선순위 점수**: {best_suggestion.priority_score:.1f}/100\n\n"
                ]

                if best_suggestion.time_preference_bonus:
                    response_parts.append("✨ 선호 시간대입니다 (오전 10시 또는 오후 3시)\n")

                if best_suggestion.target_date_proximity >= 0.8:
                    response_parts.append("📅 목표 날짜에 매우 근접합니다\n")

                if best_suggestion.lunch_time_penalty:
                    response_parts.append("⚠️ 점심시간과 겹치는 점 참고해주세요\n")

                if best_suggestion.conflicted_attendees:
                    response_parts.append(f"⚠️ {len(best_suggestion.conflicted_attendees)}명의 일정 충돌이 있습니다\n")

                response_parts.append(f"\n**다른 후보 시간들:**\n")
                for i, suggestion in enumerate(suggestions[1:4], 2):
                    response_parts.append(
                        f"{i}. {suggestion.start_time.strftime('%m/%d %H:%M')} (점수: {suggestion.priority_score:.1f})\n")

                # 스트리밍 효과
                for part in response_parts:
                    words = part.split()
                    for word in words:
                        yield word + " "
                        time.sleep(0.03)

            return action_data, suggestion_generator()

        except Exception as e:
            def error_generator():
                yield f"시간 제안 처리 중 오류가 발생했습니다: {str(e)}"

            return None, error_generator()

    def _extract_target_date(self, prompt: str) -> datetime:
        """프롬프트에서 목표 날짜 추출"""
        now = datetime.now()

        # 날짜 키워드 매핑
        if "내일" in prompt:
            return now + timedelta(days=1)
        elif "다음 주" in prompt or "다음주" in prompt:
            days_ahead = 7 - now.weekday()
            return now + timedelta(days=days_ahead)
        elif "이번 주" in prompt or "이번주" in prompt:
            return now + timedelta(days=1)
        elif "다음 달" in prompt or "다음달" in prompt:
            return now + timedelta(days=30)

        # 요일 키워드 확인
        weekdays = {
            "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3,
            "금요일": 4, "토요일": 5, "일요일": 6
        }

        for day_name, day_num in weekdays.items():
            if day_name in prompt:
                days_ahead = (day_num - now.weekday()) % 7
                if days_ahead == 0:  # 오늘이 해당 요일이면 다음 주
                    days_ahead = 7
                return now + timedelta(days=days_ahead)

        # 기본값: 1주일 후
        return now + timedelta(days=7)

    def _extract_duration(self, prompt: str) -> int:
        """프롬프트에서 회의 시간 추출 (시간 단위)"""
        # 시간 키워드 확인
        if "30분" in prompt or "반시간" in prompt:
            return 1  # 30분은 0.5시간이지만 최소 1시간으로
        elif "1시간" in prompt or "한시간" in prompt:
            return 1
        elif "2시간" in prompt or "두시간" in prompt:
            return 2
        elif "3시간" in prompt or "세시간" in prompt:
            return 3
        elif "반나절" in prompt:
            return 4
        elif "하루" in prompt or "종일" in prompt:
            return 8

        # 기본값: 1시간
        return 1

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
            r'```json\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'\{.*\}',
        ]

        for pattern in json_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)

        return None
