#!/usr/bin/env python3
"""
Gemini 2.5 Flash Native Audio - Live API Test

Real-time voice conversation using the Native Audio model.
Requires: microphone and speakers (use headphones to avoid echo)

Model: gemini-2.5-flash-native-audio-preview-12-2025

Usage:
  python live_audio.py [API_KEY] [VOICE]

  Voices: Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr
"""

import asyncio
import os
import sys
import queue
from pathlib import Path

# Load .env file
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

try:
    import pyaudio
except ImportError:
    print("Error: pyaudio not installed")
    print("Install with: pip install pyaudio")
    print("On Ubuntu/Debian, you may need: sudo apt-get install portaudio19-dev")
    sys.exit(1)

from google import genai
from google.genai import types

# Audio configuration (16-bit PCM, mono)
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"

# Available voices for Live API (source: https://ai.google.dev/gemini-api/docs/live-guide)
VOICES = [
    ("Puck", "Upbeat, energetic"),
    ("Charon", "Informative, clear"),
    ("Kore", "Firm, confident"),
    ("Fenrir", "Excitable, dynamic"),
    ("Aoede", "Breezy, natural"),
    ("Leda", "Youthful, energetic"),
    ("Orus", "Firm, decisive"),
    ("Zephyr", "Bright, cheerful"),
]


def get_api_key():
    """Get API key from args, env, or prompt."""
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        return sys.argv[1]

    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key and api_key != "your-api-key-here":
        return api_key

    print("API Key not found. Get one at: https://aistudio.google.com/apikey")
    return input("Enter API Key: ").strip() or None


def get_voice():
    """Get voice from args or prompt."""
    voice_names = [v[0] for v in VOICES]

    if len(sys.argv) > 2:
        voice = sys.argv[2]
        if voice in voice_names:
            return voice

    print("\nAvailable voices:")
    for i, (name, desc) in enumerate(VOICES, 1):
        print(f"  {i}. {name:10} - {desc}")

    choice = input("\nSelect voice (1-8) or press Enter for Puck: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(VOICES):
        return VOICES[int(choice) - 1][0]
    return "Puck"


async def main():
    api_key = get_api_key()
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)

    voice = get_voice()

    # Initialize client
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})

    # Configure for native audio output
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            )
        ),
    )

    print("=" * 60)
    print("Gemini 2.5 Flash Native Audio - Live Conversation")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Voice: {voice}")
    print("Use headphones to avoid echo!")
    print("Speak into your microphone. Press Ctrl+C to exit.")
    print("-" * 60)

    # Audio queues
    audio_in_queue = queue.Queue()
    audio_out_queue = queue.Queue()

    pya = pyaudio.PyAudio()

    async with client.aio.live.connect(model=MODEL, config=config) as session:
        # Set up audio output stream
        output_stream = pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )

        # Set up audio input stream
        input_stream = pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

        async def send_audio():
            """Continuously send microphone audio to Gemini."""
            while True:
                try:
                    data = input_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    await session.send_realtime_input(
                        audio=types.Blob(data=data, mime_type="audio/pcm")
                    )
                    await asyncio.sleep(0.01)
                except Exception as e:
                    print(f"Send error: {e}")
                    break

        async def receive_audio():
            """Receive and play audio responses from Gemini."""
            while True:
                try:
                    turn = session.receive()
                    async for response in turn:
                        if response.server_content:
                            if response.server_content.model_turn:
                                for part in response.server_content.model_turn.parts:
                                    if part.inline_data:
                                        output_stream.write(part.inline_data.data)
                            if response.server_content.output_transcription:
                                print(f"\nGemini: {response.server_content.output_transcription.text}")
                except Exception as e:
                    print(f"Receive error: {e}")
                    break

        print("\nListening... (speak now)")

        try:
            await asyncio.gather(
                send_audio(),
                receive_audio(),
            )
        except KeyboardInterrupt:
            print("\n\nEnding conversation...")
        finally:
            input_stream.stop_stream()
            input_stream.close()
            output_stream.stop_stream()
            output_stream.close()
            pya.terminate()

    print("Goodbye!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExited.")
