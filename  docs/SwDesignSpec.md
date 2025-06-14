# 소프트웨어 설계서 (Software Design Document)

## 🎯 설계 개요

### 설계 목적
AI Meeting Booking System의 상세 설계를 통해 개발자가 구현 가능한 수준의 기술 명세를 제공합니다.

### 설계 원칙
1. **모듈 독립성**: 각 모듈간 느슨한 결합
2. **재사용성**: 공통 컴포넌트 활용
3. **확장성**: 새로운 기능 추가 용이
4. **테스트 용이성**: 단위 테스트 가능한 구조
5. **성능 최적화**: 효율적인 알고리즘 적용

---

## 📂 프로젝트 구조

### 디렉토리 구조
```
meeting_booking_system/
├── .streamlit/
│   └── config.toml                 # Streamlit 설정
├── src/
│   ├── __init__.py
│   ├── models/                     # 데이터 모델
│   │   ├── __init__.py
│   │   ├── meeting.py              # 회의 관련 모델
│   │   ├── employee.py             # 임직원 모델
│   │   ├── schedule.py             # 일정 모델
│   │   └── chat.py                 # 채팅 모델
│   ├── services/                   # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── ai_service.py           # AI 서비스
│   │   ├── meeting_service.py      # 회의 관리
│   │   ├── schedule_service.py     # 일정 관리
│   │   ├── employee_service.py     # 임직원 관리
│   │   ├── priority_service.py     # 우선순위 알고리즘
│   │   └── notification_service.py # 알림 서비스
│   ├── repositories/               # 데이터 접근 계층
│   │   ├── __init__.py
│   │   ├── meeting_repository.py   # 회의 저장소
│   │   ├── employee_repository.py  # 임직원 저장소
│   │   └── schedule_repository.py  # 일정 저장소
│   ├── api/                        # API 계층
│   │   ├── __init__.py
│   │   ├── external_apis.py        # 외부 API 연동
│   │   ├── ai_api.py              # AI API 래퍼
│   │   └── calendar_api.py        # 캘린더 API
│   ├── components/                 # UI 컴포넌트
│   │   ├── __init__.py
│   │   ├── layout/                 # 레이아웃 컴포넌트
│   │   ├── forms/                  # 폼 컴포넌트
│   │   ├── tables/                 # 테이블 컴포넌트
│   │   └── chat/                   # 채팅 컴포넌트
│   ├── utils/                      # 유틸리티
│   │   ├── __init__.py
│   │   ├── config.py               # 설정 관리
│   │   ├── validators.py           # 유효성 검사
│   │   ├── formatters.py           # 데이터 포맷팅
│   │   ├── cache.py                # 캐시 관리
│   │   └── logger.py               # 로깅 유틸리티
│   └── exceptions/                 # 예외 처리
│       ├── __init__.py
│       ├── business_exceptions.py  # 비즈니스 예외
│       └── api_exceptions.py       # API 예외
├── tests/                          # 테스트 코드
│   ├── unit/                       # 단위 테스트
│   ├── integration/                # 통합 테스트
│   └── e2e/                        # E2E 테스트
├── docs/                           # 문서
├── scripts/                        # 스크립트
├── requirements.txt                # 의존성
├── docker-compose.yml              # 개발 환경
├── Dockerfile                      # 컨테이너 이미지
└── app.py                          # 메인 애플리케이션
```

---

## 🗃️ 데이터 모델 설계

### 핵심 모델 클래스

#### 1. Employee 모델
```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class EmployeeRole(Enum):
    PRESIDENT = "사장"
    VICE_PRESIDENT = "부사장"
    MANAGING_DIRECTOR = "상무"
    MASTER = "Master"
    PL = "PL"
    GROUP_LEADER = "그룹장"
    TL = "TL"
    PART_LEADER = "파트장"
    CA = "CA"
    EA = "EA"
    DXA = "DXA"
    MCA = "MCA"
    MEA = "MEA"
    MDXA = "MDXA"
    EMPLOYEE = ""

@dataclass
class Employee:
    id: str
    name: str
    email: str
    team: str
    role: EmployeeRole
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_priority_level(self) -> int:
        """역할별 우선순위 레벨 반환"""
        
    def is_executive(self) -> bool:
        """임원급 여부 확인"""
        
    def is_leader(self) -> bool:
        """리더급 여부 확인"""
```

#### 2. Meeting 모델
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum

class MeetingStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class AttendeeRole(Enum):
    ORGANIZER = "organizer"
    REQUIRED = "required"
    OPTIONAL = "optional"

@dataclass
class Attendee:
    employee_id: str
    role: AttendeeRole
    status: str = "pending"
    has_conflict: bool = False

@dataclass
class Meeting:
    id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    attendees: List[Attendee]
    organizer_id: str
    status: MeetingStatus
    created_at: datetime
    updated_at: datetime
    
    def get_duration_minutes(self) -> int:
        """회의 지속 시간(분) 반환"""
        
    def get_required_attendees(self) -> List[Attendee]:
        """필수 참석자 목록 반환"""
        
    def get_executive_attendees(self) -> List[Attendee]:
        """임원급 참석자 목록 반환"""
```

#### 3. Schedule 모델
```python
@dataclass
class Schedule:
    id: str
    employee_id: str
    title: str
    start_time: datetime
    end_time: datetime
    type: str  # meeting, personal, vacation, etc.
    meeting_id: Optional[str] = None
    external_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    def overlaps_with(self, other_start: datetime, other_end: datetime) -> bool:
        """다른 일정과 겹치는지 확인"""
        
    def is_lunch_time(self) -> bool:
        """점심시간 여부 확인"""
```

#### 4. Chat 모델
```python
@dataclass
class ChatMessage:
    id: str
    user_input: str
    ai_response: str
    intent: Optional[str]
    entities: Dict[str, Any]
    confidence: float
    session_id: str
    timestamp: datetime

@dataclass
class ChatSession:
    id: str
    user_id: str
    context: Dict[str, Any]
    messages: List[ChatMessage]
    created_at: datetime
    last_activity: datetime
```

---

## 🔧 서비스 계층 설계

### 1. AI Service 설계

#### AIService 클래스
```python
class AIService:
    """AI 서비스 메인 클래스"""
    
    def __init__(self, api_client: AIAPIClient, cache: CacheManager):
        self.api_client = api_client
        self.cache = cache
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        
    async def process_message(self, user_input: str, context: ChatContext) -> ChatResponse:
        """사용자 입력 처리"""
        
    async def extract_meeting_info(self, text: str) -> MeetingInfo:
        """텍스트에서 회의 정보 추출"""
        
    def generate_response(self, intent: str, entities: Dict, context: ChatContext) -> str:
        """응답 생성"""
```

#### Intent Classification
```python
class IntentClassifier:
    """의도 분류기"""
    
    INTENTS = {
        'create_meeting': ['회의', '미팅', '예약', '잡아', '만들어'],
        'modify_meeting': ['수정', '변경', '바꿔', '업데이트'],
        'suggest_time': ['시간 제안', '언제가 좋', '적절한 시간'],
        'add_attendee': ['참석자 추가', '초대', '포함'],
        'check_availability': ['가능한지', '비어있', '일정 확인'],
        'general_chat': ['안녕', '고마워', '도움말']
    }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """텍스트의 의도 분류"""
```

#### Entity Extraction
```python
class EntityExtractor:
    """엔티티 추출기"""
    
    def extract_datetime(self, text: str) -> Optional[datetime]:
        """날짜/시간 정보 추출"""
        
    def extract_attendees(self, text: str) -> List[str]:
        """참석자 이름 추출"""
        
    def extract_meeting_title(self, text: str) -> Optional[str]:
        """회의 제목 추출"""
```

### 2. Meeting Service 설계

#### MeetingService 클래스
```python
class MeetingService:
    """회의 관리 서비스"""
    
    def __init__(self, meeting_repo: MeetingRepository, 
                 employee_repo: EmployeeRepository,
                 schedule_service: ScheduleService,
                 notification_service: NotificationService):
        self.meeting_repo = meeting_repo
        self.employee_repo = employee_repo
        self.schedule_service = schedule_service
        self.notification_service = notification_service
        
    async def create_meeting(self, meeting_data: CreateMeetingRequest) -> Meeting:
        """회의 생성"""
        
    async def update_meeting(self, meeting_id: str, updates: UpdateMeetingRequest) -> Meeting:
        """회의 수정"""
        
    async def cancel_meeting(self, meeting_id: str, reason: str) -> bool:
        """회의 취소"""
        
    async def add_attendee(self, meeting_id: str, employee_id: str, role: AttendeeRole) -> bool:
        """참석자 추가"""
        
    async def check_conflicts(self, meeting: Meeting) -> ConflictReport:
        """일정 충돌 확인"""
```

### 3. Priority Service 설계

#### PriorityService 클래스
```python
class PriorityService:
    """우선순위 알고리즘 서비스"""
    
    def __init__(self, schedule_repo: ScheduleRepository,
                 employee_repo: EmployeeRepository):
        self.schedule_repo = schedule_repo
        self.employee_repo = employee_repo
        self.algorithm = PriorityAlgorithm()
        
    async def suggest_meeting_times(self, 
                                  attendee_ids: List[str],
                                  target_date: datetime,
                                  duration_minutes: int,
                                  preferences: MeetingPreferences) -> List[TimeSlot]:
        """최적 회의 시간 제안"""
        
    def calculate_time_score(self, time_slot: datetime, attendees: List[Employee]) -> float:
        """시간대 점수 계산"""
        
    def analyze_availability(self, attendee_ids: List[str], 
                           start_time: datetime, 
                           end_time: datetime) -> AvailabilityReport:
        """가용성 분석"""
```

#### Priority Algorithm
```python
class PriorityAlgorithm:
    """우선순위 계산 알고리즘"""
    
    # 시간대별 점수
    TIME_SCORES = {
        8: 3.0, 9: 5.0, 10: 10.0, 11: 7.0,
        12: 2.0, 13: 1.0, 14: 6.0, 15: 10.0,
        16: 8.0, 17: 5.0, 18: 3.0, 19: 2.0, 20: 1.0
    }
    
    # 역할별 가중치
    ROLE_WEIGHTS = {
        EmployeeRole.PRESIDENT: 10.0,
        EmployeeRole.VICE_PRESIDENT: 9.0,
        EmployeeRole.MANAGING_DIRECTOR: 8.0,
        EmployeeRole.MASTER: 8.0,
        EmployeeRole.PL: 6.0,
        EmployeeRole.GROUP_LEADER: 6.0,
        EmployeeRole.TL: 4.0,
        EmployeeRole.PART_LEADER: 4.0,
        EmployeeRole.EMPLOYEE: 1.0
    }
    
    def calculate_score(self, time_slot: TimeSlot) -> float:
        """종합 점수 계산"""
        time_score = self._calculate_time_score(time_slot)
        role_score = self._calculate_role_score(time_slot)
        availability_score = self._calculate_availability_score(time_slot)
        proximity_score = self._calculate_proximity_score(time_slot)
        
        return (time_score * 0.3 + 
                role_score * 0.3 + 
                availability_score * 0.3 + 
                proximity_score * 0.1)
```

---

## 🔌 API 설계

### 1. REST API 엔드포인트

#### Meeting API
```python
# POST /api/v1/meetings
{
    "title": "팀 회의",
    "start_time": "2024-12-20T14:00:00Z",
    "end_time": "2024-12-20T15:00:00Z",
    "description": "주간 팀 회의",
    "attendees": [
        {"employee_id": "emp_001", "role": "organizer"},
        {"employee_id": "emp_002", "role": "required"}
    ]
}

# Response
{
    "id": "meeting_123",
    "status": "created",
    "conflicts": []
}

# GET /api/v1/meetings/{meeting_id}
# PUT /api/v1/meetings/{meeting_id}
# DELETE /api/v1/meetings/{meeting_id}
```

#### AI Chat API
```python
# POST /api/v1/chat/message
{
    "message": "내일 오후 2시에 팀 미팅 잡아줘",
    "session_id": "session_123",
    "context": {}
}

# Response (Server-Sent Events)
data: {"type": "intent", "data": {"intent": "create_meeting", "confidence": 0.95}}
data: {"type": "entities", "data": {"time": "2024-12-20T14:00:00Z", "title": "팀 미팅"}}
data: {"type": "response", "data": {"text": "팀 미팅을 내일 오후 2시에 예약하시겠습니까?"}}
data: {"type": "action", "data": {"type": "create_meeting", "data": {...}}}
```

#### Priority API
```python
# POST /api/v1/priority/suggest-times
{
    "attendee_ids": ["emp_001", "emp_002", "emp_003"],
    "target_date": "2024-12-20",
    "duration_minutes": 60,
    "preferences": {
        "avoid_lunch": true,
        "preferred_times": ["10:00", "15:00"]
    }
}

# Response
{
    "suggestions": [
        {
            "start_time": "2024-12-20T10:00:00Z",
            "end_time": "2024-12-20T11:00:00Z",
            "score": 9.2,
            "availability_rate": 1.0,
            "conflicts": []
        }
    ]
}
```

### 2. WebSocket API (실시간 기능)

#### Chat WebSocket
```python
# Connection: ws://localhost:8000/ws/chat/{session_id}

# Client -> Server
{
    "type": "message",
    "data": {
        "text": "회의 시간을 변경해줘",
        "meeting_id": "meeting_123"
    }
}

# Server -> Client
{
    "type": "streaming_response",
    "data": {
        "chunk": "회의 시간을 언제로 변경하시겠습니까?",
        "is_final": false
    }
}
```

---

## 🧪 테스트 설계

### 1. 테스트 전략

#### 테스트 피라미드
```
       /\
      /  \     E2E Tests (5%)
     /____\    ├── 사용자 시나리오 테스트
    /      \   └── 브라우저 자동화 테스트
   /        \  
  /   IT     \ Integration Tests (25%)
 /___________\ ├── API 통합 테스트
/             \├── 데이터베이스 테스트
/   Unit Tests \└── 외부 서비스 연동 테스트
/_______________|
    (70%)       Unit Tests
                ├── 서비스 로직 테스트
                ├── 유틸리티 함수 테스트
                └── 모델 검증 테스트
```

### 2. 단위 테스트 예시

#### AI Service 테스트
```python
class TestAIService:
    
    @pytest.fixture
    def ai_service(self):
        mock_client = Mock(spec=AIAPIClient)
        mock_cache = Mock(spec=CacheManager)
        return AIService(mock_client, mock_cache)
    
    async def test_extract_meeting_info_success(self, ai_service):
        # Given
        input_text = "내일 오후 2시에 개발팀과 프로젝트 회의"
        
        # When
        result = await ai_service.extract_meeting_info(input_text)
        
        # Then
        assert result.title == "프로젝트 회의"
        assert result.start_time.hour == 14
        assert "개발팀" in result.attendee_keywords
    
    def test_intent_classification(self, ai_service):
        # Given
        test_cases = [
            ("회의 잡아줘", "create_meeting"),
            ("시간 변경해줘", "modify_meeting"),
            ("언제가 좋을까?", "suggest_time")
        ]
        
        # When & Then
        for text, expected_intent in test_cases:
            intent, confidence = ai_service.intent_classifier.classify(text)
            assert intent == expected_intent
            assert confidence > 0.7
```

#### Priority Algorithm 테스트
```python
class TestPriorityAlgorithm:
    
    def test_time_score_calculation(self):
        # Given
        algorithm = PriorityAlgorithm()
        time_10am = datetime(2024, 12, 20, 10, 0)
        time_1pm = datetime(2024, 12, 20, 13, 0)
        
        # When
        score_10am = algorithm._calculate_time_score(time_10am)
        score_1pm = algorithm._calculate_time_score(time_1pm)
        
        # Then
        assert score_10am > score_1pm  # 10시가 13시보다 높은 점수
        assert score_10am == 10.0  # 최고 점수
        assert score_1pm == 1.0   # 점심시간 낮은 점수
    
    def test_role_priority_calculation(self):
        # Given
        algorithm = PriorityAlgorithm()
        president = Employee(role=EmployeeRole.PRESIDENT)
        employee = Employee(role=EmployeeRole.EMPLOYEE)
        attendees = [president, employee]
        
        # When
        role_score = algorithm._calculate_role_score(attendees)
        
        # Then
        assert role_score > 5.0  # 임원 포함으로 높은 점수
```

### 3. 통합 테스트 예시

#### API 통합 테스트
```python
class TestMeetingAPI:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_create_meeting_success(self, client, sample_meeting_data):
        # Given
        meeting_data = sample_meeting_data
        
        # When
        response = client.post("/api/v1/meetings", json=meeting_data)
        
        # Then
        assert response.status_code == 201
        assert response.json()["status"] == "created"
        assert "id" in response.json()
    
    def test_create_meeting_with_conflicts(self, client, conflicted_meeting_data):
        # Given
        meeting_data = conflicted_meeting_data
        
        # When
        response = client.post("/api/v1/meetings", json=meeting_data)
        
        # Then
        assert response.status_code == 409
        assert len(response.json()["conflicts"]) > 0
```

---

## 🔒 보안 설계

### 1. 인증 및 인가

#### JWT 토큰 구조
```python
class TokenManager:
    
    def generate_token(self, user: Employee) -> str:
        payload = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "permissions": self.get_user_permissions(user),
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def validate_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return TokenPayload(**payload)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

#### 권한 체계
```python
class Permission(Enum):
    READ_MEETING = "meeting:read"
    CREATE_MEETING = "meeting:create"
    UPDATE_MEETING = "meeting:update"
    DELETE_MEETING = "meeting:delete"
    MANAGE_USERS = "user:manage"
    VIEW_ALL_SCHEDULES = "schedule:view_all"

class RolePermissionMapping:
    PERMISSIONS = {
        EmployeeRole.PRESIDENT: [
            Permission.READ_MEETING,
            Permission.CREATE_MEETING,
            Permission.UPDATE_MEETING,
            Permission.DELETE_MEETING,
            Permission.MANAGE_USERS,
            Permission.VIEW_ALL_SCHEDULES
        ],
        EmployeeRole.PL: [
            Permission.READ_MEETING,
            Permission.CREATE_MEETING,
            Permission.UPDATE_MEETING,
            Permission.VIEW_ALL_SCHEDULES
        ],
        EmployeeRole.EMPLOYEE: [
            Permission.READ_MEETING,
            Permission.CREATE_MEETING,
            Permission.UPDATE_MEETING
        ]
    }

def require_permission(permission: Permission):
    """권한 확인 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if not has_permission(current_user, permission):
                raise PermissionError(f"Required permission: {permission.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

### 2. 데이터 보안

#### 데이터 암호화
```python
class DataEncryption:
    
    def __init__(self, encryption_key: str):
        self.fernet = Fernet(encryption_key.encode())
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """민감한 데이터 암호화"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """암호화된 데이터 복호화"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

class PersonalDataMasking:
    
    @staticmethod
    def mask_email(email: str) -> str:
        """이메일 마스킹"""
        local, domain = email.split('@')
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """전화번호 마스킹"""
        return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]
```

### 3. API 보안

#### Rate Limiting
```python
class RateLimiter:
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_rate_limit(self, user_id: str, endpoint: str, 
                        requests_per_minute: int = 60) -> bool:
        """API 호출 제한 확인"""
        key = f"rate_limit:{user_id}:{endpoint}"
        current_minute = int(time.time() // 60)
        
        pipe = self.redis.pipeline()
        pipe.incr(f"{key}:{current_minute}")
        pipe.expire(f"{key}:{current_minute}", 60)
        result = pipe.execute()
        
        return result[0] <= requests_per_minute

class APISecurityMiddleware:
    
    def process_request(self, request):
        # CORS 검증
        if not self.validate_cors(request):
            raise SecurityError("Invalid CORS origin")
        
        # CSRF 토큰 검증
        if request.method in ['POST', 'PUT', 'DELETE']:
            if not self.validate_csrf_token(request):
                raise SecurityError("Invalid CSRF token")
        
        # Rate limiting
        user_id = self.get_user_id(request)
        if not self.rate_limiter.check_rate_limit(user_id, request.path):
            raise SecurityError("Rate limit exceeded")
```

---

## 📊 성능 최적화 설계

### 1. 캐싱 전략

#### 다층 캐시 구조
```python
class CacheManager:
    
    def __init__(self, redis_client, memory_cache):
        self.redis = redis_client
        self.memory = memory_cache
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        # L1: 메모리 캐시
        if value := self.memory.get(key):
            return value
        
        # L2: Redis 캐시
        if value := await self.redis.get(key):
            deserialized = pickle.loads(value)
            self.memory.set(key, deserialized, ttl=300)  # 5분
            return deserialized
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """캐시에 데이터 저장"""
        # L1: 메모리 캐시
        self.memory.set(key, value, ttl=min(ttl, 300))
        
        # L2: Redis 캐시
        serialized = pickle.dumps(value)
        await self.redis.setex(key, ttl, serialized)

class CacheKeys:
    EMPLOYEE_BY_ID = "employee:id:{employee_id}"
    TEAM_MEMBERS = "team:members:{team_name}"
    SCHEDULE_CONFLICTS = "conflicts:{employee_ids}:{date}"
    AI_RESPONSE = "ai:response:{input_hash}"
```

#### 캐시 무효화 전략
```python
class CacheInvalidator:
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
    
    async def invalidate_employee_cache(self, employee_id: str):
        """임직원 관련 캐시 무효화"""
        patterns = [
            f"employee:id:{employee_id}",
            f"team:members:*",  # 팀 변경 가능성
            f"conflicts:*{employee_id}*"  # 해당 직원 포함 충돌 캐시
        ]
        await self.cache.delete_by_patterns(patterns)
    
    async def invalidate_schedule_cache(self, employee_id: str, date: str):
        """일정 관련 캐시 무효화"""
        patterns = [
            f"conflicts:*{employee_id}*:{date}",
            f"schedule:employee:{employee_id}:{date}"
        ]
        await self.cache.delete_by_patterns(patterns)
```

### 2. 데이터베이스 최적화

#### 쿼리 최적화
```python
class OptimizedQueries:
    
    @staticmethod
    def get_meetings_with_attendees(start_date: date, end_date: date) -> str:
        """참석자 정보를 포함한 회의 조회 (JOIN 최적화)"""
        return """
        SELECT 
            m.id, m.title, m.start_time, m.end_time,
            json_agg(
                json_build_object(
                    'employee_id', a.employee_id,
                    'name', e.name,
                    'role', a.role
                )
            ) as attendees
        FROM meetings m
        LEFT JOIN attendees a ON m.id = a.meeting_id
        LEFT JOIN employees e ON a.employee_id = e.id
        WHERE m.start_time >= %s AND m.end_time <= %s
        GROUP BY m.id, m.title, m.start_time, m.end_time
        ORDER BY m.start_time
        """
    
    @staticmethod
    def check_schedule_conflicts_batch(employee_ids: List[str], 
                                     start_time: datetime, 
                                     end_time: datetime) -> str:
        """일괄 일정 충돌 확인 (IN 절 최적화)"""
        return """
        SELECT employee_id, COUNT(*) as conflict_count
        FROM schedules
        WHERE employee_id = ANY(%s)
        AND (
            (start_time <= %s AND end_time > %s) OR
            (start_time < %s AND end_time >= %s) OR
            (start_time >= %s AND end_time <= %s)
        )
        GROUP BY employee_id
        """

class DatabaseIndexes:
    """데이터베이스 인덱스 정의"""
    
    INDEXES = [
        "CREATE INDEX idx_meetings_start_time ON meetings(start_time)",
        "CREATE INDEX idx_meetings_organizer ON meetings(organizer_id)",
        "CREATE INDEX idx_attendees_meeting ON attendees(meeting_id)",
        "CREATE INDEX idx_attendees_employee ON attendees(employee_id)",
        "CREATE INDEX idx_schedules_employee_time ON schedules(employee_id, start_time, end_time)",
        "CREATE INDEX idx_employees_team ON employees(team)",
        "CREATE INDEX idx_employees_role ON employees(role)"
    ]
```

### 3. 비동기 처리

#### 백그라운드 작업
```python
class BackgroundTasks:
    
    def __init__(self, celery_app):
        self.celery = celery_app
    
    @celery.task
    def send_meeting_notifications(meeting_id: str):
        """회의 알림 발송 (비동기)"""
        meeting = MeetingRepository.get_by_id(meeting_id)
        notification_service = NotificationService()
        
        for attendee in meeting.attendees:
            notification_service.send_email(
                to=attendee.email,
                subject=f"회의 알림: {meeting.title}",
                template="meeting_invitation",
                data={"meeting": meeting, "attendee": attendee}
            )
    
    @celery.task
    def update_external_calendars(meeting_id: str):
        """외부 캘린더 동기화 (비동기)"""
        meeting = MeetingRepository.get_by_id(meeting_id)
        calendar_service = CalendarService()
        
        for attendee in meeting.attendees:
            calendar_service.create_event(
                calendar_id=attendee.calendar_id,
                event_data=meeting.to_calendar_event()
            )
    
    @celery.task
    def generate_ai_insights(meeting_id: str):
        """AI 기반 회의 인사이트 생성 (비동기)"""
        meeting = MeetingRepository.get_by_id(meeting_id)
        ai_service = AIService()
        
        insights = ai_service.analyze_meeting_effectiveness(meeting)
        InsightRepository.save(meeting_id, insights)
```

---

## 🔧 설정 관리

### 1. 환경별 설정

#### 설정 클래스
```python
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 기본 설정
    app_name: str = "AI Meeting Booking System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 데이터베이스
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url: str
    redis_db: int = 0
    
    # AI API
    google_ai_api_key: str
    openai_api_key: Optional[str] = None
    ai_response_timeout: int = 30
    
    # 보안
    secret_key: str
    encryption_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    
    # 성능
    cache_default_ttl: int = 3600
    rate_limit_per_minute: int = 60
    max_attendees_per_meeting: int = 50
    
    # 외부 서비스
    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 환경별 설정
class DevelopmentSettings(Settings):
    debug: bool = True
    database_url: str = "postgresql://localhost/meeting_booking_dev"
    redis_url: str = "redis://localhost:6379/0"

class ProductionSettings(Settings):
    debug: bool = False
    # 프로덕션 환경 변수에서 로드

class TestSettings(Settings):
    database_url: str = "postgresql://localhost/meeting_booking_test"
    redis_url: str = "redis://localhost:6379/1"
```

### 2. 기능 플래그

#### Feature Flag 관리
```python
class FeatureFlags:
    
    def __init__(self, config_source: str = "database"):
        self.config_source = config_source
        self.flags = self._load_flags()
    
    def _load_flags(self) -> Dict[str, bool]:
        """기능 플래그 로드"""
        return {
            "ai_streaming_response": True,
            "advanced_priority_algorithm": True,
            "external_calendar_sync": False,
            "voice_input": False,
            "mobile_app_support": False,
            "meeting_analytics": True,
            "auto_meeting_summary": False
        }
    
    def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """기능 플래그 확인"""
        if flag_name not in self.flags:
            return False
        
        # 사용자별 플래그 (A/B 테스트 등)
        if user_id and self._is_beta_user(user_id):
            return self.flags.get(f"{flag_name}_beta", self.flags[flag_name])
        
        return self.flags[flag_name]
    
    def _is_beta_user(self, user_id: str) -> bool:
        """베타 사용자 확인"""
        # 사용자 ID 해시의 마지막 자리가 0-2면 베타 사용자 (30%)
        return hash(user_id) % 10 < 3
```

---

## 📝 로깅 및 모니터링

### 1. 구조화된 로깅

#### 로거 설정
```python
import structlog
from typing import Any, Dict

class StructuredLogger:
    
    def __init__(self):
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.processors.add_logger_name,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        self.logger = structlog.get_logger()
    
    def log_api_request(self, request_id: str, method: str, 
                       path: str, user_id: str, **kwargs):
        """API 요청 로그"""
        self.logger.info(
            "api_request",
            request_id=request_id,
            method=method,
            path=path,
            user_id=user_id,
            **kwargs
        )
    
    def log_business_event(self, event_type: str, entity_id: str, 
                          user_id: str, details: Dict[str, Any]):
        """비즈니스 이벤트 로그"""
        self.logger.info(
            "business_event",
            event_type=event_type,
            entity_id=entity_id,
            user_id=user_id,
            details=details
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any]):
        """에러 로그"""
        self.logger.error(
            "application_error",
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )
```

### 2. 메트릭 수집

#### 애플리케이션 메트릭
```python
from prometheus_client import Counter, Histogram, Gauge

class ApplicationMetrics:
    
    def __init__(self):
        # 카운터 메트릭
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status']
        )
        
        self.meetings_created_total = Counter(
            'meetings_created_total',
            'Total meetings created',
            ['user_role']
        )
        
        self.ai_requests_total = Counter(
            'ai_requests_total',
            'Total AI requests',
            ['intent', 'success']
        )
        
        # 히스토그램 메트릭
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration',
            ['method', 'endpoint']
        )
        
        self.ai_response_time = Histogram(
            'ai_response_time_seconds',
            'AI response time',
            ['model', 'intent']
        )
        
        # 게이지 메트릭
        self.active_users = Gauge(
            'active_users',
            'Number of active users'
        )
        
        self.cache_hit_rate = Gauge(
            'cache_hit_rate',
            'Cache hit rate percentage'
        )
    
    def record_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """API 요청 메트릭 기록"""
        self.api_requests_total.labels(
            method=method, 
            endpoint=endpoint, 
            status=status
        ).inc()
        
        self.request_duration.labels(
            method=method, 
            endpoint=endpoint
        ).observe(duration)
    
    def record_meeting_creation(self, user_role: str):
        """회의 생성 메트릭 기록"""
        self.meetings_created_total.labels(user_role=user_role).inc()
```

---

## 🔄 CI/CD 파이프라인 설계

### 1. GitHub Actions 워크플로우

#### 빌드 및 테스트
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: meeting_booking_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        black --check .
        isort --check-only .
        flake8 .
        mypy src/
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src/
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/meeting_booking_test
        REDIS_URL: redis://localhost:6379/1
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run security checks
      run: |
        pip install safety bandit
        safety check
        bandit -r src/
    
    - name: Run dependency check
      uses: pypa/gh-action-pip-audit@v1.0.8

  build:
    needs: [test, security]
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t meeting-booking:${{ github.sha }} .
    
    - name: Push to registry
      if: github.ref == 'refs/heads/main'
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push meeting-booking:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to staging
      run: |
        # Kubernetes 배포 스크립트 실행
        kubectl set image deployment/meeting-booking meeting-booking=meeting-booking:${{ github.sha }}
```

---

## 📋 체크리스트

### 개발 완료 체크리스트

#### 📊 기능 구현
- [ ] 회의 CRUD 기능
- [ ] 참석자 관리 시스템
- [ ] AI 자연어 처리
- [ ] 우선순위 알고리즘
- [ ] 일정 충돌 검사
- [ ] 사용자 인증/인가
- [ ] 캐싱 시스템
- [ ] 알림 기능

#### 🧪 품질 보증
- [ ] 단위 테스트 커버리지 80% 이상
- [ ] 통합 테스트 작성
- [ ] E2E 테스트 시나리오
- [ ] 성능 테스트 완료
- [ ] 보안 스캔 통과
- [ ] 접근성 검증

#### 📚 문서화
- [ ] API 문서 (OpenAPI/Swagger)
- [ ] 사용자 매뉴얼
- [ ] 운영 가이드
- [ ] 트러블슈팅 가이드
- [ ] 아키텍처 다이어그램

#### 🚀 배포 준비
- [ ] 프로덕션 환경 설정
- [ ] 모니터링 대시보드
- [ ] 백업 전략 수립
- [ ] 재해 복구 계획
- [ ] 성능 기준선 설정

---

*문서 버전: 1.0*  
*작성일: 2024-12-15*  
*검토자: Software Architect*  
*승인자: Technical Lead*