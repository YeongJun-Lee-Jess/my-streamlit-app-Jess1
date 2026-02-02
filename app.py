import streamlit as st
import requests
from typing import Dict, List, Tuple

# =============================
# Page
# =============================
st.set_page_config(page_title="PickMeMovie", page_icon="🎬", layout="wide")

# =============================
# TMDB
# =============================
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

# =============================
# “멋있게” 바꾼 질문(문구 업그레이드)
# (선택지는 기존 4개 그대로 유지)
# =============================
QUESTIONS: List[Tuple[str, List[str]]] = [
    ("1) 이번 주말, 네 에너지가 가장 끌리는 방향은?", ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"]),
    ("2) 멘탈 흔들릴 때, 너만의 회복 루틴은?", ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"]),
    ("3) 영화 한 편을 ‘명작’으로 만드는 결정적 요소는?", ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"]),
    ("4) 여행을 떠난 너의 플레이리스트는 어떤 느낌?", ["계획적", "즉흥적", "액티비티", "힐링"]),
    ("5) 친구들 사이에서 너의 포지션은?", ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"]),
]

# 선택지 -> 장르 성향
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

# 장르별 “누구랑 보면 좋은지”
WATCH_WITH: Dict[str, str] = {
    "드라마": "감정선을 천천히 따라가줄 **가까운 친구/동기** 또는 **조용히 함께 있어도 편한 사람**과 찰떡.",
    "로맨스": "설렘을 공유할 **연인/썸**과 최고! (혼자 보면 ‘감성 충전’ 확실.)",
    "코미디": "웃음은 나눌수록 커져. **친구들/과 동기/동아리**와 같이 보면 만족도 폭발.",
    "액션": "몰입해서 같이 소리 지를 사람 필요함. **액션 좋아하는 친구** 또는 **형제/자매** 추천!",
    "SF": "떡밥·설정·해석 토크가 핵심. **덕질 친구/토론 좋아하는 친구**와 보면 2배 재밌음.",
    "판타지": "세계관에 진심인 **취향 비슷한 친구**와 좋고, 분위기 타고 싶으면 **혼영**도 강추.",
}

# =============================
# Logic
# =============================
def analyze_answers(answers: List[str]) -> Tuple[str, Dict[str, int], str]:
    scores = {g: 0 for g in GENRE_IDS.keys()}
    picked_by_genre = {g: [] for g in GENRE_IDS.keys()}

    for ans in answers:
        g = OPTION_TO_GENRE.get(ans)
        if g:
            scores[g] += 1
            picked_by_genre[g].append(ans)

    # 동점 우선순위
    priority = ["드라마", "로맨스", "코미디", "액션", "SF", "판타지"]
    top_score = max(scores.values())
    candidates = [g for g, s in scores.items() if s == top_score]
    candidates.sort(key=lambda x: priority.index(x) if x in priority else 999)
    top_genre = candidates[0]

    examples = picked_by_genre[top_genre][:2]
    if examples:
        reason = f"네 선택(예: {', '.join(examples)}) 흐름이 **{top_genre}** 감성에 가장 가까워!"
    else:
        reason = f"전체 답변 흐름상 **{top_genre}** 장르가 가장 잘 맞아 보여!"

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
    r = requests.get(TMDB_DISCOVER_URL, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get("results", [])


def build_reason(top_genre: str, user_reason: str) -> str:
    return f"{user_reason} 그래서 지금 딱 보기 좋은 **{top_genre}** 무드의 인기작으로 골랐어."


# =============================
# Ultra UI (CSS)
# =============================
st.markdown(
    """
<style>
/* ---- Global ---- */
:root {
  --card: rgba(255,255,255,0.06);
  --card2: rgba(255,255,255,0.08);
  --stroke: rgba(255,255,255,0.10);
  --stroke2: rgba(255,255,255,0.14);
  --textSoft: rgba(255,255,255,0.78);
  --shadow: 0 20px 60px rgba(0,0,0,0.35);
}
.block-container { padding-top: 2.0rem; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

/* ---- Hero ---- */
.hero {
  border-radius: 26px;
  padding: 1.35rem 1.6rem;
  background:
    radial-gradient(1200px 600px at 10% 10%, rgba(255,215,0,0.22), transparent 55%),
    radial-gradient(1000px 650px at 95% 20%, rgba(99,102,241,0.20), transparent 50%),
    linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
  border: 1px solid var(--stroke);
  box-shadow: var(--shadow);
}
.hero h1 {
  margin: 0;
  font-size: 2.3rem;
  font-weight: 900;
  letter-spacing: -0.02em;
}
.hero p {
  margin: 0.35rem 0 0 0;
  color: var(--textSoft);
  font-size: 1.02rem;
}

/* ---- Pill ---- */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.28rem 0.72rem;
  border-radius: 999px;
  font-weight: 900;
  background: rgba(255,255,255,0.10);
  border: 1px solid var(--stroke2);
}

/* ---- Question Card ---- */
.qwrap {
  border-radius: 18px;
  padding: 1rem 1.05rem;
  background: linear-gradient(180deg, var(--card), rgba(255,255,255,0.02));
  border: 1px solid var(--stroke);
}
.qtitle {
  font-weight: 900;
  font-size: 1.06rem;
  margin-bottom: 0.55rem;
  letter-spacing: -0.01em;
}
.hint {
  color: var(--textSoft);
  font-size: 0.92rem;
}

/* ---- Movie Card ---- */
.mcard {
  border-radius: 18px;
  padding: 0.85rem 0.85rem 0.5rem 0.85rem;
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  border: 1px solid var(--stroke);
  box-shadow: 0 12px 30px rgba(0,0,0,0.28);
  transition: transform 160ms ease, border 160ms ease;
}
.mcard:hover {
  transform: translateY(-3px);
  border: 1px solid rgba(255,255,255,0.20);
}
.mtitle {
  font-size: 1.02rem;
  font-weight: 900;
  margin-top: 0.55rem;
  line-height: 1.25;
}
.mmeta {
  margin-top: 0.15rem;
  color: var(--textSoft);
  font-size: 0.92rem;
}

/* ---- Poster ---- */
.poster img {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.10);
}

/* ---- Buttons ---- */
.stButton > button {
  border-radius: 999px !important;
  padding: 0.75rem 1.1rem !important;
  font-weight: 900 !important;
}

/* ---- Expander ---- */
div[data-testid="stExpander"] details {
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.04);
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# Sidebar
# =============================
with st.sidebar:
    st.markdown("### 🔑 TMDB API Key")
    api_key = st.text_input("API Key", type="password", placeholder="TMDB API Key를 입력하세요")
    st.caption("키는 저장되지 않고, 현재 세션에서만 사용돼요.")

    st.divider()
    st.markdown("### 💡 참고/영감")
    st.markdown(
        "- **넷플릭스(Netflix)**: 개인화 추천 경험\n"
        "- **왓챠(Watcha)**: 평가 기반 취향 분석\n"
        "- **IMDb**: 평점/리뷰 중심 탐색"
    )

# =============================
# Main Header
# =============================
st.markdown(
    """
<div class="hero">
  <h1>🎬 PickMeMovie</h1>
  <p>고민은 짧게, 취향은 정확하게. <b>지금</b> 보기 좋은 영화를 골라줄게.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.write("")
st.markdown("#### ✨ 5문항으로 ‘지금의 너’에 딱 맞는 무드를 찾자")

# =============================
# Questions (pretty)
# =============================
answers: List[str] = []

for i, (q, opts) in enumerate(QUESTIONS, start=1):
    st.markdown(f'<div class="qwrap"><div class="qtitle">{q}</div>', unsafe_allow_html=True)
    choice = st.radio(
        label="",
        options=opts,
        key=f"q{i}",
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown(f'<div class="hint">선택 하나로 분위기가 결정돼요 👀</div></div>', unsafe_allow_html=True)
    st.write("")
    answers.append(choice)

# =============================
# CTA
# =============================
c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    show = st.button("🚀 결과 보기", type="primary", use_container_width=True)
with c2:
    st.button("🔄 다시 선택", use_container_width=True)
with c3:
    st.caption("Tip: 결과는 TMDB 인기 순 기반 + (다음 단계에서) AI 근거 생성으로 더 정교해질 수 있어요.")

# =============================
# Result
# =============================
if show:
    if not api_key.strip():
        st.error("사이드바에 TMDB API Key를 입력해 주세요.")
        st.stop()

    with st.spinner("🧠 취향 분석 중... 영화 세계관 소환 중..."):
        top_genre, scores, user_reason = analyze_answers(answers)
        genre_id = GENRE_IDS[top_genre]
        try:
            movies = fetch_movies(api_key.strip(), genre_id)
        except requests.HTTPError:
            st.error("TMDB 요청에 실패했어요. API Key가 맞는지 확인해 주세요.")
            st.stop()
        except requests.RequestException:
            st.error("네트워크 오류로 TMDB에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.")
            st.stop()

    watch_with_text = WATCH_WITH.get(top_genre, "취향이 맞는 친구와 함께 보면 더 좋아요!")

    st.write("")
    st.markdown(
        f"""
<div class="hero">
  <h1>당신에게 딱인 장르는: <span class="pill">✨ {top_genre}</span>!</h1>
  <p>{user_reason}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.write("")
    colA, colB = st.columns([1.2, 2.0], gap="large")
    with colA:
        st.success(f"👥 **누구랑 보면 좋을까?**\n\n{watch_with_text}")
    with colB:
        st.info("🎯 **추천 기준**\n\nTMDB의 인기 순 데이터를 바탕으로, 지금 당신의 무드와 가장 가까운 장르 영화 5편을 보여줘요.")

    if not movies:
        st.warning("해당 장르 영화가 없어요. 다시 시도해 주세요.")
        st.stop()

    st.write("")
    st.markdown("## 🍿 추천 영화 TOP 5")
    st.caption("카드를 눌러 상세 정보를 확인해봐!")

    # 3-column cards
    cols = st.columns(3, gap="large")
    top5 = movies[:5]

    for idx, m in enumerate(top5):
        title = m.get("title") or "제목 없음"
        rating = m.get("vote_average")
        overview = m.get("overview") or "줄거리 정보가 없어요."
        poster_path = m.get("poster_path")
        poster_url = f"{TMDB_POSTER_BASE}{poster_path}" if poster_path else None

        with cols[idx % 3]:
            st.markdown('<div class="mcard">', unsafe_allow_html=True)

            if poster_url:
                st.markdown('<div class="poster">', unsafe_allow_html=True)
                st.image(poster_url, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.caption("포스터 없음")

            st.markdown(f'<div class="mtitle">{title}</div>', unsafe_allow_html=True)
            if isinstance(rating, (int, float)):
                st.markdown(f'<div class="mmeta">⭐ 평점 <b>{rating:.1f}</b></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="mmeta">⭐ 평점 정보 없음</div>', unsafe_allow_html=True)

            with st.expander("📌 상세 보기"):
                st.markdown("**줄거리**")
                st.write(overview)

                st.markdown("**이 영화를 추천하는 이유**")
                st.write(build_reason(top_genre, user_reason))

                st.markdown("**누구랑 보면 더 좋을까?**")
                st.write(watch_with_text)

            st.markdown("</div>", unsafe_allow_html=True)

    # (원하면 점수도 보여주기)
    with st.expander("🧾 (디버그) 장르 점수 보기"):
        st.json(scores)
