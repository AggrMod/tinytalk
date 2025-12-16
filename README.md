# TinyTalk - AI Speech Teacher for Toddlers

An AI-powered speech development tool for children ages 2-4, using Google's Gemini 2.5 Flash Native Audio.

## What is TinyTalk?

TinyTalk helps toddlers develop speech skills through:
- **Interactive conversations** with a patient AI friend
- **Word teaching** with pictures and repetition
- **Songs and rhymes** for language learning
- **Positive reinforcement** with stars and celebrations

## Features

- Real-time voice interaction (Gemini Native Audio)
- Child-friendly interface (big buttons, bright colors)
- Multiple teaching modes (Words, Chat, Songs)
- Session time limits for healthy screen time
- Parental controls and progress tracking
- Secure backend (API key never exposed to client)

## Quick Start

### 1. Start the Server

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set your API key
export GOOGLE_API_KEY=your-api-key

# Run
python app.py
```

### 2. Open the App

Navigate to `http://localhost:5000` in your browser.

### 3. Parent Setup

1. Click the settings icon (bottom right)
2. Enter PIN: `1234` (change this!)
3. Configure session length and word lists

## Project Structure

```
tinytalk/
├── server/
│   ├── app.py              # Flask backend + WebSocket proxy
│   ├── prompts.py          # Educational system prompts
│   └── requirements.txt
├── web/
│   ├── index.html          # Child-friendly main UI
│   ├── parent.html         # Parent dashboard
│   └── assets/             # Images, sounds
└── README.md
```

## Voice Options

TinyTalk uses child-appropriate voices:

| Voice | Style | Best For |
|-------|-------|----------|
| Aoede | Breezy, natural | General conversation |
| Leda | Youthful, energetic | Songs and games |
| Puck | Upbeat, energetic | Encouragement |

## Safety & Privacy

- API keys stored server-side only
- No data collection without consent
- Automatic session timeouts
- Content filtered for child safety
- COPPA-conscious design

## Speech Development Tips

Based on pediatric research:
- **Wait 5-10 seconds** for child to respond
- **Model clearly** - speak slowly, use full sentences
- **Repeat words** in different contexts
- **Keep sessions short** - 5-10 minutes max
- **Praise effort** not just success

## Requirements

- Python 3.8+
- Modern browser with microphone
- Google API key ([get one here](https://aistudio.google.com/apikey))

## Based On

This project is built on [gemini-native-audio-test](https://github.com/AggrMod/gemini-native-audio-test), using Google's Gemini 2.5 Flash Native Audio API.

## License

MIT
