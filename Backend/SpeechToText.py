from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# ================= PATH FIX =================

CURRENT_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_FILE)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

env_path = os.path.join(ROOT_DIR, ".env")
env_vars = dotenv_values(env_path)

InputLanguage = os.getenv("InputLanguage") or env_vars.get("InputLanguage")

VOICE_HTML_PATH = os.path.join(ROOT_DIR, "Data", "Voice.html")
TempDirPath = os.path.join(ROOT_DIR, "Frontend", "Files")

# ============================================


# ------------------ HTML TEMPLATE ------------------
HtmlCode="""<!DOCTYPE html>
<html>
<head>
    <title>Speech Recognition</title>
</head>
<body>

<button id="start">Start Recognition</button>
<button id="end">Stop Recognition</button>

<p id="output"></p>

<script>
const output = document.getElementById("output");
let recognition;
let recognizing = false;

function startRecognition() {
    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';  // replace with dynamic language if needed
    recognition.continuous = true;
    recognizing = true;

    recognition.onresult = function(event) {
        const transcript = event.results[event.results.length - 1][0].transcript;
        output.textContent += transcript;
    };

    recognition.onend = function() {
        if (recognizing) {
            recognition.start(); // restart only if not stopped
        }
    };

    recognition.start();
}

function stopRecognition() {
    recognizing = false;  // prevent auto-restart
    if (recognition) {
        recognition.stop();
        recognition = null; // release reference and mic
    }
}

// Bind buttons
document.getElementById("start").onclick = startRecognition;
document.getElementById("end").onclick = stopRecognition;
</script>

</body>
</html>"""

HtmlCode = str(HtmlCode).replace(
    "recognition.lang = '';",
    f"recognition.lang = '{InputLanguage}';"
)

# Write HTML
with open(VOICE_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

Link = VOICE_HTML_PATH


chrome_options = Options()
user_agent ="Mozilla/5.0 (Windows NT 10.0; Win64 ; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("use-fake-ui-for-media-stream")
chrome_options.add_argument("use-fake-device-for-media-stream")
chrome_options.add_argument("headless=new")
chrome_options.add_argument("--disable-background-networking")
chrome_options.add_argument("--disable-background-timer-throttling")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")

service = Service(ChromeDriverManager().install())
global driver
driver = webdriver.Chrome(service=service, options=chrome_options)


def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words=new_query.split()
    question_words = [
        "what", "who", "where", "when",
        "why", "how", "can you",
        "could you", "do you"
    ]

    if any(word + " " in new_query for word in question_words):

        if query_words[-1][-1] in ['.', '?',"!"]:
            new_query=new_query[:-1]+"?"
        else:
            new_query += '?'

    else:
        if query_words[-1][-1] in ['.', '?',"!"]:
            new_query = new_query[:-1]+"."
        else:
            new_query += '.'

    return new_query.capitalize()


def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()


def SpeechRecognition():
    driver.get("file:///" + Link.replace("\\", "/"))

    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text

            if Text:
                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)

                SetAssistantStatus("Translating...")
                return QueryModifier(UniversalTranslator(Text))

        except Exception:
            pass


if __name__ == "__main__":
        while True:
            Text = SpeechRecognition()
            print(Text)