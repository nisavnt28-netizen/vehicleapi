import os
from time import sleep
from PIL import Image
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# ==================== DIRECTORIES ====================

# PHENOMENON root detect (works from Main.py and direct run)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "Data")
FILES_DIR = os.path.join(BASE_DIR, "Frontend", "Files")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FILES_DIR, exist_ok=True)

# ==================== ENV VARS ====================

load_dotenv(os.path.join(BASE_DIR, ".env"))
HF_TOKEN = os.environ.get("HuggingFaceAPIKey")
client = InferenceClient(api_key=HF_TOKEN)

# ==================== OPEN IMAGES ====================

def open_images(prompt: str):
    prompt_clean = prompt.replace(" ", "_")
    for i in range(1, 5):
        image_path = os.path.join(DATA_DIR, f"{prompt_clean}_{i}.png")
        try:
            img = Image.open(image_path)
            print(f"Opening: {image_path}")
            img.show()
            sleep(1)
        except Exception as e:
            print(f"Unable to open {image_path}: {e}")

# ==================== GENERATE IMAGES ====================

def GenerateImages(prompt: str):
    print("Requesting images from Hugging Face…")
    prompt_clean = prompt.replace(" ", "_")

    for i in range(4):
        img = client.text_to_image(
            prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            height=1024,
            width=1024
        )
        filename = os.path.join(DATA_DIR, f"{prompt_clean}_{i+1}.png")
        img.save(filename)
        print(f"Saved: {filename}")

    open_images(prompt)

# ==================== MONITOR IMAGE GENERATION FILE ====================

while True:
    try:
        file_path = os.path.join(FILES_DIR, "ImageGeneration.data")

        with open(file_path, "r") as f:
            Data = f.read()

        if not Data:
            sleep(1)
            continue

        Prompt, Status = [x.strip() for x in Data.split(",")]

        if Status == "True":
            print("Generating Images …")
            GenerateImages(Prompt)

            # Reset file
            with open(file_path, "w") as fw:
                fw.write("False, False")

            break
        else:
            sleep(1)

    except Exception as e:
        print("Error monitoring file:", e)
        sleep(1)