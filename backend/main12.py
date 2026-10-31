import base64
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from sarvamai import SarvamAI

import requests

import json

import re
def detect_response_language(text: str) -> str:
    kannada_chars = sum(
        1 for char in text
        if "\u0C80" <= char <= "\u0CFF"
    )

    latin_chars = sum(
        1 for char in text
        if char.isascii() and char.isalpha()
    )

    if kannada_chars > 0 and kannada_chars >= latin_chars:
        return "Kannada"

    return "English"


from commands import execute_command

from web_search import web_search





# ==================================================

# FASTAPI APP

# ==================================================



app = FastAPI()

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

sarvam_client = (
    SarvamAI(api_subscription_key=SARVAM_API_KEY)
    if SARVAM_API_KEY
    else None
)



# ==================================================

# CORS

# ==================================================



app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173",

        "http://127.0.0.1:5173",

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)





# ==================================================

# REQUEST MODEL

# ==================================================



class ChatRequest(BaseModel):

    message: str





# ==================================================

# HOME

# ==================================================



@app.get("/")

def home():

    return {

        "status": "Nexa backend is running"

    }

class KannadaTTSRequest(BaseModel):
    text: str


@app.post("/api/tts/kannada")
def kannada_tts(request: KannadaTTSRequest):
    if not sarvam_client:
        raise HTTPException(
            status_code=500,
            detail="Sarvam API key is missing from backend/.env",
        )

    text = request.text.strip()
    print("KANNADA TEXT RECEIVED:", repr(text))
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty",
        )

    if len(text) > 2500:
        raise HTTPException(
            status_code=400,
            detail="Text is too long for one speech request",
        )

    try:
        result = sarvam_client.text_to_speech.convert(
    text=text,
    language_code="kn-IN",
    speaker="ishita",
    model="bulbul:v3",
    pace=1.0,
    temperature=0.75,
    output_audio_codec="wav",
)
        

        if not result.audios:
            raise HTTPException(
                status_code=502,
                detail="Sarvam returned no audio",
            )

        audio_bytes = base64.b64decode(result.audios[0])

        return Response(
            content=audio_bytes,
            media_type="audio/wav",
        )

    except HTTPException:
        raise

    except Exception as error:
        print("SARVAM TTS ERROR TYPE:", type(error).__name__)
        print("SARVAM TTS ERROR DETAILS:", str(error))
        raise HTTPException(
            status_code=502,
            detail="Could not generate Kannada speech",
        )





# ==================================================

# EXTRACT JSON

# ==================================================



def extract_json(text: str):



    text = text.strip()



    # Remove Qwen thinking section

    text = re.sub(

        r"<think>.*?</think>",

        "",

        text,

        flags=re.DOTALL

    )



    # Remove markdown

    text = text.replace("\`\`\`json", "")

    text = text.replace("\`\`\`", "")

    text = text.strip()



    # Try complete JSON

    try:

        return json.loads(text)



    except json.JSONDecodeError:

        pass



    # Find JSON inside other text

    matches = re.findall(

        r'\{[^{}]*"intent"\s*:\s*"[^"]+"\s*\}',

        text

    )



    if matches:

        try:

            return json.loads(matches[-1])



        except json.JSONDecodeError:

            pass



    return None





# ==================================================

# AI COMMAND UNDERSTANDING

# ==================================================



def understand_command(user_message):
    prompt = f"""
You are Nexa's command classifier.
Understand user commands in English, Kannada, and
Kannada-English mixed language.

AVAILABLE INTENTS:

Examples:
User: ಕ್ಯಾಲ್ಕುಲೇಟರ್ ತೆರೆಯಿರಿ
Answer: {{"intent":"OPEN_CALCULATOR"}}

User: Chrome ತೆರೆ
Answer: {{"intent":"OPEN_CHROME"}}


User: ವಾಲ್ಯೂಮ್ ಜಾಸ್ತಿ ಮಾಡು
Answer: {{"intent":"VOLUME_UP"}}

User: ಧ್ವನಿಯನ್ನು ಹೆಚ್ಚಿಸಿ
Answer: {{"intent":"VOLUME_UP"}}

User: ವಾಲ್ಯೂಮ್ ಕಡಿಮೆ ಮಾಡು
Answer: {{"intent":"VOLUME_DOWN"}}

User: ಧ್ವನಿಯನ್ನು ಕಡಿಮೆ ಮಾಡಿ
Answer: {{"intent":"VOLUME_DOWN"}}

User: ಧ್ವನಿಯ ಶಬ್ದವನ್ನು ಕಡಿಮೆ ಮಾಡಿ
Answer: {{"intent":"VOLUME_DOWN"}}

User: ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡಿ
Answer: {{"intent":"MUTE_VOLUME"}}
User: unmute the volume
Answer: {{"intent":"UNMUTE_VOLUME"}}

User: ಬ್ಯಾಟರಿ ಎಷ್ಟು ಇದೆ?
Answer: {{"intent":"BATTERY_STATUS"}}

User: ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ತೆಗೆ
Answer: {{"intent":"TAKE_SCREENSHOT"}}

User: ಡೌನ್‌ಲೋಡ್ಸ್ ತೆರೆಯಿರಿ
Answer: {{"intent":"OPEN_DOWNLOADS"}}

User: ಡೌನ್‌ಲೋಡ್ಸ್ ಓಪನ್ ಮಾಡಿ
Answer: {{"intent":"OPEN_DOWNLOADS"}}

User: Open Downloads
Answer: {{"intent":"OPEN_DOWNLOADS"}}

User: ರೀಸೈಕಲ್ ಬಿನ್ ತೆರೆಯಿರಿ
Answer: {{"intent":"OPEN_RECYCLE_BIN"}}

User: ರೀಸೈಕಲ್ ಬಿನ್ ಖಾಲಿ ಮಾಡಿ
Answer: {{"intent":"EMPTY_RECYCLE_BIN"}}

User: Open Recycle Bin
Answer: {{"intent":"OPEN_RECYCLE_BIN"}}

User: Empty Recycle Bin
Answer: {{"intent":"EMPTY_RECYCLE_BIN"}}

Rules:

1. Answer the user's actual question.
2. Use information from the search results.
3. Do not invent facts.
4. If information is uncertain, say so.
5. For current questions, mention that the information
   comes from current web search results.
6. Keep the answer concise.
7. Do not list URLs in your answer.
8. Do not use internal reasoning.

LANGUAGE RULES:

9. If the user asks in Kannada, answer entirely in natural Kannada script.
10. If the user asks in English, answer in English.
11. If the user asks in Kannada-English mixed language, follow the language they prefer.
12. In Kannada answers, translate ordinary English words into natural Kannada wherever appropriate.
13. Explain technical terms in Kannada on first use. Keep established names such as Python, Qwen, and AI when translation would be unclear.
14. Do not unnecessarily mix English words such as "Process" and "Store" into Kannada sentences when clear Kannada equivalents exist.
15. Preserve technical accuracy and the meaning of the original information.

Give only the final answer.





Your job is to decide whether the user wants:



1. A Windows action

2. A web search

3. Normal conversation



Classify the request into exactly ONE intent.



AVAILABLE INTENTS:



OPEN_CHROME

OPEN_VSCODE

OPEN_CALCULATOR

OPEN_NOTEPAD

OPEN_EXPLORER

OPEN_YOUTUBE

OPEN_GOOGLE

OPEN_DOWNLOADS

OPEN_DESKTOP

OPEN_DOCUMENTS

OPEN_PICTURES

OPEN_VIDEOS

OPEN_MUSIC

OPEN_SETTINGS

OPEN_TASK_MANAGER



VOLUME_UP

VOLUME_DOWN

MUTE_VOLUME



BRIGHTNESS_UP

BRIGHTNESS_DOWN



BATTERY_STATUS

TAKE_SCREENSHOT



GOOGLE_SEARCH

YOUTUBE_SEARCH

WEB_SEARCH



LOCK_COMPUTER

EMPTY_RECYCLE_BIN



NONE





WINDOWS COMMAND EXAMPLES:



User: open chrome

Answer:

{{"intent":"OPEN_CHROME"}}



User: launch my browser

Answer:

{{"intent":"OPEN_CHROME"}}



User: open calculator

Answer:

{{"intent":"OPEN_CALCULATOR"}}



User: show my documents

Answer:

{{"intent":"OPEN_DOCUMENTS"}}



User: open pictures

Answer:

{{"intent":"OPEN_PICTURES"}}



User: open my videos

Answer:

{{"intent":"OPEN_VIDEOS"}}



User: open music

Answer:

{{"intent":"OPEN_MUSIC"}}



User: open settings

Answer:

{{"intent":"OPEN_SETTINGS"}}





VOLUME EXAMPLES:



User: increase the volume

Answer:

{{"intent":"VOLUME_UP"}}



User: turn the volume up

Answer:

{{"intent":"VOLUME_UP"}}



User: make it louder

Answer:

{{"intent":"VOLUME_UP"}}



User: volume up

Answer:

{{"intent":"VOLUME_UP"}}



User: decrease the volume

Answer:

{{"intent":"VOLUME_DOWN"}}



User: turn the volume down

Answer:

{{"intent":"VOLUME_DOWN"}}



User: make it quieter

Answer:

{{"intent":"VOLUME_DOWN"}}



User: volume down

Answer:

{{"intent":"VOLUME_DOWN"}}



User: mute the volume

Answer:

{{"intent":"MUTE_VOLUME"}}



User: mute my computer

Answer:

{{"intent":"MUTE_VOLUME"}}



User: unmute

Answer:

{{"intent":"MUTE_VOLUME"}}





BRIGHTNESS EXAMPLES:



User: increase the brightness

Answer:

{{"intent":"BRIGHTNESS_UP"}}



User: make the screen brighter

Answer:

{{"intent":"BRIGHTNESS_UP"}}



User: turn up the brightness

Answer:

{{"intent":"BRIGHTNESS_UP"}}



User: brightness up

Answer:

{{"intent":"BRIGHTNESS_UP"}}



User: decrease the brightness

Answer:

{{"intent":"BRIGHTNESS_DOWN"}}



User: make the screen darker

Answer:

{{"intent":"BRIGHTNESS_DOWN"}}



User: turn down the brightness

Answer:

{{"intent":"BRIGHTNESS_DOWN"}}



User: brightness down

Answer:

{{"intent":"BRIGHTNESS_DOWN"}}





BATTERY EXAMPLES:



User: what is my battery percentage?

Answer:

{{"intent":"BATTERY_STATUS"}}



User: check my battery

Answer:

{{"intent":"BATTERY_STATUS"}}



User: how much battery do I have?

Answer:

{{"intent":"BATTERY_STATUS"}}



User: what's my battery status?

Answer:

{{"intent":"BATTERY_STATUS"}}





SCREENSHOT EXAMPLES:



User: take a screenshot

Answer:

{{"intent":"TAKE_SCREENSHOT"}}



User: take a screenshot of my screen

Answer:

{{"intent":"TAKE_SCREENSHOT"}}



User: capture my screen

Answer:

{{"intent":"TAKE_SCREENSHOT"}}



User: screenshot

Answer:

{{"intent":"TAKE_SCREENSHOT"}}





WEB SEARCH EXAMPLES:



User: search the web for latest AI news

Answer:

{{"intent":"WEB_SEARCH"}}



User: what is the latest AI news?

Answer:

{{"intent":"WEB_SEARCH"}}



User: what's happening in technology today?

Answer:

{{"intent":"WEB_SEARCH"}}



User: what is the weather today in Bangalore?

Answer:

{{"intent":"WEB_SEARCH"}}



User: Google React hooks

Answer:

{{"intent":"GOOGLE_SEARCH"}}



User: search Google for C++ tutorials

Answer:

{{"intent":"GOOGLE_SEARCH"}}



User: Google latest technology news

Answer:

{{"intent":"GOOGLE_SEARCH"}}



User: search YouTube for Python tutorials

Answer:

{{"intent":"YOUTUBE_SEARCH"}}



User: find C++ tutorials on YouTube

Answer:

{{"intent":"YOUTUBE_SEARCH"}}



User: YouTube Java tutorials

Answer:

{{"intent":"YOUTUBE_SEARCH"}}



User: what's the latest cricket score?

Answer:

{{"intent":"WEB_SEARCH"}}



User: will it rain today in Bangalore?

Answer:

{{"intent":"WEB_SEARCH"}}



User: who won today's cricket match?

Answer:

{{"intent":"WEB_SEARCH"}}



User: find the best laptop under 50000

Answer:

{{"intent":"WEB_SEARCH"}}



User: find laptops under 50000 rupees

Answer:

{{"intent":"WEB_SEARCH"}}



User: search React tutorials

Answer:

{{"intent":"WEB_SEARCH"}}



User: find information about Python

Answer:

{{"intent":"WEB_SEARCH"}}



User: look up Java programming tutorials

Answer:

{{"intent":"WEB_SEARCH"}}





NORMAL CONVERSATION:



User: what is artificial intelligence?

Answer:

{{"intent":"NONE"}}



User: tell me a joke

Answer:

{{"intent":"NONE"}}



User: hello

Answer:

{{"intent":"NONE"}}



User: explain recursion

Answer:

{{"intent":"NONE"}}





IMPORTANT:



Use WEB_SEARCH when the user asks for:



- latest information

- today's information

- current information

- news

- weather

- sports scores

- match results

- current prices

- products

- recent events

- online tutorials

- information that benefits from the internet



Use NONE for general knowledge questions that do not require current information.



Return ONLY JSON.



User request:

{user_message}

"""



    try:



        response = requests.post(

            "http://127.0.0.1:11434/api/chat",



            json={

                "model": "qwen3:1.7b",



                "messages": [

                    {

                        "role": "user",

                        "content": prompt

                    }

                ],



                "stream": False,

                "think": False,



                "options": {

                    "temperature": 0,

                    "num_predict": 50

                }

            },



            timeout=180

        )



        response.raise_for_status()



        data = response.json()



        content = data["message"]["content"].strip()



        print("RAW AI COMMAND RESPONSE:")

        print(content)



        result = extract_json(content)



        if not result:

            print("Could not extract JSON.")

            return "NONE"



        intent = result.get(

            "intent",

            "NONE"

        )



        allowed_intents = {

            "OPEN_CHROME",

            "OPEN_VSCODE",

            "OPEN_CALCULATOR",

            "OPEN_NOTEPAD",

            "OPEN_EXPLORER",

            "OPEN_YOUTUBE",

            "OPEN_GOOGLE",

            "OPEN_DOWNLOADS",

            "OPEN_DESKTOP",

            "OPEN_DOCUMENTS",

            "OPEN_PICTURES",

            "OPEN_VIDEOS",

            "OPEN_MUSIC",

            "OPEN_SETTINGS",

            "OPEN_TASK_MANAGER",



            "VOLUME_UP",

            "VOLUME_DOWN",

            "MUTE_VOLUME",
            "UNMUTE_VOLUME",

            "BRIGHTNESS_UP",

            "BRIGHTNESS_DOWN",



            "BATTERY_STATUS",

            "TAKE_SCREENSHOT",



            "LOCK_COMPUTER",

            "EMPTY_RECYCLE_BIN",



            "WEB_SEARCH",

            "GOOGLE_SEARCH",

            "YOUTUBE_SEARCH",



            "NONE"

        }



        if intent not in allowed_intents:



            print(

                "Unknown AI intent:",

                intent

            )



            return "NONE"



        return intent



    except requests.exceptions.RequestException as error:



        print(

            "AI COMMAND CONNECTION ERROR:",

            error

        )



        return "NONE"



    except Exception as error:



        print(

            "AI COMMAND ERROR:",

            error

        )



        return "NONE"





# ==================================================

# EXECUTE AI INTENT

# ==================================================



def execute_ai_intent(intent: str):



    intent_commands = {



        "OPEN_CHROME":

            "open chrome",



        "OPEN_VSCODE":

            "open vscode",



        "OPEN_CALCULATOR":

            "open calculator",



        "OPEN_NOTEPAD":

            "open notepad",



        "OPEN_EXPLORER":

            "open file explorer",



        "OPEN_YOUTUBE":

            "open youtube",



        "OPEN_GOOGLE":

            "open google",



        "OPEN_DOWNLOADS":

            "open downloads",



        "OPEN_DESKTOP":

            "open desktop",



        "OPEN_DOCUMENTS":

            "open documents",



        "OPEN_PICTURES":

            "open pictures",



        "OPEN_VIDEOS":

            "open videos",



        "OPEN_MUSIC":

            "open music",



        "OPEN_SETTINGS":

            "open settings",



        "OPEN_TASK_MANAGER":

            "open task manager",



        # ==============================

        # SYSTEM CONTROLS

        # ==============================



        "VOLUME_UP":

            "volume up",



        "VOLUME_DOWN":

            "volume down",



        "MUTE_VOLUME":

            "mute",
        "UNMUTE_VOLUME":
        "unmute",


        "BRIGHTNESS_UP":

            "brightness up",



        "BRIGHTNESS_DOWN":

            "brightness down",



        "BATTERY_STATUS":

            "battery status",



        "TAKE_SCREENSHOT":

            "take screenshot",

    }



    if intent in intent_commands:
        command = intent_commands[intent]
        return execute_command(command)

    if intent == "LOCK_COMPUTER":
        try:
            import ctypes
            result = ctypes.windll.user32.LockWorkStation()
            if result:
                return "Locking your computer now."
            return "Sorry, I could not lock your computer."
        except Exception as e:
            print("LOCK ERROR:", e)
            return "Sorry, I could not lock your computer."

    if intent == "EMPTY_RECYCLE_BIN":
        return "Emptying the Recycle Bin is not enabled yet."

    return None


# ==================================================

# EXTRACT SEARCH QUERY

# ==================================================



def extract_search_query(user_message: str):



    search_query = user_message.strip()



    phrases = [

        "search the web for",

        "search web for",

        "search the internet for",

        "search internet for",

        "search google for",

        "search google",

        "search for",

        "look up",

        "find information about",

        "find information on",

        "find information",

        "find",

        "google"

    ]



    for phrase in phrases:



        pattern = (

            r"^\s*"

            + re.escape(phrase)

            + r"\s+"

        )



        if re.search(

            pattern,

            search_query,

            flags=re.IGNORECASE

        ):



            search_query = re.sub(

                pattern,

                "",

                search_query,

                count=1,

                flags=re.IGNORECASE

            )



            break



    return search_query.strip()





# ==================================================

# SPECIAL SEARCH QUERY

# ==================================================




def extract_special_search_query(user_message: str):
    text = user_message.strip()
    normalized = text.lower()

    # Detect explicit Kannada Google searches first.
    if "ಗೂಗಲ್" in normalized and any(
        word in normalized for word in ["ಹುಡುಕು", "ಹುಡುಕಿ", "ಹುಡುಕಲು"]
    ):
        query = re.sub(r"ಗೂಗಲ್", "", text, flags=re.IGNORECASE)
        query = re.sub(
            r"ಹುಡುಕು|ಹುಡುಕಿ|ಹುಡುಕಲು",
            "",
            query
        )
        query = re.sub(r"ದಲ್ಲಿ|ನಲ್ಲಿ|ಗೆ", "", query)
        query = re.sub(r"[\u200c\u200d\ufeff]", "", query)
        query = query.strip(" \t.,!?")
        return "GOOGLE_SEARCH", query

    # Detect explicit Kannada YouTube searches.
    if "ಯೂಟ್ಯೂಬ್" in normalized and any(
        word in normalized for word in ["ಹುಡುಕು", "ಹುಡುಕಿ", "ಹುಡುಕಲು"]
    ):
        query = re.sub(r"ಯೂಟ್ಯೂಬ್", "", text, flags=re.IGNORECASE)
        query = re.sub(
            r"ಹುಡುಕು|ಹುಡುಕಿ|ಹುಡುಕಲು",
            "",
            query
        )
        query = re.sub(r"[\u200c\u200d\ufeff]", "", query)
        query = re.sub(r"ದಲ್ಲಿ|ನಲ್ಲಿ|ಗೆ", "", query)
        query = query.strip(" \t.,!?")
        query = " ".join(query.split())

        return "YOUTUBE_SEARCH", query

    google_patterns = [
        r"^google\s+(.+)$",
        r"^search google for\s+(.+)$",
    ]

    youtube_patterns = [
    r"^youtube\s+(.+)$",
    r"^search youtube for\s+(.+)$",
    r"^searching youtube for\s+(.+)$",
    r"^find\s+(.+)\s+on youtube$",
]

    for pattern in google_patterns:
        match = re.match(pattern, text, flags=re.IGNORECASE)
        if match:
            return "GOOGLE_SEARCH", match.group(1).strip()

    for pattern in youtube_patterns:
        match = re.match(pattern, text, flags=re.IGNORECASE)
        if match:
            return "YOUTUBE_SEARCH", match.group(1).strip(" \t.,!?")

    return None, None





# ==================================================

# WEB SEARCH

# ==================================================



def perform_web_search(user_message: str):



    search_query = extract_search_query(

        user_message

    )



    if not search_query:

        search_query = user_message



    print()

    print("========================================")

    print("WEB SEARCH QUERY:", search_query)

    print("========================================")



    # ==================================================

    # SEARCH

    # ==================================================



    results = web_search(

        search_query,

        5

    )



    if not results:



        return {

            "answer":

                "Sorry, I couldn't find any web results.",



            "results": []

        }



    # ==================================================

    # BUILD CONTEXT

    # ==================================================



    search_context = ""



    for index, result in enumerate(

        results,

        start=1

    ):



        search_context += f"""



RESULT {index}



TITLE:

{result.get("title", "")}



URL:

{result.get("url", "")}



DESCRIPTION:

{result.get("description", "")}



"""



    # ==================================================

    # ASK QWEN

    # ==================================================



    prompt = f"""

You are Nexa, a personal AI assistant.



The user asked:



{user_message}



Use the web search results below to answer.



WEB RESULTS:

{search_context}



Rules:



1. Answer the user's actual question.

2. Use information from the search results.

3. Do not invent facts.

4. If information is uncertain, say so.

5. For current questions, mention that the information

   comes from current web search results.

6. Keep the answer concise.

7. Do not list URLs in your answer.

8. Do not use internal reasoning.



Give only the final answer.

"""



    try:



        response = requests.post(

            "http://127.0.0.1:11434/api/chat",



            json={

                "model": "qwen3:1.7b",



                "messages": [

                    {

                        "role": "user",

                        "content": prompt

                    }

                ],



                "stream": False,

                "think": False,



                "options": {

                    "temperature": 0.3,

                    "num_predict": 200

                }

            },



            timeout=180

        )



        response.raise_for_status()



        data = response.json()



        answer = data["message"]["content"].strip()



        answer = re.sub(

            r"<think>.*?</think>",

            "",

            answer,

            flags=re.DOTALL

        ).strip()



        if not answer:

            answer = "I found some web results for you."



        return {

            "answer": answer,

            "results": results[:5]

        }



    except Exception as error:



        print(

            "WEB ANSWER ERROR:",

            error

        )



        return {

            "answer":

                "I found these web results for you.",



            "results":

                results[:5]

        }





# ==================================================

# CHAT ENDPOINT

# ==================================================



@app.post("/api/chat")

def chat(request: ChatRequest):



    user_message = request.message.strip()



    if not user_message:



        return {

            "response":

                "Please tell me what you want me to do.",



            "web_results": []

        }



    print()

    print("========================================")

    print("USER:", user_message)
    response_language = detect_response_language(user_message)
    print("DETECTED RESPONSE LANGUAGE:", response_language)

    print("========================================")


    
    normalized_message = user_message.strip().lower()

    # Direct Kannada intent overrides
    intent = None

    if any(phrase in normalized_message for phrase in [
        "ಧ್ವನಿಯನ್ನು ಅನ್‌ಮ್ಯೂಟ್",
        "ಧ್ವನಿಯ ಮ್ಯೂಟ್ ತೆಗೆದುಹಾಕಿ",
        "ಮ್ಯೂಟ್ ತೆಗೆದುಹಾಕಿ",
        "ಅನ್‌ಮ್ಯೂಟ್ ಮಾಡಿ",
    ]):
        intent = "UNMUTE_VOLUME"

    elif any(phrase in normalized_message for phrase in [
        "ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡಿ",
        "ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡು",
        "ವಾಲ್ಯೂಮ್ ಮ್ಯೂಟ್ ಮಾಡಿ",
    ]):
        intent = "MUTE_VOLUME"

    
    elif (
        any(word in normalized_message for word in [
            "ಹೊಳಪ",
            "ಬ್ರೈಟ್ನೆಸ್",
            "brightness",
        ])
        and any(word in normalized_message for word in [
            "ಹೆಚ್ಚ",
            "ಜಾಸ್ತಿ",
            "ಏರಿಸ",
            "increase",
            "brighter",
            "up",
        ])
    ):
        intent = "BRIGHTNESS_UP"
        print("KANNADA BRIGHTNESS OVERRIDE:", repr(normalized_message), intent)

    elif (
        any(word in normalized_message for word in [
            "ಹೊಳಪ",
            "ಬ್ರೈಟ್ನೆಸ್",
            "brightness",
        ])
        and any(word in normalized_message for word in [
            "ಕಡಿಮೆ",
            "ಇಳಿಸ",
            "ತಗ್ಗಿಸ",
            "decrease",
            "darker",
            "down",
        ])
    ):
        intent = "BRIGHTNESS_DOWN"
        print("KANNADA BRIGHTNESS OVERRIDE:", repr(normalized_message), intent)


    elif normalized_message in [
        "ಡೌನ್‌ಲೋಡ್ಸ್ ತೆರೆಯಿರಿ",
        "ಡೌನ್‌ಲೋಡ್ಸ್ ಓಪನ್ ಮಾಡಿ",
    ]:
        intent = "OPEN_DOWNLOADS"

    # STEP 1: Direct Windows command
    if intent:
        command_response = execute_ai_intent(intent)
    else:
        command_response = execute_command(user_message)

    if command_response:
        if response_language == "Kannada":
            kannada_confirmations = {
                "UNMUTE_VOLUME": "ಧ್ವನಿಯ ಮ್ಯೂಟ್ ತೆಗೆದುಹಾಕಲಾಗಿದೆ.",
                "MUTE_VOLUME": "ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡಲಾಗಿದೆ.",
                "BRIGHTNESS_UP": "ಪರದೆಯ ಹೊಳಪನ್ನು ಹೆಚ್ಚಿಸಲಾಗುತ್ತಿದೆ.",
                "BRIGHTNESS_DOWN": "ಪರದೆಯ ಹೊಳಪನ್ನು ಕಡಿಮೆ ಮಾಡಲಾಗುತ್ತಿದೆ.",
                "OPEN_DOWNLOADS": "ಡೌನ್‌ಲೋಡ್ಸ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            }

            if intent in kannada_confirmations:
                command_response = kannada_confirmations[intent]

        print("DIRECT COMMAND:", command_response)

        return {
            "response": command_response,
            "web_results": []
        }




    # ==================================================

    # STEP 2

    # UNDERSTAND USER

    # ==================================================



  
    intent = understand_command(user_message)

    if any(phrase in normalized_message for phrase in [
        "ಧ್ವನಿಯನ್ನು ಅನ್‌ಮ್ಯೂಟ್",
        "ಧ್ವನಿಯ ಮ್ಯೂಟ್ ತೆಗೆದುಹಾಕಿ",
        "ಮ್ಯೂಟ್ ತೆಗೆದುಹಾಕಿ",
        "ಅನ್‌ಮ್ಯೂಟ್ ಮಾಡಿ",
    ]):
        intent = "UNMUTE_VOLUME"

    elif any(phrase in normalized_message for phrase in [
        "ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡಿ",
        "ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡು",
        "ವಾಲ್ಯೂಮ್ ಮ್ಯೂಟ್ ಮಾಡಿ",
    ]):
        intent = "MUTE_VOLUME"


    # ==================================================

       # ==================================================
    # SPECIAL SEARCHES
    # ==================================================

    special_intent, search_query = extract_special_search_query(
        user_message
    )

    if special_intent:
        print("SPECIAL SEARCH:", special_intent)
        print("SEARCH QUERY:", search_query)

        import webbrowser
        from urllib.parse import quote_plus

        if special_intent == "GOOGLE_SEARCH":
            url = (
                "https://www.google.com/search?q="
                + quote_plus(search_query)
            )
            webbrowser.open(url)

            confirmation = (
                f"ಗೂಗಲ್‌ನಲ್ಲಿ {search_query} ಹುಡುಕಲಾಗುತ್ತಿದೆ."
                if response_language == "Kannada"
                else f"Searching Google for {search_query}."
            )

            return {
                "response": confirmation,
                "web_results": []
            }

        elif special_intent == "YOUTUBE_SEARCH":
            url = (
                "https://www.youtube.com/results?search_query="
                + quote_plus(search_query)
            )
            webbrowser.open(url)

            confirmation = (
                f"ಯೂಟ್ಯೂಬ್‌ನಲ್ಲಿ {search_query} ಹುಡುಕಲಾಗುತ್ತಿದೆ."
                if response_language == "Kannada"
                else f"Searching YouTube for {search_query}."
            )

            return {
                "response": confirmation,
                "web_results": []
            }
    # ==================================================

    # STEP 3

    # WEB SEARCH

    # ==================================================



    if intent == "WEB_SEARCH":



        search_data = perform_web_search(

            user_message

        )



        print(

            "WEB SEARCH ANSWER:",

            search_data["answer"]

        )



        return {

            "response":

                search_data["answer"],



            "web_results":

                search_data["results"]

        }



    # ==================================================

    # STEP 4

    # WINDOWS COMMAND

    # ==================================================



    ai_command_response = execute_ai_intent(

        intent

    )
    

    if response_language == "Kannada":
        kannada_confirmations = {
            "OPEN_CHROME": "ಕ್ರೋಮ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_VSCODE": "ವಿಷುವಲ್ ಸ್ಟುಡಿಯೋ ಕೋಡ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_CALCULATOR": "ಕ್ಯಾಲ್ಕುಲೇಟರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_NOTEPAD": "ನೋಟ್‌ಪ್ಯಾಡ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_EXPLORER": "ಫೈಲ್ ಎಕ್ಸ್‌ಪ್ಲೋರರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_YOUTUBE": "ಯೂಟ್ಯೂಬ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_GOOGLE": "ಗೂಗಲ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_DOWNLOADS": "ಡೌನ್‌ಲೋಡ್ಸ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_DESKTOP": "ಡೆಸ್ಕ್‌ಟಾಪ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_DOCUMENTS": "ಡಾಕ್ಯುಮೆಂಟ್ಸ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_PICTURES": "ಚಿತ್ರಗಳ ಫೋಲ್ಡರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_VIDEOS": "ವೀಡಿಯೊಗಳ ಫೋಲ್ಡರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_MUSIC": "ಸಂಗೀತದ ಫೋಲ್ಡರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_SETTINGS": "ಸೆಟ್ಟಿಂಗ್ಸ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "OPEN_TASK_MANAGER": "ಟಾಸ್ಕ್ ಮ್ಯಾನೇಜರ್ ತೆರೆಯಲಾಗುತ್ತಿದೆ.",
            "VOLUME_UP": "ಧ್ವನಿಯನ್ನು ಹೆಚ್ಚಿಸಲಾಗುತ್ತಿದೆ.",
            "VOLUME_DOWN": "ಧ್ವನಿಯನ್ನು ಕಡಿಮೆ ಮಾಡಲಾಗುತ್ತಿದೆ.",
            "MUTE_VOLUME": "ಧ್ವನಿಯನ್ನು ಮ್ಯೂಟ್ ಮಾಡಲಾಗುತ್ತಿದೆ.",
            "UNMUTE_VOLUME": "ಧ್ವನಿಯ ಮ್ಯೂಟ್ ತೆಗೆದುಹಾಕಲಾಗುತ್ತಿದೆ.",
            "BRIGHTNESS_UP": "ಪರದೆಯ ಹೊಳಪನ್ನು ಹೆಚ್ಚಿಸಲಾಗುತ್ತಿದೆ.",
            "BRIGHTNESS_DOWN": "ಪರದೆಯ ಹೊಳಪನ್ನು ಕಡಿಮೆ ಮಾಡಲಾಗುತ್ತಿದೆ.",
            "BATTERY_STATUS": "ಬ್ಯಾಟರಿ ಸ್ಥಿತಿಯನ್ನು ಪರಿಶೀಲಿಸಲಾಗುತ್ತಿದೆ.",
            "TAKE_SCREENSHOT": "ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ತೆಗೆದುಕೊಳ್ಳಲಾಗುತ್ತಿದೆ.",
            "LOCK_COMPUTER": "ನಿಮ್ಮ ಕಂಪ್ಯೂಟರ್ ಲಾಕ್ ಮಾಡಲಾಗುತ್ತಿದೆ.",
        }

        if intent == "BATTERY_STATUS":
            match = re.search(
                r"(\\d+)\\s*%?",
                ai_command_response or "",
                re.IGNORECASE
            )
            if match:
                battery_level = match.group(1)
                kannada_numbers = {
                    "0": "ಸೊನ್ನೆ",
                    "1": "ಒಂದು",
                    "2": "ಎರಡು",
                    "3": "ಮೂರು",
                    "4": "ನಾಲ್ಕು",
                    "5": "ಐದು",
                    "6": "ಆರು",
                    "7": "ಏಳು",
                    "8": "ಎಂಟು",
                    "9": "ಒಂಬತ್ತು",
                    "10": "ಹತ್ತು",
                    "20": "ಇಪ್ಪತ್ತು",
                    "30": "ಮೂವತ್ತು",
                    "40": "ನಲವತ್ತು",
                    "50": "ಐವತ್ತು",
                    "60": "ಅರವತ್ತು",
                    "70": "ಎಪ್ಪತ್ತು",
                    "80": "ಎಂಭತ್ತು",
                    "90": "ತೊಂಬತ್ತು",
                    "100": "ನೂರು",
                }
                battery_level = kannada_numbers.get(
                    battery_level, battery_level
                )
                ai_command_response = (
                    f"ನಿಮ್ಮ ಲ್ಯಾಪ್‌ಟಾಪ್ ಬ್ಯಾಟರಿ {battery_level} ಪ್ರತಿಶತ ಇದೆ."
                )
            else:
                ai_command_response = kannada_confirmations[intent]

        elif intent in kannada_confirmations:
            ai_command_response = kannada_confirmations[intent]

    if ai_command_response:
        print("AI COMMAND:", ai_command_response)
        return {
            "response": ai_command_response,
            "web_results": []
        }

# STEP 5

# NORMAL AI CHAT

# ==================================================



    try:
        print("CURRENT MESSAGE BEFORE OLLAMA:", repr(user_message)) 
        print("SYSTEM PROMPT LANGUAGE RULE:", "English message means English answer")
        print("LANGUAGE RULE ACTIVE: English input -> English output")
        response = requests.post(



            "http://127.0.0.1:11434/api/chat",



            json={



                "model":

                    "qwen3:1.7b",



                "messages": [
    {
        "role": "system",
       "content": (
           f"Reply entirely in {response_language}. "
           "Answer the user's question directly; never copy the question as your answer. "
"If the user greets you, greet them back naturally. "
"For 'Hello Nexa, how are you?', reply: 'Hello! I'm doing well, thanks for asking. How can I help you today?' "
    "You are Nexa, a personal Windows laptop assistant. "
    "You MUST reply in the language of the CURRENT user message. "
    "The current user message determines the language. "
    "English message means English answer. "
    "Kannada message means Kannada answer in Kannada script. "
    "Never answer an English message in Kannada. "
    "Never answer a Kannada message in English unless requested. "
    "Ignore the language used in previous conversation turns. "
    "For an English greeting, reply with a short English greeting. "
    "For a Kannada greeting, reply with a short, natural Kannada greeting. "
    "Example Kannada reply: ನಮಸ್ಕಾರ! ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ. ನೀನು ಹೇಗಿದ್ದೀಯ? "
    "Be concise and return only the final answer."
)
    },
    {
        "role": "user",
        "content": user_message
    }
],



                "stream":

                    False,



                "think":

                    False,



                "options": {



                    "temperature":

                        0.2,



                    "num_predict":

                        150

                }

            },



            timeout=180

        )



        response.raise_for_status()



        data = response.json()



        ai_response = data[

            "message"

        ][

            "content"

        ].strip()
        print("AI RESPONSE GENERATED:", repr(ai_response))



        # Clean Qwen reasoning from the final response.
        # Qwen may return reasoning inside <think>...</think>
        # or expose it separately in the `thinking` field.
        message_data = data.get("message", {})

        if message_data.get("thinking") and not ai_response:
            ai_response = message_data.get("content", "").strip()

        if "</think>" in ai_response:
            ai_response = ai_response.split("</think>", 1)[1].strip()
        elif "<think>" in ai_response:
            ai_response = re.sub(
                r"<think>.*?</think>",
                "",
                ai_response,
                flags=re.DOTALL
            ).strip()

        ai_response = re.sub(
            r"<think>.*?</think>",
            "",
            ai_response,
            flags=re.DOTALL
        ).strip()

        if not ai_response:
            ai_response = "Sorry, I couldn't generate a response."

        return {



            "response":

                ai_response,



            "web_results": []

        }



    except requests.exceptions.RequestException as error:



        print(

            "OLLAMA ERROR:",

            repr(error)

        )



        raise HTTPException(



            status_code=500,



            detail=

                f"Ollama connection error: {repr(error)}"

        )



    except Exception as error:



        print(

            "NEXA ERROR:",

            repr(error)

        )



        raise HTTPException(



            status_code=500,



            detail=

                f"Nexa could not get an AI response: {repr(error)}"

        )