import streamlit as st

# 페이지 설정
st.set_page_config(layout="wide", page_title="스타크래프트 대회 대시보드")

# --- 🎨 사이트 전체 커스텀 스타일 ---
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .main-title {
        text-align: center; 
        font-size: 3rem !important; 
        font-weight: 900 !important;
        color: #ffffff; 
        letter-spacing: 2px;
        margin-bottom: 5px;
        background: linear-gradient(to right, #ffffff, #76deff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .player-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .draft-panel {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 25px;
        margin-top: 10px;
    }
    .stButton > button {
        padding: 2px 8px !important;
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
        border-radius: 4px !important;
    }
    /* 탭 스타일 조정 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #161b22;
        border-radius: 5px 5px 0px 0px;
        padding: 10px 20px;
        color: #c9d1d9;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #76deff !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 세션 상태 초기화 ---
if "title_type" not in st.session_state:
    st.session_state.title_type = "텍스트 입력"
if "title_text" not in st.session_state:
    st.session_state.title_text = "스진동 종족최강전"
if "all_players" not in st.session_state:
    st.session_state.all_players = {}
if "today_entry" not in st.session_state:
    st.session_state.today_entry = [] 
if "teams" not in st.session_state:
    st.session_state.teams = {
        "Left_Team": {"name": "좌측", "players": []},
        "Right_Team": {"name": "우측", "players": []}
    }
if "maps" not in st.session_state:
    st.session_state.maps = {}
if "matches" not in st.session_state:
    st.session_state.matches = []

# --- 🎬 [사이드바] 스크린 제어 ---
with st.sidebar:
    st.header("🎬 스크린 제어")
    broadcast_mode = st.checkbox("📺 방송 송출 모드 (UI 전체 숨기기)", value=False)
    if broadcast_mode:
        st.info("💡 모든 관리 탭과 입력 조작창이 숨겨졌습니다. 메인 화면만 크롭하여 OBS에 올리세요.")

# --- 👑 [메인 상단] 타이틀 구역 ---
if st.session_state.title_type == "이미지 업로드" and st.session_state.get("title_img") is not None:
    title_col1, title_col2, title_col3 = st.columns([1, 3, 1])
    with title_col2:
        st.image(st.session_state.title_img, use_container_width=True)
else:
    st.markdown(f"<h1 class='main-title'>{st.session_state.title_text}</h1>", unsafe_allow_html=True)

st.markdown("<hr style='border-color: #30363d; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)


# =========================================================
# 🗂️ 3단 탭 구조 정의 (송출 모드일 때는 대진표만 노출)
# =========================================================
if not broadcast_mode:
    tab_main, tab_draft, tab_admin = st.tabs(["🏆 메인 경기 대시보드", "🤝 실시간 팀 가르기", "⚙️ 대회 데이터 관리"])
else:
    tab_main = st.container()

# =========================================================
# 🏆 [1번 탭] 메인 경기 대시보드 화면
# =========================================================
with tab_main:
    # 하단 3분할 경기 진행 레이아웃
    main_col1, main_col2, main_col3 = st.columns([2.5, 5, 2.5])

    # 👈 좌측 팀 명단
    with main_col1:
        left_team_data = st.session_state.teams["Left_Team"]
        st.markdown(f"<h2 style='color: #4facfe; text-align: center;'>{left_team_data['name']}</h2>", unsafe_allow_html=True)
        st.write("")
        
        if not left_team_data["players"]:
            st.info("선수가 없습니다.")
        
        for p_name in list(left_team_data["players"]):
            p_info = st.session_state.all_players.get(p_name)
            if p_info:
                race_emoji = "🔵" if p_info["race"] == "Terran" else "🔴" if p_info["race"] == "Zerg" else "🟡"
                with st.container():
                    st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
                    col_size = [1.2, 2.2, 0.6] if not broadcast_mode else [1.2, 2.8]
                    p_cols = st.columns(col_size)
                    with p_cols[0]:
                        st.image(p_info["img"] if p_info["img"] else "https://via.placeholder.com/60/161b22/c9d1d9?text=No+Image", width=60)
                    with p_cols[1]:
                        st.markdown(f"<p style='margin-bottom:2px; font-size:1.1rem;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                        st.markdown(f"<span style='color:#8b949e; font-size:0.9rem;'>{race_emoji} {p_info['race']}</span>", unsafe_allow_html=True)
                    if not broadcast_mode:
                        with p_cols[2]:
                            if st.button("X", key=f"del_L_{p_name}"):
                                left_team_data["players"].remove(p_name)
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # 👉 우측 팀 명단
    with main_col3:
        right_team_data = st.session_state.teams["Right_Team"]
        st.markdown(f"<h2 style='color: #ff0844; text-align: center;'>{right_team_data['name']}</h2>", unsafe_allow_html=True)
        st.write("")
        
        if not right_team_data["players"]:
            st.info("선수가 없습니다.")
            
        for p_name in list(right_team_data["players"]):
            p_info = st.session_state.all_players.get(p_name)
            if p_info:
                race_emoji = "🔵" if p_info["race"] == "Terran" else "🔴" if p_info["race"] == "Zerg" else "🟡"
                with st.container():
                    st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
                    col_size = [1.2, 2.2, 0.6] if not broadcast_mode else [1.2, 2.8]
                    p_cols = st.columns(col_size)
                    with p_cols[0]:
                        st.image(p_info["img"] if p_info["img"] else "https://via.placeholder.com/60/161b22/c9d1d9?text=No+Image", width=60)
                    with p_cols[1]:
                        st.markdown(f"<p style='margin-bottom:2px; font-size:1.1rem;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                        st.markdown(f"<span style='color:#8b949e; font-size:0.9rem;'>{race_emoji} {p_info['race']}</span>", unsafe_allow_html=True)
                    if not broadcast_mode:
                        with p_cols[2]:
                            if st.button("X", key=f"del_R_{p_name}"):
                                right_team_data["players"].remove(p_name)
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # ⚔️ 중앙 실시간 대진 지명 및 MATCH BOARD
    with main_col2:
        if not broadcast_mode:
            st.markdown("<h3 style='text-align: center; color:#ffb199; margin-bottom: 15px;'>📝 실시간 대진 지명</h3>", unsafe_allow_html=True)
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
            with ctrl_col1:
                p1 = st.selectbox(f"{left_team_data['name']} 선택", options=left_team_data["players"], key="sb_p1")
            with ctrl_col2:
                p2 = st.selectbox(f"{right_team_data['name']} 선택", options=right_team_data["players"], key="sb_p2")
            with ctrl_col3:
                selected_map = st.selectbox("경기 맵 선택", options=list(st.session_state.maps.keys()), key="sb_map")
                
            if st.button("⚔️ 매치 확정 및 대진표 추가", use_container_width=True):
                if p1 and p2 and selected_map:
                    st.session_state.matches.append({"p1": p1, "p2": p2, "map": selected_map})
                    st.rerun()
            st.markdown("<br><hr style='border-color: #30363d;'><br>", unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; letter-spacing: 4px; color: #ffffff;'>MATCH BOARD</h2>", unsafe_allow_html=True)
        st.write("")
        
        if not st.session_state.matches:
            st.markdown("<p style='text-align: center; color: #8b949e; font-style: italic; margin-top: 20px;'>성사된 매치가 없습니다. 선수 배치 후 대진을 지명해 주세요.</p>", unsafe_allow_html=True)
            
        for idx, match in enumerate(list(st.session_state.matches)):
            p1_info = st.session_state.all_players.get(match["p1"])
            p2_info = st.session_state.all_players.get(match["p2"])
            map_img = st.session_state.maps.get(match["map"])
            
            if p1_info and p2_info:
                st.markdown(f"""<div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; position: relative;">""", unsafe_allow_html=True)
                head_col1, head_col2 = st.columns([9, 1])
                with head_col1:
                    st.markdown(f"<p style='font-weight: bold; color: #ff9f43; font-size: 1.2rem; margin: 0;'>SET {idx+1}</p>", unsafe_allow_html=True)
                with head_col2:
                    if not broadcast_mode:
                        if st.button("X", key=f"del_match_{idx}"):
                            st.session_state.matches.remove(match)
                            st.rerun()
                
                m_col1, m_col2, m_col3 = st.columns([2, 3, 2])
                with m_col1:
                    st.markdown(f"<h3 style='text-align: center; color: #4facfe; margin-bottom:2px;'>{match['p1']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; color: #8b949e; font-size:0.9rem;'>{p1_info['race']}</p>", unsafe_allow_html=True)
                    if p1_info["img"]: st.image(p1_info["img"], use_container_width=True)
                with m_col2:
                    st.markdown("<h2 style='text-align: center; margin-top: 20px; color: #ff0844;'>VS</h2>", unsafe_allow_html=True)
                    if map_img: st.image(map_img, caption=f"Map: {match['map']}", use_container_width=True)
                with m_col3:
                    st.markdown(f"<h3 style='text-align: center; color: #ff0844; margin-bottom:2px;'>{match['p2']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; color: #8b949e; font-size:0.9rem;'>{p2_info['race']}</p>", unsafe_allow_html=True)
                    if p2_info["img"]: st.image(p2_info["img"], use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 🤝 [2번 탭] 실시간 팀 가르기 (독립된 탭으로 구성)
# =========================================================
if not broadcast_mode:
    with tab_draft:
        st.markdown("<div class='draft-panel'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #76deff;'>🤝 당일 출전 선수 팀 드래프트 보드</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #8b949e;'>당일 확정된 엔트리 선수들을 각 팀으로 분배하는 조작실입니다.</p>", unsafe_allow_html=True)
        st.write("")
        
        if st.session_state.today_entry:
            unassigned_players = [p for p in st.session_state.today_entry 
                                  if p not in st.session_state.teams["Left_Team"]["players"] 
                                  and p not in st.session_state.teams["Right_Team"]["players"]]
            
            if unassigned_players:
                df_col1, df_col2, df_col3 = st.columns([2, 2, 1])
                with df_col1:
                    draft_p = st.selectbox("팀을 나눌 선수 선택", options=unassigned_players, key="draft_selectbox_p")
                with df_col2:
                    team_options = {
                        st.session_state.teams["Left_Team"]["name"]: "Left_Team",
                        st.session_state.teams["Right_Team"]["name"]: "Right_Team"
                    }
                    selected_team_name = st.selectbox("지명할 팀 선택", options=list(team_options.keys()), key="draft_selectbox_t")
                    draft_t = team_options[selected_team_name]
                with df_col3:
                    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                    if st.button("🤝 선택 선수 팀 배치 확정", use_container_width=True):
                        st.session_state.teams[draft_t]["players"].append(draft_p)
                        st.success(f"{draft_p} 선수가 '{selected_team_name}'에 합류했습니다!")
                        st.rerun()
            else:
                st.success("🎉 오늘 출전하는 모든 선수의 팀 드래프트 분배가 끝났습니다! 메인 대시보드 탭에서 경기를 조율하세요.")
                
            st.markdown("---")
            st.markdown("#### 📢 현재 실시간 팀 배정 현황")
            
            entry_status = []
            for p in st.session_state.today_entry:
                if p in st.session_state.teams["Left_Team"]["players"]:
                    entry_status.append(f"<span style='color:#4facfe; font-weight:bold;'>{p}({st.session_state.teams['Left_Team']['name']})</span>")
                elif p in st.session_state.teams["Right_Team"]["players"]:
                    entry_status.append(f"<span style='color:#ff0844; font-weight:bold;'>{p}({st.session_state.teams['Right_Team']['name']})</span>")
                else:
                    entry_status.append(f"<span style='color:#ffffff;'>{p}(미배정)</span>")
            st.markdown(" / ".join(entry_status), unsafe_allow_html=True)
        else:
            st.warning("⚠️ 아직 오늘 출전 엔트리가 확정되지 않았습니다. '⚙️ 대회 데이터 관리' 탭에서 당일 출전 선수를 체크해 주세요.")
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# ⚙️ [3번 탭] 대회 데이터 관리 화면
# =========================================================
if not broadcast_mode:
    with tab_admin:
        st.markdown("### ⚙️ 대회 데이터 설정 백오피스")
        st.caption("선수 풀 등록, 당일 출전 체크, 팀명 및 타이틀 변경, 맵 관리 등의 사전 작업을 수행하는 전용 공간입니다.")
        st.write("")
        
        adm_col1, adm_col2 = st.columns(2)
        
        with adm_col1:
            # 1. 타이틀 & 팀명 설정
            with st.container(border=True):
                st.subheader("👑 대회 타이틀 및 팀명 변경")
                st.session_state.title_type = st.radio("타이틀 형태 선택", ["텍스트 입력", "이미지 업로드"], key="rb_title_type")
                if st.session_state.title_type == "텍스트 입력":
                    st.session_state.title_text = st.text_input("대회 이름 입력", st.session_state.title_text, key="ti_title_text")
                else:
                    st.session_state.title_img = st.file_uploader("타이틀 로고 이미지 업로드", type=["jpg", "png", "jpeg"], key="fu_title_img")
                
                st.markdown("---")
                st.session_state.teams["Left_Team"]["name"] = st.text_input("좌측 팀명 수정", st.session_state.teams["Left_Team"]["name"], key="ti_t_left")
                st.session_state.teams["Right_Team"]["name"] = st.text_input("우측 팀명 수정", st.session_state.teams["Right_Team"]["name"], key="ti_t_right")

            # 2. 맵 등록
            with st.container(border=True):
                st.subheader("🗺️ 대회 공식 맵 등록")
                m_name = st.text_input("맵 이름", key="ti_m_name")
                m_img = st.file_uploader("맵 이미지 업로드", type=["jpg", "png", "jpeg"], key="map_img")
                if st.button("🗺️ 시스템 맵 추가") and m_name:
                    st.session_state.maps[m_name] = m_img
                    st.success(f"'{m_name}' 맵 등록 완료!")
                    st.rerun()

        with adm_col2:
            # 3. 선수 마스터 DB 등록
            with st.container(border=True):
                st.subheader("👤 전체 선수 Pool 데이터 등록")
                p_name = st.text_input("선수 이름 입력", key="ti_p_name")
                p_race = st.selectbox("종족 선택", ["Terran", "Zerg", "Protoss"], key="sb_p_race")
                p_img = st.file_uploader("선수 사진 업로드", type=["jpg", "png", "jpeg"], key="player_img")
                
                if st.button("👤 마스터 DB에 선수 추가") and p_name:
                    st.session_state.all_players[p_name] = {"race": p_race, "img": p_img}
                    st.success(f"선수 DB에 '{p_name}' 등록 완료!")
                    st.rerun()

            # 4. 당일 출전 엔트리 셀렉터
            with st.container(border=True):
                st.subheader("📅 대회 당일 출전 엔트리 확정")
                if st.session_state.all_players:
                    st.markdown("<small>오늘 경기를 치를 선수를 선택하세요.</small>", unsafe_allow_html=True)
                    updated_entry = []
                    for name in st.session_state.all_players.keys():
                        is_checked = name in st.session_state.today_entry
                        if st.checkbox(name, value=is_checked, key=f"entry_{name}"):
                            updated_entry.append(name)
                    st.session_state.today_entry = updated_entry
                else:
                    st.info("등록된 선수가 없습니다. 왼쪽 창에서 선수를 먼저 등록해 주세요.")