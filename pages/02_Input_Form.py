import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="기록물 메타데이터 입력",
    page_icon="📝",
    layout="wide"
)

def convert_year(text: str) -> dict:
    """API를 호출하여 연호를 변환합니다."""
    if not text:
        return {
            "is_valid": False,
            "message": "연도를 입력해주세요."
        }
    
    try:
        response = requests.post(
            "https://8750000-q8ubvx9pkgdh3kv3na4scy.streamlit.app/api/convert",
            json={"text": text},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {str(e)}")
        return {
            "is_valid": False,
            "message": "서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요."
        }

def on_year_change():
    """생산년도 입력값이 변경될 때 호출되는 콜백 함수"""
    if 'year' in st.session_state and st.session_state.year:
        result = convert_year(st.session_state.year)
        if result["is_valid"]:
            st.session_state.segi_year = result["segi_year"]
            st.session_state.dangi_year = result["original_year"]
            st.session_state.year_valid = True
        else:
            st.session_state.year_valid = False
            st.session_state.year_error = result["message"]

def main():
    st.title("기록물 메타데이터 입력")
    
    # 세션 상태 초기화
    if 'metadata_list' not in st.session_state:
        st.session_state.metadata_list = []
    if 'year_valid' not in st.session_state:
        st.session_state.year_valid = False
    
    # 메타데이터 입력 섹션
    st.subheader("메타데이터 입력")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        title = st.text_input(
            "제목",
            placeholder="기록물 제목을 입력하세요",
            help="기록물의 제목을 입력하세요.",
            key="title"
        )
    
    with col2:
        year = st.text_input(
            "생산년도",
            placeholder="예: 단기 4356",
            help="단기 연도를 입력하세요. 자동으로 서기로 변환됩니다.",
            key="year",
            on_change=on_year_change
        )
        
        # 연도 변환 결과 표시
        if 'year_valid' in st.session_state:
            if st.session_state.year_valid:
                st.success(f"서기: {st.session_state.segi_year}년")
            elif 'year_error' in st.session_state and st.session_state.year:
                st.error(st.session_state.year_error)
    
    with col3:
        department = st.text_input(
            "생산부서",
            placeholder="생산부서를 입력하세요",
            help="기록물을 생산한 부서명을 입력하세요.",
            key="department"
        )
    
    # 추가 버튼
    if st.button("메타데이터 추가", use_container_width=True, type="primary"):
        if not all([title, year, department]):
            st.error("모든 필드를 입력해주세요.")
        elif not st.session_state.year_valid:
            st.error("유효한 생산년도를 입력해주세요.")
        else:
            # 메타데이터 추가
            metadata = {
                "제목": title,
                "생산년도(단기)": st.session_state.dangi_year,
                "생산년도(서기)": st.session_state.segi_year,
                "생산부서": department
            }
            st.session_state.metadata_list.append(metadata)
            st.success("메타데이터가 추가되었습니다.")
            
            # 입력 필드 초기화
            for key in ["title", "year", "department"]:
                st.session_state[key] = ""
            st.session_state.year_valid = False
            st.rerun()
    
    # 구분선
    st.divider()
    
    # 메타데이터 테이블 표시
    if st.session_state.metadata_list:
        st.subheader("입력된 메타데이터")
        df = pd.DataFrame(st.session_state.metadata_list)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "제목": st.column_config.TextColumn(
                    "제목",
                    width="large"
                ),
                "생산년도(단기)": st.column_config.NumberColumn(
                    "생산년도(단기)",
                    help="단기 연도"
                ),
                "생산년도(서기)": st.column_config.NumberColumn(
                    "생산년도(서기)",
                    help="서기 연도"
                ),
                "생산부서": st.column_config.TextColumn(
                    "생산부서",
                    width="medium"
                )
            }
        )
        
        col1, col2 = st.columns(2)
        with col1:
            # 데이터 다운로드 버튼
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="CSV 다운로드",
                data=csv,
                file_name="metadata.csv",
                mime="text/csv",
                help="입력된 메타데이터를 CSV 파일로 다운로드합니다.",
                use_container_width=True
            )
        
        with col2:
            # 테이블 초기화 버튼
            if st.button("테이블 초기화", type="secondary", use_container_width=True):
                st.session_state.metadata_list = []
                st.rerun()

if __name__ == "__main__":
    main() 