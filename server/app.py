#!/usr/bin/env python3
"""
TinyTalk - Flask backend with WebSocket proxy to Gemini Live API.
Keeps API key secure server-side and adds educational prompts.
"""

import os
import json
import asyncio
import random
import time
from pathlib import Path

from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_sock import Sock
import websockets

from prompts import (
    TODDLER_TEACHER_PROMPT,
    WORD_TEACHING_PROMPT,
    CONVERSATION_PROMPT,
    SONG_PROMPT,
    WORD_LISTS,
    GREETINGS,
    ENCOURAGEMENTS,
    GOODBYES,
)

# Load .env file
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

app = Flask(__name__, static_folder='../web', static_url_path='')
sock = Sock(app)

# Configuration
API_KEY = os.environ.get('GOOGLE_API_KEY', '')
MODEL = 'gemini-2.5-flash-native-audio-preview-12-2025'
VOICES = ['Aoede', 'Leda', 'Puck']  # Child-appropriate voices
DEFAULT_VOICE = 'Aoede'

# Session management
sessions = {}
MAX_SESSION_DURATION = 600  # 10 minutes default


class Session:
    """Track session state and timing."""
    def __init__(self, session_id, mode='conversation', voice=DEFAULT_VOICE, max_duration=MAX_SESSION_DURATION):
        self.id = session_id
        self.mode = mode
        self.voice = voice
        self.start_time = time.time()
        self.max_duration = max_duration
        self.current_word = None
        self.word_index = 0
        self.stars = 0

    def is_expired(self):
        return time.time() - self.start_time > self.max_duration

    def time_remaining(self):
        return max(0, self.max_duration - (time.time() - self.start_time))

    def get_system_prompt(self):
        """Get the appropriate system prompt for the current mode."""
        base = TODDLER_TEACHER_PROMPT

        if self.mode == 'words' and self.current_word:
            word, desc = self.current_word
            return base + '\n\n' + WORD_TEACHING_PROMPT.format(word=word, category=desc)
        elif self.mode == 'songs':
            return base + '\n\n' + SONG_PROMPT
        else:
            return base + '\n\n' + CONVERSATION_PROMPT


@app.route('/')
def index():
    """Serve the main child UI."""
    return send_from_directory('../web', 'index.html')


@app.route('/parent')
def parent():
    """Serve the parent dashboard."""
    return send_from_directory('../web', 'parent.html')


@app.route('/assets/<path:filename>')
def assets(filename):
    """Serve static assets."""
    return send_from_directory('../web/assets', filename)


@app.route('/api/config')
def get_config():
    """Get app configuration (no secrets)."""
    return jsonify({
        'voices': VOICES,
        'defaultVoice': DEFAULT_VOICE,
        'modes': ['conversation', 'words', 'songs'],
        'wordCategories': list(WORD_LISTS.keys()),
        'maxSessionDuration': MAX_SESSION_DURATION,
    })


@app.route('/api/words/<category>')
def get_words(category):
    """Get word list for a category."""
    if category in WORD_LISTS:
        return jsonify([{'word': w, 'hint': h} for w, h in WORD_LISTS[category]])
    return jsonify([])


@app.route('/api/greeting')
def get_greeting():
    """Get a random greeting."""
    return jsonify({'greeting': random.choice(GREETINGS)})


@app.route('/api/encouragement')
def get_encouragement():
    """Get a random encouragement."""
    return jsonify({'message': random.choice(ENCOURAGEMENTS)})


@sock.route('/ws')
def websocket_proxy(ws):
    """WebSocket proxy to Gemini Live API."""

    if not API_KEY:
        ws.send(json.dumps({'error': 'API key not configured'}))
        return

    # Get session config from first message
    try:
        config_msg = ws.receive(timeout=5)
        config = json.loads(config_msg)
    except Exception as e:
        ws.send(json.dumps({'error': f'Invalid config: {e}'}))
        return

    session_id = config.get('sessionId', str(time.time()))
    mode = config.get('mode', 'conversation')
    voice = config.get('voice', DEFAULT_VOICE)
    max_duration = config.get('maxDuration', MAX_SESSION_DURATION)
    word_category = config.get('wordCategory', 'animals')

    # Validate voice
    if voice not in VOICES:
        voice = DEFAULT_VOICE

    # Create session
    session = Session(session_id, mode, voice, max_duration)

    # If in word mode, set up word list
    if mode == 'words' and word_category in WORD_LISTS:
        words = WORD_LISTS[word_category]
        if words:
            session.current_word = words[0]

    sessions[session_id] = session

    # Connect to Gemini
    gemini_url = f'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={API_KEY}'

    async def run_proxy():
        try:
            async with websockets.connect(gemini_url) as gemini_ws:
                # Send setup with system prompt
                setup_msg = {
                    'setup': {
                        'model': f'models/{MODEL}',
                        'generation_config': {
                            'response_modalities': ['AUDIO'],
                            'speech_config': {
                                'voice_config': {
                                    'prebuilt_voice_config': {
                                        'voice_name': session.voice
                                    }
                                }
                            }
                        },
                        'system_instruction': {
                            'parts': [{'text': session.get_system_prompt()}]
                        }
                    }
                }
                await gemini_ws.send(json.dumps(setup_msg))

                # Wait for setup complete
                setup_response = await gemini_ws.recv()
                ws.send(setup_response)

                # Bidirectional proxy
                async def client_to_gemini():
                    """Forward client audio to Gemini."""
                    while not session.is_expired():
                        try:
                            data = ws.receive(timeout=0.1)
                            if data:
                                await gemini_ws.send(data)
                        except Exception:
                            await asyncio.sleep(0.05)

                async def gemini_to_client():
                    """Forward Gemini responses to client."""
                    while not session.is_expired():
                        try:
                            response = await asyncio.wait_for(gemini_ws.recv(), timeout=0.1)
                            ws.send(response)
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            print(f"Gemini receive error: {e}")
                            break

                    # Session expired - send goodbye
                    if session.is_expired():
                        goodbye = random.choice(GOODBYES)
                        ws.send(json.dumps({
                            'sessionEnd': {
                                'reason': 'timeout',
                                'message': goodbye,
                                'stars': session.stars
                            }
                        }))

                async def timer_check():
                    """Check session timer and send updates."""
                    while not session.is_expired():
                        await asyncio.sleep(30)
                        remaining = session.time_remaining()
                        ws.send(json.dumps({
                            'timeUpdate': {
                                'remaining': remaining,
                                'stars': session.stars
                            }
                        }))

                await asyncio.gather(
                    client_to_gemini(),
                    gemini_to_client(),
                    timer_check()
                )

        except Exception as e:
            print(f"Proxy error: {e}")
            ws.send(json.dumps({'error': str(e)}))
        finally:
            if session_id in sessions:
                del sessions[session_id]

    # Run async proxy in sync context
    asyncio.run(run_proxy())


if __name__ == '__main__':
    if not API_KEY:
        print("WARNING: GOOGLE_API_KEY not set!")
        print("Set it with: export GOOGLE_API_KEY=your-key")

    print("\n" + "="*50)
    print("TinyTalk Server")
    print("="*50)
    print(f"Open http://localhost:5000 in your browser")
    print(f"Parent dashboard: http://localhost:5000/parent")
    print("="*50 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
