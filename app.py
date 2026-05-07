import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# [!] 빌드 태그 (이게 'MASTER-FIX-FINAL-01'로 보여야 합니다)
BUILD_TAG = "MASTER-FIX-FINAL-01"

# 1. 🔍 파일 경로 자동 추적 시스템 (사장님을 괴롭힌 경로 에러 박멸)
def get_script_path(filename):
    """현재 실행 환경에서 파일의 절대 경로를 찾아냅니다."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    target_path = os.path.join(base_path, filename)
    
    # 만약 파일을 못 찾으면 하위 폴더까지 뒤집니다.
    if not os.path.exists(target_path):
        for root, dirs, files in os.walk(base_path):
            if filename in files:
                return os.path.join(root, filename)
    return target_path

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.environ["IMG_DIR"] = IMAGE_FOLDER

if os.path.exists(os.path.join(PROJECT_DIR, ".env")):
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))
else:
    try:
        for k, v in st.secrets.items(): os.environ[k] = str(v)
    except: pass

if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

# 2. 페이지 설정
st.set_page_config(page_title="워드프레스 공장 V2.0", layout="wide", initial_sidebar_state="collapsed")

# 3. 🎨 [디자인 최종 병기] 1:1 정방향 강제 + 블랙 텍스트 절대 고정
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 🌊 리플(Ripple) 애니메이션 */
    @keyframes rippleAnim {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.4); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 35px rgba(162, 103, 105, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --bg: #FDF7F0; 
        --rose: #A26769;
        --black: #1D1D1F !important;
    }}

    /* 전체 배경 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: var(--bg) !important;
    }}

    /* 🍱 1:1 정방향 Bento 타일 강제 구현 (빼빼로 모양 방지) */
    div.stButton > button {{
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 40px !important;
        border: 1px solid rgba(162, 103, 105, 0.2) !important;
        
        /* 💥 물리적 1:1 비율 강제 고정 💥 */
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; 
        height: auto !important;
        
        font-size: clamp(18px, 2.5vw, 32px) !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
        transition: all 0.4s ease !important;
        margin-bottom: 20px;
    }}

    div.stButton > button:hover {{
        transform: translateY(-10px) !important;
        box-shadow: 0 40px 80px rgba(162, 103, 105, 0.15) !important;
        border-color: var(--rose) !important;
    }}

    /* 🌊 현재 진행 단계 리플 */
    .active-engine div.stButton > button {{
        animation: rippleAnim 2s infinite !important;
        border: 4px solid var(--rose) !important;
    }}

    /* 🎀 여성스러운 로딩바 */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 14px !important;
    }}

    /* 📖 가이드 박스 & 모든 텍스트 - 블랙 픽스 (#1D1D1F) */
    .guide-card {{
        background: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 80px !important;
        margin-top: 40px !important;
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}

    /* 모든 텍스트 요소를 블랙으로 강제 압수 */
    .guide-card *, div[data-testid="stMarkdownContainer"] p, 
    div[data-testid="stMarkdownContainer"] h2, div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stStatusWidget"] *, .stAlert p {{
        color: #1D1D1F !important;
        opacity: 1 !important;
    }}

    /* 상태 표시줄(st.status) 배경도 선명하게 */
    div[data-testid="stStatusWidget"] {{
        background-color: #FFFFFF !important;
        border: 1px solid var(--rose) !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. 실시간 엔진 실행 함수
def run_script(filename):
    path = get_script_path(filename)
    if not os.path.exists(path):
        st.error(f"❌ 파일을 찾을 수 없습니다: {filename}\n(예상 경로: {path})")
        return -1
    
    try:
        proc = subprocess.Popen([sys.executable, "-u", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in proc.stdout:
            st.text(line.rstrip()) # 로그 출력
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.error(f"❌ 가동 중 오류 발생: {e}")
        return -1

# 5. 메인 UI 조종실
st.markdown("<h1 style='text-align:center; color:#1D1D1F; font-size:64px; font-weight:800; margin-bottom:100px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="b1"):
        with st.status("🔍 분석 엔진 가동 중...", expanded=True):
            if run_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="b2"):
        with st.status("✍️ AI 본문 작성 중...", expanded=True):
            if run_script("wp_content_generator.py") == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="b3"):
        st.session_state.show_data = True

# 🚀 [로딩바] 가이드 바로 위 (이쁜 그라데이션)
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
if st.session_state.factory_step == 1:
    st.markdown("<p style='font-weight:700;'>✨ 1단계: 분석 대기 중</p>", unsafe_allow_html=True)
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.markdown("<p style='font-weight:700;'>✨ 2단계: 생성 준비 완료</p>", unsafe_allow_html=True)
    st.progress(0.5)
else:
    st.markdown("<p style='font-weight:700;'>✅ 모든 공정 완료</p>", unsafe_allow_html=True)
    st.progress(1.0)

# 📖 워드프레스 검수 가이드 (블랙 텍스트 강제)
st.markdown("<div class='guide-card'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; margin-bottom:50px;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

st.markdown("<h3>1. 워드프레스 임시글 확인</h3>", unsafe_allow_html=True)
st.markdown("<p>포스팅 생성이 완료되면 워드프레스 [글] 메뉴에서 확인하세요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수</h3>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집 정보를 구글 SEO에 최적화해서 알려줘.'")
if os.path.exists("step2.png"): st.image("step2.png")

st.markdown("<h3 style='margin-top:60px;'>3. 예약 발행</h3>", unsafe_allow_html=True)
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; color:#8B7E6A; margin-top:60px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)