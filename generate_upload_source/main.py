import functions_framework
import datetime
import re
import uuid
from google.cloud import storage

# --- CONFIGURATION ---
BUCKET_NAME = "spastha-final-bucket"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB in bytes
ALLOWED_EXTENSIONS = ['.pdf']
# --- END CONFIGURATION ---

@functions_framework.http
def generate_signed_url_v4(request):
    """
    HTTP Cloud Function that generates a signed URL for a file upload.
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Validate request method
        if request.method != 'POST':
            return ({'error': 'Only POST method is allowed.'}, 405, headers)
        
        request_json = request.get_json(silent=True)
        
        # Better error handling for missing JSON
        if not request_json:
            return ({'error': 'Request must contain valid JSON.'}, 400, headers)
        
        file_name = request_json.get('fileName', '').strip()
        
        # Validate fileName presence
        if not file_name:
            return ({'error': 'JSON body must contain a non-empty "fileName" field.'}, 400, headers)
        
        # Validate file extension
        if not any(file_name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
            return ({'error': f'Only {", ".join(ALLOWED_EXTENSIONS)} files are allowed.'}, 400, headers)
        
        # Optional: Get file size for validation (if provided)
        file_size = request_json.get('fileSize')
        if file_size and file_size > MAX_FILE_SIZE:
            return ({'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)} MB.'}, 400, headers)
        
        # Sanitize filename to prevent path traversal and ensure valid characters
        sanitized_filename = sanitize_filename(file_name)
        if not sanitized_filename:
            return ({'error': 'Invalid filename provided.'}, 400, headers)
        
        # Add timestamp and UUID to prevent filename conflicts
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        final_filename = f"{timestamp}_{unique_id}_{sanitized_filename}"
        
        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(final_filename)
        
        # Set up conditions for the signed URL
        conditions = [
            ['content-length-range', 1, MAX_FILE_SIZE],  # File size constraints
        ]
        
        function_service_account_email = "992685094776-compute@developer.gserviceaccount.com"
        # Generate a signed URL that is valid for 15 minutes    
        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(minutes=15),
            method="PUT",
            content_type="application/pdf",  # Enforce PDF uploads
            service_account_email=function_service_account_email,
            
            headers={
                'x-goog-content-length-range': f'1,{MAX_FILE_SIZE}'
            }
        )
        
        response_data = {
            'signedUrl': url,
            'fileName': final_filename,
            'originalFileName': file_name,
            'expiresAt': (datetime.datetime.now() + datetime.timedelta(minutes=15)).isoformat(),
            'maxFileSize': MAX_FILE_SIZE,
            'allowedTypes': ALLOWED_EXTENSIONS
        }
        
        print(f"Generated signed URL for file: {final_filename}")
        return (response_data, 200, headers)
        
    except Exception as e:
        print(f"An error occurred generating signed URL: {e}")
        return ({'error': 'An internal error occurred while generating the upload URL.'}, 500, headers)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues and ensure valid characters.
    """
    # Remove path separators and other potentially dangerous characters
    filename = filename.replace('\\', '').replace('/', '')
    
    # Remove any non-alphanumeric characters except dots, dashes, and underscores
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple consecutive dots (potential security issue)
    filename = re.sub(r'\.{2,}', '.', filename)
    
    # Ensure filename doesn't start with a dot
    if filename.startswith('.'):
        filename = 'file' + filename
    
    # Limit filename length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 100:
        name = name[:100]
    
    final_filename = f"{name}.{ext}" if ext else name
    
    # Final validation
    if not final_filename or final_filename in ['.', '..']:
        return None
    
    return final_filename