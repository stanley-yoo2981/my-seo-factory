import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 1. 프로젝트 경로 및 API 연결 (PDF 원본 로직 100% 복원)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # 깃허브 서버(Streamlit Cloud) 환경일 때 Secrets 금고에서 키를 강제로 주입
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# 주요 파일 경로 정의
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (파비콘: ⚖️ 저울)
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Apple Haptic Studio CSS (비주얼 미니멀리즘 및 햅틱 효과 완결판)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* 줌-인 등장 애니메이션 */
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
    [data-testid="stSidebar"] {
        background-color: #262730 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* [Bento Card -> 버튼으로 개조] */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 35px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05) !important;
        height: 380px !important;
        width: 100% !important;
        transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 40px !important;
        color: var(--titanium-black) !important;
        font-size: 24px !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
        margin-top: 0px !important;
    }

    /* [마우스 오버: 떠오르는 느낌] */
    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.65) !important;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-10px) !important;
        border-color: rgba(255, 255, 255, 1) !important;
        color: var(--titanium-black) !important;
    }

    /* [클릭: 햅틱 압축 느낌] */
    div.stButton > button:active {
        transform: scale(0.94) translateY(-5px) !important;
        transition: all 0.1s ease !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05) !important;
    }

    /* 하단 매뉴얼 가이드 박스: 무조건 블랙 글씨 */
    .guide-box {
        background: #ffffff !important;
        border-radius: 40px !important;
        padding: 60px !important;
        margin-top: 80px !important;
        color: #1d1d1f !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
    }
    .guide-box h2, .guide-box h3, .guide-box h4, .guide-box p, .guide-box li, .guide-box b {
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

# API 연결 상태 확인 (원본 로직)
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

# subprocess 실시간 스트리밍 엔진 (원본 로직 보존)
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

# 6. 메인 UI 조종실 (햅틱 Bento 카드 에디션)
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

# --- 카드 1: 키워드 분석 ---
with col1:
    if st.button("📊\n\n키워드 분석", key="card_kw"):
        with st.status("분석 중...", expanded=True) as status:
            log_box = st.empty()
            rc, _ = stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box)
            if rc == 0: status.update(label="분석 완료", state="complete")

# --- 카드 2: 포스팅 생성 ---
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

# --- 카드 3: 데이터 분석 ---
with col3:
    if st.button("📈\n\n데이터 분석", key="card_view"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("발굴 키워드", f"{len(df)}개")
        c2.metric("최대 검색량", f"{int(df['total_volume'].max()):,}")
        c3.metric("평균 검색량", f"{int(df['total_volume'].mean()):,}")
        c4.metric("카테고리 수", df['seed'].nunique() if 'seed' in df.columns else 0)
        st.dataframe(df, use_container_width=True, height=450)

# ==========================================================
# 7. 법률 블로그 운영자 인수인계 매뉴얼 (최종 통합본)
# ==========================================================
st.markdown("""
<div class='guide-box'>
    <h2 style='text-align: center; margin-bottom: 50px;'>📑 법률 블로그 운영자 인수인계서 (A to Z)</h2>
    <h3>1. 워드프레스 임시글 확인 및 진입</h3>
    <p>포스팅 생성 완료 후, 워드프레스 관리자 페이지의 [글] > [모든 글] 메뉴로 접속합니다. 목록에서 작성 된 제목을 클릭하여 편집 화면으로 들어갑니다.</p>
    <img src="step1.png" style="width:100%; border-radius:20px; border:1px solid #eee; margin:20px 0;">
    
    <h3 style='margin-top: 40px;'>2. 과장님 검수 / RankMath SEO 설정 (중요)</h3>
    <p>AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 이상한 부분이 없는지 체크하는 단계입니다.</p>
    
    <p><b>1) 스니펫 편집:</b> 제미나이에 본문을 복사한 뒤 제목, 퍼머링크, 설명을 최적화하세요.</p>
    <p><i>"스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘."</i></p>
    <img src="step2.png" style="width:100%; border-radius:20px; margin:10px 0;">
    <img src="step2-1.png" style="width:100%; border-radius:20px; margin:10px 0;">
    
    <p><b>2) 포커스 키워드 및 체크리스트:</b> 제목의 첫 번째 키워드를 삽입하고 랭크매스 점수가 80점 이상이 되도록 수정합니다.</p>
    <img src="step2-2.png" style="width:100%; border-radius:20px; margin:10px 0;">
    <img src="step2-3.png" style="width:100%; border-radius:20px; margin:10px 0;">
    <img src="step2-4.png" style="width:100%; border-radius:20px; margin:10px 0;">
    
    <h3>3. 공개 일정 예약</h3>
    <p>하루 10개는 즉시 업로드, 나머지 10개는 매일 오전 9시 발행되도록 예약을 걸어둡니다.</p>
    <img src="step3.png" style="width:100%; border-radius:20px; margin:10px 0;">
    <img src="step3-1.png" style="width:100%; border-radius:20px; margin:10px 0;">
    <img src="step3-2.png" style="width:100%; border-radius:20px; margin:10px 0;">
    <img src="step4.png" style="width:100%; border-radius:20px; margin:10px 0;">
</div>
""", unsafe_allow_html=True)