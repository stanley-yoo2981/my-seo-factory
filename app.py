"""
법률 수익화 블로그 자동화 — Streamlit 제어 대시보드
====================================================
keyword_research.py 와 wp_content_generator.py 를 버튼 한 번으로 실행하고,
subprocess stdout을 실시간으로 웹 화면에 스트리밍한다.

실행:
    streamlit run app.py
또는:
    python3 -m streamlit run app.py
"""

import os
import sys
import subprocess
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
KEYWORD_SCRIPT = os.path.join(PROJECT_DIR, "keyword_research.py")
PUBLISH_SCRIPT = os.path.join(PROJECT_DIR, "wp_content_generator.py")

st.set_page_config(
    page_title="법률 블로그 자동화 대시보드",
    page_icon="⚖️",
    layout="wide",
)

# ─────────────────────────────────────────────
# Sidebar: .env 연결 상태
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔌 연결 상태")

    naver_ok = bool(
        os.getenv("NAVER_AD_ACCESS_KEY") and os.getenv("NAVER_AD_SECRET_KEY")
        and os.getenv("NAVER_AD_CUSTOMER_ID")
    )
    openai_ok = bool(os.getenv("OPENAI_API_KEY"))
    wp_ok = bool(
        os.getenv("WP_URL") and os.getenv("WP_USERNAME") and os.getenv("WP_PASSWORD")
    )

    def status_line(label: str, ok: bool, hint: str = ""):
        icon = "🟢" if ok else "🔴"
        st.markdown(f"{icon} **{label}** {'· ' + hint if hint and ok else ''}")
        if not ok:
            st.caption(f"⚠️ `.env` 누락: {label}")

    status_line("네이버 검색광고 API", naver_ok,
                hint=f"customer={os.getenv('NAVER_AD_CUSTOMER_ID', '?')}")
    status_line("OpenAI API (DALL-E 3)", openai_ok)
    status_line("WordPress REST API", wp_ok,
                hint=os.getenv("WP_URL", ""))

    st.divider()
    st.markdown("## ⚙️ 옵션")
    images_enabled = st.checkbox(
        "🖼️ DALL-E 3 이미지 생성 (IMAGES_ENABLED)",
        value=False,
        help=(
            "OFF: HTML 자리에 주석 플레이스홀더만 삽입.\n"
            "ON: DALL-E 3 HD 호출 + 미디어 업로드 + featured_media 자동 연결.\n"
            "(인물 등장 시 한국인 강제 규칙 자동 적용)"
        ),
    )
    if images_enabled and not openai_ok:
        st.warning("OpenAI API 키가 없습니다.")

    st.divider()
    st.caption("📁 프로젝트")
    st.code(PROJECT_DIR, language="text")

# ─────────────────────────────────────────────
# 메인 헤더
# ─────────────────────────────────────────────
st.title("⚖️ 법률 수익화 블로그 자동화 대시보드")
st.caption("네이버 키워드 발굴 → SEO/AEO 본문 생성 → 워드프레스 임시글 발행")

# ─────────────────────────────────────────────
# 공통: subprocess 실시간 스트리밍 헬퍼
# ─────────────────────────────────────────────
def stream_subprocess(cmd: list, env_extra: dict, log_placeholder, max_lines: int = 1000):
    """subprocess를 띄우고 stdout 라인을 Streamlit placeholder에 실시간 출력."""
    env = {**os.environ, **env_extra, "PYTHONUNBUFFERED": "1"}
    buffer: list[str] = []
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=PROJECT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )
    except Exception as e:
        log_placeholder.error(f"subprocess 실행 실패: {e}")
        return -1, []

    assert proc.stdout is not None
    for line in proc.stdout:
        buffer.append(line.rstrip("\n"))
        log_placeholder.code("\n".join(buffer[-max_lines:]), language="text")
    proc.wait()
    return proc.returncode, buffer


# ─────────────────────────────────────────────
# 탭 구성
# ─────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔍 1. 키워드 분석",
    "✍️ 2. 포스팅 자동 실행",
    "📋 keywords.csv 미리보기",
])

# ====================== TAB 1 =========================
with tab1:
    st.subheader("네이버 검색광고 API → 연관 키워드 발굴")
    st.markdown(
        "- 시드 키워드: **음주운전, 명예훼손, 형사고소** "
        "(`keyword_research.py` 내부 설정)\n"
        "- PC + 모바일 합산 월 **1,500회 이상** 만 통과\n"
        "- 결과는 `keywords.csv` 로 저장됩니다."
    )

    if not naver_ok:
        st.error("네이버 API 키가 `.env`에 없습니다. 사이드바 상태를 확인하세요.")
    else:
        col1, col2 = st.columns([1, 4])
        run_kw = col1.button("🚀 키워드 분석 실행", type="primary", key="btn_kw")
        col2.caption("실행 결과는 아래 콘솔에 실시간 표시됩니다.")

        if run_kw:
            with st.status("키워드 분석 진행 중...", expanded=True) as status:
                log_box = st.empty()
                rc, _buf = stream_subprocess(
                    [sys.executable, "-u", KEYWORD_SCRIPT],
                    env_extra={},
                    log_placeholder=log_box,
                )
                if rc == 0:
                    status.update(label="✅ 키워드 분석 완료", state="complete")
                    st.toast("keywords.csv 갱신됨")
                else:
                    status.update(label=f"❌ 종료 코드 {rc}", state="error")

# ====================== TAB 2 =========================
with tab2:
    st.subheader("AEO/SEO 최적화 포스팅 자동 발행")
    st.markdown(
        "- `keywords.csv` → 수익성 가중 점수로 핵심 키워드 1개 자동 선정\n"
        "- 인라인 CSS HTML 본문 + ToC + 3줄 요약(AEO) + 표 + FAQ JSON-LD + 용어사전 생성\n"
        "- WordPress REST API로 **임시글(draft)** 업로드 + RankMath 메타 세팅"
    )

    mode_label = "🟢 DALL-E 3 ON (이미지 생성 + 업로드)" if images_enabled \
        else "⚪ 이미지 OFF (주석 플레이스홀더)"
    st.info(f"이미지 모드: **{mode_label}**  (사이드바 체크박스로 변경)")

    if not wp_ok:
        st.error("WordPress 자격증명이 `.env`에 없습니다.")
    elif not os.path.exists(CSV_PATH):
        st.warning("`keywords.csv` 가 아직 없습니다. 탭1에서 먼저 키워드 분석을 실행하세요.")
    else:
        col1, col2 = st.columns([1, 4])
        run_post = col1.button("📝 포스팅 자동 실행", type="primary", key="btn_post")
        col2.caption(
            "subprocess 환경변수로 IMAGES_ENABLED 가 주입됩니다."
        )

        if run_post:
            env_extra = {"IMAGES_ENABLED": "true" if images_enabled else "false"}
            with st.status("포스팅 자동 실행 중...", expanded=True) as status:
                log_box = st.empty()
                rc, buf = stream_subprocess(
                    [sys.executable, "-u", PUBLISH_SCRIPT],
                    env_extra=env_extra,
                    log_placeholder=log_box,
                )
                if rc == 0:
                    status.update(label="✅ 발행 완료", state="complete")
                    # 결과 라인에서 임시글 ID와 편집 URL 추출
                    edit_line = next(
                        (ln for ln in buf if "post.php?post=" in ln), None
                    )
                    if edit_line:
                        url = edit_line.split()[-1].strip()
                        st.success(f"✅ 워드프레스 임시글 편집 화면: {url}")
                else:
                    status.update(label=f"❌ 종료 코드 {rc}", state="error")

# ====================== TAB 3 =========================
with tab3:
    st.subheader("📋 keywords.csv 데이터프레임")
    if not os.path.exists(CSV_PATH):
        st.info("아직 keywords.csv 가 없습니다. 탭1에서 키워드 분석을 실행하세요.")
    else:
        df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("키워드 수", len(df))
        c2.metric("최대 월 검색량", f"{int(df['total_volume'].max()):,}")
        c3.metric("평균 월 검색량", f"{int(df['total_volume'].mean()):,}")
        c4.metric("시드 종류", df['seed'].nunique() if 'seed' in df.columns else 0)

        st.dataframe(df, use_container_width=True, height=520)

        st.download_button(
            "📥 keywords.csv 다운로드",
            data=df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name="keywords.csv",
            mime="text/csv",
        )

# 푸터
st.markdown("---")
st.caption("⚖️ 본 대시보드는 자동화 컨트롤 패널입니다. 발행 전 워드프레스 관리자에서 검수하세요.")
