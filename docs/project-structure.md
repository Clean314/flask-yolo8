# 프로젝트 폴더 및 파일 구조

```
.
├── app.py                # Flask 앱 진입점
├── config.py             # 환경설정 클래스
├── models.py             # DB 모델 정의
├── requirements.txt      # 의존성 목록
├── yolov8n.pt            # YOLOv8 모델 파일
├── .gitignore
├── README.md
├── routes/               # 라우트(블루프린트) 폴더
│   ├── main.py           # 메인 기능 라우트
│   └── auth.py           # 인증 라우트
├── utils/                # 유틸리티 함수 폴더
│   └── file_utils.py     # 파일 확장자 판별 함수
├── static/               # 정적 파일 폴더
│   ├── css/
│   │   └── style.css     # 스타일시트
│   ├── uploads/          # 업로드 파일 저장
│   │   └── p.PNG         # 업로드된 이미지
│   └── results/          # 분석 결과 저장 폴더 (.gitkeep 포함)
├── samples/              # 샘플 이미지/비디오
│   ├── highway-7213206_1280.jpg
│   ├── night-7530755_1280.jpg
│   ├── 10881-226635366_medium.mp4
│   └── 215258_medium.mp4
├── templates/            # Jinja2 템플릿 폴더
│   ├── base.html         # 기본 템플릿
│   ├── index.html        # 메인 페이지 (파일 업로드 페이지)
│   ├── login.html        # 로그인 페이지
│   ├── register.html     # 회원가입 페이지
│   └── results.html      # 결과 페이지
├── migrations/           # 데이터베이스 마이그레이션
│   ├── alembic.ini       # Alembic 설정
│   ├── env.py            # 마이그레이션 환경 설정
│   ├── script.py.mako    # 마이그레이션 스크립트 템플릿
│   ├── README            # 마이그레이션 설명
│   └── versions/
│       └── 6cc98110be16_add_status_field_to_result.py  # 상태 필드 추가
├── flask_session/        # Flask 세션 저장소
│   └── 2029240f6d1128be89ddc32729463129  # 세션 파일
└── docs/                 # 프로젝트 문서
    ├── api-spec.md       # API 명세서
    ├── code-flow.md      # 코드 흐름 설명
    ├── data-flow.md      # 데이터 흐름 설명
    └── project-structure.md  # 프로젝트 구조 설명
```

## 주요 파일 설명

### 핵심 애플리케이션 파일

**app.py** - 웹사이트의 시작점

-   Flask 웹 서버를 시작하고 설정을 불러옵니다
-   데이터베이스와 세션을 초기화합니다
-   로그인/회원가입과 메인 기능 페이지를 연결합니다

**config.py** - 웹사이트 설정 파일

-   비밀번호 암호화 키, 데이터베이스 주소 등 중요한 설정들을 저장합니다
-   파일을 저장할 폴더 경로들을 지정합니다

**models.py** - 데이터베이스 테이블 설계

-   사용자 정보를 저장하는 User 테이블 (아이디, 비밀번호)
-   분석 결과를 저장하는 Result 테이블 (파일명, 결과 경로, 상태 등)

**requirements.txt** - 필요한 프로그램 목록

-   Flask, YOLO, 데이터베이스 등 웹사이트에 필요한 모든 프로그램들을 나열합니다

### 라우트 구조

**routes/main.py** - 메인 기능 담당

-   파일 업로드: 사용자가 이미지/비디오를 올리는 기능
-   YOLO 분석: 업로드된 파일을 AI로 분석하는 기능
-   결과 조회: 분석 결과를 보여주는 기능
-   파일 다운로드: 분석된 결과 파일을 다운로드하는 기능

**routes/auth.py** - 로그인/회원가입 담당

-   회원가입: 새로운 사용자 계정을 만드는 기능
-   로그인: 기존 사용자가 로그인하는 기능
-   로그아웃: 사용자가 로그아웃하는 기능

### 데이터베이스

**SQLite** - 사용자 정보와 분석 결과를 저장하는 데이터베이스

-   파일명: users.db
-   사용자 테이블: 아이디, 비밀번호 저장
-   결과 테이블: 분석한 파일 정보와 결과 저장

**마이그레이션** - 데이터베이스 구조 변경 관리

-   Alembic 도구를 사용해서 데이터베이스 구조를 안전하게 변경합니다
-   데이터 마이그레이션 : 데이터베이스 스키마의 변경사항(테이블, 컬럼 등)을 코드로 기록하고, 해당 변경을 DB에 안전하게 적용하는 절차

### 파일 관리

**static/uploads/** - 사용자가 올린 파일들이 저장되는 폴더 (파일명: 영문, 숫자, 점(.), 하이픈(-), 언더바(\_)만 허용, 한글/공백/특수문자 불가)
**static/results/** - AI 분석 결과 파일들이 저장되는 폴더
**samples/** - 테스트용 샘플 이미지/비디오 파일들
**utils/file_utils.py** - 파일 확장자 검사 기능 (jpg, png, mp4 등 허용)

### 개발 도구

**Flask-Migrate** - 데이터베이스 구조를 안전하게 변경하는 도구
**Flask-Session** - 사용자 로그인 상태를 서버에 저장하는 도구
**Ultralytics** - YOLOv8 AI 모델을 사용해서 객체를 감지하는 도구

## 기술 스택

### 백엔드 (서버 측)

-   **Flask**: Python으로 웹사이트를 만드는 프레임워크
-   **SQLAlchemy**: 데이터베이스를 쉽게 다루는 도구
-   **Flask-Migrate**: 데이터베이스 구조 변경 관리
-   **Flask-Session**: 사용자 로그인 상태 관리
-   **Werkzeug**: 보안 기능 (비밀번호 암호화 등)

### 프론트엔드 (웹페이지 디자인)

-   **Jinja2 템플릿**

    -   Python 웹 프레임워크에서 사용하는 템플릿 엔진 (Flask 기본 템플릿 엔진)
    -   HTML과 Python 데이터를 연결해주는 중간 매개체 역할

-   **Bootstrap CSS**

-   **JavaScript**

### AI/ML (인공지능)

-   **Ultralytics**: YOLOv8 객체 감지 모델을 사용하는 라이브러리
-   **YOLOv8n**: 빠르고 정확한 객체 감지 AI 모델

### 데이터베이스

-   **SQLite**: 가볍고 빠른 파일 기반 데이터베이스
-   **Alembic**: 데이터베이스 구조 변경 관리 도구
