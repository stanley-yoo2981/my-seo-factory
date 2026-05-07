import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [!] 버전 태그
BUILD_TAG = "V2.0-MASSIVE-TILE-FORCE-01"

# 1. 인프라 및 경로 설정
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

# 3. 🎨 프리미엄 스튜디오 디자인 (거대한 타일 강제 고정 & 완벽한 가독성)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    @keyframes rippleAnim {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.4); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 35px rgba(162, 103, 105, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --bg-color: #FDF7F0; /* 따뜻한 크림색 */
        --rose: #A26769;
        --pure-black: #1D1D1F !important;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: var(--bg-color) !important;
    }}

    /* 💥 스트림릿 무시 방지: 거대한 버튼 강제 구현 💥 */
    div[data-testid="stButton"] > button,
    div.stButton > button {{
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 40px !important;
        border: 2px solid rgba(162, 103, 105, 0.2) !important;
        
        /* 높이와 너비 무조건 꽉 채우기 */
        width: 100% !important;
        height: 350px !important; /* 사장님, 높이를 350픽셀로 대폭 키웠습니다! */
        
        font-size: 40px !important; /* 글씨도 거대하게 */
        font-weight: 800 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 20px !important;
    }}

    div[data-testid="stButton"] > button:hover,
    div.stButton > button:hover {{
        transform: translateY(-15px) !important;
        box-shadow: 0 40px 80px rgba(162, 103, 105, 0.2) !important;
        border-color: var(--rose) !important;
        color: var(--rose) !important;
    }}

    .active-engine div[data-testid="stButton"] > button,
    .active-engine div.stButton > button {{
        animation: rippleAnim 2s infinite !important;
        border: 5px solid var(--rose) !important;
    }}

    /* 로딩바 디자인 */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 14px !important;
    }}

    /* 📖 가이드 박스 - 초보자를 위한 따뜻하고 선명한 디자인 */
    .guide-box {{
        background-color: #FFFFFF !important;
        border-radius: 40px !important;
        padding: 60px 80px !important;
        margin-top: 60px !important;
        border: 1px solid rgba(162, 103, 105, 0.15) !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.03) !important;
    }}

    /* 💥 텍스트 시인성 확보: 모든 글자 블랙 고정 💥 */
    .guide-box *, [data-testid="stMarkdownContainer"] *, .stAlert * {{
        color: #1D1D1F !important;
    }}

    /* 상태창(Status) 배경 & 글씨 픽스 */
    [data-testid="stStatusWidget"] {{ background-color: #FFFFFF !important; border: 1px solid #A26769 !important; }}
    [data-testid="stStatusWidget"] * {{ color: #1D1D1F !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 🚨 안전한 파일 실행 엔진
def run_factory_script(filename):
    script_path = os.path.join(PROJECT_DIR, filename)
    
    if not os.path.exists(script_path):
        st.error(f"🚨 '{filename}' 파일이 서버에 없습니다!\n\n사장님, 깃허브 저장소에 이 파일이 정상적으로 업로드되었는지 꼭 확인해 주세요.")
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
st.markdown("<h1 style='text-align:center; color:#1D1D1F; font-size:64px; font-weight:800; margin-bottom:80px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn1"):
        with st.status("🔍 네이버 API 연동 및 분석 중...", expanded=True):
            if run_factory_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="btn2"):
        with st.status("✍️ AI 본문 생성 중...", expanded=True):
            if run_factory_script("wp_content_generator.py") == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with col3:
    if st.button("데이터 분석", key="btn3"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)
    else:
        st.info("아직 분석된 키워드 데이터(CSV)가 없습니다. '키워드 분석'을 먼저 실행해 주세요.")

# 6. 로딩바 및 현재 상태 표시
st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
if st.session_state.factory_step == 1:
    st.markdown("<h3 style='color:#1D1D1F;'>✨ 1단계: 키워드 분석을 시작해주세요.</h3>", unsafe_allow_html=True)
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.markdown("<h3 style='color:#1D1D1F;'>✨ 2단계: 포스팅 생성 준비 완료!</h3>", unsafe_allow_html=True)
    st.progress(0.5)
else:
    st.markdown("<h3 style='color:#1D1D1F;'>✅ 모든 공정 완료! 가이드를 따라 검수를 진행하세요.</h3>", unsafe_allow_html=True)
    st.progress(1.0)

# 7. 📖 초보자를 위한 '가장 친절한' 워드프레스 검수 가이드
st.markdown("<div class='guide-box'>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; color:#A26769 !important; margin-bottom:50px;'>📝 워드프레스 초보자 검수 가이드</h1>", unsafe_allow_html=True)

# Step 1
st.markdown("<h2 style='color:#1D1D1F;'>1. 워드프레스 임시글 확인 및 진입</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size: 18px; line-height: 1.8;'>
포스팅 생성이 완료되었다면, 이제 워드프레스 관리자 페이지로 이동할 차례입니다!<br>
좌측 메뉴에서 <b>[글] > [모든 글]</b>을 클릭해 접속해 주세요. 목록에 AI가 방금 작성해 둔 임시글이 보일 텐데, 그 <b>제목을 클릭</b>하여 편집 화면으로 들어갑니다.
</p>
""", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

# Step 2
st.markdown("<h2 style='color:#1D1D1F; margin-top:60px;'>2. 과장님 검수 / RankMath SEO 설정 (⭐가장 중요)</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size: 18px; line-height: 1.8;'>
AI가 작성한 원본 글을 사람이 최종적으로 다듬어, 구글 검색이 좋아하는 '완벽한 글'로 만드는 핵심 단계입니다. 문맥상 어색한 부분은 없는지 한 번만 쓱 읽어보며 체크해 주세요.
</p>
""", unsafe_allow_html=True)

st.markdown("<h3 style='color:#A26769 !important; margin-top:30px;'>① 스니펫 편집 (설명글 최적화)</h3>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size: 16px; line-height: 1.8; background-color:#F4F0E6; padding: 20px; border-radius: 10px;'>
제미나이(Gemini)를 활용하면 아주 쉽습니다. 워드프레스 본문 글을 모두 복사해서 제미나이에게 붙여넣기 한 후, 아래 마법의 프롬프트를 입력하세요.<br><br>
<b>"스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘."</b><br><br>
제미나이가 정답을 알려주면, 그 내용을 워드프레스 우측 RankMath 메뉴의 '스니펫 편집' 창에 그대로 복사해서 붙여넣으시면 됩니다!
</p>
""", unsafe_allow_html=True)
if os.path.exists("step2.png"): st.image("step2.png")
if os.path.exists("step2-1.png"): st.image("step2-1.png")

st.markdown("<h3 style='color:#A26769 !important; margin-top:30px;'>② 포커스 키워드 입력</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px;'>작성된 <b>제목의 맨 첫 번째 키워드</b>를 그대로 복사해서 '포커스 키워드' 칸에 쏙 넣어주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step2-2.png"): st.image("step2-2.png")

st.markdown("<h3 style='color:#A26769 !important; margin-top:30px;'>③ RankMath 100점 만들기 (초록불 켜기)</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 18px;'>RankMath가 안내하는 [기본 SEO], [추가], [제목 가독성], [콘텐츠 가독성] 4가지 항목이 <b>모두 초록색 체크(v) 표시</b>가 되도록 조금씩 수정 및 보완해 주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step2-3.png"): st.image("step2-3.png")
if os.path.exists("step2-4.png"): st.image("step2-4.png")

# Step 3
st.markdown("<h2 style='color:#1D1D1F; margin-top:60px;'>3. 공개일정 예약 (전략적 발행)</h2>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size: 18px; line-height: 1.8;'>
구글 애드센스 승인을 위해 마이너하면서 전문적인 콘텐츠 <b>총 20개</b>를 발행해야 합니다.<br>
전략적으로 <b>20개 중 10개는 오늘 즉시 업로드</b>하시고, <b>나머지 10개는 매일 오전 9시에 1개씩 발행</b>되도록 예약 설정을 걸어두세요. 이것으로 모든 세팅이 완벽하게 끝납니다!
</p>
""", unsafe_allow_html=True)
if os.path.exists("step3.png"): st.image("step3.png")
if os.path.exists("step3-1.png"): st.image("step3-1.png")
if os.path.exists("step3-2.png"): st.image("step3-2.png")
if os.path.exists("step4.png"): st.image("step4.png")

st.markdown("</div>", unsafe_allow_html=True)

# 버전 태그
st.markdown(f"<div style='text-align:center; color:#8B7E6A; margin-top:40px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)