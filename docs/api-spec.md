# API 명세서

## 인증 관련

### POST /register

-   설명: 회원가입
-   요청: username, password, confirm_password (form)
-   응답: 성공/실패 메시지, 리다이렉트
-   인증: 불필요

### POST /login

-   설명: 로그인
-   요청: username, password (form)
-   응답: 성공/실패 메시지, 세션 저장, 리다이렉트
-   인증: 불필요

### GET /logout

-   설명: 로그아웃
-   응답: 세션 초기화, 리다이렉트
-   인증: 필요

---

## 메인 기능

### GET,POST /

-   설명: 메인 페이지, 파일 업로드/샘플 선택 및 분석
-   요청: (POST) fileSelect, video(file)
-   응답: 분석 결과 렌더링(index.html)
-   인증: 필요

### GET /results

-   설명: 분석 결과 목록 조회
-   응답: 사용자별 분석 결과 리스트(results.html)
-   인증: 필요

---

## 파일/폴더 경로

-   업로드: static/uploads
-   결과: static/results
-   샘플: samples/
