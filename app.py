import streamlit as st
import pandas as pd
import time
import json
import os

# 페이지 설정
st.set_page_config(layout="wide", page_title="스타크래프트 대회 대시보드")

# =========================================================
# 🔗 [연동 완료] 질문자님의 구글 스프레드시트 주소를 적용했습니다!
# =========================================================
SHEET_URL = "https://docs.google.com/spreadsheets/d/1eA1GCEga0FcpmPMO8Qm8nXoZOPeQioAaBgXZs-NDyCc/edit?usp=sharing"

# 구글 시트 ID 추출
try:
    SHEET_ID = SHEET_URL.split("/d/")[1].split("/")[0]
except:
    SHEET_ID = ""

# --- 📁 구글 시트 기반 영구 동기화 백엔드 시스템 ---
@st.cache_data(ttl=1) # 1초마다 최신 데이터 로드
def fetch_sheet_data(sheet_name):
    try:
        csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        df = pd.read_csv(csv_url)
        return df.fillna("")
    except:
        return pd.DataFrame()

# 마스터 선수/맵 DB 로드
df_players = fetch_sheet_data("players")
df_maps = fetch_sheet_data("maps")

# 구글 시트에 실시간 대회 진행 상황을 영구 저장하는 함수
def save_tournament_status():
    status_data = {
        "matches": st.session_state.matches,
        "teams": st.session_state.teams,
        "today_entry": st.session_state.today_entry,
        "assigned_maps": st.session_state.assigned_maps,
        "title_type": st.session_state.title_type,
        "title_text": st.session_state.title_text,
        "active_maps": st.session_state.get("active_maps", [])
    }
    with open("local_backup_status.json", "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=4)

def load_tournament_status():
    if os.path.exists("local_backup_status.json"):
        try:
            with open("local_backup_status.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

# 실시간 대회 데이터 영구 세션 초기화 및 로드
backup = load_tournament_status()
if backup and "matches" not in st.session_state:
    st.session_state.matches = backup.get("matches", [])
    st.session_state.teams = backup.get("teams", {"Left_Team": {"name": "좌측", "players": []}, "Right_Team": {"name": "우측", "players": []}})
    st.session_state.today_entry = backup.get("today_entry", [])
    st.session_state.assigned_maps = backup.get("assigned_maps", [])
    st.session_state.title_type = backup.get("title_type", "텍스트 입력")
    st.session_state.title_text = backup.get("title_text", "스진동 종족최강전")
    st.session_state.active_maps = backup.get("active_maps", [])
else:
    if "matches" not in st.session_state: st.session_state.matches = []
    if "teams" not in st.session_state: st.session_state.teams = {"Left_Team": {"name": "좌측", "players": []}, "Right_Team": {"name": "우측", "players": []}}
    if "today_entry" not in st.session_state: st.session_state.today_entry = []
    if "assigned_maps" not in st.session_state: st.session_state.assigned_maps = []
    if "title_type" not in st.session_state: st.session_state.title_type = "텍스트 입력"
    if "title_text" not in st.session_state: st.session_state.title_text = "스진동 종족최강전"
    if "active_maps" not in st.session_state: st.session_state.active_maps = []

if "title_img" not in st.session_state:
    st.session_state.title_img = None

# 🎨 종족 마크 커스텀 세팅 구역
RACE_ICONS = {
    "테란": "https://via.placeholder.com/20/00ffa3/ffffff?text=T",  # 👈 여기에 자체 제작하신 테란 마크 주소 삽입
    "저그": "https://via.placeholder.com/20/00ffa3/ffffff?text=Z",  # 👈 여기에 자체 제작하신 저그 마크 주소 삽입
    "프로토스": "https://via.placeholder.com/20/00ffa3/ffffff?text=P", # 👈 여기에 자체 제작하신 프로토스 마크 주소 삽입
}

# --- 🎨 치지직 오피셜 컬러 및 이미지 크롭 커스텀 스타일 ---
st.markdown("""
<style>
    .stApp { background-color: #0c0d10; color: #e2e8f0; }
    
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp div {
        color: #e2e8f0 !important;
    }
    
    div[data-baseweb="select"] * { color: #ffffff !important; }
    div[data-testid="stSelectbox"] label p { color: #00ffa3 !important; font-weight: bold; }
    ul[role="listbox"] li { background-color: #1c1e26 !important; color: #ffffff !important; }
    ul[role="listbox"] li:hover { background-color: #2d3139 !important; color: #00ffa3 !important; }
    div[data-testid="stRadio"] label p { color: #ffffff !important; }
    .stDataFrame div { color: #ffffff !important; }
    
    .main-title {
        text-align: center; font-size: 3rem !important; font-weight: 900 !important;
        color: #ffffff !important; letter-spacing: 2px; margin-bottom: 5px;
        background: linear-gradient(to right, #ffffff, #00ffa3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .player-card {
        background-color: #181a20; border: 1px solid #2d3139;
        border-radius: 10px; padding: 10px; margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    .draft-panel {
        background-color: #181a20; border: 1px solid #2d3139;
        border-radius: 12px; padding: 25px; margin-top: 10px;
    }
    
    .player-list-img img { width: 60px !important; height: 60px !important; object-fit: cover !important; border-radius: 6px !important; }
    .match-player-img img { width: 100% !important; max-height: 140px !important; object-fit: cover !important; border-radius: 8px !important; }
    .match-map-img img { max-height: 140px !important; object-fit: contain !important; border-radius: 8px !important; }
    .race-icon-img { display: inline-block; width: 16px; height: 16px; object-fit: contain; vertical-align: middle; margin-right: 4px; }

    .extra-info {
        font-size: 0.8rem; color: #00ffa3 !important; background-color: #0c0d10;
        padding: 2px 8px; border-radius: 4px; margin-top: 6px; 
        display: inline-block; border: 1px solid rgba(0, 255, 163, 0.2);
    }
    .extra-info * { color: #00ffa3 !important; }
    
    .stButton > button {
        padding: 3px 10px !important; font-size: 0.85rem !important;
        line-height: 1.5 !important; border-radius: 6px !important;
        background-color: #1c1e26 !important; color: #e2e8f0 !important;
        border: 1px solid #2d3139 !important; transition: all 0.2s ease;
    }
    .stButton > button:hover { border-color: #00ffa3 !important; color: #00ffa3 !important; box-shadow: 0 0 8px rgba(0, 255, 163, 0.3); }
    .stButton > button * { color: inherit !important; }
    
    .del-btn > div > button {
        padding: 1px 6px !important; font-size: 0.75rem !important;
        background-color: rgba(255, 85, 85, 0.15) !important; color: #ff5555 !important;
        border: 1px solid rgba(255, 85, 85, 0.3) !important;
    }
    .del-btn > div > button:hover { background-color: #ff5555 !important; color: #ffffff !important; box-shadow: 0 0 8px rgba(255, 85, 85, 0.4); }

    .stApp > div:nth-child(1) .stTabs {
        margin-top: -50px !important;
    }
    .stApp > div:nth-child(1) .stTabs [data-baseweb="tab-list"] { 
        gap: 4px; justify-content: flex-start !important; padding-left: 5px; border-bottom: 1px solid #2d3139; margin-bottom: 15px; 
    }
    .stApp > div:nth-child(1) .stTabs [data-baseweb="tab"] {
        height: 32px !important; background-color: #14161d; border-radius: 4px 4px 0px 0px;
        padding: 4px 12px !important; font-size: 0.85rem !important; color: #64748b !important;
        border: 1px solid #2d3139; border-bottom: none;
    }
    .stApp > div:nth-child(1) .stTabs [aria-selected="true"] { 
        background-color: #1c1e26 !important; color: #00ffa3 !important; font-weight: bold; border-top: 2px solid #00ffa3 !important; 
    }
    
    .sub-tabs {
        margin-top: 10px !important;
        padding-top: 5px !important;
    }
    .sub-tabs [data-baseweb="tab-list"] { 
        margin-top: 0px !important; 
        border-bottom: 1px solid #2d3139 !important; 
        justify-content: flex-start !important;
        gap: 10px !important;
    }
    .sub-tabs [data-baseweb="tab"] { 
        background-color: #0c0d10 !important; 
        border: none !important; 
        color: #94a3b8 !important; 
        height: auto !important;
        padding: 8px 16px !important;
    }
    .sub-tabs [aria-selected="true"] { 
        color: #00ffa3 !important; 
        border-bottom: 2px solid #00ffa3 !important; 
        border-top: none !important; 
        background-color: transparent !important; 
        font-weight: bold !important;
    }

    .stCheckbox [data-testid="stCheckboxUserSelectBackdrop"] { background-color: #00ffa3 !important; }
    hr { border-color: #2d3139 !important; }
    .copyright-text { text-align: center; font-size: 0.75rem; color: #555b66 !important; margin-top: 50px; margin-bottom: 20px; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)

# 종족 표준 분류 파서 함수
def parse_race(race_text):
    race_text = str(race_text).strip().lower()
    if "테" in race_text or "te" in race_text: return "테란"
    if "저" in race_text or "ze" in race_text: return "저그"
    if "프" in race_text or "pr" in race_text: return "프로토스"
    return "미정"

def get_race_badge_html(race_text):
    norm_race = parse_race(race_text)
    icon_url = RACE_ICONS.get(norm_race)
    if icon_url and norm_race != "미정":
        return f'<img src="{icon_url}" class="race-icon-img"> <span style="color:#94a3b8 !important; font-size:0.9rem; vertical-align:middle;">{norm_race}</span>'
    return f'<span style="color:#94a3b8 !important; font-size:0.9rem; vertical-align:middle;">🟡 {norm_race}</span>'

# --- 🎬 [사이드바] 스크린 제어 ---
with st.sidebar:
    st.header("🎬 스크린 제어")
    broadcast_mode = st.checkbox("📺 방송 송출 모드 (UI 전체 숨기기)", value=False)
    
    st.markdown("---")
    if st.button("🚨 대회 전체 데이터 초기화 (리셋)", use_container_width=True):
        st.session_state.matches = []
        st.session_state.teams = {"Left_Team": {"name": "좌측", "players": []}, "Right_Team": {"name": "우측", "players": []}}
        st.session_state.today_entry = []
        st.session_state.assigned_maps = []
        st.session_state.active_maps = []
        save_tournament_status()
        st.success("초기화 완료!")
        time.sleep(1)
        st.rerun()

    if broadcast_mode:
        st.info("🔄 실시간 송출 동기화 활성화 중...")
        b = load_tournament_status()
        if b:
            st.session_state.matches = b.get("matches", [])
            st.session_state.teams = b.get("teams", st.session_state.teams)
            st.session_state.assigned_maps = b.get("assigned_maps", [])
            st.session_state.title_type = b.get("title_type", "텍스트 입력")
            st.session_state.title_text = b.get("title_text", "스진동 종족최강전")
            st.session_state.active_maps = b.get("active_maps", [])
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
    if st.session_state.title_type == "이미지 업로드" and st.session_state.title_img is not None:
        t_col1, t_col2, t_col3 = st.columns([1.5, 3, 1.5])
        with t_col2: st.image(st.session_state.title_img, use_container_width=True)
    else:
        st.markdown(f"<h1 class='main-title'>{st.session_state.title_text}</h1>", unsafe_allow_html=True)
        
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
                        if extra_info_list: st.markdown(f"<div class='extra-info'>{' | '.join(extra_info_list)}</div>", unsafe_allow_html=True)
                            
                if not broadcast_mode:
                    with p_cols[2]:
                        if st.button("X", key=f"del_L_{p_name}"):
                            left_team_data["players"].remove(p_name)
                            save_tournament_status()
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
                        if extra_info_list: st.markdown(f"<div class='extra-info'>{' | '.join(extra_info_list)}</div>", unsafe_allow_html=True)
                            
                    if not broadcast_mode:
                        with p_cols[2]:
                            if st.button("X", key=f"del_R_{p_name}"):
                                right_team_data["players"].remove(p_name)
                                save_tournament_status()
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # ⚔️ 중앙 실시간 대진 지명 및 MATCH BOARD
    with main_col2:
        if not broadcast_mode:
            st.markdown("<h3 style='text-align: center; color:#00ffa3 !important; font-weight: bold; margin-bottom: 15px;'>📝 실시간 대진 지명</h3>", unsafe_allow_html=True)
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
            with ctrl_col1: p1 = st.selectbox(f"{left_team_data['name']} 선택", options=left_team_data["players"], key="sb_p1")
            with ctrl_col2: p2 = st.selectbox(f"{right_team_data['name']} 선택", options=right_team_data["players"], key="sb_p2")
            with ctrl_col3:
                map_pool = st.session_state.assigned_maps if st.session_state.assigned_maps else (st.session_state.active_maps if st.session_state.active_maps else (df_maps['map_name'].tolist() if not df_maps.empty else []))
                selected_map = st.selectbox("경기 맵 선택", options=map_pool, key="sb_map")
                
            if st.button("⚔️ 매치 확정 및 대진표 추가", use_container_width=True):
                if p1 and p2 and selected_map:
                    st.session_state.matches.append({"p1": p1, "p2": p2, "map": selected_map})
                    save_tournament_status()
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
            with head_col1: st.markdown(f"<p style='font-weight: bold; color: #00ffa3 !important; font-size: 1.2rem; margin: 0;'>SET {idx+1}</p>", unsafe_allow_html=True)
            with head_col2:
                if not broadcast_mode:
                    if st.button("X", key=f"del_match_{idx}"):
                        st.session_state.matches.remove(match)
                        save_tournament_status()
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
# 🤝 [2번 탭] 실시간 팀 가르기
# =========================================================
if not broadcast_mode:
    with tab_draft:
        st.markdown("<div class='draft-panel'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #00ffa3 !important; font-weight: bold;'>🤝 대회 출전 엔트리 팀 & 맵 지명 드래프트 룸</h2>", unsafe_allow_html=True)
        st.write("")
        
        draft_col1, draft_col2 = st.columns([5, 5])
        with draft_col1:
            st.markdown("#### 1️⃣ 선수 팀 지명 배정")
            if st.session_state.today_entry:
                unassigned_players = [p for p in st.session_state.today_entry if p not in st.session_state.teams["Left_Team"]["players"] and p not in st.session_state.teams["Right_Team"]["players"]]
                if unassigned_players:
                    p_col1, p_col2, p_col3 = st.columns([2, 2, 1])
                    with p_col1: draft_p = st.selectbox("팀 분배할 선수 선택", options=unassigned_players, key="draft_sel_p")
                    with p_col2:
                        team_names_mapping = {st.session_state.teams["Left_Team"]["name"]: "Left_Team", st.session_state.teams["Right_Team"]["name"]: "Right_Team"}
                        selected_team_name = st.selectbox("지명 소속팀 선택", options=list(team_names_mapping.keys()), key="draft_sel_t")
                        draft_t = team_names_mapping[selected_team_name]
                    with p_col3:
                        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                        if st.button("🤝 팀 확정", use_container_width=True):
                            st.session_state.teams[draft_t]["players"].append(draft_p)
                            save_tournament_status()
                            st.rerun()
                else: st.success("🎉 모든 출전 선수의 팀 분배가 완료되었습니다.")
            else: st.warning("⚠️ '⚙️ 데이터 관리' 탭에서 당일 출전 선수를 선택해야 드래프트 보드에 연동됩니다.")
                
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("#### 2️⃣ 세트별 경기 사용 맵 추가")
            
            active_map_pool = st.session_state.active_maps if st.session_state.active_maps else (df_maps['map_name'].tolist() if not df_maps.empty else [])
            if active_map_pool:
                m_col1, m_col2 = st.columns([3, 1])
                with m_col1: draft_map_choice = st.selectbox("대회에 사용할 공식 맵 선택", options=active_map_pool, key="draft_sel_m")
                with m_col2:
                    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                    if st.button("🗺️ 맵 지정", use_container_width=True):
                        st.session_state.assigned_maps.append(draft_map_choice)
                        save_tournament_status()
                        st.rerun()
            else:
                st.warning("활성화된 맵이 없습니다. '데이터 관리' 탭에서 사용할 맵을 체크해 주세요.")

        with draft_col2:
            st.markdown("#### 📊 실시간 드래프트 현황")
            st.markdown(f"**🟢 {st.session_state.teams['Left_Team']['name']} 스쿼드:**")
            if st.session_state.teams["Left_Team"]["players"]:
                for p in list(st.session_state.teams["Left_Team"]["players"]):
                    st.markdown(f"<div class='del-btn' style='display:inline-block; margin-right:10px; margin-bottom:5px;'>", unsafe_allow_html=True)
                    m_c1, m_c2 = st.columns([4, 1])
                    m_c1.markdown(f"👤 {p}")
                    if m_c2.button("X", key=f"rev_L_{p}"):
                        st.session_state.teams["Left_Team"]["players"].remove(p)
                        save_tournament_status()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else: st.caption("지명된 선수가 없습니다.")
                
            st.markdown(f"**🔴 {st.session_state.teams['Right_Team']['name']} 스쿼드:**")
            if st.session_state.teams["Right_Team"]["players"]:
                for p in list(st.session_state.teams["Right_Team"]["players"]):
                    st.markdown(f"<div class='del-btn' style='display:inline-block; margin-right:10px; margin-bottom:5px;'>", unsafe_allow_html=True)
                    m_c1, m_c2 = st.columns([4, 1])
                    m_c1.markdown(f"👤 {p}")
                    if m_c2.button("X", key=f"rev_R_{p}"):
                        st.session_state.teams["Right_Team"]["players"].remove(p)
                        save_tournament_status()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else: st.caption("지명된 선수가 없습니다.")
                
            st.markdown("<hr style='border-style:dashed;'>", unsafe_allow_html=True)
            st.markdown("**🗺️ 지정된 세트별 맵 순서:**")
            if st.session_state.assigned_maps:
                for idx, m_name in enumerate(list(st.session_state.assigned_maps)):
                    st.markdown(f"<div class='del-btn'>", unsafe_allow_html=True)
                    m_c1, m_c2 = st.columns([4, 1])
                    m_c1.markdown(f"**SET {idx+1}**: {m_name}")
                    if m_c2.button("X", key=f"rev_M_{idx}_{m_name}"):
                        st.session_state.assigned_maps.pop(idx)
                        save_tournament_status()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else: st.caption("지정된 맵이 없습니다.")
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# ⚙️ [3번 탭] 대회 데이터 관리
# =========================================================
if not broadcast_mode:
    with tab_admin:
        st.markdown("### ⚙️ 백오피스 대회 데이터 및 테마 관리 시스템")
        adm_col1, adm_col2 = st.columns(2)
        
        with adm_col1:
            with st.container(border=True):
                st.subheader("👑 대회 타이틀 및 대문 로고 설정")
                st.session_state.title_type = st.radio("대문 타이틀 형태 선택", ["텍스트 입력", "이미지 업로드"], index=0 if st.session_state.title_type == "텍스트 입력" else 1)
                if st.session_state.title_type == "텍스트 입력":
                    st.session_state.title_text = st.text_input("대회 이름 수정", value=st.session_state.title_text)
                else:
                    st.session_state.title_img = st.file_uploader("로고 이미지 파일 업로드", type=["png", "jpg", "jpeg"])
                
                if st.button("👑 대회 대문 타이틀 설정 즉시 저장"):
                    save_tournament_status()
                    st.success("타이틀 설정 백업 완료!")

            with st.container(border=True):
                st.subheader("🚩 팀명 커스텀 수정")
                st.session_state.teams["Left_Team"]["name"] = st.text_input("좌측 팀명", st.session_state.teams["Left_Team"]["name"])
                st.session_state.teams["Right_Team"]["name"] = st.text_input("우측 팀명", st.session_state.teams["Right_Team"]["name"])
                if st.button("🚩 팀 이름 변경사항 백업 저장"):
                    save_tournament_status()
                    st.success("팀명 백업 완료!")
            
            with st.container(border=True):
                st.subheader("🗺️ 오늘 대회의 사용할 맵 선택")
                if not df_maps.empty:
                    st.markdown("<small style='color:#94a3b8;'>마스터 DB 맵 리스트입니다. 오늘 중계에 활성화할 맵을 체크하세요.</small>", unsafe_allow_html=True)
                    updated_maps = []
                    
                    map_names = df_maps['map_name'].tolist()
                    m_cols = st.columns(3)
                    for i, m_name in enumerate(map_names):
                        col_idx = i % 3
                        is_map_checked = m_name in st.session_state.active_maps
                        if m_cols[col_idx].checkbox(m_name, value=is_map_checked, key=f"map_chk_{m_name}"):
                            updated_maps.append(m_name)
                    
                    if st.button("🗺️ 사용할 맵 라인업 저장"):
                        st.session_state.active_maps = updated_maps
                        save_tournament_status()
                        st.success("오늘 사용할 대회 맵 리스트가 업데이트되었습니다!")
                        st.rerun()
                else: st.caption("구글 시트에 맵 데이터가 비어있습니다.")

        with adm_col2:
            with st.container(border=True):
                st.subheader("📅 당일 엔트리 선수 체크 확정 (종족별 분류)")
                if not df_players.empty:
                    st.markdown("<p style='font-size: 0.85rem; color:#94a3b8; margin-bottom: 12px;'>오늘 현장에 출전 등판한 선수들을 종족별로 필터링하여 체크하세요.</p>", unsafe_allow_html=True)
                    
                    players_by_race = {"테란": [], "저그": [], "프로토스": [], "미정": []}
                    for _, row in df_players.iterrows():
                        p_name = row['name']
                        p_race = parse_race(row['race'])
                        players_by_race[p_race].append(p_name)
                    
                    st.markdown('<div class="sub-tabs">', unsafe_allow_html=True)
                    t_terran, t_zerg, t_protoss, t_unknown = st.tabs(["🔵 테란", "🔴 저그", "🟡 프로토스", "⚪ 기타"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if "entry_chk_state" not in st.session_state:
                        st.session_state.entry_chk_state = {name: (name in st.session_state.today_entry) for name in df_players['name'].tolist()}
                    
                    with t_terran:
                        if players_by_race["테란"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["테란"]):
                                st.session_state.entry_chk_state[name] = cc[idx%2].checkbox(name, value=st.session_state.entry_chk_state[name], key=f"p_chk_{name}")
                        else: st.caption("등록된 테란 선수가 없습니다.")
                        
                    with t_zerg:
                        if players_by_race["저그"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["저그"]):
                                st.session_state.entry_chk_state[name] = cc[idx%2].checkbox(name, value=st.session_state.entry_chk_state[name], key=f"p_chk_{name}")
                        else: st.caption("등록된 저그 선수가 없습니다.")
                        
                    with t_protoss:
                        if players_by_race["프로토스"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["프로토스"]):
                                st.session_state.entry_chk_state[name] = cc[idx%2].checkbox(name, value=st.session_state.entry_chk_state[name], key=f"p_chk_{name}")
                        else: st.caption("등록된 프로토스 선수가 없습니다.")
                        
                    with t_unknown:
                        if players_by_race["미정"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["미정"]):
                                st.session_state.entry_chk_state[name] = cc[idx%2].checkbox(name, value=st.session_state.entry_chk_state[name], key=f"p_chk_{name}")
                        else: st.caption("기타 분류 선수가 없습니다.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("📅 당일 출전 엔트리 라인업 저장"):
                        st.session_state.today_entry = [name for name, is_checked in st.session_state.entry_chk_state.items() if is_checked]
                        save_tournament_status()
                        st.success(f"총 {len(st.session_state.today_entry)}명의 선수 엔트리 저장이 완료되었습니다!")
                        st.rerun()
                else: st.warning("구글 시트에 선수를 먼저 등록해 주세요.")

# =========================================================
# 📜 [맨 하단] 저작권 표기 구역
# =========================================================
st.markdown("<p class='copyright-text'>해당 포멧의 저작권은 스진동에 있습니다.</p>", unsafe_allow_html=True)
