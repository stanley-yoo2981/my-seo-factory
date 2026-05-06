import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [17-23] 프로젝트 경로 설정 및 API 강제 연결 로직 (PDF 17-23라인 완벽 복구)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env") # [cite: 17, 18]

if os.path.exists(env_path):
    load_dotenv(env_path) # [cite: 19, 20]
else:
    # 깃허브 서버(Streamlit Cloud) 환경일 때 Secrets 금고에서 키를 꺼내 시스템 환경 변수로 강제 주입
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value) # [cite: 21, 22, 23]
    except:
        pass

# [24-25] 파일 경로 정의 [cite: 24, 25]
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# [26-31] 페이지 설정 [cite: 26-31]
st.set_page_config(
    page_title="법률 블로그 자동화 대시보드",
    page_icon="🍏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [32-264] Apple Pro Studio Ultra-Minimalist CSS (PDF 37-263라인의 방대한 스타일 로직 복구)
st.markdown("""
<style>
    /* ===== Global Theme Variables ===== */
    :root {
        --bg-primary: #f5f5f7;
        --bg-secondary: #ffffff;
        --text-primary: #1d1d1f;
        --text-secondary: #86868b;
        --shadow-soft: 0 8px 30px rgba(0, 0, 0, 0.04);
        --shadow-hover: 0 20px 40px rgba(0, 0, 0, 0.08);
    } [cite: 37-44]

    /* ===== Body & App Container ===== */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
        letter-spacing: -0.022em !important;
    } [cite: 46-52]

    [data-testid="stMainBlockContainer"] {
        padding: 80px 100px !important;
        max-width: none !important;
    } [cite: 56-58]

    /* ===== Typography ===== */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600 !important;
        letter-spacing: -0.025em !important;
        color: var(--text-primary) !important;
    } [cite: 60-66]

    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
    } [cite: 74-77]

    /* Hide Navigation [cite: 81-86] */
    [data-baseweb="tab-list"] { display: none !important; }

    /* ===== Studio Card Container (Bento Style) ===== */
    .studio-card {
        background: #ffffff !important;
        border-radius: 28px !important;
        padding: 60px 40px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 340px !important;
        box-shadow: var(--shadow-soft) !important;
        border: 1px solid rgba(0, 0, 0, 0.02) !important;
    } [cite: 96-111]

    .studio-card:hover {
        box-shadow: var(--shadow-hover) !important;
        transform: translateY(-5px) !important;
    } [cite: 112-115]

    .studio-card-title {
        font-size: 24px !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: var(--text-primary) !important;
        margin-bottom: 12px !important;
    } [cite: 116-122]

    /* ===== Button Styling (Apple Blue Pill) ===== */
    button[kind="primary"] {
        background: #0071E3 !important;
        color: white !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 14px 40px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    } [cite: 124-136]

    button[kind="primary"]:hover {
        background: #0077ED !important;
        transform: scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(0, 113, 227, 0.3) !important;
    } [cite: 137-141]

    /* ===== Metric Container ===== */
    [data-testid="stMetricContainer"] {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: var(--shadow-soft) !important;
        border: 1px solid rgba(0, 0, 0, 0.02) !important;
    } [cite: 173-179]

    /* ===== Studio Logs (Dark Mode) ===== */
    pre, code {
        background-color: #1d1d1f !important;
        color: #f5f5f7 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        font-family: 'SF Mono', 'Monaco', monospace !important;
        font-size: 13px !important;
    } [cite: 203-211]
</style>
""", unsafe_allow_html=True) [cite: 263-264]

# [265-276] API 연결 상태 확인 로직 (PDF 원본 복구)
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY") and os.getenv("NAVER_AD_CUSTOMER_ID")) [cite: 268-272]
openai_ok = bool(os.getenv("OPENAI_API_KEY")) [cite: 273]
wp_ok = bool(os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD")) [cite: 274-276]

# [277-292] Sidebar - 미니멀 상태 표시 [cite: 280-292]
with st.sidebar:
    st.markdown("### **System Status**")
    st.write("Naver API:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI API:", "🟢" if openai_ok else "🔴")
    st.write("WordPress API:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("이미지 생성 모드", value=False) [cite: 292]

# [293-317] subprocess 실시간 스트리밍 엔진 (사장님의 핵심 로직 복구) [cite: 295-317]
def stream_subprocess(cmd: list, env_extra: dict, log_placeholder, max_lines=1000):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"} [cite: 297]
    buffer = []
    try:
        proc = subprocess.Popen(
            cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1, env=env
        ) [cite: 300-307]
        assert proc.stdout is not None
        for line in proc.stdout:
            buffer.append(line.rstrip("\n"))
            log_placeholder.code("\n".join(buffer[-max_lines:]), language="text") [cite: 313-315]
        proc.wait()
        return proc.returncode, buffer [cite: 316-317]
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}")
        return -1, [] [cite: 308-310]

# [318-380] 메인 UI - Studio 컨트롤 패널
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 48px; font-weight: 600; margin-bottom: 50px;'>SEO Factory Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large") [cite: 321]

# ========== Card 1: 키워드 분석 [cite: 322-343] ==========
with col1:
    st.markdown('<div class="studio-card"><div class="studio-card-title">키워드 분석</div><p style="color: #86868b;">Naver AD API 연동 발굴</p></div>', unsafe_allow_html=True)
    if not naver_ok:
        st.error("API 연결 필요") [cite: 328-329]
    else:
        if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True): [cite: 331-332]
            with st.status("진행 중...", expanded=True) as status:
                log_box = st.empty()
                rc, _ = stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box) [cite: 334-338]
                if rc == 0:
                    status.update(label="분석 완료", state="complete") [cite: 340]
                    st.toast("keywords.csv 데이터 갱신") [cite: 341]
                else:
                    status.update(label=f"오류 발생 (Code: {rc})", state="error") [cite: 343]

# ========== Card 2: 포스팅 생성 [cite: 344-372] ==========
with col2:
    st.markdown('<div class="studio-card"><div class="studio-card-title">포스팅 생성</div><p style="color: #86868b;">AI 본문 작성 및 발행</p></div>', unsafe_allow_html=True)
    if not wp_ok:
        st.error("API 연결 필요") [cite: 350-351]
    elif not os.path.exists(CSV_PATH):
        st.warning("분석 데이터가 없습니다") [cite: 352]
    else:
        if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True):
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"} [cite: 356]
            with st.status("발행 중...", expanded=True) as status:
                log_box = st.empty()
                rc, buf = stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box) [cite: 358-362]
                if rc == 0:
                    status.update(label="발행 완료", state="complete") [cite: 364]
                    # URL 추출 로직 [cite: 365-371]
                    edit_line = next((ln for ln in buf if "post.php?post=" in ln), None)
                    if edit_line:
                        url = edit_line.split()[-1].strip()
                        st.success(f"글 주소: {url}")
                else:
                    status.update(label=f"오류 {rc}", state="error") [cite: 372]

# ========== Card 3: 데이터 보기 [cite: 373-380] ==========
with col3:
    st.markdown('<div class="studio-card"><div class="studio-card-title">데이터 보기</div><p style="color: #86868b;">분석 결과 데이터베이스</p></div>', unsafe_allow_html=True)
    if st.button("파일 열기", key="btn_view", type="primary", use_container_width=True): [cite: 379]
        st.session_state.show_data = True [cite: 380]

# [381-400] 데이터 뷰 섹션 (상세 수치 분석 로직 복구) [cite: 382-400]
if st.session_state.get("show_data", False):
    st.divider() [cite: 383]
    if not os.path.exists(CSV_PATH):
        st.info("아직 분석된 데이터 파일이 없습니다.") [cite: 386]
    else:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig") [cite: 388]
        c1, c2, c3, c4 = st.columns(4) [cite: 389]
        c1.metric("발굴 키워드", f"{len(df)}개") [cite: 390]
        c2.metric("최대 검색량", f"{int(df['total_volume'].max()):,}") [cite: 391]
        c3.metric("평균 검색량", f"{int(df['total_volume'].mean()):,}") [cite: 392]
        c4.metric("시드 카테고리", df['seed'].nunique() if 'seed' in df.columns else "N/A") [cite: 393]
        st.dataframe(df, use_container_width=True, height=520) [cite: 394]
        st.download_button(
            "데이터 다운로드 (CSV)", 
            data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"), 
            file_name="seo_results.csv", mime="text/csv", use_container_width=True
        ) [cite: 395-400]