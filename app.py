from flask import Flask, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)

# allow all origin
CORS(app)

# Uploaded images folder path
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'image')

# Ensure folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Rate limiter
limiter_5 = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])


# Helper function — allowed image formats
def allowed_images(filename):
    if '.' not in filename:
        return False
    allowed_extensions = ('png', 'jpg', 'jpeg', 'gif')
    return filename.rsplit('.')[-1].lower() in allowed_extensions


# ---------------------------
# Upload endpoint
# ---------------------------
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Image input is required in the form'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400

    if not allowed_images(file.filename):
        return jsonify({
            'error': 'Invalid image format. Allowed formats: png, jpg, jpeg, gif'
        }), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        return jsonify({'error': 'Image with the same name already exists'}), 400

    # Save the image
    file.save(file_path)
    return jsonify({
        'message': 'Image uploaded successfully',
        'filename': filename,
        'url': url_for('get_image_file', filename=filename, _external=True)
    }), 201


# ---------------------------
# Get image metadata / check existence
# ---------------------------
@app.route('/image/<filename>', methods=['GET'])
def image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Image does not exist'}), 404

    return jsonify({
        'message': 'Image found',
        'filename': filename,
        'url': url_for('get_image_file', filename=filename, _external=True)
    })


# ---------------------------
# Serve the actual image file
# ---------------------------
@app.route('/capturedimage/<filename>', methods=['GET'])
def get_image_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Image not found'}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---------------------------
# Global error handler
# ---------------------------
@app.errorhandler(Exception)
def handle_error(error):
    print(f"❌ Error: {error}")
    return jsonify({'error': str(error)}), 500
5000

if __name__ == '__main__':
    load_dotenv()
    APP_PORT = int(os.getenv('APP_PORT', 8000))
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=APP_PORT, debug=False)
