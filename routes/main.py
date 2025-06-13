from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from models import db, Result
from utils.file_utils import is_image, is_video
import os, uuid

main_bp = Blueprint('main', __name__)
model = YOLO("yolov8n.pt")


def login_required_view(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@main_bp.route("/results")
@login_required_view
def results():  # ✅ 반드시 'results'로 이름 지정
    username = session.get("username")
    results = Result.query.filter_by(username=username).order_by(Result.timestamp.desc()).all()
    return render_template("results.html", videos=results, username=username)


@main_bp.route("/", methods=["GET", "POST"])
@login_required_view
def index():
    username = session.get("username")
    result_path = None
    result_type = None
    result_ext = None
    sample_files = os.listdir(current_app.config['SAMPLE_FOLDER'])

    if request.method == "POST":
        file_select = request.form.get("fileSelect")

        if file_select == "new":
            uploaded_file = request.files.get("video")
            if not uploaded_file or uploaded_file.filename == "":
                flash("파일이 선택되지 않았습니다.", "danger")
                return redirect(url_for('main.index'))

            filename = secure_filename(uploaded_file.filename)
            ext = filename.rsplit('.', 1)[1].lower()

            if not (is_image(filename) or is_video(filename)):
                flash("지원하지 않는 파일 형식입니다. jpg, jpeg, png, mp4, avi, mov 형식만 지원합니다.", "danger")
                return redirect(url_for('main.index'))

            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)
            input_path = save_path

        else:
            filename = file_select
            ext = filename.rsplit('.', 1)[1].lower()
            input_path = os.path.join(current_app.config['SAMPLE_FOLDER'], file_select)

            if not os.path.exists(input_path):
                flash("선택한 샘플 파일이 존재하지 않습니다.", "danger")
                return redirect(url_for('main.index'))

        # 분석 결과 파일명 생성
        result_filename = f"{uuid.uuid4().hex}.{ext}"
        result_path = os.path.join(current_app.config['RESULT_FOLDER'], result_filename)

        # YOLO 예측 수행
        if is_image(filename):
            results = model(input_path)
            results[0].save(filename=result_path)
            result_type = 'image'
            result_ext = ext

        elif is_video(filename):
            # YOLO 비디오 처리 → predict 폴더 내 저장됨
            temp_dir = os.path.join(current_app.config['RESULT_FOLDER'], uuid.uuid4().hex)
            os.makedirs(temp_dir, exist_ok=True)

            model.predict(source=input_path, save=True, project=temp_dir, name='predict', exist_ok=True)

            prediction_dir = os.path.join(temp_dir, 'predict')
            found = False

            for f in os.listdir(prediction_dir):
                if is_video(f):
                    result_path = os.path.join(prediction_dir, f)
                    result_type = 'video'
                    result_ext = f.rsplit('.', 1)[1].lower()
                    found = True
                    break

            if not found:
                flash("YOLO 분석 결과에서 비디오를 찾지 못했습니다.", "danger")
                return redirect(url_for('main.index'))

        if result_type is None:
            flash("파일 처리 중 오류가 발생했습니다. 지원되지 않는 형식이거나 분석 결과를 생성할 수 없습니다.", "danger")
            return redirect(url_for('main.index'))

        # DB 저장
        db.session.add(Result(
            username=username,
            original_filename=filename,
            result_path=result_path,
            result_type=result_type,
            result_ext=result_ext
        ))
        db.session.commit()

        return render_template("index.html", sample_files=sample_files,
                               result_path=result_path,
                               result_type=result_type,
                               result_ext=result_ext,
                               username=username)

    return render_template("index.html", sample_files=sample_files,
                           username=username)
