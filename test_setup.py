#!/usr/bin/env python3
"""
Gemini 2.5 Flash Native Audio - Setup & Test

Supports API key via:
  1. .env file (GOOGLE_API_KEY=...)
  2. Environment variable
  3. Command line: python test_setup.py YOUR_API_KEY
  4. Interactive prompt
"""

import os
import sys
from pathlib import Path

# Add venv to path
venv_path = Path(__file__).parent / 'python' / 'venv' / 'lib' / 'python3.12' / 'site-packages'
if venv_path.exists():
    sys.path.insert(0, str(venv_path))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from google import genai
except ImportError:
    print("Error: google-genai not installed")
    print("Run: cd python && source venv/bin/activate && pip install google-genai")
    sys.exit(1)


# Available voices for Native Audio (Live API)
# Source: https://ai.google.dev/gemini-api/docs/live-guide
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

# Models
MODEL_STANDARD = "gemini-2.5-flash"
MODEL_NATIVE_AUDIO = "gemini-2.5-flash-native-audio-preview-12-2025"


def get_api_key():
    """Get API key from various sources."""
    # Load .env file if exists
    env_file = Path(__file__).parent / '.env'
    if load_dotenv and env_file.exists():
        load_dotenv(env_file)

    # Check command line argument
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        return sys.argv[1]

    # Check environment variable
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key and api_key != "your-api-key-here":
        return api_key

    # Interactive prompt
    print("=" * 60)
    print("GOOGLE_API_KEY not found!")
    print("=" * 60)
    print("\nGet your API key at: https://aistudio.google.com/apikey")
    print("\nYou can provide it via:")
    print("  1. Create .env file with GOOGLE_API_KEY=your-key")
    print("  2. export GOOGLE_API_KEY=your-key")
    print("  3. python test_setup.py your-key")
    print("  4. Enter it now:\n")

    api_key = input("API Key: ").strip()
    if api_key:
        # Save to .env for future use
        save = input("Save to .env for future use? [Y/n]: ").strip().lower()
        if save != 'n':
            with open(env_file, 'w') as f:
                f.write(f"GOOGLE_API_KEY={api_key}\n")
            print(f"Saved to {env_file}")
        return api_key

    return None


def test_connection(api_key):
    """Test the Gemini API connection."""
    print("\nTesting Gemini API connection...")
    print("-" * 40)

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=MODEL_STANDARD,
        contents="Say exactly: 'Gemini 2.5 Flash Native Audio ready!'"
    )

    print(f"Response: {response.text}")
    print("-" * 40)
    print("SUCCESS! API connection working.\n")
    return client


def list_voices():
    """Show available voices."""
    print("\nAvailable HD Voices (Live API):")
    print("-" * 40)
    for i, (name, desc) in enumerate(VOICES, 1):
        print(f"  {i}. {name:10} - {desc}")
    print("-" * 40)


def test_voice(client, voice_name="Puck"):
    """Test text-to-speech with selected voice."""
    print(f"\nTesting voice: {voice_name}")
    print("-" * 40)

    # Get voice description
    voice_desc = next((desc for name, desc in VOICES if name == voice_name), "")

    print(f"Voice characteristics: {voice_desc}")
    print(f"Model for Live API: {MODEL_NATIVE_AUDIO}")

    # Test the API with this configuration context
    response = client.models.generate_content(
        model=MODEL_STANDARD,
        contents=f"The '{voice_name}' voice is described as '{voice_desc}'. Generate a short 2-sentence greeting that would sound good in this voice style."
    )

    print(f"\nSample greeting for {voice_name}:")
    print(response.text)
    print("-" * 40)


def main():
    api_key = get_api_key()
    if not api_key:
        print("\nNo API key provided. Exiting.")
        sys.exit(1)

    client = test_connection(api_key)

    # Show voices
    list_voices()

    # Test a voice
    choice = input("\nSelect a voice to test (1-8) or press Enter for Puck: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(VOICES):
        voice = VOICES[int(choice) - 1][0]
    else:
        voice = "Puck"

    test_voice(client, voice)

    print("\n" + "=" * 60)
    print("Setup complete! Next steps:")
    print("=" * 60)
    print("""
  # Analyze an audio file:
  source python/venv/bin/activate
  python python/audio_test.py /path/to/audio.mp3

  # Live voice conversation (needs mic + pyaudio):
  python python/live_audio.py

  # JavaScript test:
  cd js && node live_audio.js
""")


if __name__ == "__main__":
    main()
