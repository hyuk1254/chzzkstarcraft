import streamlit as st
import pandas as pd
import time
import json

# 페이지 설정
st.set_page_config(layout="wide", page_title="스타크래프트 대회 대시보드")

# =========================================================
# 🔗 [중요] 여기에 질문자님의 구글 스프레드시트 주소를 입력하세요!
# =========================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eA1GCEga0FcpmPMO8Qm8nXoZOPeQioAaBgXZs-NDyCc/edit?usp=sharing"

# =========================================================
# 🎨 [시각 효과] 여기에 자체 제작하신 종족 마크 이미지 주소(URL)를 넣으세요!
# =========================================================
RACE_ICONS = {
    "테란": "https://via.placeholder.com/20/00ffa3/ffffff?text=T",  # 👈 여기에 테란 마크 주소 삽입
    "저그": "https://via.placeholder.com/20/00ffa3/ffffff?text=Z",  # 👈 여기에 저그 마크 주소 삽입
    "프로토스": "https://via.placeholder.com/20/00ffa3/ffffff?text=P", # 👈 여기에 프로토스 마크 주소 삽입
}

# 구글 시트를 판다스 데이터프레임으로 변환하여 안전하게 긁어오는 함수
@st.cache_data(ttl=2) # 2초마다 구글 시트의 최신 데이터를 갱신
def fetch_sheet_data(sheet_name):
    try:
        csv_url = SHEET_URL.replace("/edit?usp=sharing", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}")
        csv_url = csv_url.replace("/edit#", f"/gviz/tq?tqx=out:csv&sheet={sheet_name}&")
        df = pd.read_csv(csv_url)
        return df.fillna("")
    except Exception as e:
        return pd.DataFrame()

# 구글 시트 데이터 로드
df_players = fetch_sheet_data("players")
df_maps = fetch_sheet_data("maps")

# 실시간 매치 및 드래프트 동기화 세션 연동
if "matches" not in st.session_state:
    st.session_state.matches = []
if "teams" not in st.session_state:
    st.session_state.teams = {
        "Left_Team": {"name": "좌측", "players": []},
        "Right_Team": {"name": "우측", "players": []}
    }
if "today_entry" not in st.session_state:
    st.session_state.today_entry = []
if "assigned_maps" not in st.session_state:
    st.session_state.assigned_maps = [] # ⭐ 팀 가르기 탭에서 지정된 맵 순서 저장 공간

# --- 🎨 치지직 오피셜 컬러 및 이미지 크롭 커스텀 스타일 ---
st.markdown("""
<style>
    /* 치지직 다크 모드 배경 및 기본 텍스트 색상 */
    .stApp { background-color: #0c0d10; color: #e2e8f0; }
    
    /* 가독성 개선 백신: 어두운 배경에서 숨은 모든 텍스트를 흰색/밝은색으로 강제 교정 */
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp div {
        color: #e2e8f0 !important;
    }
    
    /* 드롭다운(Selectbox) 선택 창 및 라벨 글씨색 흰색 고정 */
    div[data-baseweb="select"] * {
        color: #ffffff !important;
    }
    div[data-testid="stSelectbox"] label p {
        color: #00ffa3 !important; 
        font-weight: bold;
    }
    /* 드롭다운 클릭 시 아래로 열리는 팝업 메뉴 배경 및 폰트 색상 강제 지정 */
    ul[role="listbox"] li {
        background-color: #1c1e26 !important;
        color: #ffffff !important;
    }
    ul[role="listbox"] li:hover {
        background-color: #2d3139 !important;
        color: #00ffa3 !important;
    }
    
    /* 데이터프레임 및 테이블 내부 글씨 보정 */
    .stDataFrame div { color: #ffffff !important; }
    
    /* 타이틀 그라데이션: 화이트에서 치지직 연두색(#00ffa3)으로 */
    .main-title {
        text-align: center; font-size: 3rem !important; font-weight: 900 !important;
        color: #ffffff !important; letter-spacing: 2px; margin-bottom: 5px;
        background: linear-gradient(to right, #ffffff, #00ffa3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    /* 선수 카드: 치지직 UI 스타일의 어두운 회색 조합 */
    .player-card {
        background-color: #181a20; border: 1px solid #2d3139;
        border-radius: 10px; padding: 10px; margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    .draft-panel {
        background-color: #181a20; border: 1px solid #2d3139;
        border-radius: 12px; padding: 25px; margin-top: 10px;
    }
    
    /* 대시보드 내부 모든 이미지 강제 규격화 CSS */
    .player-list-img img {
        width: 60px !important; height: 60px !important;
        object-fit: cover !important; border-radius: 6px !important;
    }
    .match-player-img img {
        width: 100% !important; max-height: 140px !important;
        object-fit: cover !important; border-radius: 8px !important;
    }
    .match-map-img img {
        max-height: 140px !important; object-fit: contain !important; border-radius: 8px !important;
    }
    
    /* 종족 마크 미니 이미지 스타일 */
    .race-icon-img {
        display: inline-block; width: 16px; height: 16px; 
        object-fit: contain; vertical-align: middle; margin-right: 4px;
    }

    /* 추가 정보 태그: 연두색 포인트 border 처리 */
    .extra-info {
        font-size: 0.8rem; color: #00ffa3 !important; background-color: #0c0d10;
        padding: 2px 8px; border-radius: 4px; margin-top: 6px; 
        display: inline-block; border: 1px solid rgba(0, 255, 163, 0.2);
    }
    .extra-info * { color: #00ffa3 !important; }
    
    /* 스트림릿 기본 버튼 스타일 커스텀 */
    .stButton > button {
        padding: 3px 10px !important; font-size: 0.85rem !important;
        line-height: 1.5 !important; border-radius: 6px !important;
        background-color: #1c1e26 !important; color: #e2e8f0 !important;
        border: 1px solid #2d3139 !important; transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #00ffa3 !important; color: #00ffa3 !important;
        box-shadow: 0 0 8px rgba(0, 255, 163, 0.3);
    }
    .stButton > button * { color: inherit !important; }
    
    /* 조작 수정용 미니 취소 버튼 (X) 전용 디자인 */
    .del-btn > div > button {
        padding: 1px 6px !important; font-size: 0.75rem !important;
        background-color: rgba(255, 85, 85, 0.15) !important; color: #ff5555 !important;
        border: 1px solid rgba(255, 85, 85, 0.3) !important;
    }
    .del-btn > div > button:hover {
        background-color: #ff5555 !important; color: #ffffff !important;
        box-shadow: 0 0 8px rgba(255, 85, 85, 0.4);
    }

    /* 탭 메뉴 바 디자인: 최상단 구석으로 완벽 밀착 및 여백 제거 */
    .stTabs { margin-top: -50px !important; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; justify-content: flex-start !important; padding-left: 5px; border-bottom: 1px solid #2d3139; margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 32px !important; background-color: #14161d; border-radius: 4px 4px 0px 0px;
        padding: 4px 12px !important; font-size: 0.85rem !important; color: #64748b !important;
        border: 1px solid #2d3139; border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] * { color: inherit !important; }
    .stTabs [aria-selected="true"] {
        background-color: #1c1e26 !important; color: #00ffa3 !important; font-weight: bold; border-top: 2px solid #00ffa3 !important; 
    }
    
    .stCheckbox [data-testid="stCheckboxUserSelectBackdrop"] { background-color: #00ffa3 !important; }
    hr { border-color: #2d3139 !important; }
    .copyright-text { text-align: center; font-size: 0.75rem; color: #555b66 !important; margin-top: 50px; margin-bottom: 20px; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# 종족 텍스트 표준화 및 마크 HTML 렌더링 함수
def get_race_badge_html(race_text):
    race_text = str(race_text).strip().lower()
    norm_race = "테란" if "테" in race_text or "te" in race_text else "저그" if "저" in race_text or "ze" in race_text else "프로토스" if "프" in race_text or "pr" in race_text else "미정"
    
    icon_url = RACE_ICONS.get(norm_race)
    if icon_url and norm_race != "미정":
        return f'<img src="{icon_url}" class="race-icon-img"> <span style="color:#94a3b8 !important; font-size:0.9rem; vertical-align:middle;">{norm_race}</span>'
    else:
        return f'<span style="color:#94a3b8 !important; font-size:0.9rem; vertical-align:middle;">🟡 {norm_race}</span>'

# --- 🎬 [사이드바] 스크린 제어 ---
with st.sidebar:
    st.header("🎬 스크린 제어")
    broadcast_mode = st.checkbox("📺 방송 송출 모드 (UI 전체 숨기기)", value=False)
    if broadcast_mode:
        st.info("🔄 실시간 송출 동기화 활성화 중...")
        time.sleep(2)
        st.rerun()

# 🗂️ 3단 탭 구조 정의
if not broadcast_mode:
    tab_main, tab_draft, tab_admin = st.tabs(["🏆 메인 대시보드", "🤝 팀 가르기", "⚙️ 데이터 관리"])
else:
    tab_main = st.container()

# =========================================================
# 🏆 [1번 탭] 메인 경기 대시보드 화면
# =========================================================
with tab_main:
    st.markdown("<h1 class='main-title'>스진동 종족최강전</h1>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

    main_col1, main_col2, main_col3 = st.columns([2.5, 5, 2.5])

    # 👈 좌측 팀 명단
    with main_col1:
        left_team_data = st.session_state.teams["Left_Team"]
        st.markdown(f"<h2 style='color: #00ffa3 !important; text-align: center; font-weight: bold;'>{left_team_data['name']}</h2>", unsafe_allow_html=True)
        st.write("")
        
        for p_name in list(left_team_data["players"]):
            p_row = df_players[df_players['name'] == p_name] if not df_players.empty else pd.DataFrame()
            race = p_row.iloc[0]['race'] if not p_row.empty else "미정"
            img = p_row.iloc[0]['img_url'] if not p_row.empty else ""
            
            with st.container():
                st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
                p_cols = st.columns([1.2, 2.2, 0.6] if not broadcast_mode else [1.2, 2.8])
                with p_cols[0]:
                    st.markdown("<div class='player-list-img'>", unsafe_allow_html=True)
                    st.image(img if img else "https://via.placeholder.com/60/181a20/e2e8f0?text=User")
                    st.markdown("</div>", unsafe_allow_html=True)
                with p_cols[1]:
                    st.markdown(f"<p style='margin-bottom:2px; font-size:1.1rem; color:#ffffff !important;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                    st.markdown(get_race_badge_html(race), unsafe_allow_html=True)
                    
                    if not df_players.empty and not p_row.empty:
                        extra_info_list = []
                        for col in df_players.columns:
                            if col not in ['name', 'race', 'img_url']:
                                val = p_row.iloc[0][col]
                                if val: extra_info_list.append(f"{col}: {val}")
                        if extra_info_list:
                            st.markdown(f"<div class='extra-info'>{' | '.join(extra_info_list)}</div>", unsafe_allow_html=True)
                            
                if not broadcast_mode:
                    with p_cols[2]:
                        if st.button("X", key=f"del_L_{p_name}"):
                            left_team_data["players"].remove(p_name)
                            st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # 👉 우측 팀 명단
    with main_col3:
        right_team_data = st.session_state.teams["Right_Team"]
        st.markdown(f"<h2 style='color: #00ffa3 !important; text-align: center; font-weight: bold;'>{right_team_data['name']}</h2>", unsafe_allow_html=True)
        st.write("")
        
        for p_name in list(right_team_data["players"]):
            p_row = df_players[df_players['name'] == p_name] if not df_players.empty else pd.DataFrame()
            race = p_row.iloc[0]['race'] if not p_row.empty else "미정"
            img = p_row.iloc[0]['img_url'] if not p_row.empty else ""
            
            with st.container():
                st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
                p_cols = st.columns([1.2, 2.2, 0.6] if not broadcast_mode else [1.2, 2.8])
                with p_cols[0]:
                    st.markdown("<div class='player-list-img'>", unsafe_allow_html=True)
                    st.image(img if img else "https://via.placeholder.com/60/181a20/e2e8f0?text=User")
                    st.markdown("</div>", unsafe_allow_html=True)
                with p_cols[1]:
                    st.markdown(f"<p style='margin-bottom:2px; font-size:1.1rem; color:#ffffff !important;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                    st.markdown(get_race_badge_html(race), unsafe_allow_html=True)
                    
                    if not df_players.empty and not p_row.empty:
                        extra_info_list = []
                        for col in df_players.columns:
                            if col not in ['name', 'race', 'img_url']:
                                val = p_row.iloc[0][col]
                                if val: extra_info_list.append(f"{col}: {val}")
                        if extra_info_list:
                            st.markdown(f"<div class='extra-info'>{' | '.join(extra_info_list)}</div>", unsafe_allow_html=True)
                            
                    if not broadcast_mode:
                        with p_cols[2]:
                            if st.button("X", key=f"del_R_{p_name}"):
                                right_team_data["players"].remove(p_name)
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # ⚔️ 중앙 실시간 대진 지명 및 MATCH BOARD
    with main_col2:
        if not broadcast_mode:
            st.markdown("<h3 style='text-align: center; color:#00ffa3 !important; font-weight: bold; margin-bottom: 15px;'>📝 실시간 대진 지명</h3>", unsafe_allow_html=True)
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
            with ctrl_col1:
                p1 = st.selectbox(f"{left_team_data['name']} 선택", options=left_team_data["players"], key="sb_p1")
            with ctrl_col2:
                p2 = st.selectbox(f"{right_team_data['name']} bandwidth 선택", options=right_team_data["players"], key="sb_p2")
            with ctrl_col3:
                # ⭐ 팀 가르기 탭에서 지정된 맵 리스트가 있다면 최우선 적용, 없다면 마스터 DB 전체 연동
                map_pool = st.session_state.assigned_maps if st.session_state.assigned_maps else (df_maps['map_name'].tolist() if not df_maps.empty else [])
                selected_map = st.selectbox("경기 맵 선택", options=map_pool, key="sb_map")
                
            if st.button("⚔️ 매치 확정 및 대진표 추가", use_container_width=True):
                if p1 and p2 and selected_map:
                    st.session_state.matches.append({"p1": p1, "p2": p2, "map": selected_map})
                    st.rerun()
            st.markdown("<br><hr><br>", unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; letter-spacing: 4px; color: #ffffff !important; font-weight: bold;'>MATCH BOARD</h2>", unsafe_allow_html=True)
        st.write("")
        
        for idx, match in enumerate(list(st.session_state.matches)):
            p1_row = df_players[df_players['name'] == match["p1"]] if not df_players.empty else pd.DataFrame()
            p2_row = df_players[df_players['name'] == match["p2"]] if not df_players.empty else pd.DataFrame()
            map_row = df_maps[df_maps['map_name'] == match["map"]] if not df_maps.empty else pd.DataFrame()
            
            st.markdown(f"""<div style="background-color: #181a20; border: 1px solid #2d3139; border-radius: 12px; padding: 20px; margin-bottom: 20px; position: relative;">""", unsafe_allow_html=True)
            head_col1, head_col2 = st.columns([9, 1])
            with head_col1:
                st.markdown(f"<p style='font-weight: bold; color: #00ffa3 !important; font-size: 1.2rem; margin: 0;'>SET {idx+1}</p>", unsafe_allow_html=True)
            with head_col2:
                if not broadcast_mode:
                    if st.button("X", key=f"del_match_{idx}"):
                        st.session_state.matches.remove(match)
                        st.rerun()
            
            m_col1, m_col2, m_col3 = st.columns([2, 3, 2])
            with m_col1:
                st.markdown(f"<h3 style='text-align: center; color: #ffffff !important; margin-bottom:2px;'>{match['p1']}</h3>", unsafe_allow_html=True)
                img1 = p1_row.iloc[0]['img_url'] if not p1_row.empty else ""
                st.markdown("<div class='match-player-img'>", unsafe_allow_html=True)
                st.image(img1 if img1 else "https://via.placeholder.com/120/181a20/e2e8f0?text=User")
                st.markdown("</div>", unsafe_allow_html=True)
            with m_col2:
                st.markdown("<h2 style='text-align: center; margin-top: 20px; color: #00ffa3 !important; font-weight: bold;'>VS</h2>", unsafe_allow_html=True)
                if not map_row.empty and map_row.iloc[0]['map_url']:
                    st.markdown("<div class='match-map-img'>", unsafe_allow_html=True)
                    st.image(map_row.iloc[0]['map_url'], caption=f"Map: {match['map']}")
                    st.markdown("</div>", unsafe_allow_html=True)
            with m_col3:
                st.markdown(f"<h3 style='text-align: center; color: #ffffff !important; margin-bottom:2px;'>{match['p2']}</h3>", unsafe_allow_html=True)
                img2 = p2_row.iloc[0]['img_url'] if not p2_row.empty else ""
                st.markdown("<div class='match-player-img'>", unsafe_allow_html=True)
                st.image(img2 if img2 else "https://via.placeholder.com/120/181a20/e2e8f0?text=User")
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 🤝 [2번 탭] 실시간 팀 가르기 & 맵 드래프트 보드 (전면 업그레이드 ⭐)
# =========================================================
if not broadcast_mode:
    with tab_draft:
        st.markdown("<div class='draft-panel'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #00ffa3 !important; font-weight: bold;'>🤝 대회 출전 엔트리 팀 & 맵 지명 드래프트 룸</h2>", unsafe_allow_html=True)
        st.write("")
        
        draft_col1, draft_col2 = st.columns([5, 5])
        
        # 👈 왼쪽 구역: 실시간 선수/맵 지정 컨트롤 패널
        with draft_col1:
            st.markdown("#### 1️⃣ 선수 팀 지명 배정")
            if st.session_state.today_entry:
                unassigned_players = [p for p in st.session_state.today_entry 
                                      if p not in st.session_state.teams["Left_Team"]["players"] 
                                      and p not in st.session_state.teams["Right_Team"]["players"]]
                
                if unassigned_players:
                    p_col1, p_col2, p_col3 = st.columns([2, 2, 1])
                    with p_col1:
                        draft_p = st.selectbox("팀 분배할 선수 선택", options=unassigned_players, key="draft_sel_p")
                    with p_col2:
                        team_names_mapping = {
                            st.session_state.teams["Left_Team"]["name"]: "Left_Team",
                            st.session_state.teams["Right_Team"]["name"]: "Right_Team"
                        }
                        selected_team_name = st.selectbox("지명 소속팀 선택", options=list(team_names_mapping.keys()), key="draft_sel_t")
                        draft_t = team_names_mapping[selected_team_name]
                    with p_col3:
                        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                        if st.button("🤝 팀 확정", use_container_width=True):
                            st.session_state.teams[draft_t]["players"].append(draft_p)
                            st.rerun()
                else:
                    st.success("🎉 모든 출전 선수의 팀 분배가 완료되었습니다.")
            else:
                st.warning("⚠️ '⚙️ 데이터 관리' 탭에서 당일 출전 선수를 선택해야 드래프트 보드에 연동됩니다.")
                
            st.markdown("<hr>", unsafe_allow_html=True)
            
            st.markdown("#### 2️⃣ 세트별 경기 사용 맵 추가")
            if not df_maps.empty:
                m_col1, m_col2 = st.columns([3, 1])
                with m_col1:
                    draft_map_choice = st.selectbox("대회에 사용할 공식 맵 선택", options=df_maps['map_name'].tolist(), key="draft_sel_m")
                with m_col2:
                    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                    if st.button("🗺️ 맵 지정", use_container_width=True):
                        st.session_state.assigned_maps.append(draft_map_choice)
                        st.rerun()
            else:
                st.warning("구글 시트에 맵 정보가 없습니다.")

        # 👉 오른쪽 구역: 실시간 배정 현황판 및 수정용 X 취소 버튼 기능 (실시간 수정 시스템)
        with draft_col2:
            st.markdown("#### 📊 실시간 드래프트 현황 (오류 발생 시 X 버튼으로 즉시 수정)")
            
            # 좌측 팀 명단 관리 및 수정
            st.markdown(f"**🟢 {st.session_state.teams['Left_Team']['name']} 스quad:**")
            if st.session_state.teams["Left_Team"]["players"]:
                for p in list(st.session_state.teams["Left_Team"]["players"]):
                    st.markdown(f"<div class='del-btn' style='display:inline-block; margin-right:10px; margin-bottom:5px;'>", unsafe_allow_html=True)
                    m_c1, m_c2 = st.columns([4, 1])
                    m_c1.markdown(f"👤 {p}")
                    if m_c2.button("X", key=f"rev_L_{p}"):
                        st.session_state.teams["Left_Team"]["players"].remove(p)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.caption("지명된 선수가 없습니다.")
                
            # 우측 팀 명단 관리 및 수정
            st.markdown(f"**🔴 {st.session_state.teams['Right_Team']['name']} 스quad:**")
            if st.session_state.teams["Right_Team"]["players"]:
                for p in list(st.session_state.teams["Right_Team"]["players"]):
                    st.markdown(f"<div class='del-btn' style='display:inline-block; margin-right:10px; margin-bottom:5px;'>", unsafe_allow_html=True)
                    m_c1, m_c2 = st.columns([4, 1])
                    m_c1.markdown(f"👤 {p}")
                    if m_c2.button("X", key=f"rev_R_{p}"):
                        st.session_state.teams["Right_Team"]["players"].remove(p)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.caption("지명된 선수가 없습니다.")
                
            st.markdown("<hr style='border-style:dashed;'>", unsafe_allow_html=True)
            
            # 지정된 맵 순서 관리 및 수정
            st.markdown("**🗺️ 지정된 세트별 맵 순서:**")
            if st.session_state.assigned_maps:
                for idx, m_name in enumerate(list(st.session_state.assigned_maps)):
                    st.markdown(f"<div class='del-btn'>", unsafe_allow_html=True)
                    m_c1, m_c2 = st.columns([4, 1])
                    m_c1.markdown(f"**SET {idx+1}**: {m_name}")
                    if m_c2.button("X", key=f"rev_M_{idx}_{m_name}"):
                        st.session_state.assigned_maps.pop(idx)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.caption("순서대로 맵을 지정해 주세요. 지정된 맵이 1순위 대진 선택지로 연동됩니다.")
                
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# ⚙️ [3번 탭] 대회 데이터 관리
# =========================================================
if not broadcast_mode:
    with tab_admin:
        st.markdown("### ⚙️ 구글 스프레드시트 실시간 데이터 연동 상태")
        st.info("💡 구글 시트의 데이터가 실시간으로 매칭되어 노출됩니다.")
        
        adm_col1, adm_col2 = st.columns(2)
        
        with adm_col1:
            with st.container(border=True):
                st.subheader("🚩 팀명 커스텀 수정")
                st.session_state.teams["Left_Team"]["name"] = st.text_input("좌측 팀명", st.session_state.teams["Left_Team"]["name"])
                st.session_state.teams["Right_Team"]["name"] = st.text_input("우측 팀명", st.session_state.teams["Right_Team"]["name"])
            
            with st.container(border=True):
                st.subheader("🗺️ 연동된 공식 맵 리스트")
                if not df_maps.empty:
                    st.dataframe(df_maps, use_container_width=True)
                else:
                    st.caption("맵 데이터가 비어있습니다.")

        with adm_col2:
            with st.container(border=True):
                st.subheader("📅 당일 엔트리 선수 체크 확정")
                if not df_players.empty:
                    updated_entry = []
                    for name in df_players['name'].tolist():
                        is_checked = name in st.session_state.today_entry
                        if st.checkbox(name, value=is_checked, key=f"entry_{name}"):
                            updated_entry.append(name)
                    
                    if st.button("📅 당일 출전 엔트리 확정 저장"):
                        st.session_state.today_entry = updated_entry
                        st.success("엔트리가 저장되었습니다!")
                        st.rerun()
                else:
                    st.warning("구글 시트에 선수를 먼저 등록해 주세요.")

# =========================================================
# 📜 [맨 하단] 저작권 표기 구역
# =========================================================
st.markdown("<p class='copyright-text'>해당 포멧의 저작권은 스진동에 있습니다.</p>", unsafe_allow_html=True)
