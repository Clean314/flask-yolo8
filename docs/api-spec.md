# API 명세서

## 인증 관련 API

### POST /register

**회원가입**

-   **설명**: 새로운 사용자 계정 생성
-   **요청 방식**: POST
-   **Content-Type**: application/x-www-form-urlencoded
-   **인증**: 불필요

**요청 파라미터**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| username | string | ✓ | 사용자명 (고유값) |
| password | string | ✓ | 비밀번호 |
| confirm_password | string | ✓ | 비밀번호 확인 |

**응답**

-   **성공**: 302 리다이렉트 → /login
-   **실패**: 200 (register.html 렌더링)
-   **플래시 메시지**: "회원가입 성공! 로그인 해주세요." / "비밀번호가 일치하지 않습니다." / "이미 존재하는 사용자입니다."

### POST /login

**로그인**

-   **설명**: 사용자 인증 및 세션 생성
-   **요청 방식**: POST
-   **Content-Type**: application/x-www-form-urlencoded
-   **인증**: 불필요

**요청 파라미터**
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| username | string | ✓ | 사용자명 |
| password | string | ✓ | 비밀번호 |

**응답**

-   **성공**: 302 리다이렉트 → /
-   **실패**: 200 (login.html 렌더링)
-   **플래시 메시지**: "로그인 성공!" / "로그인 실패. 사용자명을 확인하세요."

### GET /logout

**로그아웃**

-   **설명**: 세션 초기화 및 로그아웃
-   **요청 방식**: GET
-   **인증**: 필요 (세션)

**응답**

-   **성공**: 302 리다이렉트 → /login
-   **플래시 메시지**: "로그아웃 되었습니다."

---

## 메인 기능 API

### GET /

**메인 페이지**

-   **설명**: 파일 업로드 및 샘플 선택 화면
-   **요청 방식**: GET
-   **인증**: 필요 (세션)

**응답**

-   **성공**: 200 (index.html 렌더링)
-   **실패**: 302 리다이렉트 → /login

**템플릿 변수**

-   `sample_files`: samples/ 폴더의 파일 목록
-   `username`: 현재 로그인한 사용자명

### POST /

**파일 업로드 및 분석**

-   **설명**: 파일 업로드 또는 샘플 선택 후 YOLO 분석 실행
-   **요청 방식**: POST
-   **Content-Type**: multipart/form-data
-   **인증**: 필요 (세션)

**요청 파라미터**
| 파라미터 | 타입 | 필수 | 조건 | 설명 |
|----------|------|------|------|------|
| fileSelect | string | ✓ | - | "new" 또는 샘플 파일명 |
| video | file | 조건부 | fileSelect="new" | 업로드할 파일 |

**지원 파일 형식**

-   **이미지**: jpg, jpeg, png
-   **비디오**: mp4, avi, mov

**파일명 규칙**

-   파일명에는 영문, 숫자, 점(.), 하이픈(-), 언더바(\_)만 사용할 수 있습니다.
-   한글, 공백, 기타 특수문자가 포함된 파일명은 업로드할 수 없습니다.

**응답**

-   **성공**: 302 리다이렉트 → /results
-   **실패**: 302 리다이렉트 → / (플래시 메시지와 함께)
-   **플래시 메시지**: "파일이 선택되지 않았습니다." / "지원하지 않는 파일 형식입니다." / "선택한 샘플 파일이 존재하지 않습니다."

### GET /results

**분석 결과 목록**

-   **설명**: 사용자별 YOLO 분석 결과 목록 조회
-   **요청 방식**: GET
-   **인증**: 필요 (세션)

**응답**

-   **성공**: 200 (results.html 렌더링)
-   **실패**: 302 리다이렉트 → /login

**템플릿 변수**

-   `videos`: Result 객체 리스트 (최신순 정렬)
-   `username`: 현재 사용자명
-   `result_folder`: 결과 파일 폴더 경로

### GET /results/status

**실시간 상태 확인**

-   **설명**: Ajax를 통한 실시간 처리 상태 확인
-   **요청 방식**: GET
-   **인증**: 필요 (세션)
-   **Content-Type**: application/json

**응답**

```json
[
    {
        "id": 1,
        "filename": "example.jpg",
        "status": "done",
        "result_type": "image",
        "download_url": "/download/abc123.jpg"
    }
]
```

**상태값**

-   `processing`: 처리 중
-   `done`: 처리 완료
-   `error`: 처리 오류

### GET /download/<filename>

**결과 파일 다운로드**

-   **설명**: 분석 결과 파일 다운로드
-   **요청 방식**: GET
-   **인증**: 필요 (세션)

**URL 파라미터**
| 파라미터 | 타입 | 설명 |
|----------|------|------|
| filename | string | 다운로드할 파일명 |

**응답**

-   **성공**: 200 (파일 첨부)
-   **실패**: 404 (파일 없음)

---

## 에러 처리

### 인증 에러

-   세션이 없는 경우: `/login`으로 리다이렉트
-   플래시 메시지로 에러 안내

### 파일 처리 에러

-   지원하지 않는 파일 형식
-   파일 업로드 실패
-   샘플 파일 존재하지 않음

### YOLO 분석 에러

-   모델 로딩 실패
-   분석 처리 중 오류
-   결과 파일 생성 실패

---

## 파일 경로 설정

### 환경 설정 (config.py)

```python
UPLOAD_FOLDER = 'static/uploads'      # 업로드 파일 저장
RESULT_FOLDER = 'static/results'      # 분석 결과 저장
SAMPLE_FOLDER = 'samples'             # 샘플 파일 위치
```

### 실제 파일 경로

-   **업로드**: `static/uploads/[파일명]`
-   **결과**: `static/results/[UUID].[확장자]` (이미지)
-   **결과**: `static/results/[UUID]/predict/[파일명]` (비디오)
-   **샘플**: `samples/[파일명]`

---

## 보안 고려사항

### 인증 보안

-   비밀번호 해시화 (Werkzeug)
-   세션 기반 인증
-   로그인 데코레이터

### 파일 업로드 보안

-   파일명 정규화 (secure_filename)
-   확장자 화이트리스트 검증
-   파일 크기 제한 (Flask 기본값)

### 세션 보안

-   서버 측 세션 저장
-   SECRET_KEY 설정
-   세션 타임아웃 관리

---

## 데이터베이스 스키마

### User 테이블

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL
);
```

### Result 테이블

```sql
CREATE TABLE result (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    original_filename VARCHAR(200) NOT NULL,
    result_path VARCHAR(200),
    result_type VARCHAR(20),
    result_ext VARCHAR(20),
    status VARCHAR(20) DEFAULT 'processing',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 성능 최적화

### 비동기 처리

-   YOLO 분석을 백그라운드 스레드에서 실행
-   사용자 요청 응답 지연 방지

### 캐싱

-   세션 데이터 파일시스템 캐싱
-   정적 파일 브라우저 캐싱

### 데이터베이스

-   인덱스: username, timestamp
-   쿼리 최적화: 사용자별 결과 조회
