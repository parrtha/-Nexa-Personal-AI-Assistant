
import os
from pathlib import Path
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")

if not api_key:
    raise RuntimeError("SARVAM_API_KEY is missing from backend/.env")

client = SarvamAI(api_subscription_key=api_key)

response = client.text_to_speech.convert(
    text="ನಮಸ್ಕಾರ, ನಾನು ನೆಕ್ಸಾ. ನಿಮಗೆ ಏನು ಸಹಾಯ ಬೇಕು?",
    language_code="kn-IN",
    speaker="ishita",
    model="bulbul:v3",
    output_audio_codec="wav",
)

output_path = Path("sarvam_kannada_test.wav")
response_path = getattr(response, "audios", None)

if response_path:
    import base64
    output_path.write_bytes(base64.b64decode(response_path[0]))
    print(f"Audio saved to: {output_path.resolve()}")
else:
    print("No audio returned. Response:", response)
