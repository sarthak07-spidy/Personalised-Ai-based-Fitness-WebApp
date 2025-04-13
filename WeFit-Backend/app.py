from flask import Flask, request, jsonify, redirect
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import os
from datetime import datetime, timedelta, timezone  # Import timezone
from models import db, User

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Allow React frontend

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth Setup
google_bp = make_google_blueprint(
    client_id='YOUR_GOOGLE_CLIENT_ID',
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',
    redirect_to='google_login'
)
app.register_blueprint(google_bp, url_prefix='/google_login')

# Database Init
db.init_app(app)

# Token generation
def generate_token(user_id):
    exp_time = datetime.now(timezone.utc) + timedelta(hours=1)  # Use timezone.utc
    token = jwt.encode({'user_id': user_id, 'exp': exp_time}, app.config['SECRET_KEY'], algorithm='HS256')
    return token

# Import external routes
from routes import setup_routes
setup_routes(app)

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            token = generate_token(user.id)
            return jsonify({
                "message": "Login successful",
                "token": token,
                "username": user.username  # Include username in the response
            }), 200

        return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred", "details": str(e)}), 500
   

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        print("Signup endpoint hit")  # Debugging print
        print("Raw request data:", request.data)  # Log raw request data
        if not request.is_json:
            print("Request is not JSON")  # Debugging print
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.get_json()
        print("Parsed JSON data:", data)  # Debugging print

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            print("Missing fields")  # Debugging print
            return jsonify({"error": "Username, email, and password are required"}), 400

        if User.query.filter_by(email=email).first():
            print("User already exists with email:", email)  # Debugging print
            return jsonify({"error": "User already exists"}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        print("User created successfully:", new_user)  # Debugging print
        return jsonify({"message": "Signup successful!"}), 201

    except Exception as e:
        print("Error in /api/signup:", str(e))  # Debugging print
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
        print("🛠️ Database initialized")
        print("🛣️ Registered Routes:")
        for rule in app.url_map.iter_rules():
            print(rule)
    app.run(debug=True)

