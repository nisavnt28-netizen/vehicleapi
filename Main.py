# ================= FRONTEND IMPORTS =================
from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

# ================= BACKEND IMPORTS =================
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealTimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition , driver 
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

# ================= OTHER IMPORTS =================
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import time


# Main.py ke top me
# ================= LOAD ENV VARIABLES =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Phenomenon folder
env_path = os.path.join(BASE_DIR, ".env")
env_vars = dotenv_values(env_path)

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")

# ================= FOLDERS =================
DATA_DIR = os.path.join(BASE_DIR, "Data")
FILES_DIR = os.path.join(BASE_DIR, "Frontend", "Files")
GRAPHICS_DIR = os.path.join(BASE_DIR, "Frontend", "graphics")

# ================= DEFAULT MESSAGE =================
DefaultMessage = f"""
{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?
"""

subprocesses = []

# ================= FUNCTIONS LIST =================
Functions = ["open", "close", "play", "system", "content","google search","youtube search"]

# ========================== CLEANUP FUNCTION ==========================
def SafeExit():

    SetMicrophoneStatus("False")
    try:
        driver.quit()   # Selenium driver close karega, mic band ho jayega
    except Exception as e:
        print(f"Driver quit failed: {e}")

    # 2️⃣ Thoda wait karo taaki background tasks complete ho jaye
    time.sleep(2)

    # 3️⃣ Program terminate
    print("Exiting program...")
    os._exit(0)

# ================== GUI / INITIALIZATION FUNCTIONS ==================
def ShowDefaultChatIfNoChats():
    with open(os.path.join(DATA_DIR, "ChatLog.json"), "r", encoding="utf-8") as file:
        if len(file.read()) < 5:
            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
                file.write("")
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
                file.write(DefaultMessage)

def ReadChatLogJson():
    with open(os.path.join(DATA_DIR, "ChatLog.json"), "r", encoding="utf-8") as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username +" ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname +" ")

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    file_path = TempDirectoryPath('Database.data')
    with open(file_path, "r", encoding='utf-8') as file:
        data = file.read()
    if len(data) > 0:
        lines = data.split('Xn')
        result = '\n'.join(lines)
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(result)

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


# Run initial setup
InitialExecution()

# ================== MAIN EXECUTION ==================
def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening ... ")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking ... ")

    Decision = FirstLayerDMM(Query)
    print(f"Decision: {Decision}")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    if ImageExecution:
        with open(os.path.join(FILES_DIR, "ImageGeneration.data"), "w", encoding="utf-8") as file:
            file.write(f"{ImageGenerationQuery}, True")
        try:
            pl = subprocess.Popen(
                ["python", os.path.join(BASE_DIR, "Backend", "ImageGeneration.py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(pl)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R:
        SetAssistantStatus("Searching …")
        Answer = RealTimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering …")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking..." )
                QueryFinal = Queries.replace("general ","")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname}:{Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching …")
                QueryFinal = Queries.replace("real time", "")
                Answer = RealTimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering …")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering …")
                TextToSpeech(Answer)
                SafeExit()



            # driver = tumhara Selenium driver instance
            # ================== THREADS ==================
def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available …" not in AIStatus:
                SetAssistantStatus("Available …")
            sleep(0.1)

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()