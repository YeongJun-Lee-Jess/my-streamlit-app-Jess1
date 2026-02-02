import streamlit as st
import requests
from typing import Dict, List, Tuple

st.set_page_config(page_title="나와 어울리는 영화는?", page_icon="🎬", layout="wide")

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
# 심리테스트 질문
# -----------------------------
QUESTIONS: List[Tuple[str, List[str]]] = [
    ("1. 주말에 가장 하고 싶은 것은?", ["집에서 휴식", "친구와 놀기", "새로운 곳 탐험", "혼자 취미생활"]),
    ("2. 스트레스 받으면?", ["혼자 있기", "수다 떨기", "운동하기", "맛있는 거 먹기"]),
    ("3. 영화에서 중요한 것은?", ["감동 스토리", "시각적 영상미", "깊은 메시지", "웃는 재미"]),
    ("4. 여행 스타일?", ["계획적", "즉흥적", "액티비티", "힐링"]),
    ("5. 친구 사이에서 나는?", ["듣는 역할", "주도하기", "분위기 메이커", "필요할 때 나타남"]),
]

# 각 선택지를 "장르 성향"으로 매핑 (점수 1점)
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

# 장르별 "누구랑 보면 좋은지" 추천 문구
WATCH_WITH: Dict[str, str] = {
    "드라마": "감정선을 같이 따라가줄 **친한 친구**나, 편하게 이야기 나눌 수 있는 **가까운 사람**과 좋아요.",
    "로맨스": "설레는 분위기를 함께 즐길 **연인/썸 상대**와 최고예요. (혼자 봐도 감성 충전!)",
    "코미디": "웃음이 배가 되는 **친구들**이나 **동아리/과 친구**랑 보면 더 재밌어요.",
    "액션": "같이 몰입해서 ‘와!’ 할 수 있는 **액션 좋아하는 친구**나 **형제/자매**랑 추천!",
    "SF": "설정 얘기, 떡밥 해석을 같이 할 수 있는 **덕질 친구**나 **토론 좋아하는 친구**와 찰떡!",
    "판타지": "세계관에 푹 빠질 수 있는 **취향 비슷한 친구**나, 조용히 즐기고 싶다면 **혼영**도 좋아요.",
}

# -----------------------------
# 로직
# -----------------------------
def analyze_answers(answers: List[str]) -> Tuple[str, Dict[str, int], str]:
    """답변을 장르 점수로 환산해 1등 장르 + 요약 이유 반환"""
    scores = {g: 0 for g in GENRE_IDS.keys()}
    picked_by_genre = {g: [] for g in GENRE_IDS.keys()}

    for ans in answers:
        g = OPTION_TO_GENRE.get(ans)
        if g:
            scores[g] += 1
            picked_by_genre[g].append(ans)

    # 동점 처리: 우선순위로 안정적인 선택
    priority = ["드라마", "로맨스", "코미디", "액션", "SF", "판타지"]
    top_score = max(scores.values())
    candidates = [g for g, s in scores.items() if s == top_score]
    candidates.sort(key=lambda x: priority.index(x) if x in priority else 999)
    top_genre = candidates[0]

    examples = picked_by_genre[top_genre][:2]
    if examples:
        reason = f"선택한 답변(예: {', '.join(examples)})을 보면 **{top_genre}** 성향이 가장 강해요."
    else:
        reason = f"전체 답변 흐름상 **{top_genre}** 장르가 가장 잘 맞아 보여요."

    return top_genre, scores, reason


@st.cache_data(show_spinner=False, ttl=600)
def fetch_movies(api_key: str, genre_id: int) -> List[dict]:
    """TMDB discover API로 장르별 인기 영화 목록 가져오기"""
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
    return f"{user_reason} 그래서 **{top_genre}** 느낌이 강한 인기 영화를 추천해요!"


# -----------------------------
# 스타일(CSS)
# -----------------------------
st.markdown(
    """
    <style>
      .hero {
        padding: 1rem 1.25rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(255,215,0,0.18), rgba(99,102,241,0.10));
        border: 1px solid rgba(255,255,255,0.10);
        margin-bottom: 1rem;
      }
      .hero-title {
        font-size: 2.0rem;
        font-weight: 900;
        line-height: 1.25;
        margin: 0;
      }
      .genre-pill {
        display: inline-block;
        padding: 0.22rem 0.7rem;
        border-radius: 999px;
        font-weight: 800;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.16);
      }
      .card-title {
        font-size: 1.05rem;
        font-weight: 850;
        margin-top: 0.35rem;
      }
      .card-sub {
        font-size: 0.95rem;
        opacity: 0.85;
      }
      .small-muted {
        opacity: 0.75;
        font-size: 0.9rem;
      }
      div[data-testid="stExpander"] details {
        border-radius: 14px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# UI
# -----------------------------
st.title("🎬 나와 어울리는 영화는?")
st.write("아래 5개 질문에 답하면, 당신에게 어울리는 장르를 분석해서 TMDB 인기 영화 5편을 추천해드려요!")

with st.sidebar:
    st.header("🔑 TMDB API Key")
    api_key = st.text_input("API Key 입력", type="password", placeholder="TMDB API Key를 입력하세요")
    st.caption("키는 저장되지 않고, 현재 실행 중인 세션에서만 사용돼요.")

st.divider()

answers: List[str] = []
for q, opts in QUESTIONS:
    answers.append(st.radio(q, opts, key=q))

st.divider()

# -----------------------------
# 결과 보기
# -----------------------------
if st.button("결과 보기", type="primary"):
    if not api_key.strip():
        st.error("사이드바에서 TMDB API Key를 먼저 입력해 주세요.")
        st.stop()

    with st.spinner("분석 중..."):
        top_genre, scores, user_reason = analyze_answers(answers)
        genre_id = GENRE_IDS[top_genre]

        try:
            movies = fetch_movies(api_key.strip(), genre_id)
        except requests.HTTPError:
            st.error("TMDB 요청에 실패했어요. API Key 또는 요청 파라미터를 확인해 주세요.")
            st.stop()
        except requests.RequestException:
            st.error("네트워크 오류로 TMDB에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.")
            st.stop()

    # 결과 헤더
    watch_with_text = WATCH_WITH.get(top_genre, "취향이 맞는 친구와 함께 보면 더 좋아요!")
    st.markdown(
        f"""
        <div class="hero">
          <p class="hero-title">당신에게 딱인 장르는: <span class="genre-pill">{top_genre}</span>!</p>
          <p class="small-muted">TMDB 인기 순(장르 기반)으로 5편을 추천해요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 누구랑 보면 좋은지 + 분석 요약
    st.success(f"👥 **누구랑 보면 좋을까?**  {watch_with_text}")
    st.info(user_reason)

    if not movies:
        st.warning("해당 장르의 영화를 가져오지 못했어요. 다른 선택으로 다시 시도해 보세요.")
        st.stop()

    st.subheader("🎥 추천 영화 TOP 5")

    # 3열 카드
    cols = st.columns(3, gap="large")

    for idx, m in enumerate(movies[:5]):
        title = m.get("title") or "제목 없음"
        rating = m.get("vote_average")
        overview = m.get("overview") or "줄거리 정보가 없어요."
        poster_path = m.get("poster_path")
        poster_url = f"{TMDB_POSTER_BASE}{poster_path}" if poster_path else None

        with cols[idx % 3]:
            with st.container(border=True):
                # 카드: 포스터/제목/평점
                if poster_url:
                    st.image(poster_url, use_container_width=True)
                else:
                    st.caption("포스터 없음")

                st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
                if isinstance(rating, (int, float)):
                    st.markdown(f'<div class="card-sub">⭐ 평점: <b>{rating:.1f}</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="card-sub">⭐ 평점: 정보 없음</div>', unsafe_allow_html=True)

                # 상세(클릭)
                with st.expander("상세 보기"):
                    st.markdown("**줄거리**")
                    st.write(overview)

                    st.markdown("**이 영화를 추천하는 이유**")
                    st.write(build_reason(top_genre, user_reason))

                    st.markdown("**누구랑 보면 더 좋을까?**")
                    st.write(watch_with_text)

    # (선택) 점수 표시가 필요하면 주석 해제
    # st.write("장르 점수")
    # st.json(scores)
