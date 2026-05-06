import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# 1. 인프라 설정 (원본 로직 100% 보존)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

# 권한 에러 방지를 위한 경로 설정
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

if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (제목 픽스: 워드프레스 공장)
st.set_page_config(
    page_title="워드프레스 공장",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. 애플 Intelligence UI (글자색 블랙 강제 고정 & 햅틱 조종석)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 첫 번째 단계 유도 메아리 애니메이션 */
    @keyframes echoPulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.3); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 30px rgba(0, 0, 0, 0); transform: scale(1.02); }}
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
        padding: 60px 10% !important;
    }}

    /* 사이드바 가시성 확보 */
    [data-testid="stSidebar"] {{ background-color: #1d1d1f !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* Bento 카드형 버튼 디자인 (이모지 제거 버전) */
    div.stButton > button {{
        background: #ffffff !important;
        border-radius: 44px !important;
        border: 1px solid #e5e5e7 !important;
        height: 450px !important;
        width: 100% !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: var(--apple-black) !important;
        font-size: 34px !important;
        font-weight: 700 !important;
        letter-spacing: -2px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.01) !important;
    }}

    div.stButton > button:hover {{
        transform: translateY(-12px) !important;
        box-shadow: 0 40px 80px rgba(0,0,0,0.1) !important;
        border-color: #d2d2d7 !important;
    }}

    /* 현재 진행 단계 메아리 적용 */
    .step-active div.stButton > button {{
        animation: echoPulse 2s infinite !important;
        border: 2px solid var(--apple-black) !important;
    }}

    /* 워드프레스 검수 가이드 (블랙 텍스트 강제 고정) */
    .guide-box {{
        background: #ffffff !important;
        border-radius: 56px !important;
        padding: 80px !important;
        margin-top: 100px !important;
        border: 1px solid #e5e5e7 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}
    
    /* 💥 가이드 박스 내 모든 글자 선명한 블랙 픽스 💥 */
    .guide-box, .guide-box h2, .guide-box h3, .guide-box p, .guide-box b, .guide-box span {{
        color: #1D1D1F !important;
    }}

    .stProgress > div > div > div > div {{ background-color: var(--apple-black) !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 시스템 상태 확인
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL"))

with st.sidebar:
    st.markdown("### 시스템 가동 현황")
    st.write("네이버 데이터 엔진:", "🟢" if naver_ok else "🔴")
    st.write("지능형 AI 엔진:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스 코어:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 비주얼 생성 모드", value=False)

# 5. 강화된 엔진 스트리밍 엔진
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
        log_placeholder.error(f"가동 실패: {e}")
        return -1, []

# 6. 메인 조종실 UI
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 64px; font-weight: 700; margin-bottom: 100px; letter-spacing: -4px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="card_kw"):
        with st.status("수익성 분석 진행 중..."):
            p_bar = st.progress(0)
            if run_engine_with_progress([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty(), p_bar)[0] == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="card_post"):
        with st.status("지능형 본문 작성 중..."):
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
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# ==========================================
# 7. 워드프레스 검수 가이드 (픽스된 한글 명칭 & 친절 어투)
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 60px;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

# 단계별 안내 함수
def render_step(title, content, img_list=None):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>{content}</p>", unsafe_allow_html=True)
    if img_list:
        for img in img_list:
            if os.path.exists(img): st.image(img, use_container_width=True)

render_step("1. 워드프레스 임시글 확인 및 진입", "포스팅 생성이 완료되면 워드프레스 관리자 페이지의 [글] > [모든 글] 메뉴로 접속해 보세요. 목록에서 방금 작성된 제목을 클릭해서 편집 화면으로 들어가면 돼요!", ["step1.png"])

st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI가 작성한 원문은 사람이 최종적으로 다듬어서 보석으로 만드는 단계예요. 문맥상 어색한 부분은 없는지 한 번만 체크해 주세요.</p>", unsafe_allow_html=True)
st.markdown("<p><b>(1) 스니펫 편집:</b> 제목, 퍼머링크, 설명을 최적화할 거예요. 본문 내용을 모두 복사해서 <b>제미나이</b>에 붙여넣은 뒤 아래 프롬프트를 입력해 보세요.</p>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.'")
st.markdown("<p>제미나이가 알려준 대로 랭크매스(RankMath) 스니펫 편집기에 복사해서 넣어주면 끝이에요.</p>", unsafe_allow_html=True)
render_step("", "", ["step2.png", "step2-1.png"])

st.markdown("<p><b>(2) 포커스 키워드:</b> 제목 맨 앞에 위치한 핵심 키워드를 그대로 입력해 주세요.</p>", unsafe_allow_html=True)
render_step("", "", ["step2-2.png"])

st.markdown("<p><b>(3) RankMath 초록불 만들기:</b> 모든 항목이 초록색 체크(v) 표시가 되도록 살짝만 보완해 보세요. 최종 점수 80점 이상을 목표로 다듬어주면 돼요!</p>", unsafe_allow_html=True)
render_step("", "", ["step2-3.png", "step2-4.png"])

st.markdown("<h3 style='margin-top:60px;'>3. 공개 일정 예약</h3>", unsafe_allow_html=True)
st.markdown("<p>전문 콘텐츠 20개 중 10개는 바로 업로드하고, 나머지 10개는 매일 오전 9시에 발행되도록 예약을 걸어주세요!</p>", unsafe_allow_html=True)
render_step("", "", ["step3.png", "step3-1.png", "step3-2.png", "step4.png", "4단계.png"])

st.markdown("</div>", unsafe_allow_html=True)