from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import books_collection, users_collection 
from bson import ObjectId
import datetime
from .utilities_books import checkBookInBookList 
from random import randint
from random import randint
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
        "rating": 0,
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
    try:
        email = get_jwt_identity()

        user = users_collection.find_one({"email": email})
        if not user:
            return jsonify({"message": "User not found"}), 404

        user_books = books_collection.find({"user_id": user["_id"]})

        books_list = []
        for book in user_books:
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "num_pages": book.get("num_pages"),
                "rating": book.get("rating"),
                "genre": book.get("genre"),
                "pages": book.get("pages")
            })

        return jsonify({"books": books_list}), 200

    except Exception as e:
        print(f"Error in get_user_books: {e}")
        return jsonify({"message": "Internal server error"}), 500



@books.route("/get_top_pick", methods=["GET"])
def get_top_pick():
#בוחר 4 ספרים רנדומליים מהדאטה בייס 
    books = books_collection.find()
    lenght_collection = books_collection.count_documents({})-1
    books_list = []
    while(len(books_list)<4):
        book  = books[randint(0,lenght_collection)]
        if (not checkBookInBookList(books_list , book)):
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat(),
                "num_pages": book.get("num_pages"),
                "pages": book.get("pages")
            })

    return jsonify({"books": books_list}), 200


@books.route("/get_top_rated", methods=["GET"])
def get_top_rated():
    #בוחר 4 ספרים עם הדירוג הגבוה ביותר מהדאטה בייס 
    books = books_collection.find().sort({"rating":-1 , "numPages":-1} )
    books_list = []
    for book in books:
        if (len(books_list)==4):
            break

        if (not checkBookInBookList(books_list , book)):
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat(),
                "num_pages": book.get("num_pages"),
                "pages": book.get("pages")
            })

    return jsonify({"books": books_list}), 200



@books.route("/genre/<string:genre>" , methods=["GET"])
def get_books_genre(genre):
    books = books_collection.find({"genre": genre})
    books_list = []
    for book in books:
        if (not checkBookInBookList(books_list , book)):
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat(),
                "num_pages": book.get("num_pages"),
                "pages": book.get("pages")
            })
    return jsonify({"books": books_list}), 200


@books.route("/recent_added" , methods=["GET"])
def get_recent_added():
    books = books_collection.find({}).sort({"created_at":-1})
    books_list = []
    for i in range(5):
        book = books[i]
        if (not checkBookInBookList(books_list , book)):
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat(),
                "num_pages": book.get("num_pages"),
                "pages": book.get("pages")
            })
    return jsonify({"books": books_list}), 200

