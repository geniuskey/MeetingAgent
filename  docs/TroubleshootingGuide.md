# 🚨 AI Meeting Booking System - 트러블슈팅 가이드

> **해커톤 중 발생할 수 있는 문제들과 빠른 해결책**

---

## 🔧 **환경 설정 문제**

### **❌ 문제: GOOGLE_API_KEY 오류**
```
ERROR: API key not found
ERROR: Authentication failed
```

**✅ 해결책:**
```bash
# 1. API 키 확인
echo $GOOGLE_API_KEY

# 2. 환경변수 설정 (Linux/Mac)
export GOOGLE_API_KEY='your-api-key-here'

# 3. 환경변수 설정 (Windows)
set GOOGLE_API_KEY=your-api-key-here

# 4. Python에서 확인
import os
print("API Key exists:", bool(os.getenv('GOOGLE_API_KEY')))

# 5. Streamlit secrets 사용 (.streamlit/secrets.toml)
GOOGLE_API_KEY = "your-api-key-here"

# 6. 코드에서 secrets 접근
import streamlit as st
api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv('GOOGLE_API_KEY'))
```

### **❌ 문제: 패키지 설치 오류**
```
ERROR: No module named 'google.genai'
ERROR: No module named 'streamlit_quill'
```

**✅ 해결책:**
```bash
# 1. 최신 pip 업그레이드
pip install --upgrade pip

# 2. 패키지 재설치
pip install streamlit google-genai streamlit-quill pandas

# 3. 가상환경 사용 권장
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4. requirements.txt 사용
pip install -r requirements.txt

# 5. 특정 버전 설치
pip install streamlit==1.28.0 google-genai==1.20.0
```

---

## 🤖 **AI 서비스 문제**

### **❌ 문제: "응답 생성 중 오류가 발생했습니다"**

**✅ 해결책:**
```python
# 1. 디버그 모드 활성화
import streamlit as st
import traceback

def debug_ai_service():
    try:
        ai_service = AIService()
        success, message = ai_service.initialize()
        st.write(f"초기화: {success}, {message}")
        
        if success:
            response = ai_service.process_prompt("안녕", {})
            st.write(f"응답: {response}")
    except Exception as e:
        st.error(f"오류: {str(e)}")
        st.code(traceback.format_exc())

# 2. API 호출 테스트
def test_google_genai():
    from google import genai
    import os
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("API 키가 없습니다!")
        return
    
    try:
        client = genai.Client(api_key=api_key)
        response = ""
        for chunk in client.models.generate_content_stream(
            model='gemini-2.0-flash-001',
            contents="안녕하세요"
        ):
            if chunk.text:
                response += chunk.text
        
        st.success(f"API 테스트 성공: {response}")
    except Exception as e:
        st.error(f"API 테스트 실패: {str(e)}")
```

### **❌ 문제: JSON 파싱 오류**
```
ERROR: Expecting ',' delimiter
ERROR: JSON decode error
```

**✅ 해결책:**
```python
# 1. 안전한 JSON 파싱
import json
import re

def safe_json_parse(text):
    try:
        # JSON 블록 추출
        json_pattern = r'```json\n(.*?)\n```'
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            json_text = match.group(1)
        else:
            # 중괄호 찾기
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                json_text = text[start:end]
            else:
                return None
        
        return json.loads(json_text)
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        print(f"원본 텍스트: {text}")
        return None
```

# 2. 프롬프트 개선
SYSTEM_PROMPT = """
반드시 다음 형식으로만 응답하세요:

ACTION:
{"action": "update", "updates": {"title": "회의제목"}}

RESPONSE:
사용자 메시지
"""

---

## 💾 **데이터 모델 문제**

### **❌ 문제: AttributeError: 'dict' object has no attribute**
```
ERROR: 'dict' object has no attribute 'name'
ERROR: 'Meeting' object has no attribute 'start_str'
```

**✅ 해결책:**
```python
# 1. 안전한 속성 접근
def safe_get_attr(obj, attr, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    else:
        return getattr(obj, attr, default)

# 사용 예시
name = safe_get_attr(employee, 'name', '알 수 없음')

# 2. 데이터 타입 통일
@dataclass
class Employee:
    id: str
    name: str
    team: str
    role: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

# 3. TimeSlot 속성 문제 해결
@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    score: float
    
    @property
    def start_str(self):
        return self.start_time.strftime("%m/%d %H:%M")
    
    @property
    def end_str(self):
        return self.end_time.strftime("%H:%M")
```

### **❌ 문제: 세션 상태 초기화 오류**
```
ERROR: 'NoneType' object is not subscriptable
ERROR: Key 'current_meeting' not found
```

**✅ 해결책:**
```python
# 1. 안전한 세션 상태 초기화
def init_session_state():
    defaults = {
        'current_meeting': {
            'title': '',
            'start_time': datetime.now(),
            'end_time': datetime.now() + timedelta(hours=1),
            'attendees': [],
            'content': ''
        },
        'chat_history': [],
        'meeting_storage': []
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# 2. 안전한 상태 접근
def get_current_meeting():
    init_session_state()
    return st.session_state.current_meeting

def update_current_meeting(updates):
    current = get_current_meeting()
    if isinstance(current, dict):
        current.update(updates)
        st.session_state.current_meeting = current
```

---

## 🎨 **UI/UX 문제**

### **❌ 문제: Streamlit 레이아웃 깨짐**
```
WARNING: Column ratios don't sum to 1
ERROR: Widget key conflicts
```

**✅ 해결책:**
```python
# 1. 컬럼 비율 수정
col1, col2, col3 = st.columns([2, 1, 1])  # 비율 합계 = 4
# 또는
col1, col2, col3 = st.columns(3)  # 동일 비율

# 2. 고유 키 생성
import uuid

def generate_unique_key(prefix=""):
    return f"{prefix}_{str(uuid.uuid4())[:8]}"

# 사용
button_key = generate_unique_key("delete_btn")
if st.button("삭제", key=button_key):
    pass

# 3. 키 충돌 방지
class KeyManager:
    def __init__(self):
        self.counters = {}
    
    def get_key(self, prefix):
        if prefix not in self.counters:
            self.counters[prefix] = 0
        self.counters[prefix] += 1
        return f"{prefix}_{self.counters[prefix]}"

key_manager = KeyManager()
```

### **❌ 문제: CSS 스타일 적용 안됨**
```
WARNING: CSS not loading
WARNING: Style not applied
```

**✅ 해결책:**
```python
# 1. CSS 적용 순서 확인
def apply_styles():
    st.markdown("""
    <style>
    /* 스타일 코드 */
    .stButton > button {
        background-color: #667eea !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 캐시 문제 해결
def force_css_reload():
    import time
    timestamp = int(time.time())
    
    st.markdown(f"""
    <style id="custom-style-{timestamp}">
    /* 스타일 코드 */
    </style>
    """, unsafe_allow_html=True)

# 3. Streamlit 클래스명 확인
# 브라우저 개발자 도구로 실제 클래스명 확인
# css-1d391kg (사이드바) 등은 버전마다 변경될 수 있음
```

---

## ⚡ **성능 문제**

### **❌ 문제: 앱이 느려짐, 무한 로딩**

**✅ 해결책:**
```python
# 1. 불필요한 리렌더링 방지
@st.cache_data
def expensive_calculation():
    # 시간이 오래 걸리는 작업
    pass

# 2. Fragment 사용
@st.fragment
def static_component():
    st.markdown("### 정적 컨텐츠")
    # 변경되지 않는 부분

# 3. 조건부 렌더링
def render_conditionally():
    if st.session_state.get('show_advanced', False):
        render_advanced_features()

# 4. 데이터 크기 제한
def limit_data_size(data, max_items=100):
    if len(data) > max_items:
        st.warning(f"데이터가 많아 {max_items}개만 표시합니다.")
        return data[:max_items]
    return data
```

### **❌ 문제: 메모리 사용량 증가**

**✅ 해결책:**
```python
# 1. 세션 상태 정리
def cleanup_session_state():
    # 오래된 데이터 정리
    if 'old_data' in st.session_state:
        del st.session_state.old_data

# 2. 제너레이터 사용
def process_large_data():
    for item in large_dataset:
        yield process_item(item)  # 한 번에 하나씩 처리

# 3. 캐시 크기 제한
@st.cache_data(max_entries=10)
def cached_function():
    pass
```

---

## 🧪 **테스트 및 디버깅**

### **❌ 문제: 테스트 실행 실패**

**✅ 해결책:**
```python
# 1. 간단한 단위 테스트
def test_employee_api():
    try:
        from src.api.employee_api import MockEmployeeAPI
        api = MockEmployeeAPI()
        
        # 기본 테스트
        assert len(api.employees) > 0, "임직원 데이터가 없습니다"
        assert len(api.schedules) > 0, "일정 데이터가 없습니다"
        
        # 검색 테스트
        results = api.search_by_name("김")
        assert len(results) > 0, "검색 결과가 없습니다"
        
        print("✅ Employee API 테스트 통과")
        return True
    except Exception as e:
        print(f"❌ Employee API 테스트 실패: {e}")
        return False

# 2. 통합 테스트
def integration_test():
    tests = [
        test_employee_api,
        test_ai_service,
        test_priority_algorithm
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"통합 테스트 결과: {passed}/{len(tests)} 통과")

# 3. 실시간 디버깅
def debug_mode():
    if st.sidebar.checkbox("디버그 모드"):
        st.sidebar.json(st.session_state.to_dict())
        
        if st.sidebar.button("세션 상태 초기화"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
```

---

## 🚀 **배포 문제**

### **❌ 문제: Streamlit Cloud 배포 실패**

**✅ 해결책:**
```python
# 1. requirements.txt 확인
streamlit>=1.28.0
google-genai>=1.20.0
streamlit-quill>=0.9.0
pandas>=1.5.0

# 2. Python 버전 호환성
# runtime.txt 파일 추가
python-3.9

# 3. 환경변수 설정
# Streamlit Cloud > Settings > Secrets
GOOGLE_API_KEY = "your-api-key-here"

# 4. 포트 설정
# .streamlit/config.toml
[server]
port = 8501
headless = true

# 5. 메모리 최적화
# config.toml
[server]
maxUploadSize = 50
maxMessageSize = 50
```

### **❌ 문제: 로컬 실행 시 포트 충돌**

**✅ 해결책:**
```bash
# 1. 다른 포트 사용
streamlit run app.py --server.port 8502

# 2. 실행 중인 프로세스 확인
lsof -i :8501  # Mac/Linux
netstat -ano | findstr :8501  # Windows

# 3. 프로세스 종료
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

---

## 📋 **빠른 체크리스트**

### **🔍 문제 발생 시 체크 순서**

1. **[ ]** API 키 설정 확인
2. **[ ]** 패키지 버전 호환성
3. **[ ]** 세션 상태 초기화
4. **[ ]** 브라우저 콘솔 에러 확인
5. **[ ]** 터미널 에러 메시지 확인
6. **[ ]** 네트워크 연결 상태

### **⚡ 응급 처치**

```python
# 1. 전체 초기화
def emergency_reset():
    # 세션 상태 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # 캐시 초기화
    st.cache_data.clear()
    
    # 페이지 새로고침
    st.rerun()

# 2. 안전 모드 실행
def safe_mode():
    try:
        # 최소 기능만 실행
        st.title("🔧 안전 모드")
        st.write("기본 기능만 실행 중...")
        
        # API 테스트
        if st.button("API 테스트"):
            test_google_genai()
            
    except Exception as e:
        st.error(f"안전 모드 실행 실패: {e}")
```

### **📞 도움 요청 시 포함할 정보**

1. **에러 메시지 전체**
2. **Python/Streamlit 버전**
3. **운영체제 정보**
4. **재현 단계**
5. **관련 코드 스니펫**

```python
# 시스템 정보 출력
def system_info():
    import sys
    import streamlit as st
    import platform
    
    st.write(f"Python: {sys.version}")
    st.write(f"Streamlit: {st.__version__}")
    st.write(f"OS: {platform.system()} {platform.release()}")
```

---

## 🎯 **예방 차원의 모범 사례**

### **1. 에러 처리**
```python
def safe_function_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"함수 실행 실패: {func.__name__}: {e}")
        return None
```

### **2. 로깅**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_action(action, details=""):
    logger.info(f"Action: {action}, Details: {details}")
    if st.sidebar.checkbox("로그 표시"):
        st.sidebar.text(f"{action}: {details}")
```

### **3. 버전 관리**
```python
# version.py
VERSION = "1.0.0"
BUILD_DATE = "2024-12-15"

def show_version():
    st.sidebar.text(f"v{VERSION} ({BUILD_DATE})")
```

---

**🚨 문제가 해결되지 않으면 디버그 모드를 켜고 로그를 확인하세요!**
**💪 해커톤 중에는 완벽함보다 동작하는 것이 우선입니다!**