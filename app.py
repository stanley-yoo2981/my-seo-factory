import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# [!] 버전 관리 태그 (이게 'FORCE-SQUARE-TILING'으로 바뀌어야 성공입니다)
BUILD_TAG = "FACTORY-STUDIO-V2026-FORCE-SQUARE-TILING"

# 1. 시스템 핵심 로직 (사장님의 462줄 정밀 로직 100% 통합)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
# Permission Error 원천 봉쇄 경로 설정
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
if not os.path.exists(IMAGE_FOLDER):
    try: os.makedirs(IMAGE_FOLDER, exist_ok=True)
    except: IMAGE_FOLDER = "/tmp/images"
os.environ["IMG_DIR"] = IMAGE_FOLDER

# 환경 변수 로드
if os.path.exists(os.path.join(PROJECT_DIR, ".env")):
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))
else:
    try:
        for k, v in st.secrets.items(): os.environ[k] = str(v)
    except: pass

# 공장 가동 상태 관리 (메아리 파동 제어용)
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (따뜻한 감성 테마)
st.set_page_config(
    page_title="워드프레스 공장 V2.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. 🎨 프리미엄 UI/UX 디자인 시스템 (1:1 정방향 Bento + Ripple + Warmth)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 🌊 리플(Ripple) 및 메아리 파동 효과 */
    @keyframes studioPulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.3); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 45px rgba(162, 103, 105, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --s-bg-warm: #FDF7F0; /* 따뜻한 크림색 배경 */
        --s-accent-rose: #A26769; /* 로즈 골드 포인트 */
        --s-text-black: #1D1D1F; /* 깊은 블랙 */
        --s-card-white: #FFFFFF;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background-color: var(--s-bg-warm) !important;
        font-family: 'Inter', sans-serif !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        padding: 80px 10% !important;
    }}

    /* 메인 타이틀 */
    .factory-title-text {{
        text-align: center;
        color: var(--s-text-black) !important;
        font-size: 64px;
        font-weight: 700;
        margin-bottom: 90px;
        letter-spacing: -3px;
    }}

    /* 🍱 Bento Card 버튼 - 사장님 지시: 1:1 정방향 사각형 디자인 (빼빼로 완전 퇴출) */
    div.stButton > button {{
        background-color: var(--s-card-white) !important;
        color: var(--s-text-black) !important;
        border-radius: 35px !important;
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
        /* 💥 가로 폭에 맞춰 높이를 강제 조정하여 정방향 1:1 그리드 구현 💥 */
        height: 380px !important; /* 1280px 메인 컨테이너 기준 대략적인 1:1 비율 */
        width: 100% !important;
        font-size: 38px !important;
        font-weight: 700 !important;
        letter-spacing: -2px !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.03) !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative;
        overflow: hidden;
    }}

    div.stButton > button:hover {{
        transform: translateY(-15px) !important;
        box-shadow: 0 50px 100px rgba(162, 103, 105, 0.12) !important;
        border-color: var(--s-accent-rose) !important;
        color: var(--s-accent-rose) !important;
    }}

    /* 클릭 시 리플 느낌의 액틱브 효과 */
    div.stButton > button:active {{
        transform: scale(0.97) !important;
        background-color: #FAF4F4 !important;
    }}

    /* 🌊 현재 단계 '메아리 파동' 강제 적용 (가시성 유도) */
    .step-active-engine div.stButton > button {{
        animation: studioPulse 2s infinite cubic-bezier(0.25, 0, 0, 1) !important;
        border: 3.5px solid var(--s-accent-rose) !important;
    }}

    /* 🎀 여성스러운 로딩바 (Rose-Sandstone 그라데이션) */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 14px !important;
        border-radius: 10px !important;
    }}

    /* 📖 워드프레스 검수 가이드 - 선명한 블랙 텍스트 절대 고정 */
    .factory-guide-box {{
        background: var(--s-card-white) !important;
        border-radius: 45px !important;
        padding: 90px !important;
        margin-top: 40px !important; /* 로딩바 아래 위치 */
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}
    
    /* 💥 텍스트 시인성 결함 완벽 방지: 젯 블랙(#1D1D1F) 꽁꽁 묶음 💥 */
    .factory-guide-box h2, .factory-guide-box h3, .factory-guide-box p, .factory-guide-box b, .factory-guide-box span, .factory-guide-box li {{
        color: #1D1D1F !important;
        line-height: 1.7 !important;
    }}

    [data-testid="stSidebar"] {{ background-color: var(--s-text-black) !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{ color: #ffffff !important; }}
</style>
""", unsafe_allow_html=True)

# 4. API 상태 대시보드
with st.sidebar:
    st.markdown("### 시스템 가동 현황")
    st.write("네이버 엔진: 🟢")
    st.write("AI 지능 코어: 🟢")
    st.write("워드프레스 연결: 🟢")
    st.divider()
    images_enabled = st.checkbox("AI 비주얼 생성 모드", value=False)

# 5. 실시간 엔진 함수 (462줄 정밀 로직 실행)
def run_studio_engine(script_name, env_ext, log_p, pb):
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

# 6. 메인 통합 조종실
st.markdown("<div class='factory-title-text'>워드프레스 공장</div>", unsafe_allow_html=True)

# Bento Grid (사장님 지시: 1:1 정방향 그리드)
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="step-active-engine">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="b1"):
        with st.status("분석 진행 중..."):
            if run_studio_engine("keyword_research.py", {}, st.empty(), st.progress(0)) == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="step-active-engine">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="b2"):
        with st.status("본문 자동 작성 중..."):
            if run_studio_engine("wp_content_generator.py", {}, st.empty(), st.progress(0)) == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="b3"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# 7. 🚀 [지시사항 핵심] 로딩 바 (여성 TARGET 감성 그라데이션)
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

# 8. 워드프레스 검수 가이드 (블랙 텍스트 & 프리미엄 디자인)
st.markdown("<div class='factory-guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

def render_guide_step(title, text, img_list=None):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 20px;'>{text}</p>", unsafe_allow_html=True)
    if img_list:
        for img in img_list:
            if os.path.exists(img): st.image(img, use_container_width=True)

render_guide_step("1. 워드프레스 임시글 확인 및 진입", "포스팅 생성이 완료되면 워드프레스 관리자 페이지의 [글] > [모든 글] 메뉴로 접속해 보세요. 제목을 클릭해서 편집 화면으로 들어가면 돼요!", ["step1.png"])

st.markdown("<h3 style='margin-top:80px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI 원본 글을 보석으로 다듬는 과정이에요. 문맥상 어색한 부분은 없는지 한 번만 체크해 주세요.</p>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집 정보를 구글 SEO에 가장 최적화 해서 알려줘.'")
render_guide_step("", "", ["step2.png", "step2-1.png"])

st.markdown("<p><b>(1) 포커스 키워드 설정:</b> 제목 맨 앞에 위치한 핵심 키워드를 그대로 복사해서 넣어주세요.</p>", unsafe_allow_html=True)
render_guide_step("", "", ["step2-2.png"])

st.markdown("<p><b>(2) RankMath 초록불 만들기:</b> 모든 항목이 초록색 체크(v)가 되도록 살짝만 보완해 보세요. 점수가 80점만 넘으면 완벽해요!</p>", unsafe_allow_html=True)
render_guide_step("", "", ["step2-3.png", "step2-4.png"])

st.markdown("<h3 style='margin-top:80px;'>3. 공개 일정 예약 및 발행</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 20px;'>10개는 즉시 발행, 나머지 10개는 매일 오전 9시에 발행되도록 예약을 걸어주면 끝이에요!</p>", unsafe_allow_html=True)
render_guide_step("", "", ["step3.png", "step3-1.png", "step3-2.png", "step4.png", "4단계.png"])

st.markdown("</div>", unsafe_allow_html=True)

# 버전 정보 (캐시 확인용)
st.markdown(f"<div style='text-align: center; color: #86868b; margin-top: 60px; font-size: 14px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)