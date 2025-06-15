"""
임직원 조회 Mock API
"""
import random
from typing import List, Optional
from src.models.employee import Employee


class MockEmployeeAPI:
    """임직원 조회 시스템 Mock API"""

    def __init__(self):
        self.employees = self._generate_sample_employees()

    def _generate_sample_employees(self) -> List[Employee]:
        """샘플 임직원 데이터 생성 (30명, 역할 포함)"""
        teams = ["개발팀", "기획팀", "디자인팀", "마케팅팀", "영업팀", "인사팀", "재무팀"]
        roles = ["사장", "부사장", "상무", "Master", "PL", "그룹장", "TL", "파트장", ""]

        # 역할별 인원 분배
        role_distribution = {
            "사장": 1,
            "부사장": 1,
            "상무": 2,
            "Master": 2,
            "PL": 3,
            "그룹장": 3,
            "TL": 5,
            "파트장": 5,
            "": 8  # 일반 실무자
        }

        names = [
            "김철수", "이영희", "박민수", "정지영", "최윤호", "한소영", "임대현", "조미영",
            "강준호", "윤서연", "장동혁", "서지은", "김태원", "박수진", "이현우", "정예린",
            "최성민", "한지영", "임준혁", "조윤서", "강민지", "윤태현", "장소영", "서현준",
            "김지영", "박태윤", "이민서", "정현우", "최소영", "한태현", "임지은", "조민혁"
        ]

        employees = []
        name_idx = 0

        # 역할별로 임직원 생성
        for role, count in role_distribution.items():
            for _ in range(count):
                if name_idx >= len(names):
                    break

                name = names[name_idx]
                team = random.choice(teams)

                # 임원급은 특정 팀에 배치
                if role in ["사장", "부사장"]:
                    team = "경영진"
                elif role == "상무":
                    team = random.choice(["개발팀", "영업팀"])
                elif role == "Master":
                    team = random.choice(["개발팀", "기획팀"])

                employees.append(Employee(
                    id=f"emp_{name_idx + 1:03d}",
                    name=name,
                    team=team,
                    role=role,
                    email=f"{name.lower()}@company.com"
                ))
                name_idx += 1

        return employees

    def search_by_name(self, name: str) -> List[Employee]:
        """이름으로 임직원 검색"""
        return [emp for emp in self.employees if name in emp.name]

    def get_team_members(self, team: str) -> List[Employee]:
        """팀별 임직원 조회"""
        return [emp for emp in self.employees if emp.team == team]

    def get_employee_by_id(self, employee_id: str) -> Optional[Employee]:
        """ID로 임직원 조회"""
        for emp in self.employees:
            if emp.id == employee_id:
                return emp
        return None

    def get_all_employees(self) -> List[Employee]:
        """전체 임직원 조회"""
        return self.employees

    def get_all_teams(self) -> List[str]:
        """전체 팀 목록 조회"""
        return list(set(emp.team for emp in self.employees))

    def get_employees_by_role(self, role: str) -> List[Employee]:
        """역할별 임직원 조회"""
        return [emp for emp in self.employees if emp.role == role]

    def get_executives(self) -> List[Employee]:
        """임원급 임직원 조회"""
        return [emp for emp in self.employees if emp.is_executive()]

    def get_leaders(self) -> List[Employee]:
        """리더급 임직원 조회"""
        return [emp for emp in self.employees if emp.is_leader()]


# 싱글톤 인스턴스
_employee_api_instance = None


def get_employee_api() -> MockEmployeeAPI:
    """임직원 API 인스턴스 반환"""
    global _employee_api_instance
    if _employee_api_instance is None:
        _employee_api_instance = MockEmployeeAPI()
    return _employee_api_instance
