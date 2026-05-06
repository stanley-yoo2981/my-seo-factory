import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 1. 프로젝트 경로 및 API 강제 연결 (PDF 원본 로직 100% 복구)
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

# 2. 페이지 설정 (파비콘: ⚖️ 저울)
st.set_page_config(
    page_title="SEO 자동화 공장 Pro",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Apple Pro Studio Ultra-Premium CSS (매뉴얼 시인성 극대화)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    @keyframes studioReveal {
        0% { transform: scale(0.97); opacity: 0; filter: blur(15px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    :root {
        --bg-apple: #F5F5F7;
        --glass-white: rgba(255, 255, 255, 0.45);
        --glass-border: rgba(255, 255, 255, 0.8);
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

    .studio-card {
        background: var(--glass-white) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 35px !important;
        padding: 50px 40px !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 350px !important;
    }

    button[kind="primary"] {
        background: var(--titanium-black) !important;
        color: white !important;
        border-radius: 999px !important;
        padding: 14px 45px !important;
        font-weight: 500 !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        border: none !important;
    }

    /* 운영 매뉴얼 가이드 박스 디자인 */
    .guide-box {
        background: #ffffff !important;
        border-radius: 40px !important;
        padding: 60px !important;
        margin-top: 80px !important;
        color: #1d1d1f !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }

    .manual-step {
        border-bottom: 1px solid #f2f2f7;
        padding-bottom: 40px;
        margin-bottom: 40px;
    }

    .manual-step:last-child { border: none; }

    .step-title {
        font-size: 28px !important;
        font-weight: 600 !important;
        margin-bottom: 20px !important;
        display: flex;
        align-items: center;
    }

    .step-number {
        background: #1d1d1f;
        color: white;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-right: 15px;
    }

    .img-caption {
        font-size: 14px;
        color: #86868b;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 30px;
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

# 5. subprocess 실시간 스트리밍 엔진 (원본 로직 복원)
def stream_subprocess(cmd: list, env_extra: dict, log_placeholder, max_lines=1000):
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

# 6. 메인 UI
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="studio-card"><div style="font-size: 24px; font-weight: 600; margin-bottom: 12px;">키워드 분석</div><p style="color: #86868b; text-align: center;">네이버 실시간 데이터를 분석하여<br>수익성 높은 키워드를 발굴합니다</p></div>', unsafe_allow_html=True)
    if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True):
        with st.status("분석 중...", expanded=True):
            log_box = st.empty()
            stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box)

with col2:
    st.markdown('<div class="studio-card"><div style="font-size: 24px; font-weight: 600; margin-bottom: 12px;">포스팅 생성</div><p style="color: #86868b; text-align: center;">AI가 독창적인 법률 본문을 작성하고<br>워드프레스에 임시글로 발행합니다</p></div>', unsafe_allow_html=True)
    if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True):
        env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
        with st.status("발행 중...", expanded=True):
            log_box = st.empty()
            stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box)

with col3:
    st.markdown('<div class="studio-card"><div style="font-size: 24px; font-weight: 600; margin-bottom: 12px;">데이터 분석</div><p style="color: #86868b; text-align: center;">발굴된 키워드 통계를 분석하고<br>공장 가동 현황을 확인합니다</p></div>', unsafe_allow_html=True)
    if st.button("데이터 보기", key="btn_view", type="primary", use_container_width=True):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        st.dataframe(df, use_container_width=True, height=450)

# ==========================================================
# 7. 사장님표 A to Z 운영자 인수인계 매뉴얼 (최종 통합본)
# ==========================================================
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; margin-bottom: 60px;'>📑 법률 블로그 운영자 인수인계서 (A to Z)</h2>", unsafe_allow_html=True)

# --- Step 1 ---
st.markdown("<div class='manual-step'>", unsafe_allow_html=True)
st.markdown("<div class='step-title'><div class='step-number'>1</div>1. 워드프레스 임시글 확인 및 진입</div>", unsafe_allow_html=True)
st.markdown("포스팅 생성 완료 후, 워드프레스 관리자 페이지의 **[글] > [모든 글]** 메뉴로 접속합니다. 목록에서 작성된 제목을 클릭하여 편집 화면으로 들어갑니다.")
st.image("step1.png", use_container_width=True)
st.markdown("<div class='img-caption'>워드프레스 '모든 글' 목록 화면</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Step 2 ---
st.markdown("<div class='manual-step'>", unsafe_allow_html=True)
st.markdown("<div class='step-title'><div class='step-number'>2</div>2. 과장님 검수 / RankMath SEO 설정 (중요)</div>", unsafe_allow_html=True)
st.markdown("AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 이상한 부분이 없는지 체크하는 단계입니다.")

st.markdown("#### **1) 스니펫 편집**")
st.markdown("제목, 퍼머링크, 설명(160자 이내)을 설정합니다. 해당 내용은 제미나이(Gemini)에 본문 글을 모두 복사 붙여넣기 후 아래 프롬프트를 사용하세요.")
st.info("**프롬프트:** \"스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.\"")
st.markdown("제미나이가 알려주는 대로 복사하여 붙여넣기 합니다.")
st.image(["step2.jpg", "step2-1.png"], use_container_width=True)

st.markdown("#### **2) 포커스 키워드**")
st.markdown("제목의 **맨 첫 번째 키워드**를 포커스 키워드 란에 삽입합니다.")
st.image("step2-2.jpg", use_container_width=True)

st.markdown("#### **3) Rank Math 체크리스트 최적화**")
st.markdown("Rank Math가 안내하는 **기본 SEO, 추가, 제목 가독성, 콘텐츠 가독성** 항목이 모두 초록색 체크표시(v)가 되도록 수정 및 보완하세요. **80점 이상**이면 OK입니다.")
st.image(["step2-3.jpg", "step2-4.jpg"], use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Step 3 ---
st.markdown("<div class='manual-step'>", unsafe_allow_html=True)
st.markdown("<div class='step-title'><div class='step-number'>3</div>3. 공개 일정 예약 및 발행</div>", unsafe_allow_html=True)
st.markdown("구글 애드센스 승인을 위해 전문적인 콘텐츠 20개를 전략적으로 발행합니다.")
st.warning("**발행 전략:** 20개 중 하루에 10개 콘텐츠를 즉시 업로드하고, 나머지 10개는 **매일 오전 9시**에 발행되도록 예약을 걸어둡니다.")

col_img1, col_img2 = st.columns(2)
with col_img1:
    st.image("step3.jpg", caption="우측 상단 SEO 점수 및 공개 설정 확인")
    st.image("step3-1.jpg", caption="[공개: 즉시] 클릭하여 달력 열기")
with col_img2:
    st.image("step3-2.jpg", caption="날짜와 시간(09:00) 설정 후 X 버튼 클릭")
    st.image("step4.jpg", caption="마지막으로 우측 상단 [예약] 버튼 클릭 시 완료")

st.success("💡 **마스터 팁:** 꾸준한 예약 발행은 블로그 지수를 높여 검색 상위 노출에 매우 유리합니다.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)