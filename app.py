"""
법률 수익화 블로그 자동화 — Streamlit 제어 대시보드
====================================================
keyword_research.py 와 wp_content_generator.py 를 버튼 한 번으로 실행하고,
subprocess stdout을 실시간으로 웹 화면에 스트리밍한다.

실행:
    streamlit run app.py
또는:
    python3 -m streamlit run app.py
"""

import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 깃허브 서버(Streamlit Cloud) 환경일 때 Secrets 금고에서 키를 꺼내옵니다.
    for key, value in st.secrets.items():
        os.environ[key] = str(value)

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

st.set_page_config(
    page_title="법률 블로그 자동화 대시보드",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Apple Pro Studio Ultra-Minimalist CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ===== Global Theme Variables ===== */
    :root {
        --bg-primary: #f5f5f7;
        --bg-secondary: #ffffff;
        --text-primary: #000000;
        --text-secondary: #666666;
        --shadow-soft: 0 8px 24px rgba(0, 0, 0, 0.05);
        --shadow-hover: 0 16px 40px rgba(0, 0, 0, 0.08);
    }

    /* ===== Body & App Container ===== */
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif !important;
        overflow-x: hidden !important;
        letter-spacing: -0.3px !important;
    }

    .stApp {
        background: transparent !important;
    }

    /* ===== Main Content Area ===== */
    [data-testid="stMainBlockContainer"] {
        padding: 80px 100px !important;
        max-width: none !important;
    }

    /* ===== Typography ===== */
    h1, h2, h3, h4, h5, h6 {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.4px !important;
        color: var(--text-primary) !important;
    }

    p, span, div, li {
        font-weight: 400 !important;
        line-height: 1.7 !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.2px !important;
    }

    /* ===== Sidebar ===== */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border-right: 1px solid rgba(0, 0, 0, 0.04) !important;
        padding: 32px 20px !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 12px !important;
    }

    /* ===== Hide Tab Navigation ===== */
    [data-baseweb="tab-list"],
    [data-testid="stSidebarContent"] .stMarkdown h2,
    [data-testid="stSidebarContent"] .stMarkdown h3 {
        display: none !important;
    }

    [data-testid="stSidebarContent"] hr {
        margin: 12px 0 !important;
        border-color: rgba(0, 0, 0, 0.04) !important;
    }

    [data-testid="stSidebarContent"] .stCaption,
    [data-testid="stSidebarContent"] .stCode {
        display: none !important;
    }

    /* ===== Glass Card Container (Studio Style) ===== */
    .studio-card {
        background: #ffffff !important;
        border: 0 !important;
        border-radius: 24px !important;
        padding: 56px 40px !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 32px !important;
        cursor: pointer !important;
        min-height: 320px !important;
        box-shadow: var(--shadow-soft) !important;
        position: relative !important;
    }

    .studio-card:hover {
        box-shadow: var(--shadow-hover) !important;
        transform: translateY(-4px) !important;
    }

    .studio-card-title {
        font-size: 22px !important;
        font-weight: 600 !important;
        letter-spacing: -0.3px !important;
        color: var(--text-primary) !important;
        text-align: center !important;
    }

    /* ===== Button Styling (Silver Gradient Pill) ===== */
    button[kind="primary"] {
        background: linear-gradient(135deg, #e8e8eb 0%, #f5f5f7 100%) !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        border-radius: 50px !important;
        padding: 13px 36px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        letter-spacing: -0.2px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        cursor: pointer !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #e0e0e3 0%, #eeeeef 100%) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        transform: scale(1.04) !important;
    }

    button[kind="primary"]:active {
        transform: scale(0.98) !important;
    }

    button {
        border-radius: 50px !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.2px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* ===== Input Fields ===== */
    input, textarea, [data-baseweb="input"] {
        background-color: #f9f9f9 !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 11px 14px !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
        font-weight: 400 !important;
        letter-spacing: -0.2px !important;
        transition: all 0.2s ease !important;
    }

    input:focus, textarea:focus {
        border-color: rgba(0, 0, 0, 0.15) !important;
        background-color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.03) !important;
        outline: none !important;
    }

    /* ===== Metric Container ===== */
    [data-testid="stMetricContainer"] {
        background: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stMetricContainer"]:hover {
        border-color: rgba(0, 0, 0, 0.12) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06) !important;
    }

    /* ===== Alert Styling ===== */
    [data-testid="stAlert"] {
        background: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        border-radius: 12px !important;
        border-left: 3px solid var(--text-primary) !important;
        padding: 16px 18px !important;
        font-weight: 400 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
    }

    /* ===== Status Container ===== */
    [data-testid="stStatus"] {
        background: #ffffff !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
    }

    /* ===== Code Block ===== */
    pre, code {
        background-color: #f9f9f9 !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        border-radius: 8px !important;
        color: #333333 !important;
        padding: 12px !important;
        font-family: 'Monaco', 'Menlo', monospace !important;
        font-weight: 400 !important;
    }

    /* ===== DataFrame ===== */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03) !important;
    }

    /* ===== Divider ===== */
    hr {
        border-color: rgba(0, 0, 0, 0.04) !important;
        margin: 16px 0 !important;
    }

    /* ===== Checkbox ===== */
    [data-testid="stCheckbox"] label {
        color: var(--text-primary) !important;
        font-weight: 400 !important;
        letter-spacing: -0.2px !important;
    }

    /* ===== Download Button ===== */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #e8e8eb 0%, #f5f5f7 100%) !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        color: var(--text-primary) !important;
        font-weight: 400 !important;
        letter-spacing: -0.2px !important;
    }

    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #e0e0e3 0%, #eeeeef 100%) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06) !important;
    }

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }

    ::-webkit-scrollbar-track {
        background: transparent !important;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.1) !important;
        border-radius: 4px !important;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.15) !important;
    }

    /* ===== Columns Layout ===== */
    [data-testid="stHorizontalBlock"] {
        gap: 24px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API 연결 상태 확인
# ─────────────────────────────────────────────
naver_ok = bool(
    os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY")
    and os.getenv("NAVER_AD_CUSTOMER_ID")
)
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(
    os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD")
)

# ─────────────────────────────────────────────
# Sidebar - 미니멀 상태 표시
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("**연결**")
    col1, col2, col3 = st.columns(3)
    col1.markdown("🟢" if naver_ok else "🔴", unsafe_allow_html=True)
    col2.markdown("🟢" if openai_ok else "🔴", unsafe_allow_html=True)
    col3.markdown("🟢" if wp_ok else "🔴", unsafe_allow_html=True)
    
    st.divider()
    images_enabled = st.checkbox("이미지 생성", value=False)

# ─────────────────────────────────────────────
# subprocess 실시간 스트리밍
# ─────────────────────────────────────────────
def stream_subprocess(cmd: list, env_extra: dict, log_placeholder, max_lines: int = 1000):
    """subprocess를 띄우고 stdout 라인을 Streamlit placeholder에 실시간 출력."""
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
    buffer: list[str] = []
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}")
        return -1, []

    assert proc.stdout is not None
    for line in proc.stdout:
        buffer.append(line.rstrip("\n"))
        log_placeholder.code("\n".join(buffer[-max_lines:]), language="text")
    proc.wait()
    return proc.returncode, buffer


# ─────────────────────────────────────────────
# 메인 UI - Studio 컨트롤 패널
# ─────────────────────────────────────────────

# 상단 3개 카드 레이아웃
col1, col2, col3 = st.columns(3, gap="large")

# ========== Card 1: 키워드 분석 ==========
with col1:
    st.markdown("""
    <div class="studio-card">
        <div class="studio-card-title">키워드 분석</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not naver_ok:
        st.error("API 연결 필요")
    else:
        if st.button("실행", key="btn_kw", use_container_width=True, type="primary"):
            with st.status("진행 중...", expanded=True) as status:
                log_box = st.empty()
                rc, _buf = stream_subprocess(
                    [sys.executable, "-u", KEYWORD_SCRIPT],
                    env_extra={},
                    log_placeholder=log_box,
                )
                if rc == 0:
                    status.update(label="완료", state="complete")
                    st.toast("keywords.csv 갱신됨")
                else:
                    status.update(label=f"오류 {rc}", state="error")

# ========== Card 2: 포스팅 생성 ==========
with col2:
    st.markdown("""
    <div class="studio-card">
        <div class="studio-card-title">포스팅 생성</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not wp_ok:
        st.error("API 연결 필요")
    elif not os.path.exists(CSV_PATH):
        st.warning("키워드 분석 필요")
    else:
        if st.button("실행", key="btn_post", use_container_width=True, type="primary"):
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
            with st.status("진행 중...", expanded=True) as status:
                log_box = st.empty()
                rc, buf = stream_subprocess(
                    [sys.executable, "-u", PUBLISH_SCRIPT],
                    env_extra=env_extra,
                    log_placeholder=log_box,
                )
                if rc == 0:
                    status.update(label="완료", state="complete")
                    edit_line = next(
                        (ln for ln in buf if "post.php?post=" in ln), None
                    )
                    if edit_line:
                        url = edit_line.split()[-1].strip()
                        st.success(f"✓ {url}")
                else:
                    status.update(label=f"오류 {rc}", state="error")

# ========== Card 3: 데이터 보기 ==========
with col3:
    st.markdown("""
    <div class="studio-card">
        <div class="studio-card-title">데이터 보기</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("실행", key="btn_view", use_container_width=True, type="primary"):
        st.session_state.show_data = True

# ========== Data View Section ==========
if st.session_state.get("show_data", False):
    st.divider()
    st.markdown("#### CSV 데이터")
    
    if not os.path.exists(CSV_PATH):
        st.info("아직 keywords.csv 가 없습니다.")
    else:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("키워드 수", len(df))
        c2.metric("최대 월검색", f"{int(df['total_volume'].max()):,}")
        c3.metric("평균 월검색", f"{int(df['total_volume'].mean()):,}")
        c4.metric("시드 종류", df['seed'].nunique() if 'seed' in df.columns else 0)

        st.dataframe(df, use_container_width=True, height=520)

        st.download_button(
            "다운로드",
            data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name="keywords.csv",
            mime="text/csv",
            use_container_width=True,
        )
