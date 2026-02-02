# ============================================================
# 👑 PickMeMovie — "Princess Edition"
# 고풍 + 왕실 + 공주님 무드로 처음부터 UI를 새로 설계한 Streamlit 앱
# - 질문 UI/카드 UI/결과 UI 전부 리디자인
# - TMDB 연동 (사이드바 API Key 입력)
# - 장르 분석 -> TMDB 인기 5편 -> 3열 카드 + expander 상세
# - "누구랑 보면 좋은지" 포함
#
# ※ 실행: streamlit run app.py
# ============================================================

import time
import requests
from typing import Dict, List, Tuple, Optional

import streamlit as st

# ============================================================
# 1) Page Config
# ============================================================

st.set_page_config(
    page_title="PickMeMovie — Princess Edition",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2) Constants / TMDB
# ============================================================

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

# ============================================================
# 3) Princess-style Questions (완전 새로 문구 설계)
#    - 선택지는 사용자가 준 4개를 유지하되
#      문장을 훨씬 고풍스럽게 “표현”만 바꿈
# ============================================================

QUESTIONS: List[Tuple[str, List[str]]] = [
    (
        "Ⅰ. 궁정의 여유로운 주말, 전하께서는 어떤 시간을 가장 탐하시나이까?",
        ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"],
    ),
    (
        "Ⅱ. 마음에 구름이 드리울 때, 전하의 평온을 되찾는 의식은 무엇이옵니까?",
        ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"],
    ),
    (
        "Ⅲ. 한 편의 영화가 ‘명작’으로 봉인되기 위한, 가장 중한 덕목은 무엇이라 여기시나이까?",
        ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"],
    ),
    (
        "Ⅳ. 왕실의 여행길, 전하의 여정은 어떤 풍모를 띠나이까?",
        ["계획적", "즉흥적", "액티비티", "힐링"],
    ),
    (
        "Ⅴ. 벗들 사이에서 전하의 위엄(혹은 매력)이 빛나는 자리란?",
        ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"],
    ),
]

# ============================================================
# 4) Answer -> Genre Mapping
# ============================================================

OPTION_TO_GENRE: Dict[str, str] = {
    # Q1
    "집에서 휴식": "드라마",
    "친구와 놀기": "코미디",
    "새로운 곳 탐험": "액션",
    "혼자 취미생활": "판타지",
    # Q2
    "혼자 있기": "드라마",
    "수다 떨기": "로맨스",
    "운동하기": "액션",
    "맛있는 거 먹기": "코미디",
    # Q3
    "감동 스토리": "드라마",
    "시각적 영상미": "판타지",
    "깊은 메시지": "SF",
    "웃는 재미": "코미디",
    # Q4
    "계획적": "드라마",
    "즉흥적": "로맨스",
    "액티비티": "액션",
    "힐링": "로맨스",
    # Q5
    "듣는 역할": "드라마",
    "주도하기": "액션",
    "분위기 메이커": "코미디",
    "필요할 때 나타남": "SF",
}

# ============================================================
# 5) “누구랑 보면 좋을까” (Princess tone)
# ============================================================

WATCH_WITH: Dict[str, str] = {
    "드라마": "고요한 정서를 함께 음미할 **가까운 벗** 혹은 **편안히 곁을 내어줄 사람**과 함께하시길.",
    "로맨스": "설렘을 나눌 **연인/썸**과 함께하면 황홀하옵니다. (홀로 보시면 감성의 왕관을 쓰게 되실지도.)",
    "코미디": "웃음은 연회처럼 함께할수록 성대해집니다. **친구들/동아리/과 동기**와 함께하소서.",
    "액션": "심장이 뛰는 장면에 함께 환호할 **열정의 동료**(액션 러버 친구/형제자매)와 보시길.",
    "SF": "설정과 떡밥을 해석하며 담소 나눌 **덕질 동무** 혹은 **토론을 즐기는 벗**이 최상입니다.",
    "판타지": "세계관에 흠뻑 젖을 **취향이 닮은 벗**과 좋고, 가끔은 **혼영**도 귀하옵니다.",
}

# ============================================================
# 6) UI Copy (Royal tone)
# ============================================================

APP_NAME = "PickMeMovie"
APP_SUBTITLE = "Princess Edition"
APP_TAGLINE = "고민은 궁정 문지기에게 맡기고, 오늘의 영화는 전하의 취향에 맞게."
APP_DESC = (
    "다섯 가지 문답으로 전하의 ‘지금’ 무드를 가늠하고, "
    "TMDB의 인기작 중 가장 어울리는 5편을 고풍스럽게 진상하옵니다."
)

# ============================================================
# 7) Theme / CSS (공주님 + 고풍 + 왕실)
# ============================================================

st.markdown(
    r"""
<style>
/* =========================
   Princess Edition Theme
   ========================= */

/* Base layout */
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1400px; }

/* Background – parchment + soft pink + gold glow */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 600px at 10% 10%, rgba(255, 205, 230, 0.18), transparent 55%),
    radial-gradient(900px 600px at 90% 15%, rgba(255, 219, 120, 0.20), transparent 55%),
    radial-gradient(1200px 700px at 50% 95%, rgba(188, 170, 255, 0.12), transparent 50%),
    linear-gradient(180deg, rgba(255, 250, 245, 0.55), rgba(255, 245, 252, 0.40));
}

/* Sidebar background */
section[data-testid="stSidebar"] > div {
  background:
    radial-gradient(700px 500px at 15% 10%, rgba(255, 219, 120, 0.25), transparent 55%),
    linear-gradient(180deg, rgba(255,255,255,0.55), rgba(255,255,255,0.30));
  border-right: 1px solid rgba(120, 90, 20, 0.10);
}

/* Typography tweaks */
html, body, [class*="css"]  {
  font-family: ui-serif, "Georgia", "Times New Roman", serif !important;
}

/* Remove default Streamlit padding around some elements */
div[data-testid="stVerticalBlock"] { gap: 1.05rem; }

/* Hero card */
.pm-hero {
  border-radius: 26px;
  padding: 1.35rem 1.6rem;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.65), rgba(255,255,255,0.30));
  border: 1px solid rgba(120, 90, 20, 0.14);
  box-shadow: 0 22px 60px rgba(120, 50, 90, 0.18);
  position: relative;
  overflow: hidden;
}
.pm-hero:before {
  content: "";
  position: absolute;
  inset: -2px;
  background:
    radial-gradient(800px 240px at 12% 12%, rgba(255, 219, 120, 0.26), transparent 55%),
    radial-gradient(700px 260px at 88% 18%, rgba(255, 190, 230, 0.24), transparent 60%);
  opacity: 0.85;
  pointer-events: none;
}
.pm-hero-inner { position: relative; z-index: 1; }
.pm-title {
  font-size: 2.55rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  margin: 0;
  color: rgba(65, 35, 55, 0.95);
}
.pm-subtitle {
  margin: 0.35rem 0 0 0;
  color: rgba(65, 35, 55, 0.72);
  font-size: 1.05rem;
}
.pm-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(120, 90, 20, 0.28), transparent);
  margin: 1.05rem 0 0.85rem 0;
}

/* Crown badge */
.pm-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  background: rgba(255, 219, 120, 0.20);
  border: 1px solid rgba(120, 90, 20, 0.18);
  font-weight: 900;
  color: rgba(65, 35, 55, 0.90);
}

/* Question card */
.pm-qcard {
  border-radius: 20px;
  padding: 1rem 1.1rem 0.9rem 1.1rem;
  background: rgba(255,255,255,0.55);
  border: 1px solid rgba(120, 90, 20, 0.14);
  box-shadow: 0 16px 40px rgba(120, 50, 90, 0.10);
}
.pm-qtitle {
  font-weight: 900;
  font-size: 1.05rem;
  color: rgba(65, 35, 55, 0.92);
  margin-bottom: 0.5rem;
}
.pm-qhint {
  font-size: 0.92rem;
  color: rgba(65, 35, 55, 0.70);
  margin-top: 0.45rem;
}

/* Radio area */
div[role="radiogroup"] label {
  background: rgba(255,255,255,0.60) !important;
  border: 1px solid rgba(120, 90, 20, 0.14) !important;
  border-radius: 999px !important;
  padding: 0.15rem 0.5rem !important;
  margin: 0.18rem 0.22rem 0.18rem 0 !important;
}
div[role="radiogroup"] label:hover {
  border-color: rgba(120, 90, 20, 0.28) !important;
}
div[role="radiogroup"] label span {
  color: rgba(65, 35, 55, 0.88) !important;
  font-weight: 800 !important;
}

/* Buttons */
.stButton > button {
  border-radius: 999px !important;
  padding: 0.78rem 1.05rem !important;
  font-weight: 900 !important;
  border: 1px solid rgba(120, 90, 20, 0.22) !important;
  background: linear-gradient(135deg, rgba(255, 219, 120, 0.55), rgba(255, 190, 230, 0.40)) !important;
  color: rgba(65, 35, 55, 0.92) !important;
  box-shadow: 0 14px 32px rgba(120, 50, 90, 0.14);
}
.stButton > button:hover {
  transform: translateY(-1px);
  filter: brightness(1.03);
}

/* Result hero */
.pm-result {
  border-radius: 26px;
  padding: 1.25rem 1.4rem;
  background:
    radial-gradient(900px 280px at 15% 20%, rgba(255, 219, 120, 0.28), transparent 60%),
    radial-gradient(900px 280px at 85% 25%, rgba(255, 190, 230, 0.25), transparent 60%),
    rgba(255,255,255,0.58);
  border: 1px solid rgba(120, 90, 20, 0.18);
  box-shadow: 0 24px 60px rgba(120, 50, 90, 0.16);
}
.pm-result-title {
  margin: 0;
  font-size: 2.15rem;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: rgba(65, 35, 55, 0.95);
}
.pm-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.28rem 0.8rem;
  border-radius: 999px;
  background: rgba(255, 219, 120, 0.22);
  border: 1px solid rgba(120, 90, 20, 0.20);
  font-weight: 900;
}
.pm-result-sub {
  margin-top: 0.45rem;
  color: rgba(65, 35, 55, 0.72);
}

/* Movie card */
.pm-mcard {
  border-radius: 20px;
  padding: 0.85rem 0.85rem 0.55rem 0.85rem;
  background: rgba(255,255,255,0.58);
  border: 1px solid rgba(120, 90, 20, 0.14);
  box-shadow: 0 14px 38px rgba(120, 50, 90, 0.12);
  transition: transform 160ms ease, box-shadow 160ms ease, border 160ms ease;
}
.pm-mcard:hover {
  transform: translateY(-3px);
  border: 1px solid rgba(120, 90, 20, 0.24);
  box-shadow: 0 18px 44px rgba(120, 50, 90, 0.16);
}
.pm-poster img {
  border-radius: 16px !important;
  border: 1px solid rgba(120, 90, 20, 0.12);
}
.pm-mtitle {
  font-weight: 900;
  color: rgba(65, 35, 55, 0.92);
  font-size: 1.03rem;
  margin-top: 0.55rem;
  line-height: 1.25;
}
.pm-mmeta {
  color: rgba(65, 35, 55, 0.70);
  font-size: 0.92rem;
  margin-top: 0.12rem;
}

/* Expander */
div[data-testid="stExpander"] details {
  border-radius: 16px;
  border: 1px solid rgba(120, 90, 20, 0.14);
  background: rgba(255,255,255,0.50);
}

/* Section headings */
.pm-section {
  font-size: 1.35rem;
  font-weight: 900;
  color: rgba(65, 35, 55, 0.92);
  margin-top: 0.2rem;
}

/* Small helper text */
.pm-caption {
  color: rgba(65, 35, 55, 0.68);
  font-size: 0.95rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 8) Helpers
# ============================================================

def _safe_float(x) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def analyze_answers(answers: List[str]) -> Tuple[str, Dict[str, int], str]:
    """
    답변을 장르 점수로 환산해 1등 장르와 이유 텍스트 반환.
    """
    scores = {g: 0 for g in GENRE_IDS.keys()}
    picked_by_genre = {g: [] for g in GENRE_IDS.keys()}

    for ans in answers:
        g = OPTION_TO_GENRE.get(ans)
        if g:
            scores[g] += 1
            picked_by_genre[g].append(ans)

    # 동점 우선순위(원하는대로 조정 가능)
    priority = ["드라마", "로맨스", "코미디", "액션", "SF", "판타지"]
    top_score = max(scores.values()) if scores else 0
    candidates = [g for g, s in scores.items() if s == top_score] or ["드라마"]
    candidates.sort(key=lambda x: priority.index(x) if x in priority else 999)
    top_genre = candidates[0]

    examples = picked_by_genre[top_genre][:2]
    if examples:
        reason = f"전하의 선택(예: {', '.join(examples)})은 **{top_genre}**의 품격을 가장 강하게 띠옵니다."
    else:
        reason = f"문답의 전체 결을 살피건대, **{top_genre}**가 전하께 가장 어울리옵니다."

    return top_genre, scores, reason


@st.cache_data(show_spinner=False, ttl=600)
def fetch_movies(api_key: str, genre_id: int) -> List[dict]:
    """
    TMDB discover API로 장르별 인기 영화 목록 가져오기
    """
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


def build_reason(top_genre: str, user_reason: str) -> str:
    return f"{user_reason} 그러므로 지금 이 순간, **{top_genre}**의 정취가 깃든 인기작을 진상하옵니다."


def genre_blurb(genre: str) -> str:
    """
    장르를 고풍스럽게 소개
    """
    blurbs = {
        "드라마": "잔잔한 서사와 감정의 레이스가 궁정의 촛불처럼 은은히 타오릅니다.",
        "로맨스": "설렘과 고백의 향이 장미처럼 번지는 밤, 마음이 먼저 왕관을 씁니다.",
        "코미디": "연회장의 웃음처럼 유쾌한 순간이 이어져, 근심을 잠시 내려놓게 하옵니다.",
        "액션": "검과 번개처럼 속도감 넘치는 전개가 피를 데우고, 눈을 떼지 못하게 하옵니다.",
        "SF": "별의 지도와 미지의 문이 열리는 순간, 상상력은 왕실의 영토를 넘어섭니다.",
        "판타지": "마법과 전설이 살아 숨쉬는 세계로—현실의 경계를 우아히 넘나듭니다.",
    }
    return blurbs.get(genre, "전하께 어울리는 특별한 무드가 깃든 장르이옵니다.")


def tiny_pause():
    # 로딩이 너무 즉시 끝나면 느낌이 안 살아서 아주 살짝만
    time.sleep(0.25)


# ============================================================
# 9) Sidebar (Royal Cabinet)
# ============================================================

with st.sidebar:
    st.markdown("## 👑 왕실 서재")
    st.markdown(
        "<div class='pm-caption'>전하의 영화 추천을 위해 필요한 열쇠를 보관하는 곳이옵니다.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### 🔑 TMDB 비밀 열쇠")
    api_key = st.text_input("API Key", type="password", placeholder="여기에 TMDB API Key를 입력하옵소서")
    st.caption("열쇠는 저장되지 않으며, 현재 세션에서만 쓰입니다.")

    st.markdown("---")
    st.markdown("### 💡 참고/영감 (왕실 기록)")
    st.markdown(
        "- **넷플릭스(Netflix)**: 개인화 추천 경험\n"
        "- **왓챠(Watcha)**: 평가 기반 취향 분석\n"
        "- **IMDb**: 평점/리뷰 중심 탐색"
    )

    st.markdown("---")
    st.markdown("### 🕊️ 안내")
    st.markdown(
        "<div class='pm-caption'>이 앱은 장르 기반 추천(인기순)입니다. "
        "다음 단계에서 OpenAI를 연결하면 ‘추천 이유’가 더 정교해집니다.</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# 10) Main — Hero
# ============================================================

st.markdown(
    f"""
<div class="pm-hero">
  <div class="pm-hero-inner">
    <div class="pm-badge">👑 {APP_NAME} · {APP_SUBTITLE}</div>
    <div class="pm-divider"></div>
    <h1 class="pm-title">{APP_TAGLINE}</h1>
    <p class="pm-subtitle">{APP_DESC}</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")
st.markdown(
    "<div class='pm-section'>📜 궁정 문답 (5문항)</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='pm-caption'>가장 마음이 가는 선택지 하나만 고르시면 되옵니다.</div>",
    unsafe_allow_html=True,
)

# ============================================================
# 11) Questions — Two-column layout (더 왕실스럽게)
# ============================================================

answers: List[str] = []

left, right = st.columns([1, 1], gap="large")
question_cols = [left, right, left, right, left]  # 5개 배치

for i, (q, opts) in enumerate(QUESTIONS, start=1):
    with question_cols[i - 1]:
        st.markdown(f"<div class='pm-qcard'>", unsafe_allow_html=True)
        st.markdown(f"<div class='pm-qtitle'>{q}</div>", unsafe_allow_html=True)

        # 라디오를 좀 더 “공주님 감성”으로: 가로 배치
        choice = st.radio(
            label="",
            options=opts,
            key=f"q{i}",
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown(
            "<div class='pm-qhint'>✨ 전하의 선택은 곧 무드의 왕관이 되옵니다.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        answers.append(choice)

st.write("")
c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.2, 2.4], gap="large")
with c1:
    run_btn = st.button("👑 결과를 진상하라", type="primary", use_container_width=True)
with c2:
    st.button("🔄 다시 고르기", use_container_width=True)
with c3:
    st.button("💾 (다음) 결과 저장", use_container_width=True, disabled=True)
with c4:
    st.markdown(
        "<div class='pm-caption'>※ 저장 기능은 ‘다음 단계’에서 구현 예정(세션/DB).</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# 12) Result Section
# ============================================================

if run_btn:
    if not api_key.strip():
        st.error("왕실 서재(사이드바)에 TMDB 비밀 열쇠(API Key)를 먼저 입력하옵소서.")
        st.stop()

    with st.spinner("👑 전하의 취향을 분석 중이옵니다... (왕실 추천서를 작성하는 중)"):
        tiny_pause()
        top_genre, scores, user_reason = analyze_answers(answers)
        genre_id = GENRE_IDS[top_genre]

        try:
            movies = fetch_movies(api_key.strip(), genre_id)
        except requests.HTTPError:
            st.error("TMDB 요청이 실패하였습니다. 열쇠(API Key)가 올바른지 확인하옵소서.")
            st.stop()
        except requests.RequestException:
            st.error("네트워크가 불안정하옵니다. 잠시 후 다시 시도하옵소서.")
            st.stop()

        tiny_pause()

    watch_with_text = WATCH_WITH.get(top_genre, "취향이 맞는 벗과 함께 보시면 더 즐거우리다.")
    blurb = genre_blurb(top_genre)

    st.write("")
    st.markdown(
        f"""
<div class="pm-result">
  <h2 class="pm-result-title">당신에게 딱인 장르는: <span class="pm-pill">👑 {top_genre}</span>!</h2>
  <div class="pm-result-sub">{blurb}</div>
  <div class="pm-result-sub" style="margin-top:0.45rem;">{user_reason}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")
    info_left, info_right = st.columns([1.25, 1.85], gap="large")
    with info_left:
        st.success(f"👥 **누구와 함께 보시면 좋을까요?**\n\n{watch_with_text}")
    with info_right:
        st.info(
            "📌 **추천 기준**\n\n"
            "TMDB의 장르 기반 인기작을 가져오며, 전하의 선택을 통해 가장 어울리는 장르를 결정하옵니다.\n\n"
            "다음 단계에서 OpenAI를 연결하면 영화별 추천 이유를 더 섬세하게 생성할 수 있사옵니다."
        )

    if not movies:
        st.warning("해당 장르의 영화가 조회되지 않았사옵니다. 다른 선택으로 다시 시도하옵소서.")
        st.stop()

    st.write("")
    st.markdown("<div class='pm-section'>🍿 왕실 추천 영화 5선</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='pm-caption'>아래의 카드를 열어 줄거리와 추천 이유를 확인하옵소서.</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    # 3열 카드
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

            st.markdown("</div>", unsafe_allow_html=True)

    # Debug / Score
    with st.expander("🧾 (선택) 장르 점수표 열람"):
        st.json(scores)
