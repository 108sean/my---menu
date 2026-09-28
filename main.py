import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import pytz
import re

# 1. 페이지 기본 설정
st.set_page_config(page_title="급식 칼로리 조회", page_icon="🍱", layout="wide")

# 2. 한국 시간(KST) 기준 오늘 날짜
kst = pytz.timezone("Asia/Seoul")
today_kst = datetime.datetime.now(kst).date()

st.title("🍱 학교 급식 최고 칼로리 메뉴")

# 3. 학교 검색 함수
def search_school(keyword):
    url = "https://open.neis.go.kr/hub/schoolInfo"
    params = {"Type": "json", "SCHUL_NM": keyword}
    
    try:
        res = requests.get(url, params=params).json()
        if "schoolInfo" in res:
            return res["schoolInfo"][1]["row"]
    except Exception:
        pass
    
    # 줄임말 자동 보정
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

# 4. 급식 정보 수집 함수
def get_meal_data(office_code, school_code, from_date, to_date, max_pages=10):
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    all_meals = []
    
    for p_index in range(1, max_pages + 1):
        params = {
            "Type": "json",
            "ATPT_OFCDC_SC_CODE": office_code,
            "SD_SCHUL_CODE": school_code,
            "MMEAL_SC_CODE": "2",  # 중식
            "MLSV_FROM_YMD": from_date.strftime("%Y%m%d"),
            "MLSV_TO_YMD": to_date.strftime("%Y%m%d"),
            "pIndex": p_index,
            "pSize": 100
        }
        
        try:
            res = requests.get(url, params=params).json()
            if "mealServiceDietInfo" in res:
                rows = res["mealServiceDietInfo"][1]["row"]
                all_meals.extend(rows)
                if len(rows) < 100:
                    break
            else:
                break
        except Exception:
            break
            
    return all_meals

# 5. 칼로리 숫자 파싱 함수
def parse_calorie(cal_str):
    if not cal_str:
        return 0.0
    match = re.search(r"([\d\.]+)", cal_str)
    return float(match.group(1)) if match else 0.0

# 6. 메뉴 알레르기 번호 제거 함수
def clean_menu(menu_str):
    if not menu_str:
        return ""
    cleaned = menu_str.replace("<br/>", ", ")
    cleaned = re.sub(r"\([0-9\.]+\)", "", cleaned)
    return cleaned

# 7. 클릭 반응형 플립 카드 UI
def render_flip_card(date_str, menu_text, cal_text, label="최고 칼로리"):
    formatted_menu = menu_text.replace("<br/>", "\n")
    cleaned_menu_text = clean_menu(formatted_menu).replace(", ", "<br/>")
    
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
        height: 300px;
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
        background: #ffffff;
        color: #212529;
        border: 2px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
      }}
      .flip-card-back {{
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5253 100%);
        color: white;
        transform: rotateY(180deg);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      }}
      .badge {{
        font-size: 0.85rem;
        font-weight: 700;
        color: #ff6b6b;
        background: #ffe3e3;
        padding: 4px 10px;
        border-radius: 12px;
        margin-bottom: 8px;
      }}
      .meal-date {{
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: #343a40;
      }}
      .meal-content {{
        font-size: 0.95rem;
        line-height: 1.45;
        color: #495057;
        max-height: 150px;
        overflow-y: auto;
      }}
      .calorie-title {{
        font-size: 1.2rem;
        font-weight: 600;
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
            <div class="badge">🔥 {label}</div>
            <div class="meal-date">📅 {date_str}</div>
            <div class="meal-content">{cleaned_menu_text}</div>
            <div class="click-hint">👆 클릭 시 칼로리 확인</div>
          </div>
          <div class="flip-card-back">
            <div class="calorie-title">🔥 총 열량</div>
            <div class="calorie-value">{cal_text}</div>
            <div class="click-hint">👆 다시 클릭시 메뉴 보기</div>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    components.html(card_html, height=320)

# ----------------- 사이드바 -----------------
st.sidebar.header("🔍 학교 검색")
search_input = st.sidebar.text_input("학교명 입력", placeholder="예: 수도여고, 서울고")

selected_school = None

if search_input:
    schools = search_school(search_input)
    if schools:
        options = {f"{s['SCHUL_NM']} ({s['LCTN_SC_NM']})": s for s in schools}
        selected_option = st.sidebar.selectbox("학교 선택", list(options.keys()))
        selected_school = options[selected_option]
    else:
        st.sidebar.error("검색 결과가 없습니다.")

# ----------------- 메인 화면 -----------------
if selected_school:
    st.subheader(f"🏫 {selected_school['SCHUL_NM']} ({selected_school['LCTN_SC_NM']})")
    
    tab1, tab2 = st.tabs(["📅 날짜별 조회", "🏆 최고 칼로리 메뉴"])
    
    # 1. 일별 단일 조회
    with tab1:
        selected_date = st.date_input("조회 날짜", value=today_kst)
        meals = get_meal_data(
            selected_school["ATPT_OFCDC_SC_CODE"],
            selected_school["SD_SCHUL_CODE"],
            selected_date,
            selected_date,
            max_pages=1
        )
        
        if meals:
            meal = meals[0]
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                render_flip_card(meal["MLSV_YMD"], meal["DDISH_NM"], meal["CAL_INFO"], label="선택 날짜 급식")
        else:
            st.info("해당 날짜에 급식 정보가 없습니다.")
            
    # 2. 기간별 1개 최고 칼로리 카드 출력
    with tab2:
        st.write("원하는 기간을 선택하면 **기간 내 가장 칼로리가 높았던 1개 메뉴**가 표시됩니다.")
        col1, col2, col3 = st.columns(3)
        
        target_days = None
        period_label = ""
        
        if col1.button("일주일 최고", use_container_width=True):
            target_days = 7
            period_label = "최근 1주일 최고 칼로리"
        if col2.button("한 달 최고", use_container_width=True):
            target_days = 30
            period_label = "최근 1달 최고 칼로리"
        if col3.button("1년 최고", use_container_width=True):
            target_days = 365
            period_label = "최근 1년 최고 칼로리"
            
        if target_days:
            start_date = today_kst - datetime.timedelta(days=target_days)
            
            with st.spinner("급식 정보를 불러오는 중입니다..."):
                raw_meals = get_meal_data(
                    selected_school["ATPT_OFCDC_SC_CODE"],
                    selected_school["SD_SCHUL_CODE"],
                    start_date,
                    today_kst,
                    max_pages=5
                )
                
            if raw_meals:
                # 최고 칼로리 메뉴 1개 추출
                top_meal = max(raw_meals, key=lambda x: parse_calorie(x.get("CAL_INFO", "")))
                
                # 중앙에 1개 카드 표시
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2:
                    render_flip_card(
                        top_meal["MLSV_YMD"],
                        top_meal["DDISH_NM"],
                        top_meal["CAL_INFO"],
                        label=period_label
                    )
            else:
                st.warning("선택한 기간에 급식 데이터가 없습니다.")
else:
    st.info("👈 왼쪽 사이드바에서 학교명을 검색해 주세요.")
