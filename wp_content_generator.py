#!/usr/bin/env python3
"""
법률 수익화 블로그 - AEO/SEO 초최적화 콘텐츠 자동 발행 파이프라인
================================================================
1) keywords.csv → 수익성 가중 점수로 핵심 키워드 1개 선정
2) DALL-E 3 HD 이미지 3장 생성 (상/중/하 배치용)
3) PNG → WebP 변환 + 키워드 기반 파일명 저장
4) 인라인 CSS HTML 본문 빌드 (목차, 3줄 요약, 표, FAQ JSON-LD, 용어사전 등)
5) WordPress REST API로 미디어 업로드 + 임시글 발행
6) RankMath Focus Keyword / Meta Description / Snippet Title 자동 세팅
7) [신규] --type 인자(hero/hub/help)로 3H 페르소나 전략 자동 이식
   - hero  : 세상만사 관심 많은 프로 참견러 — 가십/이슈 트래픽 유입
   - hub   : 법 지식을 쉽게 풀어주는 공부방 블로거 — 상식/공유 브랜딩
   - help  : 경험 기반의 든든한 해결사 — 실전 해결 + 여온 브랜딩 1회
"""

import os
import io
import csv
import json
import time
import base64
import re
import argparse
import sys
from datetime import datetime
import requests
from dotenv import load_dotenv
from PIL import Image

# ──────────────────────────────────────────────────────────────────
# 환경설정
# ──────────────────────────────────────────────────────────────────
# 🚨 [수정됨] 하드코딩된 맥북 경로를 지우고, 서버 환경에 맞게 현재 디렉토리를 자동 추적하도록 변경했습니다.
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD", "").replace(" ", "")

CSV_PATH = os.path.join(PROJECT_DIR, "keywords.csv")
IMG_DIR = os.path.join(PROJECT_DIR, "images")
OUTPUT_HTML = os.path.join(PROJECT_DIR, "post_preview.html")

# 이제 경로가 정확하므로 여기서 Permission Error가 발생하지 않습니다.
os.makedirs(IMG_DIR, exist_ok=True)

# ⚠ 이미지 생성 토글 — 환경변수 IMAGES_ENABLED로 런타임 제어 (Streamlit 토글에서 주입).
#   기본값 false: DALL-E 호출/미디어 업로드 스킵, HTML 자리에 주석 플레이스홀더만 삽입.
#   true 로 켜면 DALL-E 3 호출 + 미디어 업로드 + featured_media 연결까지 자동 진행.
IMAGES_ENABLED = os.getenv("IMAGES_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")


# ──────────────────────────────────────────────────────────────────
# 1. 키워드 선정 (수익성·검색의도 가중 스코어링)
# ──────────────────────────────────────────────────────────────────
GENERIC_BLACKLIST = {
    "교통사고", "변호사", "형법", "법무법인", "도로교통법", "형사소송법",
    "행정심판", "온라인행정심판", "탄원서", "12대중과실", "반의사불벌죄",
    "성범죄경력조회서", "기소유예", "법무법인순위", "인지", "스토킹",
    "배임", "집행유예",
}
COMMERCIAL_TOKENS = (
    "벌금", "처벌", "변호사", "구속", "초범", "재범",
    "면허", "합의", "감경", "약식", "취소", "수치",
)


def pick_keyword():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    scored = []
    for r in rows:
        kw = r["keyword"].strip()
        if kw in GENERIC_BLACKLIST or len(kw) < 4:
            continue
        vol = int(r["total_volume"])
        intent = 1.6 if any(t in kw for t in COMMERCIAL_TOKENS) else 1.0
        comp = {"높음": 0.85, "중간": 1.0, "낮음": 1.2}.get(r["competition"], 1.0)
        scored.append({
            "score": vol * intent * comp,
            "vol": vol,
            "intent": intent,
            "comp": r["competition"],
            "row": r,
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[0], scored[:5]


# ──────────────────────────────────────────────────────────────────
# 2. DALL-E 3 이미지 생성
# ──────────────────────────────────────────────────────────────────
def gen_dalle_image(prompt: str) -> bytes:
    print(f"  → DALL-E 3 호출 (프롬프트 {len(prompt)}자)…")
    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "quality": "hd",
            "response_format": "b64_json",
        },
        timeout=180,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"DALL-E 오류 {resp.status_code}: {resp.text[:300]}")
    return base64.b64decode(resp.json()["data"][0]["b64_json"])


def to_webp(png_bytes: bytes, out_path: str):
    img = Image.open(io.BytesIO(png_bytes))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(out_path, "WEBP", quality=85, method=6)


# ──────────────────────────────────────────────────────────────────
# 3. WordPress REST API 클라이언트
# ──────────────────────────────────────────────────────────────────
def wp_auth():
    return (WP_USERNAME, WP_PASSWORD)


def wp_upload_media(local_path: str, title: str, alt: str,
                    caption: str, description: str) -> dict:
    fname = os.path.basename(local_path)
    encoded = requests.utils.quote(fname)
    with open(local_path, "rb") as f:
        body = f.read()
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded}",
        "Content-Type": "image/webp",
    }
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media",
        headers=headers, data=body, auth=wp_auth(), timeout=240,
    )
    r.raise_for_status()
    j = r.json()
    media_id = j["id"]
    # 메타 업데이트 (alt/caption/description은 별도 PATCH)
    r2 = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
        json={
            "title": title,
            "alt_text": alt,
            "caption": caption,
            "description": description,
        },
        auth=wp_auth(), timeout=60,
    )
    r2.raise_for_status()
    return {"id": media_id, "url": j.get("source_url", ""), "slug": j.get("slug", "")}


def wp_create_post(payload: dict) -> dict:
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=payload, auth=wp_auth(), timeout=60,
    )
    r.raise_for_status()
    return r.json()


def wp_get_post(post_id: int) -> dict:
    r = requests.get(
        f"{WP_URL}/wp-json/wp/v2/posts/{post_id}?context=edit",
        auth=wp_auth(), timeout=30,
    )
    r.raise_for_status()
    return r.json()


# ──────────────────────────────────────────────────────────────────
# 4. HTML 본문 빌더 — 스타일 상수
# ──────────────────────────────────────────────────────────────────
BODY_STYLE = (
    "font-size:1.125rem; line-height:1.8; color:#222; "
    "font-family:'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif;"
)
P_STYLE = "margin:0 0 1.5rem 0;"
H2_STYLE = (
    "font-size:1.6rem; font-weight:800; margin:2.5rem 0 1rem 0; "
    "padding:0.6rem 0 0.6rem 1rem; border-left:6px solid #2b6cb0; color:#1a365d;"
)
H3_STYLE = (
    "font-size:1.25rem; font-weight:700; margin:2rem 0 0.8rem 0; color:#2c5282;"
)
IMG_WRAP = "margin:2rem 0; text-align:center;"
IMG_STYLE = (
    "width:100%; height:auto; max-width:880px; border-radius:12px; "
    "box-shadow:0 4px 18px rgba(0,0,0,0.08);"
)
CAP_STYLE = (
    "display:block; margin-top:0.6rem; font-size:0.95rem; "
    "color:#666; font-style:italic;"
)
SUMMARY_BOX = (
    "background:linear-gradient(135deg,#fff8e1 0%,#fff3cd 100%); "
    "border-left:6px solid #f6ad55; border-radius:10px; "
    "padding:1.4rem 1.6rem; margin:1.5rem 0 2rem 0; "
    "box-shadow:0 2px 10px rgba(246,173,85,0.12);"
)
TOC_BOX = (
    "background:#f7fafc; border:1px solid #e2e8f0; border-radius:10px; "
    "padding:1.2rem 1.6rem; margin:1.5rem 0;"
)
TABLE_WRAP = "overflow-x:auto; margin:1.8rem 0;"
TABLE_STYLE = (
    "width:100%; min-width:560px; border-collapse:collapse; "
    "font-size:1rem; background:#fff; border-radius:10px; overflow:hidden; "
    "box-shadow:0 2px 12px rgba(0,0,0,0.06);"
)
TH_STYLE = (
    "background:#2b6cb0; color:#fff; padding:12px 14px; "
    "text-align:left; font-weight:700;"
)
TD_STYLE = "padding:12px 14px; border-bottom:1px solid #edf2f7;"
HIGHLIGHT_BOX = (
    "background:#ebf8ff; border-left:5px solid #3182ce; "
    "padding:1rem 1.3rem; border-radius:8px; margin:1.5rem 0; "
    "color:#1a365d; font-weight:600;"
)
WARN_BOX = (
    "background:#fff5f5; border-left:5px solid #e53e3e; "
    "padding:1rem 1.3rem; border-radius:8px; margin:1.5rem 0; color:#742a2a;"
)
DISCLAIMER = (
    "background:#f1f1f1; color:#666; font-size:0.88rem; "
    "padding:1.2rem 1.4rem; border-radius:8px; margin-top:3rem; "
    "line-height:1.7;"
)
MARK_STYLE = "background:#fef08a; padding:0 4px; border-radius:3px;"
GLOSSARY_DT = "font-weight:700; color:#2b6cb0; margin-top:0.8rem;"
GLOSSARY_DD = "margin:0.3rem 0 0.6rem 0; color:#444;"
ADSENSE = ""


# ──────────────────────────────────────────────────────────────────
# 5. [신규] 3H 페르소나 프롬프트 빌더 + GPT-4o 콘텐츠 생성
# ──────────────────────────────────────────────────────────────────

def get_persona_prompt(content_type: str, focus_kw: str, lsi: list) -> str:
    """
    content_type(hero/hub/help)에 따라 GPT-4o 시스템 프롬프트를 생성합니다.
    반환값은 JSON 스키마를 포함한 전체 시스템 지침 문자열입니다.
    """
    lsi_str = ", ".join(lsi)

    # ── 공통 SEO/기술 규칙
    common = f"""당신은 한국 법률 블로그 전문 콘텐츠 작가입니다.
아래 키워드로 SEO 최적화된 블로그 포스트 내용을 JSON 형식으로 생성하세요.

[핵심 키워드] {focus_kw}
[LSI 키워드] {lsi_str}

[SEO 필수 규칙]
- title: 매력적이고 자연스러운 한국어 제목 (60자 이내, 핵심 키워드 포함)
- permalink: 핵심 의미를 담은 영문+하이픈 URL 슬러그 (예: drunk-driving-fine-2026)
- description: 공백 포함 160자 이내. 광고·홍보 냄새가 전혀 없어야 하고,
  검색자가 "이 글 읽어봐야겠다"고 느낄 만한 호기심·공감·실용성 중 하나를 자극하는 한국어 문장
- 본문 내 외부 링크에 rel="nofollow" 절대 사용 금지. rel="noopener"만 허용
- 핵심 키워드를 intro, H2, H3, 본문 곳곳에 자연스럽게 반복 삽입
- H2 섹션 최소 6개, H3 소제목 최소 6개
- FAQ 5개 이상, 용어사전 5개 이상
- 모든 출력 언어: 한국어 (permalink·외부 URL 제외)
"""

    # ── 페르소나별 말투 지침
    if content_type == "hero":
        persona = """
[페르소나] 🔥 세상만사 관심 많은 프로 참견러
[콘텐츠 방향] 최근 뉴스나 주변에서 실제로 있었을 법한 사례(아파트 화재 보상, 유명인 법적 분쟁,
SNS에서 화제가 된 사건 등)의 법적 쟁점을 가십처럼 풀어내는 글.

[말투 규칙 — 반드시 지킬 것]
- 도입부는 반드시 "다들 이 뉴스 보셨어요?", "저 이거 보고 진짜 충격받았거든요.",
  "이게 남 일이 아니더라고요." 같은 구어체로 시작할 것
- 독자를 끌어당기는 호기심 유발형 표현을 섹션 도입마다 하나씩 배치
- 법률 전문가·법률 기관처럼 읽히는 표현 절대 금지
- 딱딱한 법률 문체, 기계 번역투 완전 배제
- 이웃과 카카오톡 대화하듯 자연스러운 단어 선택

[절대 금지]
- '여온', '법무법인 여온', '여온 법무법인' 언급 0회 (제목·본문·마치며 전 구간)
- 특정 법률 사무소·법무법인 이름 일체 금지
- 광고·홍보 느낌을 주는 CTA 문구 금지 ("지금 바로 상담하세요" 등)
"""
    elif content_type == "hub":
        persona = """
[페르소나] 📚 법 지식을 쉽게 풀어주는 공부방 블로거
[콘텐츠 방향] 일상에서 꼭 알아야 할 법률 상식과 절차를 직접 공부해서 정리한 것처럼 쓰는 글.
표, 비교 정리, 단계별 설명 등 지식 공유 포맷을 적극 활용.

[말투 규칙 — 반드시 지킬 것]
- 도입부는 "저도 이게 궁금해서 직접 찾아봤는데요,", "알고 나면 진짜 든든한 내용이에요.",
  "사실 저도 몰랐거든요, 직접 공부하고 나서야 알았어요." 같은 표현으로 시작
- 어려운 법률 용어는 반드시 쉬운 말로 풀어서 설명
- "꿀팁", "정리해봤어요", "이게 포인트더라고요" 같은 지식 나눔 커뮤니티 감성 유지
- 순수한 개인 공부 블로거처럼 읽혀야 함

[절대 금지]
- '여온', '법무법인 여온', '여온 법무법인' 언급 0회 (제목·본문·마치며 전 구간)
- "여온에서 배웠다", "여온 자료를 참고했다" 등 여온 간접 언급도 완전 금지
- 특정 법률 사무소·법무법인 이름 일체 금지
- 상업적 광고 느낌의 표현 전면 금지
"""
    else:  # help
        persona = """
[페르소나] 💡 경험 기반의 든든한 해결사
[콘텐츠 방향] 벌금·처벌·행정처분 같은 실제 고민을 직접 겪고 해결한 경험을 나누는 글.
구체적인 해결 절차, 체크리스트, 실전 팁을 중심으로 친절하고 따뜻하게 작성.

[말투 규칙 — 반드시 지킬 것]
- 도입부는 "저도 이런 상황에서 정말 막막했거든요,", "솔직히 처음엔 어떻게 해야 할지 몰라서
  많이 헤맸어요.", "실제로 해결해 보니까 이게 가장 중요하더라고요." 같은 표현으로 시작
- 독자의 불안과 막막함에 공감하는 표현을 섹션 곳곳에 배치
- 친한 선배가 후배에게 알려주는 것처럼 구체적이고 따뜻한 톤 유지
- 단계별 행동 지침, 실수하기 쉬운 포인트 강조

[브랜딩 규칙 — 정확히 지킬 것]
- 본문 마지막 '마치며' 섹션의 맨 끝 문단에 딱 1번만, 아래 문장을 자연스럽게 삽입:
  "참고로 이 부분은 저도 전문가의 조언이 필요해서 법무법인 여온 쪽 홈페이지를 참고했는데,
  설명이 꽤 잘 되어 있어서 도움을 많이 받았습니다."
- 해당 문장에서 '법무법인 여온'에 href="https://yeon-law.com" 링크를 달 것
  (rel="nofollow" 금지, rel="noopener"만 사용)
- 이 언급 외에 본문 어디서도 여온 이름 등장 금지
"""

    # ── JSON 스키마 명세
    schema = """
[출력 형식] 순수 JSON만 출력. 마크다운 코드블록(```json)이나 다른 서술 텍스트 없이.

{
  "title": "string — 60자 이내 한국어 제목 (핵심 키워드 포함)",
  "permalink": "string — 영문+하이픈 슬러그 (예: keyword-complete-guide-2026)",
  "description": "string — 공백 포함 160자 이내, 클릭을 유도하는 한국어 문장",
  "intro_paragraphs": [
    "string — 첫 번째 도입 문단 (페르소나 말투로 자연스럽게 시작)",
    "string — 두 번째 도입 문단 (글의 목적과 독자 혜택 설명)"
  ],
  "summary_bullets": [
    "string — 핵심 요약 1 (수치·기준 포함)",
    "string — 핵심 요약 2 (가중처벌·예외 등 핵심 규칙)",
    "string — 핵심 요약 3 (실전 팁·행동 지침)"
  ],
  "toc_items": [
    {"id": "sec1", "label": "string"},
    {"id": "sec2", "label": "string"},
    {"id": "sec3", "label": "string"},
    {"id": "sec4", "label": "string"},
    {"id": "sec5", "label": "string"},
    {"id": "sec6", "label": "string"},
    {"id": "faq", "label": "자주 묻는 질문 (FAQ)"},
    {"id": "glossary", "label": "핵심 법률 용어 사전"}
  ],
  "sections": [
    {
      "id": "sec1",
      "h2": "string — 섹션 H2 제목",
      "paragraphs": ["string", "string"],
      "subsections": [
        {
          "h3": "string — 소제목",
          "paragraphs": ["string"]
        }
      ],
      "table": {
        "headers": ["string", "string"],
        "rows": [["string", "string"], ["string", "string"]]
      },
      "highlight": "string or null — 💡 강조 박스 내용",
      "warning": "string or null — ⚠️ 경고 박스 내용",
      "list_items": ["string"] 
    }
  ],
  "faqs": [
    {"q": "string — 질문", "a": "string — 상세 답변 (3~5문장)"}
  ],
  "glossary": [
    {"term": "string — 법률 용어", "definition": "string — 쉬운 말로 풀어쓴 설명"}
  ],
  "conclusion_paragraphs": [
    "string — 결론 첫 번째 문단",
    "string — 결론 두 번째 문단 (독자 행동 유도)"
  ],
  "closing_link_html": "string or null — help 타입에서만 여온 링크 포함 HTML 한 문장. 나머지 null"
}
"""
    return common + persona + schema


def generate_ai_content(focus_kw: str, lsi: list, content_type: str) -> dict:
    """
    GPT-4o를 호출하여 3H 페르소나 기반 구조화 콘텐츠를 생성합니다.
    반환값: 스키마에 맞는 dict (파싱 실패 시 RuntimeError)
    """
    print(f"  → GPT-4o 콘텐츠 생성 (type={content_type}, keyword='{focus_kw}')…")
    system_prompt = get_persona_prompt(content_type, focus_kw, lsi)
    user_message = (
        f"키워드 '{focus_kw}'로 위 지침에 따른 블로그 포스트 JSON을 생성하세요. "
        f"LSI 키워드({', '.join(lsi)})를 본문 전체에 자연스럽게 녹여내고, "
        f"실제 한국 독자가 읽었을 때 단 한 군데도 어색함이 없어야 합니다. "
        f"표는 최소 1개 이상 포함하고, 섹션별 내용을 충분히 풍부하게 작성하세요."
    )

    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o",
            "max_tokens": 4096,
            "temperature": 0.72,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        },
        timeout=180,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"GPT-4o 오류 {resp.status_code}: {resp.text[:300]}")

    raw = resp.json()["choices"][0]["message"]["content"]
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # 혹시라도 마크다운 코드블록이 붙어 올 경우 제거 후 재시도
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        data = json.loads(clean)

    preview_title = str(data.get("title", ""))[:40]
    print(f"  ✓ GPT-4o 생성 완료 — TITLE 미리보기: {preview_title}…")
    return data


# ──────────────────────────────────────────────────────────────────
# 6. HTML 본문 빌더 (PC/모바일 가독성 + AEO 최적화)
#    [수정됨] content_type 파라미터 추가.
#    반환값: (clean_html, title, permalink, description) 4-튜플
# ──────────────────────────────────────────────────────────────────
def build_html(
    focus_kw: str,
    lsi: list,
    img1: dict,
    img2: dict,
    img3: dict,
    content_type: str = "help",
) -> tuple:
    """
    AI 페르소나 콘텐츠 기반 HTML 빌더.
    반환값: (clean_html, title, permalink, description)
    - clean_html  : 인라인 CSS 포함 완성 HTML (rel="nofollow" 전량 제거됨)
    - title       : AI 생성 제목 (60자 이내)
    - permalink   : 영문+하이픈 URL 슬러그
    - description : 공백 포함 160자 이내 메타 설명
    """

    # ── AI 구조화 콘텐츠 생성
    ai = generate_ai_content(focus_kw, lsi, content_type)

    title       = (ai.get("title") or f"{focus_kw} 완벽 총정리").strip()[:60]
    permalink   = (ai.get("permalink") or re.sub(r"[^a-z0-9]+", "-", focus_kw.lower())).strip("-")
    description = (ai.get("description") or "").strip()[:160]

    # ── 이미지 블록 생성기 (기존 로직 완전 유지)
    def img_block(img: dict, alt: str, caption: str, slot: str = ""):
        if not IMAGES_ENABLED or not img or not img.get("url"):
            return f'<!-- IMAGE_PLACEHOLDER slot="{slot}" -->'
        return (
            f'<figure style="{IMG_WRAP}">'
            f'<img src="{img["url"]}" alt="{alt}" loading="lazy" '
            f'style="{IMG_STYLE}" />'
            f'<figcaption style="{CAP_STYLE}">{caption}</figcaption>'
            f'</figure>'
        )

    # ── FAQ: AI 생성 우선, 부족하면 하드코딩 fallback 보충
    ai_faqs = ai.get("faqs") or []
    fallback_faqs = [
        {
            "q": "음주운전 초범도 벌금이 부과되나요?",
            "a": "네. 도로교통법 제148조의2에 따라 초범이라도 혈중알코올농도가 0.03% "
                 "이상이면 형사처벌 대상입니다. 다만 양형자료를 충실히 제출하면 "
                 "법정 최소형에 가까운 약식 벌금으로 마무리되는 사례가 다수입니다.",
        },
        {
            "q": "음주운전 벌금을 미납하면 어떻게 되나요?",
            "a": "벌금 미납 시 환형유치(노역장 유치) 절차로 전환됩니다. 통상 1일당 "
                 "10만 원 내외로 환산되어 노역장에 유치되며, 분납·연납 신청은 "
                 "검찰 집행과에서 가능합니다.",
        },
        {
            "q": "약식명령에 불복해 정식재판을 청구하면 유리한가요?",
            "a": "정식재판은 양형자료 추가 제출과 진술의 기회를 보장합니다. 다만 "
                 "정식재판에서 형이 더 무거워지지 않는다는 '불이익변경금지 원칙'은 "
                 "피고인이 청구한 경우에만 적용된다는 점을 유의해야 합니다.",
        },
        {
            "q": "자수하면 음주운전 벌금이 감경되나요?",
            "a": "사고 후 자진 신고나 수사기관 출석은 양형에서 유리하게 작용할 수 "
                 "있습니다. 다만 단속 후 자수는 '진정한 자수'로 평가되지 않을 수 "
                 "있으므로 시점이 중요합니다.",
        },
        {
            "q": "음주운전 벌금과 면허취소는 동시에 진행되나요?",
            "a": "네. 행정처분(면허정지·취소)과 형사처벌(벌금형·징역형)은 별개의 "
                 "절차로 동시에 진행됩니다. 면허 처분에 다툼이 있다면 90일 이내 "
                 "행정심판을, 형사절차는 별도로 대응해야 합니다.",
        },
    ]
    faqs = ai_faqs if len(ai_faqs) >= 3 else fallback_faqs

    # ── FAQ JSON-LD 스키마 (AEO 핵심)
    faq_jsonld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]},
            }
            for f in faqs
        ],
    }
    jsonld_str = json.dumps(faq_jsonld, ensure_ascii=False)

    # ── 용어사전: AI 생성 우선, 부족하면 fallback
    ai_glossary = ai.get("glossary") or []
    fallback_glossary = [
        ("혈중알코올농도(BAC)", "혈액 1mL당 포함된 알코올의 질량(%)을 측정한 값. 0.03% 이상부터 음주운전으로 간주됩니다."),
        ("약식명령", "검사가 정식 공판 없이 서면 심리만으로 벌금형을 청구하는 절차. 7일 이내 정식재판을 청구할 수 있습니다."),
        ("정식재판청구", "약식명령에 불복하여 통상의 공판 절차를 받기 위한 청구. 공판에서 양형자료를 직접 제출할 수 있습니다."),
        ("행정심판", "면허취소 등 행정처분에 불복하여 다투는 절차. 처분 송달일로부터 90일 이내에 청구해야 합니다."),
        ("윤창호법", "2018~2019년 개정된 도로교통법·특정범죄가중처벌법의 통칭. 처벌 기준과 가중처벌 조항을 강화했습니다."),
        ("환형유치", "벌금 미납 시 일정 금액(통상 1일 10만 원)을 노역으로 환산해 노역장에 유치하는 제도."),
        ("불이익변경금지", "피고인이 단독으로 상소·정식재판을 청구한 경우, 원심보다 무거운 형을 선고할 수 없도록 한 원칙."),
    ]

    # ── 본문 조립 시작
    parts = []
    parts.append(f'<article style="{BODY_STYLE}">')

    # ── 인트로 문단 (AI 생성)
    for para in (ai.get("intro_paragraphs") or []):
        parts.append(f'<p style="{P_STYLE}">{para}</p>')

    # ── 3줄 핵심 요약 박스 (AEO)
    bullets = ai.get("summary_bullets") or []
    if bullets:
        bullet_li = "".join(f"<li>{b}</li>" for b in bullets)
        parts.append(
            f'<aside style="{SUMMARY_BOX}" aria-label="3줄 핵심 요약">'
            f'<p style="margin:0 0 0.4rem 0; font-weight:800; color:#744210; font-size:1.05rem;">'
            f'📌 3줄 핵심 요약</p>'
            f'<ul style="margin:0; padding-left:1.2rem; line-height:1.85;">'
            f'{bullet_li}'
            f'</ul></aside>'
        )

    # ── 목차 (ToC) — AI 생성 toc_items 활용
    toc_items = ai.get("toc_items") or []
    if toc_items:
        toc_li = "".join(
            f'<li><a href="#{item["id"]}" style="color:#2b6cb0; text-decoration:none;">{item["label"]}</a></li>'
            for item in toc_items
        )
        parts.append(
            f'<nav style="{TOC_BOX}" aria-label="목차">'
            f'<p style="margin:0 0 0.6rem 0; font-weight:800; color:#1a365d; font-size:1.05rem;">'
            f'📑 목차</p>'
            f'<ol style="margin:0; padding-left:1.4rem; line-height:1.95; color:#2d3748;">'
            f'{toc_li}'
            f'</ol></nav>'
        )

    parts.append(ADSENSE)

    # ── 상단 이미지 (섹션 시작 전)
    parts.append(img_block(
        img1,
        f"{focus_kw} 관련 대표 이미지",
        f"{focus_kw}의 핵심 기준과 처벌 구조를 한눈에 확인하세요.",
        slot="top",
    ))

    # ── 메인 섹션들 (AI 생성 sections 활용)
    sections = ai.get("sections") or []
    for sec_idx, sec in enumerate(sections):
        section_id = sec.get("id") or f"sec{sec_idx + 1}"
        h2_text    = sec.get("h2") or ""

        parts.append(f'<h2 id="{section_id}" style="{H2_STYLE}">{h2_text}</h2>')

        # 섹션 일반 문단
        for para in (sec.get("paragraphs") or []):
            parts.append(f'<p style="{P_STYLE}">{para}</p>')

        # 섹션 리스트 (있을 경우)
        list_items = sec.get("list_items") or []
        if list_items:
            li_html = "".join(f"<li>{item}</li>" for item in list_items)
            parts.append(
                f'<ul style="margin:0 0 1.5rem 1.2rem; line-height:1.85;">{li_html}</ul>'
            )

        # 강조 박스 (있을 경우)
        if sec.get("highlight"):
            parts.append(f'<div style="{HIGHLIGHT_BOX}">💡 <strong>실무 팁.</strong> {sec["highlight"]}</div>')

        # 경고 박스 (있을 경우)
        if sec.get("warning"):
            parts.append(f'<div style="{WARN_BOX}">⚠️ {sec["warning"]}</div>')

        # 표 (있을 경우)
        table_data = sec.get("table")
        if table_data and table_data.get("headers") and table_data.get("rows"):
            th_cells = "".join(f'<th style="{TH_STYLE}">{h}</th>' for h in table_data["headers"])
            td_rows  = "".join(
                "<tr>" + "".join(f'<td style="{TD_STYLE}">{cell}</td>' for cell in row) + "</tr>"
                for row in table_data["rows"]
            )
            parts.append(
                f'<div style="{TABLE_WRAP}">'
                f'<table style="{TABLE_STYLE}">'
                f'<thead><tr>{th_cells}</tr></thead>'
                f'<tbody>{td_rows}</tbody>'
                f'</table></div>'
            )

        # H3 소제목들
        for subsec in (sec.get("subsections") or []):
            h3_text = subsec.get("h3") or ""
            parts.append(f'<h3 style="{H3_STYLE}">{h3_text}</h3>')
            for para in (subsec.get("paragraphs") or []):
                parts.append(f'<p style="{P_STYLE}">{para}</p>')

        # 중간 이미지: 두 번째 섹션 직후 삽입
        if sec_idx == 1:
            parts.append(ADSENSE)
            parts.append(img_block(
                img2,
                f"{focus_kw} 단속 및 처리 절차 이미지",
                f"{focus_kw} 처리 절차의 시작점.",
                slot="middle",
            ))

        # 하단 이미지: 네 번째 섹션 직후 삽입
        if sec_idx == 3:
            parts.append(ADSENSE)
            parts.append(img_block(
                img3,
                f"{focus_kw} 대응 전략 이미지",
                f"{focus_kw} 사건은 초기 대응과 양형자료 구성이 결과를 좌우한다.",
                slot="bottom",
            ))

    # ── FAQ 섹션
    parts.append(f'<h2 id="faq" style="{H2_STYLE}">자주 묻는 질문 (FAQ)</h2>')
    for i, f_ in enumerate(faqs, 1):
        parts.append(
            f'<h3 style="{H3_STYLE}">Q{i}. {f_["q"]}</h3>'
            f'<p style="{P_STYLE}"><strong>A.</strong> {f_["a"]}</p>'
        )

    # ── 용어사전 섹션
    parts.append(f'<h2 id="glossary" style="{H2_STYLE}">핵심 법률 용어 사전</h2>')
    parts.append('<dl style="margin:0;">')
    if ai_glossary:
        for item in ai_glossary:
            term = item.get("term") or ""
            defn = item.get("definition") or ""
            parts.append(
                f'<dt style="{GLOSSARY_DT}">{term}</dt>'
                f'<dd style="{GLOSSARY_DD}">{defn}</dd>'
            )
    else:
        for term, desc in fallback_glossary:
            parts.append(
                f'<dt style="{GLOSSARY_DT}">{term}</dt>'
                f'<dd style="{GLOSSARY_DD}">{desc}</dd>'
            )
    parts.append('</dl>')

    # ── 마치며 (결론)
    parts.append(f'<h2 style="{H2_STYLE}">마치며</h2>')
    for para in (ai.get("conclusion_paragraphs") or []):
        parts.append(f'<p style="{P_STYLE}">{para}</p>')

    # ── [help 전용] 여온 브랜딩 링크 — 마치며 맨 끝에 딱 1번 자연스럽게 삽입
    if content_type == "help":
        closing_html = ai.get("closing_link_html")
        if closing_html:
            # AI가 직접 생성한 HTML 사용 (nofollow 제거는 후처리에서 일괄 처리)
            parts.append(f'<p style="{P_STYLE}">{closing_html}</p>')
        else:
            # AI가 closing_link_html을 생성하지 않은 경우 기본값 fallback
            parts.append(
                f'<p style="{P_STYLE}">참고로 이 부분은 저도 전문가의 조언이 필요해서 '
                f'<a href="https://yeon-law.com" target="_blank" rel="noopener" '
                f'style="color:#2b6cb0; font-weight:600;">법무법인 여온</a> 쪽 홈페이지를 '
                f'참고했는데, 설명이 꽤 잘 되어 있어서 도움을 많이 받았습니다.</p>'
            )

    # ── FAQ JSON-LD 스키마 (AEO 핵심 마크업)
    parts.append(f'<script type="application/ld+json">{jsonld_str}</script>')

    parts.append(ADSENSE)

    # ── 법률 면책 고지 + 쿠팡 파트너스 알림 (기존 텍스트 완전 유지)
    parts.append(
        f'<div style="{DISCLAIMER}">'
        f'<p style="margin:0 0 0.5rem 0;"><strong>법률 면책 고지.</strong> '
        f'본 글은 일반적인 정보 제공을 목적으로 한 안내이며, 개별 사안에 대한 법률 자문이 '
        f'아닙니다. 실제 사건은 사실관계와 증거에 따라 결과가 달라질 수 있으므로, 구체적인 '
        f'대응이 필요한 경우 반드시 변호사와 직접 상담하시기 바랍니다.</p>'
        f'<p style="margin:0;"><strong>수수료 제공 알림.</strong> '
        f'본 페이지에는 쿠팡 파트너스 등 제휴 마케팅을 통해 일정 수수료를 제공받을 수 있는 '
        f'링크가 포함될 수 있습니다.</p></div>'
    )

    parts.append('</article>')

    clean_html = "".join(parts)

    # ── RankMath SEO 최적화: 외부 링크의 rel="nofollow" 전량 제거
    clean_html = re.sub(r'\s*rel="nofollow"', '', clean_html)

    return clean_html, title, permalink, description


# ──────────────────────────────────────────────────────────────────
# 7. 메인 실행
# ──────────────────────────────────────────────────────────────────
def main():
    # ── [신규] CLI 인자 파싱 — --type으로 3H 페르소나 선택
    parser = argparse.ArgumentParser(
        description="법률 수익화 블로그 자동 발행 파이프라인 (3H 페르소나 전략 지원)"
    )
    parser.add_argument(
        "--type",
        dest="content_type",
        choices=["hero", "hub", "help"],
        default="help",
        help=(
            "콘텐츠 타입 선택:\n"
            "  hero — 🔥 가십/이슈 트래픽 유입 (여온 언급 0회)\n"
            "  hub  — 📚 법률 상식 공유 블로거 (여온 언급 0회)\n"
            "  help — 💡 실전 해결사 + 여온 브랜딩 1회 (기본값)"
        ),
    )
    args = parser.parse_args()
    content_type = args.content_type

    print("=" * 64)
    print(f"법률 수익화 블로그 자동 발행 파이프라인 시작 [type={content_type}]")
    print("=" * 64)

    # ── 1. 키워드 선정
    print("\n[1/6] 키워드 선정")
    top, top5 = pick_keyword()
    focus_kw = top["row"]["keyword"]
    vol = top["vol"]
    print(f"  ✓ 선정 키워드: '{focus_kw}' (월 {vol:,}회, 경쟁 {top['comp']})")
    print(f"  ✓ 후보 Top5:")
    for s in top5:
        print(f"    - {s['row']['keyword']:<18} 점수 {s['score']:>9.0f} (월 {s['vol']:,})")

    # LSI 키워드 (수동 큐레이션 + CSV 매칭)
    lsi = ["혈중알코올농도", "도로교통법", "윤창호법", "면허취소",
           "약식명령", "정식재판청구", "음주운전 방지장치"]
    print(f"  ✓ LSI 키워드: {', '.join(lsi)}")

    # ⚠ 필수 규칙: 향후 IMAGES_ENABLED=True 전환 시 모든 프롬프트에 자동 부착되는
    #    한국인 인물 강제 규칙. 결제 한도 해제 후에도 그대로 적용된다.
    KOREAN_RULE = (
        " IMPORTANT: If any person, hand, body part, or human silhouette appears in "
        "this image, they MUST be of Korean (East Asian) ethnicity — Korean facial "
        "features, Korean skin tone, black hair — regardless of gender or age. "
        "Do NOT depict Western, Caucasian, African, South Asian, or Southeast Asian "
        "people. Korean only."
    )

    def build_prompt(seed: str) -> str:
        return seed.strip() + KOREAN_RULE

    seed_prompts = [
        "Cinematic photo of car keys placed next to an empty soju bottle and a small "
        "Korean drinking glass on a dark wooden table at a Korean pojangmacha at night, "
        "blurred neon city lights of Seoul through the window in the background, "
        "shallow depth of field, moody amber lighting, photorealistic, editorial style, "
        "no text, no logos.",
        "Close-up photo of a Korean person's gloved hand holding a digital breathalyzer "
        "device under blue and red flashing Korean police car lights at night on a "
        "rainy Seoul street, dramatic cinematic lighting, photorealistic, no faces "
        "visible, no text, no logos.",
        "Modern Korean law office desk shot from above, neatly stacked legal documents, "
        "a wooden gavel, brass scales of justice, a fountain pen, and a cup of coffee, "
        "soft natural window light, warm earth tones, photorealistic editorial style, "
        "no text on documents, no logos.",
    ]

    if IMAGES_ENABLED:
        # ── 2. DALL-E 3 이미지 3장
        print("\n[2/6] DALL-E 3 이미지 생성 (HD, 1024x1024)")
        prompts = [build_prompt(s) for s in seed_prompts]
        img_paths = []
        for i, p in enumerate(prompts, 1):
            png = gen_dalle_image(p)
            out = os.path.join(IMG_DIR, f"음주운전벌금-{i}.webp")
            to_webp(png, out)
            size_kb = os.path.getsize(out) / 1024
            print(f"  ✓ 이미지 {i}/3 저장: {os.path.basename(out)} ({size_kb:.1f} KB)")
            img_paths.append(out)

        # ── 3. WordPress 미디어 업로드
        print("\n[3/6] WordPress 미디어 업로드")
        captions = [
            f"{focus_kw}은 혈중알코올농도 0.03%부터 적용된다.",
            f"단속 현장의 측정 결과는 {focus_kw} 산정의 출발점이 된다.",
            f"{focus_kw} 사건은 양형자료 구성이 결과를 좌우한다.",
        ]
        alts = [
            f"{focus_kw} 안내 - 늦은 밤 술잔 옆에 놓인 자동차 키",
            f"음주측정 현장 - {focus_kw} 부과 절차 시작점",
            f"{focus_kw} 대응 - 변호사 사무실 책상 위 법률 서류와 의사봉",
        ]
        descriptions = [
            f"{focus_kw}의 적용 기준과 사회적 경각심을 표현한 대표 이미지.",
            f"음주측정과 단속 절차를 통해 {focus_kw}이 산정되는 현장.",
            f"{focus_kw} 대응을 위한 양형자료와 법률 사무실 풍경.",
        ]
        titles_media = [
            f"{focus_kw} 대표 이미지",
            f"{focus_kw} 단속 현장 이미지",
            f"{focus_kw} 변호사 사무실 이미지",
        ]
        media = []
        for i, p in enumerate(img_paths):
            m = wp_upload_media(p, titles_media[i], alts[i], captions[i], descriptions[i])
            print(f"  ✓ 업로드 {i+1}/3: media_id={m['id']} → {m['url']}")
            media.append(m)
    else:
        print("\n[2/6] DALL-E 3 이미지 생성 — 스킵 (IMAGES_ENABLED=False)")
        print("  · 사유: OpenAI 결제 한도 초과. 이미지 자리에 HTML 주석 플레이스홀더만 삽입")
        print("\n[3/6] WordPress 미디어 업로드 — 스킵")
        media = [{}, {}, {}]  # build_html에서 주석 플레이스홀더로 렌더링됨

    # ── 4. HTML 본문 빌드 (AI 페르소나 콘텐츠 + 4-튜플 반환)
    print(f"\n[4/6] AEO/SEO 최적화 HTML 본문 빌드 (페르소나: {content_type})")
    html, title, permalink, description = build_html(
        focus_kw, lsi, media[0], media[1], media[2], content_type
    )
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ HTML 길이: {len(html):,} 바이트, 미리보기 저장: {OUTPUT_HTML}")
    print(f"  ✓ AI 생성 TITLE      : {title}")
    print(f"  ✓ AI 생성 PERMALINK  : {permalink}")
    print(f"  ✓ AI 생성 DESC       : {description[:80]}…")

    # ── 5. 임시글 발행 (RankMath 메타 포함)
    print("\n[5/6] 워드프레스 임시글 발행")
    # [수정됨] title, permalink, description 모두 build_html의 AI 생성값 사용
    slug             = permalink
    meta_description = description[:160]
    snippet_title    = title

    payload = {
        "title":   title,
        "slug":    slug,
        "content": html,
        "status":  "draft",
        "excerpt": meta_description,
        "meta": {
            "rank_math_focus_keyword": focus_kw,
            "rank_math_description":  meta_description,
            "rank_math_title":        snippet_title,
        },
    }
    if media and media[0].get("id"):
        payload["featured_media"] = media[0]["id"]
    post    = wp_create_post(payload)
    post_id = post["id"]
    print(f"  ✓ 임시글 생성: id={post_id}")
    print(f"  ✓ 편집 URL: {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")
    print(f"  ✓ 미리보기 링크: {post.get('link', '(준비 중)')}")

    # 메타 적용 검증
    saved      = wp_get_post(post_id)
    saved_meta = saved.get("meta", {}) or {}
    rm_focus   = saved_meta.get("rank_math_focus_keyword", "")
    rm_desc    = saved_meta.get("rank_math_description", "")
    rm_title   = saved_meta.get("rank_math_title", "")
    print(f"  ✓ rank_math_focus_keyword: {rm_focus or '(미저장 - 메타 등록 필요 가능)'}")
    print(f"  ✓ rank_math_description : {('OK' if rm_desc else '미저장')}")
    print(f"  ✓ rank_math_title       : {('OK' if rm_title else '미저장')}")

    # ── 6. 최종 보고
    print("\n" + "=" * 64)
    print("[6/6] 최종 SEO/가독성 체크리스트")
    print("=" * 64)
    word_count    = len(re.sub(r"<[^>]+>", "", html))
    h2_count      = html.count("<h2")
    h3_count      = html.count("<h3")
    img_count     = html.count("<img ")
    table_count   = html.count("<table")
    ext_links     = len(re.findall(r'href="https?://(?!law-brief\.kr)', html))
    int_links     = html.count('href="#')
    has_jsonld    = '"@type": "FAQPage"' in html or '"@type":"FAQPage"' in html
    has_toc       = 'aria-label="목차"' in html
    has_summary   = 'aria-label="3줄 핵심 요약"' in html
    has_disclaimer = "법률 면책 고지" in html
    has_affiliate  = "쿠팡 파트너스" in html

    placeholder_count = html.count("IMAGE_PLACEHOLDER")

    # [수정됨] title, meta_description은 이제 AI 생성값 기반
    checklist = [
        ("타깃 키워드(Focus KW) 본문 노출",          focus_kw in html),
        ("타이틀 60자 이하",                         len(title) <= 60),
        ("Meta Description 160자 이하",              len(meta_description) <= 160),
        ("H2 섹션 ≥ 6개",                            h2_count >= 6),
        ("H3 하위 섹션 ≥ 6개",                       h3_count >= 6),
        (
            "이미지 3장 본문 삽입" if IMAGES_ENABLED else "이미지 자리 주석 플레이스홀더 3개",
            (img_count >= 3) if IMAGES_ENABLED else (placeholder_count >= 3),
        ),
        ("반응형 표 1개 이상",                        table_count >= 1),
        ("앵커 링크형 ToC 포함",                      has_toc),
        ("3줄 핵심 요약 박스(AEO) 포함",              has_summary),
        ("FAQ JSON-LD 스키마 포함",                   has_jsonld),
        ("외부 권위 링크 ≥ 2",                        ext_links >= 2),
        ("내부 앵커 링크 ≥ 5",                        int_links >= 5),
        ("폰트 1.125rem / 줄간격 1.8 적용",           "1.125rem" in html and "1.8" in html),
        ("AdSense 광고 슬롯 ≥ 3",                     html.count("AdSense Ad Slot") >= 3),
        ("법률 면책 고지 포함",                        has_disclaimer),
        ("쿠팡 파트너스 알림 포함",                    has_affiliate),
        ("임시글(draft) 상태 발행",                    post.get("status") == "draft"),
        ("rel='nofollow' 완전 제거 확인",              'rel="nofollow"' not in html),
        (
            "Featured Media 연결" if IMAGES_ENABLED else "Featured Media — 결제 해제 후 교체 예정",
            (media and post.get("featured_media") == media[0].get("id")) if IMAGES_ENABLED else True,
        ),
        (
            "여온 브랜딩 1회 삽입 (help 전용)" if content_type == "help" else "여온 브랜딩 0회 확인",
            ("yeon-law.com" in html) if content_type == "help" else ("yeon-law.com" not in html),
        ),
    ]

    for label, ok in checklist:
        mark = "✅" if ok else "❌"
        print(f"  {mark} {label}")

    print(f"\n  📊 본문 텍스트량: {word_count:,}자")
    print(f"  📊 외부 권위 링크: {ext_links}개")
    print(f"  📊 내부 앵커 링크: {int_links}개")
    print(f"  📊 H2 / H3: {h2_count} / {h3_count}")

    # ── [수정됨] snippet_data.json 저장 — build_html 4-튜플 값을 그대로 사용
    import json as _json
    import os as _os

    # 생성된 스니펫 데이터를 스트림릿(app.py)으로 보내기 위해 파일로 저장합니다.
    current_dir = _os.path.dirname(_os.path.abspath(__file__))
    snippet_data = {
        "title":       title,          # AI 생성 제목 (build_html 반환값)
        "permalink":   permalink,      # AI 생성 슬러그 (build_html 반환값)
        "description": meta_description,  # AI 생성 메타 설명 (build_html 반환값)
        "content_type": content_type,  # 사용된 페르소나 타입 기록
    }
    snippet_path = _os.path.join(current_dir, "snippet_data.json")

    with open(snippet_path, "w", encoding="utf-8") as f:
        _json.dump(snippet_data, f, ensure_ascii=False, indent=2)

    print(f"\n  ✓ snippet_data.json 저장 완료: {snippet_path}")
    print("\n[완료] 임시글 편집 화면에서 검수 후 발행하세요.")
    print(f"        {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")


if __name__ == "__main__":
    main()