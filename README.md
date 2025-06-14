# AI Meeting Booking System

Google Gen AI를 활용한 자연어 기반 회의 예약 시스템입니다.

## 🏗️ 프로젝트 구조

```
meeting_booking_system/
├── .streamlit/
│   └── config.toml                 # Streamlit 설정 파일
├── src/
│   ├── __init__.py
│   ├── models/                     # 데이터 모델
│   │   ├── __init__.py
│   │   ├── meeting.py              # Meeting, Attendee 모델
│   │   ├── employee.py             # Employee, Schedule 모델
│   │   └── chat.py                 # Chat, LLMResponse 모델
│   ├── services/                   # 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── ai_service.py           # AI/LLM 서비스
│   │   ├── meeting_service.py      # 회의 관리 서비스
│   │   ├── attendee_service.py     # 참석자 관리 서비스
│   │   └── time_service.py         # 시간 관리 서비스
│   ├── api/                        # Mock API
│   │   ├── __init__.py
│   │   ├── employee_api.py         # 임직원 API (Mock)
│   │   └── schedule_api.py         # 일정 API (Mock)
│   ├── components/                 # UI 컴포넌트
│   │   ├── __init__.py
│   │   ├── layout.py               # 헤더, 로고 등 레이아웃
│   │   ├── sidebar.py              # 사이드바 컴포넌트들
│   │   ├── meeting_form.py         # 회의 폼 컴포넌트
│   │   ├── attendee_table.py       # 참석자 테이블 컴포넌트
│   │   └── ai_chat.py              # AI 채팅 컴포넌트
│   ├── utils/                      # 유틸리티
│   │   ├── __init__.py
│   │   ├── session.py              # 세션 관리
│   │   ├── styles.py               # CSS 스타일
│   │   └── config.py               # 설정 및 상수
│   └── pages/                      # 멀티페이지 (향후 확장용)
│       └── __init__.py
├── data/                           # 데이터 파일 (향후 확장용)
├── tests/                          # 테스트 파일 (향후 확장용)
├── requirements.txt                # Python 의존성
├── README.md                       # 프로젝트 설명
├── .gitignore                      # Git 무시 파일
└── app.py                          # 메인 Streamlit 앱
```

## 🚀 주요 기능

- 🤖 **자연어 AI 어시스턴트**: 스트리밍 채팅으로 회의 예약 지원
- 📅 **직관적인 회의 예약 폼**: 제목, 시간, 참석자, 안건 관리
- 👥 **참석자 관리 테이블**: 역할 지정, 일정 충돌 확인, 검색 기능
- 📋 **회의 히스토리**: 이전 회의 목록, 수정/복사/삭제 기능
- 📝 **Rich Text 에디터**: Quill 에디터로 회의 안건 작성
- 🎨 **모던한 Material-UI 스타일**: 반응형 디자인
- 🔄 **실시간 동기화**: AI 응답에 따른 폼 자동 업데이트

## 📦 설치 방법

1. **저장소 클론**
```bash
git clone <repository-url>
cd meeting_booking_system
```

2. **필요한 패키지 설치**
```bash
pip install -r requirements.txt
```

3. **환경 변수 설정**
```bash
export GOOGLE_API_KEY='your-google-api-key'
```

## 🏃‍♂️ 실행 방법

```bash
streamlit run app.py
```

## 💡 사용법

### 자연어 명령 예시
- "내일 오후 2시에 팀 미팅 잡아줘"
- "다음 주 월요일 10시부터 12시까지 프로젝트 리뷰 회의"
- "김철수, 이영희, 박민수와 함께 기획 회의 예약"
- "회의 제목을 '월간 보고서 검토'로 바꿔줘"
- "참석자에 홍길동 추가해줘"
- "회의 시간을 1시간 연장해줘"

### 참석자 관리
- **역할 지정**: 주관자, 필수 참석자, 선택 참석자
- **일정 충돌 확인**: 해당 시간의 다른 일정 자동 체크
- **임직원 검색**: 이름 또는 팀명으로 검색
- **일괄 관리**: 체크박스로 다중 선택 삭제

### 이전 회의 관리
- **📥 수정**: 기존 회의를 불러와서 수정
- **📋 복사**: 기존 회의를 복사해서 새 회의 생성  
- **🗑️ 삭제**: 회의 삭제

## 🛠️ API 키 설정

Google AI Studio에서 API 키를 발급받아 환경변수로 설정해주세요:

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. API 키 생성
3. 환경변수 설정:
   ```bash
   export GOOGLE_API_KEY='your-api-key-here'
   ```

## 🔧 기술 스택

- **Frontend**: Streamlit, Streamlit-Quill
- **AI**: Google Gen AI (Gemini 2.0)
- **Backend**: Python
- **Styling**: Custom CSS (Material-UI inspired)
- **Architecture**: Modular Design Pattern

## 🏗️ 아키텍처 특징

### 모듈화 설계
- **Models**: 데이터 구조 정의
- **Services**: 비즈니스 로직 처리
- **Components**: UI 컴포넌트 렌더링
- **API**: Mock API 레이어
- **Utils**: 공통 유틸리티

### 확장성
- 새로운 기능 추가 시 해당 모듈에만 코드 추가
- 컴포넌트 재사용성 극대화
- 테스트 코드 작성 용이
- 멀티페이지 지원 준비

### 성능 최적화
- 세션 상태 효율적 관리
- AI 스트리밍으로 응답성 향상
- CSS 최적화로 빠른 렌더링

## 🔮 향후 계획

- [ ] 실제 API 연동 (임직원 정보, 일정 관리)
- [ ] 이메일 알림 기능
- [ ] 회의록 자동 생성
- [ ] 캘린더 동기화
- [ ] 다국어 지원
- [ ] 테스트 코드 작성
- [ ] Docker 컨테이너화

## 📄 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.