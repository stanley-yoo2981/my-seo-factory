import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# 1. 인프라 설정 (PDF 462줄 로직 100% 보존)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# 공장 운영 상태 관리 (애니메이션 제어용)
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1  # 1: 분석, 2: 생성, 3: 데이터

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정
st.set_page_config(
    page_title="워드프레스 공장 🏭",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Apple Intelligence Design System (고급 햅틱 & 메아리 애니메이션)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* 메아리(Pulse) 애니메이션 정의 */
    @keyframes echoPulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(29, 29, 31, 0.2); }}
        70% {{ box-shadow: 0 0 0 30px rgba(29, 29, 31, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(29, 29, 31, 0); }}
    }}

    :root {{
        --apple-bg: #F5F5F7;
        --apple-black: #1D1D1F;
        --apple-gray: #86868B;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--apple-bg) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        padding: 60px 120px !important;
    }}

    /* 사이드바 프리미엄 화이트 텍스트 */
    [data-testid="stSidebar"] {{ background-color: #1d1d1f !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {{
        color: #ffffff !important;
        font-weight: 400 !important;
    }}

    /* Bento Card 버튼 고도화 디자인 */
    div.stButton > button {{
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(50px) saturate(200%) !important;
        border-radius: 44px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        height: 480px !important;
        width: 100% !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: var(--apple-black) !important;
        font-size: 32px !important;
        font-weight: 500 !important;
        letter-spacing: -1.5px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }}

    div.stButton > button:hover {{
        background: rgba(255, 255, 255, 1) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 40px 80px rgba(0,0,0,0.08) !important;
    }}

    div.stButton > button:active {{
        transform: scale(0.96) !important;
    }}

    /* 메아리 애니메이션 적용 (현재 단계 카드) */
    .step-active div.stButton > button {{
        animation: echoPulse 2s infinite !important;
        border: 1.5px solid var(--apple-black) !important;
    }}

    /* 로딩바 디자인 커스텀 */
    .stProgress > div > div > div > div {{
        background-color: var(--apple-black) !important;
        height: 6px !important;
    }}

    /* 가이드 박스 (최종 실무 지침서 스타일) */
    .guide-box {{
        background: #ffffff !important;
        border-radius: 50px !important;
        padding: 80px !important;
        margin-top: 100px !important;
        color: var(--apple-black) !important;
        box-shadow: 0 4px 40px rgba(0,0,0,0.02) !important;
    }}
    .guide-box h2 {{ font-size: 48px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px; text-align: center; }}
    .guide-box h3 {{ font-size: 28px; font-weight: 600; margin-top: 60px; margin-bottom: 20px; }}
    .guide-box p {{ font-size: 18px; line-height: 1.8; color: #424245; margin-bottom: 30px; }}
    .guide-box b {{ color: var(--apple-black); }}
    .guide-box .code-inline {{ background: #f5f5f7; padding: 4px 10px; border-radius: 8px; font-family: monospace; font-weight: 500; }}
</style>
""", unsafe_allow_html=True)

# 4. API 상태 확인
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL"))

with st.sidebar:
    st.markdown("### System Status")
    st.write("Naver Core:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI Intelligence:", "🟢" if openai_ok else "🔴")
    st.write("WordPress Engine:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI Vision Generation", value=False)

# 5. 스트리밍 엔진 (로딩바 포함)
def stream_subprocess_with_progress(cmd, env_extra, log_placeholder, progress_bar):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen(cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for i, line in enumerate(proc.stdout):
            buffer.append(line.rstrip("\n"))
            log_placeholder.code("\n".join(buffer[-500:]), language="text")
            current_prog = min(0.95, (i + 1) / 100) 
            progress_bar.progress(current_prog)
        proc.wait()
        progress_bar.progress(1.0)
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"Execution Failed: {e}")
        return -1, []

# 6. 메인 UI 조종실
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 80px; letter-spacing: -3px;'>Law-Brief Intelligence Studio</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

# 카드 1: 키워드 분석
with col1:
    if st.session_state.factory_step == 1:
        st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("키워드 찾기", key="card_kw"):
        with st.status("Analyzing Market Demand...", expanded=True):
            p_bar = st.progress(0)
            stream_subprocess_with_progress([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty(), p_bar)
            st.session_state.factory_step = 2
            st.rerun()
    if st.session_state.factory_step == 1:
        st.markdown('</div>', unsafe_allow_html=True)

# 카드 2: 포스팅 생성
with col2:
    if st.session_state.factory_step == 2:
        st.markdown('<div class="step-active">', unsafe_allow_html=True)
    if st.button("콘텐츠 공장 가동", key="card_post"):
        with st.status("Writing Professional Intelligence...", expanded=True):
            p_bar = st.progress(0)
            env_extra = {"IMAGES_ENABLED": str(images_enabled).lower()}
            rc, _ = stream_subprocess_with_progress([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, st.empty(), p_bar)
            if rc == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2:
        st.markdown('</div>', unsafe_allow_html=True)

# 카드 3: 데이터 분석
with col3:
    if st.button("데이터 분석", key="card_view"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        st.dataframe(df, use_container_width=True, height=450)

# ==========================================
# 7. 워드프레스 검수 가이드
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

st.markdown("<h3>Phase 1. 워드프레스 시스템 진입 및 동기화</h3>", unsafe_allow_html=True)
st.markdown("""
<p>포스팅 생성이 완료되면 시스템은 자동으로 워드프레스에 <b class='code-inline'>임시글(Draft)</b> 상태로 데이터를 전송합니다. 
운영자는 워드프레스 관리자 페이지의 <b class='code-inline'>[글] > [모든 글]</b> 메뉴로 접속하여 방금 생성된 최상단 콘텐츠를 확인하십시오. 
제목을 클릭하여 편집 모드로 진입하는 것이 모든 업무의 시작입니다.</p>
""", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

st.markdown("<h3>Phase 2. Human-AI Collaborative SEO 최적화</h3>", unsafe_allow_html=True)
st.markdown("""
<p>이 단계는 AI가 생산한 원석을 사람이 보석으로 깎는 과정입니다. 문맥의 자연스러움을 최종 검수하고, 
구글의 최신 검색 알고리즘(AEO/SEO)에 맞게 <b>RankMath</b> 설정을 보정해야 합니다.</p>
""", unsafe_allow_html=True)

st.markdown("<h4>1) 스니펫(Snippet) 고도화 편집</h4>")
st.markdown("""
<p>스니펫은 검색 결과에서 사용자에게 가장 먼저 노출되는 요약 정보입니다. 본문 전체를 복사하여 <b>제미나이(Gemini)</b>에 붙여넣은 뒤, 
아래의 <b>Golden Prompt</b>를 입력하여 최적의 값을 도출하십시오.</p>
""", unsafe_allow_html=True)
st.info("💡 Golden Prompt: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.'")
st.markdown("<p>도출된 <b>제목, 퍼머링크, 설명</b> 값을 워드프레스 하단의 RankMath 스니펫 편집기에 그대로 이식하십시오.</p>", unsafe_allow_html=True)
if os.path.exists("step2.png"): st.image("step2.png")
if os.path.exists("step2-1.png"): st.image("step2-1.png")

st.markdown("<h4>2) 포커스 키워드(Focus Keyword) 배치</h4>")
st.markdown("<p>콘텐츠 제목의 가장 첫 번째에 위치한 핵심 키워드를 RankMath의 포커스 키워드 란에 입력하십시오. 이는 구글 검색 봇이 주제를 파악하는 결정적인 지표가 됩니다.</p>", unsafe_allow_html=True)
if os.path.exists("step2-2.png"): st.image("step2-2.png")

st.markdown("<h4>3) Rank Math 지수 80점 돌파 전략</h4>")
st.markdown("""
<p>랭크매스가 안내하는 <b>기본 SEO, 추가, 제목 가독성, 콘텐츠 가독성</b> 항목을 체크하십시오. 
모든 항목에 <b>초록색 체크(v)</b> 표시가 들어올 때까지 문장을 수정하거나 이미지를 보충하십시오. 
최종 점수가 <b>80점 이상</b>이 되어야 상단 노출 경쟁력이 확보됩니다.</p>
""", unsafe_allow_html=True)
if os.path.exists("step2-3.png"): st.image("step2-3.png")
if os.path.exists("step2-4.png"): st.image("step2-4.png")

st.markdown("<h3>Phase 3. 전략적 콘텐츠 발행 및 애드센스 승인 자동화</h3>", unsafe_allow_html=True)
st.markdown("""
<p>구글 애드센스 승인을 위해서는 전문적이고 마이너한 콘텐츠 20개가 핵심입니다. 
하지만 한꺼번에 발행하는 것은 구글 알고리즘이 '스팸'으로 오인할 수 있습니다.</p>
<p><b>운영 지침:</b> 생성된 20개의 콘텐츠 중 10개는 즉시 업로드하고, 나머지 10개는 매일 오전 9시에 순차적으로 발행되도록 예약 기능을 반드시 사용하십시오.</p>
""", unsafe_allow_html=True)
if os.path.exists("step3.png"): st.image("step3.png")
if os.path.exists("step3-1.png"): st.image("step3-1.png")
if os.path.exists("step3-2.png"): st.image("step3-2.png")
if os.path.exists("step4.png"): st.image("step4.png")

st.markdown("</div>", unsafe_allow_html=True)