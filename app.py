import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 1. 시스템 핵심 로직 (PDF 17-25라인 완벽 복구)
# ==========================================
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 스트림릿 클라우드 Secrets 대응
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# ==========================================
# 2. 프리미엄 페이지 설정
# ==========================================
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 3. Apple Haptic Studio CSS (디자인 총집계)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* 등장 애니메이션 */
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

    /* [사이드바] 무조건 화이트 글씨 */
    [data-testid="stSidebar"] {
        background-color: #262730 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* [Bento Card -> 버튼 통합] 햅틱 피드백 */
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
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
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

    /* [매뉴얼 가이드 박스] 무조건 블랙 글씨 */
    .guide-box {
        background: #ffffff !important;
        border-radius: 40px !important;
        padding: 60px !important;
        margin-top: 80px !important;
        color: #1d1d1f !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    
    .guide-box h2, .guide-box h3, .guide-box h4, .guide-box p, .guide-box li, .guide-box b, .guide-box i {
        color: #1d1d1f !important;
    }

    pre, code {
        background-color: #1d1d1f !important;
        color: #f5f5f7 !important;
        border-radius: 20px !important;
    }

    [data-baseweb="tab-list"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. API 상태 체크 로직 (PDF 268-276라인)
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
# 5. 스트리밍 엔진 (PDF 295-317라인)
# ==========================================
def stream_subprocess(cmd, env_extra, log_placeholder, max_lines=1000):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen(
            cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1, env=env
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            buffer.append(line.rstrip("\n"))
            log_placeholder.code("\n".join(buffer[-max_lines:]), language="text")
        proc.wait()
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}")
        return -1, []

# ==========================================
# 6. 메인 조종실 UI
# ==========================================
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.button("📊\n\n키워드 분석", key="card_kw"):
        with st.status("분석 중...", expanded=True) as status:
            log_box = st.empty()
            rc, _ = stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box)
            if rc == 0: status.update(label="분석 완료", state="complete")

with col2:
    if st.button("✍️\n\n포스팅 생성", key="card_post"):
        env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
        with st.status("생성 중...", expanded=True) as status:
            log_box = st.empty()
            rc, buf = stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box)
            if rc == 0:
                status.update(label="발행 성공", state="complete")
                edit_line = next((ln for ln in buf if "post.php?post=" in ln), None)
                if edit_line: st.success(f"생성 완료: {edit_line.split()[-1].strip()}")

with col3:
    if st.button("📈\n\n데이터 분석", key="card_view"):
        st.session_state.show_data = True

# 데이터 분석 섹션 (PDF 382-400라인)
if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("발굴 키워드", f"{len(df)}개")
        c2.metric("최대 검색량", f"{int(df.get('total_volume', [0])[0] if not df.empty else 0):,}")
        c3.metric("평균 검색량", f"{int(df.get('total_volume', [0]).mean() if not df.empty else 0):,}")
        c4.metric("시드 카테고리", df['seed'].nunique() if 'seed' in df.columns else 0)
        st.dataframe(df, use_container_width=True, height=450)

# ==========================================
# 7. 인수인계 매뉴얼 (완벽 시인성 버전)
# ==========================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 50px;'>📑 법률 블로그 운영자 인수인계서 (A to Z)</h2>", unsafe_allow_html=True)

# 1단계
st.markdown("<h3 style='margin-top: 30px;'>1. 워드프레스 임시글 확인 및 진입</h3>", unsafe_allow_html=True)
st.markdown("<p>포스팅 생성 완료 후, 워드프레스 관리자 페이지의 [글] > [모든 글] 메뉴로 접속합니다. 목록에서 작성 된 제목을 클릭하여 편집 화면으로 들어갑니다.</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

# 2단계
st.markdown("<h3 style='margin-top: 40px;'>2. 과장님 검수 / RankMath SEO 설정 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 이상한 부분이 없는지 체크하는 단계입니다.</p>", unsafe_allow_html=True)

st.markdown("<p><b>1) 스니펫 편집:</b> 제미나이에 본문을 복사한 뒤 제목, 퍼머링크, 설명을 최적화하세요.</p>", unsafe_allow_html=True)
st.info("프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.'")
if os.path.exists("step2.png"): st.image("step2.png")
if os.path.exists("step2-1.png"): st.image("step2-1.png")

st.markdown("<p><b>2) 포커스 키워드:</b> 제목 맨 첫 번째 키워드를 삽입하고 점수가 80점 이상 되도록 보완합니다.</p>", unsafe_allow_html=True)
if os.path.exists("step2-2.png"): st.image("step2-2.png")
if os.path.exists("step2-3.png"): st.image("step2-3.png")
if os.path.exists("step2-4.png"): st.image("step2-4.png")

# 3단계
st.markdown("<h3 style='margin-top: 40px;'>3. 공개 일정 예약</h3>", unsafe_allow_html=True)
st.markdown("<p>하루 10개는 즉시 업로드, 나머지 10개는 매일 오전 9시 발행되도록 예약을 걸어둡니다.</p>", unsafe_allow_html=True)
if os.path.exists("step3.png"): st.image("step3.png")
if os.path.exists("step3-1.png"): st.image("step3-1.png")
if os.path.exists("step3-2.png"): st.image("step3-2.png")
if os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)