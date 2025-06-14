"""
참석자 관리 서비스
"""
from typing import List

from src.models.meeting import Meeting, Attendee, AttendeeRole
from src.api.employee_api import get_employee_api


class AttendeeService:
    """참석자 관리 서비스 클래스"""

    @staticmethod
    def search_employees(query: str) -> List[dict]:
        """임직원 검색"""
        emp_api = get_employee_api()

        # 이름으로 검색
        employees = emp_api.search_by_name(query)

        # 팀으로 검색도 시도
        if not employees:
            teams = emp_api.get_all_teams()
            matching_teams = [team for team in teams if query in team]
            if matching_teams:
                employees = emp_api.get_team_members(matching_teams[0])

        return [emp.to_dict() for emp in employees]

    @staticmethod
    def add_attendee(meeting: Meeting, employee_id: str, role: AttendeeRole) -> bool:
        """참석자 추가"""
        emp_api = get_employee_api()
        employee = emp_api.get_employee_by_id(employee_id)

        if not employee:
            return False

        # 이미 있는지 확인
        if any(att.employee_id == employee_id for att in meeting.attendees):
            return False

        attendee = Attendee(
            employee_id=employee.id,
            name=employee.name,
            team=employee.team,
            role=role
        )

        meeting.attendees.append(attendee)
        return True

    @staticmethod
    def remove_attendees(meeting: Meeting, employee_ids: List[str]) -> int:
        """참석자 제거"""
        original_count = len(meeting.attendees)
        meeting.attendees = [
            att for att in meeting.attendees
            if att.employee_id not in employee_ids
        ]
        return original_count - len(meeting.attendees)

    @staticmethod
    def update_attendee_role(meeting: Meeting, employee_id: str, new_role: AttendeeRole) -> bool:
        """참석자 역할 업데이트"""
        for attendee in meeting.attendees:
            if attendee.employee_id == employee_id:
                attendee.role = new_role
                return True
        return False