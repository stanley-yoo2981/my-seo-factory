import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [17-23] 프로젝트 경로 및 API 강제 연결 (PDF 원본 로직 100% 복구)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env") # [cite: 18]

if os.path.exists(env_path):
    load_dotenv(env_path) # [cite: 19-20]
else:
    # 깃허브 서버 환경일 때 Secrets 금고에서 키를 꺼내 시스템 환경 변수로 강제 주입 [cite: 22-23]
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value) # [cite: 23]
    except:
        pass

# [24-25] 주요 파일 경로 정의 [cite: 24-25]
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv") # [cite: 24]
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py") # [cite: 25]
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py") # [cite: 25]

# [26-31] 페이지 설정 (파비콘을 법률/수익 결에 맞는 저울로 교체)
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", # 🍏에서 ⚖️(저울) 또는 📊(그래프)로 변경 가능합니다 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# [32-264] Apple Pro Studio Ultra-Premium CSS (애니메이션 & 질감 고도화)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* [줌-인 등장 애니메이션] 배열이 촥~ 맞아 들어가는 느낌 */
    @keyframes studioReveal {
        0% { transform: scale(0.96); opacity: 0; filter: blur(15px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    :root {
        --bg-apple: #F5F5F7;
        --glass-white: rgba(255, 255, 255, 0.45);
        --glass-border: rgba(255, 255, 255, 0.8);
        --titanium-black: #1D1D1F;
        --text-sub: #86868B;
    } [cite: 37-44]

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-apple) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
    } [cite: 46-50]

    /* 메인 컨테이너 애니메이션 적용 */
    [data-testid="stMainBlockContainer"] {
        padding: 80px 100px !important;
        animation: studioReveal 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    } [cite: 56]

    /* [하이엔드 유리 카드] 질감 극대화 */
    .studio-card {
        background: var(--glass-white) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 35px !important;
        padding: 60px 40px !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 380px !important;
    } [cite: 96-111]

    .studio-card:hover {
        background: rgba(255, 255, 255, 0.65) !important;
        box-shadow: 0 40px 80px rgba(0, 0, 0, 0.12) !important;
        transform: translateY(-10px) scale(1.03) !important;
    } [cite: 112-115]

    .studio-card-title {
        font-size: 26px !important;
        font-weight: 600 !important;
        color: var(--titanium-black) !important;
        margin-bottom: 12px !important;
        letter-spacing: -0.5px !important;
    } [cite: 116-122]

    /* [티타늄 블랙 버튼] 파란색 제거, 누르고 싶게 만드는 고급스러운 사틴 블랙 */
    button[kind="primary"] {
        background: var(--titanium-black) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 999px !important; /* Pill shape */
        padding: 16px 45px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    } [cite: 124-136]

    button[kind="primary"]:hover {
        background: #3c3c3e !important; /* 미세하게 밝아지는 티타늄 텍스처 */
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
        transform: scale(1.05) !important;
    } [cite: 137-141]

    /* 사이드바 시인성 (한글화 반영) */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(25px) !important;
    } [cite: 74-77]
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
        color: #1d1d1f !important;
        font-weight: 500 !important;
    }

    /* 로그 박스: Studio Dark [cite: 203-211] */
    pre, code {
        background-color: #1d1d1f !important;
        color: #f5f5f7 !important;
        border-radius: 20px !important;
        padding: 24px !important;
        font-family: 'SF Mono', 'Monaco', monospace !important;
    }
</style>
""", unsafe_allow_html=True) [cite: 263-264]

# [265-276] API 연결 상태 확인 로직 (한글화 반영) [cite: 268-276]
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY") and os.getenv("NAVER_AD_CUSTOMER_ID")) # [cite: 268-272]
openai_ok = bool(os.getenv("OPENAI_API_KEY")) # [cite: 273]
wp_ok = bool(os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD")) # [cite: 274-276]

# [277-292] 사이드바 - 시스템 상태 (한글화) [cite: 280-292]
with st.sidebar:
    st.markdown("### **시스템 상태**")
    st.write("네이버 API:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI API:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 이미지 생성 모드", value=False) # [cite: 292]

# [293-317] subprocess 실시간 스트리밍 엔진 (원본 로직 100% 복구) 
def stream_subprocess(cmd: list, env_extra: dict, log_placeholder, max_lines=1000):
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"} # [cite: 297]
    buffer = [] # [cite: 298]
    try:
        proc = subprocess.Popen(
            cmd, cwd=PROJECT_DIR, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, bufsize=1, env=env
        ) # [cite: 300-307]
        assert proc.stdout is not None # [cite: 312]
        for line in proc.stdout:
            buffer.append(line.rstrip("\n")) # [cite: 314]
            log_placeholder.code("\n".join(buffer[-max_lines:]), language="text") # [cite: 315]
        proc.wait() # [cite: 316]
        return proc.returncode, buffer # [cite: 317]
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}") # [cite: 309]
        return -1, [] # [cite: 310]

# [318-380] 메인 UI - 한글화 및 디자인 적용
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large") # [cite: 321]

# ========== 카드 1: 키워드 분석 [cite: 322-343] ==========
with col1:
    st.markdown('<div class="studio-card"><div class="studio-card-title">키워드 분석</div><p style="color: #86868b; text-align: center;">네이버 실시간 데이터를<br>정밀하게 발굴합니다</p></div>', unsafe_allow_html=True)
    if not naver_ok:
        st.error("API 연결이 필요합니다") # [cite: 329]
    else:
        if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True): # [cite: 331-332]
            with st.status("키워드 발굴 중...", expanded=True) as status: # [cite: 333]
                log_box = st.empty()
                rc, _ = stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box) # [cite: 334-338]
                if rc == 0:
                    status.update(label="분석 완료", state="complete") # [cite: 340]
                    st.toast("데이터 갱신 완료") # [cite: 341]
                else:
                    status.update(label=f"오류 발생 ({rc})", state="error") # [cite: 343]

# ========== 카드 2: 포스팅 생성 [cite: 344-372] ==========
with col2:
    st.markdown('<div class="studio-card"><div class="studio-card-title">포스팅 생성</div><p style="color: #86868b; text-align: center;">AI가 독창적인 법률 본문을<br>작성하고 자동 발행합니다</p></div>', unsafe_allow_html=True)
    if not wp_ok:
        st.error("API 연결이 필요합니다") # [cite: 351]
    elif not os.path.exists(CSV_PATH):
        st.warning("분석 데이터가 필요합니다") # [cite: 352]
    else:
        if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True): # [cite: 354]
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"} # [cite: 356]
            with st.status("콘텐츠 발행 중...", expanded=True) as status: # [cite: 357]
                log_box = st.empty()
                rc, buf = stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box) # [cite: 358-362]
                if rc == 0:
                    status.update(label="발행 성공", state="complete") # [cite: 364]
                    edit_line = next((ln for ln in buf if "post.php?post=" in ln), None) # [cite: 365-367]
                    if edit_line:
                        url = edit_line.split()[-1].strip() # [cite: 370]
                        st.success(f"발행 완료: {url}") # [cite: 371]
                else:
                    status.update(label=f"오류 발생 ({rc})", state="error") # [cite: 372]

# ========== 카드 3: 데이터 인사이트 [cite: 373-380] ==========
with col3:
    st.markdown('<div class="studio-card"><div class="studio-card-title">인사이트</div><p style="color: #86868b; text-align: center;">수집된 키워드와<br>포스팅 통계를 분석합니다</p></div>', unsafe_allow_html=True)
    if st.button("데이터 보기", key="btn_view", type="primary", use_container_width=True): # [cite: 379]
        st.session_state.show_data = True # [cite: 380]

# [381-400] 데이터 뷰 섹션 [cite: 382-400]
if st.session_state.get("show_data", False):
    st.divider() # [cite: 383]
    st.markdown("#### **수집된 키워드 데이터베이스**") # [cite: 384]
    if not os.path.exists(CSV_PATH):
        st.info("아직 분석된 데이터 파일이 없습니다.") # [cite: 386]
    else:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig") # [cite: 388]
        c1, c2, c3, c4 = st.columns(4) # [cite: 389]
        c1.metric("발굴 키워드", f"{len(df)}개") # [cite: 390]
        c2.metric("최대 검색량", f"{int(df['total_volume'].max()):,}") # [cite: 391]
        c3.metric("평균 검색량", f"{int(df['total_volume'].mean()):,}") # [cite: 392]
        c4.metric("카테고리 수", df['seed'].nunique() if 'seed' in df.columns else 0) # [cite: 393]
        st.dataframe(df, use_container_width=True, height=550) # [cite: 394]
        st.download_button(
            "엑셀로 추출하기 (CSV)", 
            data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"), 
            file_name="law_seo_data.csv", mime="text/csv", use_container_width=True
        ) # [cite: 395-400]