import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# 1. 시스템 인프라 로직 (PDF 462줄 정밀 로직 100% 보존)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

# 쓰기 권한 및 스트리밍 설정
TEMP_IMG_DIR = "/tmp/images"
os.environ["IMG_DIR"] = TEMP_IMG_DIR

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 스트림릿 클라우드 Secrets 보안 금고 대응
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# 공장 가동 스텝 관리 (메아리 애니메이션용)
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

# 3. Apple Intelligence UI System (글자색 절대 고정)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 메아리(Pulse) 효과 - 첫 번째 작업 유도 */
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

    /* 사이드바 글씨: 무조건 화이트 */
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
        transform: translateY(-10px) !important;
        box-shadow: 0 40px 80px rgba(0,0,0,0.1) !important;
    }}

    /* 현재 작업 메아리 적용 */
    .step-active div.stButton > button {{
        animation: echoPulse 2s infinite !important;
        border: 2px solid #1d1d1f !important;
    }}

    /* 워드프레스 검수 가이드 박스 - 글자색 강제 픽스 */
    .guide-box {{
        background: #ffffff !important;
        border-radius: 50px !important;
        padding: 80px !important;
        margin-top: 100px !important;
        border: 1px solid #e5e5e7 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.03) !important;
    }}

    /* 💥 가이드 박스 안의 모든 텍스트는 예외 없이 블랙(#1D1D1F) 💥 */
    .guide-box, .guide-box div, .guide-box p, .guide-box span, .guide-box h2, .guide-box h3, .guide-box h4, .guide-box li, .guide-box b {{
        color: #1D1D1F !important;
    }}

    .stProgress > div > div > div > div {{ background-color: #1d1d1f !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 시스템 가동 현황
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL"))

with st.sidebar:
    st.markdown("### 시스템 가동 현황")
    st.write("네이버 데이터 엔진:", "🟢" if naver_ok else "🔴")
    st.write("AI 인텔리전스:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스 엔진:", "🟢" if wp_ok else "🔴")
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
        log_placeholder.error(f"엔진 오류 발생: {e}")
        return -1, []

# 6. 메인 조종실
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 700; margin-bottom: 80px; letter-spacing: -3px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="card_kw"):
        with st.status("수익성 분석 엔진 가동 중..."):
            p_bar = st.progress(0)
            if run_engine_with_progress([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty(), p_bar)[0] == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="card_post"):
        with st.status("AI 본문 자동 생성 중..."):
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
# 7. 워드프레스 검수 가이드 (제목 및 내용 픽스)
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 50px;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

# 1단계
st.markdown("<h3>1. 워드프레스 임시글 확인 및 진입</h3>", unsafe_allow_html=True)
st.markdown("<p>포스팅 생성이 완료되면 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속해 보세요. 목록에서 방금 작성된 따끈따끈한 제목을 클릭해서 편집 화면으로 들어가면 돼요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

# 2단계
st.markdown("<h3 style='margin-top:60px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI가 작성한 원석을 사람이 최종적으로 다듬어서 보석으로 만드는 단계예요. 문맥상 어색한 부분은 없는지 한 번만 체크해 주세요.</p>", unsafe_allow_html=True)

st.markdown("<p><b>(1) 스니펫 편집:</b> 제목, 퍼머링크, 설명을 검색 엔진에 맞게 고칠 거예요. 본문 내용을 모두 복사해서 <b>제미나이</b>에 붙여넣은 뒤 아래 프롬프트를 써보세요.</p>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.'")
st.markdown("<p>그다음 제미나이가 알려준 대로 랭크매스(RankMath) 스니펫 편집기에 예쁘게 옮겨주면 돼요.</p>", unsafe_allow_html=True)
if os.path.exists("step2.png"): st.image("step2.png")
if os.path.exists("step2-1.png"): st.image("step2-1.png")

st.markdown("<p><b>(2) 포커스 키워드:</b> 제목의 맨 앞에 있는 핵심 키워드를 그대로 복사해서 넣어주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step2-2.png"): st.image("step2-2.png")

st.markdown("<p><b>(3) RankMath 점수 올리기:</b> 모든 항목이 <b>초록색 체크(v)</b> 표시가 되도록 살짝만 보완해 주세요. 최종 점수 80점만 넘기면 상단 노출 준비 끝이에요!</p>", unsafe_allow_html=True)
if os.path.exists("step2-3.png"): st.image("step2-3.png")
if os.path.exists("step2-4.png"): st.image("step2-4.png")

# 3단계
st.markdown("<h3 style='margin-top:60px;'>3. 공개 일정 예약</h3>", unsafe_allow_html=True)
st.markdown("<p>애드센스 승인을 위해 전문적인 콘텐츠 20개를 만들 거예요. <b>이 중 10개는 바로 업로드하고, 나머지 10개는 매일 오전 9시</b>에 발행되도록 예약을 걸어주면 완벽해요!</p>", unsafe_allow_html=True)
if os.path.exists("step3.png"): st.image("step3.png")
if os.path.exists("step3-1.png"): st.image("step3-1.png")
if os.path.exists("step3-2.png"): st.image("step3-2.png")
# step4/4단계 이미지 확실히 노출
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)