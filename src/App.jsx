
import { useEffect, useRef, useState } from "react";
import "./App.css";

import { startListening } from "./services/speech";
import { speak } from "./services/tts";
import { askNexa } from "./services/ai";

import {
  startWakeWord,
  stopWakeWord
} from "./services/wakeWord";

import ChatHistory from "./ChatHistory";
import FileSearch from "./FileSearch";
import SystemMonitor from "./SystemMonitor";
import Reminders from "./Reminders";

const BAR_COUNT = 24;
const STORAGE_KEY = "nexa_conversations";
const ACTIVE_CHAT_KEY = "nexa_active_conversation_id";

// Read saved conversations safely.
const readSavedConversations = () => {
  try {
    const saved = JSON.parse(
      localStorage.getItem(STORAGE_KEY) || "[]"
    );

    return Array.isArray(saved) ? saved : [];
  } catch (error) {
    console.error("Could not load chat history:", error);
    return [];
  }
};

function App() {
  const [listening, setListening] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [input, setInput] = useState("");

  const [wakeWordEnabled, setWakeWordEnabled] = useState(false);
  const [language, setLanguage] = useState("en-IN");
  const [showSettings, setShowSettings] = useState(false);
  const [activePage, setActivePage] = useState("assistant");

  // Chat history state.
  const [conversations, setConversations] = useState(
    readSavedConversations
  );

  const [activeConversationId, setActiveConversationId] = useState(
    () => localStorage.getItem(ACTIVE_CHAT_KEY) || null
  );

  // Restore the last active conversation.
  const [messages, setMessages] = useState(() => {
    const saved = readSavedConversations();
    const activeId = localStorage.getItem(ACTIVE_CHAT_KEY);

    const activeConversation = saved.find(
      (item) => item.id === activeId
    );

    return activeConversation?.messages || [];
  });

  const chatEndRef = useRef(null);
  const processMessageRef = useRef(null);

  // Save conversations in browser storage.
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(conversations)
      );
    } catch (error) {
      console.error("Could not save chat history:", error);
    }
  }, [conversations]);

  // Save active conversation ID.
  useEffect(() => {
    if (activeConversationId) {
      localStorage.setItem(
        ACTIVE_CHAT_KEY,
        activeConversationId
      );
    } else {
      localStorage.removeItem(ACTIVE_CHAT_KEY);
    }
  }, [activeConversationId]);

  // Automatically save messages to the current conversation.
  useEffect(() => {
    const savedMessages = messages.filter(
      (message) => !message.pending
    );

    if (savedMessages.length === 0) {
      return;
    }

    const id = activeConversationId || crypto.randomUUID();

    if (!activeConversationId) {
      setActiveConversationId(id);
    }

    const firstUserMessage = savedMessages.find(
      (message) => message.sender === "You"
    );

    const title =
      firstUserMessage?.text?.slice(0, 55) ||
      "New conversation";

    setConversations((previous) => {
      const existing = previous.find(
        (conversation) => conversation.id === id
      );

      const updatedConversation = {
        id,
        title,
        messages: savedMessages,
        createdAt:
          existing?.createdAt || new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      const otherConversations = previous.filter(
        (conversation) => conversation.id !== id
      );

      return [
        updatedConversation,
        ...otherConversations
      ].slice(0, 100);
    });
  }, [messages, activeConversationId]);

  // Automatically scroll to latest message.
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [messages]);

  // Add a message to chat.
  const addMessage = (sender, text, webResults = []) => {
    setMessages((previous) => [
      ...previous,
      {
        sender,
        text,
        webResults
      }
    ]);
  };

  // Open a saved conversation.
  const openConversation = (id) => {
    const conversation = conversations.find(
      (item) => item.id === id
    );

    if (!conversation) {
      return;
    }

    setActiveConversationId(id);
    setMessages(conversation.messages || []);
    setInput("");
    setActivePage("assistant");
  };

  // Delete a saved conversation.
  const deleteConversation = (id) => {
    setConversations((previous) =>
      previous.filter((item) => item.id !== id)
    );

    if (activeConversationId === id) {
      setActiveConversationId(null);
      setMessages([]);
    }
  };

  // Start a new conversation without deleting old chats.
  const startNewConversation = () => {
    if (thinking) {
      return;
    }

    setMessages([]);
    setActiveConversationId(null);
    setInput("");
    setActivePage("assistant");
  };

  // Clear current conversation.
  const clearConversation = () => {
    if (!thinking) {
      startNewConversation();
    }
  };

  // PROCESS MESSAGE.
  const processMessage = async (userText) => {
    if (!userText?.trim() || thinking) {
      return;
    }

    const text = userText.trim();

    console.log("Nexa processing:", text);

    setMessages((previous) => [
      ...previous,
      {
        sender: "You",
        text,
        webResults: []
      },
      {
        sender: "Nexa",
        text: "Thinking...",
        webResults: [],
        pending: true
      }
    ]);

    setThinking(true);

    try {
      const data = await askNexa(text);

      setMessages((previous) => {
        const updated = [...previous];

        const pendingIndex = updated.findIndex(
          (message) => message.pending
        );

        if (pendingIndex !== -1) {
          updated[pendingIndex] = {
            sender: "Nexa",
            text: data.response,
            webResults: data.webResults || []
          };
        }

        return updated;
      });

      speak(
        data.response,
        () => {
          console.log(
            "TTS completed. Language:",
            language
          );

          if (!wakeWordEnabled) {
            setThinking(false);

            window.setTimeout(() => {
              restartListening();
            }, 500);
          }
        },
        language
      );

    } catch (error) {
      console.error("Nexa error:", error);

      setMessages((previous) => {
        const updated = [...previous];

        const pendingIndex = updated.findIndex(
          (message) => message.pending
        );

        if (pendingIndex !== -1) {
          updated[pendingIndex] = {
            sender: "Nexa",
            text:
              "Sorry, I couldn't connect to my AI brain. Please check the backend and Ollama.",
            webResults: []
          };
        }

        return updated;
      });

    } finally {
      setThinking(false);
    }
  };

  processMessageRef.current = processMessage;

  // Send typed message.
  const sendMessage = async () => {
    if (!input.trim() || thinking) {
      return;
    }

    const text = input.trim();

    setInput("");

    await processMessage(text);
  };

  // Restart microphone listening.
  const restartListening = () => {
    if (wakeWordEnabled || listening || thinking) {
      return;
    }

    setListening(true);

    startListening(
      handleVoiceResult,
      handleVoiceError,
      handleVoiceEnd,
      language
    );
  };

  // Manual microphone result.
  const handleVoiceResult = async (recognizedText) => {
    setListening(false);

    if (recognizedText?.trim()) {
      await processMessage(recognizedText);
    }
  };

  // Microphone error.
  const handleVoiceError = (error) => {
    console.error("Voice error:", error);

    setListening(false);

    addMessage(
      "Nexa",
      "Sorry, I couldn't hear you. Please try again."
    );
  };

  // Microphone ended.
  const handleVoiceEnd = () => {
    setListening(false);

    console.log("Command recognition ended.");
  };

  // Manual microphone button.
  const handleMicrophone = () => {
    if (listening || thinking) {
      return;
    }

    stopWakeWord();

    if (wakeWordEnabled) {
      setWakeWordEnabled(false);
    }

    setListening(true);

    startListening(
      handleVoiceResult,
      handleVoiceError,
      handleVoiceEnd,
      language
    );
  };

  // HEY NEXA WAKE WORD INTEGRATION.
  useEffect(() => {
    if (!wakeWordEnabled) {
      stopWakeWord();
      return undefined;
    }

    console.log(
      "Nexa selected language:",
      language
    );

    const started = startWakeWord(
      async (command) => {
        console.log(
          "Hey Nexa command received:",
          command
        );

        if (!command?.trim()) {
          return;
        }

        return processMessageRef.current(command);
      },
      language
    );

    if (!started) {
      console.error("Wake word is not available.");
      setWakeWordEnabled(false);
    }

    return () => {
      console.log("Stopping previous wake-word listener.");
      stopWakeWord();
    };
  }, [wakeWordEnabled, language]);

  // Status.
  const status = listening
    ? "Listening to you"
    : thinking
      ? "Nexa is thinking"
      : wakeWordEnabled
        ? "Wake word is active"
        : "Ready when you are";

  // PAGE UI.
  return (
    <div className="nexa-shell">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <button
          className="brand"
          onClick={() => {
            setActivePage("assistant");
            clearConversation();
          }}
          aria-label="Nexa home"
        >
          <span className="brand-mark">N</span>

          <span className="brand-copy">
            <strong>NEXA</strong>
            <small>PERSONAL AI</small>
          </span>
        </button>

        <button
          className="new-chat-button"
          onClick={startNewConversation}
          disabled={thinking}
        >
          <span>＋</span> New conversation
        </button>

        <div className="sidebar-section-label">
          YOUR ASSISTANT
        </div>

        {/* AI ASSISTANT */}

        <button
          className={`sidebar-feature ${
            activePage === "assistant" ? "active" : ""
          }`}
          onClick={() => setActivePage("assistant")}
        >
          <span className="nav-icon">✧</span>
          <span>AI Assistant</span>

          {activePage === "assistant" && (
            <span className="active-indicator" />
          )}
        </button>

        {/* SYSTEM MONITOR */}

        <button
          className={`sidebar-feature ${
            activePage === "system" ? "active" : ""
          }`}
          onClick={() => setActivePage("system")}
        >
          <span className="nav-icon">◉</span>
          <span>System Monitor</span>

          {activePage === "system" && (
            <span className="active-indicator" />
          )}
        </button>

        {/* REMINDERS */}

        <button
          className={`sidebar-feature ${
            activePage === "reminders" ? "active" : ""
          }`}
          onClick={() => setActivePage("reminders")}
        >
          <span className="nav-icon">◷</span>
          <span>Reminders</span>

          {activePage === "reminders" && (
            <span className="active-indicator" />
          )}
        </button>

        {/* CHAT HISTORY */}

        <button
          className={`sidebar-feature ${
            activePage === "history" ? "active" : ""
          }`}
          onClick={() => setActivePage("history")}
        >
          <span className="nav-icon">◴</span>
          <span>Chat History</span>

          {activePage === "history" && (
            <span className="active-indicator" />
          )}
        </button>

        {/* FILE SEARCH */}

        <button
          className={`sidebar-feature ${
            activePage === "files" ? "active" : ""
          }`}
          onClick={() => setActivePage("files")}
        >
          <span className="nav-icon">⌕</span>
          <span>File Search</span>

          {activePage === "files" && (
            <span className="active-indicator" />
          )}
        </button>

        <div className="sidebar-feature">
          <span className="nav-icon">◌</span>
          <span>Voice interface</span>
        </div>

        <div className="sidebar-spacer" />

        <div className="local-card">
          <span className="local-status-dot" />

          <div>
            <strong>Running locally</strong>
            <small>Private on this device</small>
          </div>
        </div>

        <button
          className={`sidebar-settings ${
            showSettings ? "selected" : ""
          }`}
          onClick={() =>
            setShowSettings((value) => !value)
          }
        >
          <span>⚙</span> Settings
        </button>

        <div className="sidebar-footer">
          NEXA DESKTOP · PERSONAL EDITION
        </div>

      </aside>

      {/* MAIN PANEL */}

      <main className="main-panel">

        {/* TOPBAR */}

        <header className="topbar">

          <div className="topbar-title">

            <span className="mobile-brand-mark">
              N
            </span>

            <div>
              <strong>
                {activePage === "system"
                  ? "System Monitor"
                  : activePage === "files"
                    ? "File Search"
                    : activePage === "reminders"
                      ? "Reminders"
                      : activePage === "history"
                        ? "Chat History"
                        : "AI Assistant"}
              </strong>

              <small>
                {activePage === "system"
                  ? "Live computer performance"
                  : activePage === "files"
                    ? "Find files on your computer"
                    : activePage === "reminders"
                      ? "Manage your reminders"
                      : activePage === "history"
                        ? "Your saved conversations"
                        : "Your personal space"}
              </small>
            </div>

          </div>

          <div className="topbar-actions">

            <span className="connection-pill">
              <i /> Local AI
            </span>

            {activePage === "assistant" && (
              <button
                className={`wake-toggle ${
                  wakeWordEnabled ? "enabled" : ""
                }`}
                onClick={() =>
                  setWakeWordEnabled((value) => !value)
                }
                aria-pressed={wakeWordEnabled}
              >
                <span className="toggle-dot" />

                Hey Nexa {wakeWordEnabled ? "On" : "Off"}
              </button>
            )}

          </div>

        </header>

        {/* SETTINGS */}

        {showSettings && (
          <section className="settings-panel">

            <div>
              <strong>Voice language</strong>

              <p>
                Choose the language used for speech
                recognition and voice.
              </p>
            </div>

            <select
              value={language}
              onChange={(event) =>
                setLanguage(event.target.value)
              }
              aria-label="Voice language"
            >
              <option value="en-IN">
                English (India)
              </option>

              <option value="kn-IN">
                ಕನ್ನಡ (Kannada)
              </option>
            </select>

          </section>
        )}

        {/* PAGE CONTENT */}

        {activePage === "system" ? (

          <SystemMonitor />

        ) : activePage === "files" ? (

          <FileSearch />

        ) : activePage === "reminders" ? (

          <Reminders />

        ) : activePage === "history" ? (

          <ChatHistory
            conversations={conversations}
            onOpen={openConversation}
            onDelete={deleteConversation}
            onNewChat={startNewConversation}
          />

        ) : (

          <section className="workspace">

            {/* ASSISTANT STAGE */}

            <section className="assistant-stage">

              <div
                className={`orb-wrap ${
                  listening ? "is-listening" : ""
                } ${
                  thinking ? "is-thinking" : ""
                }`}
                aria-label={status}
              >
                <div className="orb-ring ring-one" />
                <div className="orb-ring ring-two" />

                <div className="orb-core">
                  <span>N</span>
                </div>

                <span className="orb-spark spark-one" />
                <span className="orb-spark spark-two" />

              </div>

              <div className="assistant-greeting">

                <span className="eyebrow">
                  YOUR PERSONAL AI ASSISTANT
                </span>

                <h1>
                  {messages.length
                    ? "I'm here with you."
                    : "Hello, I'm Nexa."}
                </h1>

                <p>
                  {messages.length
                    ? status
                    : "Ask me anything, or tell me what you'd like to get done."}
                </p>

              </div>

              <div
                className={`voice-bars ${
                  listening || thinking ? "active" : ""
                }`}
                aria-hidden="true"
              >
                {Array.from(
                  { length: BAR_COUNT },
                  (_, index) => (
                    <span
                      key={index}
                      style={{ "--bar": index }}
                    />
                  )
                )}
              </div>

              <div className="state-label">

                <span
                  className={`state-dot ${
                    listening
                      ? "blue"
                      : thinking
                        ? "purple"
                        : wakeWordEnabled
                          ? "green"
                          : ""
                  }`}
                />

                {status}

              </div>

            </section>

            {/* CONVERSATION PANEL */}

            <section className="conversation-panel">

              <div className="conversation-heading">

                <div>
                  <span className="eyebrow">
                    CONVERSATION
                  </span>

                  <h2>Chat with Nexa</h2>
                </div>

                {messages.length > 0 && (
                  <button
                    className="clear-button"
                    onClick={clearConversation}
                    disabled={thinking}
                  >
                    Clear chat
                  </button>
                )}

              </div>

              {/* MESSAGES */}

              <div
                className="messages-area"
                aria-live="polite"
              >

                {messages.length === 0 ? (

                  <div className="empty-state">

                    <div className="empty-icon">
                      ✧
                    </div>

                    <strong>
                      Where should we start?
                    </strong>

                    <p>
                      Choose a suggestion or type your
                      own request below.
                    </p>

                    <div className="suggestion-grid">

                      {[
                        [
                          "⌕",
                          "Search the web",
                          "Search for the latest AI news"
                        ],
                        [
                          "▣",
                          "Open an app",
                          "Open Calculator"
                        ],
                        [
                          "✧",
                          "Ask a question",
                          "Explain machine learning simply"
                        ]
                      ].map(([icon, title, prompt]) => (

                        <button
                          key={title}
                          className="suggestion-card"
                          onClick={() => setInput(prompt)}
                        >
                          <span>{icon}</span>
                          <strong>{title}</strong>
                          <small>{prompt}</small>
                        </button>

                      ))}

                    </div>

                  </div>

                ) : (

                  messages.map((message, index) => (

                    <article
                      className={`chat-message ${
                        message.sender === "You"
                          ? "from-user"
                          : "from-nexa"
                      }`}
                      key={`${index}-${message.sender}`}
                    >

                      <div className="message-avatar">
                        {message.sender === "You"
                          ? "Y"
                          : "N"}
                      </div>

                      <div className="message-content">

                        <div className="message-author">
                          {message.sender}
                        </div>

                        <p>{message.text}</p>

                        {message.webResults?.length > 0 && (

                          <div className="web-results">

                            <strong>Web results</strong>

                            {message.webResults.map(
                              (result, resultIndex) => (

                                <a
                                  href={result.url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  key={resultIndex}
                                >
                                  <span>{result.title}</span>

                                  <small>
                                    {result.description}
                                  </small>
                                </a>

                              )
                            )}

                          </div>

                        )}

                      </div>

                    </article>

                  ))

                )}

                <div ref={chatEndRef} />

              </div>

              {/* MESSAGE INPUT */}

              <div className="composer">

                <input
                  type="text"
                  value={input}
                  onChange={(event) =>
                    setInput(event.target.value)
                  }
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      sendMessage();
                    }
                  }}
                  placeholder={
                    language === "kn-IN"
                      ? "Nexaಗೆ ಏನು ಕೇಳಬೇಕು?"
                      : "Message Nexa..."
                  }
                  disabled={thinking}
                  aria-label="Message Nexa"
                />

                <button
                  className={`mic-button ${
                    listening ? "recording" : ""
                  }`}
                  onClick={handleMicrophone}
                  disabled={thinking || listening}
                  title="Speak to Nexa"
                  aria-label="Speak to Nexa"
                >
                  {listening ? "■" : "🎙"}
                </button>

                <button
                  className="send-button"
                  onClick={sendMessage}
                  disabled={thinking || !input.trim()}
                  aria-label="Send message"
                >
                  {thinking ? "…" : "↑"}
                </button>

              </div>

              <div className="composer-note">
                <span>🎙 Voice enabled</span>
                <span>Enter to send</span>

                <span>
                  {language === "kn-IN"
                    ? "ಕನ್ನಡ"
                    : "English"}
                </span>
              </div>

            </section>

          </section>

        )}

        {/* FOOTER */}

        <footer className="main-footer">
          <span>Designed for your desktop</span>
          <span>Local-first · Private · Personal</span>
        </footer>

      </main>

    </div>
  );
}

export default App;
