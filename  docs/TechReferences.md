# 🔧 AI Meeting Booking System - 기술 참고 문서

> **해커톤 개발자를 위한 빠른 참고 자료**

---

## 📚 **핵심 코드 템플릿**

### **1. 기본 Streamlit 앱 구조**

```python
# app.py
import streamlit as st
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="AI Meeting Booking System",
    page_icon="📅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 메인 앱 클래스
class MeetingBookingApp:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        if 'current_meeting' not in st.session_state:
            st.session_state.current_meeting = self.create_default_meeting()
    
    def create_default_meeting(self):
        return {
            'title': '',
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'attendees': []
        }
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown("### 🤖 AI 어시스턴트")
            prompt = st.chat_input("회의를 예약해보세요...")
            return prompt
    
    def render_main(self):
        st.markdown("## 📅 회의 예약")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_meeting_form()
        
        with col2:
            self.render_attendee_list()
    
    def render_meeting_form(self):
        title = st.text_input("회의 제목", value=st.session_state.current_meeting['title'])
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("날짜")
            start_time = st.time_input("시작 시간")
        with col2:
            end_time = st.time_input("종료 시간")
        
        if st.button("💾 회의 저장"):
            st.success("회의가 저장되었습니다!")
    
    def render_attendee_list(self):
        st.markdown("### 👥 참석자")
        
        # 참석자 추가
        new_attendee = st.text_input("참석자 이름")
        if st.button("➕ 추가"):
            if new_attendee:
                st.session_state.current_meeting['attendees'].append(new_attendee)
                st.rerun()
        
        # 참석자 목록
        for i, attendee in enumerate(st.session_state.current_meeting['attendees']):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 {attendee}")
            with col2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.current_meeting['attendees'].pop(i)
                    st.rerun()
    
    def run(self):
        prompt = self.render_sidebar()
        self.render_main()
        
        if prompt:
            # AI 처리 로직
            st.sidebar.success(f"AI: {prompt}을 처리했습니다!")

# 실행
if __name__ == "__main__":
    app = MeetingBookingApp()
    app.run()
```

### **2. Google GenAI 연동**

```python
# src/services/ai_service.py
from google import genai
import json
import os

class AIService:
    def __init__(self):
        self.client = None
        self.api_key = os.getenv('GOOGLE_API_KEY')
    
    def initialize(self):
        if not self.api_key:
            return False, "GOOGLE_API_KEY 환경변수가 설정되지 않았습니다."
        
        try:
            self.client = genai.Client(api_key=self.api_key)
            return True, "AI 서비스 초기화 완료"
        except Exception as e:
            return False, f"초기화 실패: {str(e)}"
    
    def process_meeting_request(self, prompt, current_meeting):
        system_prompt = f"""
        당신은 회의 예약 AI 어시스턴트입니다.
        
        현재 회의 정보:
        - 제목: {current_meeting.get('title', '')}
        - 참석자: {', '.join(current_meeting.get('attendees', []))}
        
        사용자 요청: {prompt}
        
        다음 형식으로 응답하세요:
        ACTION: {{"action": "update", "updates": {{"title": "새 제목", "attendees": ["김철수", "이영희"]}}}}
        RESPONSE: 사용자에게 보여줄 친근한 응답
        """
        
        try:
            response = ""
            for chunk in self.client.models.generate_content_stream(
                model='gemini-2.0-flash-001',
                contents=system_prompt
            ):
                if chunk.text:
                    response += chunk.text
            
            return self.parse_ai_response(response)
        except Exception as e:
            return None, f"AI 처리 실패: {str(e)}"
    
    def parse_ai_response(self, response):
        try:
            # ACTION과 RESPONSE 분리
            if "ACTION:" in response and "RESPONSE:" in response:
                parts = response.split("RESPONSE:")
                action_part = parts[0].replace("ACTION:", "").strip()
                response_part = parts[1].strip()
                
                # JSON 파싱
                action_data = json.loads(action_part)
                return action_data, response_part
            else:
                return None, response
        except:
            return None, response

# 사용 예시
ai_service = AIService()
success, message = ai_service.initialize()

if success:
    action, response = ai_service.process_meeting_request(
        "내일 오후 2시에 팀 미팅 잡아줘",
        {'title': '', 'attendees': []}
    )
```

### **3. Mock 데이터 생성**

```python
# src/api/employee_api.py
import random
from datetime import datetime, timedelta

class MockEmployeeAPI:
    def __init__(self):
        self.employees = self._generate_employees()
        self.schedules = self._generate_schedules()
    
    def _generate_employees(self):
        """40명의 현실적인 임직원 데이터 생성"""
        roles = {
            "임원급": ["사장", "부사장", "상무", "Master"],
            "팀장급": ["PL", "그룹장", "TL", "파트장"], 
            "전문직": ["CA", "EA", "DXA", "MCA"],
            "일반직": [""]
        }
        
        teams = ["개발팀", "기획팀", "디자인팀", "마케팅팀", "영업팀", "인사팀", "재무팀"]
        names = [
            "김대표", "이부사장", "박상무", "정마스터",  # 임원급
            "김철수", "이영희", "박민수", "정지영",      # 팀장급
            "최윤호", "한소영", "임대현", "조미영",      # 전문직
            "강준호", "윤서연", "장동혁", "서지은",      # 일반직
            "김태원", "박수진", "이현우", "정예린",
            "최성민", "한지영", "임준혁", "조윤서"
        ]
        
        employees = []
        for i, name in enumerate(names):
            if i < 4:  # 임원급
                role = roles["임원급"][i]
                team = "경영진"
            elif i < 12:  # 팀장급
                role = random.choice(roles["팀장급"])
                team = random.choice(teams)
            elif i < 16:  # 전문직
                role = random.choice(roles["전문직"])
                team = random.choice(teams)
            else:  # 일반직
                role = ""
                team = random.choice(teams)
            
            employees.append({
                'id': f'emp_{i+1:03d}',
                'name': name,
                'team': team,
                'role': role,
                'priority_level': self._get_priority_level(role)
            })
        
        return employees
    
    def _get_priority_level(self, role):
        """역할별 우선순위 레벨 (1이 가장 높음)"""
        if role in ["사장", "부사장", "상무", "Master"]:
            return 1
        elif role in ["PL", "그룹장"]:
            return 2
        elif role in ["TL", "파트장"]:
            return 3
        elif role in ["CA", "EA", "DXA", "MCA"]:
            return 4
        else:
            return 5
    
    def _generate_schedules(self):
        """3주간 현실적인 일정 생성"""
        schedules = []
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now() + timedelta(days=14)
        
        meeting_types = [
            "팀 미팅", "프로젝트 회의", "1:1 미팅", "전체 회의",
            "브레인스토밍", "코드 리뷰", "디자인 리뷰", "교육"
        ]
        
        for employee in self.employees:
            # 역할별 회의 빈도
            if employee['priority_level'] == 1:  # 임원급
                meetings_per_day = random.randint(4, 7)
            elif employee['priority_level'] <= 3:  # 팀장급
                meetings_per_day = random.randint(2, 5)
            else:  # 일반직
                meetings_per_day = random.randint(1, 3)
            
            current_date = start_date
            while current_date <= end_date:
                # 주말 제외
                if current_date.weekday() < 5:
                    for _ in range(meetings_per_day):
                        # 9-17시 사이 랜덤 시간
                        hour = random.randint(9, 16)
                        minute = random.choice([0, 30])
                        
                        meeting_start = current_date.replace(
                            hour=hour, minute=minute, second=0, microsecond=0
                        )
                        meeting_end = meeting_start + timedelta(
                            minutes=random.choice([30, 60, 90])
                        )
                        
                        schedules.append({
                            'employee_id': employee['id'],
                            'title': random.choice(meeting_types),
                            'start_time': meeting_start,
                            'end_time': meeting_end
                        })
                
                current_date += timedelta(days=1)
        
        return schedules
    
    def search_by_name(self, name):
        """이름으로 임직원 검색"""
        return [emp for emp in self.employees if name in emp['name']]
    
    def get_team_members(self, team):
        """팀별 임직원 조회"""
        return [emp for emp in self.employees if emp['team'] == team]
    
    def check_schedule_conflicts(self, employee_ids, start_time, end_time):
        """일정 충돌 확인"""
        conflicts = {}
        for emp_id in employee_ids:
            emp_conflicts = []
            for schedule in self.schedules:
                if (schedule['employee_id'] == emp_id and
                    start_time < schedule['end_time'] and
                    end_time > schedule['start_time']):
                    emp_conflicts.append(schedule)
            
            if emp_conflicts:
                conflicts[emp_id] = emp_conflicts
        
        return conflicts

# 사용 예시
api = MockEmployeeAPI()
print(f"총 임직원: {len(api.employees)}명")
print(f"총 일정: {len(api.schedules)}개")

# 검색 테스트
results = api.search_by_name("김")
print(f"'김' 검색 결과: {len(results)}명")
```

### **4. 우선순위 알고리즘**

```python
# src/services/schedule_priority.py
from datetime import datetime, timedelta

class SchedulePriorityService:
    # 시간대별 선호도 점수
    TIME_SCORES = {
        8: 3, 9: 5, 10: 10, 11: 7,     # 오전
        12: 2, 13: 1,                   # 점심시간 (낮은 점수)
        14: 6, 15: 10, 16: 8, 17: 5,   # 오후
        18: 3, 19: 2, 20: 1            # 저녁 (임원급만)
    }
    
    def suggest_meeting_times(self, attendee_ids, target_date, duration_minutes=60):
        """최적 회의 시간 제안"""
        from src.api.employee_api import MockEmployeeAPI
        
        api = MockEmployeeAPI()
        attendees = [api.get_employee_by_id(emp_id) for emp_id in attendee_ids]
        attendees = [emp for emp in attendees if emp]
        
        # 검색 기간: 목표일 전후 1주일
        search_start = target_date - timedelta(days=7)
        search_end = target_date + timedelta(days=7)
        
        time_slots = []
        current_date = search_start
        
        while current_date <= search_end:
            # 주말 제외
            if current_date.weekday() < 5:
                # 30분 간격으로 체크
                for hour in range(8, 21):
                    for minute in [0, 30]:
                        slot_start = current_date.replace(
                            hour=hour, minute=minute, second=0, microsecond=0
                        )
                        slot_end = slot_start + timedelta(minutes=duration_minutes)
                        
                        # 업무시간 체크
                        if self._is_valid_business_hours(slot_start, slot_end, attendees):
                            score = self._calculate_slot_score(
                                slot_start, slot_end, attendees, target_date, api
                            )
                            
                            if score > 0:  # 유효한 슬롯만 추가
                                time_slots.append({
                                    'start_time': slot_start,
                                    'end_time': slot_end,
                                    'score': score,
                                    'start_str': slot_start.strftime("%m/%d %H:%M"),
                                    'end_str': slot_end.strftime("%H:%M")
                                })
            
            current_date += timedelta(days=1)
        
        # 점수 순으로 정렬하여 상위 5개 반환
        time_slots.sort(key=lambda x: x['score'], reverse=True)
        return time_slots[:5]
    
    def _is_valid_business_hours(self, start_time, end_time, attendees):
        """업무시간 유효성 체크"""
        start_hour = start_time.hour
        end_hour = end_time.hour
        
        # 일반직이 포함된 경우 9-17시로 제한
        has_regular_employee = any(emp['priority_level'] == 5 for emp in attendees)
        if has_regular_employee:
            return 9 <= start_hour <= 17 and end_hour <= 18
        
        # 리더급만 있으면 8-20시 가능
        return 8 <= start_hour <= 20 and end_hour <= 21
    
    def _calculate_slot_score(self, start_time, end_time, attendees, target_date, api):
        """시간 슬롯 점수 계산"""
        score = 0
        
        # 1. 시간대 선호도 (가중치: 20)
        time_score = self.TIME_SCORES.get(start_time.hour, 1)
        score += time_score * 20
        
        # 2. 목표 날짜 근접도 (가중치: 15)
        date_diff = abs((start_time.date() - target_date.date()).days)
        date_score = max(0, 10 - date_diff * 0.5)
        score += date_score * 15
        
        # 3. 참석자 우선순위 (가중치: 20)
        priority_score = 0
        for attendee in attendees:
            level = attendee['priority_level']
            priority_score += max(0, 6 - level) * 2  # 임원급 10점, 일반직 2점
        score += priority_score * 10
        
        # 4. 일정 충돌 체크 (가중치: 30)
        attendee_ids = [emp['id'] for emp in attendees]
        conflicts = api.check_schedule_conflicts(attendee_ids, start_time, end_time)
        
        total_attendees = len(attendees)
        conflicted_attendees = len(conflicts)
        availability_rate = (total_attendees - conflicted_attendees) / total_attendees
        score += availability_rate * 30
        
        # 5. 점심시간 패널티
        if self._is_lunch_time(start_time, end_time):
            score -= 20
        
        return round(score, 1)
    
    def _is_lunch_time(self, start_time, end_time):
        """점심시간 여부 확인 (12:00-13:30)"""
        lunch_start_hour = 12
        lunch_end_hour = 13
        lunch_end_minute = 30
        
        start_hour = start_time.hour
        end_hour = end_time.hour
        end_minute = end_time.minute
        
        # 점심시간과 겹치는지 확인
        return (start_hour <= lunch_end_hour and 
                end_hour >= lunch_start_hour and
                not (end_hour == lunch_start_hour or 
                     (start_hour == lunch_end_hour and start_time.minute >= lunch_end_minute)))

# 사용 예시
priority_service = SchedulePriorityService()
attendee_ids = ['emp_001', 'emp_002', 'emp_003']
target_date = datetime.now() + timedelta(days=3)

suggestions = priority_service.suggest_meeting_times(attendee_ids, target_date, 90)
for i, slot in enumerate(suggestions, 1):
    print(f"{i}. {slot['start_str']} - {slot['end_str']} (점수: {slot['score']})")
```

### **5. Streamlit UI 컴포넌트**

```python
# src/components/meeting_form.py
import streamlit as st
from datetime import datetime, timedelta

class MeetingFormComponent:
    def render(self, meeting_data):
        """회의 폼 렌더링"""
        st.markdown("### 📝 회의 정보")
        
        # 제목 입력
        title = st.text_input(
            "회의 제목",
            value=meeting_data.get('title', ''),
            placeholder="회의 제목을 입력하세요"
        )
        
        # 날짜/시간 입력
        col1, col2 = st.columns(2)
        
        with col1:
            meeting_date = st.date_input(
                "날짜",
                value=meeting_data.get('start_time', datetime.now()).date()
            )
        
        with col2:
            col2_1, col2_2 = st.columns(2)
            
            with col2_1:
                start_time = st.time_input(
                    "시작 시간",
                    value=meeting_data.get('start_time', datetime.now()).time(),
                    step=timedelta(minutes=30)
                )
            
            with col2_2:
                end_time = st.time_input(
                    "종료 시간", 
                    value=meeting_data.get('end_time', datetime.now()).time(),
                    step=timedelta(minutes=30)
                )
        
        # 회의 내용
        content = st.text_area(
            "회의 안건",
            value=meeting_data.get('content', ''),
            placeholder="회의 안건을 입력하세요...",
            height=100
        )
        
        # 업데이트된 회의 정보 반환
        return {
            'title': title,
            'start_time': datetime.combine(meeting_date, start_time),
            'end_time': datetime.combine(meeting_date, end_time),
            'content': content,
            'attendees': meeting_data.get('attendees', [])
        }

# src/components/attendee_table.py  
import pandas as pd

class AttendeeTableComponent:
    def render(self, meeting_data):
        """참석자 테이블 렌더링"""
        st.markdown("### 👥 참석자 관리")
        
        # 참석자 추가 UI
        with st.expander("➕ 참석자 추가", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                search_name = st.text_input(
                    "이름 검색", 
                    placeholder="김철수",
                    key="attendee_search"
                )
            
            with col2:
                if st.button("🔍 검색", use_container_width=True):
                    if search_name:
                        # Mock API로 검색
                        from src.api.employee_api import MockEmployeeAPI
                        api = MockEmployeeAPI()
                        results = api.search_by_name(search_name)
                        
                        if results:
                            st.write("**검색 결과:**")
                            for emp in results[:3]:
                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    st.write(f"**{emp['name']}** ({emp['team']}, {emp['role']})")
                                with col_b:
                                    if st.button("추가", key=f"add_{emp['id']}"):
                                        if emp not in meeting_data['attendees']:
                                            meeting_data['attendees'].append(emp)
                                            st.success(f"{emp['name']}님을 추가했습니다!")
                                            st.rerun()
        
        # 참석자 목록 테이블
        if meeting_data['attendees']:
            attendee_df = pd.DataFrame([
                {
                    "선택": False,
                    "이름": att['name'],
                    "팀": att['team'], 
                    "역할": att['role'],
                    "우선순위": att['priority_level']
                }
                for att in meeting_data['attendees']
            ])
            
            edited_df = st.data_editor(
                attendee_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "선택": st.column_config.CheckboxColumn("선택"),
                    "우선순위": st.column_config.NumberColumn("우선순위", min_value=1, max_value=5)
                }
            )
            
            # 선택된 참석자 삭제
            if st.button("🗑️ 선택 삭제"):
                selected_indices = [
                    i for i, row in edited_df.iterrows() if row['선택']
                ]
                
                if selected_indices:
                    for idx in reversed(selected_indices):
                        meeting_data['attendees'].pop(idx)
                    st.success(f"{len(selected_indices)}명을 삭제했습니다!")
                    st.rerun()
        else:
            st.info("참석자를 추가해주세요.")
        
        return meeting_data

# src/components/ai_chat.py
class AIChatComponent:
    def __init__(self, ai_service):
        self.ai_service = ai_service
        self.chat_history = []
    
    def render(self):
        """AI 채팅 컴포넌트 렌더링"""
        st.markdown("### 🤖 AI 어시스턴트")
        
        # 채팅 히스토리 표시
        chat_container = st.container(height=300)
        
        with chat_container:
            if self.chat_history:
                for chat in self.chat_history[-5:]:  # 최근 5개만
                    with st.chat_message("user"):
                        st.write(chat['user'])
                    with st.chat_message("assistant"):
                        st.write(chat['assistant'])
            else:
                with st.chat_message("assistant"):
                    st.markdown("""
                    안녕하세요! 회의 예약을 도와드립니다.
                    
                    **예시:**
                    - "내일 오후 2시에 팀 미팅 잡아줘"
                    - "참석자에 김철수 추가해줘"
                    - "적절한 시간 제안해줘"
                    """)
        
        # 채팅 입력
        prompt = st.chat_input("자연어로 회의를 예약하세요...")
        
        # 초기화 버튼
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            self.chat_history.clear()
            st.rerun()
        
        return prompt
    
    def add_chat(self, user_msg, assistant_msg):
        """채팅 히스토리에 추가"""
        self.chat_history.append({
            'user': user_msg,
            'assistant': assistant_msg,
            'timestamp': datetime.now()
        })
```

---

## 🎨 **CSS 스타일링 팁**

### **Material-UI 스타일 버튼**

```css
/* src/utils/styles.py */
def get_modern_css():
    return """
    <style>
    /* 버튼 스타일링 */
    .stButton > button {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.02857em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 3px 1px -2px rgba(0,0,0,0.2), 
                    0 2px 2px 0 rgba(0,0,0,0.14), 
                    0 1px 5px 0 rgba(0,0,0,0.12);
    }
    
    .stButton > button:hover {
        background: #5a67d8;
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.2),
                    0 4px 5px 0 rgba(0,0,0,0.14),
                    0 1px 10px 0 rgba(0,0,0,0.12);
        transform: translateY(-1px);
    }
    
    /* 입력 필드 스타일링 */
    .stTextInput > div > div > input {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 사이드바 다크 테마 */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        color: white;
    }
    
    /* 메인 컨테이너 카드 스타일 */
    .main .block-container {
        padding: 2rem 3rem;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        margin: 2rem;
    }
    
    /* 성공/오류 메시지 */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #b8daff;
        color: #155724;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    </style>
    """
```

---

## 🚨 **자주 발생하는 오류 해결**

### **1. Google GenAI API 오류**

```python
# 환경변수 설정 확인
import os
print("API Key:", os.getenv('GOOGLE_API_KEY'))

# API 키 설정 방법
# Linux/Mac: export GOOGLE_API_KEY='your-key'
# Windows: set GOOGLE_API_KEY=your-key

# Streamlit에서 secrets 사용
# .streamlit/secrets.toml
# GOOGLE_API_KEY = "your-key-here"

# 코드에서 secrets 접근
import streamlit as st
api_key = st.secrets.get("GOOGLE_API_KEY")
```

### **2. 세션 상태 관리**

```python
# 세션 상태 초기화
def init_session_state():
    if 'meeting_data' not in st.session_state:
        st.session_state.meeting_data = {
            'title': '',
            'attendees': [],
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(hours=1)
        }
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

# 안전한 상태 업데이트
def update_meeting_safely(updates):
    current = st.session_state.meeting_data.copy()
    current.update(updates)
    st.session_state.meeting_data = current
```

### **3. 데이터 타입 오류**

```python
# datetime 안전 처리
def safe_datetime_parse(date_str, time_str):
    try:
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            date_obj = date_str
            
        if isinstance(time_str, str):
            time_obj = datetime.strptime(time_str, "%H:%M").time()
        else:
            time_obj = time_str
            
        return datetime.combine(date_obj, time_obj)
    except Exception as e:
        st.error(f"시간 파싱 오류: {e}")
        return datetime.now()
```

---

## ⚡ **성능 최적화 팁**

### **1. 데이터 캐싱**

```python
# API 결과 캐싱
@st.cache_data
def get_employees():
    api = MockEmployeeAPI()
    return api.employees

@st.cache_data  
def calculate_time_suggestions(attendee_ids, target_date):
    priority_service = SchedulePriorityService()
    return priority_service.suggest_meeting_times(attendee_ids, target_date)
```

### **2. 컴포넌트 분리**

```python
# 변경이 적은 부분은 별도 컴포넌트로
@st.fragment
def render_static_info():
    st.markdown("### ℹ️ 사용법")
    st.info("자연어로 회의를 예약하세요!")

# 자주 변경되는 부분만 리렌더링
def render_dynamic_content():
    meeting = st.session_state.meeting_data
    # 동적 콘텐츠만
```

---

## 🧪 **빠른 테스트 방법**

### **테스트 시나리오**

```python
# tests/quick_test.py
def test_basic_functionality():
    """기본 기능 테스트"""
    # 1. Mock 데이터 생성
    api = MockEmployeeAPI()
    assert len(api.employees) >= 40
    
    # 2. 검색 기능
    results = api.search_by_name("김")
    assert len(results) > 0
    
    # 3. 우선순위 계산
    priority_service = SchedulePriorityService()
    suggestions = priority_service.suggest_meeting_times(
        ['emp_001', 'emp_002'], 
        datetime.now() + timedelta(days=1)
    )
    assert len(suggestions) > 0
    
    print("✅ 모든 기본 기능 테스트 통과!")

if __name__ == "__main__":
    test_basic_functionality()
```

---

## 📱 **배포 가이드**

### **Streamlit Cloud 배포**

```python
# requirements.txt
streamlit>=1.28.0
google-genai>=1.20.0
streamlit-quill>=0.9.0
pandas>=1.5.0

# .streamlit/secrets.toml (로컬 개발용)
GOOGLE_API_KEY = "your-api-key-here"

# Streamlit Cloud에서는 Settings > Secrets에 추가
```

### **로컬 실행**

```bash
# 환경변수 설정 후 실행
export GOOGLE_API_KEY='your-key'
streamlit run app.py

# 또는 .env 파일 사용
pip install python-dotenv
# .env 파일에 GOOGLE_API_KEY=your-key 추가
```

---

**🚀 이 참고 문서로 20시간 내에 완성할 수 있습니다! 화이팅!**