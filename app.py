from flask import Flask
from flask_session import Session
from models import db
from config import Config
from routes.auth import auth_bp
from routes.main import main_bp
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

# DB 마이그레이션 초기화
migrate = Migrate(app, db)
db.init_app(app)

# 세션 스토리지 (서버 측 세션)
Session(app)

# DB 테이블 생성
with app.app_context():
    db.create_all()

# 라우트 등록
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
