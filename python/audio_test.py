#!/usr/bin/env python3
"""
Gemini 2.5 Flash Audio Understanding Test

Tests basic audio processing capabilities:
- Transcription
- Description
- Analysis
"""

import sys
import os
from pathlib import Path

from google import genai

def main():
    # Check for API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Get your key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Check for audio file argument
    if len(sys.argv) < 2:
        print("Usage: python audio_test.py <audio_file>")
        print("Supported formats: WAV, MP3, AIFF, AAC, OGG, FLAC")
        sys.exit(1)

    audio_path = Path(sys.argv[1])
    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}")
        sys.exit(1)

    print(f"Processing: {audio_path}")
    print("-" * 50)

    # Upload the audio file
    print("Uploading audio file...")
    uploaded_file = client.files.upload(file=str(audio_path))
    print(f"Uploaded: {uploaded_file.name}")

    # Test 1: Transcription
    print("\n[1] Transcription:")
    print("-" * 30)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe this audio. Provide the full text.",
            uploaded_file
        ]
    )
    print(response.text)

    # Test 2: Description
    print("\n[2] Audio Description:")
    print("-" * 30)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Describe this audio clip. What do you hear? Include details about speakers, tone, background sounds, etc.",
            uploaded_file
        ]
    )
    print(response.text)

    # Test 3: Analysis
    print("\n[3] Content Analysis:")
    print("-" * 30)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Analyze this audio content. Summarize the main topics, identify any speakers, and note the overall sentiment.",
            uploaded_file
        ]
    )
    print(response.text)

    # Cleanup
    print("\n" + "-" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
