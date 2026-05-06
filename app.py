import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 1. 프로젝트 경로 및 API 강제 연결
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

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Apple Pro Studio CSS (가독성 및 디자인 최적화)
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
    }

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
        padding: 24px !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. API 연결 상태 확인
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL"))

with st.sidebar:
    st.markdown("### **시스템 상태**")
    st.write("네이버 API:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI API:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 이미지 생성 모드", value=False)

# 5. subprocess 스트리밍 엔진
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

# 6. 메인 UI
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="studio-card"><h3>키워드 분석</h3></div>', unsafe_allow_html=True)
    if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True):
        with st.status("분석 중..."):
            stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, st.empty())

with col2:
    st.markdown('<div class="studio-card"><h3>포스팅 생성</h3></div>', unsafe_allow_html=True)
    if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True):
        with st.status("생성 중..."):
            stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], {"IMAGES_ENABLED": str(images_enabled).lower()}, st.empty())

with col3:
    st.markdown('<div class="studio-card"><h3>데이터 분석</h3></div>', unsafe_allow_html=True)
    if st.button("데이터 보기", key="btn_view", type="primary", use_container_width=True):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        st.dataframe(df, use_container_width=True, height=450)

# 7. 운영자 인수인계 매뉴얼 (사장님 원고 반영)
st.markdown("""
<div class='guide-box'>
    <h2 style='text-align: center; margin-bottom: 40px;'>📑 법률 블로그 운영자 인수인계서 (A to Z)</h2>
    
    <h3>1. 워드프레스 임시글 확인 및 진입</h3>
    <p>포스팅 생성 완료 후, [글] > [모든 글] 메뉴로 접속하여 작성된 제목을 클릭합니다.</p>
    <img src="step1.png" style="width:100%; border-radius:20px; margin:20px 0;">
    
    <h3>2. 과장님 검수 / RankMath SEO 설정 (중요)</h3>
    <p><b>1) 스니펫 편집:</b> 제미나이에 본문을 복사한 뒤 아래 프롬프트를 사용하여 제목, 퍼머링크, 설명을 최적화하세요.</p>
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