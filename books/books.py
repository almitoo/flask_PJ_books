from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import books_collection, users_collection 
from bson import ObjectId
import datetime

books = Blueprint("books", __name__)

# 🔹 יצירת ספר חדש
@books.route("/createbook", methods=["POST"])
@jwt_required()
def create_book():
    data = request.json
    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404

    title = data.get("title")
    author = data.get("author", user["full_name"])
    pages = data.get("pages", {})

    if not title or not pages:
        return jsonify({"message": "Missing title or pages"}), 400

    book = {
        "title": title,
        "author": author,
        "user_id": user["_id"],
        "created_at": datetime.datetime.utcnow(),
        "num_pages": len(pages),
        "pages": pages
    }

    result = books_collection.insert_one(book)

    return jsonify({
        "message": "Book created successfully",
        "book_id": str(result.inserted_id)
    }), 201


@books.route("/get_user_books", methods=["GET"])
@jwt_required()
def get_user_books():
    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404

    # חיפוש כל הספרים לפי user_id
    user_books = books_collection.find({"user_id": user["_id"]})

    books_list = []
    for book in user_books:
        books_list.append({
            "id": str(book["_id"]),
            "title": book.get("title"),
            "author": book.get("author"),
            "created_at": book.get("created_at").isoformat(),
            "num_pages": book.get("num_pages"),
            "pages": book.get("pages")
        })

    return jsonify({"books": books_list}), 200


@books.route("/create_book_from_ai_utils", methods=["POST"])
@jwt_required()
def create_book_from_ai_utils(jsonBookData):
    email = get_jwt_identity()
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    title = jsonBookData.get("title")
    author = jsonBookData.get("author", user["full_name"])
    pages = jsonBookData.get("pages", {})
    description = jsonBookData.get("description" , "")
    if not title or not pages:
        return jsonify({"message": "Missing title or pages"}), 400
    book = {
        "title": title,
        "author": author,
        "description" :description,
        "user_id": user["_id"],
        "created_at": datetime.datetime.utcnow(),
        "num_pages": len(pages),
        "pages": pages
    }
    result = books_collection.insert_one(book)
    print(f"Book created successfully in the DB , {str(result.inserted_id)}")