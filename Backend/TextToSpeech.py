import os
import random
import asyncio
import pygame
from dotenv import dotenv_values
import edge_tts

# ================= PATH CONFIG =================
# Get ROOT_DIR (PHENOMENON folder)
CURRENT_FILE = os.path.abspath(__file__)      # Backend/speech/TextToSpeech.py
BACKEND_DIR = os.path.dirname(CURRENT_FILE)  # Backend/speech
ROOT_DIR = os.path.dirname(BACKEND_DIR)  # PHENOMENON

# Load .env
env_path = os.path.join(ROOT_DIR, ".env")
env_vars = dotenv_values(env_path)
AssistantVoice = env_vars.get("AssistantVoice")


# Data folder path
DATA_DIR = os.path.join(ROOT_DIR, "Data")
AUDIO_FILE = os.path.join(DATA_DIR, "speech.mp3")

# ================= FUNCTIONS =================

async def TextToAudioFile(text) -> None:
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)

    communicate = edge_tts.Communicate(text, AssistantVoice, pitch="+5Hz", rate="+5%")
    await communicate.save(AUDIO_FILE)

def TTs(Text, func=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(Text))
            pygame.mixer.init()
            pygame.mixer.music.load(AUDIO_FILE)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)
            return True

        except Exception as e:
            print(f"TTS Error: {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except Exception as e:
                print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    responses = [
        "The rest of the result has been printed to the chat screen.",
        "The rest of the text is now on the chat screen, sir, please check it out.",
        "You can see the rest of the text on the chat screen, sir, kindly check it out.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for more.",
        "You'll find more to read on the chat screen.",
        "Sir, check the chat screen for the continuation.",
        "The chat screen has more information.",
        "There's more to see on the chat screen for additional text.",
        "Please read on the chat screen, sir.",
        "Check the screen for the rest of the text.",
        "Here's the rest of the text, sir.",
        "Look on the chat screen, sir, please.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out, sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    # Split long text into chunks (max 250 chars per chunk)
    Data = str(Text).split(".")
    if len(Text) >= 250 and len(Data):
        chunk = " ".join(Data[0:2]) + ". " + random.choice(responses)
        TTs(chunk, func)
    else:
        TTs(Text, func)

# ================= MAIN =================
if __name__ == "__main__":
    print("Text-to-Speech System Ready. Type your text:")
    while True:
        TTs(input("Enter the text: "))