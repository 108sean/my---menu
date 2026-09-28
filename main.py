import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pytz
import re

# 1. 페이지 설정
st.set_page_config(page_title="가장 칼로리가 높았던 메뉴", page_icon="🍱", layout="wide")

# 2. 한국 시간(KST) 기준 오늘 날짜 가져오기
kst = pytz.timezone("Asia/Seoul")
today_kst = datetime.datetime.now(kst).date()

st.title("🍱 가장 칼로리가 높았던 메뉴")

# 3. 학교 검색 함수 (줄임말 자동 보정 포함)
def search_school(keyword):
    url = "https://open.neis.go.kr/hub/schoolInfo"
    params = {"Type": "json", "SCHUL_NM": keyword}
    
    try:
        res = requests.get(url, params=params).json()
        if "schoolInfo" in res:
            return res["schoolInfo"][1]["row"]
    except Exception:
        pass
    
    # 1차 검색 실패 시 줄임말 대체 후 2차 검색
    alt_keyword = keyword
    if "여고" in alt_keyword:
        alt_keyword = alt_keyword.replace("여고", "여자고등학교")
    elif "고" in alt_keyword and not alt_keyword.endswith("고등학교"):
        alt_keyword = alt_keyword.replace("고", "고등학교")
        
    if alt_keyword != keyword:
        try:
            params["SCHUL_NM"] = alt_keyword
            res = requests.get(url, params=params).json()
            if "schoolInfo" in res:
                return res["schoolInfo"][1]["row"]
        except Exception:
            pass
            
    return []

# 4. 급식 정보 조회 함수
def get_meal_data(office_code, school_code, from_date, to_date):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "Type": "json",
        "ATPT_OFCDC_SC_CODE": office_code,
        "SD_SCHUL_CODE": school_code,
        "MMEAL_SC_CODE": "2",  # 중식
        "MLSV_FROM_YMD": from_date.strftime("%Y%m%d"),
        "MLSV_TO_YMD": to_date.strftime("%Y%m%d")
    }
    
    try:
        res = requests.get(url, params=params).json()
        if "mealServiceDietInfo" in res:
            return res["mealServiceDietInfo"][1]["row"]
    except Exception:
        pass
    return []

# 5. 칼로리 파싱 함수 (문자열 -> float)
def parse_calorie(cal_str):
    if not cal_str:
        return 0.0
    match = re.search(r"([\d\.]+)", cal_str)
    return float(match.group(1)) if match else 0.0

# 6. 메뉴 텍스트 정제 함수 (알레르기 번호 제거)
def clean_menu(menu_str):
    if not menu_str:
        return ""
    cleaned = menu_str.replace("<br/>", "\n")
    cleaned = re.sub(r"\([0-9\.]+\)", "", cleaned)
    return cleaned

# 7. 클릭 시 뒤집히는 HTML/CSS/JS 플립 카드 렌더링
def render_flip_card(date_str, menu_text, cal_text):
    clean_menu_display = clean_menu(menu_text).replace("\n", "<br/>")
    
    card_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      body {{
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background-color: transparent;
      }}
      .flip-card {{
        background-color: transparent;
        width: 100%;
        height: 280px;
        perspective: 1000px;
        cursor: pointer;
      }}
      .flip-card-inner {{
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
      }}
      /* 클릭 시 flipped 클래스가 추가되어 뒤집힘 */
      .flip-card.flipped .flip-card-inner {{
        transform: rotateY(180deg);
      }}
      .flip-card-front, .flip-card-back {{
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        border-radius: 16px;
        padding: 20px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        user-select: none;
      }}
      .flip-card-front {{
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #212529;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      }}
      .flip-card-back {{
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5253 100%);
        color: white;
        transform: rotateY(180deg);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      }}
      .meal-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: #343a40;
      }}
      .meal-content {{
        font-size: 0.95rem;
        line-height: 1.5;
        color: #495057;
        max-height: 180px;
        overflow-y: auto;
      }}
      .calorie-title {{
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 8px;
      }}
      .calorie-value {{
        font-size: 2.2rem;
        font-weight: 800;
      }}
      .click-hint {{
        font-size: 0.8rem;
        margin-top: 12px;
        opacity: 0.8;
      }}
    </style>
    </head>
    <body>
      <div class="flip-card" onclick="this.classList.toggle('flipped')">
        <div class="flip-card-inner">
          <div class="flip-card-front">
            <div class="meal-title">📅 {date_str}</div>
            <div class="meal-content">{clean_menu_display}</div>
            <div class="click-hint">👆 카드를 클릭하면 칼로리가 나옵니다</div>
          </div>
          <div class="flip-card-back">
            <div class="calorie-title">🔥 총 열량</div>
            <div class="calorie-value">{cal_text}</div>
            <div class="click-hint">👆 다시 클릭하면 메뉴를 볼 수 있습니다</div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    components.html(card_html, height=300)

# ----------------- 사이드바: 학교 검색 -----------------
st.sidebar.header("🔍 학교 검색")
search_input = st.sidebar.text_input("학교 이름을 입력하세요", placeholder="예: 수도여고, 서울고")

selected_school = None

if search_input:
    schools = search_school(search_input)
    if schools:
        options = {f"{s['SCHUL_NM']} ({s['LCTN_SC_NM']})": s for s in schools}
        selected_option = st.sidebar.selectbox("학교를 선택하세요", list(options.keys()))
        selected_school = options[selected_option]
    else:
        st.sidebar.error("검색된 학교가 없습니다. 정확한 명칭을 입력해 주세요.")

# ----------------- 메인 영역 -----------------
if selected_school:
    st.subheader(f"🏫 {selected_school['SCHUL_NM']} ({selected_school['LCTN_SC_NM']})")
    
    tab1, tab2 = st.tabs(["📅 날짜별 조회", "🏆 최고 칼로리 메뉴"])
    
    # [TAB 1] 특정 날짜 선택 및 카드 출력
    with tab1:
        selected_date = st.date_input("조회할 날짜를 선택하세요", value=today_kst)
        meals = get_meal_data(
            selected_school["ATPT_OFCDC_SC_CODE"],
            selected_school["SD_SCHUL_CODE"],
            selected_date,
            selected_date
        )
        
        if meals:
            meal = meals[0]
            render_flip_card(meal["MLSV_YMD"], meal["DDISH_NM"], meal["CAL_INFO"])
        else:
            st.info("해당 날짜에는 급식 정보가 없습니다.")
            
    # [TAB 2] 기간별 최고 칼로리 탐색
    with tab2:
        st.write("기간을 선택하면 해당 기간 중 **가장 칼로리가 높았던 날**의 급식을 찾아드립니다.")
        col1, col2, col3 = st.columns(3)
        
        target_range = None
        if col1.button("일주일 (최근 7일)", use_container_width=True):
            target_range = (today_kst - datetime.timedelta(days=6), today_kst)
        if col2.button("한 달 (최근 30일)", use_container_width=True):
            target_range = (today_kst - datetime.timedelta(days=29), today_kst)
        if col3.button("1년 (최근 365일)", use_container_width=True):
            target_range = (today_kst - datetime.timedelta(days=364), today_kst)
            
        if target_range:
            start_d, end_d = target_range
            st.write(f"**조회 기간:** {start_d} ~ {end_d}")
            
            with st.spinner("급식 데이터를 조회 중입니다..."):
                range_meals = get_meal_data(
                    selected_school["ATPT_OFCDC_SC_CODE"],
                    selected_school["SD_SCHUL_CODE"],
                    start_d,
                    end_d
                )
                
            if range_meals:
                max_meal = max(range_meals, key=lambda x: parse_calorie(x.get("CAL_INFO", "")))
                st.success(f"🔥 최고 칼로리 날짜: {max_meal['MLSV_YMD']}")
                render_flip_card(max_meal["MLSV_YMD"], max_meal["DDISH_NM"], max_meal["CAL_INFO"])
            else:
                st.warning("선택한 기간 내에 급식 데이터가 존재하지 않거나, 인증키 미사용으로 제한된 결과만 제공됩니다.")
else:
    st.info("👈 왼쪽 사이드바에서 학교 이름을 검색해 선택해 주세요.")
