from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from auth.auth import auth
from books.books import books
from ai_utils.memoryManager import initialize_app
from ai_utils.ai_routes import ai_story
from werkzeug.serving import WSGIRequestHandler
from db import books_collection

def update_old_books_with_is_shared():
    """
    Updates all books in the database that do not have the 'is_shared' field,
    by setting 'is_shared' to False.
    """
    result = books_collection.update_many(
        {"is_shared": {"$exists": False}},  # מצא ספרים שאין להם את השדה
        {"$set": {"is_shared": False}}      # הוסף להם את השדה עם ערך False
    )
    print(f"✅ Updated {result.modified_count} books to include is_shared=False")



app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY


jwt = JWTManager(app)

# רישום הנתיבים
app.register_blueprint(auth, url_prefix="/api/auth")
app.register_blueprint(books, url_prefix="/api/books")
app.register_blueprint(ai_story, url_prefix="/api/story-ai")

if __name__ == "__main__":

    #התקנה של פיירבאס רק להרצה , ברגע שתוריד את הפייבאס תוריד את השורה הזו 
    initialize_app()
    #update_old_books_with_is_shared() //add fild of is shared in the old book need to oprete once 
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    app.run(host="0.0.0.0", port=5000, debug=True)

