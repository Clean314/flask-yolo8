class Config:
        """
        Flask 앱 설정
        """
        SECRET_KEY = 'asdf-secret-key'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
        JWT_SECRET_KEY = '938a3jbcx2gwoi2876831dhagb'
        SESSION_TYPE = 'filesystem'
        UPLOAD_FOLDER = 'static/uploads'
        RESULT_FOLDER = 'static/results'
        SAMPLE_FOLDER = 'samples'