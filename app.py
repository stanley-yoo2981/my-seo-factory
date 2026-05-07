import os
import sys
import subprocess
import base64
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [!] 업데이트 확인용 태그
BUILD_TAG = "V2.0-FINAL-LINK-BUTTON"

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

# 2. 페이지 세팅
st.set_page_config(page_title="워드프레스 공장", layout="wide", initial_sidebar_state="collapsed")

# 3. 🎨 프리미엄 UI 디자인 (거대 정사각형 + 리플 효과)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');

    @keyframes rippleAnim {{
        0% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0.4); transform: scale(1); }}
        70% {{ box-shadow: 0 0 0 40px rgba(162, 103, 105, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(162, 103, 105, 0); transform: scale(1); }}
    }}

    :root {{
        --bg-color: #FDF7F0; 
        --rose: #A26769;
    }}

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: var(--bg-color) !important;
    }}

    /* 🍱 거대 1:1 정방향 사각형 버튼 */
    div[data-testid="stButton"] > button {{
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
        border-radius: 24px !important;
        border: 2px solid rgba(162, 103, 105, 0.15) !important;
        width: 100% !important;
        aspect-ratio: 1 / 1 !important; 
        min-height: 280px !important;
        font-size: clamp(20px, 2.5vw, 36px) !important;
        font-weight: 800 !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    div[data-testid="stButton"] > button:hover {{
        transform: translateY(-10px) !important;
        box-shadow: 0 30px 60px rgba(162, 103, 105, 0.15) !important;
        border-color: var(--rose) !important;
        color: var(--rose) !important;
    }}

    .active-engine div[data-testid="stButton"] > button {{
        animation: rippleAnim 2s infinite !important;
        border: 4px solid var(--rose) !important;
    }}

    /* 글 확인하기 버튼 전용 스타일 (지름길 버튼) */
    .link-button {{
        display: inline-block;
        background-color: var(--rose);
        color: white !important;
        padding: 20px 40px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 700;
        font-size: 20px;
        margin-top: 20px;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(162, 103, 105, 0.2);
    }}
    .link-button:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(162, 103, 105, 0.4);
        background-color: #8b5658;
    }}

    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #A26769, #D5B9B2) !important;
        height: 14px !important;
    }}

    /* 상태창 디자인 픽스 */
    [data-testid="stStatusWidget"] {{ background-color: #FFFFFF !important; border: 1px solid #A26769 !important; }}
    [data-testid="stStatusWidget"] * {{ color: #1D1D1F !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 파일 실행 로직
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

# 5. 메인 UI
st.markdown("<h1 style='text-align:center; color:#1D1D1F; font-size:68px; font-weight:800; margin-bottom:80px;'>워드프레스 공장</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    if st.session_state.factory_step == 1: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn1"):
        with st.status("🔍 분석 중...", expanded=True):
            if run_factory_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.session_state.factory_step == 2: st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="btn2"):
        with st.status("✍️ 작성 중...", expanded=True):
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

# 6. 로딩바 및 단계 표시
st.markdown("<div style='margin-top: 80px;'></div>", unsafe_allow_html=True)
if st.session_state.factory_step == 1:
    st.markdown("<h3 style='color:#1D1D1F;'>✨ 1단계 대기 중</h3>", unsafe_allow_html=True)
    st.progress(0.0)
elif st.session_state.factory_step == 2:
    st.markdown("<h3 style='color:#1D1D1F;'>✨ 2단계 준비 완료</h3>", unsafe_allow_html=True)
    st.progress(0.5)
else:
    st.markdown("<h3 style='color:#1D1D1F;'>✅ 모든 공정 완료!</h3>", unsafe_allow_html=True)
    st.progress(1.0)
    # 💥 사장님 지시: 공정 완료 시 글 확인하기 버튼 노출 💥
    st.markdown('<div style="text-align: center;"><a href="https://law-brief.kr/wp-admin/" target="_blank" class="link-button">🚀 글 확인하기 (워드프레스 이동)</a></div>', unsafe_allow_html=True)

# 7. 📖 워드프레스 검수 가이드
def get_img_html(filename):
    img_path = os.path.join(PROJECT_DIR, filename)
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{encoded}" style="width:100%; max-width:800px; border-radius:12px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">'
    return ""

guide_html = f"""
<div style="background-color: #FFFFFF; border-radius: 40px; padding: 80px; margin-top: 50px; border: 1px solid rgba(162, 103, 105, 0.15); box-shadow: 0 15px 40px rgba(0,0,0,0.03); color: #1D1D1F;">
    <h1 style="text-align:center; color:#A26769; margin-bottom:60px;">워드프레스 검수 가이드</h1>
    
    <h2 style="color:#1D1D1F; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">1. 워드프레스 임시글 확인 및 진입</h2>
    <p style="font-size: 18px; line-height: 1.8;">
        포스팅 생성이 완료되면 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속하세요. 목록에서 작성된 제목을 클릭하여 편집 화면으로 들어갑니다.
    </p>
    {get_img_html("step1.png")}
    
    <h2 style="color:#1D1D1F; margin-top:60px; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">2. 과장님 검수 / RankMath SEO 설정 (중요)</h2>
    <p style="font-size: 18px; line-height: 1.8;">
        AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 이상한 부분이 없는지 체크하는 단계입니다.
    </p>
    
    <h3 style="color:#A26769; margin-top:30px;">1) 스니펫 편집</h3>
    <p style="font-size: 16px; line-height: 1.8; background-color:#F4F0E6; padding: 20px; border-radius: 10px;">
        제미나이에 본문 글을 모두 복사 붙여넣기 후 아래 내용을 입력하세요:<br><br>
        <b>"스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO, AEO에 가장 최적화 하여 알려줘."</b><br><br>
        결과를 RankMath 스니펫 편집기에 복사해 넣습니다.
    </p>
    {get_img_html("step2.png")}
    {get_img_html("step2-1.png")}
    
    <h3 style="color:#A26769; margin-top:30px;">2) 포커스 키워드</h3>
    <p style="font-size: 18px;">제목 맨 첫번째 키워드를 삽입합니다.</p>
    {get_img_html("step2-2.png")}
    
    <h3 style="color:#A26769; margin-top:30px;">3) Rank Math 초록불 만들기</h3>
    <p style="font-size: 18px;">기본 SEO, 추가, 제목 가독성, 콘텐츠 가독성이 모두 초록색 v 표시가 되도록 보완합니다.</p>
    {get_img_html("step2-3.png")}
    
    <h3 style="color:#A26769; margin-top:40px; background-color: #f8f9fa; padding: 30px; border-radius: 20px;">💡 4) 기타 경고 안내 (무시 가능)</h3>
    <ul style="font-size: 16px; line-height: 1.8;">
        <li><b>"Table of Contents plugin를 사용하지 않는 것 같습니다."</b><br>
            <span style="color: #666;">우리 공장은 이미 구글이 좋아하는 '수제 HTML 목차'를 본문에 찍어내고 있습니다. RankMath가 특정 플러그인을 찾지 못해 띄우는 경고이니 무시하셔도 노출에는 100% 지장이 없습니다.</span>
        </li>
        <li style="margin-top: 15px;"><b>"Content AI를 사용하여 Post를 최적화하십시오."</b><br>
            <span style="color: #666;">RankMath 회사의 유료 서비스 광고입니다. 무시하셔도 됩니다.</span>
        </li>
    </ul>

    <h2 style="color:#1D1D1F; margin-top:60px; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">3. 공개일정 예약</h2>
    <p style="font-size: 18px; line-height: 1.8;">
        구글 애드센스 승인을 위해 20개 중 <b>하루에 10개는 즉시 업로드</b>하고, 나머지 10개는 <b>매일 오전 9시 발행</b>되도록 예약 걸어두세요.
    </p>
    {get_img_html("step4.png")}
</div>
"""
st.markdown(guide_html, unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; color:#8B7E6A; margin-top:40px;'>{BUILD_TAG}</div>", unsafe_allow_html=True)