# 🏆 AI Meeting Booking System - 해커톤 구현 가이드

> **목표**: 20시간 내 AI 기반 회의 예약 시스템 완성  
> **구조**: 4시간씩 5단계로 진행  
> **팀 구성**: 개발자 + AI 어시스턴트  

---

## 📋 **전체 타임라인 개요**

| 시간 | 단계 | 주요 목표 | 완료 기준 |
|------|------|-----------|-----------|
| **0-4h** | 🏗️ 기초 설계 | 프로젝트 구조 + Mock API | 기본 Streamlit 앱 실행 |
| **4-8h** | 💾 데이터 모델링 | 회의/임직원 모델 + 우선순위 | 테스트 데이터 생성 완료 |
| **8-12h** | 🤖 AI 통합 | LLM 서비스 + 자연어 처리 | 기본 AI 대화 동작 |
| **12-16h** | ⚡ 핵심 알고리즘 | 일정 우선순위 + 시간 제안 | 스마트 시간 제안 완성 |
| **16-20h** | 🎨 UI/UX 완성 | 디자인 + 테스트 + 배포 | 데모 준비 완료 |

---

## 🚀 **단계별 상세 가이드**

### 📦 **사전 준비 (30분)**

```bash
# 1. 환경 설정
pip install streamlit google-genai streamlit-quill pandas

# 2. Google AI API 키 발급
# https://aistudio.google.com/app/apikey

# 3. 프로젝트 구조 생성
mkdir meeting_booking_system
cd meeting_booking_system
mkdir -p src/{models,services,api,components,utils} tests docs
```

---

## 🏗️ **1단계: 기초 설계 (0-4시간)**

### ⏰ **시간 배분**
- **1시간**: 프로젝트 구조 설계
- **1.5시간**: 기본 Streamlit 앱 + 라우팅
- **1시간**: Mock API 기반 구조
- **0.5시간**: 기본 테스트 및 검증

### 🎯 **핵심 목표**
1. ✅ 깔끔한 모듈 구조 완성
2. ✅ Streamlit 기본 UI 구동
3. ✅ Mock 데이터 생성 시스템
4. ✅ 기본 네비게이션 완성

### 📝 **구현 체크리스트**

#### **1.1 프로젝트 구조 (1시간)**
```python
# app.py - 메인 엔트리포인트
import streamlit as st

def main():
    st.set_page_config(
        page_title="AI Meeting Booking",
        page_icon="📅",
        layout="wide"
    )
    st.title("🤖 AI Meeting Booking System")
    st.write("Hello, Hackathon!")

if __name__ == "__main__":
    main()
```

#### **1.2 기본 모델 정의 (1시간)**
```python
# src/models/meeting.py
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Meeting:
    title: str
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    
# src/models/employee.py  
@dataclass
class Employee:
    id: str
    name: str
    team: str
```

#### **1.3 Mock API 기초 (1.5시간)**
```python
# src/api/employee_api.py
class MockEmployeeAPI:
    def __init__(self):
        self.employees = self._generate_sample_data()
    
    def _generate_sample_data(self):
        # 20명 정도의 샘플 임직원 데이터
        pass
        
    def search_by_name(self, name: str):
        pass
```

#### **1.4 기본 UI 컴포넌트 (0.5시간)**
```python
# src/components/layout.py
def render_header():
    st.markdown("## 📅 회의 예약")

def render_sidebar():
    with st.sidebar:
        st.markdown("### 🔧 도구")
```

### ✅ **1단계 완료 기준**
- [ ] `streamlit run app.py` 정상 실행
- [ ] 기본 UI 레이아웃 표시
- [ ] Mock 데이터 로딩 확인
- [ ] 모듈 import 에러 없음

---

## 💾 **2단계: 데이터 모델링 (4-8시간)**

### ⏰ **시간 배분**
- **1시간**: 역할 시스템 설계
- **1.5시간**: 회의 데이터 모델 완성
- **1시간**: 일정 충돌 로직
- **0.5시간**: 테스트 데이터 생성

### 🎯 **핵심 목표**
1. ✅ 임직원 역할 시스템 (임원/팀장/일반직)
2. ✅ 회의 참석자 관리
3. ✅ 일정 충돌 감지
4. ✅ 현실적인 Mock 데이터

### 📝 **구현 체크리스트**

#### **2.1 역할 시스템 (1시간)**
```python
# src/models/employee.py
from enum import Enum

class EmployeeRole(Enum):
    PRESIDENT = "사장"
    VICE_PRESIDENT = "부사장"  
    MANAGING_DIRECTOR = "상무"
    PL = "PL"
    TL = "TL"
    EMPLOYEE = ""
    
    @classmethod
    def get_priority_level(cls, role):
        # 우선순위 매핑
        pass
```

#### **2.2 회의 모델 확장 (1.5시간)**
```python
# src/models/meeting.py
class AttendeeRole(Enum):
    ORGANIZER = "주관자"
    REQUIRED = "필수"
    OPTIONAL = "선택"

@dataclass  
class Attendee:
    employee_id: str
    name: str
    team: str
    role: AttendeeRole
    has_conflict: bool = False
```

#### **2.3 일정 충돌 로직 (1시간)**
```python
# src/api/schedule_api.py
def check_conflicts(self, employee_ids, start_time, end_time):
    conflicts = {}
    # 시간 겹침 확인 로직
    return conflicts
```

#### **2.4 현실적인 데이터 생성 (0.5시간)**
```python
# 임원급: 하루 3-6개 회의
# 팀장급: 하루 2-5개 회의  
# 일반직: 하루 1-3개 회의
# 점심시간 패턴 반영
```

### ✅ **2단계 완료 기준**
- [ ] 40명 임직원 데이터 생성
- [ ] 3주간 현실적인 일정 생성
- [ ] 역할별 우선순위 동작
- [ ] 일정 충돌 감지 작동

---

## 🤖 **3단계: AI 통합 (8-12시간)**

### ⏰ **시간 배분**
- **1시간**: Google GenAI 연동
- **1.5시간**: 프롬프트 엔지니어링
- **1시간**: 자연어 파싱
- **0.5시간**: 스트리밍 UI

### 🎯 **핵심 목표**
1. ✅ LLM API 연동 완료
2. ✅ 자연어 → 회의 정보 변환
3. ✅ 실시간 스트리밍 응답
4. ✅ 기본 대화 기능

### 📝 **구현 체크리스트**

#### **3.1 AI 서비스 기초 (1시간)**
```python
# src/services/ai_service.py
from google import genai

class AIService:
    def __init__(self):
        self.client = None
        
    def initialize(self):
        self.client = genai.Client(api_key=API_KEY)
        
    def process_prompt(self, prompt, current_meeting):
        # LLM 호출 + 응답 파싱
        pass
```

#### **3.2 프롬프트 설계 (1.5시간)**
```python
SYSTEM_PROMPT = """
당신은 회의 예약 AI입니다.

## 응답 형식:
ACTION: {"action": "update", "updates": {...}}
RESPONSE: 사용자 친화적 메시지

## 예시:
사용자: "내일 오후 2시 팀 미팅"
ACTION: {"action": "update", "updates": {"title": "팀 미팅", "start_time": "2024-12-26 14:00"}}
RESPONSE: ✅ 내일 오후 2시에 팀 미팅을 설정했습니다!
"""
```

#### **3.3 자연어 파싱 (1시간)**
```python
def parse_action_response(self, llm_output):
    # ACTION과 RESPONSE 분리
    # JSON 파싱
    # 에러 처리
    pass
```

#### **3.4 스트리밍 UI (0.5시간)**
```python
# src/components/ai_chat.py
def render_streaming_chat(self):
    for chunk in ai_response_generator:
        yield chunk
```

### ✅ **3단계 완료 기준**
- [ ] "내일 오후 2시 팀 미팅" → 회의 생성
- [ ] "참석자에 김철수 추가" → 참석자 업데이트
- [ ] 스트리밍 응답 정상 작동
- [ ] 에러 처리 완성

---

## ⚡ **4단계: 핵심 알고리즘 (12-16시간)**

### ⏰ **시간 배분**
- **2시간**: 우선순위 알고리즘 설계
- **1시간**: 시간 제안 엔진
- **0.5시간**: 점심시간 패턴 분석
- **0.5시간**: AI 통합

### 🎯 **핵심 목표**
1. ✅ 스마트 시간 제안 완성
2. ✅ 참석자 우선순위 고려
3. ✅ 일정 충돌 회피
4. ✅ "적절한 시간 제안해줘" 동작

### 📝 **구현 체크리스트**

#### **4.1 우선순위 알고리즘 (2시간)**
```python
# src/services/schedule_priority.py
class SchedulePriorityService:
    def suggest_meeting_times(self, attendee_ids, target_date, duration):
        # 1. 참석자 역할 분석
        # 2. 업무시간 제한 확인
        # 3. 일정 충돌 검사
        # 4. 점수 계산
        # 5. 상위 N개 반환
        pass
    
    def _calculate_score(self, time_slot, attendees):
        score = 0
        score += self._time_preference_score(time_slot)  # 10시, 15시 높은 점수
        score += self._attendee_priority_score(attendees)  # 임원급 가중치
        score += self._availability_score(conflicts)  # 가용성
        score -= self._lunch_penalty(time_slot)  # 점심시간 패널티
        return score
```

#### **4.2 시간 제안 엔진 (1시간)**
```python
def get_optimal_time_slots(self):
    time_slots = []
    
    # 30분 간격으로 체크
    for hour in range(8, 21):
        for minute in [0, 30]:
            slot = self._evaluate_time_slot(hour, minute)
            time_slots.append(slot)
    
    # 점수 순 정렬
    return sorted(time_slots, key=lambda x: x.score, reverse=True)[:5]
```

#### **4.3 점심시간 패턴 (0.5시간)**
```python
def analyze_lunch_patterns(self, team):
    # 팀별 점심시간 분석
    # 12:00-13:30 패턴 학습
    pass
```

#### **4.4 AI 통합 (0.5시간)**
```python
def _handle_schedule_suggestion(self, prompt, meeting):
    # "적절한 시간 제안" 키워드 감지
    # 우선순위 서비스 호출
    # 상위 3-5개 시간 제안
    pass
```

### ✅ **4단계 완료 기준**
- [ ] "다음 주 수요일 적절한 시간 제안해줘" 동작
- [ ] 임원 포함 시 확장된 시간대 제안
- [ ] 일정 충돌 자동 회피
- [ ] 점수 기반 최적 시간 정렬

---

## 🎨 **5단계: UI/UX 완성 (16-20시간)**

### ⏰ **시간 배분**
- **1시간**: 폼 UI 완성
- **1시간**: 테이블 + 참석자 관리
- **1시간**: CSS 스타일링
- **1시간**: 테스트 + 버그 수정

### 🎯 **핵심 목표**
1. ✅ 직관적인 회의 예약 폼
2. ✅ 실시간 참석자 관리
3. ✅ Material-UI 스타일링
4. ✅ 데모 준비 완료

### 📝 **구현 체크리스트**

#### **5.1 회의 폼 완성 (1시간)**
```python
# src/components/meeting_form.py
def render_meeting_form(self, meeting):
    # 제목, 시간, 내용 입력
    # 실시간 하이라이트 효과
    # 유효성 검사
    pass
```

#### **5.2 참석자 관리 테이블 (1시간)**  
```python
# src/components/attendee_table.py
def render_attendee_table(self, meeting):
    # 체크박스 선택
    # 역할 변경 드롭다운
    # 일정 충돌 표시
    # 일괄 삭제
    pass
```

#### **5.3 CSS 스타일링 (1시간)**
```css
/* Material-UI 스타일 버튼 */
.stButton > button {
    background: #667eea;
    border-radius: 4px;
    box-shadow: 0 3px 1px -2px rgba(0,0,0,0.2);
    transition: all 0.3s;
}

/* 사이드바 다크 테마 */
.css-1d391kg {
    background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
}
```

#### **5.4 테스트 및 최적화 (1시간)**
```python
# 시나리오 테스트
# 1. 기본 회의 생성
# 2. AI로 정보 수정  
# 3. 참석자 추가/삭제
# 4. 시간 제안 요청
# 5. 최종 저장

# 성능 최적화
# 버그 수정
# 데모 시나리오 준비
```

### ✅ **5단계 완료 기준**
- [ ] 모든 기능 정상 작동
- [ ] 깔끔한 UI/UX
- [ ] 에러 없는 안정성
- [ ] 데모 시나리오 완성

---

## 🏆 **데모 시나리오**

### 📝 **5분 데모 스크립트**

1. **🎬 오프닝 (30초)**
   - "AI와 함께 20시간 만에 완성한 스마트 회의 예약 시스템입니다"

2. **💬 자연어 예약 (2분)**
   ```
   사용자: "다음 주 수요일에 개발 전략 회의를 잡고 싶어"
   AI: ✅ 다음 주 수요일에 개발 전략 회의를 설정했습니다!
   
   사용자: "김철수, 이영희, 박상무를 참석자로 추가해줘"
   AI: ✅ 3명의 참석자를 추가했습니다!
   
   사용자: "적절한 시간을 제안해줘"
   AI: 📊 최적 시간을 분석했습니다!
   1순위: 수요일 10:00-11:30 (점수 89.2, 가용성 100%)
   2순위: 수요일 15:00-16:30 (점수 87.8, 가용성 100%)
   ```

3. **⚡ 핵심 기능 시연 (2분)**
   - 실시간 참석자 관리
   - 일정 충돌 감지  
   - 역할별 우선순위
   - 스마트 시간 제안

4. **🎯 마무리 (30초)**
   - "임직원 40명, 3주간 일정 분석하여 최적 시간 0.1초 내 제안"

---

## 🛠️ **주요 도구 및 라이브러리**

### **필수 라이브러리**
```txt
streamlit>=1.28.0
google-genai>=1.20.0  
streamlit-quill>=0.9.0
pandas>=1.5.0
```

### **개발 도구**
- **IDE**: VSCode + Python 확장
- **AI 어시스턴트**: Claude/ChatGPT for 빠른 코드 생성
- **테스트**: 브라우저 실시간 테스트
- **배포**: Streamlit Cloud (선택사항)

---

## ⚠️ **주의사항 및 팁**

### **🚨 시간 관리**
- ⏰ **각 단계마다 타이머 설정**
- 🎯 **완벽함보다는 동작하는 MVP 우선**
- 🔄 **매 2시간마다 전체 테스트**
- 📝 **구현 중 발견한 이슈 즉시 기록**

### **💡 효율성 팁**
- 🤖 **AI 도구 적극 활용**: 코드 생성, 디버깅, 테스트 데이터
- 📋 **체크리스트 엄격히 준수**: 단계별 완료 기준 확인
- 🔧 **Mock 데이터 먼저**: 실제 API 연동은 나중에
- 🎨 **디자인은 마지막**: 기능 완성 후 스타일링

### **🐛 일반적인 함정들**
- ❌ **과도한 기능 욕심**: 핵심 기능에 집중
- ❌ **완벽한 에러 처리**: 기본적인 try-catch만
- ❌ **복잡한 알고리즘**: 단순하고 동작하는 로직 우선
- ❌ **세밀한 UI**: 기능 중심의 깔끔한 인터페이스

---

## 🎉 **성공 지표**

### **✅ 최소 성공 기준**
- [x] 자연어로 회의 생성
- [x] 참석자 추가/삭제  
- [x] 기본 일정 충돌 확인
- [x] 안정적인 UI 동작

### **🏆 우수 성공 기준** 
- [x] 스마트 시간 제안
- [x] 역할별 우선순위
- [x] 실시간 스트리밍 
- [x] 세련된 UI/UX

### **🌟 탁월한 성공 기준**
- [x] 복잡한 자연어 이해
- [x] 점심시간 패턴 학습
- [x] 성능 최적화
- [x] 완벽한 데모 경험

---

**📞 문의사항이나 막히는 부분이 있으면 각 단계별로 AI 어시스턴트와 상의하며 진행하세요!**

**🚀 화이팅! 20시간 후에 멋진 AI 회의 예약 시스템이 탄생할 것입니다!**