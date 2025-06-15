from . import memoryManager
import requests
from .qualityEnum import fileType

#version 1 with satble diffusion ,  imports not rellevent
# import torch
# from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
# from PIL import ImageFilter
# from diffusers import AutoPipelineForImage2Image
# from diffusers.utils import load_image

import uuid
from io import BytesIO
from google import genai
from os import getenv
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
from dotenv import load_dotenv


# # #version 1 with satble diffusion , not rellevent
# def makeImageAI(prompt, steps, height, width, idPictuere):
#     model_id = "stabilityai/stable-diffusion-2"

#     scheduler = EulerDiscreteScheduler.from_pretrained(model_id, subfolder="scheduler")
#     pipe = StableDiffusionPipeline.from_pretrained(model_id, scheduler=scheduler, torch_dtype=torch.float16)
#     pipe = pipe.to("cuda")
#     image = pipe(   prompt = prompt +",cartoon,children story style,8K",
#                     negative_prompt="extra heads,extra limbs, missing arms, missing legs, bad anatomy, low quality, blurry",
#                     height = height,
#                     width = width,
#                     guidance_scale=9.5,
#                     num_inference_steps=steps
#                 ).images[0]
#     print("making image complete ")
#     fileName  = f'image {idPictuere}.png'
#     image = image.filter(ImageFilter.DETAIL)
#     image.save(fileName)
#     print(f"image saved as {fileName}")
#     return memoryManager.save_file(fileName ,fileType.png)

#version 2 with google gemini


def makeImageAI(prompt, resolution=""):
    load_dotenv(override=True)
    apiKey = getenv("API_KEY")
    client = genai.Client(api_key=apiKey)

    # הוספת מידע לבקשת התמונה
    prompt += f", 4K definition, resolution = {resolution}"
    contents = prompt

    max_attempts = 5
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            # יצירת שם אקראי לתמונה
            idPicture = str(uuid.uuid4())[1:6]
            fileName = f'image_{idPicture}.png'
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # image = Image.open(BytesIO(part.inline_data.data))
                    image_bytes = base64.b64decode(part.inline_data.data)
                    image = Image.open(BytesIO(image_bytes))                    
                    if resolution != "":
                        image = image.resize(turnStringintoResolution(resolution))
                    image.save(fileName)
                    print(f"✅ Image saved as {fileName} | size: {image.size}")
                    return memoryManager.save_file(fileName ,fileType.png)

                elif part.text is not None:
                    print(f"[INFO] TEXT response: {part.text}")

        except Exception as e:
            print(f"⚠️ Error during image generation: {e}")

    raise RuntimeError("❌ Failed to generate image after multiple attempts.")
# # # #version 1 Stable Diffusion not Rellvant
# def makeImageFromImage(prompt, steps, height, width, idPictuere , url_image_source):
#     pipeline = AutoPipelineForImage2Image.from_pretrained(
#     "stabilityai/stable-diffusion-xl-refiner-1.0", torch_dtype=torch.float16, variant="fp16", use_safetensors=True
#     )
#     pipeline.enable_model_cpu_offload()

#     # Load image from URL
#     response = requests.get(url_image_source)
#     response.raise_for_status()  # Raise an error for bad responses
#     init_image = Image.open(BytesIO(response.content)).convert("RGB")


    
#     # pass prompt and image to pipeline
#     image = pipeline(prompt, 
#                     image=init_image,
#                     height = height,
#                     width = width, 
#                     strength=0.7).images[0] ## More creative divergence from source
#     print("making image complete ")
#     fileName  = f'image {idPictuere}.png'
#     image = image.filter(ImageFilter.DETAIL)
#     image.save(fileName)
#     print(f"image saved as {fileName}")
#     return memoryManager.save_file(fileName ,fileType.png)

#version 2 google gemini

def makeImageFromImage(prompt, url_image_source, resolution=""):
    # Load API key
    load_dotenv(override=True)
    apiKey = getenv("API_KEY")
    client = genai.Client(api_key=apiKey)
    # Enhance the prompt with consistency and resolution
    prompt += ", making sure to maintain consistent visual elements such as [clothing, colors, background, art style, recurring objects]"
    prompt += f", 4K definition, resolution = {resolution}"

    # Load the reference image from URL
    try:
        response = requests.get(url_image_source)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to load image from URL: {e}")

    text_input = prompt

    # Generate a unique file name
    idPicture = str(uuid.uuid4())[1:6]
    fileName = f"image_{idPicture}.png"
    max_attempts = 5
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=[text_input, image],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            for part in response.candidates[0].content.parts:
                if part.text:
                    print(f"[INFO] Gemini responded:\n{part.text}\n")
                elif part.inline_data:
                    # Load image from the inline data
                    # image_result = Image.open(BytesIO(part.inline_data.data))
                    image_bytes = base64.b64decode(part.inline_data.data)
                    image_result = Image.open(BytesIO(image_bytes))
                    # Resize if needed
                    if resolution:
                        image_result = image_result.resize(turnStringintoResolution(resolution))
                    image_result.save(fileName)
                    print(f"✅ Image saved as {fileName} | size: {image_result.size}")
                    # Return result from memoryManager
                    return memoryManager.save_file(fileName, fileType.png)

        except Exception as e:
            print(f"⚠️ Attempt {attempts} failed: {e}")

    raise RuntimeError("❌ Failed to generate image after multiple attempts.")
                
def turnStringintoResolution(str_res : str):
    str_res = str_res.lower()
    resolution = []
    slice_place = str_res.find('x')
    resolution.append(int(str_res[0:slice_place]))
    resolution.append(int(str_res[slice_place+1:len(str_res)]))
    print(resolution)
    return (resolution[0] , resolution[1])



#version 1 Stable Diffusion not Rellvant

# def makeImagesFromPrompts(prompts, steps, height, width, idPrefix, url_image_source):
#     # Load the model once
#     pipeline = AutoPipelineForImage2Image.from_pretrained(
#         "stabilityai/stable-diffusion-xl-refiner-1.0",
#         torch_dtype=torch.float16,
#         variant="fp16",
#         use_safetensors=True
#     )
#     pipeline.enable_model_cpu_offload()

#     # Load source image from URL
#     response = requests.get(url_image_source)
#     response.raise_for_status()
#     init_image = Image.open(BytesIO(response.content)).convert("RGB")

#     urls = []

#     for i, prompt in enumerate(prompts):
#         print(f"Generating image for prompt {i + 1}/{len(prompts)}...")

#         # Generate image from prompt
#         image = pipeline(
#             prompt,
#             image=init_image,
#             height=height,
#             width=width,
#             strength=0.9
#         ).images[0]

#         image = image.filter(ImageFilter.DETAIL)
#         fileName = f'image_{idPrefix}_{i}.png'
#         image.save(fileName)

#         print(f"Image {i + 1} saved as {fileName}")
#         image_url = memoryManager.save_file(fileName, fileType.png)
#         urls.append(image_url)

#     print("All images generated and saved.")
#     return urls




