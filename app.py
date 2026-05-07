import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [!] 업데이트 캐시 클리어 태그
BUILD_TAG = "V2.0-PREMIUM-SLIDE-DESIGN"

# 1. 경로 설정 (권한 에러 방지)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.environ["IMG_DIR"] = IMAGE_FOLDER
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")

if os.path.exists(os.path.join(PROJECT_DIR, ".env")):
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))

if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

# 2. 페이지 세팅
st.set_page_config(page_title="워드프레스 공장", layout="wide", initial_sidebar_state="collapsed")

# 3. 🎨 프리미엄 슬라이드 감성 CSS (거대 사각형 + 찌꺼기 제거)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    :root {{
        --bg-warm: #fff3dd; /* 슬라이드의 따뜻한 크림 배경 */
        --rose-accent: #A26769; /* 로즈 골드 포인트 */
        --card-bg: #F4F0E6; /* 타일 배경색 */
        --text-dark: #2E2E33 !important;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: var(--bg-warm) !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* 💥 거대 벤토 사각형 버튼 강제 세팅 💥 */
    div[data-testid="stButton"] > button {{
        background-color: var(--card-bg) !important;
        color: var(--text-dark) !important;
        border-radius: 20px !important; /* 동그라미 방지: 20px로 부드러운 사각형 유지 */
        border: 1px solid rgba(46, 46, 51, 0.1) !important;
        
        width: 100% !important;
        min-height: 250px !important; /* 버튼을 무조건 큼직하게 유지 */
        
        font-size: clamp(24px, 2vw, 36px) !important;
        font-weight: 800 !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: translateY(-8px) !important;
        box-shadow: 0 25px 50px rgba(162, 103, 105, 0.2) !important;
        border-color: var(--rose-accent) !important;
        color: var(--rose-accent) !important;
    }}

    /* 현재 진행 단계 타일 강조 */
    .active-engine div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 3px solid var(--rose-accent) !important;
    }}

    /* 이쁜 그라데이션 로딩바 */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 12px !important;
        border-radius: 10px !important;
    }}

    /* 모든 기본 텍스트 색상 블랙 고정 */
    p, h1, h2, h3, li, span {{
        color: var(--text-dark) !important;
    }}

    /* 상태창 디자인 */
    [data-testid="stStatusWidget"] {{
        background-color: #ffffff !important; 
        border: 1px solid #A26769 !important; 
        border-radius: 12px !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. 안전한 실행 엔진
def run_factory_script(filename):
    script_path = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(script_path):
        st.error(f"🚨 '{filename}' 파일이 깃허브에 없습니다!")
        return -1
    try:
        proc = subprocess.Popen([sys.executable, "-u", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_DIR, bufsize=1)
        for line in proc.stdout:
            st.write(f"⚙️ {line.strip()}")
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.error(f"❌ 오류: {str(e)}")
        return -1

# 5. 메인 조종실
st.markdown("<h1 style='text-align:center; font-size:70px; margin-bottom:60px;'>워드프레스 공장 2.0</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("1. 키워드 분석", key="btn1"):
        with st.status("🔍 키워드 데이터 수집 중...", expanded=True):
            if run_factory_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("2. 포스팅 생성", key="btn2"):
        with st.status("✍️ AI 본문 최적화 작성 중...", expanded=True):
            if run_factory_script("wp_content_generator.py") == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("3. 데이터 분석", key="btn3"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# 6. 로딩바 및 단계 표시
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
if st.session_state.factory_step == 1:
    st.markdown("<h3>✨ 엔진 대기 중: 키워드 분석을 시작해주세요.</h3>", unsafe_allow_html=True)
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.markdown("<h3>✨ 키워드 확보 완료: 포스팅 생성을 시작해주세요.</h3>", unsafe_allow_html=True)
    st.progress(0.5)
else:
    st.markdown("<h3>✅ 공정 완료: 하단의 검수 가이드를 확인하세요.</h3>", unsafe_allow_html=True)
    st.progress(1.0)

st.divider()

# 7. 📖 워드프레스 검수 가이드 (유령 박스 원천 차단 - 순수 스트림릿 마크다운 활용)
st.markdown("<h1 style='color:#A26769 !important; text-align:center; margin-top:20px; margin-bottom:40px;'>워드프레스 검수 가이드</h1>", unsafe_allow_html=True)

st.header("1. 워드프레스 임시글 확인 및 진입")
st.write("포스팅 생성이 완료되면 워드프레스 관리자 페이지의 **[글] > [모든 글]** 메뉴로 접속하세요. 목록에서 작성된 제목을 클릭하여 편집 화면으로 들어갑니다.")
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

st.header("2. 과장님 검수 / RankMath SEO 설정 (중요)")
st.write("AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 이상한 부분이 없는지 체크하는 단계입니다.")

st.subheader("1) 스니펫 편집")
st.info("💡 제미나이에 본문 글을 모두 복사 붙여넣기 후 아래 내용을 입력하세요:\n\n**\"스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘.\"**\n\n결과를 RankMath 스니펫 편집기에 복사해 넣습니다.")
if os.path.exists("step2.png"): st.image("step2.png", use_container_width=True)
if os.path.exists("step2-1.png"): st.image("step2-1.png", use_container_width=True)

st.subheader("2) 포커스 키워드")
st.write("제목 맨 첫번째 키워드를 삽입합니다.")
if os.path.exists("step2-2.png"): st.image("step2-2.png", use_container_width=True)

st.subheader("3) Rank Math 초록불 만들기")
st.write("기본 SEO, 추가, 제목 가독성, 콘텐츠 가독성이 모두 초록색 v 표시가 되도록 수정 및 보완합니다.")
if os.path.exists("step2-3.png"): st.image("step2-3.png", use_container_width=True)
if os.path.exists("step2-4.png"): st.image("step2-4.png", use_container_width=True)

st.header("3. 공개일정 예약")
st.write("구글 애드센스 승인을 위해 마이너하며 전문적인 콘텐츠 20개를 발행합니다. 20개 중 **하루에 10개 콘텐츠는 모두 업로드**하고, 나머지 10개는 **매일 오전 9시 발행**되도록 예약 걸어두세요.")
if os.path.exists("step3.png"): st.image("step3.png", use_container_width=True)
if os.path.exists("step3-1.png"): st.image("step3-1.png", use_container_width=True)
if os.path.exists("step3-2.png"): st.image("step3-2.png", use_container_width=True)
if os.path.exists("step4.png"): st.image("step4.png", use_container_width=True)

st.markdown(f"<p style='text-align:center; color:#8B7E6A; margin-top:60px;'>{BUILD_TAG}</p>", unsafe_allow_html=True)