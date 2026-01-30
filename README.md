# Photo to QR Code Web Application

A full-featured web application that converts uploaded photos into scannable QR codes. When anyone scans the QR code on any device, the original photo displays in their browser.

## Features

✅ **Image Upload** - Clean UI with drag-and-drop support  
✅ **QR Code Generation** - Instant unique QR codes for each photo  
✅ **Image Preview** - See your photo before generating QR code  
✅ **Secure Storage** - Images stored on server with automatic expiration  
✅ **Mobile Responsive** - Works seamlessly on all devices  
✅ **Download QR** - Save QR codes as PNG images  
✅ **Copy URL** - Share image URLs with one click  
✅ **Automatic Expiration** - Images available for 24 hours  
✅ **Error Handling** - Graceful error messages and validation  
✅ **Cloud Ready** - Deployable on Vercel, Render, Railway  

## Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **QR Code Generation**: qrcode library
- **Image Processing**: Pillow
- **File Storage**: Filesystem (local) or compatible with cloud storage
- **CORS**: Flask-CORS for cross-origin requests

## Project Structure

```
keyboard/
├── app.py                 # Flask backend (all API routes & QR generation)
├── templates/
│   └── index.html         # Frontend (HTML, CSS, JavaScript)
├── uploads/               # Image storage (auto-created)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation & Setup

### Local Development

1. **Clone or navigate to the project:**
   ```bash
   cd keyboard
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   - Open your browser and go to: `http://localhost:5000`
   - Upload a photo, get a QR code instantly
   - Share or scan the QR code on any device!

### Environment Variables (Optional)

Create a `.env` file in the project root (for production):

```env
FLASK_ENV=production
FLASK_DEBUG=False
MAX_FILE_SIZE=10485760
QR_EXPIRATION_HOURS=24
```

## Usage Guide

### For Users

1. **Upload Photo**
   - Click the upload area or drag-drop an image
   - Supported formats: PNG, JPG, JPEG, GIF, WebP
   - Maximum file size: 10MB

2. **Preview Image**
   - Your photo appears in the preview section
   - Check it looks good before generating QR code

3. **Generate QR Code**
   - Click "Upload & Generate QR" button
   - Your unique QR code appears instantly
   - Image URL is displayed below

4. **Share QR Code**
   - Download the QR code image
   - Copy and share the URL
   - Share via email, messaging, print, etc.

5. **Scan to View**
   - Anyone with any device can scan the QR code
   - Original photo displays in browser
   - QR codes work for 24 hours

### API Endpoints

#### 1. **POST /api/upload**
Uploads an image and generates QR code.

**Request:**
```
Content-Type: multipart/form-data
Body: file (image file)
```

**Response:**
```json
{
  "success": true,
  "message": "Image uploaded successfully!",
  "qr_code": "data:image/png;base64,...",
  "image_url": "http://localhost:5000/image/uuid",
  "image_id": "uuid",
  "expires_at": "2024-01-31T10:30:00"
}
```

#### 2. **GET /image/{image_id}**
Serves the uploaded image by its unique ID.

**Response:**
- Image file (PNG/JPG/etc.) or
- 404 if not found
- 410 if expired

**Example:**
```
http://localhost:5000/image/550e8400-e29b-41d4-a716-446655440000
```

#### 3. **POST /api/preview**
Generates base64 preview of uploaded file (client-side only).

**Request:**
```
Content-Type: multipart/form-data
Body: file (image file)
```

**Response:**
```json
{
  "success": true,
  "preview": "data:image/jpeg;base64,..."
}
```

#### 4. **GET /health**
Health check for deployment services.

**Response:**
```json
{
  "status": "healthy"
}
```

## Validation Rules

### File Upload Validation

- **File Type**: PNG, JPG, JPEG, GIF, WebP only
- **File Size**: Maximum 10MB
- **Image Validity**: Must be a valid image file
- **Errors**: Clear error messages shown to user

### Constraints Handled

- Duplicate uploads generate unique QR codes
- Expired images auto-cleanup
- Invalid images rejected with explanation
- Large files prevented before upload
- CORS enabled for cross-domain requests

## Deployment

### Deploy to Render

1. Push code to GitHub
2. Connect repository to Render
3. Configure build command: `pip install -r requirements.txt`
4. Configure start command: `gunicorn app:app`
5. Add environment variable: `PYTHON_VERSION=3.11`
6. Deploy!

### Deploy to Railway

1. Push code to GitHub
2. Connect repository to Railway
3. Add `Procfile`:
   ```
   web: gunicorn app:app
   ```
4. Railway auto-detects Python and installs dependencies
5. Deploy!

### Deploy to Vercel (with Serverless Python)

1. Create `vercel.json`:
   ```json
   {
     "buildCommand": "pip install -r requirements.txt",
     "outputDirectory": ".",
     "functions": {
       "app.py": {
         "runtime": "python3.9"
       }
     }
   }
   ```

2. Add `Procfile`:
   ```
   web: gunicorn app:app
   ```

3. Push to GitHub and connect to Vercel
4. Deploy!

### Pre-Production Checklist

- [ ] Set `FLASK_DEBUG=False` in production
- [ ] Use a production WSGI server (gunicorn)
- [ ] Configure `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging
- [ ] Configure CORS properly for your domain
- [ ] Use environment variables for sensitive data
- [ ] Test QR code scanning on actual devices
- [ ] Verify image expiration works
- [ ] Monitor file storage usage

## Security Features

✅ **Input Validation** - File type, size, and content verification  
✅ **Unique IDs** - UUIDs prevent URL guessing  
✅ **Automatic Expiration** - Images deleted after 24 hours  
✅ **CORS Protection** - Configurable cross-origin requests  
✅ **Error Handling** - No sensitive info in error messages  
✅ **File Isolation** - Each file stored securely  

## Performance Optimizations

- Base64 encoded QR codes (no extra requests)
- In-memory image metadata
- Automatic cleanup of expired images
- Efficient Pillow image processing
- Gzip compression ready (Flask handles)
- CDN-friendly deployments

## Troubleshooting

### Issue: "Module not found" error
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: Port 5000 already in use
**Solution:** 
```bash
# Change port in app.py or run:
python app.py --port 5001
```

### Issue: Image not displaying after scan
**Solution:** 
- Check if image URL is correct
- Verify image hasn't expired (24-hour limit)
- Clear browser cache and try again
- Check browser console for errors

### Issue: QR code not scannable
**Solution:**
- Try with different QR scanner apps
- Ensure QR image is clear and not compressed
- Try downloading and printing the QR code
- Check if URL is correct when pasting

### Issue: Uploads folder missing
**Solution:** Folder auto-creates on first upload. If issues persist:
```bash
# Manually create folder
mkdir uploads
```

### Issue: CORS errors
**Solution:** The app already has CORS enabled. If you customize domains:
```python
# In app.py, update CORS configuration
CORS(app, resources={r"/api/*": {"origins": ["your-domain.com"]}})
```

## Browser Compatibility

✅ Chrome/Chromium (90+)  
✅ Firefox (88+)  
✅ Safari (14+)  
✅ Edge (90+)  
✅ Mobile browsers (iOS Safari, Chrome Mobile)  

## File Size Limits

- Upload limit: 10MB per image
- QR code size: ~2KB (base64)
- Total storage: Depends on hosting

## Database Alternative

For persistent storage across deployments, integrate:

- **PostgreSQL**: Use SQLAlchemy
- **MongoDB**: Use PyMongo
- **Firebase**: Use Firebase Admin SDK
- **AWS S3**: Use boto3 for cloud storage

## Development Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Endpoints with cURL

```bash
# Test health check
curl http://localhost:5000/health

# Upload file
curl -X POST -F "file=@photo.jpg" http://localhost:5000/api/upload

# Get image
curl http://localhost:5000/image/{image_id}
```

### Modify QR Code Style

In `app.py`, customize QR generation:

```python
qr = qrcode.QRCode(
    version=2,  # Size: 1-40
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # Error correction level
    box_size=20,  # Pixel size
    border=5,  # Border width
)
```

## Contributing

Feel free to extend this project with:
- Database integration
- User authentication
- Image editing features
- Advanced QR code customization
- Analytics tracking
- Batch uploads

## License

MIT License - Free to use and modify

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the code comments
3. Check browser console for errors
4. Enable debug logging in Flask

---

**Happy QR coding! 📱✨**
