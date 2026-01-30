"""
QR Code Photo Upload Application
A Flask web application that converts uploaded photos into QR codes.
When scanned, the QR code displays the original photo in a browser.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
import qrcode
from io import BytesIO
import base64
import os
import uuid
from datetime import datetime, timedelta
import mimetypes
from PIL import Image
import re

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
QR_EXPIRATION_HOURS = 24  # QR codes expire after 24 hours

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for image metadata (for serverless compatibility)
image_store = {}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file(file):
    """Validate uploaded file."""
    errors = []
    
    if not file or file.filename == '':
        errors.append('No file selected.')
        return errors
    
    if not allowed_file(file.filename):
        errors.append(f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}')
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        errors.append(f'File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit.')
    
    # Try to open as image to verify it's valid
    try:
        img = Image.open(file)
        img.verify()
        file.seek(0)
    except Exception as e:
        errors.append(f'Invalid image file: {str(e)}')
    
    return errors


def save_image(file):
    """Save image and return unique ID."""
    try:
        # Read file data
        file_data = file.read()
        file.seek(0)
        
        # Generate unique ID
        unique_id = str(uuid.uuid4())
        
        # Save to filesystem
        filename = f"{unique_id}.{file.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        # Store metadata
        image_store[unique_id] = {
            'filename': filename,
            'filepath': filepath,
            'uploaded_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=QR_EXPIRATION_HOURS)
        }
        
        return unique_id
    except Exception as e:
        raise Exception(f'Error saving image: {str(e)}')


def cleanup_expired_images():
    """Remove expired images from storage."""
    now = datetime.now()
    expired_ids = [
        id for id, data in image_store.items()
        if now > data['expires_at']
    ]
    
    for id in expired_ids:
        try:
            os.remove(image_store[id]['filepath'])
            del image_store[id]
        except:
            pass


def generate_qr_code(url):
    """Generate QR code image from URL."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return qr_base64
    except Exception as e:
        raise Exception(f'Error generating QR code: {str(e)}')


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """Handle image upload and QR code generation."""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided.'}), 400
        
        file = request.files['file']
        
        # Validate file
        errors = validate_file(file)
        if errors:
            return jsonify({'success': False, 'error': errors[0]}), 400
        
        # Save image
        unique_id = save_image(file)
        
        # Generate image serving URL (works locally and on cloud)
        image_url = request.host_url.rstrip('/') + f'/image/{unique_id}'
        
        # Generate QR code
        qr_base64 = generate_qr_code(image_url)
        
        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully!',
            'qr_code': f'data:image/png;base64,{qr_base64}',
            'image_url': image_url,
            'image_id': unique_id,
            'expires_at': image_store[unique_id]['expires_at'].isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/image/<image_id>')
def serve_image(image_id):
    """Serve uploaded image by ID."""
    try:
        # Cleanup expired images periodically
        cleanup_expired_images()
        
        # Check if image exists
        if image_id not in image_store:
            return '''
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1>❌ Image Not Found</h1>
                    <p>The image has expired or was not found.</p>
                    <p>Images are available for 24 hours after upload.</p>
                    <a href="/" style="color: #007bff; text-decoration: none;">← Back to Upload</a>
                </body>
            </html>
            ''', 404
        
        # Check if image has expired
        if datetime.now() > image_store[image_id]['expires_at']:
            del image_store[image_id]
            return '''
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1>⏰ Image Expired</h1>
                    <p>This image has expired after 24 hours.</p>
                    <a href="/" style="color: #007bff; text-decoration: none;">← Upload a New Image</a>
                </body>
            </html>
            ''', 410
        
        # Serve the image
        filename = image_store[image_id]['filename']
        return send_from_directory(UPLOAD_FOLDER, filename)
        
    except Exception as e:
        return f'Error: {str(e)}', 500


@app.route('/api/preview', methods=['POST'])
def preview_image():
    """Get image preview as base64."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided.'}), 400
        
        file = request.files['file']
        
        # Validate file
        errors = validate_file(file)
        if errors:
            return jsonify({'success': False, 'error': errors[0]}), 400
        
        # Convert to base64 for preview
        file.seek(0)
        file_data = file.read()
        preview_base64 = base64.b64encode(file_data).decode('utf-8')
        
        # Detect MIME type
        ext = file.filename.rsplit('.', 1)[1].lower()
        mime_type = mimetypes.guess_type(f'file.{ext}')[0] or 'image/jpeg'
        
        return jsonify({
            'success': True,
            'preview': f'data:{mime_type};base64,{preview_base64}'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500


@app.route('/health')
def health_check():
    """Health check endpoint for deployment services."""
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
