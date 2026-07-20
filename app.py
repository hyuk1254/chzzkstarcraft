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
    st.session_state.teams = backup.get("teams", {"Left_Team": {"name": "1팀 멤버", "players": []}, "Right_Team": {"name": "2팀 멤버", "players": []}})
    st.session_state.today_entry = backup.get("today_entry", [])
    st.session_state.assigned_maps = backup.get("assigned_maps", [])
    st.session_state.title_type = backup.get("title_type", "텍스트 입력")
    st.session_state.title_text = backup.get("title_text", "스진동 종족최강전")
    st.session_state.active_maps = backup.get("active_maps", [])
else:
    if "matches" not in st.session_state: st.session_state.matches = []
    if "teams" not in st.session_state: st.session_state.teams = {"Left_Team": {"name": "1팀 멤버", "players": []}, "Right_Team": {"name": "2팀 멤버", "players": []}}
    if "today_entry" not in st.session_state: st.session_state.today_entry = []
    if "assigned_maps" not in st.session_state: st.session_state.assigned_maps = []
    if "title_type" not in st.session_state: st.session_state.title_type = "텍스트 입력"
    if "title_text" not in st.session_state: st.session_state.title_text = "스진동 종족최강전"
    if "active_maps" not in st.session_state: st.session_state.active_maps = []

if "title_img" not in st.session_state:
    st.session_state.title_img = None

# 🎨 제공해주신 스진동 오피셜 고화질 종족 마크 세팅
RACE_ICONS = {
    "테란": "https://cdn.discordapp.com/attachments/1528721011732643951/1528793445269770421/qtPQWR_1fiy6ly6NbndO9Sp-CA73mBjJ52ZtZGwQj1Ozo9FlQOeTV5pjtS3UKrA-_4qCiNLGr3_rgpklZ1HSJCk-0kw5lxqO-VCVHEvGo6jDv60hOCVhzX4Kcun7dxbwK73isQF0cBHi3qjeHDct5w.webp?ex=6a5f9758&is=6a5e45d8&hm=e3199aaefab4395ddca0983c8738bee5bf7c491b6ff3c456a437ce3d9913ad5f&",
    "저그": "https://cdn.discordapp.com/attachments/1528721011732643951/1528793444846403715/vkWLywILixMzHkg83QumKeJR3YPhDMGdAZtjbJ2SBLPOQCHgpqcbXRCRyudHo-3nP5AYQEkKIJFncVwYoOjG4AHdeJ-dcwc1uwhiR90LsKIfDy6If7-s5EhI2xI59o0Vkchd9PNFAOFM_CQamYXFXQ.webp?ex=6a5f9758&is=6a5e45d8&hm=dd0ba630755f7d54b893c5e17412f56f4dcea5c06e69d6f970aaa4dfdacd4c3f&",
    "프로토스": "https://cdn.discordapp.com/attachments/1528721011732643951/1528793444435099648/WrK9L73w0c_CY7HVAOuXzdRg4yS7OBrMXtBIs1qEGHnPZPTeH7N8t1Mzb8sIRkcSkLSi0v47wBiONdp35r10WIE-tmRf8d4EN2gUaMBVgOR0OYFJj_kPILzCIDBFwL6SMK05jX0r1pnJiNIp2t5PjQ.webp?ex=6a5f9758&is=6a5e45d8&hm=63492a3a94779f80643e3c3f5a1f546e5df60b4da678e33ae2b9e260b58b76c2&",
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
    
    .main-title-container {
        padding-top: 35px !important;
        margin-bottom: 5px !important;
        clear: both !important;
    }
    .main-title {
        text-align: center; font-size: 3rem !important; font-weight: 900 !important;
        color: #ffffff !important; letter-spacing: 2px; margin-bottom: 5px;
        background: linear-gradient(to right, #ffffff, #00ffa3);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    
    /* 팀 멤버 묶음 박스 디자인 */
    .broadcast-team-card {
        background-color: #14161d; 
        border: 2px solid #2d3139;
        border-radius: 16px; 
        padding: 20px; 
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    .broadcast-player-container {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 15px !important;
        flex-wrap: wrap !important;
        margin-top: 15px;
    }
    .broadcast-player-card {
        background-color: #1c1e26; border: 1px solid #2d3139;
        border-radius: 12px; padding: 12px; text-align: center;
        width: 130px;
    }
    .broadcast-avatar-img img {
        width: 90px !important; height: 90px !important;
        object-fit: cover !important; border-radius: 12px !important;
        margin: 0 auto 8px auto;
    }

    .draft-panel {
        background-color: #181a20; border: 1px solid #2d3139;
        border-radius: 12px; padding: 25px; margin-top: 35px !important;
    }
    
    /* 사용맵 나열 대형 와이드 박스 디자인 */
    .use-map-container-box {
        background-color: #14161d; border: 2px solid #2d3139; border-radius: 16px; padding: 15px 20px; margin-bottom: 35px;
    }
    
    /* 맵 타임라인 가로 강제 연동 */
    .map-timeline-row {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        gap: 15px !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
    }
    .map-timeline-box {
        background-color: #1c1e26; border: 1px solid #2d3139; border-radius: 12px; padding: 10px; text-align: center;
        width: 150px !important; flex-shrink: 0 !important;
    }
    .map-timeline-img img {
        width: 100% !important; height: 95px !important;
        object-fit: cover !important; border-radius: 6px !important;
    }
    
    /* 🛠️ [레이아웃 절대 고정] 매치 보드 수평 구조 및 정렬 유지 */
    .match-board-flex-row {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    .match-board-card {
        background-color: #181a20; border: 1px solid #2d3139; border-radius: 16px; 
        padding: 25px; margin: 0 auto 30px auto !important;
        max-width: 650px !important;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.6);
    }
    
    .match-side-player-block {
        text-align: center !important;
        width: 160px !important;
        flex-shrink: 0 !important;
    }
    
    .match-player-img img { 
        width: 150px !important; height: 150px !important; 
        object-fit: cover !important; border-radius: 12px !important; 
        border: 2px solid #2d3139;
        margin: 0 auto;
    }
    
    .match-mid-text-container {
        text-align: center !important;
        flex-grow: 1 !important;
        display: block !important;
    }

    .admin-match-text-row {
        background-color: #181a20; border: 1px solid #2d3139;
        border-radius: 8px; padding: 12px 20px; margin-bottom: 10px;
    }

    .race-icon-img { display: inline-block; width: 18px; height: 16px; object-fit: contain; vertical-align: middle; margin-right: 4px; }
    
    .stButton > button {
        padding: 3px 10px !important; font-size: 0.85rem !important;
        background-color: #1c1e26 !important; color: #e2e8f0 !important;
        border: 1px solid #2d3139 !important; transition: all 0.2s ease;
    }
    .stButton > button:hover { border-color: #00ffa3 !important; color: #00ffa3 !important; box-shadow: 0 0 8px rgba(0, 255, 163, 0.3); }
    
    .del-btn > div > button {
        padding: 2px 8px !important; font-size: 0.8rem !important;
        background-color: rgba(255, 85, 85, 0.15) !important; color: #ff5555 !important;
        border: 1px solid rgba(255, 85, 85, 0.3) !important;
    }
    .del-btn > div > button:hover { background-color: #ff5555 !important; color: #ffffff !important; }

    .stApp > div:nth-child(1) .stTabs { margin-top: -50px !important; }
    .stApp > div:nth-child(1) .stTabs [data-baseweb="tab-list"] { gap: 4px; justify-content: flex-start !important; padding-left: 5px; border-bottom: 1px solid #2d3139; margin-bottom: 15px; }
    .stApp > div:nth-child(1) .stTabs [data-baseweb="tab"] { height: 32px !important; background-color: #14161d; border-radius: 4px 4px 0px 0px; padding: 4px 12px !important; font-size: 0.85rem !important; color: #64748b !important; border: 1px solid #2d3139; border-bottom: none; }
    .stApp > div:nth-child(1) .stTabs [aria-selected="true"] { background-color: #1c1e26 !important; color: #00ffa3 !important; font-weight: bold; border-top: 2px solid #00ffa3 !important; }
    
    .sub-tabs-container { margin-top: 25px !important; padding-top: 10px !important; clear: both !important; }
    .sub-tabs-container [data-baseweb="tab-list"] { margin-top: 0px !important; padding-top: 0px !important; height: auto !important; border-bottom: 1px solid #2d3139 !important; justify-content: flex-start !important; gap: 12px !important; }
    .sub-tabs-container [data-baseweb="tab"] { background-color: #0c0d10 !important; border: 1px solid transparent !important; color: #94a3b8 !important; height: 40px !important; padding: 6px 16px !important; margin-top: 0px !important; }
    .sub-tabs-container [aria-selected="true"] { color: #00ffa3 !important; border-bottom: 2px solid #00ffa3 !important; border-top: none !important; background-color: transparent !important; font-weight: bold !important; }

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
    if "프" in race_text or "pr" in race_text or "토" in race_text: return "프로토스"
    return "미정"

# 종족 배지 가독성 빌더
def get_race_badge_html(race_text):
    norm_race = parse_race(race_text)
    icon_url = RACE_ICONS.get(norm_race)
    if icon_url and norm_race != "미정" and "placeholder" not in icon_url:
        return f'<div style="line-height:1; display:inline-block; margin-top:4px;"><img src="{icon_url}" class="race-icon-img"> <span style="color:#94a3b8 !important; font-size:0.85rem; vertical-align:middle;">{norm_race}</span></div>'
    elif norm_race != "미정":
        return f'<span style="color:#94a3b8 !important; font-size:0.85rem; vertical-align:middle;">{norm_race}</span>'
    return f'<span style="color:#94a3b8 !important; font-size:0.85rem; vertical-align:middle;">미정</span>'

# 내부 리셋 전용 코어 함수
def execute_master_reset():
    st.session_state.matches = []
    st.session_state.teams = {"Left_Team": {"name": "1팀 멤버", "players": []}, "Right_Team": {"name": "2팀 멤버", "players": []}}
    st.session_state.today_entry = []
    st.session_state.assigned_maps = []
    st.session_state.active_maps = []
    if "entry_chk_state" in st.session_state:
        del st.session_state.entry_chk_state
    save_tournament_status()

# --- 🎬 [사이드바] 스크린 제어 ---
with st.sidebar:
    st.header("🎬 스크린 제어")
    broadcast_mode = st.checkbox("📺 방송 송출 모드 (UI 전체 숨기기)", value=False)
    
    st.markdown("---")
    if st.button("🚨 대회 전체 데이터 초기화 (리셋)", key="sb_reset_btn", use_container_width=True):
        execute_master_reset()
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
    tab_main, tab_draft, tab_admin = st.tabs(["🏆 방송 송출 오버레이", "📝 실시간 대진 지명", "⚙️ 데이터 관리"])
else:
    tab_main = st.container()

# =========================================================
# 🏆 [1번 탭] 방송 송출 오버레이
# =========================================================
with tab_main:
    st.markdown('<div class="main-title-container">', unsafe_allow_html=True)
    if st.session_state.title_type == "이미지 업로드" and st.session_state.title_img is not None:
        t_col1, t_col2, t_col3 = st.columns([1.5, 3, 1.5])
        with t_col2: st.image(st.session_state.title_img, use_container_width=True)
    else:
        st.markdown(f"<h1 class='main-title'>{st.session_state.title_text}</h1>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px;'>", unsafe_allow_html=True)

    # 1. 최상단: [1팀 멤버] 와 [2팀 멤버] 박스
    team_left, team_right = st.columns(2)
    
    with team_left:
        st.markdown(f"<div class='broadcast-team-card'><h3 style='color:#00ffa3; font-weight:bold; text-align:center; margin:0;'>🟢 {st.session_state.teams['Left_Team']['name']}</h3>", unsafe_allow_html=True)
        players = st.session_state.teams['Left_Team']['players']
        if players:
            st.markdown("<div class='broadcast-player-container'>", unsafe_allow_html=True)
            for p_name in players:
                p_row = df_players[df_players['name'] == p_name] if not df_players.empty else pd.DataFrame()
                race = p_row.iloc[0]['race'] if not p_row.empty else "미정"
                img = p_row.iloc[0]['img_url'] if not p_row.empty else ""
                
                st.markdown(f"""
                <div class='broadcast-player-card'>
                    <div class='broadcast-avatar-img'><img src="{img if img else 'https://via.placeholder.com/90/181a20/e2e8f0?text=User'}"></div>
                    <p style='margin:0; font-size:0.95rem; font-weight:bold; color:#fff;'>{p_name}</p>
                    {get_race_badge_html(race)}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("<p style='text-align:center; color:#64748b; margin-top:15px;'>배정된 선수가 없습니다.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with team_right:
        st.markdown(f"<div class='broadcast-team-card'><h3 style='color:#00ffa3; font-weight:bold; text-align:center; margin:0;'>🔴 {st.session_state.teams['Right_Team']['name']}</h3>", unsafe_allow_html=True)
        players = st.session_state.teams['Right_Team']['players']
        if players:
            st.markdown("<div class='broadcast-player-container'>", unsafe_allow_html=True)
            for p_name in players:
                p_row = df_players[df_players['name'] == p_name] if not df_players.empty else pd.DataFrame()
                race = p_row.iloc[0]['race'] if not p_row.empty else "미정"
                img = p_row.iloc[0]['img_url'] if not p_row.empty else ""
                
                st.markdown(f"""
                <div class='broadcast-player-card'>
                    <div class='broadcast-avatar-img'><img src="{img if img else 'https://via.placeholder.com/90/181a20/e2e8f0?text=User'}"></div>
                    <p style='margin:0; font-size:0.95rem; font-weight:bold; color:#fff;'>{p_name}</p>
                    {get_race_badge_html(race)}
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("<p style='text-align:center; color:#64748b; margin-top:15px;'>배정된 선수가 없습니다.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. 중간: [사용맵 나열] 가로형 단독 배너
    if st.session_state.matches:
        st.markdown("<div class='use-map-container-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #94a3b8; font-weight: bold; margin-top:0px; margin-bottom:15px;'>🗺️ 사용맵 나열</h3>", unsafe_allow_html=True)
        
        timeline_html = "<div class='map-timeline-row'>"
        for idx, match in enumerate(st.session_state.matches):
            map_row = df_maps[df_maps['map_name'] == match["map"]] if not df_maps.empty else pd.DataFrame()
            map_img = map_row.iloc[0]['map_url'] if not map_row.empty and map_row.iloc[0]['map_url'] else "https://via.placeholder.com/150/14161d/ffffff?text=No+Image"
            
            timeline_html += f"""
            <div class='map-timeline-box'>
                <p style='margin:0 0 5px 0; font-size:0.85rem; font-weight:bold; color:#00ffa3;'>SET {idx+1}</p>
                <div class='map-timeline-img'><img src="{map_img}"></div>
                <p style='margin:5px 0 0 0; font-size:0.85rem; font-weight:bold; color:#fff; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'>{match['map']}</p>
            </div>
            """
        timeline_html += "</div>"
        st.markdown(timeline_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><h2 style='text-align: center; letter-spacing: 6px; font-weight: 900; color: #ffffff !important;'>MATCH BOARD</h2>", unsafe_allow_html=True)
    st.write("")
    
    # 3. 하단: [🚨 버그 박멸 완료] 스케치 레이아웃 1:1 수평 대진 카드 출력
    for idx, match in enumerate(list(st.session_state.matches)):
        p1_row = df_players[df_players['name'] == match["p1"]] if not df_players.empty else pd.DataFrame()
        p2_row = df_players[df_players['name'] == match["p2"]] if not df_players.empty else pd.DataFrame()
        
        img1 = p1_row.iloc[0]['img_url'] if not p1_row.empty and p1_row.iloc[0]['img_url'] else "https://via.placeholder.com/150/1c1e26/e2e8f0?text=User"
        img2 = p2_row.iloc[0]['img_url'] if not p2_row.empty and p2_row.iloc[0]['img_url'] else "https://via.placeholder.com/150/1c1e26/e2e8f0?text=User"
        
        # 주입형 데이터 포매팅 문자열(f) 누락 버그 완벽 수정
        st.markdown(f"""
        <div class='match-board-card'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d3139; padding-bottom: 8px; margin-bottom: 15px;'>
                <p style='font-weight: bold; color: #00ffa3 !important; font-size: 1.2rem; margin: 0;'>SET {idx+1}</p>
            </div>
            <div class='match-board-flex-row'>
                <!-- 좌측 선수 구역 -->
                <div class='match-side-player-block'>
                    <div class='match-player-img'><img src="{img1}"></div>
                    <h3 style='color: #ffffff !important; margin-top:12px; font-weight:bold; font-size:1.4rem; text-align:center; margin-bottom:0;'>{match['p1']}</h3>
                </div>
                
                <!-- 중앙 스케치 텍스트 구역 -->
                <div class='match-mid-text-container'>
                    <p style='margin:0; font-size:1.3rem; font-weight:bold; color:#00ffa3;'>{idx+1}SET</p>
                    <h1 style='margin:2px 0; color:#fff; font-weight:900; font-size:2.3rem; line-height:1;'>VS</h1>
                    <p style='margin:0; font-size:1.1rem; font-weight:bold; color:#94a3b8;'>{match['map']}</p>
                </div>
                
                <!-- 우측 선수 구역 -->
                <div class='match-side-player-block'>
                    <div class='match-player-img'><img src="{img2}"></div>
                    <h3 style='color: #ffffff !important; margin-top:12px; font-weight:bold; font-size:1.4rem; text-align:center; margin-bottom:0;'>{match['p2']}</h3>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# 📝 [2번 탭] 실시간 대진 지명 및 대진 현황
# =========================================================
if not broadcast_mode:
    with tab_draft:
        st.markdown("<div class='draft-panel'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #00ffa3 !important; font-weight: bold;'>📝 실시간 대진표 지명 및 조작 컨트롤 보드</h2>", unsafe_allow_html=True)
        st.write("")
        
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        left_team_name = st.session_state.teams["Left_Team"]["name"]
        right_team_name = st.session_state.teams["Right_Team"]["name"]
        
        with ctrl_col1:
            p1 = st.selectbox(f"🟢 {left_team_name} 출전 선수 지명", options=st.session_state.teams["Left_Team"]["players"], key="admin_sb_p1")
        with ctrl_col2:
            p2 = st.selectbox(f"🔴 {right_team_name} 출전 선수 지명", options=st.session_state.teams["Right_Team"]["players"], key="admin_sb_p2")
        with ctrl_col3:
            map_pool = st.session_state.assigned_maps if st.session_state.assigned_maps else (st.session_state.active_maps if st.session_state.active_maps else (df_maps['map_name'].tolist() if not df_maps.empty else []))
            selected_map = st.selectbox("전장 맵 선택", options=map_pool, key="admin_sb_map")
            
        if st.button("⚔️ 확정 대진표에 추가", use_container_width=True):
            if p1 and p2 and selected_map:
                st.session_state.matches.append({"p1": p1, "p2": p2, "map": selected_map})
                save_tournament_status()
                st.rerun()
                
        st.markdown("<br><hr style='border-style: dashed;'><br>", unsafe_allow_html=True)
        st.markdown("### 📊 현재 구성된 실시간 대진표 리스트 (글씨 최적화 모드)", unsafe_allow_html=True)
        
        # 🛠️ [🚨 오타 완벽 복구 교정 완료] 
        if st.session_state.matches:
            for idx, match in enumerate(list(st.session_state.matches)):
                st.markdown(f"<div class='admin-match-text-row'>", unsafe_allow_html=True)
                txt_c1, txt_c2 = st.columns([8.5, 1.5])
                with txt_c1:
                    st.markdown(f"<p style='margin:0; font-size:1.1rem; line-height:1.8;'><b style='color:#00ffa3;'>[SET {idx+1}]</b> &nbsp;&nbsp; 🟢 {match['p1']} &nbsp;&nbsp; <b style='color:#64748b;'>VS</b> &nbsp;&nbsp; 🔴 {match['p2']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#94a3b8; font-size:0.95rem;'>전장 맵: {match['map']}</span></p>", unsafe_allow_html=True)
                with txt_c2:
                    st.markdown("<div class='del-btn'>", unsafe_allow_html=True)
                    if st.button("X 취소", key=f"admin_del_match_{idx}", use_container_width=True):
                        st.session_state.matches.remove(match)
                        save_tournament_status()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.caption("현재 성사된 대진표가 없습니다. 위의 지명 시스템으로 세트별 대진을 추가해 주세요.")
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# ⚙️ [3번 탭] 대회 데이터 관리
# =========================================================
if not broadcast_mode:
    with tab_admin:
        st.markdown("### ⚙️ 백오피스 대회 데이터 및 테마 관리 시스템")
        
        with st.container(border=True):
            st.markdown("<p style='font-size:1rem; font-weight:bold; color:#ff5555 !important; margin-bottom:5px;'>🚨 대회 진행 상황 완전 초기화 구역</p>", unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.8rem; color:#94a3b8; margin-bottom:12px;'>현재까지 편성된 대진표, 가르기 완료된 팀 명단, 당일 엔트리 및 활성화된 맵 정보를 영구 삭제하고 첫 상태로 리셋합니다.</p>", unsafe_allow_html=True)
            if st.button("🚨 대회 모든 내용 실시간 초기화", key="admin_master_reset_btn"):
                execute_master_reset()
                st.success("대회 데이터가 완벽히 초기화되었습니다!")
                time.sleep(1)
                st.rerun()
                
        st.write("")
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
                    st.markdown("<p style='font-size: 0.85rem; color:#94a3b8; margin-bottom: 5px;'>오늘 현장에 출전 등판한 선수들을 종족별로 필터링하여 체크하세요.</p>", unsafe_allow_html=True)
                    
                    players_by_race = {"테란": [], "저그": [], "프로토스": [], "미정": []}
                    for _, row in df_players.iterrows():
                        p_name = row['name']
                        p_race = parse_race(row['race'])
                        players_by_race[p_race].append(p_name)
                    
                    st.markdown('<div class="sub-tabs-container">', unsafe_allow_html=True)
                    t_terran, t_zerg, t_protoss, t_unknown = st.tabs(["🔵 테란", "🔴 저그", "🟡 프로토스", "⚪ 기타"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    current_entry_list = st.session_state.today_entry
                    
                    with t_terran:
                        if players_by_race["테란"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["테란"]):
                                is_chk = name in current_entry_list
                                if cc[idx%2].checkbox(name, value=is_chk, key=f"p_chk_{name}"):
                                    if name not in st.session_state.today_entry: st.session_state.today_entry.append(name)
                                else:
                                    if name in st.session_state.today_entry: st.session_state.today_entry.remove(name)
                        else: st.caption("등록된 테란 선수가 없습니다.")
                        
                    with t_zerg:
                        if players_by_race["저그"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["저그"]):
                                is_chk = name in current_entry_list
                                if cc[idx%2].checkbox(name, value=is_chk, key=f"p_chk_{name}"):
                                    if name not in st.session_state.today_entry: st.session_state.today_entry.append(name)
                                else:
                                    if name in st.session_state.today_entry: st.session_state.today_entry.remove(name)
                        else: st.caption("등록된 저그 선수가 없습니다.")
                        
                    with t_protoss:
                        if players_by_race["프로토스"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["프로토스"]):
                                is_chk = name in current_entry_list
                                if cc[idx%2].checkbox(name, value=is_chk, key=f"p_chk_{name}"):
                                    if name not in st.session_state.today_entry: st.session_state.today_entry.append(name)
                                else:
                                    if name in st.session_state.today_entry: st.session_state.today_entry.remove(name)
                        else: st.caption("등록된 프로토스 선수가 없습니다.")
                        
                    with t_unknown:
                        if players_by_race["미정"]:
                            cc = st.columns(2)
                            for idx, name in enumerate(players_by_race["미정"]):
                                is_chk = name in current_entry_list
                                if cc[idx%2].checkbox(name, value=is_chk, key=f"p_chk_{name}"):
                                    if name not in st.session_state.today_entry: st.session_state.today_entry.append(name)
                                else:
                                    if name in st.session_state.today_entry: st.session_state.today_entry.remove(name)
                        else: st.caption("기타 분류 선수가 없습니다.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("📅 당일 출전 엔트리 라인업 저장"):
                        save_tournament_status()
                        st.success(f"총 {len(st.session_state.today_entry)}명의 선수 엔트리 저장이 완료되었습니다!")
                        st.rerun()
                else: st.warning("구글 시트에 선수를 먼저 등록해 주세요.")
