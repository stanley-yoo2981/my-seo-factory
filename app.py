import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 1. 프로젝트 경로 및 API 강제 연결 (서버 환경 대응)
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

# 3. Apple Pro Studio Ultra-Premium CSS (시인성 최적화)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    @keyframes studioReveal {
        0% { transform: scale(0.97); opacity: 0; filter: blur(15px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    :root {
        --bg-apple: #F5F5F7;
        --glass-white: rgba(255, 255, 255, 0.5);
        --titanium-black: #1D1D1F;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg-apple) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
        color: var(--titanium-black) !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding: 80px 100px !important;
        animation: studioReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    /* 사이드바 텍스트 검은색 고정 */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h3 {
        color: #1d1d1f !important;
        font-weight: 600 !important;
    }

    .studio-card {
        background: var(--glass-white) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 35px !important;
        padding: 50px 40px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        min-height: 350px !important;
    }

    button[kind="primary"] {
        background: var(--titanium-black) !important;
        color: white !important;
        border-radius: 999px !important;
        padding: 14px 45px !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }

    /* 하단 가이드 박스: 흰 배경에 선명한 검은색 글씨 */
    .guide-box {
        background: #ffffff !important;
        border-radius: 30px !important;
        padding: 50px !important;
        margin-top: 60px !important;
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
        padding: 24px !important;
    }

    [data-baseweb="tab-list"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# 4. API 연결 상태 확인
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

# 5. subprocess 스트리밍 로직 (원본 복구)
def stream_subprocess(cmd, env_extra, log_placeholder):
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
            log_placeholder.code("\n".join(buffer[-1000:]), language="text")
        proc.wait()
        return proc.returncode, buffer
    except Exception as e:
        log_placeholder.error(f"실행 실패: {e}")
        return -1, []

# 6. 메인 UI 조종석
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="studio-card"><h3>키워드 분석</h3></div>', unsafe_allow_html=True)
    if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True):
        with st.status("분석 중...", expanded=True) as status:
            log_box = st.empty()
            rc, _ = stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box)
            if rc == 0: status.update(label="분석 완료", state="complete")

with col2:
    st.markdown('<div class="studio-card"><h3>포스팅 생성</h3></div>', unsafe_allow_html=True)
    if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True):
        env_extra = {"IMAGES_ENABLED": str(images_enabled).lower()}
        with st.status("생성 중...", expanded=True) as status:
            log_box = st.empty()
            rc, buf = stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box)
            if rc == 0:
                edit_line = next((ln for ln in buf if "post.php?post=" in ln), None)
                if edit_line: st.success(f"생성 완료: {edit_line.split()[-1].strip()}")

with col3:
    st.markdown('<div class="studio-card"><h3>데이터 분석</h3></div>', unsafe_allow_html=True)
    if st.button("데이터 보기", key="btn_view", type="primary", use_container_width=True):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("발굴 키워드", f"{len(df)}개")
        c2.metric("최대 검색량", f"{int(df['total_volume'].max()):,}")
        c3.metric("평균 검색량", f"{int(df['total_volume'].mean()):,}")
        c4.metric("시드 카테고리", df['seed'].nunique() if 'seed' in df.columns else 0)
        st.dataframe(df, use_container_width=True, height=450)

# 7. 사장님표 운영자 인수인계 매뉴얼
st.markdown("""
<div class='guide-box'>
    <h2 style='text-align: center; margin-bottom: 40px;'>📑 워드프레스 사용방법 </h2>
    <h3>1. 워드프레스 임시글 확인 및 진입</h3>
    <p>포스팅 생성 완료 후, [글] > [모든 글] 메뉴로 접속하여 임시글 제목을 클릭합니다.</p>
    <img src="step1.png" style="width:100%; border-radius:20px; margin:20px 0;">
    
    <h3 style='margin-top: 40px;'>2. 과장님 검수 / RankMath SEO 설정</h3>
    <p>AI 글을 다듬고 스니펫 편집, 포커스 키워드를 설정합니다.</p>
    <img src="step2.png" style="width:100%; border-radius:20px; margin:20px 0;">
    
    <h3 style='margin-top: 40px;'>3. 공개 일정 예약 및 발행</h3>
    <p>달력 기능을 이용해 매일 오전 9시에 발행되도록 예약을 걸어둡니다.</p>
    <img src="step3.png" style="width:100%; border-radius:20px; margin:20px 0;">
</div>
""", unsafe_allow_html=True)