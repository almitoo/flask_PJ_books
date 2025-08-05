from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import books_collection, users_collection 
from bson import ObjectId
import datetime
from random import randint
from random import randint

def create_book_from_ai_utils(jsonBookData):
    email = get_jwt_identity()

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"message": "User not found"}), 404

    title = jsonBookData.get("title")
    author = jsonBookData.get("author", user["full_name"])
    pages = jsonBookData.get("pages", {})
    genre = jsonBookData.get("genre" ,"null")
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
        "rating" : 0,
        "genre" :genre,
        "pages": pages,
        "is_shared": False
    }

    result = books_collection.insert_one(book)
    print(f"Book created successfully in the DB , {str(result.inserted_id)}")
    
def change_genre_story(data , genre):
    id = ObjectId(data['_id']['$oid'])
    # חיפוש כל הספרים לפי user_id
    bookObj = books_collection.find({"_id": id})

    if not bookObj:
        raise Exception(f"books is not found in mongo DB with id {id}")
    newvalues = { "$set": { "genre": genre } }

    books_collection.update_one({"_id":id},newvalues)
    print(f"genere of book updated to {genre}")

def checkBookInBookList(listBooks ,bookObj):
    book_text = ''.join([page["text_page"] for page in bookObj["pages"]])
    for b in listBooks:
        
        b_text = ''.join([page["text_page"] for page in b["pages"]])
        if bookObj["title"] == b["title"] or b_text == book_text:
            return True
    return False

def getCounterBooksForId(id_user):
    id = (ObjectId(id_user))
    return books_collection.count_documents({"user_id":id})