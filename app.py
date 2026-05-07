import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [!] 버전 태그 (이게 'SQUARE-BENTO-V2'로 보여야 합니다)
BUILD_TAG = "SQUARE-BENTO-V2"

# 1. 인프라 및 경로 설정 (Permission Error 완벽 해결)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.environ["IMG_DIR"] = IMAGE_FOLDER
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv") 

if os.path.exists(os.path.join(PROJECT_DIR, ".env")):
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))

if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

# 2. 페이지 설정
st.set_page_config(page_title="워드프레스 공장 V2.0", layout="wide", initial_sidebar_state="collapsed")

# 3. 🎨 프리미엄 벤토 디자인 (1:1 정방향 강제 고정 & 의미 없는 흰색 바 삭제)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    /* 🌊 리플(Ripple) 및 메아리 애니메이션 */
    @keyframes studioRipple {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.3); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 50px rgba(162, 103, 105, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --bg-warm: #FDF7F0; /* 따뜻한 크림색 */
        --rose: #A26769;
        --pure-black: #1D1D1F !important;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: var(--bg-warm) !important;
    }}

    /* 🍱 Bento Card 버튼 - 1:1 정방향 모서리 둥근 정사각형 강제 고정 */
    div[data-testid="stButton"] > button {{
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 60px !important; /* 사장님 지시: 모서리가 둥근 디자인 */
        border: 2px solid rgba(162, 103, 105, 0.15) !important;
        
        /* 💥 빼빼로 모양 원천 봉쇄: 가로 너비=세로 높이 1:1 고정 💥 */
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; 
        height: auto !important;
        
        font-size: clamp(20px, 2.5vw, 36px) !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04) !important;
        transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: translateY(-15px) !important;
        box-shadow: 0 50px 100px rgba(162, 103, 105, 0.15) !important;
        border-color: var(--rose) !important;
        color: var(--rose) !important;
    }}

    /* 🌊 리플 효과 (현재 단계 유도) */
    .active-step div[data-testid="stButton"] > button {{
        animation: studioRipple 2s infinite !important;
        border: 4px solid var(--rose) !important;
    }}

    /* 🎀 여성스러운 그라데이션 로딩바 */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 14px !important;
        border-radius: 10px !important;
    }}

    /* 📖 가이드 박스 - 모든 글자 블랙 고정 */
    .guide-box {{
        background-color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 80px !important;
        margin-top: 40px !important;
        border: 1px solid rgba(162, 103, 105, 0.1) !important;
        box-shadow: 0 15px 45px rgba(0,0,0,0.02) !important;
    }}

    /* 💥 흰색 글씨 박멸 💥 */
    .guide-box *, [data-testid="stMarkdownContainer"] *, .stAlert *, [data-testid="stStatusWidget"] * {{
        color: #1D1D1F !important;
        opacity: 1 !important;
    }}

    [data-testid="stStatusWidget"] {{
        background-color: #FFFFFF !important;
        border: 1px solid var(--rose) !important;
    }}
</style>
""", unsafe_allow_html=True)

# 4. 파일 실행 엔진 (서버 내 절대 경로 추적)
def run_script(filename):
    script_path = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(script_path):
        st.error(f"🚨 '{filename}' 파일이 깃허브에 없습니다! 업로드 확인이 필요합니다.")
        return -1
    try:
        proc = subprocess.Popen([sys.executable, "-u", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=PROJECT_DIR, bufsize=1)
        for line in proc.stdout:
            st.write(f"⚙️ {line.strip()}")
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.error(f"❌ 가동 오류: {str(e)}")
        return -1

# 5. 메인 UI 조종실
st.markdown("<h1 style='text-align:center; color:#1D1D1F; font-size:68px; font-weight:800; margin-bottom:100px; letter-spacing:-3px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-step">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="b1"):
        with st.status("🔍 네이버 데이터 실시간 분석 중...", expanded=True):
            if run_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-step">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="b2"):
        with st.status("✍️ AI 본문 최적화 작성 중...", expanded=True):
            if run_script("wp_content_generator.py") == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="b3"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# 🚀 [로딩바] 사장님 지시: 가이드 바로 위 배치
st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
if st.session_state.factory_step == 1:
    st.markdown("<p style='font-weight:700;'>✨ 1단계: 키워드 분석 대기 중</p>", unsafe_allow_html=True)
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.markdown("<p style='font-weight:700;'>✨ 2단계: 포스팅 생성 준비 완료</p>", unsafe_allow_html=True)
    st.progress(0.5)
else:
    st.markdown("<p style='font-weight:700;'>✅ 모든 공정 완료! 검수 단계로 이동하세요.</p>", unsafe_allow_html=True)
    st.progress(1.0)

# 📖 워드프레스 검수 가이드 (블랙 텍스트 & 정갈한 디자인)
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#A26769 !important; margin-bottom:60px;'>워드프레스 검수 가이드</h1>", unsafe_allow_html=True)

# Step 1
st.markdown("<h2>1. 워드프레스 임시글 확인 및 진입</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 19px;'>공정 완료 후 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속하세요. 목록에서 AI가 생성한 제목을 클릭해 편집 화면으로 들어갑니다.</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

# Step 2
st.markdown("<h2 style='margin-top:60px;'>2. 과장님 검수 / RankMath SEO 설정 (핵심 단계)</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 19px;'>사람이 직접 문맥을 다듬어 '최고급 콘텐츠'로 완성하는 단계입니다.</p>", unsafe_allow_html=True)

st.markdown("<h3 style='color:#A26769 !important;'>① 스니펫 편집 (AEO 최적화)</h3>", unsafe_allow_html=True)
st.info("💡 제미나이에 본문을 복사하고 물어보세요: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO에 최적화해서 알려줘.'")
if os.path.exists("step2.png"): st.image("step2.png")

st.markdown("<h3 style='color:#A26769 !important;'>② 포커스 키워드 설정</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px;'>제목 맨 앞의 핵심 키워드를 복사해서 '포커스 키워드' 칸에 넣어주세요.</p>", unsafe_allow_html=True)

st.markdown("<h3 style='color:#A26769 !important;'>③ RankMath 초록불(v) 켜기</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px;'>안내되는 모든 지표가 초록색이 되도록 살짝만 보완해주세요. 점수 80점 돌파가 목표입니다!</p>", unsafe_allow_html=True)
if os.path.exists("step2-3.png"): st.image("step2-3.png")

# Step 3
st.markdown("<h2 style='margin-top:60px;'>3. 공개일정 예약</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 19px;'>전략적 발행이 중요합니다. <b>10개는 오늘 즉시 발행</b>하고, <b>나머지 10개는 매일 오전 9시에 1개씩</b> 발행되도록 예약을 걸어주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step4.png"): st.image("step4.png")

st.markdown("</div>", unsafe_allow_html=True)

# 버전 태그
st.markdown(f"<div style='text-align:center; color:#8B7E6A; margin-top:60px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)