#!/usr/bin/env node
/**
 * Gemini 2.5 Flash Audio Understanding Test
 *
 * Tests basic audio processing capabilities:
 * - Transcription
 * - Description
 * - Analysis
 */

import { GoogleGenAI } from '@google/genai';
import { readFileSync } from 'fs';
import { basename, extname } from 'path';

const MIME_TYPES = {
  '.mp3': 'audio/mp3',
  '.wav': 'audio/wav',
  '.aiff': 'audio/aiff',
  '.aac': 'audio/aac',
  '.ogg': 'audio/ogg',
  '.flac': 'audio/flac',
};

async function main() {
  // Check for API key
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error('Error: GOOGLE_API_KEY environment variable not set');
    console.error('Get your key at: https://aistudio.google.com/apikey');
    process.exit(1);
  }

  // Check for audio file argument
  const audioPath = process.argv[2];
  if (!audioPath) {
    console.log('Usage: node audio_test.js <audio_file>');
    console.log('Supported formats: WAV, MP3, AIFF, AAC, OGG, FLAC');
    process.exit(1);
  }

  // Determine MIME type
  const ext = extname(audioPath).toLowerCase();
  const mimeType = MIME_TYPES[ext];
  if (!mimeType) {
    console.error(`Error: Unsupported audio format: ${ext}`);
    console.error('Supported: WAV, MP3, AIFF, AAC, OGG, FLAC');
    process.exit(1);
  }

  console.log(`Processing: ${audioPath}`);
  console.log('-'.repeat(50));

  // Initialize client
  const ai = new GoogleGenAI({ apiKey });

  // Upload the audio file
  console.log('Uploading audio file...');
  const audioData = readFileSync(audioPath);
  const base64Audio = audioData.toString('base64');

  const audioPart = {
    inlineData: {
      mimeType,
      data: base64Audio,
    },
  };

  // Test 1: Transcription
  console.log('\n[1] Transcription:');
  console.log('-'.repeat(30));
  let response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [
      {
        role: 'user',
        parts: [
          { text: 'Transcribe this audio. Provide the full text.' },
          audioPart,
        ],
      },
    ],
  });
  console.log(response.text);

  // Test 2: Description
  console.log('\n[2] Audio Description:');
  console.log('-'.repeat(30));
  response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [
      {
        role: 'user',
        parts: [
          { text: 'Describe this audio clip. What do you hear? Include details about speakers, tone, background sounds, etc.' },
          audioPart,
        ],
      },
    ],
  });
  console.log(response.text);

  // Test 3: Analysis
  console.log('\n[3] Content Analysis:');
  console.log('-'.repeat(30));
  response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [
      {
        role: 'user',
        parts: [
          { text: 'Analyze this audio content. Summarize the main topics, identify any speakers, and note the overall sentiment.' },
          audioPart,
        ],
      },
    ],
  });
  console.log(response.text);

  console.log('\n' + '-'.repeat(50));
  console.log('Done!');
}

main().catch(console.error);
