# 기록물 전산화 도구 모음

기록물 전산화를 위한 특수 목적 도구 모음입니다.

## 주요 기능

- 연호 변환기: 단기/일본 연호를 서기로 변환
- 추가 기능 개발 중

## 기술 스택

- Frontend: Streamlit
- 인증: streamlit-authenticator
- 데이터 처리: pandas
- API: FastAPI

## 로컬 개발 환경 설정

1. Python 3.12 이상 설치
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
3. 앱 실행:
   ```bash
   streamlit run app.py
   ```

## 배포 정보

이 애플리케이션은 Streamlit Community Cloud에서 호스팅됩니다.

- 배포 URL: [추후 업데이트 예정]
- 데모 계정:
  - 관리자: demo_admin / demo123
  - 일반 사용자: demo_user / demo123

## 보안 정보

- 실제 운영 환경에서는 반드시 다음 사항을 변경해야 합니다:
  - 데모 계정 제거
  - 새로운 관리자 계정 생성
  - 보안 키 재설정
  - 쿠키 설정 변경

## 라이선스

Apache License 2.0