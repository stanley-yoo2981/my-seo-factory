import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# [!] 버전 및 빌드 태그 (디자인 캐시 박멸용)
BUILD_TAG = "STUDIO-V2.0-PREMIUM-ROSE"

# 1. 시스템 핵심 인프라 (462줄 정밀 로직 보존 및 경로 에러 박멸)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.environ["IMG_DIR"] = IMAGE_FOLDER

# 환경 변수 로드
if os.path.exists(os.path.join(PROJECT_DIR, ".env")):
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))
else:
    try:
        for k, v in st.secrets.items(): os.environ[k] = str(v)
    except: pass

# 공장 가동 상태 관리
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1
if "process_log" not in st.session_state:
    st.session_state.process_log = ""

# 2. 페이지 설정 (따뜻한 감성 테마)
st.set_page_config(
    page_title="Wordpress Factory 2.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. 🎨 프리미엄 UI/UX 디자인 시스템 (Bento + Ripple + Warmth)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@400;700&display=swap');

    /* 🌊 리플(Ripple) 및 메아리 파동 효과 */
    @keyframes rippleEffect {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.4); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 40px rgba(162, 103, 105, 0); transform: scale(1.01); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --bg-warm: #FDF7F0; /* 따뜻한 크림색 배경 */
        --accent-rose: #A26769; /* 로즈 골드 포인트 */
        --text-black: #1D1D1F; /* 깊은 블랙 */
        --card-white: #FFFFFF;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background-color: var(--bg-warm) !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        padding: 80px 8% !important;
    }}

    /* 메인 타이틀 - 고급스러운 무게감 */
    .studio-title {{
        text-align: center;
        color: var(--text-black) !important;
        font-size: 68px;
        font-weight: 700;
        margin-bottom: 90px;
        letter-spacing: -3px;
    }}

    /* 🍱 Bento Card 버튼 - 정사각형의 팬시한 디자인 */
    div.stButton > button {{
        background-color: var(--card-white) !important;
        color: var(--text-black) !important;
        border-radius: 35px !important;
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
        height: 400px !important;
        width: 100% !important;
        font-size: 36px !important;
        font-weight: 700 !important;
        letter-spacing: -1.5px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.03) !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        position: relative;
        overflow: hidden;
    }}

    div.stButton > button:hover {{
        transform: translateY(-15px) !important;
        box-shadow: 0 50px 100px rgba(162, 103, 105, 0.12) !important;
        border-color: var(--accent-rose) !important;
        color: var(--accent-rose) !important;
    }}

    /* 클릭 시 리플 느낌을 주는 액티브 상태 */
    div.stButton > button:active {{
        transform: scale(0.97) !important;
        background-color: #FAF4F4 !important;
    }}

    /* 🌊 현재 진행 단계 강제 유도 (메아리 효과) */
    .active-step div.stButton > button {{
        animation: rippleEffect 2s infinite !important;
        border: 3px solid var(--accent-rose) !important;
    }}

    /* 🎀 여성스러운 로딩바 (Rose-Sandstone 그라데이션) */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 14px !important;
        border-radius: 10px !important;
    }}

    /* 📖 워드프레스 가이드 - 선명한 블랙 텍스트 고정 */
    .premium-guide {{
        background: var(--card-white) !important;
        border-radius: 45px !important;
        padding: 90px !important;
        margin-top: 40px !important; /* 로딩바 아래 위치 */
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}

    .premium-guide h2, .premium-guide h3, .premium-guide p, .premium-guide b, .premium-guide span, .premium-guide li {{
        color: var(--text-black) !important;
        line-height: 1.7 !important;
    }}

    [data-testid="stSidebar"] {{ background-color: var(--text-black) !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 실시간 엔진 함수 (462줄 정밀 로직 실행)
def run_studio_engine(script_name):
    script_path = os.path.join(PROJECT_DIR, script_name)
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    try:
        proc = subprocess.Popen([sys.executable, "-u", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for line in proc.stdout:
            st.session_state.process_log = line.strip()
            # 실시간 로그는 작게 표시
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.error(f"엔진 가동 오류: {e}")
        return -1

# 5. 메인 UI 조종실
st.markdown("<div class='studio-title'>워드프레스 공장</div>", unsafe_allow_html=True)

# Bento Grid Layout
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-step">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn_kw"):
        with st.status("분석 엔진 가동 중...", expanded=False):
            if run_studio_engine("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-step">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="btn_post"):
        with st.status("AI 본문 자동 작성 중...", expanded=False):
            if run_studio_engine("wp_content_generator.py") == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="btn_view"):
        st.session_state.show_data = True

# 6. 🚀 [지시사항 핵심] 가이드 바로 위에 위치한 '이쁜 로딩바'
st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True) # 여백
if st.session_state.factory_step == 1:
    st.write("✨ 현재 **1단계: 키워드 분석** 대기 중...")
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.write("✨ **2단계: 포스팅 생성** 준비 완료!")
    st.progress(0.5)
elif st.session_state.factory_step == 3:
    st.write("✅ **모든 공정 완료!** 워드프레스에서 확인하세요.")
    st.progress(1.0)

# 7. 워드프레스 검수 가이드 (블랙 텍스트 & 프리미엄 디자인)
st.markdown("<div class='premium-guide'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 60px;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

st.markdown("<h3>1. 워드프레스 임시글 확인 및 진입</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 20px;'>포스팅 생성이 완료되면 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속해 보세요. 방금 작성된 따끈따끈한 제목을 클릭해서 편집 화면으로 들어가면 돼요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

st.markdown("<h3 style='margin-top:80px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI 원본 글을 보석으로 다듬는 과정이에요. 문맥상 어색한 부분은 없는지 한 번만 체크해 주세요.</p>", unsafe_allow_html=True)
st.info("💡 꿀팁 프롬프트: '스니펫 편집 정보를 구글 SEO에 가장 최적화 해서 알려줘.'라고 제미나이에 물어보세요!")
if os.path.exists("step2.png"): st.image("step2.png")

st.markdown("<h3 style='margin-top:80px;'>3. 공개 일정 예약 및 발행</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 20px;'>10개는 즉시 발행, 나머지 10개는 매일 오전 9시에 발행되도록 예약을 걸어주면 끝이에요! 정말 고생 많으셨어요!</p>", unsafe_allow_html=True)
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)

# 버전 정보 (캐시 확인용)
st.markdown(f"<div style='text-align: center; color: #8B7E6A; margin-top: 60px; font-size: 14px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)