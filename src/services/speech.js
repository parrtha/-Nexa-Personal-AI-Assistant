export function startListening(
  onResult,
  onError,
  onEnd,
  language = "en-IN"
) {
  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    onError("Speech recognition is not supported in this browser.");
    return;
  }

  const recognition = new SpeechRecognition();

  // ==========================================
  // CONFIGURATION
  // ==========================================

  recognition.lang = language;
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  let finished = false;

  // ==========================================
  // START
  // ==========================================

  recognition.onstart = () => {
    console.log("🎤 Speech recognition started:", language);
  };

  // ==========================================
  // RESULT
  // ==========================================

  recognition.onresult = (event) => {
    const transcript =
      event.results?.[0]?.[0]?.transcript?.trim() || "";

    console.log("👂 You said:", transcript);

    if (transcript) {
      finished = true;
      onResult(transcript);
    }
  };

  // ==========================================
  // ERROR
  // ==========================================

  
  
recognition.onerror = (event) => {
  if (event.error === "aborted") {
    console.debug("Speech recognition session stopped.");
    return;
  }

  console.error("Speech recognition error:", event.error);

  if (event.error === "no-speech") {
  console.debug("No speech detected during this listening session.");
  return;
}

  if (
    event.error === "not-allowed" ||
    event.error === "service-not-allowed"
  ) {
    onError(
      "Microphone permission was denied. Please allow microphone access."
    );
    return;
  }

  if (event.error === "audio-capture") {
    onError("Microphone could not be accessed.");
    return;
  }

  onError(event.error);
};



   
  // ==========================================
  // END
  // ==========================================

  recognition.onend = () => {
    console.log("🎤 Speech recognition ended.");

    onEnd();
  };

  // ==========================================
  // START RECOGNITION
  // ==========================================

  try {
    recognition.start();
  } catch (error) {
    console.error(
      "Could not start speech recognition:",
      error
    );

    // Ignore duplicate start errors.
    if (
      !error.message?.toLowerCase().includes("already started")
    ) {
      onError(error.message);
    }
  }

  // ==========================================
  // RETURN CONTROL
  // ==========================================

  return {
    stop: () => {
      if (!finished) {
        try {
          recognition.stop();
        } catch (error) {
          console.log(
            "Speech recognition already stopped."
          );
        }
      }
    },

    abort: () => {
      try {
        recognition.abort();
      } catch (error) {
        console.log(
          "Speech recognition already aborted."
        );
      }
    }
  };
}
