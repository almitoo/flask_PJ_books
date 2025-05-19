from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from auth.auth import auth
from books.books import books
from ai_utils.ai_routes import ai_story
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY

jwt = JWTManager(app)

# רישום הנתיבים
app.register_blueprint(auth, url_prefix="/api/auth")
app.register_blueprint(books, url_prefix="/api/books")
app.register_blueprint(ai_story, url_prefix="/api/story-ai")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

