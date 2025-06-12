from flask import Flask, request, render_template, session, redirect, url_for, flash
import os, uuid
from ultralytics import YOLO
from glob import glob
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Flask 애플리케이션의 보안을 위한 시크릿 키 설정
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_secret_key_123')

# YOLO 분석 결과물이 저장될 디렉토리
RESULT_FOLDER = 'static/results'
# 사용자가 업로드한 원본 파일이 저장될 디렉토리
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 사용자 정보를 임시로 저장하는 딕셔너리 (실제 서비스에서는 DB 사용 필요)
users = {}

# YOLO 객체 탐지 모델 초기화
model = YOLO("yolov8n.pt")

# 처리 가능한 파일 확장자 정의
ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png'}
ALLOWED_VIDEO_EXT = {'mp4', 'avi', 'mov'}

# 파일이 허용된 비디오 형식인지 확인
def is_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXT

# 파일이 허용된 이미지 형식인지 확인
def is_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXT

# 메인 페이지 - 비로그인 사용자는 로그인 페이지로 리다이렉트
@app.route('/', methods=['GET', 'POST'])
def index():
    # 비로그인 사용자는 로그인 페이지로 리다이렉트
    if 'username' not in session:
        return redirect(url_for('login_get'))
    
    if request.method == 'POST':
        # 파일 업로드 및 분석 요청 처리
        file_select = request.form.get('fileSelect')
        
        if file_select == 'new':
            # 새 파일 업로드 처리
            if 'video' not in request.files:
                flash('비디오 파일을 선택해주세요.', 'error')
                return redirect(url_for('index'))
                
            file = request.files['video']
            if file.filename == '':
                flash('파일이 선택되지 않았습니다.', 'error')
                return redirect(url_for('index'))
                
            if not is_video(file.filename):
                flash('허용되지 않는 파일 형식입니다.', 'error')
                return redirect(url_for('index'))
                
            # 업로드된 파일을 안전한 이름으로 저장
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            # 이전 업로드 파일 재사용
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_select)
            if not os.path.exists(filepath):
                flash('선택한 파일을 찾을 수 없습니다.', 'error')
                return redirect(url_for('index'))
            filename = file_select
        
        # YOLO 모델을 사용하여 영상 분석 수행
        result_dir = os.path.join(RESULT_FOLDER, uuid.uuid4().hex)
        model.predict(source=filepath, save=True, project=result_dir, name='', exist_ok=True)
        
        # 분석 결과 파일을 찾아서 사용자의 비디오 목록에 추가
        for f in os.listdir(result_dir):
            if is_video(f):
                result_path = os.path.join(result_dir, f)
                users[session['username']]['videos'].append({
                    'original': filename,
                    'result': result_path
                })
                break
                
        flash('비디오가 성공적으로 분석되었습니다.', 'success')
        return redirect(url_for('results'))
    
    # GET 요청 처리 - 업로드 페이지 렌더링
    previous_files = []
    if session['username'] in users and 'videos' in users[session['username']]:
        for video in users[session['username']]['videos']:
            previous_files.append({
                'name': os.path.basename(video['original']),
                'path': video['original']
            })
    
    return render_template('upload.html', previous_files=previous_files)

# 로그인 페이지 렌더링 - 이미 로그인한 사용자는 메인 페이지로 리다이렉트
@app.route('/login', methods=['GET'])
def login_get():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

# 로그인 요청 처리 - 사용자 인증 후 세션에 사용자 정보 저장
@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and check_password_hash(users[username]['password'], password):
        session['username'] = username
        flash('로그인되었습니다.', 'success')
        return redirect(url_for('index'))
    flash('잘못된 사용자명 또는 비밀번호입니다.', 'error')
    return redirect(url_for('login_get'))

# 회원가입 페이지 렌더링
@app.route('/register', methods=['GET'])
def register_get():
    return render_template('register.html')

# 회원가입 요청 처리 - 새로운 사용자 정보 저장
@app.route('/register', methods=['POST'])
def register_post():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    if username in users:
        flash('이미 존재하는 사용자명입니다.', 'error')
    elif password != confirm_password:
        flash('비밀번호가 일치하지 않습니다.', 'error')
    else:
        users[username] = {
            'password': generate_password_hash(password),
            'videos': []
        }
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('login_get'))
    return redirect(url_for('register_get'))

# 로그아웃 처리 - 세션에서 사용자 정보 제거
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('login_get'))

# 분석 결과 페이지 렌더링 - 사용자별 분석된 비디오 목록 표시
@app.route('/results')
def results():
    if 'username' not in session:
        return redirect(url_for('login_get'))
    user_videos = users[session['username']]['videos']
    return render_template('results.html', videos=user_videos)

# 디버그 모드로 개발 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
