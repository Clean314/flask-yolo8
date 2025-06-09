from flask import Flask, request, render_template
import os, uuid
from ultralytics import YOLO
from glob import glob

app = Flask(__name__)
RESULT_FOLDER = 'static/results'
SAMPLE_FOLDER = 'samples'
os.makedirs(RESULT_FOLDER, exist_ok=True)

model = YOLO("yolov8n.pt")

ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png'}
ALLOWED_VIDEO_EXT = {'mp4', 'avi', 'mov'}

def is_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

def is_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

@app.route("/", methods=["GET", "POST"])
def index():
    result_path = None
    result_type = None
    sample_files = os.listdir(SAMPLE_FOLDER)

    if request.method == "POST":
        selected_file = request.form.get("selected_file")
        full_path = os.path.join(SAMPLE_FOLDER, selected_file)
        ext = selected_file.rsplit('.', 1)[1].lower()

        if not os.path.exists(full_path):
            return "파일이 존재하지 않습니다.", 404

        # 결과 저장 경로 설정
        result_filename = f"{uuid.uuid4().hex}.{ext}"
        result_path = os.path.join(RESULT_FOLDER, result_filename)

        # 이미지 처리
        if is_image(selected_file):
            results = model(full_path)
            results[0].save(filename=result_path)
            result_type = 'image'

        # 비디오 처리
        elif is_video(selected_file):
            # YOLO는 디렉터리 저장을 하므로 임시 디렉터리 사용
            temp_dir = os.path.join(RESULT_FOLDER, uuid.uuid4().hex)
            model.predict(source=full_path, save=True, project=temp_dir, name='', exist_ok=True)
            # 저장된 비디오 경로 찾기
            for f in os.listdir(temp_dir):
                if is_video(f):
                    result_path = os.path.join(temp_dir, f)
                    result_type = 'video'
                    break

    return render_template("index.html",
                           sample_files=sample_files,
                           result_path=result_path,
                           result_type=result_type)
