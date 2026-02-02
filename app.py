# ============================================================
# 👑 PickMeMovie — Princess Edition (Ultra Royal v2)
# "공주 컨셉"을 더 진하게: 왕실 UI / 궁정 호칭 / 티아라 컬러 / 왕실 증서 / 의식(로딩) 연출
#
# ✅ 기능
# - 5문항(고풍 카피) + 라디오(가로)
# - 결과 보기 -> 장르 분석 -> TMDB 장르 인기 5편 -> 3열 카드 + expander 상세
# - 포스터/제목/평점 표시
# - "누구랑 보면 좋은지" + "왕실 추천 증서" + "궁정 팁" 추가
# - Sidebar: API Key + 컨셉 커스터마이즈(호칭/티아라 컬러/연출 토글)
#
# 실행: streamlit run app.py
# ============================================================

import time
import requests
from typing import Dict, List, Tuple, Optional

import streamlit as st

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="PickMeMovie — Princess Edition",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# TMDB 설정
# -----------------------------
TMDB_DISCOVER_URL = "https://api.themoviedb.org/3/discover/movie"
TMDB_POSTER_BASE = "https://image.tmdb.org/t/p/w500"

GENRE_IDS = {
    "액션": 28,
    "코미디": 35,
    "드라마": 18,
    "SF": 878,
    "로맨스": 10749,
    "판타지": 14,
}

# -----------------------------
# Princess 질문(컨셉 강화)
# - 선택지는 기존 그대로(요구사항 호환)
# -----------------------------
QUESTIONS: List[Tuple[str, List[str], str]] = [
    (
        "Ⅰ. 주말이 허락된 날, 전하의 마음이 가장 끌리는 연회는?",
        ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
        "한 가지를 고르시면 ‘오늘의 무드’가 정해지옵니다.",
    ),
    (
        "Ⅱ. 근심이 스며들 때, 전하의 평정을 되찾는 ‘회복 의식’은?",
        ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
        "가장 편안해지는 선택이 정답이옵니다.",
    ),
    (
        "Ⅲ. 한 편의 영화가 ‘명작’이 되기 위한, 가장 귀한 보석은?",
        ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
        "전하가 중요하게 여기는 기준을 선택하옵소서.",
    ),
    (
        "Ⅳ. 여행길에 오른 전하의 여정, 가장 닮은 풍모는?",
        ["계획적", "즉흥적", "액티비티", "힐링"],
        "여정의 스타일은 영화 취향과 닮아 있사옵니다.",
    ),
    (
        "Ⅴ. 벗들 사이에서 전하의 매력이 빛나는 포지션은?",
        ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
        "궁정에서는 역할이 곧 분위기이옵니다.",
    ),
]

# -----------------------------
# 선택지 -> 장르 매핑
# -----------------------------
OPTION_TO_GENRE: Dict[str, str] = {
    "집에서 휴식": "드라마",
    "친구와 놀기": "코미디",
    "새로운 곳 탐험": "액션",
    "혼자 취미생활": "판타지",
    "혼자 있기": "드라마",
    "수다 떨기": "로맨스",
    "운동하기": "액션",
    "맛있는 거 먹기": "코미디",
    "감동 스토리": "드라마",
    "시각적 영상미": "판타지",
    "깊은 메시지": "SF",
    "웃는 재미": "코미디",
    "계획적": "드라마",
    "즉흥적": "로맨스",
    "액티비티": "액션",
    "힐링": "로맨스",
    "듣는 역할": "드라마",
    "주도하기": "액션",
    "분위기 메이커": "코미디",
    "필요할 때 나타남": "SF",
}

# -----------------------------
# 장르별 “누구랑 보면 좋을까” (공주톤)
# -----------------------------
WATCH_WITH: Dict[str, str] = {
    "드라마": "감정선을 함께 음미할 **가까운 벗** 혹은 **조용히 곁을 내어줄 사람**과 함께하시면 좋사옵니다.",
    "로맨스": "설렘을 나눌 **연인/썸**과 함께하면 황홀하옵니다. (홀로 보시면 감성의 왕관을 쓰게 되실지도!)",
    "코미디": "웃음은 연회처럼 함께할수록 성대해집니다. **친구들/동아리/과 동기**와 함께하소서!",
    "액션": "심장 뛰는 장면에 함께 환호할 **열정의 동료**(액션 러버 친구/형제자매)와 보시길 권하옵니다.",
    "SF": "설정·떡밥을 해석하며 담소 나눌 **덕질 동무** 혹은 **토론을 즐기는 벗**과 찰떡이옵니다.",
    "판타지": "세계관에 진심인 **취향이 닮은 벗**과 좋고, 분위기를 타고 싶다면 **혼영**도 귀하옵니다.",
}

# -----------------------------
# 참고/영감
# -----------------------------
INSPIRATIONS = [
    ("넷플릭스(Netflix)", "개인화 추천 경험"),
    ("왓챠(Watcha)", "평가 기반 취향 분석"),
    ("IMDb", "평점/리뷰 중심 탐색"),
]

# -----------------------------
# Helpers
# -----------------------------
def _safe_float(x) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def analyze_answers(answers: List[str]) -> Tuple[str, Dict[str, int], str]:
    scores = {g: 0 for g in GENRE_IDS.keys()}
    picked_by_genre = {g: [] for g in GENRE_IDS.keys()}

    for ans in answers:
        g = OPTION_TO_GENRE.get(ans)
        if g:
            scores[g] += 1
            picked_by_genre[g].append(ans)

    # 동점 처리 우선순위(원하는 성향대로 조정 가능)
    priority = ["드라마", "로맨스", "코미디", "액션", "SF", "판타지"]
    top_score = max(scores.values()) if scores else 0
    candidates = [g for g, s in scores.items() if s == top_score] or ["드라마"]
    candidates.sort(key=lambda x: priority.index(x) if x in priority else 999)
    top_genre = candidates[0]

    examples = picked_by_genre[top_genre][:2]
    if examples:
        reason = f"전하의 선택(예: {', '.join(examples)})은 **{top_genre}**의 정취를 가장 강하게 띠옵니다."
    else:
        reason = f"문답의 전체 결을 살피건대, **{top_genre}**가 전하께 가장 어울리옵니다."

    return top_genre, scores, reason


@st.cache_data(show_spinner=False, ttl=600)
def fetch_movies(api_key: str, genre_id: int) -> List[dict]:
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "page": 1,
    }
    r = requests.get(TMDB_DISCOVER_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("results", [])


def genre_blurb(genre: str) -> str:
    blurbs = {
        "드라마": "촛불처럼 은은한 서사와 감정의 레이스가 마음을 감쌉니다.",
        "로맨스": "장미 향처럼 번지는 설렘—마음이 먼저 왕관을 씁니다.",
        "코미디": "연회장의 웃음처럼 유쾌한 순간이 근심을 덜어줍니다.",
        "액션": "검과 번개 같은 속도감—눈을 떼기 어렵사옵니다.",
        "SF": "별의 지도와 미지의 문—상상력은 왕실의 영토를 넘어섭니다.",
        "판타지": "마법과 전설의 왕국—현실의 경계를 우아히 넘나듭니다.",
    }
    return blurbs.get(genre, "전하께 어울리는 특별한 무드가 깃든 장르이옵니다.")


def build_reason(top_genre: str, user_reason: str) -> str:
    return f"{user_reason} 그러므로 지금 이 순간, **{top_genre}**의 향을 품은 인기작을 진상하옵니다."


def ritual_spinner(text: str, seconds: float = 1.1):
    """짧은 ‘의식’ 연출용(너무 길면 UX 안 좋으니 짧게)"""
    with st.spinner(text):
        time.sleep(seconds)


# -----------------------------
# Session State
# -----------------------------
if "ran" not in st.session_state:
    st.session_state.ran = False
if "result" not in st.session_state:
    st.session_state.result = None  # (top_genre, scores, reason, movies)
if "persona_name" not in st.session_state:
    st.session_state.persona_name = "전하"
if "tiara" not in st.session_state:
    st.session_state.tiara = "로즈골드"
if "fx" not in st.session_state:
    st.session_state.fx = True

# -----------------------------
# Ultra Royal CSS (공주 컨셉 더 강화)
# -----------------------------
def inject_css(tiara: str):
    # 티아라 컬러 프리셋
    tiara_map = {
        "로즈골드": ("rgba(255, 182, 193, 0.35)", "rgba(255, 215, 160, 0.40)", "rgba(120, 70, 95, 0.90)"),
        "샴페인골드": ("rgba(255, 240, 200, 0.45)", "rgba(255, 215, 120, 0.40)", "rgba(85, 55, 20, 0.92)"),
        "라일락": ("rgba(210, 190, 255, 0.35)", "rgba(255, 200, 230, 0.25)", "rgba(70, 40, 85, 0.92)"),
        "민트펄": ("rgba(170, 255, 230, 0.28)", "rgba(255, 230, 200, 0.25)", "rgba(30, 70, 65, 0.92)"),
    }
    g1, g2, ink = tiara_map.get(tiara, tiara_map["로즈골드"])

    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Playfair+Display:wght@600;700;800&display=swap');

.block-container {{
  padding-top: 2.3rem;
  padding-bottom: 3.5rem;
  max-width: 1450px;
}}

html, body, [class*="css"] {{
  font-family: "Playfair Display", ui-serif, Georgia, serif !important;
}}

[data-testid="stAppViewContainer"] {{
  background:
    radial-gradient(1200px 650px at 12% 10%, {g1}, transparent 58%),
    radial-gradient(1000px 650px at 90% 15%, {g2}, transparent 58%),
    radial-gradient(1200px 700px at 50% 95%, rgba(190, 170, 255, 0.14), transparent 52%),
    linear-gradient(180deg, rgba(255, 250, 245, 0.62), rgba(255, 245, 252, 0.42));
}}

section[data-testid="stSidebar"] > div {{
  background:
    radial-gradient(700px 520px at 12% 12%, rgba(255, 215, 120, 0.22), transparent 58%),
    linear-gradient(180deg, rgba(255,255,255,0.62), rgba(255,255,255,0.30));
  border-right: 1px solid rgba(120, 90, 20, 0.10);
}}

.pm-hero {{
  border-radius: 28px;
  padding: 1.5rem 1.75rem;
  background: linear-gradient(135deg, rgba(255,255,255,0.72), rgba(255,255,255,0.30));
  border: 1px solid rgba(140, 95, 30, 0.16);
  box-shadow: 0 26px 70px rgba(120, 50, 90, 0.18);
  position: relative;
  overflow: hidden;
}}

.pm-hero:before {{
  content: "";
  position: absolute;
  inset: -2px;
  background:
    radial-gradient(900px 280px at 10% eth, rgba(255, 219, 120, 0.30), transparent 62%),
    radial-gradient(900px 320px at 92% 18%, rgba(255, 190, 230, 0.26), transparent 65%),
    radial-gradient(1200px 400px at 50% 110%, rgba(190, 170, 255, 0.18), transparent 58%);
  opacity: 0.95;
  pointer-events: none;
}}

.pm-hero-inner {{ position: relative; z-index: 1; }}

.pm-badge {{
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  padding: .34rem .85rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.60);
  border: 1px solid rgba(140, 95, 30, 0.16);
  color: {ink};
  font-weight: 900;
  font-family: "Cinzel", "Playfair Display", serif !important;
}}

.pm-title {{
  margin: .75rem 0 0 0;
  font-size: 2.65rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: {ink};
  line-height: 1.16;
}}

.pm-sub {{
  margin: .45rem 0 0 0;
  color: rgba(0,0,0,0.55);
  font-size: 1.05rem;
}}

.pm-line {{
  height: 1px;
  margin: 1rem 0 .9rem 0;
  background: linear-gradient(90deg, transparent, rgba(140,95,30,0.32), transparent);
}}

.pm-section {{
  font-family: "Cinzel", "Playfair Display", serif !important;
  font-size: 1.38rem;
  font-weight: 900;
  color: {ink};
}}

.pm-caption {{
  color: rgba(0,0,0,0.55);
  font-size: 0.96rem;
}}

.pm-qcard {{
  border-radius: 22px;
  padding: 1.05rem 1.15rem;
  background: rgba(255,255,255,0.62);
  border: 1px solid rgba(140,95,30,0.14);
  box-shadow: 0 16px 46px rgba(120, 50, 90, 0.10);
}}

.pm-qtitle {{
  font-weight: 900;
  color: {ink};
  font-size: 1.06rem;
  margin-bottom: .6rem;
}}

.pm-qhint {{
  margin-top: .55rem;
  color: rgba(0,0,0,0.52);
  font-size: .92rem;
}}

div[role="radiogroup"] label {{
  background: rgba(255,255,255,0.66) !important;
  border: 1px solid rgba(140,95,30,0.14) !important;
  border-radius: 999px !important;
  padding: .14rem .55rem !important;
  margin: .18rem .22rem .18rem 0 !important;
}}
div[role="radiogroup"] label span {{
  color: rgba(0,0,0,0.66) !important;
  font-weight: 900 !important;
}}
div[role="radiogroup"] label:hover {{
  border-color: rgba(140,95,30,0.30) !important;
}}

.stButton > button {{
  border-radius: 999px !important;
  padding: .80rem 1.05rem !important;
  font-weight: 900 !important;
  border: 1px solid rgba(140,95,30,0.22) !important;
  background: linear-gradient(135deg, {g2}, {g1}) !important;
  color: {ink} !important;
  box-shadow: 0 14px 34px rgba(120, 50, 90, 0.14);
}}
.stButton > button:hover {{
  transform: translateY(-1px);
  filter: brightness(1.02);
}}

.pm-result {{
  border-radius: 28px;
  padding: 1.35rem 1.55rem;
  background:
    radial-gradient(1000px 320px at 14% 25%, rgba(255, 219, 120, 0.30), transparent 62%),
    radial-gradient(1000px 320px at 88% 25%, rgba(255, 190, 230, 0.26), transparent 62%),
    rgba(255,255,255,0.66);
  border: 1px solid rgba(140,95,30,0.18);
  box-shadow: 0 26px 70px rgba(120, 50, 90, 0.16);
}}
.pm-result-title {{
  margin: 0;
  font-size: 2.18rem;
  font-weight: 900;
  color: {ink};
}}
.pm-pill {{
  display: inline-flex;
  align-items: center;
  gap: .45rem;
  padding: .28rem .86rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.55);
  border: 1px solid rgba(140,95,30,0.18);
  font-weight: 900;
}}
.pm-result-sub {{
  margin-top: .45rem;
  color: rgba(0,0,0,0.55);
  font-size: 1.0rem;
}}

.pm-mcard {{
  border-radius: 22px;
  padding: .88rem .88rem .55rem .88rem;
  background: rgba(255,255,255,0.64);
  border: 1px solid rgba(140,95,30,0.14);
  box-shadow: 0 16px 46px rgba(120, 50, 90, 0.12);
  transition: transform 160ms ease, box-shadow 160ms ease, border 160ms ease;
}}
.pm-mcard:hover {{
  transform: translateY(-3px);
  border-color: rgba(140,95,30,0.28);
  box-shadow: 0 20px 54px rgba(120, 50, 90, 0.16);
}}
.pm-poster img {{
  border-radius: 18px !important;
  border: 1px solid rgba(140,95,30,0.12);
}}
.pm-mtitle {{
  font-weight: 900;
  color: {ink};
  font-size: 1.03rem;
  margin-top: .55rem;
  line-height: 1.25;
}}
.pm-mmeta {{
  color: rgba(0,0,0,0.55);
  font-size: .92rem;
  margin-top: .12rem;
}}

div[data-testid="stExpander"] details {{
  border-radius: 18px;
  border: 1px solid rgba(140,95,30,0.14);
  background: rgba(255,255,255,0.56);
}}

.pm-certificate {{
  border-radius: 24px;
  padding: 1.1rem 1.2rem;
  background: linear-gradient(135deg, rgba(255,255,255,0.70), rgba(255,255,255,0.38));
  border: 1px dashed rgba(140,95,30,0.26);
  box-shadow: 0 14px 40px rgba(120,50,90,0.10);
}}
.pm-cert-title {{
  font-family: "Cinzel", serif !important;
  font-weight: 900;
  font-size: 1.2rem;
  color: {ink};
  margin: 0 0 .35rem 0;
}}
.pm-cert-body {{
  color: rgba(0,0,0,0.58);
  font-size: .98rem;
  margin: 0;
}}
</style>
""",
        unsafe_allow_html=True,
    )


inject_css(st.session_state.tiara)

# ============================================================
# Sidebar (왕실 커스터마이즈)
# ============================================================
with st.sidebar:
    st.markdown("## 👑 왕실 서재 (Royal Cabinet)")
    st.markdown("<div class='pm-caption'>전하의 영화 추천을 위한 설정을 보관하옵니다.</div>", unsafe_allow_html=True)
    st.markdown("---")

    # 사용자 이름 / 호칭
    st.markdown("### 🪞 궁정 호칭")
    persona = st.text_input("이름(호칭)", value=st.session_state.persona_name, help="예: 이영준 전하, 공주님, 황태자 등")
    st.session_state.persona_name = persona.strip() if persona.strip() else "전하"

    # 티아라 컬러
    st.markdown("### 💎 티아라 색상")
    tiara = st.selectbox("원하시는 티아라를 고르시옵소서", ["로즈골드", "샴페인골드", "라일락", "민트펄"], index=["로즈골드","샴페인골드","라일락","민트펄"].index(st.session_state.tiara))
    if tiara != st.session_state.tiara:
        st.session_state.tiara = tiara
        st.rerun()

    # 연출 효과
    st.markdown("### ✨ 궁정 연출")
    st.session_state.fx = st.toggle("결과 발표 연출(반짝이)", value=st.session_state.fx)

    st.markdown("---")
    st.markdown("### 🔑 TMDB 비밀 열쇠")
    api_key = st.text_input("TMDB API Key", type="password", placeholder="여기에 TMDB API Key를 입력하옵소서")
    st.caption("열쇠는 저장되지 않으며, 현재 세션에서만 사용됩니다.")

    st.markdown("---")
    st.markdown("### 💡 참고/영감 (왕실 기록)")
    for name, why in INSPIRATIONS:
        st.markdown(f"- **{name}**: {why}")

# ============================================================
# Main Hero
# ============================================================
st.markdown(
    f"""
<div class="pm-hero">
  <div class="pm-hero-inner">
    <div class="pm-badge">👑 PickMeMovie · Princess Edition</div>
    <div class="pm-line"></div>
    <div class="pm-title">어서 오시옵소서, {st.session_state.persona_name} ✨</div>
    <div class="pm-sub">다섯 가지 문답으로 전하의 ‘지금’ 무드를 가늠하고, TMDB 인기작 중 어울리는 5편을 진상하옵니다.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")
st.markdown("<div class='pm-section'>📜 궁정 문답 (5문항)</div>", unsafe_allow_html=True)
st.markdown("<div class='pm-caption'>가장 마음이 가는 선택 하나를 고르시면 되옵니다.</div>", unsafe_allow_html=True)

# ============================================================
# Questions Layout (2열 배치 + 마지막은 전체폭)
# ============================================================
answers: List[str] = []

row1 = st.columns(2, gap="large")
row2 = st.columns(2, gap="large")
row3 = st.columns(1, gap="large")

placements = [row1[0], row1[1], row2[0], row2[1], row3[0]]

for i, (q, opts, hint) in enumerate(QUESTIONS, start=1):
    with placements[i - 1]:
        st.markdown("<div class='pm-qcard'>", unsafe_allow_html=True)
        st.markdown(f"<div class='pm-qtitle'>{q}</div>", unsafe_allow_html=True)

        choice = st.radio(
            label="",
            options=opts,
            key=f"q{i}",
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown(f"<div class='pm-qhint'>✨ {hint}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        answers.append(choice)

# ============================================================
# CTA Buttons
# ============================================================
st.write("")
c1, c2, c3 = st.columns([1.2, 1.2, 2.6], gap="large")
with c1:
    run_btn = st.button("👑 결과를 진상하라", type="primary", use_container_width=True)
with c2:
    if st.button("🔄 선택 초기화", use_container_width=True):
        for i in range(1, 6):
            if f"q{i}" in st.session_state:
                del st.session_state[f"q{i}"]
        st.session_state.ran = False
        st.session_state.result = None
        st.rerun()
with c3:
    st.markdown(
        "<div class='pm-caption'>Tip: 다음 단계에서 OpenAI를 붙이면 영화별 추천 이유를 ‘개인 취향 + 상황’으로 더 정교하게 만들 수 있사옵니다.</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# Result
# ============================================================
if run_btn:
    if not api_key.strip():
        st.error("왕실 서재(사이드바)에 TMDB 비밀 열쇠(API Key)를 먼저 입력하옵소서.")
        st.stop()

    # 의식(로딩 연출)
    ritual_spinner("👑 왕실 기록관이 전하의 취향을 판독 중이옵니다...", 0.75)
    top_genre, scores, user_reason = analyze_answers(answers)

    ritual_spinner("📜 TMDB 도서관에서 인기작을 수배하는 중이옵니다...", 0.55)
    genre_id = GENRE_IDS[top_genre]
    try:
        movies = fetch_movies(api_key.strip(), genre_id)
    except requests.HTTPError:
        st.error("TMDB 요청이 실패하였습니다. 열쇠(API Key)가 올바른지 확인하옵소서.")
        st.stop()
    except requests.RequestException:
        st.error("네트워크가 불안정하옵니다. 잠시 후 다시 시도하옵소서.")
        st.stop()

    st.session_state.ran = True
    st.session_state.result = (top_genre, scores, user_reason, movies)

# ============================================================
# Render Stored Result (새로고침해도 유지)
# ============================================================
if st.session_state.ran and st.session_state.result:
    top_genre, scores, user_reason, movies = st.session_state.result
    watch_with_text = WATCH_WITH.get(top_genre, "취향이 맞는 벗과 함께 보시면 더 즐거우리다.")
    blurb = genre_blurb(top_genre)

    if st.session_state.fx:
        # 공주 컨셉 연출: st.balloons는 귀엽지만 “왕실 발표” 느낌으로 사용
        st.balloons()

    st.write("")
    st.markdown(
        f"""
<div class="pm-result">
  <h2 class="pm-result-title">당신에게 딱인 장르는: <span class="pm-pill">👑 {top_genre}</span>!</h2>
  <div class="pm-result-sub">{blurb}</div>
  <div class="pm-result-sub" style="margin-top:.45rem;">{user_reason}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")
    left, right = st.columns([1.25, 1.85], gap="large")
    with left:
        st.success(f"👥 **누구랑 보면 좋을까요?**\n\n{watch_with_text}")
    with right:
        st.markdown(
            f"""
<div class="pm-certificate">
  <p class="pm-cert-title">🏰 왕실 추천 증서 (Royal Recommendation)</p>
  <p class="pm-cert-body">
    본 증서는 <b>{st.session_state.persona_name}</b>께서 오늘 선택하신 문답을 바탕으로,
    <b>{top_genre}</b> 장르의 정취가 가장 어울림을 인증하옵니다.
    아래 5편은 TMDB 인기 순으로 선별되었사옵니다.
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

    if not movies:
        st.warning("해당 장르의 영화가 조회되지 않았사옵니다. 다른 선택으로 다시 시도하옵소서.")
        st.stop()

    st.write("")
    st.markdown("<div class='pm-section'>🍿 왕실 추천 영화 5선</div>", unsafe_allow_html=True)
    st.markdown("<div class='pm-caption'>카드를 펼쳐 줄거리와 추천 이유를 확인하옵소서.</div>", unsafe_allow_html=True)
    st.write("")

    cols = st.columns(3, gap="large")
    top5 = movies[:5]

    for idx, m in enumerate(top5):
        title = m.get("title") or "제목 없음"
        rating = _safe_float(m.get("vote_average"))
        overview = m.get("overview") or "줄거리 정보가 없사옵니다."
        poster_path = m.get("poster_path")
        poster_url = f"{TMDB_POSTER_BASE}{poster_path}" if poster_path else None

        with cols[idx % 3]:
            st.markdown("<div class='pm-mcard'>", unsafe_allow_html=True)

            if poster_url:
                st.markdown("<div class='pm-poster'>", unsafe_allow_html=True)
                st.image(poster_url, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.caption("포스터가 없사옵니다.")

            st.markdown(f"<div class='pm-mtitle'>{title}</div>", unsafe_allow_html=True)
            if rating is not None:
                st.markdown(f"<div class='pm-mmeta'>⭐ 평점: <b>{rating:.1f}</b></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='pm-mmeta'>⭐ 평점: 정보 없음</div>", unsafe_allow_html=True)

            with st.expander("📜 상세 보기 (왕실 기록 열람)"):
                st.markdown("**줄거리**")
                st.write(overview)

                st.markdown("**이 영화를 추천하는 이유**")
                st.write(build_reason(top_genre, user_reason))

                st.markdown("**누구와 함께 보면 더 좋을까요?**")
                st.write(watch_with_text)

                st.markdown("**궁정 한 마디**")
                st.write(f"전하, 오늘은 **{top_genre}**의 무드로 마음의 왕관을 반짝이게 하시옵소서 ✨")

            st.markdown("</div>", unsafe_allow_html=True)

    # 점수표(원하면 숨김)
    with st.expander("🧾 (선택) 장르 점수표 열람"):
        st.json(scores)
