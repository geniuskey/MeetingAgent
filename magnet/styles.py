"""
CSS 스타일 모듈
"""

def get_css_styles():
    """앱의 CSS 스타일을 반환"""
    return """
<style>
    /* Streamlit 기본 UI 제거 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 상단 컬러 바 제거 */
    .stApp > header {
        background-color: transparent;
    }

    /* 전체 앱 배경 - 보라색 배경 제거 */
    .stApp {
        background: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 메인 컨테이너 - 카드 스타일 강화 */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: none;
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        margin: 2rem;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }

    /* 사이드바 스타일링 및 상단 공백 제거 */
    .css-1d391kg {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
        border-radius: 0 20px 20px 0;
        box-shadow: 5px 0 20px rgba(0, 0, 0, 0.1);
        padding-top: 1rem !important;
    }

    /* 사이드바 첫 번째 요소의 상단 마진 제거 */
    .css-1d391kg .block-container {
        padding-top: 1rem !important;
    }

    .css-1d391kg .stMarkdown {
        color: white;
    }

    /* 사이드바 제목 */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: white !important;
        margin-top: 0 !important;
    }

    /* 사이드바 텍스트 */
    .css-1d391kg p, .css-1d391kg label {
        color: #ecf0f1 !important;
    }

    /* 메인 헤더 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: none;
    }

    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }

    /* 사이드바 로고 - 상단 마진 제거 */
    .sidebar-logo {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
        margin-top: 0 !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }

    .sidebar-logo h2 {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        margin-top: 0 !important;
    }

    .sidebar-logo p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0;
        font-size: 0.9rem;
    }

    /* 회의 카드 */
    .meeting-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin-bottom: 0.8rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        cursor: pointer;
    }

    .meeting-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }

    /* 프롬프트 컨테이너 */
    .prompt-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* 예약 폼 */
    .booking-form {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid rgba(102, 126, 234, 0.1);
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }

    /* 입력 필드 스타일링 */
    .stTextInput > div > div > input {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    .stTextArea > div > div > textarea {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        min-height: 120px;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* 버튼 스타일링 - Material-UI 스타일 */
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
        min-width: 64px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 3px 1px -2px rgba(0,0,0,0.2), 0 2px 2px 0 rgba(0,0,0,0.14), 0 1px 5px 0 rgba(0,0,0,0.12);
        cursor: pointer;
        outline: none;
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        background: #5a67d8;
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.2), 0 4px 5px 0 rgba(0,0,0,0.14), 0 1px 10px 0 rgba(0,0,0,0.12);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        background: #4c51bf;
        box-shadow: 0 5px 5px -3px rgba(0,0,0,0.2), 0 8px 10px 1px rgba(0,0,0,0.14), 0 3px 14px 2px rgba(0,0,0,0.12);
        transform: translateY(0);
    }

    .stButton > button:focus {
        outline: none;
        box-shadow: 0 3px 1px -2px rgba(0,0,0,0.2), 0 2px 2px 0 rgba(0,0,0,0.14), 0 1px 5px 0 rgba(0,0,0,0.12), 0 0 0 3px rgba(102, 126, 234, 0.4);
    }

    /* 버튼 ripple 효과 (Material-UI의 특징적인 효과) */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }

    .stButton > button:active::before {
        width: 300px;
        height: 300px;
    }

    /* 사이드바 버튼 스타일 */
    .css-1d391kg .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }

    .css-1d391kg .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
    }

    .css-1d391kg .stButton > button:active {
        background: rgba(255, 255, 255, 0.3);
    }

    /* 다양한 버튼 variant 스타일 */
    .stButton > button[kind="primary"] {
        background: #667eea;
    }

    .stButton > button[kind="secondary"] {
        background: transparent;
        color: #667eea;
        border: 1px solid #667eea;
        box-shadow: none;
    }

    .stButton > button[kind="secondary"]:hover {
        background: rgba(102, 126, 234, 0.04);
        box-shadow: 0 2px 4px -1px rgba(0,0,0,0.2), 0 4px 5px 0 rgba(0,0,0,0.14), 0 1px 10px 0 rgba(0,0,0,0.12);
    }

    /* 성공/에러 메시지 */
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #b8daff;
        color: #155724;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
        font-weight: 500;
    }

    .error-message {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.2);
        font-weight: 500;
    }

    /* 데이터프레임 스타일링 */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* 확장 가능한 섹션 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        font-weight: 600;
    }

    /* 날짜/시간 입력 */
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }

    .stDateInput > div > div > input:focus,
    .stTimeInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }

    .stDateInput > div > div > input:focus-visible,
    .stTimeInput > div > div > input:focus-visible {
        outline: none !important;
        border-color: #667eea !important;
    }

    /* 날짜/시간 picker 드롭다운 */
    .stDateInput div[data-baseweb="popover"] {
        border: 2px solid #667eea !important;
        border-radius: 10px !important;
    }

    .stTimeInput div[data-baseweb="popover"] {
        border: 2px solid #667eea !important;
        border-radius: 10px !important;
    }

    /* 선택박스 */
    .stSelectbox > div > div > select {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }

    .stSelectbox > div > div > select:focus-visible {
        outline: none !important;
        border-color: #667eea !important;
    }

    /* Streamlit 기본 focus 색상 전역 덮어쓰기 */
    input:focus,
    textarea:focus,
    select:focus {
        outline: none !important;
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* 기본 브라우저 outline 제거 */
    *:focus {
        outline: none !important;
    }

    /* Streamlit 컴포넌트별 focus 상태 */
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stDateInput"] input:focus,
    div[data-testid="stTimeInput"] input:focus,
    div[data-testid="stSelectbox"] select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* 정보/경고 메시지 개선 */
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-radius: 12px;
        border-left: 4px solid #17a2b8;
    }

    .stWarning {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-radius: 12px;
        border-left: 4px solid #ffc107;
    }

    .stSuccess {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-radius: 12px;
        border-left: 4px solid #28a745;
    }

    /* 스크롤바 스타일링 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }

    /* Quill 에디터 스타일링 */
    .ql-editor {
        min-height: 200px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 14px;
        line-height: 1.6;
    }

    .ql-toolbar {
        border-top: 2px solid #e9ecef;
        border-left: 2px solid #e9ecef;
        border-right: 2px solid #e9ecef;
        border-bottom: none;
        border-radius: 10px 10px 0 0;
        background: #f8f9fa;
    }

    .ql-container {
        border-left: 2px solid #e9ecef;
        border-right: 2px solid #e9ecef;
        border-bottom: 2px solid #e9ecef;
        border-top: none;
        border-radius: 0 0 10px 10px;
        background: white;
    }

    .ql-toolbar:hover,
    .ql-container:focus-within {
        border-color: #667eea;
    }

    .ql-editor.ql-blank::before {
        color: #6c757d;
        font-style: italic;
    }

    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
            margin: 0.5rem;
        }

        .main-header h1 {
            font-size: 2rem;
        }

        .booking-form {
            padding: 1.5rem;
        }
    }
</style>
"""