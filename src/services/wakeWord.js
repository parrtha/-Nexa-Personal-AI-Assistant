
let recognition = null;

let enabled = false;
let waitingForCommand = false;
let processingCommand = false;

let onCommandCallback = null;
let restartTimer = null;

const currentLanguage = "en-IN";

// ==================================================
// NORMALIZE SPEECH
// ==================================================

function normalizeSpeechText(text = "") {
  return String(text)
    .normalize("NFC")
    .toLowerCase()
    .replace(/[^\p{L}\p{M}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function compactText(text = "") {
  return normalizeSpeechText(text).replace(/\s+/g, "");
}

// ==================================================
// ENGLISH WAKE WORD ALIASES
// ==================================================

const englishWakeWords = [
  "hey nexa",
  "henexa",
  "hennyxa",
  "heynexa",
  "hey nex a",
  "hey nex",
  "hey next",
  "hello nexa",
  "hello nex",
  "okay nexa",
  "ok nexa",
  "nexa"
];

// ==================================================
// FIND WAKE WORD
// ==================================================

function findWakeWord(text) {
  const normalized = normalizeSpeechText(text);
  const compact = compactText(normalized);

  const aliases = [...englishWakeWords].sort(
    (a, b) => compactText(b).length - compactText(a).length
  );

  for (const alias of aliases) {
    const aliasCompact = compactText(alias);

    if (
      compact === aliasCompact ||
      compact.startsWith(aliasCompact)
    ) {
      return {
        wakeWord: alias,
        compactWakeWord: aliasCompact
      };
    }
  }

  console.log("No English wake alias matched:", normalized);

  return null;
}

// ==================================================
// EXTRACT COMMAND
// ==================================================

function extractCommand(text, compactWakeWord) {
  const characters = Array.from(text);

  let matchedCharacters = 0;
  let index = 0;

  const requiredCharacters = Array.from(
    compactWakeWord
  ).length;

  while (
    index < characters.length &&
    matchedCharacters < requiredCharacters
  ) {
    if (!/\s/u.test(characters[index])) {
      matchedCharacters++;
    }

    index++;
  }

  return characters.slice(index).join("").trim();
}

// ==================================================
// CREATE RECOGNITION
// ==================================================

function createRecognition(SpeechRecognition) {
  const recognizer = new SpeechRecognition();

  recognizer.lang = currentLanguage;
  recognizer.continuous = true;
  recognizer.interimResults = false;
  recognizer.maxAlternatives = 5;

  recognizer.onstart = () => {
    console.log("Nexa English wake listener started.");
    console.log('Say "Hey Nexa".');
  };

  // ==================================================
  // SPEECH RESULTS
  // ==================================================

  recognizer.onresult = async (event) => {
    for (
      let i = event.resultIndex;
      i < event.results.length;
      i++
    ) {
      const result = event.results[i];

      if (!result.isFinal) continue;

      const alternatives = Array.from(result).map(
        item => item.transcript
      );

      console.log("Speech alternatives:", alternatives);

      let detectedText = "";
      let matchedWake = null;

      for (const transcript of alternatives) {
        const normalized = normalizeSpeechText(transcript);

        if (!normalized) continue;

        console.log("Checking alternative:", normalized);

        const match = findWakeWord(normalized);

        if (match) {
          detectedText = normalized;
          matchedWake = match;
          break;
        }

        if (!detectedText) {
          detectedText = normalized;
        }
      }

      if (!detectedText) continue;

      console.log("Nexa heard:", detectedText);

      // ==================================================
      // WAKE WORD DETECTED
      // ==================================================

      if (matchedWake) {
        console.log(
          "WAKE WORD DETECTED:",
          matchedWake.wakeWord
        );

        let command = extractCommand(
          detectedText,
          matchedWake.compactWakeWord
        );

        command = command
          .replace(/^open from\s+/i, "")
          .replace(/^and\s+/i, "")
          .replace(/^then\s+/i, "")
          .trim();

        if (command) {
          console.log("Command in same sentence:", command);

          waitingForCommand = false;

          await sendCommand(command);
        } else {
          waitingForCommand = true;

          console.log("Waiting for your command...");
        }

        continue;
      }

      // ==================================================
      // COMMAND AFTER WAKE WORD
      // ==================================================

      if (waitingForCommand) {
        waitingForCommand = false;

        console.log("Command received:", detectedText);

        await sendCommand(detectedText);
      }
    }
  };

  // ==================================================
  // ERROR HANDLING
  // ==================================================

  recognizer.onerror = (event) => {
    console.error("Wake recognition error:", event.error);

    if (
      event.error === "no-speech" ||
      event.error === "aborted"
    ) {
      return;
    }

    if (
      event.error === "audio-capture" ||
      event.error === "not-allowed" ||
      event.error === "service-not-allowed"
    ) {
      enabled = false;
      waitingForCommand = false;

      if (recognition === recognizer) {
        recognition = null;
      }

      if (restartTimer) {
        clearTimeout(restartTimer);
        restartTimer = null;
      }

      console.error(
        "Microphone unavailable or permission denied."
      );
    }
  };

  // ==================================================
  // RECOGNITION END
  // ==================================================

  recognizer.onend = () => {
    console.log("Wake listener ended.");

    if (recognition === recognizer) {
      recognition = null;
    }

    if (!enabled || processingCommand) {
      return;
    }

    scheduleRestart();
  };

  return recognizer;
}

// ==================================================
// SEND COMMAND
// ==================================================

async function sendCommand(command) {
  if (processingCommand) return;

  processingCommand = true;

  const oldRecognition = recognition;
  recognition = null;

  if (oldRecognition) {
    try {
      oldRecognition.onend = null;
      oldRecognition.stop();
    } catch (error) {
      console.log("Wake listener stop:", error.message);
    }
  }

  await new Promise(resolve => setTimeout(resolve, 400));

  try {
    if (onCommandCallback) {
      await onCommandCallback(command);
    }
  } catch (error) {
    console.error("Wake command error:", error);
  } finally {
    await new Promise(resolve => setTimeout(resolve, 1000));

    processingCommand = false;

    if (enabled) {
      startRecognition();
    }
  }
}

// ==================================================
// AUTOMATIC RESTART
// ==================================================

function scheduleRestart() {
  if (!enabled || processingCommand) return;

  if (restartTimer) {
    clearTimeout(restartTimer);
  }

  restartTimer = setTimeout(() => {
    restartTimer = null;
    startRecognition();
  }, 1000);
}

// ==================================================
// START RECOGNITION
// ==================================================

function startRecognition() {
  if (
    !enabled ||
    processingCommand ||
    recognition
  ) {
    return;
  }

  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.error("Speech Recognition is not supported.");
    enabled = false;
    return;
  }

  const newRecognition = createRecognition(SpeechRecognition);

  recognition = newRecognition;

  try {
    newRecognition.start();
  } catch (error) {
    console.error("Wake listener start error:", error.message);

    if (recognition === newRecognition) {
      recognition = null;
    }

    scheduleRestart();
  }
}

// ==================================================
// START WAKE WORD
// ==================================================

export function startWakeWord(onCommand, language = "en-IN") {
  const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.error("Speech Recognition is not supported.");
    return false;
  }

  onCommandCallback = onCommand;

  enabled = true;
  waitingForCommand = false;
  processingCommand = false;

  console.log("Starting English-only Nexa wake word.");
  console.log("Wake language: en-IN");

  startRecognition();

  return true;
}

// ==================================================
// STOP WAKE WORD
// ==================================================

export function stopWakeWord() {
  enabled = false;
  waitingForCommand = false;
  processingCommand = false;
  onCommandCallback = null;

  if (restartTimer) {
    clearTimeout(restartTimer);
    restartTimer = null;
  }

  const oldRecognition = recognition;
  recognition = null;

  if (oldRecognition) {
    try {
      oldRecognition.onend = null;
      oldRecognition.stop();
    } catch (error) {
      console.log("Wake listener stop:", error.message);
    }
  }

  console.log("Nexa wake listener stopped.");
}

// ==================================================
// STATUS
// ==================================================

export function isWakeWordRunning() {
  return enabled;
}
