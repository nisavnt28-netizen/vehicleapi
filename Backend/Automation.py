# ---------------- IMPORTS ----------------
import os
import asyncio
import webbrowser
import subprocess
import requests
import keyboard
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from pywhatkit import search , playonyt
from AppOpener import open as appopen, close 
from webbrowser import open as webopen
from groq import Groq

# ---------------- ENVIRONMENT ----------------

# ---------------- Load .env ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "Data")
os.makedirs(DATA_DIR, exist_ok=True)

env_path = os.path.join(BASE_DIR, ".env")
env_vars = dotenv_values(env_path)

GroqAPIKey = os.getenv("GroqAPIKey") or env_vars.get("GroqAPIKey")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

if not GroqAPIKey:
    raise Exception(f"GroqAPIKey not found in .env at {env_path}")

# ---------------- Initialize Groq client ----------------
client = Groq(api_key=GroqAPIKey)

# ---------------- Other variables ----------------

classes = [
    "zCubwf", "hgKElc", "LTKOO", "sY7ric", "Z0LcW",
    "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc",
    "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers table webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "SPZz6b",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc"
]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {Username}, you're a content writer . You have to write content like letter "}
]

def GoogleSearch(Topic):
    search(Topic)
    return True 


def Content(Topic):

    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>","")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic: str = Topic.replace("Content", "")
    ContentByAI = ContentWriterAI(Topic)

    filename = os.path.join(DATA_DIR, f"{Topic.lower().replace(' ','')}.txt")

    with open(filename, "w", encoding="utf-8") as file:
        file.write(ContentByAI)

    OpenNotepad(filename)
    return True


def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True



def OpenApp(app, sess=requests.session()):
    try:
        if(app=="Youtube" or "youtube"):
            raise Exception("Force error")
        else :
            appopen(app, match_closest=True, output=True , throw_error=True)
            return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]
        
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
            return None
        
        html = search_google(app)

        if html:
            links = extract_links(html)

            if links:   # 🔥 SAFE CHECK ADDED
                webopen(links[0])
            else:
                # Agar scraping fail ho jaye to direct Google open kar do
                webopen(f"https://www.google.com/search?q={app}")

        return True 
    


def CloseApp(target):
    """
    Smart and safe closing system for the assistant.
    Prevents assistant termination.
    """

    target = target.lower()

    try:
        # ---------------- CLOSE TAB ----------------
        if target in ["tab", "current tab", "this tab" , "youtube"]:
            keyboard.press_and_release("ctrl+w")
            print("Tab closed safely ✅")
            return True

        # ---------------- CLOSE WINDOW ----------------
        if target in ["window", "current window"]:
            keyboard.press_and_release("alt+f4")
            print("Window closed safely 🪟")
            return True

        # ---------------- PROTECT BROWSERS ----------------
        protected = ["chrome", "edge", "brave", "firefox", "browser"]

        if any(p in target for p in protected):
            print("Browser close blocked to protect assistant 🛡️")
            return True

        # ---------------- CLOSE NORMAL APPS ----------------
        close(target, match_closest=True, output=True, throw_error=False)
        print(f"{target} closed successfully ✅")
        return True

    except Exception as e:
        print(f"CloseSystem error: {e}")
        return False
    

def System(command):

    def mute():
        keyboard.press_and_release('volume mute')

    def unmute():
        keyboard.press_and_release('volume mute')

    def volume_up():
        keyboard.press_and_release('volume up')

    def volume_down():
        keyboard.press_and_release('volume down')

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open"):
            if "open it" in command:
                pass
            elif "open file" in command:
                pass
            else:
                # Example placeholder function
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general"):
            pass

        elif command.startswith("realtime"):
            pass

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system"):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found For: {command}")

    results = await asyncio.gather(*funcs)  # Execute all functions concurrently
    
    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield str(result)


# Main async automation function
async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

