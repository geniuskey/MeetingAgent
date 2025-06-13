# AI Meeting Booking System

Google Gen AI를 활용한 자연어 기반 회의 예약 시스템입니다.

## 주요 기능

- 🤖 자연어 AI 어시스턴트 (스트리밍 채팅)
- 📅 직관적인 회의 예약 폼
- 📋 이전 회의 컴팩트 카드 뷰
- 💾 회의 히스토리 관리
- 📝 Rich Text 회의 내용 편집
- 🎨 모던한 Material-UI 스타일
- 🖱️ 원클릭 회의 불러오기

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:
```bash
export GOOGLE_API_KEY='your-google-api-key'
```

## 실행 방법

```bash
streamlit run main.py
```

## 프로젝트 구조

```
├── main.py              # 메인 애플리케이션
├── config.py            # 설정 및 상수
├── models.py            # 데이터 모델
├── services.py          # 서비스 로직
├── components.py        # UI 컴포넌트
├── session_manager.py   # 세션 관리
├── styles.py            # CSS 스타일
└── requirements.txt     # 의존성
```

## 사용법

### 자연어 명령 예시
- "내일 오후 2시에 팀 미팅 잡아줘"
- "다음 주 월요일 10시부터 12시까지 프로젝트 리뷰 회의"
- "김철수, 이영희, 박민수와 함께 기획 회의 예약"
- "회의 제목을 '월간 보고서 검토'로 바꿔줘"

### 이전 회의 관리
- **Expander 카드 뷰**: 접었다 펼 수 있는 회의 목록
- **세련된 카드 디자인**: 그라데이션과 호버 효과가 적용된 카드
- **원클릭 불러오기**: 불러오기 버튼으로 즉시 회의 정보 로드
- **공간 효율성**: 접어두면 공간 절약, 필요할 때만 확장

## API 키 설정

Google AI Studio에서 API 키를 발급받아 환경변수로 설정해주세요:

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. API 키 생성
3. 환경변수 설정:
   ```bash
   export GOOGLE_API_KEY='your-api-key-here'
   ```

## 라이브러리 변경사항

- `google-generativeai` → `google-genai` 마이그레이션
- 스트리밍 API 지원 추가
- 모듈화된 아키텍처 적용

## 기술 스택

- **Frontend**: Streamlit, Streamlit-Quill
- **AI**: Google Gen AI (Gemini 2.0)
- **Backend**: Python, Pydantic
- **Styling**: Custom CSS (Material-UI inspired)