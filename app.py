import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [!] 강제 업데이트 확인용 태그
BUILD_TAG = "V2.0-SQUARE-FIX-FINAL"

# 1. 경로 에러 완벽 차단 (절대 경로 및 작업 디렉토리 픽스)
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

# 3. 🎨 스트림릿 강제 오버라이드 CSS (빼빼로 & 흰 글씨 박멸)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 🌊 리플(Ripple) 파동 애니메이션 */
    @keyframes rippleAnim {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.4); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 35px rgba(162, 103, 105, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --bg-color: #FDF7F0; /* 크림색 배경 */
        --rose: #A26769;
        --pure-black: #1D1D1F !important;
    }}

    /* 전체 배경 강제 적용 */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: var(--bg-color) !important;
        color: var(--pure-black) !important;
    }}

    /* 💥 1:1 정방향 타일 강제 (빼빼로 박멸) 💥 */
    /* 스트림릿의 실제 버튼 태그를 정확히 타격합니다 */
    button[data-testid="baseButton-secondary"] {{
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 35px !important;
        border: 1px solid rgba(162, 103, 105, 0.2) !important;
        
        width: 100% !important;
        height: auto !important;
        aspect-ratio: 1 / 1 !important; /* 1:1 비율 완벽 고정 */
        
        font-size: clamp(24px, 2vw, 36px) !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    button[data-testid="baseButton-secondary"]:hover {{
        transform: translateY(-8px) !important;
        box-shadow: 0 40px 80px rgba(162, 103, 105, 0.15) !important;
        border-color: var(--rose) !important;
    }}

    /* 🌊 리플 효과 적용 */
    .active-step button[data-testid="baseButton-secondary"] {{
        animation: rippleAnim 2s infinite !important;
        border: 4px solid var(--rose) !important;
    }}

    /* 🎀 그라데이션 로딩바 */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 12px !important;
    }}

    /* 💥 흰색 글씨 박멸 (다크모드 오버라이드) 💥 */
    .guide-box {{
        background-color: #FFFFFF !important;
        border-radius: 40px !important;
        padding: 80px !important;
        margin-top: 40px !important;
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
    }}

    /* 스트림릿 내의 모든 텍스트 요소를 검은색으로 강제 변경 */
    .guide-box *, [data-testid="stMarkdownContainer"] *, [data-testid="stText"] *, .stAlert * {{
        color: #1D1D1F !important;
    }}

    /* 상태창(Status) 배경 하얗게, 글씨 검게 */
    [data-testid="stStatusWidget"] {{ background-color: #FFFFFF !important; border: 1px solid #A26769 !important; }}
    [data-testid="stStatusWidget"] * {{ color: #1D1D1F !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 🚨 강력한 파일 실행 엔진 (Errno 2 완벽 해결)
def run_factory_script(filename):
    script_path = os.path.join(PROJECT_DIR, filename)
    
    # 1. 파일 존재 여부 먼저 확인
    if not os.path.exists(script_path):
        st.error(f"❌ '{filename}' 파일을 찾을 수 없습니다. 깃허브에 파일이 있는지 확인해주세요.")
        return -1
    
    try:
        # 2. cwd=PROJECT_DIR 옵션으로 서버가 정확한 위치에서 실행하도록 강제
        proc = subprocess.Popen(
            [sys.executable, "-u", script_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True, 
            cwd=PROJECT_DIR, # 핵심 해결책
            bufsize=1
        )
        for line in proc.stdout:
            st.write(f"⚙️ {line.strip()}")
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.error(f"❌ 가동 오류: {str(e)}")
        return -1

# 5. 메인 UI 조종실
st.markdown("<h1 style='text-align:center; margin-bottom:80px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-step">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn1"):
        with st.status("분석 진행 중...", expanded=True):
            if run_factory_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-step">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="btn2"):
        with st.status("본문 생성 중...", expanded=True):
            if run_factory_script("wp_content_generator.py") == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="btn3"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# 6. 🚀 여성스러운 그라데이션 로딩바 (가이드 바로 위)
st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
if st.session_state.factory_step == 1:
    st.markdown("<p style='font-weight:700;'>✨ 1단계: 키워드 분석 대기 중...</p>", unsafe_allow_html=True)
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.markdown("<p style='font-weight:700;'>✨ 2단계: 포스팅 생성 준비 완료!</p>", unsafe_allow_html=True)
    st.progress(0.5)
else:
    st.markdown("<p style='font-weight:700;'>✅ 모든 공정 완료!</p>", unsafe_allow_html=True)
    st.progress(1.0)

# 7. 워드프레스 검수 가이드
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; margin-bottom:50px;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

st.markdown("<h3>1. 워드프레스 임시글 확인</h3>", unsafe_allow_html=True)
st.markdown("<p>포스팅 생성이 완료되면 워드프레스 [글] 메뉴에서 확인하세요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수</h3>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집 정보를 구글 SEO에 최적화해서 알려줘.'")
if os.path.exists("step2.png"): st.image("step2.png")

st.markdown("<h3 style='margin-top:60px;'>3. 예약 발행</h3>", unsafe_allow_html=True)
st.markdown("<p>일부 포스팅은 즉시 발행하고, 나머지는 오전 9시에 예약 발행으로 세팅해주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)

# 버전 확인
st.markdown(f"<div style='text-align:center; color:#8B7E6A; margin-top:50px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)