import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# [!] 서버 캐시 파괴용 고유 태그 (이게 화면 하단에 보여야 합니다)
BUILD_ID = "FACTORY-STUDIO-V2026-FULL-SPEC"

# 1. 인프라 설정 (사장님의 462줄 정밀 로직 100% 통합)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

# 💥 Permission Error 원천 봉쇄
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
if not os.path.exists(IMAGE_FOLDER):
    try: os.makedirs(IMAGE_FOLDER, exist_ok=True)
    except: IMAGE_FOLDER = "/tmp/images"
os.environ["IMG_DIR"] = IMAGE_FOLDER

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    try:
        for key, value in st.secrets.items(): os.environ[key] = str(value)
    except: pass

# 공장 가동 순서 관리 (메아리 파동 제어용)
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (워드프레스 공장 고정)
st.set_page_config(page_title="워드프레스 공장", layout="wide", initial_sidebar_state="collapsed")

# 3. Apple Intelligence UI System (캐시 파괴용 클래스명 'MASTER')
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 🌊 강력한 메아리(Echo Ripple) */
    @keyframes masterEcho {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); transform: scale(1); }}
        50% {{ box-shadow: 0 0 0 55px rgba(0, 0, 0, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); transform: scale(1); }}
    }}

    :root {{ --m-bg: #F5F5F7; --m-black: #1D1D1F; }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--m-bg) !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* 메인 타이틀 */
    .master-title {{
        text-align: center;
        color: var(--m-black) !important;
        font-size: 64px;
        font-weight: 700;
        margin-bottom: 100px;
        letter-spacing: -4px;
    }}

    /* Bento Card 버튼 - 묵직한 사각형 디자인 (캡슐 스타일 강제 퇴출) */
    div.stButton > button {{
        background: #ffffff !important;
        border-radius: 60px !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        height: 500px !important;
        width: 100% !important;
        color: var(--m-black) !important;
        font-size: 42px !important;
        font-weight: 700 !important;
        letter-spacing: -2.5px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
        transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    div.stButton > button:hover {{
        transform: translateY(-25px) !important;
        box-shadow: 0 70px 140px rgba(0,0,0,0.12) !important;
    }}

    /* 🌊 현재 진행 단계 '메아리' 적용 */
    .master-active div.stButton > button {{
        animation: masterEcho 2s infinite cubic-bezier(0.25, 0, 0, 1) !important;
        border: 4px solid var(--m-black) !important;
    }}

    /* 가이드 박스 - 텍스트 시인성 200% 확보 */
    .master-guide {{
        background: #ffffff !important;
        border-radius: 70px !important;
        padding: 100px !important;
        margin-top: 150px !important;
        border: 1px solid rgba(0, 0, 0, 0.03) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}
    
    /* 💥 모든 글자는 예외 없이 선명한 블랙(#1D1D1F) 💥 */
    .master-guide h2, .master-guide h3, .master-guide p, .master-guide b, .master-guide span, .master-guide li {{
        color: #1D1D1F !important;
    }}

    [data-testid="stSidebar"] {{ background-color: var(--m-black) !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: #ffffff !important; }}
    .stProgress > div > div > div > div {{ background-color: var(--m-black) !important; height: 12px !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 실시간 엔진 함수
def run_factory_engine(script_name, env_ext, log_p, pb):
    script_p = os.path.join(PROJECT_DIR, script_name)
    env = {**os.environ, **env_ext, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen([sys.executable, "-u", script_p], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for i, line in enumerate(proc.stdout):
            buffer.append(line.rstrip())
            log_p.code("\n".join(buffer[-500:]), language="text")
            pb.progress(min(0.95, (i + 1) / 100))
        proc.wait()
        pb.progress(1.0)
        return proc.returncode
    except Exception as e:
        log_p.error(f"Error: {e}")
        return -1

# 5. 메인 UI
st.markdown("<div class='master-title'>워드프레스 공장</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    if st.session_state.factory_step == 1: st.markdown('<div class="master-active">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn1"):
        with st.status("분석 엔진 가동..."):
            if run_factory_engine("keyword_research.py", {}, st.empty(), st.progress(0)) == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with c2:
    if st.session_state.factory_step == 2: st.markdown('<div class="master-active">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="btn2"):
        with st.status("AI 본문 자동 작성..."):
            if run_factory_engine("wp_content_generator.py", {}, st.empty(), st.progress(0)) == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with c3:
    if st.button("데이터 분석", key="btn3"): st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH): st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# 6. 워드프레스 검수 가이드
st.markdown("<div class='master-guide'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)
st.markdown("<h3>1. 워드프레스 임시글 확인 및 진입</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 21px;'>포스팅 생성이 완료되면 [글] > [모든 글] 메뉴에서 방금 작성된 제목을 클릭하세요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)
st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집 정보를 구글 SEO에 가장 최적화 해서 알려줘.'")
if os.path.exists("step2.png"): st.image("step2.png")
st.markdown("<h3 style='margin-top:60px;'>3. 공개 일정 예약</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 21px;'>10개는 즉시 발행, 10개는 예약 발행으로 관리해 주면 완벽해요!</p>", unsafe_allow_html=True)
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align: center; color: #86868b; margin-top: 60px;'>{BUILD_ID}</div>", unsafe_allow_html=True)