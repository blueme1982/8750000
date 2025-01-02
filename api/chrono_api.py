from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from typing import Optional

app = FastAPI(
    title="연호 변환 API",
    description="단기/일본 연호를 서기로 변환하는 API",
    version="1.0.0"
)

class YearInput(BaseModel):
    """연호 입력 모델"""
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "단기 4356"
            }
        }

class ConversionResult(BaseModel):
    """연호 변환 결과 모델"""
    input_text: str
    era: Optional[str] = None
    original_year: Optional[int] = None
    segi_year: Optional[int] = None
    is_valid: bool
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_text": "단기 4356",
                "era": "단기",
                "original_year": 4356,
                "segi_year": 2023,
                "is_valid": True,
                "message": None
            }
        }

def parse_year_input(text: str) -> tuple[Optional[str], Optional[int]]:
    """입력 텍스트에서 연호와 연도를 추출
    
    Args:
        text (str): 입력 텍스트 (예: "단기 4356", "메이지 3년")
        
    Returns:
        tuple[Optional[str], Optional[int]]: (연호, 연도) 또는 파싱 실패시 (None, None)
    """
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

def is_valid_year(era: str, year: int) -> bool:
    """연호별 유효 기간 검증
    
    Args:
        era (str): 연호 ("단기", "메이지", "다이쇼", "쇼와")
        year (int): 연도
        
    Returns:
        bool: 유효한 연도인지 여부
    """
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

def convert_to_segi(era: str, year: int) -> Optional[int]:
    """연호와 연도를 서기로 변환
    
    Args:
        era (str): 연호 ("단기", "메이지", "다이쇼", "쇼와")
        year (int): 연도
        
    Returns:
        Optional[int]: 서기 연도 또는 변환 실패시 None
    """
    if not is_valid_year(era, year):
        return None
        
    if era == "단기":
        return year - 2333
    elif era == "메이지":
        return 1867 + year
    elif era == "다이쇼":
        return 1911 + year
    elif era == "쇼와":
        return 1925 + year
    
    return None

@app.post("/convert", response_model=ConversionResult, tags=["연호 변환"])
async def convert_year(input_data: YearInput) -> ConversionResult:
    """연호를 서기로 변환
    
    입력된 연호(단기/일본 연호)를 서기 연도로 변환합니다.
    지원하는 연호:
    - 단기: 모든 양수 연도 (서기 2002년 이하)
    - 메이지: 1-45년 (1868-1912)
    - 다이쇼: 1-15년 (1912-1926)
    - 쇼와: 1-64년 (1926-1989)
    
    Args:
        input_data (YearInput): 변환할 연호 텍스트
        
    Returns:
        ConversionResult: 변환 결과
    """
    era, year = parse_year_input(input_data.text)
    
    if not era or not year:
        return ConversionResult(
            input_text=input_data.text,
            is_valid=False,
            message="입력 형식이 올바르지 않습니다."
        )
    
    segi_year = convert_to_segi(era, year)
    
    if not segi_year:
        return ConversionResult(
            input_text=input_data.text,
            era=era,
            original_year=year,
            is_valid=False,
            message="유효하지 않은 연도입니다."
        )
    
    return ConversionResult(
        input_text=input_data.text,
        era=era,
        original_year=year,
        segi_year=segi_year,
        is_valid=True,
        message=None
    )

@app.get("/", tags=["API 정보"])
async def root():
    """API 정보"""
    return {
        "name": "연호 변환 API",
        "version": "1.0.0",
        "description": "단기/일본 연호를 서기로 변환하는 API",
        "endpoints": {
            "/convert": "연호를 서기로 변환 (POST)",
            "/docs": "API 문서 (Swagger UI)",
            "/redoc": "API 문서 (ReDoc)"
        }
    } 