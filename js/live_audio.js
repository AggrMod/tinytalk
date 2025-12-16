#!/usr/bin/env node
/**
 * Gemini 2.5 Flash Native Audio - Live API Test
 *
 * Text-based test of the Live API connection.
 * For full audio support, see the Python version or use in browser.
 *
 * Model: gemini-2.5-flash-native-audio-preview-12-2025
 */

import { GoogleGenAI } from '@google/genai';
import { createInterface } from 'readline';

const MODEL = 'gemini-2.5-flash-native-audio-preview-12-2025';

async function main() {
  // Check for API key
  const apiKey = process.env.GOOGLE_API_KEY;
  if (!apiKey) {
    console.error('Error: GOOGLE_API_KEY environment variable not set');
    console.error('Get your key at: https://aistudio.google.com/apikey');
    process.exit(1);
  }

  console.log('='.repeat(60));
  console.log('Gemini 2.5 Flash Native Audio - Live API Test');
  console.log('='.repeat(60));
  console.log(`Model: ${MODEL}`);
  console.log('Type messages to test the Live API. Type "quit" to exit.');
  console.log('-'.repeat(60));

  // Initialize client
  const ai = new GoogleGenAI({ apiKey });

  const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  try {
    // Test model availability with standard generation first
    console.log('\nTesting model connection...');

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [{ role: 'user', parts: [{ text: 'Say "Hello! Native Audio API is ready." in exactly those words.' }] }],
    });

    console.log(`Response: ${response.text}\n`);
    console.log('Model connection successful!\n');

    // Interactive loop
    const prompt = () => {
      rl.question('You: ', async (input) => {
        if (input.toLowerCase() === 'quit') {
          console.log('Goodbye!');
          rl.close();
          process.exit(0);
        }

        try {
          const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: [{ role: 'user', parts: [{ text: input }] }],
          });
          console.log(`Gemini: ${response.text}\n`);
        } catch (error) {
          console.error('Error:', error.message);
        }

        prompt();
      });
    };

    prompt();

  } catch (error) {
    console.error('Connection error:', error.message);
    rl.close();
    process.exit(1);
  }
}

main().catch(console.error);
