from groq import Groq
from json import load, dump
import datetime
import os
from dotenv import dotenv_values

"""

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey) 

"""

"or"

# Absolute path of Phenomenon folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
env_vars = dotenv_values(env_path)
GroqAPIKey = os.getenv("GroqAPIKey") or env_vars.get("GroqAPIKey")
if not GroqAPIKey:
    raise ValueError(f"GroqAPIKey not found in .env at {env_path}")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
client = Groq(api_key=GroqAPIKey) 

DATA_DIR = os.path.join(BASE_DIR, "Data")
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")
# Ensure Data folder exists
#os.makedirs(DATA_DIR, exist_ok=True)

messages = []

System = f"""
Hello, I am {Username}.
You are a highly accurate and advanced AI chatbot named {Assistantname}.
You have access to real-time, up-to-date information.

CORE RULES:
1. Do not tell the time unless specifically asked.
2. Be concise.
3. *Always reply in English.
4. No internal metadata.
5. Never mention training data.
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

"""
# Ensure Data folder exists
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
# Load or create ChatLog

try:
    with open(r"..\Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"..\Data\ChatLog.json", "w") as f:
        dump([], f)

(.....or......)
"""

try:
    with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)
except :
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        dump([], f)
    
       



def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : "
        f"{now.strftime('%M')} minutes : "
        f"{now.strftime('%S')} seconds."
    )


def AnswerModifier(Answer):
    lines = Answer.split("\n")
    cleaned = [line for line in lines if line.strip()]
    return "\n".join(cleaned)


def ChatBot(Query):
    try:
        """with open(r"..\Data\ChatLog.json", "r") as f:
            messages = load(f)
        
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)"""
        
        with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
            messages = load(f)

        messages.append({
            "role": "user",
            "content": Query
        })

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=SystemChatBot+
                     [{"role": "system", "content": RealtimeInformation()}] +
                     messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        messages.append({
            "role": "assistant",
            "content": Answer
        })

        """with open(r"..\Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        """

        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            dump(messages, f, indent=4)    
  

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")

        """with open(r"..\Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        """

        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            dump([], f)    
        return ChatBot(Query)    
        


if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question: ")
        print(ChatBot(user_input))