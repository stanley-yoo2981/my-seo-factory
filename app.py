import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [17-23] 프로젝트 경로 및 API 강제 연결 (PDF 원본 로직 100% 복구)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env") # [cite: 17-18]

if os.path.exists(env_path):
    load_dotenv(env_path) # [cite: 19-20]
else:
    # 깃허브 서버(Streamlit Cloud) 환경일 때 Secrets 금고에서 키를 강제 주입 [cite: 21-23]
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# [24-25] 주요 파일 경로 정의 [cite: 24-25]
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# [26-31] 페이지 설정 (파비콘: ⚖️ 저울) [cite: 26-31]
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [32-264] Apple Pro Studio Ultra-Premium CSS (PDF 원본의 모든 스타일 로직 복원 및 고도화)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* [줌-인 등장 애니메이션] 배열이 촥~ 맞아 들어가는 느낌 */
    @keyframes studioReveal {
        0% { transform: scale(0.97); opacity: 0; filter: blur(15px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    /* ===== Global Theme Variables ===== */
    :root {
        --bg-apple: #F5F5F7;
        --bg-secondary: #ffffff;
        --text-primary: #1d1d1f;
        --text-secondary: #86868b;
        --apple-blue: #0071E3;
        --titanium-black: #1D1D1F;
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
        animation: studioReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    } [cite: 56-58]

    /* ===== Glass Card Container (Bento Box) ===== */
    .studio-card {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 35px !important;
        padding: 50px 40px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: var(--shadow-soft) !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 350px !important;
    } [cite: 96-111]

    .studio-card:hover {
        background: rgba(255, 255, 255, 0.65) !important;
        box-shadow: var(--shadow-hover) !important;
        transform: translateY(-8px) scale(1.02) !important;
    } [cite: 112-115]

    .studio-card-title {
        font-size: 24px !important;
        font-weight: 600 !important;
        color: var(--titanium-black) !important;
        margin-bottom: 12px !important;
    } [cite: 116-122]

    /* ===== Titanium Black Button ===== */
    button[kind="primary"] {
        background: var(--titanium-black) !important;
        color: white !important;
        border-radius: 999px !important; /* Pill shape */
        padding: 14px 45px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        border: none !important;
    } [cite: 124-136]

    button[kind="primary"]:hover {
        background: #3c3c3e !important;
        transform: scale(1.04) !important;
    } [cite: 137-144]

    /* ===== 운영 매뉴얼 가이드 박스 ===== */
    .guide-box {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 30px !important;
        padding: 50px !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        margin-top: 60px !important;
        color: #1d1d1f !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03) !important;
    }

    .capture-spot {
        background: #f0f0f2;
        border: 2px dashed #d2d2d7;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        color: #86868b;
        margin: 20px 0;
        font-size: 14px;
    }

    /* ===== Logs & Metrics ===== */
    [data-testid="stMetricContainer"] {
        background: #ffffff !important;
        border-radius: 20px !important;
        padding: 24px !important;
        box-shadow: var(--shadow-soft) !important;
    } [cite: 173-180]

    pre, code {
        background-color: #1d1d1f !important;
        color: #f5f5f7 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        font-family: 'SF Mono', 'Monaco', monospace !important;
    } [cite: 203-211]

    [data-baseweb="tab-list"] { display: none !important; } [cite: 81-86]
</style>
""", unsafe_allow_html=True) [cite: 263-264]

# [265-276] API 연결 상태 확인 로직 (한글화) [cite: 268-276]
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY") and os.getenv("NAVER_AD_CUSTOMER_ID")) [cite: 268-272]
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD")) [cite: 274-276]

# [277-292] 사이드바 - 시스템 상태 [cite: 280-292]
with st.sidebar:
    st.markdown("### **시스템 상태**")
    st.write("네이버 API:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI API:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 이미지 생성 모드", value=False)

# [293-317] subprocess 실시간 스트리밍 엔진 (원본 로직 100% 복원) 
def stream_subprocess(cmd: list, env_extra: dict, log_placeholder, max_lines=1000):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
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
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}")
        return -1, []

# [318-380] 메인 UI
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

# ========== 카드 1: 키워드 분석 [cite: 322-343] ==========
with col1:
    st.markdown('<div class="studio-card"><div class="studio-card-title">키워드 분석</div><p style="color: #86868b; text-align: center;">네이버 검색 데이터를 기반으로<br>수익성 높은 키워드를 발굴합니다</p></div>', unsafe_allow_html=True)
    if not naver_ok:
        st.error("API 연결 필요")
    else:
        if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True): [cite: 331-332]
            with st.status("분석 중...", expanded=True) as status:
                log_box = st.empty()
                rc, _ = stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box) [cite: 334-338]
                if rc == 0:
                    status.update(label="분석 완료", state="complete")
                    st.toast("데이터 갱신 완료")
                else:
                    status.update(label=f"오류 발생 ({rc})", state="error")

# ========== 카드 2: 포스팅 생성 [cite: 344-372] ==========
with col2:
    st.markdown('<div class="studio-card"><div class="studio-card-title">포스팅 생성</div><p style="color: #86868b; text-align: center;">AI가 독창적인 법률 본문을 작성하고<br>워드프레스에 임시글로 발행합니다</p></div>', unsafe_allow_html=True)
    if not wp_ok:
        st.error("API 연결 필요")
    elif not os.path.exists(CSV_PATH):
        st.warning("분석 데이터가 필요합니다")
    else:
        if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True):
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
            with st.status("발행 프로세스 가동 중...", expanded=True) as status:
                log_box = st.empty()
                rc, buf = stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box) [cite: 358-362]
                if rc == 0:
                    status.update(label="발행 성공", state="complete")
                    edit_line = next((ln for ln in buf if "post.php?post=" in ln), None) [cite: 365-367]
                    if edit_line:
                        url = edit_line.split()[-1].strip()
                        st.success(f"임시글 생성 완료: {url}")
                else:
                    status.update(label=f"오류 발생 ({rc})", state="error")

# ========== 카드 3: 데이터 분석 [cite: 373-380] ==========
with col3:
    st.markdown('<div class="studio-card"><div class="studio-card-title">데이터 분석</div><p style="color: #86868b; text-align: center;">발굴된 키워드 통계를 분석하고<br>공장 가동 현황을 확인합니다</p></div>', unsafe_allow_html=True)
    if st.button("데이터 보기", key="btn_view", type="primary", use_container_width=True):
        st.session_state.show_data = True

# [381-400] 데이터 뷰 섹션 [cite: 382-400]
if st.session_state.get("show_data", False):
    st.divider()
    if not os.path.exists(CSV_PATH):
        st.info("데이터가 아직 없습니다.")
    else:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("발굴 키워드", f"{len(df)}개")
        c2.metric("최대 검색량", f"{int(df['total_volume'].max()):,}")
        c3.metric("평균 검색량", f"{int(df['total_volume'].mean()):,}")
        c4.metric("시드 카테고리", df['seed'].nunique() if 'seed' in df.columns else 0)
        st.dataframe(df, use_container_width=True, height=450)
        st.download_button("데이터 추출 (CSV)", data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"), file_name="law_seo_data.csv", use_container_width=True)

# ========== [A to Z 운영자 인수인계 매뉴얼] ==========
st.markdown("""
<div class='guide-box'>
    <h2 style='text-align: center; margin-bottom: 50px;'>📑 법률 블로그 운영자 인수인계서 (A to Z)</h2>
    
    <h3>Step 1. 워드프레스 임시글 확인 및 진입</h3>
    <p>포스팅 생성 완료 후, 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속합니다.</p>
    <div class='capture-spot'>[📸 캡처 지점: 글 목록 화면 - '— 임시글' 표시가 된 제목 확인]</div>
    <ul>
        <li>목록에서 <b>'— 임시글'</b> 표시가 붙은 제목을 클릭하여 편집 화면으로 이동합니다.</li>
    </ul>

    <h3 style='margin-top: 40px;'>Step 2. 인간 검수 (가장 중요한 품질 관리)</h3>
    <p>AI가 작성한 글을 사람이 최종적으로 다듬는 단계입니다. 노출 경쟁력을 결정합니다.</p>
    <div class='capture-spot'>[📸 캡처 지점: 워드프레스 글 편집기 전체 화면]</div>
    <ul>
        <li><b>제목:</b> 키워드(예: 음주운전벌금)가 자연스럽게 포함되었는지 확인합니다.</li>
        <li><b>가독성:</b> 문단 사이를 띄워주고, 중요한 포인트는 <b>굵게(Bold)</b> 처리합니다.</li>
    </ul>

    <h3 style='margin-top: 40px;'>Step 3. 설정 및 최종 발행</h3>
    <p>우측 사이드바 메뉴에서 카테고리와 태그를 설정합니다.</p>
    <div class='capture-spot'>[📸 캡처 지점: 우측 설정바 - 카테고리 및 태그 선택 영역]</div>
    <ul>
        <li><b>카테고리:</b> 해당 법률 주제에 맞는 카테고리를 정확히 체크합니다.</li>
        <li><b>태그:</b> 관련 핵심 키워드 3~5개를 입력합니다.</li>
    </ul>

    <h3 style='margin-top: 40px;'>Step 4. 즉시 발행 및 예약 발행</h3>
    <p>공개 시점을 결정하는 마지막 단계입니다.</p>
    <div class='capture-spot'>[📸 캡처 지점: 우측 상단 - 공개 상태 및 발행/예약 버튼]</div>
    <ul>
        <li><b>즉시 발행:</b> 바로 공개하려면 상단의 파란색 <b>[발행]</b> 버튼을 누릅니다.</li>
        <li><b>예약 발행:</b> [공개] 항목 옆의 '즉시' 버튼을 눌러 달력에서 <b>날짜와 시간</b>을 선택한 후 [예약] 버튼을 누릅니다.</li>
    </ul>
    
    <div style='background: #fdf6e3; padding: 25px; border-radius: 20px; margin-top: 40px; border: 1px solid #faebcc;'>
        <b>💡 팁:</b> 네이버 검색 노출을 위해 발행 후 URL을 <b>'네이버 서치어드바이저'</b>에 제출하는 것을 잊지 마세요.
    </div>
</div>
""", unsafe_allow_html=True)