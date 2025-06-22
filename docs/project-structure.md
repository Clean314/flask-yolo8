# 프로젝트 폴더 및 파일 구조

```
.
├── app.py                # Flask 앱 진입점
├── config.py             # 환경설정 클래스
├── models.py             # DB 모델 정의
├── requirements.txt      # 의존성 목록
├── yolov8n.pt            # YOLOv8 모델 파일
├── routes/               # 라우트(블루프린트) 폴더
│   ├── main.py           # 메인 기능 라우트
│   └── auth.py           # 인증 라우트
├── utils/                # 유틸리티 함수 폴더
│   └── file_utils.py     # 파일 확장자 판별 함수
├── static/               # 정적 파일 폴더
│   ├── css/
│   │   └── style.css     # 스타일시트
│   └── uploads/          # 업로드 파일 저장
├── samples/              # 샘플 이미지/비디오
├── templates/            # Jinja2 템플릿 폴더
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── results.html
│   └── upload.html
└── README.md
```

-   **app.py**: 앱 실행, 블루프린트 등록, DB/세션 초기화
-   **routes/**: 인증/메인 기능 라우트 분리
-   **models.py**: User, Result 모델 정의
-   **utils/**: 파일 확장자 체크 함수
-   **static/**: 업로드 파일, CSS 등 정적 자원
-   **samples/**: 샘플 데이터
-   **templates/**: 프론트엔드 템플릿
