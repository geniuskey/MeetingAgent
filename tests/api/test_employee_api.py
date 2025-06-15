# tests/api/test_employee_api.py
import pytest
from src.api.employee_api import get_employee_api, MockEmployeeAPI


class TestMockEmployeeAPI:

    def setup_method(self):
        """테스트 설정"""
        self.api = get_employee_api()

    def test_employee_data_generation(self):
        """임직원 데이터 생성 테스트"""
        employees = self.api.employees

        # 총 인원 확인 (40명 이상)
        assert len(employees) >= 40, f"임직원이 {len(employees)}명만 생성됨"

        # 역할 분포 확인
        executives = [emp for emp in employees if emp.role in ["사장", "부사장", "상무", "Master"]]
        leaders = [emp for emp in employees if emp.role in ["PL", "그룹장", "TL", "파트장"]]
        specialists = [emp for emp in employees if emp.role in ["CA", "EA", "DXA", "MCA", "MEA", "MDXA"]]
        regulars = [emp for emp in employees if emp.role == ""]

        assert len(executives) >= 4, "임원급이 부족합니다"
        assert len(leaders) >= 8, "리더급이 부족합니다"
        assert len(specialists) >= 6, "전문직이 부족합니다"
        assert len(regulars) >= 20, "일반직이 부족합니다"

        print(f"임직원 분포: 임원급 {len(executives)}명, 리더급 {len(leaders)}명, "
              f"전문직 {len(specialists)}명, 일반직 {len(regulars)}명")

    def test_search_functionality(self):
        """검색 기능 테스트"""
        # 이름 검색
        kim_results = self.api.search_by_name("김")
        assert len(kim_results) > 0, "김씨 검색 결과가 없습니다"

        lee_results = self.api.search_by_name("이")
        assert len(lee_results) > 0, "이씨 검색 결과가 없습니다"

        # 정확한 이름 검색
        exact_results = self.api.search_by_name("김대표")
        assert len(exact_results) == 1, "정확한 이름 검색이 실패했습니다"
        assert exact_results[0].name == "김대표"

    def test_team_functionality(self):
        """팀별 조회 테스트"""
        # 개발팀 조회
        dev_team = self.api.get_team_members("개발팀")
        assert len(dev_team) > 0, "개발팀 멤버가 없습니다"

        # 경영진 조회
        executives = self.api.get_team_members("경영진")
        assert len(executives) >= 4, "경영진이 부족합니다"

        # 모든 팀 목록
        all_teams = self.api.get_all_teams()
        expected_teams = ["경영진", "개발팀", "기획팀", "디자인팀", "마케팅팀", "영업팀", "인사팀", "재무팀"]
        for team in expected_teams:
            assert team in all_teams, f"{team}이 팀 목록에 없습니다"

    def test_employee_by_id(self):
        """ID로 임직원 조회 테스트"""
        # 첫 번째 임직원 조회
        first_emp = self.api.get_employee_by_id("emp_001")
        assert first_emp is not None, "첫 번째 임직원을 찾을 수 없습니다"
        assert first_emp.id == "emp_001"

        # 존재하지 않는 ID
        non_existent = self.api.get_employee_by_id("emp_999")
        assert non_existent is None, "존재하지 않는 임직원이 반환되었습니다"
