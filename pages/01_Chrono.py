import streamlit as st
import pandas as pd
import re
import io
from components.ui import section, card, info_box, header, result_box, action_button

# 연호 변환기

import streamlit as st

# 인증 상태 확인
if 'authentication_status' not in st.session_state or not st.session_state['authentication_status']:
    st.error('이 페이지에 접근하려면 로그인이 필요합니다.')
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="연호 변환기",
    page_icon="📅",
    layout="wide"
)

# CSS 스타일 적용
def load_css(css_file):
    with open(css_file, encoding='utf-8') as f:
        return f"<style>{f.read()}</style>"

# 타이포그래피 스타일 적용
st.markdown(load_css("styles/typography.css"), unsafe_allow_html=True)

# 사이드바 구성
with st.sidebar:
    st.image("https://via.placeholder.com/150x50.png?text=Logo", use_column_width=True)
    st.divider()
    
    st.markdown("### 🧰 도구 모음")
    st.markdown("현재 사용 가능한 도구:")
    current_page = "연호 변환기"
    
    menu_items = {
        "🏠 홈": "홈",
        "📅 연호 변환기": "연호 변환기",
        "🔜 추가 예정": "추가 예정"
    }
    
    for label, page in menu_items.items():
        if page == current_page:
            st.markdown(f"**{label}** ←")
        else:
            st.markdown(label)
    
    st.divider()
    st.markdown("### ℹ️ 정보")
    st.markdown("버전: 1.0.0")
    st.markdown("[사용 설명서]()")
    st.markdown("[피드백 보내기]()")

def parse_year_input(text):
    """입력 텍스트에서 연호와 연도를 추출"""
    text = text.strip()
    
    # 단기 패턴 (예: "단기 4300년", "단기4300", "단기 4300")
    dangi_pattern = r'단기\s*(\d+)년?'
    dangi_match = re.search(dangi_pattern, text)
    if dangi_match:
        year = int(dangi_match.group(1))
        return "단기", year
    
    # 일본 연호 패턴 (한국식/일본식 모두 지원)
    era_mapping = {
        '메이지': '메이지',
        '명치': '메이지',
        '다이쇼': '다이쇼',
        '대정': '다이쇼',
        '쇼와': '쇼와',
        '소화': '쇼와'
    }
    
    era_pattern = f"({'|'.join(era_mapping.keys())})\s*(\d+)년?"
    era_match = re.search(era_pattern, text)
    if era_match:
        input_era = era_match.group(1)
        year = int(era_match.group(2))
        standardized_era = era_mapping[input_era]
        return standardized_era, year
    
    # 숫자만 있는 경우 단기로 간주
    number_pattern = r'^\s*(\d+)\s*년?\s*$'
    number_match = re.search(number_pattern, text)
    if number_match:
        year = int(number_match.group(1))
        return "단기", year
    
    return None, None

def is_valid_year(era, year):
    """연호별 유효 기간 검증"""
    if era == "단기":
        # 단기는 음수가 되지 않아야 하고, 2002년을 초과하지 않아야 함
        segi_year = year - 2333
        return year >= 1 and segi_year <= 2002
    
    # 일본 연호별 유효 기간
    era_limits = {
        "메이지": (1, 45),    # 1868-1912
        "다이쇼": (1, 15),    # 1912-1926
        "쇼와": (1, 64)      # 1926-1989
    }
    
    if era in era_limits:
        min_year, max_year = era_limits[era]
        return min_year <= year <= max_year
    
    return False

def is_within_project_scope(segi_year):
    """사업 대상 연도 검증 (2002년 이하)"""
    return segi_year <= 2002

def convert_to_segi(era, year):
    """연호와 연도를 서기로 변환"""
    # 유효성 검사 추가
    if not is_valid_year(era, year):
        if era == "단기":
            segi_year = year - 2333
            if segi_year > 2002:
                st.error(f"⚠️ 입력하신 단기 {year}년(서기 {segi_year}년)은 사업 대상 기간(~2002년)을 초과합니다.")
            else:
                st.error("유효하지 않은 단기 연도입니다.")
        return None
        
    segi_year = None
    if era == "단기":
        segi_year = year - 2333
    elif era == "메이지":
        segi_year = 1867 + year
    elif era == "다이쇼":
        segi_year = 1911 + year
    elif era == "쇼와":
        segi_year = 1925 + year
    
    return segi_year

def batch_convert_years(df, column_name):
    """데이터프레임의 특정 칼럼에서 연호를 일괄 변환"""
    results = []
    original_values = []
    out_of_scope_years = []
    
    for idx, value in enumerate(df[column_name]):
        if pd.isna(value):  # 빈 값 처리
            results.append(None)
            original_values.append(None)
            continue
            
        value = str(value).strip()
        era, year = parse_year_input(value)
        
        if era and year:
            segi_year = convert_to_segi(era, year)
            if segi_year:
                if not is_within_project_scope(segi_year):
                    out_of_scope_years.append((idx + 2, value, segi_year))  # Excel 행 번호는 1부터 시작, 헤더 제외
                results.append(segi_year)
                original_values.append(value)
            else:
                results.append(None)
                original_values.append(value)
        else:
            results.append(None)
            original_values.append(value)
    
    # 범위 초과 데이터 경고
    if out_of_scope_years:
        warning_msg = "### ⚠️ 사업 대상 기간(~2002년)을 초과하는 데이터가 발견되었습니다:\n\n"
        for row_num, orig_value, converted_year in out_of_scope_years:
            warning_msg += f"- {row_num}행: {orig_value} → 서기 {converted_year}년\n"
        st.warning(warning_msg)
    
    return results, original_values

# 헤더
header(
    "연호 변환기",
    "다양한 연호를 표준화된 서기(西紀) 연도로 변환합니다."
)

# 도구 소개
with section("도구 소개", "📋"):
    st.markdown("### 지원하는 연호 체계")
    col1, col2 = st.columns(2)
    
    with col1:
        with card("연호 체계", icon="📅"):
            st.markdown("""
            * **단기(檀紀)**: 한국의 전통 연호
            * **일본 연호**
                - 메이지(明治/명치): 1868-1912
                - 다이쇼(大正/대정): 1912-1926
                - 쇼와(昭和/소화): 1926-1989
            """)
    
    with col2:
        with card("변환 규칙", icon="ℹ️"):
            st.markdown("""
            1. **단기 → 서기**: 단기 - 2333
            2. **일본 연호 → 서기**:
                - 메이지/명치 N년 → 1867 + N
                - 다이쇼/대정 N년 → 1911 + N
                - 쇼와/소화 N년 → 1925 + N
            """)

# 메인 변환 인터페이스
with section("연호 변환", "🔄"):
    st.markdown("### 변환 방식 선택")
    
    # 변환 유형 선택
    tabs = st.tabs(["📝 일반 입력", "✍️ 자유 입력", "📤 일괄 변환"])
    
    with tabs[0]:  # 일반 입력
        col1, col2 = st.columns([2, 1])
        
        with col1:
            era_type = st.radio(
                "연호 유형을 선택하세요:",
                ["단기", "일본 연호"],
                horizontal=True,
                key="era_type"
            )
            
            if era_type == "단기":
                with card("단기 연도 입력", icon="🔢"):
                    max_dangi = 4335  # 2002년에 해당하는 단기 연도
                    dangi_year = st.number_input(
                        "단기 연도를 입력하세요:",
                        min_value=1,
                        max_value=max_dangi,
                        value=2333,
                        help=f"단기 연도를 입력하세요. (최대: 단기 {max_dangi}년 = 서기 2002년)"
                    )
                    
                    if action_button("변환하기", key="convert_dangi"):
                        with st.spinner("변환 중..."):
                            segi_year = convert_to_segi("단기", dangi_year)
                            if segi_year is not None:
                                with result_box("✨ 변환 결과"):
                                    st.markdown(f'<div style="text-align: center; font-size: 1.2rem;">', unsafe_allow_html=True)
                                    st.markdown(f"단기 **{dangi_year:,}**년은", unsafe_allow_html=True)
                                    st.markdown(f'<div style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">서기 {segi_year:,}년</div>', unsafe_allow_html=True)
                                    st.markdown("입니다.", unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    df = pd.DataFrame({
                                        '구분': ['단기', '서기'],
                                        '연도': [f'{dangi_year:,}', f'{segi_year:,}']
                                    })
                                    csv = df.to_csv(index=False).encode('utf-8-sig')
                                    col1, col2, col3 = st.columns([1,2,1])
                                    with col2:
                                        st.download_button(
                                            "📥 CSV로 저장",
                                            csv,
                                            "conversion_result.csv",
                                            "text/csv",
                                            key="download_dangi"
                                        )
            else:  # 일본 연호
                with card("일본 연호 입력", icon="🗾"):
                    japanese_era = st.selectbox(
                        "일본 연호를 선택하세요:",
                        ["메이지 (明治/명치)", "다이쇼 (大正/대정)", "쇼와 (昭和/소화)"],
                        key="japanese_era"
                    )
                    
                    # 선택된 연호에 따라 max_value 동적 설정
                    if "메이지" in japanese_era:
                        max_year = 45
                        era_name = "메이지"
                    elif "다이쇼" in japanese_era:
                        max_year = 15
                        era_name = "다이쇼"
                    else:  # 쇼와
                        max_year = 64
                        era_name = "쇼와"
                    
                    jp_year = st.number_input(
                        "연도를 입력하세요:",
                        min_value=1,
                        max_value=max_year,
                        value=1,
                        help=f"해당 연호의 연도를 입력하세요. (1-{max_year}년)",
                        key="jp_year"
                    )
                    
                    if action_button("변환하기", key="convert_jp"):
                        with st.spinner("변환 중..."):
                            if is_valid_year(era_name, jp_year):
                                if "메이지" in japanese_era:
                                    segi_year = 1867 + jp_year
                                elif "다이쇼" in japanese_era:
                                    segi_year = 1911 + jp_year
                                else:  # 쇼와
                                    segi_year = 1925 + jp_year
                                
                                with result_box("✨ 변환 결과"):
                                    st.markdown(f'<div style="text-align: center; font-size: 1.2rem;">', unsafe_allow_html=True)
                                    st.markdown(f"{era_name} **{jp_year}**년은", unsafe_allow_html=True)
                                    st.markdown(f'<div style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">서기 {segi_year}년</div>', unsafe_allow_html=True)
                                    st.markdown("입니다.", unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    df = pd.DataFrame({
                                        '구분': ['일본 연호', '서기'],
                                        '연도': [f'{era_name} {jp_year}년', f'{segi_year}년']
                                    })
                                    csv = df.to_csv(index=False).encode('utf-8-sig')
                                    col1, col2, col3 = st.columns([1,2,1])
                                    with col2:
                                        st.download_button(
                                            "📥 CSV로 저장",
                                            csv,
                                            "conversion_result.csv",
                                            "text/csv",
                                            key="download_jp"
                                        )
                            else:
                                st.error(f"유효하지 않은 {era_name} 연도입니다. (1-{max_year}년)")
        
        with col2:
            with card("💡 도움말"):
                st.markdown("""
                1. 연호 유형을 선택하세요
                2. 연도를 입력하세요
                3. '변환하기' 버튼을 클릭하세요
                4. 결과를 CSV로 저장할 수 있습니다
                """)
    
    with tabs[1]:  # 자유 입력
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with card("자유 형식 입력", icon="✍️"):
                st.markdown("""
                다음과 같은 형식으로 입력할 수 있습니다:
                - 단기 4300년
                - 단기4300
                - 4300
                - 쇼와 1년 (소화 1년)
                - 메이지1년 (명치1년)
                - 다이쇼 1년 (대정 1년)
                
                💡 일본 연호는 한국식/일본식 표기 모두 사용 가능:
                - 메이지(明治) = 명치
                - 다이쇼(大正) = 대정
                - 쇼와(昭和) = 소화
                """)
                year_input = st.text_input(
                    "연도를 입력하세요:",
                    value="",
                    help="연호와 연도를 자유롭게 입력하세요.",
                    key="free_input",
                    placeholder="예: 단기 4300년, 쇼와 1년, 메이지5년"
                )
                
                if action_button("변환하기", key="convert_free"):
                    with st.spinner("변환 중..."):
                        era, year = parse_year_input(year_input)
                        if era and year:
                            segi_year = convert_to_segi(era, year)
                            if segi_year:
                                with result_box("✨ 변환 결과"):
                                    display_era = era
                                    if era in ["메이지", "다이쇼", "쇼와"]:
                                        display_value = f"{era} {year}년"
                                    else:
                                        display_value = f"단기 {year:,}년"
                                    
                                    st.markdown(f'<div style="text-align: center; font-size: 1.2rem;">', unsafe_allow_html=True)
                                    st.markdown(f"{display_value}은(는)", unsafe_allow_html=True)
                                    st.markdown(f'<div style="font-size: 2rem; font-weight: bold; margin: 1rem 0;">서기 {segi_year:,}년</div>', unsafe_allow_html=True)
                                    st.markdown("입니다.", unsafe_allow_html=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    df = pd.DataFrame({
                                        '구분': ['입력 연호', '서기'],
                                        '연도': [display_value, f'{segi_year:,}']
                                    })
                                    csv = df.to_csv(index=False).encode('utf-8-sig')
                                    col1, col2, col3 = st.columns([1,2,1])
                                    with col2:
                                        st.download_button(
                                            "📥 CSV로 저장",
                                            csv,
                                            "conversion_result.csv",
                                            "text/csv",
                                            key="download_free"
                                        )
                            else:
                                st.error("유효하지 않은 연도입니다.")
                        else:
                            st.error("입력 형식이 올바르지 않습니다. 예시와 같은 형식으로 입력해주세요.")
        
        with col2:
            with card("💡 도움말"):
                st.markdown("""
                1. 연호와 연도를 자유롭게 입력하세요
                2. '변환하기' 버튼을 클릭하세요
                3. 결과를 CSV로 저장할 수 있습니다
                
                **입력 예시**
                - 단기 4300년
                - 쇼와 1년 (소화 1년)
                - 메이지5년 (명치5년)
                """)
    
    with tabs[2]:  # 일괄 변환
        with card("파일 업로드", icon="📤"):
            st.markdown("""
            ### 📤 파일 업로드
            - CSV 또는 Excel 파일을 업로드하세요.
            - 파일에는 연호가 포함된 '생산년도' 칼럼이 있어야 합니다.
            - 지원하는 형식: 단기 4300년, 쇼와 1년, 메이지5년 등
            """)
            
            uploaded_file = st.file_uploader(
                "파일을 선택하세요",
                type=["csv", "xlsx", "xls"],
                help="CSV 또는 Excel 파일만 지원됩니다."
            )
            
            if uploaded_file is not None:
                try:
                    with st.spinner("파일 처리 중..."):
                        # 파일 확장자 확인
                        file_ext = uploaded_file.name.split(".")[-1].lower()
                        
                        if file_ext == "csv":
                            df = pd.read_csv(uploaded_file)
                        else:  # excel
                            df = pd.read_excel(uploaded_file)
                        
                        # 칼럼 선택
                        if "생산년도" in df.columns:
                            target_column = "생산년도"
                        else:
                            target_column = st.selectbox(
                                "변환할 연도가 포함된 칼럼을 선택하세요:",
                                df.columns.tolist()
                            )
                        
                        st.markdown("### 📊 데이터 미리보기")
                        st.dataframe(df.head())
                        
                        if action_button("일괄 변환하기", key="convert_batch"):
                            with st.spinner("변환 작업 진행 중..."):
                                # 변환 실행
                                converted_years, original_values = batch_convert_years(df, target_column)
                                
                                # 결과를 데이터프레임에 추가
                                df["원본_연도"] = original_values
                                df["변환_서기"] = converted_years
                                
                                # 결과 표시
                                with result_box("✨ 변환 결과"):
                                    success_count = sum(1 for x in converted_years if x is not None)
                                    fail_count = sum(1 for x in converted_years if x is None)
                                    
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("총 데이터", f"{len(df):,}건")
                                    with col2:
                                        st.metric("변환 성공", f"{success_count:,}건", delta=f"{success_count/len(df)*100:.1f}%")
                                    with col3:
                                        st.metric("변환 실패", f"{fail_count:,}건", delta=f"-{fail_count/len(df)*100:.1f}%")
                                    
                                    st.markdown("### 📊 결과 미리보기")
                                    st.dataframe(df)
                                    
                                    # 결과 다운로드
                                    st.markdown("### 💾 결과 저장")
                                    col1, col2, col3 = st.columns([1,1,1])
                                    with col1:
                                        csv = df.to_csv(index=False).encode('utf-8-sig')
                                        st.download_button(
                                            "📥 CSV로 저장",
                                            csv,
                                            f"변환결과_{uploaded_file.name}.csv",
                                            "text/csv",
                                            key="download_batch_csv"
                                        )
                                    with col2:
                                        excel_buffer = io.BytesIO()
                                        df.to_excel(excel_buffer, index=False)
                                        excel_data = excel_buffer.getvalue()
                                        st.download_button(
                                            "📥 Excel로 저장",
                                            excel_data,
                                            f"변환결과_{uploaded_file.name}.xlsx",
                                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key="download_batch_excel"
                                        )
                
                except Exception as e:
                    st.error(f"파일 처리 중 오류가 발생했습니다: {str(e)}")

# 주의사항
info_box("""
⚠️ **주의사항**
- 입력하는 연도는 해당 연호의 유효 기간 내의 값이어야 합니다:
  • 단기(檀紀): ~4335년 (서기 2002년)
  • 메이지(明治): 1-45년 (1868-1912)
  • 다이쇼(大正): 1-15년 (1912-1926)
  • 쇼와(昭和): 1-64년 (1926-1989)
- 사업 대상은 2002년 이하의 기록물입니다. 2002년을 초과하는 데이터는 오류로 처리됩니다.
- 변환된 연도는 참고용으로, 중요한 문서에 사용할 경우 반드시 검증이 필요합니다.
- 일괄 변환 시 변환할 수 없는 형식의 데이터는 원본 값이 유지됩니다.
""", "warning") 