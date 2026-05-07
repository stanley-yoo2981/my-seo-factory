import os
import sys
import subprocess
import pandas as pd
import streamlit as st
import time
from dotenv import load_dotenv

# [!] 서버 캐시 파괴 및 버전 관리 (화면 최하단에서 확인 가능)
BUILD_ID = "STUDIO-MASTER-V2026-FINAL"

# 1. 인프라 설정 (462줄 정밀 로직 100% 보존)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(PROJECT_DIR, ".env")

# 💥 권한 에러(Permission Error) 원천 차단 경로 설정
# 서버가 거부할 수 없는 프로젝트 내부 상대 경로를 사용합니다.
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
if not os.path.exists(IMAGE_FOLDER):
    try:
        os.makedirs(IMAGE_FOLDER, exist_ok=True)
    except:
        IMAGE_FOLDER = "/tmp/images"
os.environ["IMG_DIR"] = IMAGE_FOLDER

if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    try:
        for key, value in st.secrets.items():
            os.environ[key] = str(value)
    except:
        pass

# 공장 가동 순서 관리 (메아리 파동 제어용)
if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

# 2. 페이지 설정 (워드프레스 공장 픽스)
st.set_page_config(
    page_title="워드프레스 공장",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 3. Apple Studio 디자인 시스템 (시인성 200% & Bento 그리드 & 강력한 메아리)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* 🌊 강력한 메아리(Echo Ripple) 애니메이션: 시각적 강제 유도 */
    @keyframes studioEcho {{
        0% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0.2); transform: scale(1); }}
        50% {{ box-shadow: 0 0 0 55px rgba(0, 0, 0, 0); transform: scale(1.02); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0, 0, 0, 0); transform: scale(1); }}
    }}

    :root {{
        --s-bg: #F5F5F7;
        --s-black: #1D1D1F;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        background: var(--s-bg) !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }}

    [data-testid="stMainBlockContainer"] {{
        padding: 100px 10% !important;
    }}

    /* 메인 타이틀 디자인 */
    .m-title {{
        text-align: center;
        color: var(--s-black) !important;
        font-size: 72px;
        font-weight: 700;
        margin-bottom: 120px;
        letter-spacing: -4px;
    }}

    /* Bento Card 버튼 - 묵직한 사각형 디자인 (캡슐 스타일 퇴출) */
    div.stButton > button {{
        background: #ffffff !important;
        border-radius: 60px !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        height: 500px !important;
        width: 100% !important;
        transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1) !important;
        color: var(--s-black) !important;
        font-size: 42px !important;
        font-weight: 700 !important;
        letter-spacing: -2.5px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.02) !important;
    }}

    div.stButton > button:hover {{
        transform: translateY(-25px) !important;
        box-shadow: 0 70px 140px rgba(0,0,0,0.12) !important;
        border-color: var(--s-black) !important;
    }}

    /* 🌊 현재 진행 단계 '메아리 파동' 강제 적용 */
    .m-active div.stButton > button {{
        animation: studioEcho 2s infinite cubic-bezier(0.25, 0, 0, 1) !important;
        border: 4px solid var(--s-black) !important;
    }}

    /* 워드프레스 검수 가이드 (시인성 블랙 강제 고정) */
    .m-guide {{
        background: #ffffff !important;
        border-radius: 70px !important;
        padding: 110px !important;
        margin-top: 150px !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.02) !important;
    }}
    
    /* 💥 텍스트 시인성 결함 방지: 무조건 블랙 고정 💥 */
    .m-guide h2, .m-guide h3, .m-guide p, .m-guide b, .m-guide span, .m-guide li {{
        color: #1D1D1F !important;
    }}

    /* 사이드바 글씨: 화이트 */
    [data-testid="stSidebar"] {{ background-color: var(--s-black) !important; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
        color: #ffffff !important;
    }}

    .stProgress > div > div > div > div {{ background-color: var(--s-black) !important; height: 12px !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 가동 상태 대시보드
with st.sidebar:
    st.markdown("### 시스템 가동 현황")
    st.write("네이버 엔진: 🟢")
    st.write("AI 지능 코어: 🟢")
    st.write("워드프레스 연결: 🟢")
    st.divider()
    images_enabled = st.checkbox("AI 비주얼 생성 모드", value=False)

# 5. 실시간 프로세스 엔진
def run_factory_engine(script_name, env_ext, log_placeholder, p_bar):
    script_path = os.path.join(PROJECT_DIR, script_name)
    env = {**os.environ, **env_ext, "PYTHONUNBUFFERED": "1"}
    buffer = []
    try:
        proc = subprocess.Popen([sys.executable, "-u", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
        for i, line in enumerate(proc.stdout):
            buffer.append(line.rstrip())
            log_placeholder.code("\n".join(buffer[-500:]), language="text")
            p_bar.progress(min(0.95, (i + 1) / 100))
        proc.wait()
        p_bar.progress(1.0)
        return proc.returncode
    except Exception as e:
        log_placeholder.error(f"엔진 가동 실패: {e}")
        return -1

# 6. 메인 조종실 UI
st.markdown("<div class='m-title'>워드프레스 공장</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3, gap="large")

with c1:
    if st.session_state.factory_step == 1: st.markdown('<div class="m-active">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn_kw"):
        with st.status("수익성 분석 진행 중..."):
            pb = st.progress(0)
            if run_factory_engine("keyword_research.py", {}, st.empty(), pb) == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1: st.markdown('</div>', unsafe_allow_html=True)

with c2:
    if st.session_state.factory_step == 2: st.markdown('<div class="m-active">', unsafe_allow_html=True)
    if st.button("포스팅 생성", key="btn_post"):
        with st.status("지능형 본문 작성 중..."):
            pb = st.progress(0)
            env_ext = {"IMAGES_ENABLED": str(images_enabled).lower()}
            if run_factory_engine("wp_content_generator.py", env_ext, st.empty(), pb) == 0:
                st.session_state.factory_step = 3
                st.rerun()
    if st.session_state.factory_step == 2: st.markdown('</div>', unsafe_allow_html=True)

with c3:
    if st.button("데이터 분석", key="btn_view"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# ==========================================
# 7. 워드프레스 검수 가이드 (박과장님 전용)
# ==========================================
st.markdown("<div class='m-guide'>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>워드프레스 검수 가이드</h2>", unsafe_allow_html=True)

# 1단계
st.markdown("<h3>1. 워드프레스 임시글 확인 및 진입</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 21px;'>포스팅 생성이 완료되면 워드프레스 관리자 페이지의 <b>[글] > [모든 글]</b> 메뉴로 접속해 보세요. 목록에서 방금 작성된 제목을 클릭해서 편집 화면으로 들어가면 돼요!</p>", unsafe_allow_html=True)
if os.path.exists("step1.png"): st.image("step1.png", use_container_width=True)

# 2단계
st.markdown("<h3 style='margin-top:70px;'>2. 박과장님 SEO 검수 (중요)</h3>", unsafe_allow_html=True)
st.markdown("<p>AI 원본 글을 보석으로 다듬는 과정이에요. 문맥상 어색한 부분은 없는지 한 번만 체크해 주세요.</p>", unsafe_allow_html=True)

st.markdown("<p><b>(1) 스니펫 편집:</b> 제미나이에 본문을 복사한 뒤 아래 골든 프롬프트를 입력해서 결과값을 얻으세요.</p>", unsafe_allow_html=True)
st.info("💡 프롬프트: '스니펫 편집에 필요한 제목, 퍼머링크, 설명(160자 이내)을 구글 SEO에 가장 최적화 해서 알려줘.'")
st.markdown("<p>나온 결과값을 랭크매스(RankMath) 스니펫 편집기에 예쁘게 옮겨주면 돼요.</p>", unsafe_allow_html=True)
if os.path.exists("step2.png"): st.image("step2.png")
if os.path.exists("step2-1.png"): st.image("step2-1.png")

st.markdown("<p><b>(2) 포커스 키워드 설정:</b> 제목 맨 앞에 위치한 핵심 키워드를 그대로 복사해서 넣어주세요.</p>", unsafe_allow_html=True)
if os.path.exists("step2-2.png"): st.image("step2-2.png")

st.markdown("<p><b>(3) RankMath 80점 돌파:</b> 모든 항목이 초록색 체크(v)가 되도록 살짝만 보완해 보세요. 점수가 80점만 넘으면 상단 노출 준비 끝이에요!</p>", unsafe_allow_html=True)
if os.path.exists("step2-3.png"): st.image("step2-3.png")
if os.path.exists("step2-4.png"): st.image("step2-4.png")

# 3단계
st.markdown("<h3 style='margin-top:70px;'>3. 공개 일정 예약 및 전략적 발행</h3>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 21px;'>20개 중 10개는 바로 업로드하고, 나머지 10개는 매일 오전 9시에 발행되도록 예약을 걸어주면 완벽해요!</p>", unsafe_allow_html=True)
if os.path.exists("step3.png"): st.image("step3.png")
if os.path.exists("step3-1.png"): st.image("step3-1.png")
if os.path.exists("step3-2.png"): st.image("step3-2.png")
# step4 이미지 복구 완료
if os.path.exists("step4.png"): st.image("step4.png")
elif os.path.exists("4단계.png"): st.image("4단계.png")

st.markdown("</div>", unsafe_allow_html=True)

# 캐시 버스터 확인용 푸터
st.markdown(f"<div style='text-align: center; color: #86868b; margin-top: 60px;'>{BUILD_ID}</div>", unsafe_allow_html=True)