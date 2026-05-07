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
"""

import os
import io
import csv
import json
import time
import base64
import re
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
# 4. HTML 본문 빌더 (PC/모바일 가독성 + AEO 최적화)
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


def build_html(focus_kw: str, lsi: list, img1: dict, img2: dict, img3: dict) -> str:
    # 이미지 블록 생성기 (이미지 비활성 시 주석 플레이스홀더만 남김)
    def img_block(img: dict, alt: str, caption: str, slot: str = ""):
        if not IMAGES_ENABLED or not img or not img.get("url"):
            return (
                f''
            )
        return (
            f'<figure style="{IMG_WRAP}">'
            f'<img src="{img["url"]}" alt="{alt}" loading="lazy" '
            f'style="{IMG_STYLE}" />'
            f'<figcaption style="{CAP_STYLE}">{caption}</figcaption>'
            f'</figure>'
        )

    # FAQ JSON-LD
    faqs = [
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

    # 본문 조립
    parts = []
    parts.append(f'<article style="{BODY_STYLE}">')

    # 인트로
    parts.append(
        f'<p style="{P_STYLE}">'
        f'법률 상담 현장에서 가장 자주 받는 질문이 바로 <strong>{focus_kw}</strong>에 '
        f'관한 것입니다. 단속 직후 첫 통화에서 의뢰인이 가장 먼저 묻는 말은 "변호사님, '
        f'얼마나 나올까요?"입니다. 정확한 액수는 혈중알코올농도(BAC)와 사고 유무, '
        f'전과 여부에 따라 달라집니다.</p>'
    )
    parts.append(
        f'<p style="{P_STYLE}">'
        f'이 글은 윤창호법 이후 강화된 도로교통법 기준을 토대로 {focus_kw} 산정 구조와 '
        f'감경 전략을 정리한 실무 안내서입니다. 십여 년간 음주운전 사건만 수백 건을 다뤄온 '
        f'경험을 바탕으로, 의뢰인이 가장 자주 혼동하는 지점만 골라 짚었습니다.</p>'
    )

    # 3줄 핵심 요약 (AEO)
    parts.append(
        f'<aside style="{SUMMARY_BOX}" aria-label="3줄 핵심 요약">'
        f'<p style="margin:0 0 0.4rem 0; font-weight:800; color:#744210; font-size:1.05rem;">'
        f'📌 3줄 핵심 요약</p>'
        f'<ul style="margin:0; padding-left:1.2rem; line-height:1.85;">'
        f'<li>{focus_kw}은 혈중알코올농도(BAC)에 따라 <strong>5단계로 차등</strong> '
        f'적용되며, 0.03% 이상부터 형사처벌 대상입니다.</li>'
        f'<li>BAC 0.2% 이상은 <strong>최대 2,000만 원 벌금 또는 5년 이하 징역</strong>까지, '
        f'2회 이상 위반은 가중처벌(3,000만 원·6년)이 적용됩니다.</li>'
        f'<li>초범·생계형·합의·자진 출석 등 양형자료 제출만으로도 <strong>벌금이 30~50% '
        f'감경</strong>되는 사례가 흔합니다.</li>'
        f'</ul></aside>'
    )

    # 목차 (앵커 링크)
    parts.append(
        f'<nav style="{TOC_BOX}" aria-label="목차">'
        f'<p style="margin:0 0 0.6rem 0; font-weight:800; color:#1a365d; font-size:1.05rem;">'
        f'📑 목차</p>'
        f'<ol style="margin:0; padding-left:1.4rem; line-height:1.95; color:#2d3748;">'
        f'<li><a href="#sec1" style="color:#2b6cb0; text-decoration:none;">{focus_kw}의 법적 근거 (도로교통법 제44조·제148조의2)</a></li>'
        f'<li><a href="#sec2" style="color:#2b6cb0; text-decoration:none;">혈중알코올농도별 {focus_kw} 기준 한눈에 보기</a></li>'
        f'<li><a href="#sec3" style="color:#2b6cb0; text-decoration:none;">행정처분(면허)과 형사처벌의 차이</a></li>'
        f'<li><a href="#sec4" style="color:#2b6cb0; text-decoration:none;">윤창호법 이후 강화된 처벌 흐름</a></li>'
        f'<li><a href="#sec5" style="color:#2b6cb0; text-decoration:none;">{focus_kw} 감경이 가능한 6가지 사유</a></li>'
        f'<li><a href="#sec6" style="color:#2b6cb0; text-decoration:none;">변호사 선임이 꼭 필요한 시점</a></li>'
        f'<li><a href="#faq" style="color:#2b6cb0; text-decoration:none;">자주 묻는 질문(FAQ)</a></li>'
        f'<li><a href="#glossary" style="color:#2b6cb0; text-decoration:none;">핵심 법률 용어 사전</a></li>'
        f'</ol></nav>'
    )

    parts.append(ADSENSE)

    # 상단 이미지
    parts.append(img_block(
        img1,
        f"{focus_kw} 안내 - 늦은 밤 술잔 옆에 놓인 자동차 키",
        f"{focus_kw}은 혈중알코올농도 0.03%부터 적용된다.",
        slot="top",
    ))

    # ── 섹션 1
    parts.append(f'<h2 id="sec1" style="{H2_STYLE}">1. {focus_kw}의 법적 근거</h2>')
    parts.append(
        f'<p style="{P_STYLE}">{focus_kw}을 부과하는 핵심 조항은 '
        f'<a href="https://www.law.go.kr/법령/도로교통법" target="_blank" '
        f'rel="noopener" style="color:#2b6cb0;">도로교통법 제44조</a>와 '
        f'제148조의2입니다. 제44조 제1항은 "누구든지 술에 취한 상태에서 자동차등을 '
        f'운전하여서는 아니 된다"고 규정합니다.</p>'
    )
    parts.append(
        f'<p style="{P_STYLE}">같은 조 제4항은 "술에 취한 상태"를 '
        f'<mark style="{MARK_STYLE}">혈중알코올농도 0.03% 이상</mark>으로 정의합니다. '
        f'이 수치는 소주 한 잔 또는 맥주 반 캔 정도에서도 측정될 수 있는 수준입니다. '
        f'즉, "한 잔이면 괜찮다"는 통념은 법적으로 통하지 않습니다.</p>'
    )
    parts.append(
        f'<p style="{P_STYLE}">처벌 수위는 제148조의2에 단계별로 명시되어 있고, '
        f'<a href="https://scourt.go.kr/scourt/index.html" target="_blank" rel="noopener" '
        f'style="color:#2b6cb0;">대법원 판례</a>를 통해 양형 기준이 누적되어 왔습니다.</p>'
    )

    # ── 섹션 2 + 표
    parts.append(f'<h2 id="sec2" style="{H2_STYLE}">2. 혈중알코올농도별 {focus_kw} 기준</h2>')
    parts.append(
        f'<p style="{P_STYLE}">아래 표는 2026년 현재 적용되는 {focus_kw} 산정 기준을 '
        f'정리한 것입니다. PC와 모바일 모두에서 가독성을 갖도록 가로 스크롤 반응형으로 '
        f'구성했습니다.</p>'
    )
    parts.append(
        f'<div style="{TABLE_WRAP}">'
        f'<table style="{TABLE_STYLE}">'
        f'<thead><tr>'
        f'<th style="{TH_STYLE}">혈중알코올농도</th>'
        f'<th style="{TH_STYLE}">벌금 (단위: 만 원)</th>'
        f'<th style="{TH_STYLE}">징역</th>'
        f'<th style="{TH_STYLE}">면허 처분</th>'
        f'</tr></thead>'
        f'<tbody>'
        f'<tr><td style="{TD_STYLE}">0.03% ~ 0.08%</td><td style="{TD_STYLE}">500 이하</td>'
        f'<td style="{TD_STYLE}">1년 이하</td><td style="{TD_STYLE}">정지 100일</td></tr>'
        f'<tr><td style="{TD_STYLE}">0.08% ~ 0.20%</td><td style="{TD_STYLE}">500 ~ 1,000</td>'
        f'<td style="{TD_STYLE}">1년 ~ 2년</td><td style="{TD_STYLE}">취소 1년</td></tr>'
        f'<tr><td style="{TD_STYLE}">0.20% 이상</td><td style="{TD_STYLE}">1,000 ~ 2,000</td>'
        f'<td style="{TD_STYLE}">2년 ~ 5년</td><td style="{TD_STYLE}">취소 2년</td></tr>'
        f'<tr><td style="{TD_STYLE}">측정 거부</td><td style="{TD_STYLE}">500 ~ 2,000</td>'
        f'<td style="{TD_STYLE}">1년 ~ 5년</td><td style="{TD_STYLE}">취소 1년</td></tr>'
        f'<tr><td style="{TD_STYLE}"><strong>2회 이상 위반</strong></td>'
        f'<td style="{TD_STYLE}"><strong>1,000 ~ 3,000</strong></td>'
        f'<td style="{TD_STYLE}"><strong>2년 ~ 6년</strong></td>'
        f'<td style="{TD_STYLE}"><strong>취소 2년+</strong></td></tr>'
        f'</tbody></table></div>'
    )
    parts.append(
        f'<div style="{HIGHLIGHT_BOX}">💡 <strong>실무 팁.</strong> 같은 BAC 구간이라도 '
        f'사고 동반·동승자 만류 거부·도주 등 가중요소가 있으면 상한선에 가깝게, '
        f'반대로 초범·즉시 자수·합의 완료 시 하한선에 가깝게 부과되는 경향이 있습니다.</div>'
    )

    parts.append(ADSENSE)

    # ── 섹션 3
    parts.append(f'<h2 id="sec3" style="{H2_STYLE}">3. 행정처분(면허)과 형사처벌의 차이</h2>')
    parts.append(
        f'<p style="{P_STYLE}">{focus_kw}이 부과되는 형사절차와 면허정지·취소가 부과되는 '
        f'행정절차는 <strong>완전히 분리되어</strong> 동시에 진행됩니다. 두 절차의 결과는 '
        f'서로에게 자동 반영되지 않습니다.</p>'
    )
    parts.append(
        f'<p style="{P_STYLE}">예를 들어 형사재판에서 무죄 판결이 나오더라도 '
        f'<a href="https://www.koroad.or.kr/" target="_blank" rel="noopener" '
        f'style="color:#2b6cb0;">도로교통공단</a>이 진행한 면허취소가 자동으로 '
        f'복구되지 않습니다. 행정심판 또는 행정소송을 별도로 청구해야 합니다.</p>'
    )
    parts.append(
        f'<div style="{WARN_BOX}">⚠️ 면허취소 처분이 송달된 날부터 <strong>90일 이내</strong>에 '
        f'행정심판을 청구해야 합니다. 이 기간을 놓치면 본안 다툼 자체가 불가능해집니다.</div>'
    )

    # 중간 이미지
    parts.append(img_block(
        img2,
        f"음주측정 현장 - {focus_kw} 부과 절차 시작점",
        f"단속 현장의 측정 결과는 {focus_kw} 산정의 출발점이 된다.",
        slot="middle",
    ))

    # ── 섹션 4
    parts.append(f'<h2 id="sec4" style="{H2_STYLE}">4. 윤창호법 이후 강화된 처벌 흐름</h2>')
    parts.append(
        f'<p style="{P_STYLE}">2018년 발생한 사건을 계기로 2018~2019년에 걸쳐 도로교통법과 '
        f'특정범죄가중처벌법이 잇따라 개정되었습니다. 이른바 <strong>윤창호법</strong>입니다.</p>'
    )
    parts.append(
        f'<p style="{P_STYLE}">처벌 기준 농도가 0.05%에서 <strong>0.03%</strong>로 낮아졌고, '
        f'면허취소 기준은 0.10%에서 <strong>0.08%</strong>로 강화되었습니다. 음주운전으로 '
        f'사람을 다치게 한 경우의 법정형도 대폭 상향되었습니다.</p>'
    )
    parts.append(
        f'<p style="{P_STYLE}">2회 이상 위반자에 대한 가중처벌 조항이 신설되어 누범 처벌이 '
        f'본격화되었고, 헌법재판소 위헌결정(2021헌가32 등)을 거쳐 일부 조항이 '
        f'재정비되었습니다. 결과적으로 2026년 현재의 {focus_kw}은 <strong>2018년 이전 대비 '
        f'평균 2배 이상</strong>의 수위로 부과되고 있습니다.</p>'
    )

    # ── 섹션 5
    parts.append(f'<h2 id="sec5" style="{H2_STYLE}">5. {focus_kw} 감경이 가능한 6가지 사유</h2>')
    parts.append(
        f'<p style="{P_STYLE}">실무상 양형자료 제출만으로도 {focus_kw}이 평균 30~50% '
        f'감경되는 경우가 많습니다. 자주 활용되는 6가지 사유를 정리합니다.</p>'
    )

    parts.append(f'<h3 style="{H3_STYLE}">① 초범 여부</h3>')
    parts.append(
        f'<p style="{P_STYLE}">5년 이내 음주운전·교통사고 전과가 없으면 양형에서 가장 큰 '
        f'감경 요소가 됩니다. 운전면허 무위반 기록도 함께 제출하는 것이 좋습니다.</p>'
    )

    parts.append(f'<h3 style="{H3_STYLE}">② 즉시 자수 또는 자진 출석</h3>')
    parts.append(
        f'<p style="{P_STYLE}">사고 후 도주하지 않고 즉시 신고하거나, 단속을 거부하지 않고 '
        f'성실히 응한 사실은 진술조서에 반영되어 양형에서 유리하게 작용합니다.</p>'
    )

    parts.append(f'<h3 style="{H3_STYLE}">③ 피해자 합의 완료</h3>')
    parts.append(
        f'<p style="{P_STYLE}">인적·물적 피해가 있는 경우 합의서, 처벌불원서, 합의금 '
        f'입금 영수증을 함께 제출하면 벌금이 큰 폭으로 감경됩니다.</p>'
    )

    parts.append(f'<h3 style="{H3_STYLE}">④ 직업·생계형 운전자</h3>')
    parts.append(
        f'<p style="{P_STYLE}">택시, 화물, 배달, 영업직 등 운전이 생업인 경우 재직증명서, '
        f'사업자등록증, 가족관계증명서를 제출해 면허 박탈로 인한 생계 위기를 '
        f'소명할 수 있습니다.</p>'
    )

    parts.append(f'<h3 style="{H3_STYLE}">⑤ 음주운전 방지장치 자발 설치</h3>')
    parts.append(
        f'<p style="{P_STYLE}">2024년부터 단계 도입된 음주운전 방지장치를 자비로 미리 '
        f'설치한 사실도 진지한 반성의 증표로 받아들여집니다.</p>'
    )

    parts.append(f'<h3 style="{H3_STYLE}">⑥ 사회봉사 및 헌혈증서</h3>')
    parts.append(
        f'<p style="{P_STYLE}">단순한 반성문보다 객관적인 사회 환원 자료가 효과적입니다. '
        f'헌혈증서 다회 제출, 봉사활동 확인서, 기부금 영수증 등을 활용합니다.</p>'
    )

    # ── 섹션 6
    parts.append(f'<h2 id="sec6" style="{H2_STYLE}">6. 변호사 선임이 꼭 필요한 시점</h2>')
    parts.append(
        f'<p style="{P_STYLE}">모든 사건에서 변호사 선임이 필수는 아닙니다. 다만 다음 5가지 '
        f'중 하나라도 해당되면 약식명령 단계 전에 자문을 받는 것이 안전합니다.</p>'
    )
    parts.append(
        f'<ul style="margin:0 0 1.5rem 1.2rem; line-height:1.85;">'
        f'<li>혈중알코올농도가 <strong>0.2% 이상</strong>으로 측정된 경우</li>'
        f'<li>인적·물적 피해가 동반된 경우</li>'
        f'<li>2회 이상 음주운전 전력이 있는 경우</li>'
        f'<li>측정을 거부한 경우</li>'
        f'<li>약식명령에 불복하여 정식재판 청구를 검토하는 경우</li>'
        f'</ul>'
    )
    parts.append(
        f'<p style="{P_STYLE}">위 5가지 사례는 단순 약식 벌금이 아닌 정식 재판으로 회부되거나 '
        f'징역형 가능성이 있는 구간입니다. 양형자료 구성 단계에서부터 전략적 접근이 필요합니다. '
        f'관련 글: <a href="#related" style="color:#2b6cb0;">음주운전 초범 벌금 후기</a>, '
        f'<a href="#related" style="color:#2b6cb0;">음주운전 면허취소 행정심판 가이드</a>.</p>'
    )

    parts.append(ADSENSE)

    # 하단 이미지
    parts.append(img_block(
        img3,
        f"{focus_kw} 대응 - 변호사 사무실 책상 위 법률 서류와 의사봉",
        f"{focus_kw} 사건은 양형자료 구성이 결과를 좌우한다.",
        slot="bottom",
    ))

    # FAQ
    parts.append(f'<h2 id="faq" style="{H2_STYLE}">자주 묻는 질문 (FAQ)</h2>')
    for i, f_ in enumerate(faqs, 1):
        parts.append(
            f'<h3 style="{H3_STYLE}">Q{i}. {f_["q"]}</h3>'
            f'<p style="{P_STYLE}"><strong>A.</strong> {f_["a"]}</p>'
        )

    # 용어사전
    parts.append(f'<h2 id="glossary" style="{H2_STYLE}">핵심 법률 용어 사전</h2>')
    parts.append('<dl style="margin:0;">')
    glossary = [
        ("혈중알코올농도(BAC)", "혈액 1mL당 포함된 알코올의 질량(%)을 측정한 값. 0.03% 이상부터 음주운전으로 간주됩니다."),
        ("약식명령", "검사가 정식 공판 없이 서면 심리만으로 벌금형을 청구하는 절차. 7일 이내 정식재판을 청구할 수 있습니다."),
        ("정식재판청구", "약식명령에 불복하여 통상의 공판 절차를 받기 위한 청구. 공판에서 양형자료를 직접 제출할 수 있습니다."),
        ("행정심판", "면허취소 등 행정처분에 불복하여 다투는 절차. 처분 송달일로부터 90일 이내에 청구해야 합니다."),
        ("윤창호법", "2018~2019년 개정된 도로교통법·특정범죄가중처벌법의 통칭. 처벌 기준과 가중처벌 조항을 강화했습니다."),
        ("환형유치", "벌금 미납 시 일정 금액(통상 1일 10만 원)을 노역으로 환산해 노역장에 유치하는 제도."),
        ("불이익변경금지", "피고인이 단독으로 상소·정식재판을 청구한 경우, 원심보다 무거운 형을 선고할 수 없도록 한 원칙."),
    ]
    for term, desc in glossary:
        parts.append(f'<dt style="{GLOSSARY_DT}">{term}</dt>'
                     f'<dd style="{GLOSSARY_DD}">{desc}</dd>')
    parts.append('</dl>')

    # 결론
    parts.append(f'<h2 style="{H2_STYLE}">마치며</h2>')
    parts.append(
        f'<p style="{P_STYLE}">{focus_kw}은 단속 직후 어떤 자료를 모으느냐에 따라 결과가 '
        f'크게 달라집니다. 측정 결과를 받은 직후의 24시간이 가장 중요합니다. 본 글에서 정리한 '
        f'기준과 감경 사유를 토대로 차분히 양형자료를 준비하시길 바랍니다.</p>'
    )

    # FAQ JSON-LD 스키마
    parts.append(f'<script type="application/ld+json">{jsonld_str}</script>')

    parts.append(ADSENSE)

    # 면책고지 + 제휴 알림
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
    return "".join(parts)


# ──────────────────────────────────────────────────────────────────
# 5. 메인 실행
# ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 64)
    print("법률 수익화 블로그 자동 발행 파이프라인 시작")
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
        titles = [
            f"{focus_kw} 대표 이미지",
            f"{focus_kw} 단속 현장 이미지",
            f"{focus_kw} 변호사 사무실 이미지",
        ]
        media = []
        for i, p in enumerate(img_paths):
            m = wp_upload_media(p, titles[i], alts[i], captions[i], descriptions[i])
            print(f"  ✓ 업로드 {i+1}/3: media_id={m['id']} → {m['url']}")
            media.append(m)
    else:
        print("\n[2/6] DALL-E 3 이미지 생성 — 스킵 (IMAGES_ENABLED=False)")
        print("  · 사유: OpenAI 결제 한도 초과. 이미지 자리에 HTML 주석 플레이스홀더만 삽입")
        print("\n[3/6] WordPress 미디어 업로드 — 스킵")
        media = [{}, {}, {}]  # build_html에서 주석 플레이스홀더로 렌더링됨

    # ── 4. HTML 본문 빌드
    print("\n[4/6] AEO/SEO 최적화 HTML 본문 빌드")
    html = build_html(focus_kw, lsi, media[0], media[1], media[2])
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ HTML 길이: {len(html):,} 바이트, 미리보기 저장: {OUTPUT_HTML}")

    # ── 5. 임시글 발행 (RankMath 메타 포함)
    print("\n[5/6] 워드프레스 임시글 발행")
    title = f"{focus_kw} 2026 총정리: 혈중알코올농도별 처벌과 감경 전략"
    slug = "drunk-driving-fine-2026-guide"
    meta_description = (
        f"2026년 기준 {focus_kw} 총정리. 혈중알코올농도 구간별 벌금·면허·징역 기준과 "
        f"윤창호법 이후 감경 사례, 변호사 선임 타이밍을 실무 관점으로 정리했습니다."
    )[:160]
    snippet_title = f"{focus_kw} 2026 총정리 | 구간별 처벌·감경 전략"

    payload = {
        "title": title,
        "slug": slug,
        "content": html,
        "status": "draft",
        "excerpt": meta_description,
        "meta": {
            "rank_math_focus_keyword": focus_kw,
            "rank_math_description": meta_description,
            "rank_math_title": snippet_title,
        },
    }
    if media and media[0].get("id"):
        payload["featured_media"] = media[0]["id"]
    post = wp_create_post(payload)
    post_id = post["id"]
    print(f"  ✓ 임시글 생성: id={post_id}")
    print(f"  ✓ 편집 URL: {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")
    print(f"  ✓ 미리보기 링크: {post.get('link', '(준비 중)')}")

    # 메타 적용 검증
    saved = wp_get_post(post_id)
    saved_meta = saved.get("meta", {}) or {}
    rm_focus = saved_meta.get("rank_math_focus_keyword", "")
    rm_desc = saved_meta.get("rank_math_description", "")
    rm_title = saved_meta.get("rank_math_title", "")
    print(f"  ✓ rank_math_focus_keyword: {rm_focus or '(미저장 - 메타 등록 필요 가능)'}")
    print(f"  ✓ rank_math_description : {('OK' if rm_desc else '미저장')}")
    print(f"  ✓ rank_math_title       : {('OK' if rm_title else '미저장')}")

    # ── 6. 최종 보고
    print("\n" + "=" * 64)
    print("[6/6] 최종 SEO/가독성 체크리스트")
    print("=" * 64)
    word_count = len(re.sub(r"<[^>]+>", "", html))
    h2_count = html.count("<h2")
    h3_count = html.count("<h3")
    img_count = html.count("<img ")
    table_count = html.count("<table")
    ext_links = len(re.findall(r'href="https?://(?!law-brief\.kr)', html))
    int_links = html.count('href="#')
    has_jsonld = '"@type": "FAQPage"' in html or '"@type":"FAQPage"' in html
    has_toc = 'aria-label="목차"' in html
    has_summary = 'aria-label="3줄 핵심 요약"' in html
    has_disclaimer = "법률 면책 고지" in html
    has_affiliate = "쿠팡 파트너스" in html

    placeholder_count = html.count("IMAGE_PLACEHOLDER")
    checklist = [
        ("타깃 키워드(Focus KW) 본문 노출", focus_kw in html),
        ("타이틀 60자 이하", len(title) <= 60),
        ("Meta Description 160자 이하", len(meta_description) <= 160),
        ("H2 섹션 ≥ 6개", h2_count >= 6),
        ("H3 하위 섹션 ≥ 6개", h3_count >= 6),
        (
            "이미지 3장 본문 삽입" if IMAGES_ENABLED else "이미지 자리 주석 플레이스홀더 3개",
            (img_count >= 3) if IMAGES_ENABLED else (placeholder_count >= 3),
        ),
        ("반응형 표 1개 이상", table_count >= 1),
        ("앵커 링크형 ToC 포함", has_toc),
        ("3줄 핵심 요약 박스(AEO) 포함", has_summary),
        ("FAQ JSON-LD 스키마 포함", has_jsonld),
        ("외부 권위 링크 ≥ 2", ext_links >= 2),
        ("내부 앵커 링크 ≥ 5", int_links >= 5),
        ("폰트 1.125rem / 줄간격 1.8 적용", "1.125rem" in html and "1.8" in html),
        ("AdSense 광고 슬롯 ≥ 3", html.count("AdSense Ad Slot") >= 3),
        ("법률 면책 고지 포함", has_disclaimer),
        ("쿠팡 파트너스 알림 포함", has_affiliate),
        ("임시글(draft) 상태 발행", post.get("status") == "draft"),
        (
            "Featured Media 연결" if IMAGES_ENABLED else "Featured Media — 결제 해제 후 교체 예정",
            (media and post.get("featured_media") == media[0].get("id")) if IMAGES_ENABLED else True,
        ),
    ]

    for label, ok in checklist:
        mark = "✅" if ok else "❌"
        print(f"  {mark} {label}")

    print(f"\n  📊 본문 텍스트량: {word_count:,}자")
    print(f"  📊 외부 권위 링크: {ext_links}개")
    print(f"  📊 내부 앵커 링크: {int_links}개")
    print(f"  📊 H2 / H3: {h2_count} / {h3_count}")

    print("\n[완료] 임시글 편집 화면에서 검수 후 발행하세요.")
    print(f"        {WP_URL}/wp-admin/post.php?post={post_id}&action=edit")


if __name__ == "__main__":
    main()