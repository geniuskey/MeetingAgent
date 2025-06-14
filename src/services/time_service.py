"""
시간 관리 서비스
"""
from datetime import datetime, timedelta
from src.utils.config import DEFAULT_MEETING_DURATION


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
        """시작 시간에서 기본 종료 시간 계산 (1시간 후)"""
        return start_time + DEFAULT_MEETING_DURATION

    @staticmethod
    def add_default_duration(start_time: datetime) -> datetime:
        """시작 시간에 기본 회의 시간(1시간) 추가"""
        return start_time + DEFAULT_MEETING_DURATION

    @staticmethod
    def format_datetime_for_display(dt: datetime) -> str:
        """표시용 날짜/시간 포맷"""
        return dt.strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def format_time_for_display(dt: datetime) -> str:
        """표시용 시간 포맷"""
        return dt.strftime('%H:%M')

    @staticmethod
    def format_date_for_display(dt: datetime) -> str:
        """표시용 날짜 포맷"""
        return dt.strftime('%Y-%m-%d')