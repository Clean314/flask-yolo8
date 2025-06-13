ALLOWED_IMAGE_EXT = {'jpg', 'jpeg', 'png'}
ALLOWED_VIDEO_EXT = {'mp4', 'avi', 'mov'}

def is_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXT

def is_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXT