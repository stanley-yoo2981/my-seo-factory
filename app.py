import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# 1. 시스템 핵심 인프라 (로직 100% 보존)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

# 쓰기 권한 에러 방지 설정
TEMP_IMG_DIR = "/tmp/images"
os.environ["IMG_DIR"] = TEMP_IMG_DIR

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# 공장 가동 순서 관리 (메아리 애니메이션 제어)
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (제목 픽스: 워드프레스 공장)
st.set_page_config(
    page_title="워드프레스 공장",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. 애플 프리미엄 UI 디자인 (시인성 & 햅틱 & 메아리)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* 메아리(Pulse) 효과 - 첫 번째 작업 강조 */
    @keyframes echoPulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.4); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 25px rgba(0, 0, 0, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); transform: scale(1); }}
    }}

    :root {{
        --apple-bg: #F5F5F7;
        --apple-black: #1D1D1F;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--apple-bg) !important;
        font-family: 'Inter', sans-serif !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        padding: 60px 10% !important;
    }}

    /* 사이드바 가독성 강화 */
    [data-testid="stSidebar"] {{ background-color: #1d1d1f !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Bento 카드 버튼 디자인 */
    div.stButton > button {{
        background: #ffffff !important;
        border-radius: 40px !important;
        border: 1px solid #e5e5e7 !important;
        height: 420px !important;
        width: 100% !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: var(--apple-black) !important;
        font-size: 30px !important;
        font-weight: 700 !important;
        letter-spacing: -1.5px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
    }}

    div.stButton > button:hover {{
        background: #ffffff !important;
        transform: translateY(-10px) !important;
        box-shadow: 0 40px 80px rgba(0,0,0,0.1) !important;
        color: var(--apple-black) !important;
    }}

    /* 메아리 애니메이션 적용 */
    .step-active div.stButton > button {{
        animation: echoPulse 2s infinite !important;
        border: 2px solid #1d1d1f !important;
    }}

    /* 워드프레스 검수 가이드 디자인 (시인성 100%) */
    .guide-box {{
        background: #ffffff !important;
        border-radius: 50px !important;
        padding: 80px !important;
        margin-top: 100px !important;
        color: #1d1d1f !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03) !important;
        border: 1px solid #e5e5e7 !important;
    }}
    .guide-box h2 {{ font-size: 42px; font-weight: 700; margin-bottom: 50px; text-align: center; }}
    .guide-box h3 {{ font-size: 28px; font-weight: 700; margin-top: 60px; margin-bottom: 20px; }}
    .guide-box p {{ font-size: 19px; line-height: 1.8; color: #424245; margin-bottom: 30px; }}
    .guide-box b {{ color: #1d1d1f; font-weight: 700; }}

    /* 로딩바 커스텀 */
    .stProgress > div > div > div > div {{ background-color: #1d1d1f !important; height: 8px !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 시스템 가동 현황
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL"))

with st.sidebar:
    st.markdown("### 시스템 가동 현황")
    st.write("네이버 엔진:", "🟢" if naver_ok else "🔴")
    st.write("지능형 AI:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스 연결:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 비주얼 생성 모드", value=False)

# 5. 로딩바 연동 강화 엔진
def run_engine_with_progress(cmd, env_extra, log_placeholder, progress_bar):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen(cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for i, line in enumerate(proc.stdout):
            buffer.append(line.rstrip())
            log_placeholder.code("\n".join(buffer[-500:]), language="text")
            progress_bar.progress(min(0.95, (i + 1) / 100))
        proc.wait()
        progress_bar.progress(1.0)
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"엔진 오류: {e}")
        return -1, []

# 6. 메인 통합 조종실 (제목 픽스: 워드프레스 공장)
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 700; margin-bottom: 80px; letter-spacing: -3px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="card_kw"):
        with st.status("수익성 키워드 분석 중..."):
            p_bar = st.progress(0)
            if run_engine_with_progress([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty(), p_bar)[0] == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="card_post"):
        with st.status("AI 포스팅 생성 중..."):
            p_bar = st.progress(0)
            rc, _ = run_engine_with_progress([sys.executable, "-u", PUBLISH_SCRIPT], {"IMAGES_ENABLED": str(images_enabled).lower()}, st.empty(), p_bar)
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
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        st.dataframe(df, use_container_width=True, height=450)

# ==========================================
# 7. 워드프레스 검수 가이드 (제목 및 내용 픽스)
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

# 1단계
st.markdown("<h3>1. 워드프레스 임시글 확인 및 진입</h3>", unsafe_allow_html=True)
st.markdown("<p>포스팅 생성이 완료되면 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속해 보세요. 목록에서 방금 작성된 제목을 클릭해서 편집 화면으로 들어가면 돼요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

# 2단계
st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 어색한 부분은 없는지 체크하는 아주 중요한 단계예요.</p>", unsafe_allow_html=True)

st.markdown("<p><b>(1) 스니펫 편집:</b> 제목, 퍼머링크, 설명을 최적화할 거예요. 본문 글을 모두 복사해서 <b>제미나이</b>에 붙여넣은 뒤 아래 프롬프트를 입력해 주세요.</p>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.'")
st.markdown("<p>제미나이가 알려주는 대로 랭크매스(RankMath) 스니펫 편집기에 복사해서 넣어주면 돼요.</p>", unsafe_allow_html=True)
if os.path.exists("step2.png"): st.image("step2.png")
if os.path.exists("step2-1.png"): st.image("step2-1.png")

st.markdown("<p><b>(2) 포커스 키워드:</b> 제목 맨 첫 번째에 있는 키워드를 그대로 입력해 주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step2-2.png"): st.image("step2-2.png")

st.markdown("<p><b>(3) RankMath 초록불 만들기:</b> 기본 SEO, 가독성 항목들이 모두 <b>초록색 체크(v)</b> 표시가 되도록 다듬어 주세요. 최종 점수는 80점 이상을 목표로 해봐요!</p>", unsafe_allow_html=True)
if os.path.exists("step2-3.png"): st.image("step2-3.png")
if os.path.exists("step2-4.png"): st.image("step2-4.png")

# 3단계
st.markdown("<h3 style='margin-top:60px;'>3. 공개 일정 예약</h3>", unsafe_allow_html=True)
st.markdown("<p>구글 애드센스 승인을 위해 전문적인 콘텐츠 20개를 발행할 거예요. <b>이 중 10개는 바로 업로드하고, 나머지 10개는 매일 오전 9시</b>에 발행되도록 예약을 걸어주세요!</p>", unsafe_allow_html=True)
if os.path.exists("step3.png"): st.image("step3.png")
if os.path.exists("step3-1.png"): st.image("step3-1.png")
if os.path.exists("step3-2.png"): st.image("step3-2.png")
# step4 이미지 복구
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)