import cohere # Import the Cohere library for AI services.
from rich import print # Import the Rich library to enhance terminal outputs.
from dotenv import dotenv_values # Import dotenv to load environment variables from a .env file.
import os

# ---------------- SAFE ENV LOADING ----------------
# Get absolute path of .env (Phenomenon folder me)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
env_vars = dotenv_values(env_path)
CohereAPIKey = os.getenv("CohereAPIKey") or env_vars.get("CohereAPIKey")
co = cohere.Client(api_key=CohereAPIKey)

"""
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
co = cohere.Client(api_key=CohereAPIKey)
"""


# Define a list of recognized function keywords for task categorization.
funcs =["exit", "general", "realtime", "open", "close", "play",
         "generate image", "system", "content", "google search",
         "youtube search","reminder"]

# Initialize an empty list to store user messages.
messages = []

# Define the preamble that guides the AI model on how to categorize queries.
preamble = """
You are a very accurate Decision-Making Model (DMM) that decides the type of a user query.
You will NEVER answer the query yourself. Your job is ONLY to classify the query as one of these types:

1. 'general (query)' → Queries that can be answered by an AI LLM using general knowledge and do NOT require real-time information.
   Example: 'Who wrote Harry Potter?', 'What is Python programming?'

2. 'realtime (query)' → Queries that require current or real-time information from the internet, like latest news, stock prices, weather, or ongoing events.
   Example: 'Who is Elon Musk?', 'What is the score of India vs Australia match?', 'What is today's date?'

3. 'open (application name)' → Queries asking to open any app or website.
   Example: 'open chrome', 'open facebook'

4. 'close (application name)' → Queries asking to close any app.
   Example: 'close notepad', 'close whatsapp'

5. 'play (song name)' → Queries asking to play music (usually on YouTube).
   Example: 'play let it be', 'play afsanay by ys'

6. 'generate image (image prompt)' → Queries asking to generate an image.
   Example: 'generate image of a cat', 'generate image of a futuristic city'

7. 'reminder (datetime with message)' → Queries to set reminders.
   Example: 'set a reminder at 9:00pm on 25th June for gym'

8. 'system (task name)' → Queries to perform system tasks like mute, unmute, volume up/down.
   Example: 'volume up', 'mute microphone'

9. 'content (topic)' → Queries asking to write content like code, emails, essays, or articles.
   Example: 'write a python function for factorial', 'draft an email to my boss'

10. 'google search (topic)' → Queries asking to search on Google.
    Example: 'search Python tutorials on google'

11. 'youtube search (topic)' → Queries asking to search on YouTube.
    Example: 'search lo-fi music on youtube'

*** Special Rules ***

- If multiple tasks are in one query, respond with each task separated by commas.
  Example: 'open facebook and telegram, close whatsapp' → 'open facebook, open telegram, close whatsapp'

- If user says goodbye, ending the conversation, respond with 'exit'.
  Example: 'bye Jarvis' → 'exit'

- Always classify queries requiring current facts, news, events, or latest info as 'realtime (query)'.
- If unsure or the query type is not mentioned above, classify as 'general (query)'.

*** Do NOT answer the query yourself, ONLY classify it. ***
"""

# Define a chat history with predefined user-chatbot interactions for context.
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox."},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm."},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]


# Define the main function for decision-making on queries.
def FirstLayerDMM(prompt: str = "test"):

    # Add user's query to messages
    messages.append({"role": "user", "content": f"{prompt}"})

    # Stream from Cohere model
    stream = co.chat_stream(
        model='command-a-03-2025',  # Updated model
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    # Capture text from stream
    response = ""
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text


    # Clean output
    response=response.replace("\n", " ")
    response=response.split(",")

    response=[ i.strip() for i in response]

    temp=[]
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    
    response=temp

    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return response

# Entry point for the script.
if __name__ == "__main__":
    # Continuously prompt the user for input and process it.
    while True:
        print(FirstLayerDMM(input(">>> ")))