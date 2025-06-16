import requests
from random import randint
from requests.auth import HTTPBasicAuth
from time import sleep
# Making a get request
# response = requests.get('https://api.github.com / user, ',
#             auth = HTTPBasicAuth('user', 'pass'))


data_user = {
    "email" :"yam@smail.com",
    "password" :"yamking113"
}

res = requests.post('http://127.0.0.1:5000/api/auth/login' , json=data_user)
print("Status Code:", res.status_code)
#print("Response:", res.json())
data_return1 = res.json()
token = data_return1["token"]
print(f"token {token}")


# Prepare request headers with Bearer token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Data to send
subject_lists = [
    'cats and cats food',
    'fish and how they have fun underwater',
    'a boy how goes to school and makes new friends',
    'a mom and her son during a missile attack',
    'girls having fun in the mall'
]
discription = 'short and sweet, made for children'


for subject in subject_lists:
    data_for_story = {
        "subject": subject,
        "description": discription,
        "numPages": randint(3, 5),
        "auther":"Yam Horin Tester",
        "title":"",
        "text_to_voice":True,
        "resolution":"1024X570",
    }

    # Send the request to generate the story
    response = requests.post(
        'http://127.0.0.1:5000/api/story-ai/MagicOfStory/Story',
        json=data_for_story,
        headers=headers
    )

    print(f"Request for subject '{subject}': Status {response.status_code}")
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Error response:", response.text)
    for i in range(0,24,1):
        print("sleep to prevent overload the gemini")
        sleep(10)
