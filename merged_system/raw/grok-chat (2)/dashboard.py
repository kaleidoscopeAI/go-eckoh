from flask import Flask, jsonify, render_template_string
from .config import CONFIG
from .data_store import DataStore

TEMPLATE = """<html><body>Dashboard</body></html>"""  # Expand as needed

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return TEMPLATE

    return app
