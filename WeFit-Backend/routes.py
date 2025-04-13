from flask import request, jsonify
from models import db, User

def setup_routes(app):
    # Home Route
    @app.route('/')
    def home():
        return "Welcome to WeFit! Your AI-based Fitness App."

    # Get All Users (for admin/testing)
    @app.route('/users', methods=['GET'])
    def get_users():
        users = User.query.all()
        return jsonify([{"email": u.email} for u in users])

