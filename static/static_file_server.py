"""Static file server"""
from flask import Blueprint, send_from_directory
import os

static_file_server = Blueprint('static', __name__)


@static_file_server.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    static_dir = os.path.join(os.path.dirname(__file__))
    return send_from_directory(static_dir, filename) 