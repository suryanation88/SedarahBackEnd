"""Small apps to demonstrate endpoints with basic feature - CRUD"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import jwt
from api.auth.endpoints import auth_endpoints
from api.dataprotected.endpoints import protected_endpoints
from api.permohonan.endpoints import permohonan_endpoints
from api.berita.endpoints import berita_endpoints
from api.donor_respons.endpoints import donor_respons_endpoints
from api.profile.endpoints import profile_endpoints
from api.komentar.endpoints import komentar_endpoints
from config import Config
from static.static_file_server import static_file_server
import os

try:
    from flasgger import Swagger
    SWAGGER_AVAILABLE = True
except ImportError:
    SWAGGER_AVAILABLE = False
    print("Warning: Flasgger not available. API documentation will not be available.")

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Authorization"],
     supports_credentials=True)

# Initialize Swagger if available
if SWAGGER_AVAILABLE:
    Swagger(app)

jwt.init_app(app)

# Root route
@app.route('/')
def index():
    """Root endpoint - API information"""
    return jsonify({
        "message": "Backend Flask - Sistem Donor Darah API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/v1/auth",
            "permohonan": "/api/v1/permohonan",
            "donor_respons": "/api/v1/donor_respons",
            "komentar": "/api/v1/komentar",
            "berita": "/api/v1/berita",
            "profile": "/api/v1/users",
            "protected": "/api/v1/protected"
        },
        "documentation": "/apidocs" if SWAGGER_AVAILABLE else "Not available"
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Backend Flask is running"
    })

# register the blueprint
app.register_blueprint(auth_endpoints, url_prefix='/api/v1/auth')
app.register_blueprint(protected_endpoints,
                       url_prefix='/api/v1/protected')
app.register_blueprint(permohonan_endpoints, url_prefix='/api/v1/permohonan')
app.register_blueprint(berita_endpoints, url_prefix='/api/v1/berita')
app.register_blueprint(donor_respons_endpoints, url_prefix='/api/v1/donor_respons')
app.register_blueprint(profile_endpoints, url_prefix='/api/v1/users')
app.register_blueprint(komentar_endpoints, url_prefix='/api/v1/komentar')
app.register_blueprint(static_file_server, url_prefix='/static/')

PROFILE_FOLDER = os.path.join(os.getcwd(), 'profile')
UPLOADS_FOLDER = os.path.join(os.getcwd(), 'uploads')

@app.route('/profile/<filename>')
def profile_file(filename):
    return send_from_directory(PROFILE_FOLDER, filename)

@app.route('/uploads/<filename>')
def uploads_file(filename):
    return send_from_directory(UPLOADS_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
