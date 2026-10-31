
const API_BASE_URL = "http://127.0.0.1:8010";

let currentAudio = null;
let currentAudioUrl = null;

export function speak(text, onEnd, language = "en-IN") {
  const containsKannada = /[\u0C80-\u0CFF]/.test(text);

  if (language === "kn-IN" || containsKannada) {
    speakKannada(text, onEnd);
    return;
  }

  if (!("speechSynthesis" in window)) {
    console.error("Text-to-speech is not supported.");
    if (onEnd) onEnd();
    return;
  }

  stopCurrentAudio();
  window.speechSynthesis.cancel();

  const speakNow = () => {
  const voices = window.speechSynthesis.getVoices();

  console.log("TTS TEXT:", text);
  console.log(
    "AVAILABLE ENGLISH VOICES:",
    voices.filter((v) => v.lang.toLowerCase().startsWith("en"))
      .map((v) => ({ name: v.name, lang: v.lang }))
  );

    const voice =
      voices.find((v) => v.lang.toLowerCase() === "en-in") ||
      voices.find((v) => v.lang.toLowerCase().startsWith("en"));

    const utterance = new SpeechSynthesisUtterance(text);

    if (voice) {
      utterance.voice = voice;
      utterance.lang = voice.lang;
    } else {
      utterance.lang = "en-IN";
    }

    utterance.rate = 0.9;
    utterance.pitch = 1.08;
    utterance.volume = 1;

    utterance.onend = () => {
      if (onEnd) onEnd();
    };

    utterance.onerror = (event) => {
  console.error("ENGLISH TTS ERROR:", event.error);
  if (onEnd) onEnd();
};

    window.speechSynthesis.resume();
window.speechSynthesis.speak(utterance);
  };

  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = speakNow;
  } else {
    speakNow();
  }
}

async function speakKannada(text, onEnd) {
  stopCurrentAudio();
  window.speechSynthesis?.cancel();

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/kannada`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`Kannada TTS failed: ${response.status}`);
    }

    const audioBlob = await response.blob();
    currentAudioUrl = URL.createObjectURL(audioBlob);
    currentAudio = new Audio(currentAudioUrl);

    const audioToPlay = currentAudio;

    const finish = () => {
      if (currentAudio === audioToPlay) {
        currentAudio = null;

        if (currentAudioUrl) {
          URL.revokeObjectURL(currentAudioUrl);
          currentAudioUrl = null;
        }

        if (onEnd) onEnd();
      }
    };

    audioToPlay.onended = finish;
    audioToPlay.onerror = () => {
      console.error("Could not play Kannada audio.");
      finish();
    };

    await audioToPlay.play();
  } catch (error) {
    console.error("Kannada speech error:", error);
    if (onEnd) onEnd();
  }
}

function stopCurrentAudio() {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio.onended = null;
    currentAudio.onerror = null;
    currentAudio = null;
  }

  if (currentAudioUrl) {
    URL.revokeObjectURL(currentAudioUrl);
    currentAudioUrl = null;
  }
}
