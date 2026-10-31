import { useEffect, useState } from "react";
import "./App.css";

import { startListening } from "./services/speech";
import { speak } from "./services/tts";
import { askNexa } from "./services/ai";

import {
  startWakeWord,
  stopWakeWord,
} from "./services/wakeWord";


function App() {

  // ==================================================
  // STATE
  // ==================================================

  const [listening, setListening] = useState(false);

  const [thinking, setThinking] = useState(false);

  const [input, setInput] = useState("");

  const [messages, setMessages] = useState([]);


  // ==================================================
  // WAKE WORD
  // ==================================================

  const [wakeWordEnabled, setWakeWordEnabled] =
    useState(false);


  // ==================================================
  // LANGUAGE
  // ==================================================

  const [language, setLanguage] =
    useState("en-IN");


  // ==================================================
  // ADD MESSAGE
  // ==================================================

  const addMessage = (
    sender,
    text,
    webResults = []
  ) => {

    setMessages(
      (previousMessages) => [
        ...previousMessages,

        {
          sender,
          text,
          webResults,
        },
      ]
    );
  };


  // ==================================================
  // PROCESS MESSAGE
  // ==================================================

  const processMessage = async (userText) => {

    if (
      !userText.trim() ||
      thinking
    ) {
      return;
    }


    const text =
      userText.trim();


    addMessage(
      "You",
      text
    );


    addMessage(
      "Nexa",
      "Thinking..."
    );


    setThinking(true);


    try {

      const data =
        await askNexa(text);


      setMessages(
        (previousMessages) => {

          const updatedMessages = [
            ...previousMessages
          ];


          updatedMessages[
            updatedMessages.length - 1
          ] = {

            sender: "Nexa",

            text: data.response,

            webResults:
              data.webResults || [],

          };


          return updatedMessages;

        }
      );


      // Speak Nexa response
     // Speak Nexa response, then resume listening
speak(data.response, () => {
  console.log("TTS LANGUAGE:", language);
  if (wakeWordEnabled) {
    console.log("Wake word mode is active.");
    return;
  }

  setThinking(false);

  setTimeout(() => {
    restartListening();
  }, 500);
}, language);

    } catch (error) {

      console.error(
        "Nexa error:",
        error
      );


      setMessages(
        (previousMessages) => {

          const updatedMessages = [
            ...previousMessages
          ];


          updatedMessages[
            updatedMessages.length - 1
          ] = {

            sender: "Nexa",

            text:
              "Sorry, I couldn't connect to my AI brain.",

            webResults: [],

          };


          return updatedMessages;

        }
      );

    }  finally {
  setThinking(false);
  console.log("Nexa finished processing the response.");
}

  };


  // ==================================================
  // SEND MESSAGE
  // ==================================================

  const sendMessage = async () => {

    if (
      !input.trim() ||
      thinking
    ) {
      return;
    }


    const userText =
      input.trim();


    setInput("");


    await processMessage(
      userText
    );

  };


  // ==================================================
  // VOICE RESULT
  // ==================================================

  const handleVoiceResult =
    async (recognizedText) => {

      setListening(false);


      if (
        !recognizedText.trim()
      ) {
        return;
      }


      await processMessage(
        recognizedText
      );

    };


  // ==================================================
  // VOICE ERROR
  // ==================================================

  const handleVoiceError =
    (error) => {

      console.error(
        "Voice error:",
        error
      );


      setListening(false);


      addMessage(
        "Nexa",
        "Sorry, I couldn't hear you. Please try again."
      );

    };


  // ==================================================
  // VOICE END
  // ==================================================

 
  
const handleVoiceEnd = () => {
  setListening(false);
  console.log("Command recognition ended.");
};

  
const restartListening = () => {
  if (wakeWordEnabled || listening) {
    return;
  }

  console.log("Restarting microphone listening...");

  setListening(true);

  startListening(
    handleVoiceResult,
    handleVoiceError,
    handleVoiceEnd,
    language
  );
};




  // ==================================================
  // MICROPHONE
  // ==================================================

  
const handleMicrophone = () => {
  if (listening || thinking) {
    return;
  }

  // Stop the wake-word listener before manual recognition.
  stopWakeWord();

  setListening(true);

  startListening(
    handleVoiceResult,
    handleVoiceError,
    handleVoiceEnd,
    language
  );
};



  // ==================================================
  // WAKE WORD LISTENER
  // ==================================================

  useEffect(() => {

    if (!wakeWordEnabled) {

      stopWakeWord();

      return;

    }


    console.log(
      "🌐 Nexa language:",
      language
    );


    const started =
      startWakeWord(
        (command) => {

          console.log(
            "🚀 Hey Nexa command:",
            command
          );


          if (
            !command ||
            !command.trim()
          ) {
            return;
          }


          processMessage(
            command
          );

        },
        language
      );


    if (!started) {

      console.log(
        "Wake word is not available."
      );


      setWakeWordEnabled(false);

    }


    return () => {

      stopWakeWord();

    };


  }, [
    wakeWordEnabled,
    language
  ]);


  // ==================================================
  // UI
  // ==================================================

  return (

    <div className="app">
    <button
  onClick={() => {
    const audio = new Audio("/audio/sapna-kannada.mp3");
    audio.play().catch((error) => {
      console.error("Sapna audio playback failed:", error);
    });
  }}
  style={{
    position: "fixed",
    bottom: "20px",
    right: "20px",
    zIndex: 9999,
    padding: "12px 18px",
    borderRadius: "10px",
    background: "#e91e63",
    color: "white",
    border: "none",
    cursor: "pointer"
  }}
>
  Test Sapna Kannada Voice
</button>
      {/* ==================================================
          HEADER
      ================================================== */}

      <header className="header">

        <h1>
          Nexa
        </h1>

        <p>
          Your personal AI assistant
        </p>

      </header>



      <main className="main">


        {/* ==================================================
            ORB
        ================================================== */}

        <div
          className={`orb ${
            listening
              ? "listening"
              : thinking
              ? "thinking"
              : ""
          }`}
        >

          <span>
            N
          </span>

        </div>



        {/* ==================================================
            STATUS
        ================================================== */}

        <div className="status">

          {listening &&
            "Listening..."}

          {!listening &&
            thinking &&
            "Thinking..."}

          {!listening &&
            !thinking &&
            "Ready"}

        </div>



        {/* ==================================================
            LANGUAGE SELECTOR
        ================================================== */}

        <div className="language-control">

          <label htmlFor="language">

            Language

          </label>


          <select
            id="language"
            value={language}
            onChange={(event) =>
              setLanguage(
                event.target.value
              )
            }
          >

            <option value="en-IN">
              English 🇬🇧
            </option>

            <option value="kn-IN">
              ಕನ್ನಡ 🇮🇳
            </option>

          </select>

        </div>



        {/* ==================================================
            CHAT
        ================================================== */}

        <section className="chat">


          {messages.length === 0 && (

            <div className="welcome">

              <h2>
                How can I help?
              </h2>

              <p>

                Click the microphone
                and talk to Nexa.

              </p>

            </div>

          )}



          {messages.map(
            (message, index) => (

              <div
                key={index}
                className={`message ${
                  message.sender === "You"
                    ? "user"
                    : "nexa"
                }`}
              >

                <strong>
                  {message.sender}
                </strong>


                <p>
                  {message.text}
                </p>



                {/* ==================================================
                    WEB RESULTS
                ================================================== */}

                {message.webResults &&
                  message.webResults.length > 0 && (

                    <div className="web-results">

                      <h3>
                        🔎 Web Results
                      </h3>


                      {message.webResults.map(
                        (
                          result,
                          resultIndex
                        ) => (

                          <div
                            className="web-result"
                            key={resultIndex}
                          >

                            <a
                              href={result.url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >

                              {result.title}

                            </a>


                            <p>
                              {result.description}
                            </p>

                          </div>

                        )
                      )}

                    </div>

                  )}

              </div>

            )
          )}

        </section>



        {/* ==================================================
            CONTROLS
        ================================================== */}

        <div className="controls">


          {/* TEXT INPUT */}

          <input
            type="text"

            placeholder={
              language === "kn-IN"
                ? "Nexaಗೆ ಏನು ಕೇಳಬೇಕು?"
                : "Ask Nexa something..."
            }

            value={input}

            disabled={thinking}

            onChange={(event) =>
              setInput(
                event.target.value
              )
            }

            onKeyDown={(event) => {

              if (
                event.key === "Enter"
              ) {

                sendMessage();

              }

            }}

          />



          {/* SEND */}

          <button
            onClick={sendMessage}

            disabled={
              thinking ||
              !input.trim()
            }
          >

            {thinking
              ? "..."
              : "Send"}

          </button>



          {/* MICROPHONE */}

          <button
            className={`mic ${
              listening
                ? "mic-active"
                : ""
            }`}

            onClick={
              handleMicrophone
            }

            disabled={thinking}
          >

            {listening
              ? "🔴"
              : "🎤"}

          </button>



          {/* WAKE WORD */}

          <button
            onClick={() =>
              setWakeWordEnabled(
                (previous) =>
                  !previous
              )
            }
          >

            {wakeWordEnabled
              ? "🟢 Wake Word ON"
              : "⚪ Wake Word OFF"}

          </button>


        </div>


      </main>

    </div>

  );

}


export default App;