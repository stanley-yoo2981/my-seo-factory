import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# 1. 프로젝트 경로 및 API 연결 (PDF 원본 로직 유지)
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

# 3. Apple Pro Studio Ultra-Premium CSS (가시성 및 질감 고도화)
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

    .studio-card:hover {
        background: rgba(255, 255, 255, 0.65) !important;
        box-shadow: 0 40px 80px rgba(0, 0, 0, 0.12) !important;
        transform: translateY(-8px) scale(1.02) !important;
    }

    button[kind="primary"] {
        background: var(--titanium-black) !important;
        color: white !important;
        border-radius: 999px !important;
        padding: 14px 45px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        border: none !important;
    }

    /* 가이드 섹션 스타일 (글자색 검정색으로 강제 고정) */
    .guide-box {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 30px !important;
        padding: 50px !important;
        border: 1px solid rgba(0, 0, 0, 0.05) !important;
        margin-top: 60px !important;
        color: #1d1d1f !important; /* 선명한 검은색 */
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.03) !important;
    }

    .guide-box h2, .guide-box h3, .guide-box h4 {
        color: #1d1d1f !important;
        font-weight: 600 !important;
    }

    .guide-box p, .guide-box li {
        color: #1d1d1f !important;
        line-height: 1.8 !important;
        font-size: 15px !important;
    }

    .capture-placeholder {
        background: rgba(0, 0, 0, 0.03) !important;
        border: 2px dashed rgba(0, 0, 0, 0.1) !important;
        border-radius: 15px !important;
        padding: 20px !important;
        text-align: center !important;
        color: #86868b !important;
        margin: 15px 0 !important;
        font-size: 13px !important;
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
naver_ok = bool(os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY") and os.getenv("NAVER_AD_CUSTOMER_ID"))
openai_ok = bool(os.getenv("OPENAI_API_KEY"))
wp_ok = bool(os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD"))

# 사이드바 (시스템 상태)
with st.sidebar:
    st.markdown("### **시스템 상태**")
    st.write("네이버 API:", "🟢" if naver_ok else "🔴")
    st.write("OpenAI API:", "🟢" if openai_ok else "🔴")
    st.write("워드프레스:", "🟢" if wp_ok else "🔴")
    st.divider()
    images_enabled = st.checkbox("AI 이미지 생성 모드", value=False)

# 5. subprocess 실시간 스트리밍 엔진
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

# 6. 메인 UI
st.markdown("<h1 style='text-align: center; color: #1d1d1f; font-size: 56px; font-weight: 600; margin-bottom: 60px; letter-spacing: -2px;'>SEO 자동화 공장 Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown('<div class="studio-card"><div class="studio-card-title">키워드 분석</div><p style="color: #86868b; text-align: center;">네이버 검색 데이터를 기반으로<br>수익성 높은 키워드를 발굴합니다</p></div>', unsafe_allow_html=True)
    if not naver_ok: st.error("API 연결 필요")
    else:
        if st.button("분석 실행", key="btn_kw", type="primary", use_container_width=True):
            with st.status("분석 중...", expanded=True):
                log_box = st.empty()
                stream_subprocess([sys.executable, "-u", KEYWORD_SCRIPT], {}, log_box)

with col2:
    st.markdown('<div class="studio-card"><div class="studio-card-title">포스팅 생성</div><p style="color: #86868b; text-align: center;">AI가 독창적인 법률 본문을 작성하고<br>워드프레스에 임시글로 발행합니다</p></div>', unsafe_allow_html=True)
    if not wp_ok: st.error("API 연결 필요")
    else:
        if st.button("생성 시작", key="btn_post", type="primary", use_container_width=True):
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
            with st.status("발행 가동 중...", expanded=True):
                log_box = st.empty()
                rc, buf = stream_subprocess([sys.executable, "-u", PUBLISH_SCRIPT], env_extra, log_box)
                if rc == 0:
                    edit_line = next((ln for ln in buf if "post.php?post=" in ln), None)
                    if edit_line: st.success(f"임시글 생성 완료: {edit_line.split()[-1].strip()}")

with col3:
    st.markdown('<div class="studio-card"><div class="studio-card-title">데이터 분석</div><p style="color: #86868b; text-align: center;">발굴된 키워드 통계를 분석하고<br>공장 가동 현황을 확인합니다</p></div>', unsafe_allow_html=True)
    if st.button("데이터 보기", key="btn_view", type="primary", use_container_width=True):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        st.dataframe(df, use_container_width=True)

# 7. A to Z 운영자 인수인계 매뉴얼 섹션 (가독성 강화 버전)
st.markdown("""
<div class='guide-box'>
    <h2 style='text-align: center; margin-bottom: 40px;'>📑 SEO 자동화 공장 운영자 매뉴얼 (A to Z)</h2>
    
    <h3>Phase 1. 대시보드 조종 및 콘텐츠 생산</h3>
    <p>본 프로그램은 법률 키워드를 발굴하고 AI가 본문을 작성하여 워드프레스에 '임시글'로 전송하는 전 과정을 자동화합니다.</p>
    <div class='capture-placeholder'>[캡처 필수: 대시보드 메인 화면 및 사이드바 초록불 상태]</div>
    <ul>
        <li><b>1단계 (분석):</b> [키워드 분석] 카드의 '분석 실행'을 누릅니다. 네이버 광고 API를 통해 황금 키워드를 발굴합니다.</li>
        <li><b>2단계 (생성):</b> 사이드바에서 '이미지 생성 모드' 체크 여부를 결정한 후, [포스팅 생성] 카드의 '생성 시작'을 누릅니다.</li>
        <li><b>3단계 (확인):</b> 작업이 완료되면 초록색 성공 메시지와 함께 워드프레스 편집기 링크가 나타납니다.</li>
    </ul>

    <hr style='border-color: rgba(0,0,0,0.05); margin: 40px 0;'>

    <h3>Phase 2. 워드프레스 인간 검수 및 발행 (수익화 핵심)</h3>
    <p>AI가 작성한 글을 사람이 최종 검수하여 품질을 높이는 단계입니다. 이 과정이 있어야 검색 엔진에서 높은 점수를 받습니다.</p>
    <div class='capture-placeholder'>[캡처 필수: 워드프레스 글 편집기 화면 (상태: 임시글)]</div>
    
    <h4>1. 제목 및 본문 가독성 체크</h4>
    <ul>
        <li>제목에 타겟 키워드가 자연스럽게 녹아있는지 확인합니다.</li>
        <li>문단 사이의 간격이 적절한지, 핵심 문구에 <b>굵게(Bold)</b> 처리가 되었는지 훑어봅니다.</li>
    </ul>

    <h4>2. 이미지 및 멀티미디어 검수</h4>
    <ul>
        <li>AI가 생성한 이미지가 본문 내용과 결이 맞는지 확인합니다.</li>
        <li>이미지에 '대체 텍스트(Alt Text)'가 키워드 위주로 입력되었는지 확인합니다.</li>
    </ul>

    <h4>3. SEO 설정 및 최종 공개</h4>
    <div class='capture-placeholder'>[캡처 필수: 워드프레스 우측 설정바 - 카테고리, 태그, 발행 버튼]</div>
    <ul>
        <li><b>카테고리:</b> 해당 주제에 맞는 카테고리를 정확히 선택합니다.</li>
        <li><b>태그:</b> 관련 핵심 키워드 3~5개를 태그란에 입력합니다.</li>
        <li><b>공개 상태:</b> 모든 검수가 끝났다면 '임시글' 상태를 '공개'로 변경하고 <b>[발행]</b> 버튼을 누릅니다.</li>
    </ul>

    <hr style='border-color: rgba(0,0,0,0.05); margin: 40px 0;'>

    <h3>Phase 3. 사후 관리 및 인덱싱</h3>
    <ul>
        <li>발행된 글의 URL을 복사하여 <b>'네이버 서치어드바이저'</b>의 [웹 페이지 수집] 메뉴에 제출합니다.</li>
        <li>이 과정까지 마쳐야 네이버 검색 결과에 빠르게 반영됩니다.</li>
    </ul>
</div>
""", unsafe_allow_html=True)