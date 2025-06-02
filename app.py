from flask import Flask, request, render_template
import os, uuid
from ultralytics import YOLO

app = Flask(__name__)
UPLOAD_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# YOLOv8 모델 로드
model = YOLO("yolov8n.pt")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        filename = f"{uuid.uuid4().hex}.jpg"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # YOLO 추론 및 저장
        results = model(path)
        results[0].save(filename=path)

        return render_template("index.html", result_img=path)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
