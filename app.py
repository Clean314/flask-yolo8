from flask import Flask
from flask_session import Session
from models import db
from config import Config
from routes.auth import auth_bp
from routes.main import main_bp
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
migrate = Migrate(app, db)

db.init_app(app)
Session(app)

with app.app_context():
    db.create_all()

# Blueprint 등록
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
