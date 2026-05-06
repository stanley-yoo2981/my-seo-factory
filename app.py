import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# ==========================================
# 1. 시스템 핵심 인프라 (PDF 17-25 로직 100% 복구)
# ==========================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 스트림릿 클라우드 Secrets 보안 금고 대응
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# ==========================================
# 2. 프리미엄 조종석 설정
# ==========================================
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 3. Apple Haptic Studio CSS (시인성 & 햅틱 완결)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    @keyframes studioReveal {
        0% { transform: scale(0.97); opacity: 0; filter: blur(15px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    :root {
        --bg-apple: #F5F5F7;
        --titanium-black: #1D1D1F;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-apple) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 80px 100px !important;
        animation: studioReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* [사이드바] 어두운 배경에 무조건 화이트 글씨 */
    [data-testid="stSidebar"] { background-color: #262730 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* [Bento Card 버튼] 햅틱 피드백 및 미니멀리즘 */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 40px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05) !important;
        height: 420px !important;
        width: 100% !important;
        transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1) !important;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 40px !important;
        color: var(--titanium-black) !important;
        font-size: 28px !important;
        font-weight: 600 !important;
        letter-spacing: -1px !important;
    }

    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.7) !important;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-12px) !important;
    }

    div.stButton > button:active {
        transform: scale(0.93) translateY(-5px) !important;
        transition: all 0.1s ease !important;
    }

    /* 로딩바 커스텀 스타일 */
    .stProgress > div > div > div > div { background-color: #1d1d1f !important; }

    /* [매뉴얼 가이드 박스] 흰 배경에 무조건 블랙 글씨 */
    .guide-box {
        background: #ffffff !important;
        border-radius: 40px !important;
        padding: 60px !important;
        margin-top: 80px !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        color: #1d1d1f !important;
    }
    
    .guide-box h2, .guide-box h3, .guide-box h4, .guide-box p, .guide-box li, .guide-box b, .guide-box i {
        color: #1d1d1f !important;
    }

    /* 코드 블록 스타일 */
    .stCodeBlock, div[data-testid="stMarkdownContainer"] pre {
        background-color: #1d1d1f !important;
        color: #f5f5f7 !important;
        border-radius: 20px !important;
        padding: 24px !important;
    }

    [data-baseweb="tab-list"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API 상태 점검 (PDF 268-276 로직)
# ==========================================
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY") and os.getenv("NAVER_AD_CUSTOMER_ID"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD"))

with st.sidebar:
    st.markdown("### **시스템 상태**")
    st.write("네이버 API:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI API:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 이미지 생성 모드", value=False)

# ==========================================
# 5. 로딩바 연동 실시간 스트리밍 엔진 (PDF 295-317 개조)
# ==========================================
def stream_subprocess_with_progress(cmd, env_extra, log_placeholder, progress_bar):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen(
            cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1, env=env
        )
        
        for i, line in enumerate(proc.stdout):
            buffer.append(line.rstrip("\n"))
            log_placeholder.code("\n".join(buffer[-500:]), language="text")
            
            # 실시간 로딩 진행률 (로그 발생 시마다 점진적 상승)
            current_prog = min(0.95, (i + 1) / 80) 
            progress_bar.progress(current_prog)
            
        proc.wait()
        progress_bar.progress(1.0)
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}")
        return -1, []

# ==========================================
# 6. 메인 UI (햅틱 Bento 조종실)
# ==========================================
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.button("📊\n\n키워드 분석", key="card_kw"):
        with st.status("수익성 키워드 분석 중...", expanded=True):
            p_bar = st.progress(0)
            stream_subprocess_with_progress([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty(), p_bar)

with col2:
    if st.button("✍️\n\n포스팅 생성", key="card_post"):
        with st.status("AI 포스팅 생성 및 발행 중...", expanded=True):
            p_bar = st.progress(0)
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
            rc, buf = stream_subprocess_with_progress([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, st.empty(), p_bar)
            if rc == 0:
                edit_line = next((ln for ln in buf if "post.php?post=" in ln), None)
                if edit_line: st.success(f"생성 완료: {edit_line.split()[-1].strip()}")

with col3:
    if st.button("📈\n\n데이터 분석", key="card_view"):
        st.session_state.show_data = True

# 데이터 분석 통계 (PDF 382-400 로직 완벽 복구)
if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("발굴 키워드", f"{len(df)}개")
        c2.metric("최대 검색량", f"{int(df.get('total_volume', [0]).max() if not df.empty else 0):,}")
        c3.metric("평균 검색량", f"{int(df.get('total_volume', [0]).mean() if not df.empty else 0):,}")
        c4.metric("시드 카테고리", df['seed'].nunique() if 'seed' in df.columns else 0)
        st.dataframe(df, use_container_width=True, height=450)

# ==========================================
# 7. 법률 블로그 인수인계 매뉴얼 (최종 통합)
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #1d1d1f; margin-bottom: 50px;'>📑 법률 블로그 운영자 인수인계서 (A to Z)</h2>", unsafe_allow_html=True)

# 텍스트 깨짐 방지 렌더링 함수
def render_manual_step(title, text, img_file=None):
    st.markdown(f"<h3 style='color:#1d1d1f; margin-top:30px;'>{title}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#1d1d1f;'>{text}</p>", unsafe_allow_html=True)
    if img_file and os.path.exists(img_file):
        st.image(img_file, use_container_width=True)

render_manual_step("1. 워드프레스 임시글 확인 및 진입", "포스팅 생성 완료 후, [글] > [모든 글] 메뉴로 접속하여 작성 된 제목을 클릭합니다.", "step1.png")
render_manual_step("2. 과장님 검수 / RankMath SEO 설정 (중요)", "AI 글을 다듬고 스니펫 편집, 포커스 키워드를 설정합니다.")
st.info("프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명을 구글 SEO에 최적화해서 알려줘.'")
render_manual_step("", "", "step2.png")
render_manual_step("3. 공개 일정 예약 및 발행", "매일 오전 9시 예약 발행을 활용하여 블로그 지수를 관리합니다.", "step3.png")

st.markdown("</div>", unsafe_allow_html=True)