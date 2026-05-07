import os
import sys
import subprocess
import base64
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# [!] 업데이트 확인용 태그
BUILD_TAG = "V2.1-3H-STRATEGY-EDITION"

# 1. 인프라 및 경로 설정
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(PROJECT_DIR, "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.environ["IMG_DIR"] = IMAGE_FOLDER
CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
SNIPPET_PATH = os.path.join(PROJECT_DIR, "snippet_data.json")

if os.path.exists(os.path.join(PROJECT_DIR, ".env")):
    load_dotenv(os.path.join(PROJECT_DIR, ".env"))

if "factory_step" not in st.session_state:
    st.session_state.factory_step = 1

# 2. 페이지 세팅
st.set_page_config(page_title="워드프레스 공장", layout="wide", initial_sidebar_state="collapsed")

# 3. 🎨 프리미엄 UI 디자인
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

    /* 🍱 거대 1:1 정방향 사각형 — col1, col3 단일 버튼 */
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

    /* 3H 버튼 — col2 내부 작은 3분할 버튼 */
    .h3-button-wrap div[data-testid="stButton"] > button {{
        aspect-ratio: auto !important;
        min-height: 85px !important;
        font-size: clamp(14px, 1.5vw, 20px) !important;
        border-radius: 18px !important;
        margin-bottom: 10px !important;
    }}

    .active-engine div[data-testid="stButton"] > button {{
        animation: rippleAnim 2s infinite !important;
        border: 4px solid var(--rose) !important;
    }}

    /* 글 확인하기 버튼 */
    .link-button {{
        display: inline-block;
        background-color: var(--rose);
        color: white !important;
        padding: 20px 40px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 700;
        font-size: 20px;
        margin-top: 10px;
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

    /* 3H 타이틀 레이블 */
    .h3-label {{
        text-align: center;
        font-size: 13px;
        font-weight: 700;
        color: #8B7E6A;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}

    /* col2 포스팅 생성 컨테이너 — 높이 맞추기 */
    .posting-col-wrapper {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 280px;
        gap: 10px;
    }}
</style>
""", unsafe_allow_html=True)


# ── 스크립트 실행 헬퍼 (기존 유지 + --type 인자 지원) ──────────────────
def run_factory_script(filename, extra_args=None):
    script_path = os.path.join(PROJECT_DIR, filename)
    if not os.path.exists(script_path):
        st.error(f"🚨 '{filename}' 파일이 깃허브에 없습니다!")
        return -1
    try:
        cmd = [sys.executable, "-u", script_path]
        if extra_args:
            cmd.extend(extra_args)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=PROJECT_DIR,
            bufsize=1,
        )
        for line in proc.stdout:
            st.write(f"⚙️ {line.strip()}")
        proc.wait()
        return proc.returncode
    except Exception as e:
        st.error(f"❌ 오류: {str(e)}")
        return -1


# ── 메인 타이틀 ────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center; color:#1D1D1F; font-size:68px; font-weight:800; margin-bottom:80px;'>워드프레스 공장</h1>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="large")

# ── col1: 키워드 분석 ───────────────────────────────────────────────────
with col1:
    if st.session_state.factory_step == 1:
        st.markdown('<div class="active-engine">', unsafe_allow_html=True)
    if st.button("키워드 분석", key="btn1"):
        with st.status("🔍 분석 중...", expanded=True):
            if run_factory_script("keyword_research.py") == 0:
                st.session_state.factory_step = 2
                st.rerun()
    if st.session_state.factory_step == 1:
        st.markdown("</div>", unsafe_allow_html=True)

# ── col2: 포스팅 생성 (3H 분화) ────────────────────────────────────────
with col2:
    if st.session_state.factory_step == 2:
        st.markdown('<div class="active-engine">', unsafe_allow_html=True)

    st.markdown('<div class="h3-label">포스팅 생성 — 3H 전략 선택</div>', unsafe_allow_html=True)
    st.markdown('<div class="h3-button-wrap">', unsafe_allow_html=True)

    if st.button("🔥 Hero\n가십·이슈 트래픽", key="btn_hero"):
        with st.status("✍️ Hero 포스팅 작성 중...", expanded=True):
            if run_factory_script("wp_content_generator.py", ["--type", "hero"]) == 0:
                st.session_state.factory_step = 3
                st.rerun()

    if st.button("📚 Hub\n전문성·공유 브랜딩", key="btn_hub"):
        with st.status("✍️ Hub 포스팅 작성 중...", expanded=True):
            if run_factory_script("wp_content_generator.py", ["--type", "hub"]) == 0:
                st.session_state.factory_step = 3
                st.rerun()

    if st.button("💡 Help\n실전 해결·여온 브랜딩", key="btn_help"):
        with st.status("✍️ Help 포스팅 작성 중...", expanded=True):
            if run_factory_script("wp_content_generator.py", ["--type", "help"]) == 0:
                st.session_state.factory_step = 3
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.factory_step == 2:
        st.markdown("</div>", unsafe_allow_html=True)

# ── col3: 데이터 분석 ───────────────────────────────────────────────────
with col3:
    if st.button("데이터 분석", key="btn3"):
        st.session_state.show_data = True

if st.session_state.get("show_data", False):
    st.divider()
    if os.path.exists(CSV_PATH):
        st.dataframe(pd.read_csv(CSV_PATH, encoding="utf-8-sig"), use_container_width=True)

# ── 진행 단계 표시 ──────────────────────────────────────────────────────
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

    # 💥 RankMath 스니펫 복사 박스 — snippet_data.json 자동 표출
    if os.path.exists(SNIPPET_PATH):
        with open(SNIPPET_PATH, "r", encoding="utf-8") as f:
            snippet_data = json.load(f)

        # 사용된 페르소나 타입에 따라 배지 색상 구분
        _type = snippet_data.get("content_type", "")
        _type_badge = {
            "hero": "🔥 Hero",
            "hub":  "📚 Hub",
            "help": "💡 Help",
        }.get(_type, _type.upper())

        st.markdown(f"""
        <div style="background-color: #F4F0E6; padding: 25px; border-radius: 15px;
                    border: 2px solid #A26769; margin-top: 40px; margin-bottom: 20px;">
            <h3 style="color: #A26769; margin-top: 0;">✨ RankMath 스니펫 복사 박스
                <span style="font-size:14px; background:#A26769; color:#fff;
                             padding:3px 10px; border-radius:20px; margin-left:8px;
                             vertical-align:middle;">{_type_badge}</span>
            </h3>
            <p style="color: #1D1D1F; font-size: 16px; margin-bottom: 0;">
                아래 생성된 내용을 복사해서 워드프레스 RankMath 스니펫 편집기에 그대로 붙여넣으세요!
            </p>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.text_input("📌 제목 (Title)", value=snippet_data.get("title", ""))
        with col_s2:
            st.text_input("🔗 퍼머링크 (Permalink)", value=snippet_data.get("permalink", ""))

        st.text_area("📝 설명 (Description)", value=snippet_data.get("description", ""), height=100)

    st.markdown(
        '<div style="text-align: center; margin-top: 40px;">'
        '<a href="https://law-brief.kr/wp-admin/" target="_blank" class="link-button">'
        "🚀 글 확인하기 (워드프레스 이동)</a></div>",
        unsafe_allow_html=True,
    )


# ── 이미지 헬퍼 ────────────────────────────────────────────────────────
def get_img_html(filename):
    img_path = os.path.join(PROJECT_DIR, filename)
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return (
            f'<img src="data:image/png;base64,{encoded}" '
            'style="width:100%; max-width:800px; border-radius:12px; '
            'margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">'
        )
    return ""


# ── 검수 가이드 HTML ────────────────────────────────────────────────────
guide_html = f"""<div style="background-color: #FFFFFF; border-radius: 40px; padding: 80px; margin-top: 50px;
    border: 1px solid rgba(162, 103, 105, 0.15); box-shadow: 0 15px 40px rgba(0,0,0,0.03); color: #1D1D1F;">
<h1 style="text-align:center; color:#A26769; margin-bottom:60px;">워드프레스 검수 가이드</h1>

<!-- ───────────────────────────────── 3H 전략 가이드 (신규) ─────────────────────────────────── -->
<h2 style="color:#1D1D1F; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">0. 성공적인 블로그 운영을 위한 3H 발행 비율</h2>
<p style="font-size: 18px; line-height: 1.8;">
  구글이 사랑하는 '콘텐츠 믹스 전략'을 3H(Hero · Hub · Help)로 실천하세요.<br>
  세 가지 유형을 적절한 비율로 섞어 발행하면 검색 유입 + 브랜딩 + 재방문 삼박자가 완성됩니다.
</p>

<div style="display:flex; gap:20px; margin:30px 0; flex-wrap:wrap;">

  <!-- Help -->
  <div style="flex:1; min-width:220px; background:linear-gradient(135deg,#e8f5e9,#f1f8e9);
              border-radius:20px; padding:28px; border-left:6px solid #66bb6a;">
    <div style="font-size:36px; margin-bottom:10px;">💡</div>
    <h3 style="color:#2e7d32; margin:0 0 8px 0;">Help — 60%</h3>
    <p style="font-size:15px; line-height:1.7; color:#1B5E20; margin:0;">
      <b>매일 꾸준히</b> 발행하는 검색 유입의 핵심 콘텐츠.<br>
      실제 궁금증·문제를 해결해 주는 실용 정보 위주.<br>
      롱테일 키워드를 정조준해 자연 검색 트래픽을 쌓습니다.
    </p>
  </div>

  <!-- Hub -->
  <div style="flex:1; min-width:220px; background:linear-gradient(135deg,#e3f2fd,#e8eaf6);
              border-radius:20px; padding:28px; border-left:6px solid #42a5f5;">
    <div style="font-size:36px; margin-bottom:10px;">📚</div>
    <h3 style="color:#1565C0; margin:0 0 8px 0;">Hub — 30%</h3>
    <p style="font-size:15px; line-height:1.7; color:#0D47A1; margin:0;">
      <b>주 1~2회</b> 발행하는 특정 분야 전문성 강조 콘텐츠.<br>
      법률 상식·가이드 등 공유·저장하고 싶은 심화 글.<br>
      구독자 재방문과 브랜드 신뢰도를 끌어올립니다.
    </p>
  </div>

  <!-- Hero -->
  <div style="flex:1; min-width:220px; background:linear-gradient(135deg,#fff3e0,#fce4ec);
              border-radius:20px; padding:28px; border-left:6px solid #ef5350;">
    <div style="font-size:36px; margin-bottom:10px;">🔥</div>
    <h3 style="color:#B71C1C; margin:0 0 8px 0;">Hero — 10%</h3>
    <p style="font-size:15px; line-height:1.7; color:#7F0000; margin:0;">
      <b>월 1~2회</b> 발행하는 가십·이슈형 폭발적 트래픽 유발 콘텐츠.<br>
      시의성 높은 사건·판결·연예인 이슈 등과 법률을 연결.<br>
      SNS 확산 + 단기 대규모 유입으로 블로그를 알립니다.
    </p>
  </div>

</div>

<div style="background:#F4F0E6; border-radius:14px; padding:20px 28px; border-left:5px solid #A26769; margin-bottom:50px;">
  <b style="color:#A26769;">💡 사장님 TIP:</b>
  <span style="font-size:15px; color:#1D1D1F;">
    Help로 기반을 쌓고, Hub로 권위를 키우고, Hero로 폭발시킨다.
    이 순서를 지키면 구글 알고리즘과 독자 모두를 동시에 잡을 수 있습니다.
  </span>
</div>

<!-- ────────────────────────────── 기존 가이드 ──────────────────────────────── -->
<h2 style="color:#1D1D1F; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">1. 워드프레스 임시글 확인 및 진입</h2>
<p style="font-size: 18px; line-height: 1.8;">
포스팅 생성이 완료되면 워드프레스 관리자 페이지의 <b>[글] &gt; [모든 글]</b> 메뉴로 접속하세요. 목록에서 작성된 제목을 클릭하여 편집 화면으로 들어갑니다.
</p>
{get_img_html("step1.png")}

<h2 style="color:#1D1D1F; margin-top:60px; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">2. 과장님 검수 / RankMath SEO 설정 (중요)</h2>
<p style="font-size: 18px; line-height: 1.8;">
AI가 작성한 글을 사람이 최종적으로 다듬어 문맥상 이상한 부분이 없는지 체크하는 단계입니다.
</p>

<h3 style="color:#A26769; margin-top:30px;">1) 스니펫 편집</h3>
<p style="font-size: 16px; line-height: 1.8; background-color:#F4F0E6; padding: 20px; border-radius: 10px;">
<b>🎉 번거로운 제미나이 복사/붙여넣기 작업이 생략되었습니다!</b><br><br>
포스팅 생성이 완료되면 화면 상단에 <b>'RankMath 스니펫 복사 박스'</b>가 나타납니다.
어떤 3H 타입으로 생성했는지 배지로 표시되므로 확인 후, 그곳에 있는 내용(제목, 퍼머링크, 설명)을 복사해
워드프레스 우측 RankMath 스니펫 편집기에 붙여넣으시면 끝입니다!
</p>
{get_img_html("step2.png")}
{get_img_html("step2-1.png")}

<h3 style="color:#A26769; margin-top:30px;">2) 포커스 키워드</h3>
<p style="font-size: 18px;">제목 맨 첫번째 키워드를 삽입합니다.</p>
{get_img_html("step2-2.png")}

<h3 style="color:#A26769; margin-top:30px;">3) Rank Math 초록불 만들기</h3>
<p style="font-size: 18px;">기본 SEO, 추가, 제목 가독성, 콘텐츠 가독성이 모두 초록색 v 표시가 되도록 보완합니다.</p>
{get_img_html("step2-3.png")}
{get_img_html("step2-4.png")}

<h3 style="color:#A26769; margin-top:40px; background-color: #f8f9fa; padding: 30px; border-radius: 20px;">💡 4) 기타 경고 안내 (무시 가능)</h3>
<ul style="font-size: 16px; line-height: 1.8;">
<li><b>"Table of Contents plugin를 사용하지 않는 것 같습니다."</b><br>
<span style="color: #666;">우리 공장은 이미 구글이 좋아하는 '수제 HTML 목차'를 본문에 찍어내고 있습니다. RankMath가 특정 플러그인을 찾지 못해 띄우는 경고이니 무시하셔도 노출에는 100% 지장이 없습니다.</span>
</li>
<li><b>"Content AI를 사용하여 Post를 최적화하십시오."</b><br>
<span style="color: #666;">RankMath 회사의 유료 서비스 광고입니다. 가볍게 무시하세요.</span>
</li>
</ul>

<h2 style="color:#1D1D1F; margin-top:60px; border-bottom: 2px solid #FDF7F0; padding-bottom: 10px;">3. 공개일정 예약</h2>
<p style="font-size: 18px; line-height: 1.8;">
구글 애드센스 승인을 위해 20개 중 <b>하루에 10개는 즉시 업로드</b>하고, 나머지 10개는 <b>매일 오전 9시 발행</b>되도록 예약 걸어두세요.
</p>
{get_img_html("step3.png")}
{get_img_html("step3-1.png")}
{get_img_html("step3-2.png")}
{get_img_html("step4.png")}
</div>"""

st.markdown(guide_html, unsafe_allow_html=True)

st.markdown(
    f"<div style='text-align:center; color:#8B7E6A; margin-top:40px;'>{BUILD_TAG}</div>",
    unsafe_allow_html=True,
)