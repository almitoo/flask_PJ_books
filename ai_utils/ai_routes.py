from flask import Blueprint, request, url_for, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from ai_utils.textMaker import makeTextAI
from ai_utils import childrenStoryMaker as child
from ai_utils import imageAIMaker
from ai_utils import voiceMaker
from ai_utils import exceptionHandler as ex
from google.api_core.exceptions import ResourceExhausted
from books.books import create_book_from_ai_utils
ai_story = Blueprint("ai_story", __name__)

# מקבלת טקסט שמתאר סצנה בסיפור ילדים שולחת את הטקסט  לפונקציית
# maketextai
# מחזירה קישור לתמונה שנוצרה על ידי הAI
@ai_story.route('/MagicOfStory/ImageAI', methods=['POST'])
def create_new_AI_image():
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        return ex.exception_no_json()
    
    try:
        textPage = str(data["Text"])
        resolution = str(data["resolution"])
        promptPhoto  = makeTextAI("please give me a promt for the AI image generator for this children story text:"+textPage+" try to pay attention to details of the photo")
        pathImage = imageAIMaker.makeImageAI(promptPhoto ,resolution)
        print("send the file to the user")
        return jsonify({"link":pathImage}), 200  # Handle missing JSON

    except KeyError as e:
        return ex.exception_json_value(e)
    except ResourceExhausted as e:
        return ex.exception_ResourceExhausted(e)
    # except Exception as e:
    #     return ex.exception_internal_server_issue(e)
# מקבלת טקסט וכתובת של תמונה קיימת
# מנסה ליצור תמונה חדשה מבוססת על הקודמת בעזרת הפונקציה
# makeImageFromImage
# מחזירה קישור לתמונה החדשה
@ai_story.route('/MagicOfStory/ImageFromImage', methods=['POST'])
def create_new_AI_image_from_image():
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        return ex.exception_no_json()
    
    try:
        textPage = str(data["Text"])
        url_image = str(data["url_image"])
        pathImage = imageAIMaker.makeImageFromImage(textPage , url_image)
        print(f"send the file to the user")
        return jsonify({"link":pathImage}), 200  # Handle missing JSON

    except KeyError as e:
        return ex.exception_json_value(e)
    except ResourceExhausted as e:
        return ex.exception_ResourceExhausted(e)
    except Exception as e:
        return ex.exception_internal_server_issue(e)
# שולחת את האינפוט לפונקציית
# maketextai
# שמייצר את הטקסט ומחזיר אותו
@ai_story.route('/MagicOfStory/Text', methods=['POST'])
def create_new_AI_text():
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        return ex.exception_no_json()
    try:
        promt = data.get('input')
        return jsonify({"respond" : makeTextAI(promt)})
    except KeyError as e:
        return ex.exception_json_value(e)
    except ResourceExhausted as e:
        return ex.exception_ResourceExhausted(e)
    except Exception as e:
        return ex.exception_internal_server_issue(e)
# יצירת סיפור חדש מתאים לפיצר הראשון והשני, מקבל JSON    
@ai_story.route('/MagicOfStory/Story', methods=['POST'])
#add for create the book in the mongoDB Yam 
@jwt_required()
def create_new_story():
    global staticNumIdPic
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        return ex.exception_no_json()
    try:
        subject = str(data["subject"])
        numPages = int(data["numPages"])
        auther = str(data["auther"])
        description = str(data["description"])
        title = str(data["title"])
        enable_voice = bool(data["text_to_voice"])
        resolution = str(data["resolution"])


        #optional value , don't raise exception
        pages_texts_list = list(data.get("story_pages",[]))
        story_obj = child.Story(subject , numPages, auther , description,title, pages_texts_list , enable_voice,resolution)
        #add story to DB
        jsonBook = story_obj.to_dict_new()
        create_book_from_ai_utils(jsonBook, user)
        return jsonify(jsonBook)

    except KeyError as e:
        return ex.exception_json_value(e)
    except ResourceExhausted as e:
        return ex.exception_ResourceExhausted(e)
    except Exception as e:
        return ex.exception_internal_server_issue(e)
# מייצרת סיפור המשך לסיפור קיים
# יוצרת סיפור חדש דרך
# child.Continued_story
# מחזירה את הסיפור החדש כאוביקט גיסון
# הפונקציה נותנת מענה לפיצר השלישי
@ai_story.route('/MagicOfStory/Story/Sequel',methods=['POST'])
@jwt_required()
def create_new_story_sequel():
    global staticNumIdPic
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        return ex.exception_no_json()
    try:
        numPages = int(data["numPages"])
        auther = str(data["auther"])
        description = str(data["description"])
        title = str(data["title"])
        enable_voice = bool(data["text_to_voice"])
        pages_previous = list(data["pages_previous"])
        title_previous = str(data["title_previous"])
        resolution = str(data["resolution"])
        story_obj = child.Continued_story(numPages,auther,description,title ,pages_previous,title_previous ,enable_voice,resolution)
        staticNumIdPic+=numPages
        jsonBook = story_obj.to_dict()
        create_book_from_ai_utils(jsonBook)
        return jsonify(jsonBook)


    except KeyError as e:
        return ex.exception_json_value(e)
    except ResourceExhausted as e:
        return ex.exception_ResourceExhausted(e)
    # except Exception as e:
    #     return ex.exception_internal_server_issue(e)

@ai_story.route('/MagicOfStory/voice',methods=['POST'])
def make_new_text_to_speach():
    data = request.get_json()  # Get JSON data from the request body
    if not data:
        ex.exception_no_json()
    try:
        text = str(data["text_page"])
        story = str(data["story_title"])
        url_file  = voiceMaker.newVoiceFile(text , f"{story}.mp3")
        return jsonify({"url": url_file})

    except KeyError as e:
        return ex.exception_json_value(e)
    except ResourceExhausted as e:
        return ex.exception_ResourceExhausted(e)
    except Exception as e:
        return ex.exception_internal_server_issue(e)
