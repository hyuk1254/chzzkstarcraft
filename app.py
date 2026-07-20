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

# 실시간 매치 데이터 조율을 위한 임시 세션 연동
if "matches" not in st.session_state:
    st.session_state.matches = []
if "teams" not in st.session_state:
    st.session_state.teams = {
        "Left_Team": {"name": "좌측", "players": []},
        "Right_Team": {"name": "우측", "players": []}
    }
if "today_entry" not in st.session_state:
    st.session_state.today_entry = []

# --- 🎨 치지직 오피셜 컬러 커스텀 스타일 ---
st.markdown("""
<style>
    /* 치지직 다크 모드 배경 및 기본 텍스트 색상 */
    .stApp { background-color: #0c0d10; color: #e2e8f0; }
    
    /* 타이틀 그라데이션: 화이트에서 치지직 연두색(#00ffa3)으로 */
    .main-title {
        text-align: center; font-size: 3rem !important; font-weight: 900 !important;
        color: #ffffff; letter-spacing: 2px; margin-bottom: 5px;
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
    
    /* 추가 정보 태그: 연두색 포인트 border 처리 */
    .extra-info {
        font-size: 0.8rem; color: #00ffa3; background-color: #0c0d10;
        padding: 2px 8px; border-radius: 4px; margin-top: 6px; 
        display: inline-block; border: 1px solid rgba(0, 255, 163, 0.2);
    }
    
    /* 스트림릿 기본 버튼 스타일 커스텀 */
    .stButton > button {
        padding: 3px 10px !important; font-size: 0.85rem !important;
        line-height: 1.5 !important; border-radius: 6px !important;
        background-color: #1c1e26 !important; color: #e2e8f0 !important;
        border: 1px solid #2d3139 !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #00ffa3 !important; color: #00ffa3 !important;
        box-shadow: 0 0 8px rgba(0, 255, 163, 0.3);
    }
    
    /* 좌측 상단 구석 탭 메뉴 바 디자인 (치지직 스킨) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        justify-content: flex-start !important; 
        padding-left: 10px;
        border-bottom: 1px solid #2d3139;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px !important; 
        background-color: #181a20;
        border-radius: 6px 6px 0px 0px;
        padding: 6px 14px !important;
        font-size: 0.9rem !important;
        color: #94a3b8;
        border: 1px solid #2d3139;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1c1e26 !important;
        color: #00ffa3 !important; 
        font-weight: bold;
        border-top: 2px solid #00ffa3 !important; 
    }
    
    /* 체크박스 및 라디오 버튼 등 입력 창 초점 컬러 수정 */
    .stCheckbox [data-testid="stCheckboxUserSelectBackdrop"] {
        background-color: #00ffa3 !important;
    }
    
    /* 수평 구분선 */
    hr { border-color: #2d3139 !important; }

    /* 📜 저작권 표기 텍스트 스타일 */
    .copyright-text {
        text-align: center;
        font-size: 0.75rem;
        color: #555b66;
        margin-top: 50px;
        margin-bottom: 20px;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 🎬 [사이드바] 스크린 제어 ---
with st.sidebar:
    st.header("🎬 스크린 제어")
    broadcast_mode = st.checkbox("📺 방송 송출 모드 (UI 전체 숨기기)", value=False)
    if broadcast_mode:
        st.info("🔄 실시간 송출 동기화 활성화 중...")
        time.sleep(2)
        st.rerun()

st.markdown("<h1 class='main-title'>스진동 종족최강전</h1>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

# 🗂️ 3단 탭 구조 정의
if not broadcast_mode:
    tab_main, tab_draft, tab_admin = st.tabs(["🏆 메인 대시보드", "🤝 팀 가르기", "⚙️ 데이터 관리"])
else:
    tab_main = st.container()

# =========================================================
# 🏆 [1번 탭] 메인 경기 대시보드 화면
# =========================================================
with tab_main:
    main_col1, main_col2, main_col3 = st.columns([2.5, 5, 2.5])

    # 👈 좌측 팀 명단
    with main_col1:
        left_team_data = st.session_state.teams["Left_Team"]
        st.markdown(f"<h2 style='color: #00ffa3; text-align: center;'>{left_team_data['name']}</h2>", unsafe_allow_html=True)
        st.write("")
        
        for p_name in list(left_team_data["players"]):
            p_row = df_players[df_players['name'] == p_name] if not df_players.empty else pd.DataFrame()
            race = p_row.iloc[0]['race'] if not p_row.empty else "Terran"
            img = p_row.iloc[0]['img_url'] if not p_row.empty else ""
            race_emoji = "🔵" if race == "Terran" else "🔴" if race == "Zerg" else "🟡"
            
            with st.container():
                st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
                p_cols = st.columns([1.2, 2.2, 0.6] if not broadcast_mode else [1.2, 2.8])
                with p_cols[0]:
                    st.image(img if img else "https://via.placeholder.com/60/181a20/e2e8f0?text=User", width=60)
                with p_cols[1]:
                    st.markdown(f"<p style='margin-bottom:2px; font-size:1.1rem;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#94a3b8; font-size:0.9rem;'>{race_emoji} {race}</span>", unsafe_allow_html=True)
                    
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
        st.markdown(f"<h2 style='color: #00ffa3; text-align: center;'>{right_team_data['name']}</h2>", unsafe_allow_html=True)
        st.write("")
        
        for p_name in list(right_team_data["players"]):
            p_row = df_players[df_players['name'] == p_name] if not df_players.empty else pd.DataFrame()
            race = p_row.iloc[0]['race'] if not p_row.empty else "Terran"
            img = p_row.iloc[0]['img_url'] if not p_row.empty else ""
            race_emoji = "🔵" if race == "Terran" else "🔴" if race == "Zerg" else "🟡"
            
            with st.container():
                st.markdown(f"<div class='player-card'>", unsafe_allow_html=True)
                p_cols = st.columns([1.2, 2.2, 0.6] if not broadcast_mode else [1.2, 2.8])
                with p_cols[0]:
                    st.image(img if img else "https://via.placeholder.com/60/181a20/e2e8f0?text=User", width=60)
                with p_cols[1]:
                    st.markdown(f"<p style='margin-bottom:2px; font-size:1.1rem;'><b>{p_name}</b></p>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#94a3b8; font-size:0.9rem;'>{race_emoji} {race}</span>", unsafe_allow_html=True)
                    
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
            st.markdown("<h3 style='text-align: center; color:#00ffa3; margin-bottom: 15px;'>📝 실시간 대진 지명</h3>", unsafe_allow_html=True)
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
            with ctrl_col1:
                p1 = st.selectbox(f"{left_team_data['name']} 선택", options=left_team_data["players"], key="sb_p1")
            with ctrl_col2:
                p2 = st.selectbox(f"{right_team_data['name']} 선택", options=right_team_data["players"], key="sb_p2")
            with ctrl_col3:
                selected_map = st.selectbox("경기 맵 선택", options=df_maps['map_name'].tolist() if not df_maps.empty else [], key="sb_map")
                
            if st.button("⚔️ 매치 확정 및 대진표 추가", use_container_width=True):
                if p1 and p2 and selected_map:
                    st.session_state.matches.append({"p1": p1, "p2": p2, "map": selected_map})
                    st.rerun()
            st.markdown("<br><hr><br>", unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center; letter-spacing: 4px; color: #ffffff;'>MATCH BOARD</h2>", unsafe_allow_html=True)
        st.write("")
        
        for idx, match in enumerate(list(st.session_state.matches)):
            p1_row = df_players[df_players['name'] == match["p1"]] if not df_players.empty else pd.DataFrame()
            p2_row = df_players[df_players['name'] == match["p2"]] if not df_players.empty else pd.DataFrame()
            map_row = df_maps[df_maps['map_name'] == match["map"]] if not df_maps.empty else pd.DataFrame()
            
            st.markdown(f"""<div style="background-color: #181a20; border: 1px solid #2d3139; border-radius: 12px; padding: 20px; margin-bottom: 20px; position: relative;">""", unsafe_allow_html=True)
            head_col1, head_col2 = st.columns([9, 1])
            with head_col1:
                st.markdown(f"<p style='font-weight: bold; color: #00ffa3; font-size: 1.2rem; margin: 0;'>SET {idx+1}</p>", unsafe_allow_html=True)
            with head_col2:
                if not broadcast_mode:
                    if st.button("X", key=f"del_match_{idx}"):
                        st.session_state.matches.remove(match)
                        st.rerun()
            
            m_col1, m_col2, m_col3 = st.columns([2, 3, 2])
            with m_col1:
                st.markdown(f"<h3 style='text-align: center; color: #ffffff; margin-bottom:2px;'>{match['p1']}</h3>", unsafe_allow_html=True)
                img1 = p1_row.iloc[0]['img_url'] if not p1_row.empty else ""
                st.image(img1 if img1 else "https://via.placeholder.com/60/181a20/e2e8f0?text=User", use_container_width=True)
            with m_col2:
                st.markdown("<h2 style='text-align: center; margin-top: 20px; color: #00ffa3;'>VS</h2>", unsafe_allow_html=True)
                if not map_row.empty and map_row.iloc[0]['map_url']:
                    st.image(map_row.iloc[0]['map_url'], caption=f"Map: {match['map']}", use_container_width=True)
            with m_col3:
                st.markdown(f"<h3 style='text-align: center; color: #ffffff; margin-bottom:2px;'>{match['p2']}</h3>", unsafe_allow_html=True)
                img2 = p2_row.iloc[0]['img_url'] if not p2_row.empty else ""
                st.image(img2 if img2 else "https://via.placeholder.com/60/181a20/e2e8f0?text=User", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 🤝 [2번 탭] 실시간 팀 가르기
# =========================================================
if not broadcast_mode:
    with tab_draft:
        st.markdown("<div class='draft-panel'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #00ffa3;'>🤝 당일 출전 선수 팀 드래프트 보드</h2>", unsafe_allow_html=True)
        st.write("")
        
        if st.session_state.today_entry:
            unassigned_players = [p for p in st.session_state.today_entry 
                                  if p not in st.session_state.teams["Left_Team"]["players"] 
                                  and p not in st.session_state.teams["Right_Team"]["players"]]
            
            if unassigned_players:
                df_col1, df_col2, df_col3 = st.columns([2, 2, 1])
                with df_col1:
                    draft_p = st.selectbox("팀을 나눌 선수 선택", options=unassigned_players, key="draft_p")
                with df_col2:
                    team_options = {
                        st.session_state.teams["Left_Team"]["name"]: "Left_Team",
                        st.session_state.teams["Right_Team"]["name"]: "Right_Team"
                    }
                    selected_team_name = st.selectbox("지명할 팀 선택", options=list(team_options.keys()), key="draft_t")
                    draft_t = team_options[selected_team_name]
                with df_col3:
                    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                    if st.button("🤝 선택 선수 팀 배치 확정", use_container_width=True):
                        st.session_state.teams[draft_t]["players"].append(draft_p)
                        st.rerun()
            else:
                st.success("🎉 당일 출전하는 모든 선수의 팀 분배가 완료되었습니다!")
        else:
            st.warning("⚠️ '⚙️ 데이터 관리' 탭에서 오늘 출전할 선수를 먼저 체크해 주세요.")
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
streamlit
pandas
