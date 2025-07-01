# Flask-YOLO8 영상 분석 시스템

Flask와 YOLOv8을 사용한 객체 감지 웹 애플리케이션입니다. 사용자가 이미지나 비디오를 업로드하면 AI가 객체를 감지하고 분석 결과를 제공합니다.

## 주요 기능

-   **사용자 인증**: 회원가입, 로그인, 로그아웃
-   **파일 업로드**: 이미지(jpg, jpeg, png) 및 비디오(mp4, avi, mov) 업로드
-   **샘플 파일**: 테스트용 샘플 이미지/비디오 제공
-   **AI 분석**: YOLOv8을 사용한 실시간 객체 감지
-   **결과 관리**: 분석 결과 이력 조회 및 다운로드
-   **실시간 상태**: Ajax를 통한 실시간 처리 상태 확인

## 기술 스택

-   **백엔드**: Flask, SQLAlchemy, Flask-Migrate
-   **AI/ML**: Ultralytics (YOLOv8)
-   **프론트엔드**: Jinja2, Bootstrap, JavaScript
-   **데이터베이스**: SQLite
-   **보안**: Werkzeug (비밀번호 해시화), Flask-Session

## 프로젝트 구조

```
flask-yolo8/
├── app.py                 # Flask 앱 진입점
├── config.py              # 환경설정
├── models.py              # 데이터베이스 모델
├── requirements.txt       # 의존성 목록
├── yolov8n.pt            # YOLOv8 모델 파일
├── routes/                # 라우트 (블루프린트)
├── templates/             # Jinja2 템플릿
├── static/                # 정적 파일 (CSS, 업로드, 결과)
├── samples/               # 샘플 이미지/비디오
├── utils/                 # 유틸리티 함수
├── migrations/            # 데이터베이스 마이그레이션
└── docs/                  # 프로젝트 문서
```

## 문서

프로젝트에 대한 자세한 정보는 다음 문서들을 참조하세요:

-   **[프로젝트 구조](./docs/project-structure.md)** - 폴더 및 파일 구조, 주요 파일 설명
-   **[코드 흐름](./docs/code-flow.md)** - 애플리케이션 초기화부터 각 기능의 상세한 코드 흐름
-   **[데이터 흐름](./docs/data-flow.md)** - 시스템 아키텍처 및 데이터 처리 과정
-   **[API 명세서](./docs/api-spec.md)** - 모든 API 엔드포인트의 상세한 명세

## 설정

주요 설정은 `config.py`에서 관리됩니다:

-   `SECRET_KEY`: 세션 보안 키
-   `SQLALCHEMY_DATABASE_URI`: 데이터베이스 연결 문자열
-   `UPLOAD_FOLDER`: 업로드 파일 저장 경로
-   `RESULT_FOLDER`: 분석 결과 저장 경로
-   `SAMPLE_FOLDER`: 샘플 파일 경로

## 사용법

1. **회원가입/로그인**: 웹사이트에 접속하여 계정을 생성하고 로그인
2. **파일 업로드**: 새 파일을 업로드하거나 샘플 파일 선택
3. **분석 시작**: "분석 시작" 버튼을 클릭하여 YOLO 분석 실행
4. **결과 확인**: "결과 확인" 페이지에서 분석 결과 조회 및 다운로드

## 보안

-   비밀번호는 Werkzeug를 사용하여 해시화되어 저장
-   파일 업로드 시 확장자 화이트리스트 검증
-   세션 기반 인증으로 사용자 접근 제어
-   파일명 정규화로 보안 강화
