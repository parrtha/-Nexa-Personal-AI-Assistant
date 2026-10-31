from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel



import requests

import json

import re



from commands import execute_command

from web_search import web_search





# ==================================================

# FASTAPI APP

# ==================================================



app = FastAPI()





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



def understand_command(user_message: str):



    prompt = f"""

You are Nexa's command classifier.



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

                "model": "qwen3:4b",



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



            timeout=60

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



        return (

            "Locking your computer "

            "is not enabled yet."

        )



    if intent == "EMPTY_RECYCLE_BIN":



        return (

            "Emptying the Recycle Bin "

            "is not enabled yet."

        )



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



    google_patterns = [

        r"^google\s+(.+)$",

        r"^search google for\s+(.+)$",

        r"^search google\s+(.+)$"

    ]



    youtube_patterns = [

        r"^search youtube for\s+(.+)$",

        r"^search youtube\s+(.+)$",

        r"^find (.+) on youtube$",

        r"^youtube\s+(.+)$"

    ]



    for pattern in google_patterns:



        match = re.match(

            pattern,

            text,

            flags=re.IGNORECASE

        )



        if match:

            return (

                "GOOGLE_SEARCH",

                match.group(1).strip()

            )



    for pattern in youtube_patterns:



        match = re.match(

            pattern,

            text,

            flags=re.IGNORECASE

        )



        if match:

            return (

                "YOUTUBE_SEARCH",

                match.group(1).strip()

            )



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

                "model": "qwen3:4b",



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



            timeout=60

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

    print("========================================")



    # ==================================================

    # STEP 1

    # DIRECT WINDOWS COMMAND

    # ==================================================



    command_response = execute_command(

        user_message

    )



    if command_response:



        print(

            "DIRECT COMMAND:",

            command_response

        )



        return {

            "response":

                command_response,



            "web_results": []

        }



    # ==================================================

    # STEP 2

    # UNDERSTAND USER

    # ==================================================



    intent = understand_command(

        user_message

    )



    # ==================================================

    # SPECIAL SEARCHES

    # ==================================================



    special_intent, search_query = (

        extract_special_search_query(

            user_message

        )

    )



    if special_intent:



        print(

            "SPECIAL SEARCH:",

            special_intent

        )



        print(

            "SEARCH QUERY:",

            search_query

        )



        if special_intent == "GOOGLE_SEARCH":



            import webbrowser

            from urllib.parse import quote_plus



            url = (

                "https://www.google.com/search?q="

                + quote_plus(search_query)

            )



            webbrowser.open(url)



            return {

                "response":

                    f"Searching Google for {search_query}.",



                "web_results": []

            }



        if special_intent == "YOUTUBE_SEARCH":



            import webbrowser

            from urllib.parse import quote_plus



            url = (

                "https://www.youtube.com/results?search_query="

                + quote_plus(search_query)

            )



            webbrowser.open(url)



            return {

                "response":

                    f"Searching YouTube for {search_query}.",



                "web_results": []

            }



    print(

        "AI INTENT:",

        intent

    )



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



    if ai_command_response:



        print(

            "AI COMMAND:",

            ai_command_response

        )



        return {

            "response":

                ai_command_response,



            "web_results": []

        }



    # ==================================================

# STEP 5

# NORMAL AI CHAT

# ==================================================



    try:



        response = requests.post(



            "http://127.0.0.1:11434/api/chat",



            json={



                "model":

                    "qwen3:4b",



                "messages": [



                    {

                        "role":

                            "system",



                        "content":

                            (

                                "You are Nexa, "

                                "a friendly personal "

                                "Windows laptop AI "

                                "assistant. "



                                "Answer clearly "

                                "and naturally. "



                                "Keep responses "

                                "concise unless "

                                "the user asks "

                                "for detail. "



                                "Do not show "

                                "internal reasoning. "



                                "Give only the "

                                "final answer."

                            )

                    },



                    {



                        "role":

                            "user",



                        "content":

                            user_message

                    }

                ],



                "stream":

                    False,



                "think":

                    False,



                "options": {



                    "temperature":

                        0.7,



                    "num_predict":

                        150

                }

            },



            timeout=60

        )



        response.raise_for_status()



        data = response.json()



        ai_response = data[

            "message"

        ][

            "content"

        ].strip()





        # Remove <think>...</think> sections

        ai_response = re.sub(

            r"<think>.*?</think>",

            "",

            ai_response,

            flags=re.DOTALL

        ).strip()



        # If Qwen returns text after </think>,

        # keep only the final answer.

        if "</think>" in ai_response:



            ai_response = (

                ai_response

                .split("</think>", 1)[1]

                .strip()

            )



        if not ai_response:



            ai_response = (

                "Sorry, I couldn't "

                "generate a response."

            )



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