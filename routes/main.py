from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash, jsonify, send_from_directory, Flask
from werkzeug.utils import secure_filename
from ultralytics import YOLO
from models import db, Result
from utils.file_utils import is_image, is_video
import os, uuid, threading

main_bp = Blueprint('main', __name__)
model = YOLO("yolov8n.pt")

def login_required_view(func):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ✅ 수정됨: 역슬래시 제거 처리 추가
@main_bp.route("/download/<path:filename>")
@login_required_view
def download(filename):
    filename = filename.replace('\\', '/')  # 웹 URL에서 역슬래시 제거
    return send_from_directory(current_app.config['RESULT_FOLDER'], filename, as_attachment=True)

@main_bp.route("/results/status")
@login_required_view
def results_status():
    username = session.get("username")
    result_folder = current_app.config['RESULT_FOLDER']
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
            # ✅ 수정됨: 경로 분리 및 웹 호환 경로로 변경
            filename_only = os.path.relpath(r.result_path, result_folder).replace(os.sep, '/')
            item['download_url'] = url_for('main.download', filename=filename_only)
        response.append(item)

    return jsonify(response)

@main_bp.route("/results")
@login_required_view
def results():
    username = session.get("username")
    results = Result.query.filter_by(username=username).order_by(Result.timestamp.desc()).all()
    result_folder = current_app.config['RESULT_FOLDER']

    for r in results:
        if r.result_path and r.result_path.startswith(result_folder):
            r.download_filename = os.path.relpath(r.result_path, result_folder).replace(os.sep, '/')
        else:
            r.download_filename = None

    return render_template("results.html", videos=results, username=username, result_folder=result_folder)

def run_yolo_in_background(app: Flask, result_record_id, input_path, filename, ext):
    with app.app_context():
        result_record = Result.query.get(result_record_id)
        try:
            result_path = None
            result_type = None

            if is_image(filename):
                result_filename = f"{uuid.uuid4().hex}.{ext}"
                result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
                results = model(input_path)
                results[0].save(filename=result_path)
                result_type = 'image'

            elif is_video(filename):
                temp_dir = os.path.join(app.config['RESULT_FOLDER'], uuid.uuid4().hex)
                os.makedirs(temp_dir, exist_ok=True)
                model.predict(source=input_path, save=True, project=temp_dir, name='predict', exist_ok=True)
                prediction_dir = os.path.join(temp_dir, 'predict')

                for f in os.listdir(prediction_dir):
                    if is_video(f):
                        result_path = os.path.join(prediction_dir, f)
                        result_type = 'video'
                        ext = f.rsplit('.', 1)[1].lower()
                        break

            if result_path and result_type:
                result_record.result_path = result_path
                result_record.result_type = result_type
                result_record.result_ext = ext
                result_record.status = 'done'
            else:
                result_record.status = 'error'

        except Exception:
            result_record.status = 'error'

        db.session.commit()

@main_bp.route("/", methods=["GET", "POST"])
@login_required_view
def index():
    username = session.get("username")
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
                flash("지원하지 않는 파일 형식입니다.", "danger")
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

        result_record = Result(
            username=username,
            original_filename=filename,
            status='processing'
        )
        db.session.add(result_record)
        db.session.commit()

        app_ctx = current_app._get_current_object()
        thread = threading.Thread(
            target=run_yolo_in_background,
            args=(app_ctx, result_record.id, input_path, filename, ext)
        )
        thread.start()

        return redirect(url_for('main.results'))

    return render_template("index.html", sample_files=sample_files, username=username)
