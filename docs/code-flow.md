# 코드 흐름 설명

## 1. 애플리케이션 초기화 (app.py)

```python
# Flask 인스턴스 생성 및 설정 적용
app = Flask(__name__)
app.config.from_object(Config)

# 데이터베이스 및 마이그레이션 초기화
migrate = Migrate(app, db)
db.init_app(app)

# 서버 측 세션 설정
Session(app)

# 블루프린트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
```

### 초기화 순서

1. Flask 인스턴스 생성
2. Config 클래스에서 설정 로드
3. SQLAlchemy 및 Flask-Migrate 초기화
4. Flask-Session 설정 (파일시스템 기반)
5. 데이터베이스 테이블 생성
6. 인증/메인 블루프린트 등록

## 2. 인증 플로우 (routes/auth.py)

### 회원가입 (/register)

```python
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 1. 사용자명 중복 확인
        if User.query.filter_by(username=username).first():
            flash("이미 존재하는 사용자입니다.", "danger")

        # 2. 비밀번호 일치 확인
        if password != confirm:
            flash("비밀번호가 일치하지 않습니다.", "danger")

        # 3. 비밀번호 해시화 후 저장
        user = User(username=username, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
```

### 로그인 (/login)

```python
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1. 사용자명으로 User 조회
        user = User.query.filter_by(username=username).first()

        # 2. 비밀번호 해시 검증
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('main.index'))
```

### 로그아웃 (/logout)

```python
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for('auth.login'))
```

## 3. 메인 기능 플로우 (routes/main.py)

### 로그인 데코레이터

```python
def login_required_view(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
```

### 메인 페이지 (/) - GET

```python
@main_bp.route("/", methods=["GET", "POST"])
@login_required_view
def index():
    # 1. 로그인 상태 확인
    username = session.get("username")

    # 2. 샘플 파일 목록 조회
    sample_files = os.listdir(current_app.config['SAMPLE_FOLDER'])

    # 3. 템플릿 렌더링
    return render_template("index.html", sample_files=sample_files, username=username)
```

### 파일 업로드/분석 (/) - POST

```python
if request.method == "POST":
    file_select = request.form.get("fileSelect")

    if file_select == "new":
        # 새 파일 업로드 처리
        uploaded_file = request.files.get("video")
        filename = secure_filename(uploaded_file.filename)

        # 파일 확장자 검증
        if not (is_image(filename) or is_video(filename)):
            flash("지원하지 않는 파일 형식입니다.", "danger")

        # 파일 저장
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(save_path)

    else:
        # 샘플 파일 선택
        filename = file_select
        input_path = os.path.join(current_app.config['SAMPLE_FOLDER'], file_select)

    # Result 레코드 생성
    result_record = Result(
        username=username,
        original_filename=filename,
        status='processing'
    )
    db.session.add(result_record)
    db.session.commit()

    # 백그라운드 YOLO 분석 시작
    thread = threading.Thread(
        target=run_yolo_in_background,
        args=(app_ctx, result_record.id, input_path, filename, ext)
    )
    thread.start()
```

### YOLO 분석 (백그라운드)

```python
def run_yolo_in_background(app: Flask, result_record_id, input_path, filename, ext):
    with app.app_context():
        result_record = Result.query.get(result_record_id)

        try:
            if is_image(filename):
                # 이미지 처리
                result_filename = f"{uuid.uuid4().hex}.{ext}"
                result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                results = model(input_path)
                results[0].save(filename=result_path)
                result_type = 'image'

            elif is_video(filename):
                # 비디오 처리
                temp_dir = os.path.join(app.config['RESULT_FOLDER'], uuid.uuid4().hex)
                os.makedirs(temp_dir, exist_ok=True)
                model.predict(source=input_path, save=True, project=temp_dir, name='predict')

            # 상태 업데이트
            result_record.status = 'done'
            result_record.result_path = result_path
            result_record.result_type = result_type

        except Exception:
            result_record.status = 'error'

        db.session.commit()
```

### 결과 조회 (/results)

```python
@main_bp.route("/results")
@login_required_view
def results():
    username = session.get("username")
    results = Result.query.filter_by(username=username).order_by(Result.timestamp.desc()).all()

    # 다운로드 URL 생성
    for r in results:
        if r.result_path and r.result_path.startswith(result_folder):
            r.download_filename = os.path.relpath(r.result_path, result_folder)

    return render_template("results.html", videos=results, username=username)
```

### 실시간 상태 확인 (/results/status)

```python
@main_bp.route("/results/status")
@login_required_view
def results_status():
    username = session.get("username")
    results = Result.query.filter_by(username=username).order_by(Result.timestamp.desc()).all()

    response = []
    for r in results:
        item = {
            'id': r.id,
            'filename': r.original_filename,
            'status': r.status,
            'result_type': r.result_type,
            'download_url': None
        }
        if r.status == 'done' and r.result_path:
            item['download_url'] = url_for('main.download', filename=filename_only)
        response.append(item)

    return jsonify(response)
```

### 파일 다운로드 (/download/<filename>)

```python
@main_bp.route("/download/<path:filename>")
@login_required_view
def download(filename):
    filename = filename.replace('\\', '/')
    return send_from_directory(current_app.config['RESULT_FOLDER'], filename, as_attachment=True)
```

## 4. 데이터 모델 (models.py)

### User 모델

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
```

### Result 모델

```python
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    result_path = db.Column(db.String(200), nullable=True)
    result_type = db.Column(db.String(20), nullable=True)
    result_ext = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='processing')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
```

## 5. 파일 처리 유틸리티 (utils/file_utils.py)

### 지원 파일 형식

```python
ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png'}
ALLOWED_VIDEO_EXT = {'mp4', 'avi', 'mov'}
```

### 검증 함수

```python
def is_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXT

def is_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXT
```

## 6. 설정 관리 (config.py)

```python
class Config:
    SECRET_KEY = 'asdf-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    JWT_SECRET_KEY = '938a3jbcx2gwoi2876831dhagb'
    SESSION_TYPE = 'filesystem'
    UPLOAD_FOLDER = 'static/uploads'
    RESULT_FOLDER = 'static/results'
    SAMPLE_FOLDER = 'samples'
```

## 7. 보안 및 인증

### 비밀번호 보안

-   Werkzeug의 `generate_password_hash()` 사용
-   `check_password_hash()`로 검증

### 파일 업로드 보안

-   `secure_filename()`으로 파일명 정규화
-   확장자 화이트리스트 검증

### 세션 보안

-   서버 측 세션 저장 (파일시스템)
-   로그인 데코레이터로 보호된 라우트

## 8. 비동기 처리

### 백그라운드 스레드

-   YOLO 분석을 별도 스레드에서 실행
-   사용자 요청 응답 지연 방지
-   실시간 상태 확인을 통한 진행 상황 모니터링
