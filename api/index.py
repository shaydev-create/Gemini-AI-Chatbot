"""
Vercel serverless function entry point for Flask application
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the Flask app
from app.main import app

# Export the app for Vercel
app = app