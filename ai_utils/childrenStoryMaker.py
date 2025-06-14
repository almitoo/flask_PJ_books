import ai_utils.textMaker as t
from ai_utils.voiceMaker import newVoiceFile
import ai_utils.imageAIMaker
import re




    
# הפונקציה מקבלת טקסט של סיפור ילדים ומפרידה אותו לעמודים
# כל עמוד מתחיל במחרוזת "Page X: " כאשר X הוא מספר העמוד
def storyTextSplit(text):
    matches = re.findall(r"\*\*Page \d+:\*\*.*?(?=(\*\*Page \d+:\*\*|$))", text, re.DOTALL)
    # Remove the first empty string if it exists, and strip whitespace
    arr = [page.strip() for page in matches if page.strip()]
    print(f"\n\n\n\n{arr}\n\n\n\n")
    if (len(arr)==0):
        matches = re.split(r'(?=Page \d+:)', text)
        arr = [page.strip() for page in matches if page.strip()]
    return arr
# # מחלקת page מייצגת עמוד בסיפור ילדים
# כוללת טקסט , קישור לתמונה וקובץ קול
# מחזירה את המידע כdict
class page():
    def __init__(self , text_page, img_url , voice_file_url):
        self.text_page = text_page
        self.img_url = img_url
        self.voice_file_url = voice_file_url
    
    def get_text_page(self):
        return self._text_page

    def set_text_page(self, text_page):
        self._text_page = text_page

    def get_img_url(self):
        return self._img_url

    def set_img_url(self, img_url):
        self._img_url = img_url

    def to_dict(self):
        return {
            'text_page': self.text_page,
            'img_url': self.img_url,
            'voice_file_url':self.voice_file_url
        }

    

# מחלקת הליבה שמייצרת את הסיפור
# אם לא נשלח טקסט עמודים היא מייצרת את כל הסיפור לבד עם
# ai_story_maker
# אם נשלח טקסט עמודים היא מייצרת את הסיפור עם
# story_media_maker
class Story():

    def __init__(
        self,
        subject: str,
        numPages: int,
        auther: str,
        description: str,
        title: str,
        pages_texts_list:  list |None,
        make_voice: bool,
        resolution:str):
        
        # no text inclued = complete AI story
        if len(pages_texts_list)==0:
           self.AI_story_maker(subject,numPages,auther,description,title,make_voice,resolution)
        #pages= story from the user 
        else:
            print("making a new story , pages has been have by the user.")
            self.story_media_maker(subject,numPages,auther,description,title,make_voice,pages_texts_list,resolution)
        print("story has been complete \n\n")
# נשתמש בה כאשר המשתמש שלח כבר טקסט של הסיפור
# אם אין כותרת הAI ימציא כותרת
# מייצר תמונה וקובץ קול
# כל הנתונים נשמרים כאוביקט page
    def story_media_maker(
            self ,
            subject: str,
            numPages: int,
            auther: str,
            description: str,
            title: str,
            make_voice : bool,
            pages_texts_list : list,
            resolution: str):
        
        self.numPages = numPages
        self.description = description
        self.auther =auther
        extra_promt = " , just print the answer"
        self.pages = []
        if title!= '':
            self.title = title
        else:
            text_output =t.makeTextAI(f"give me a title for children book with a description of {description} {extra_promt} return just one title ,  Return the respond as follow: Title:the title of the story")
            self.title  = text_output.split("Title:")[1].strip()
        #no rellevant: move from  stable diffusion to gemini
        #steps  =imageQuality[quality_images].value 
        #save value of the first image to base the rest of the images on that
        url_first_image =''
        images_prompts =[]
        for i in range(numPages):

            inputText = f'make an image prompt for children story according to this text {pages_texts_list[i]} , the subject of the story :{subject} '
            if (i>0):
                cumulative_image_prompts = ' '.join([prompt for prompt in images_prompts])
                previous_story_pages = ' '.join([pages_texts_list[j] for j in range(i)])
                inputText += f'\n making sure to maintain consistent visual elements such as [clothing, colors, background, art style, recurring objects]. The image should reflect a coherent world and preserve recurring elements seen in previous images. Focus on relevant features , e.g., expression, background setting, lighting and characters. \n here is the previous story pages for refrence {previous_story_pages}\n and here is the previous story pages images prompts for refrence: {cumulative_image_prompts}'
            
            print(inputText)

            inputText = t.makeTextAI(inputText)
            print(f"\n\n input prompt for image {i} in the story : {inputText}\n\n")
            pathImage = None
            if i==0:
                #pathImage = f"{title}_page{i}_pic"
                pathImage = ai_utils.imageAIMaker.makeImageAI(inputText,resolution=resolution)
                url_first_image = str(pathImage)
            else:
                
                #pathImage = f"{title}_page{i}_pic"
                pathImage = ai_utils.imageAIMaker.makeImageFromImage(inputText ,url_first_image,resolution=resolution)
            
            images_prompts.append(inputText)

            #no rellevant: move from  stable diffusion to gemini
            #pathImage = imageAIMaker.makeImageAI(inputText , steps , height_images  , width_images , staticNumIdPic)
            #staticNumIdPic+=1
            voice_file_url = None
            if make_voice:
                voice_file_url = newVoiceFile(pages_texts_list[i],f"{self.title}_page{i}_voice")
            self.pages.append(page(pages_texts_list[i] , pathImage,voice_file_url)) 

        
# נשתמש בה כאשר המשתמש לא שלח טקסט עמודים
# כל הטקסט יכתב בעזרת
# makeTextAI
# מפצל את העמודים בעזרת
# storyTextSplit
# עבוא כל עמוד מייצר תמונה וקובץ קול
    def AI_story_maker(
            self ,
            subject: str,
            numPages: int,
            auther: str,
            description: str,
            title: str,
            make_voice : bool,
            resolution : str):
        
        self.numPages = numPages
        self.description = description
        self.auther =auther
        story = ''
        extra_promt = " , just print the answer"
        self.pages = []
        if title!= '':
            self.title = title
        else:
            text_output =t.makeTextAI(f"give me a title for children book with a description of {description} {extra_promt} return just one title ,  Return the respond as follow: Title:the title of the story")
            self.title  = text_output.split("Title:")[1].strip()
        story = t.makeTextAI(f'''
    You are currently a children's writer who is required to write a children's book about {subject}
    You are required to write {numPages} pages with each page no more than 150 words
    Return the respond as follow:
    Page 1: Text of page 1
    Page 2: Text of page 2
    And so on
    ''')
            
        print (f"story  {story}")
        pages_text = storyTextSplit(story) 
        
        #no rellevant: move from  stable diffusion to gemini
        #steps  =imageQuality[quality_images].value 
        
        
        #save value of the first image to base the rest of the images on that
        url_first_image =''
        images_prompts =[]

        for i in range(numPages):

            inputText = f'make an image prompt for children story according to this text  {pages_text[i]}'
            if (i>0):
                cumulative_image_prompts = ' '.join([prompt for prompt in images_prompts])
                previous_story_pages = ' '.join([pages_text[j] for j in range(i)])
                inputText += f'\n making sure to maintain consistent visual elements such as [clothing, colors, background, art style, recurring objects]. The image should reflect a coherent world and preserve recurring elements seen in previous images. Focus on relevant features , e.g., expression, background setting, lighting and characters. \n here is the previous story pages for refrence {previous_story_pages}\n and here is the previous story pages images prompts for refrence: {cumulative_image_prompts}'
            
            print(inputText)

            inputText = t.makeTextAI(inputText)
            
            images_prompts.append(inputText)
            pathImage = None
            if i==0:
                pathImage = ai_utils.imageAIMaker.makeImageAI(inputText,resolution=resolution)
                url_first_image = str(pathImage)
            else:
                pathImage = ai_utils.imageAIMaker.makeImageFromImage(inputText ,url_first_image,resolution=resolution)
            #no rellevant: move from  stable diffusion to gemini
            #pathImage = imageAIMaker.makeImageAI(inputText , steps , height_images  , width_images , staticNumIdPic)
            #staticNumIdPic+=1
            voice_file_url = None
            if make_voice:
                voice_file_url = newVoiceFile(pages_text[i],f"{self.title}_page{i}_voice")
            self.pages.append(page(pages_text[i] , pathImage,voice_file_url)) 

        
    # # מחזירה את הסיפור כdict
    # המילון יכלול את מספר עמודים, שם המחבר, תיאור, כותרת וכל עמוד עם הטקסט שלו, קישור לתמונה וקובץ קול
    def to_dict(self):
        print(f"to_dict called: num pages = {len(self.pages)}")  

        dict = {
            'numPages': self.numPages,
            'auther': self.auther,
            'description': self.description,
            'title': self.title
        }
        pages_dict = [page.to_dict() for page in self.pages]
        dict['pages'] = pages_dict
        return dict
    
    def change_page_text(self, num_page,  new_text):
        self.pages[num_page].set_text_page(new_text)
    

        # בתוך child.Story
    def to_dict_new(self):
        return {
            "title": self.title,
            "author": self.auther,
            "description": self.description,
            "num_pages": self.numPages,
            # cover_image = התמונה של העמוד הראשון (נוח ל-Flutter)
            "cover_image": self.pages[0].img_url if self.pages else "",
            "pages": [
                {
                    "text_page": p.text_page,
                    "img_url":  p.img_url,
                    "voice_file_url": p.voice_file_url or ""
                }
                for p in self.pages
            ]
        }


# מטרת המחלקה ליצור סיפור המשך לסיפור קיים
# היא מקבלת את מספר העמודים, שם המחבר, תיאור, כותרת, עמודים של הספר הקודם וכותרת הספר הקודם
class Continued_story(Story):
    def __init__(self,numPages, auther, description, title
                 ,previous_book_pages  ,previous_book_title
                , make_voice,resolution):
        #part 1 finds out what the previous story was
        previous_book_story = previous_book_title +"\n"
        for page_bool_previous in previous_book_pages:
            previous_book_story += page_bool_previous.get('text_page')
            previous_book_story +='\n'

        #part 2 make the story for the current book

        self.numPages = numPages
        self.description = description
        self.auther =auther
        story = ''
        extra_promt = " , just print the answer"
        self.pages = []
        if title!= '':
            self.title = title
        else:
            self.title =t.makeTextAI(f"give me a title for children book with a description of {description} {extra_promt}")

        story = t.makeTextAI(f'''
    You are currently a children's writer who is required to write a children's book 
    You are making a sequel story, here is the text of the previous story: {previous_book_story}
    You are required to write {numPages} pages of story
    You are required to write {numPages} pages of story
    Return the respond as follow:
    Page 1: Text of page 1
    Page 2: Text of page 2
    And so on
    don't add text on top of the instruction
    just in format i show you
    don't add text on top of the instruction
    just in format i show you
    ''')
            
        print (f"story  = {story}")
        pages_text = storyTextSplit(story)    
        
 
        #save value of the first image to base the rest of the images on that
        url_first_image =''
        images_prompts =[]
        for i in range(numPages):

            inputText = f'make an image prompt for children story according to this text {pages_text[i]}'
            inputText = t.makeTextAI(inputText)
            if (i>0):
                cumulative_image_prompts = ' '.join([prompt for prompt in images_prompts])
                previous_story_pages = ' '.join([pages_text[j] for j in range(i)])
                inputText += f'\n making sure to maintain consistent visual elements such as [clothing, colors, background, art style, recurring objects]. The image should reflect a coherent world and preserve recurring elements seen in previous images. Focus on relevant features , e.g., expression, background setting, lighting and characters. \n here is the previous story pages for refrence {previous_story_pages}\n and here is the previous story pages images prompts for refrence: {cumulative_image_prompts}'
            
            print(inputText)

            pathImage = None
            
            images_prompts.append(inputText)
            if i==0:
                pathImage = ai_utils.imageAIMaker.makeImageAI(inputText,resolution=resolution)
                url_first_image = str(pathImage)
            else:
                pathImage = ai_utils.imageAIMaker.makeImageFromImage(inputText ,url_first_image,resolution=resolution)
            #no rellevant: move from  stable diffusion to gemini
            #pathImage = imageAIMaker.makeImageAI(inputText , steps , height_images  , width_images , staticNumIdPic)
            #staticNumIdPic+=1
            voice_file_url = None
            if make_voice:
                voice_file_url = newVoiceFile(pages_text[i],f"{self.title}_page{i}_voice")
            self.pages.append(page(pages_text[i] , pathImage,voice_file_url)) 





