from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import books_collection, users_collection 
from bson import ObjectId
import datetime
from .utilities_books import checkBookInBookList 
from random import randint
from random import sample
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
        "comments":[],
        "comments":[],
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
                "comments":book.get("comments"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else None,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else None,
                "pages": book.get("pages")
            })

        return jsonify({"books": books_list}), 200
    except Exception as e:
        print(f"Error in get_user_books: {e}")
        return jsonify({"message": "Internal server error"}), 500

@books.route("/all_books", methods =["GET"])
@jwt_required()
def getAllBooks():
    try:
        email = get_jwt_identity()

        user = users_collection.find_one({"email": email})
        if not user:
            return jsonify({"message": "User not found"}), 404

        user_books = books_collection.find({})

        books_list = []
        for book in user_books:
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "num_pages": book.get("num_pages"),
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else None,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else None,
                "pages": book.get("pages")
            })

        return jsonify({"books": books_list}), 200

    except Exception as e:
        print(f"Error in the request: {e}")
        return jsonify({"message": "Internal server error"}), 500

@books.route("/byUser/id=<string:id_user>", methods =["GET"])
@jwt_required()
def getAllBooksByUser(id_user):
    try:
        email = get_jwt_identity()

        user = users_collection.find_one({"email": email})
        if not user:
            return jsonify({"message": "current User not found"}), 404
        
        userIdInBookObj = ObjectId(id_user)

        #find User
        autherUser = users_collection.find_one({"_id":userIdInBookObj})
        if not user:
            return jsonify({"message": "auther books User not found"}), 404
        
        user_books = books_collection.find({"user_id":userIdInBookObj})

        books_list = []
        for book in user_books:
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "num_pages": book.get("num_pages"),
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else None,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else None,
                "pages": book.get("pages")
            })

        return jsonify({"books": books_list}), 200

    except Exception as e:
        print(f"Error in the request: {e}")
        return jsonify({"message": "Internal server error"}), 500

@books.route("/get_top_pick", methods=["GET"])
def get_top_pick():
#בוחר 4 ספרים רנדומליים מהדאטה בייס 
    books = list(books_collection.find())  
    lenght_collection = len(books) 

    #if  the user dontbhave books
    if lenght_collection == 0:
        return jsonify({"books": []}), 200
    
   # בחירת עד 4 ספרים אקראיים ללא חזרות
    selected_books = sample(books, min(4, len(books)))

    books_list = []
    for book in selected_books:
        books_list.append({
            "id": str(book.get("_id")),
            "title": book.get("title"),
            "author": book.get("author"),
            "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
            "num_pages": book.get("num_pages"),
            "comments": book.get("comments"),
            "genre": book.get("genre"),
            "rating": book.get("rating"),
            "sum_rating": book.get("sum_rating") or 0,
            "counter_rating": book.get("counter_rating") or 0,
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
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "num_pages": book.get("num_pages"),
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else 0,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else 0,
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else 0,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else 0,
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
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "num_pages": book.get("num_pages"),
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else 0,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else 0,
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else 0,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else 0,
                "pages": book.get("pages")
            })
    return jsonify({"books": books_list}), 200
@books.route("/recent_added" , methods=["GET"])
def get_recent_added():
    books_cursor = books_collection.find({}).sort("created_at", -1).limit(5)
    books = list(books_cursor)
    
    books_list = []
    for book in books:
        if not checkBookInBookList(books_list, book):
            books_list.append({
                "id": str(book["_id"]),
                "title": book.get("title"),
                "author": book.get("author"),
                "created_at": book.get("created_at").isoformat() if book.get("created_at") else None,
                "num_pages": book.get("num_pages"),
                "rating": book.get("rating"),
                "comments":book.get("comments"),
                "genre": book.get("genre"),
                "sum_rating" : book.get("sum_rating") if book.get("sum_rating") else 0,
                "counter_rating" : book.get("counter_rating") if book.get("counter_rating") else 0,
                "pages": book.get("pages")
            })
    return jsonify({"books": books_list}), 200

@books.route("/new_rating_for_book/id=<string:id_book>" ,methods=["PUT"])
def updateRatingOfBook(id_book):
    id = ObjectId(id_book)
    # חיפוש כל הספרים לפי user_id
    bookObj = books_collection.find_one({"_id": id})

    if not bookObj:
        return jsonify({"message": "Book not found"}), 404
    
    data = request.json
    rating = data.get("rating")
    sum_rating = bookObj.get("sum_rating") if bookObj.get("sum_rating") else 0
    counter_rating = bookObj.get("counter_rating") if bookObj.get("counter_rating") else 0

    sum_rating+= rating
    counter_rating+=1
    rating  = sum_rating//counter_rating

    #upadte in the DB
    newvalues = { "$set": { 
                    "sum_rating" :sum_rating,
                    "counter_rating" :counter_rating,
                    "rating" :rating
     } }
    
    books_collection.update_one({"_id":id},newvalues)
    
    dic_print = { 
                    "sum_rating" :sum_rating,
                    "counter_rating" :counter_rating,
                    "rating" :rating
     } 

    print(f"values update in the DB for book {id} {dic_print}")

    return f"values update in the DB for book {id} {dic_print}", 200

@books.route("/new_comment_for_book/id=<string:id_book>" ,methods=["PUT"])
@jwt_required()
def addNewCommentInBook(id_book):
    id = ObjectId(id_book)
    # חיפוש כל הספרים לפי user_id
    bookObj = books_collection.find_one({"_id": id})

    if not bookObj:
        return jsonify({"message": "Book not found"}), 404

    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json

    user_name = user.get("full_name","null")
    text_comment = data.get("comment","")

    comments = list(bookObj.get("comments",[]))

    comments.append({"user":user_name , "comment":text_comment})
    #upadte in the DB
    newvalues = { "$set": { 
                    "comments" :comments,
     } }
    
    books_collection.update_one({"_id":id},newvalues)
    
    dic_print = { 
                    "comments" :comments
     } 

    print(f"values update in the DB for book {id} {dic_print}")

    return f"values update in the DB for book {id} {dic_print}", 200

@books.route("/newCommentAndRanking/id=<string:id_book>" ,methods=["PUT"])
@jwt_required()
def addRankingAndComment(id_book):
    id = ObjectId(id_book)
    # חיפוש כל הספרים לפי user_id
    bookObj = books_collection.find_one({"_id": id})

    if not bookObj:
        return jsonify({"message": "Book not found"}), 404

    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.json

    user_name = user.get("full_name","null")
    text_comment = data.get("comment","")
    rating = data.get("rating")
    sum_rating = bookObj.get("sum_rating") if bookObj.get("sum_rating") else 0
    counter_rating = bookObj.get("counter_rating") if bookObj.get("counter_rating") else 0
    comments = list(bookObj.get("comments",[]))


    comments.append({"user":user_name , "comment":text_comment})
    sum_rating+= rating
    counter_rating+=1
    rating  = sum_rating//counter_rating

    #upadte in the DB
    newvalues = { "$set": { 
                    "comments" :comments,
                    "sum_rating" :sum_rating,
                    "counter_rating" :counter_rating,
                    "rating" :rating
                    
     } }
    
    books_collection.update_one({"_id":id},newvalues)
    
    dic_print = { 
                    "comments" :len(comments),
                    "sum_rating" :sum_rating,
                    "counter_rating" :counter_rating,
                    "rating" :rating
     } 

    print(f"values update in the DB for book {id} {dic_print}")

    return f"values update in the DB for book {id} {dic_print}", 200

@books.route("/delete/id=<string:id_book>" ,methods=["DELETE"])
@jwt_required()
def deleteBook(id_book):
    id = ObjectId(id_book)
    # חיפוש כל הספרים לפי user_id
    bookObj = books_collection.find_one({"_id": id})

    if not bookObj:
        return jsonify({"message": "Book not found"}), 404

    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    books_collection.delete_one({"_id": id})
    print(f"book has deleted from DB: id ={id}")
    return f"book has been deleted ",200



@books.route("/checkDeleteOption/id=<string:id_book>" ,methods=["GET"])
@jwt_required()
def checkDeleteBook(id_book):
    id = ObjectId(id_book)
    # חיפוש כל הספרים לפי user_id
    bookObj = books_collection.find_one({"_id": id})

    if not bookObj:
        return jsonify({"message": "Book not found"}), 404

    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    userIdInBookObj = ObjectId(bookObj["user_id"])
    print(f"{userIdInBookObj} == {user["_id"]}")
    if  userIdInBookObj == user["_id"] :
        return jsonify({"message": "Book can be deleted"}), 200
    else:
        return  jsonify({"message": "ERROR could not delete because the book was not made by the user "}), 400

