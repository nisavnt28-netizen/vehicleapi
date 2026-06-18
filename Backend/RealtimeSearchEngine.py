from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
import os

# Load environment variables
"""
env_vars = dotenv_values("..\.env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)
"""

# Absolute path of .env (Phenomenon folder me)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
env_vars = dotenv_values(env_path)

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

GroqAPIKey = os.getenv("GroqAPIKey") or env_vars.get("GroqAPIKey")
client = Groq(api_key=GroqAPIKey)


# ---------------- SAFE BASE PATH ----------------
DATA_DIR = os.path.join(BASE_DIR, "Data")
CHATLOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# Ensure Data folder exists
#os.makedirs(DATA_DIR, exist_ok=True)

System = f"""

Hello, I am {Username}.
You are {Assistantname}, an accurate and professional AI assistant.

Rule:*Always remember you need to speak in English *

You will be given Google search results as context.

Your task is to:
- Extract the most relevant and recent information.
- Provide a clear, concise, and professional answer.
- Keep the response within 2–4 sentences.
- Do not list multiple conflicting figures unless necessary.
- If multiple sources differ, mention it briefly and clearly.
- Do not add information outside the provided search results.
- Do not explain your reasoning.

Only provide the final answer.
Answer strictly based on the provided data.
Only give full explanaition when asked , otherwise always give short ans as enstructed before .

"""

# Try to load the chat log from a JSON file,
# or create an empty one if it doesn't exist.
#
#try:
#    with open(r"..\Data\ChatLog.json", "r") as f:
#        messages = load(f)
#except:
#    with open(r"..\Data\ChatLog.json", "w") as f:
#        dump([], f)

try:
    with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)
except :
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        dump([], f)       


# Function to perform a Google search and format the results.
def Googlesearch(query):
    results = list(search(query, advanced=True, num_results=5))

    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer +=  f"Title: {i.title}\nDescription: {i.description}\n\n"
    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "HI"},
    {
        "role": "assistant",
        "content": "Hello, how can I help you?"
    }
]

def Information():
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

def RealTimeSearchEngine(prompt):

    global SystemChatBot, messages

    # Load the chat log from the JSON file
    """with open(r"..\Data\ChatLog.json", "r") as f:
        messages = load(f)"""
    with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)

    # Add user prompt to messages
    messages.append({
        "role": "user",
        "content": f"{prompt}"
    })

    # Add Google search results to system messages
    SystemChatBot.append({
        "role": "system",
        "content": Googlesearch(prompt)
    })

    # Generate response using Groq client
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=SystemChatBot + [
            {"role": "system", "content": Information()}
        ] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")

    messages.append({
        "role": "assistant",
        "content": Answer
    })
    """
    with open(r"..\Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)"""
    
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        dump(messages, f,indent=4)

    SystemChatBot.pop()

    return AnswerModifier(Answer=Answer)


if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealTimeSearchEngine(prompt))
