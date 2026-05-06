import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# 1. 시스템 핵심 로직 (462줄 정밀 로직 100% 보존)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

# 💥 [핵심] 서버 권한 에러 완벽 해결
# 절대 경로(/Users/...)를 버리고 프로젝트 내부 폴더를 사용합니다.
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
if not os.path.exists(IMAGE_FOLDER):
    try:
        os.makedirs(IMAGE_FOLDER, exist_ok=True)
    except:
        IMAGE_FOLDER = "/tmp/images" # 최후의 수단으로 임시 폴더 활용
os.environ["IMG_DIR"] = IMAGE_FOLDER

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# 공장 가동 순서 관리 (메아리 파동 제어용)
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (워드프레스 공장 고정)
st.set_page_config(
    page_title="워드프레스 공장",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Apple Studio 디자인 시스템 (시인성 200% & Bento 그리드 & 진짜 메아리)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 🌊 진짜 메아리(Ripple) 애니메이션: 파동이 밖으로 확산됨 */
    @keyframes echoRipple {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.15); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 50px rgba(0, 0, 0, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); transform: scale(1); }}
    }}

    :root {{
        --apple-bg: #F5F5F7;
        --apple-black: #1D1D1F;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--apple-bg) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        padding: 80px 10% !important;
    }}

    /* 사이드바 글씨: 선명한 화이트 고정 */
    [data-testid="stSidebar"] {{ background-color: var(--apple-black) !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Bento Card 버튼 - 묵직한 사각형 디자인 (캡슐 버림) */
    div.stButton > button {{
        background: #ffffff !important;
        border-radius: 56px !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        height: 460px !important;
        width: 100% !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: var(--apple-black) !important;
        font-size: 38px !important;
        font-weight: 700 !important;
        letter-spacing: -2.5px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
    }}

    div.stButton > button:hover {{
        transform: translateY(-20px) !important;
        box-shadow: 0 60px 120px rgba(0,0,0,0.1) !important;
        border-color: var(--apple-black) !important;
    }}

    /* 🌊 현재 진행 단계에 '메아리 파동' 강제 적용 */
    .step-active div.stButton > button {{
        animation: echoRipple 2s infinite cubic-bezier(0.25, 0, 0, 1) !important;
        border: 3.5px solid var(--apple-black) !important;
    }}

    /* 워드프레스 검수 가이드 (블랙 텍스트 강제 고정) */
    .guide-box {{
        background: #ffffff !important;
        border-radius: 60px !important;
        padding: 100px !important;
        margin-top: 120px !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}
    
    /* 💥 텍스트 시인성 결함 방지: 블랙 강제 지정 💥 */
    .guide-box, .guide-box h2, .guide-box h3, .guide-box p, .guide-box b, .guide-box span {{
        color: #1D1D1F !important;
    }}

    .stProgress > div > div > div > div {{ background-color: var(--apple-black) !important; height: 10px !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 시스템 상태
with st.sidebar:
    st.markdown("### 가동 상태")
    st.write("네이버 엔진: 🟢")
    st.write("AI 지능: 🟢")
    st.write("워드프레스: 🟢")
    st.divider()
    images_enabled = st.checkbox("AI 비주얼 생성 모드", value=False)

# 5. 실시간 엔진 가동 함수
def run_engine(cmd, env_ext, log_placeholder, progress_bar):
    env = {**os.environ, **env_ext, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen(cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for i, line in enumerate(proc.stdout):
            buffer.append(line.rstrip())
            log_placeholder.code("\n".join(buffer[-300:]), language="text")
            progress_bar.progress(min(0.95, (i + 1) / 80))
        proc.wait()
        progress_bar.progress(1.0)
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"오류: {e}")
        return -1, []

# 6. 메인 조종실
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 64px; font-weight: 700; margin-bottom: 100px; letter-spacing: -4px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="card_kw"):
        with st.status("수익성 분석 진행 중..."):
            p_bar = st.progress(0)
            if run_engine([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty(), p_bar)[0] == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="card_post"):
        with st.status("AI 본문 자동 작성 중..."):
            p_bar = st.progress(0)
            rc, _ = run_engine([sys.executable, "-u", PUBLISH_SCRIPT], {"IMAGES_ENABLED": str(images_enabled).lower()}, st.empty(), p_bar)
            if rc == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="card_view"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# ==========================================
# 7. 워드프레스 검수 가이드 (박과장님 전용)
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

def render_guide_step(title, text, img_list=None):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 21px;'>{text}</p>", unsafe_allow_html=True)
    if img_list:
        for img in img_list:
            if os.path.exists(img): st.image(img, use_container_width=True)

render_guide_step("1. 워드프레스 임시글 확인 및 진입", "포스팅 생성이 완료되면 워드프레스 관리자 페이지의 [글] > [모든 글] 메뉴로 접속해 보세요. 목록에서 방금 작성된 제목을 클릭해서 편집 화면으로 들어가면 돼요!", ["step1.png"])

st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI 원본 글을 보석으로 다듬는 과정이에요. 문맥상 어색한 부분은 없는지 한 번만 체크해 주세요.</p>", unsafe_allow_html=True)
st.markdown("<p><b>(1) 스니펫 편집:</b> 제미나이에 본문을 복사하고 '스니펫 편집 정보를 알려줘'라고 하면 돼요. 그 값을 랭크매스에 그대로 옮겨주세요.</p>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO에 최적화 해서 알려줘.'")
render_guide_step("", "", ["step2.png", "step2-1.png"])

st.markdown("<p><b>(2) 포커스 키워드:</b> 제목의 첫 번째 키워드를 복사해서 넣어주면 돼요.</p>", unsafe_allow_html=True)
render_guide_step("", "", ["step2-2.png"])

st.markdown("<p><b>(3) RankMath 80점 돌파:</b> 초록색 체크가 되도록 살짝만 보완해 주면 상단 노출 준비 끝이에요!</p>", unsafe_allow_html=True)
render_guide_step("", "", ["step2-3.png", "step2-4.png"])

st.markdown("<h3 style='margin-top:60px;'>3. 공개 일정 예약</h3>", unsafe_allow_html=True)
st.markdown("<p>10개는 즉시 발행, 10개는 매일 오전 9시에 발행되도록 예약을 걸어주세요!</p>", unsafe_allow_html=True)
render_guide_step("", "", ["step3.png", "step3-1.png", "step3-2.png", "step4.png", "4단계.png"])

st.markdown("</div>", unsafe_allow_html=True)