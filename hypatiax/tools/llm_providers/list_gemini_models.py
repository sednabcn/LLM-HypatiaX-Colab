#!/usr/bin/env python3
"""
List available Gemini models for your API key
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("❌ GOOGLE_API_KEY not found")
    exit(1)

genai.configure(api_key=api_key)

print("Available Gemini Models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")

"""
┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab]
└─$ python hypatiax/tools/llm_providers/list_gemini_models.py                                      
Available Gemini Models:
============================================================

✓ models/gemini-2.5-pro-preview-03-25
  Display Name: Gemini 2.5 Pro Preview 03-25
  Description: Gemini 2.5 Pro Preview 03-25

✓ models/gemini-2.5-flash
  Display Name: Gemini 2.5 Flash
  Description: Stable version of Gemini 2.5 Flash, our mid-size multimodal model that supports up to 1 million tokens, released in June of 2025.

✓ models/gemini-2.5-pro-preview-05-06
  Display Name: Gemini 2.5 Pro Preview 05-06
  Description: Preview release (May 6th, 2025) of Gemini 2.5 Pro

✓ models/gemini-2.5-pro-preview-06-05
  Display Name: Gemini 2.5 Pro Preview
  Description: Preview release (June 5th, 2025) of Gemini 2.5 Pro

✓ models/gemini-2.5-pro
  Display Name: Gemini 2.5 Pro
  Description: Stable release (June 17th, 2025) of Gemini 2.5 Pro

✓ models/gemini-2.0-flash-exp
  Display Name: Gemini 2.0 Flash Experimental
  Description: Gemini 2.0 Flash Experimental

✓ models/gemini-2.0-flash
  Display Name: Gemini 2.0 Flash
  Description: Gemini 2.0 Flash

✓ models/gemini-2.0-flash-001
  Display Name: Gemini 2.0 Flash 001
  Description: Stable version of Gemini 2.0 Flash, our fast and versatile multimodal model for scaling across diverse tasks, released in January of 2025.

✓ models/gemini-2.0-flash-lite-001
  Display Name: Gemini 2.0 Flash-Lite 001
  Description: Stable version of Gemini 2.0 Flash-Lite

✓ models/gemini-2.0-flash-lite
  Display Name: Gemini 2.0 Flash-Lite
  Description: Gemini 2.0 Flash-Lite

✓ models/gemini-2.0-flash-lite-preview-02-05
  Display Name: Gemini 2.0 Flash-Lite Preview 02-05
  Description: Preview release (February 5th, 2025) of Gemini 2.0 Flash-Lite

✓ models/gemini-2.0-flash-lite-preview
  Display Name: Gemini 2.0 Flash-Lite Preview
  Description: Preview release (February 5th, 2025) of Gemini 2.0 Flash-Lite

✓ models/gemini-2.0-pro-exp
  Display Name: Gemini 2.0 Pro Experimental
  Description: Experimental release (March 25th, 2025) of Gemini 2.5 Pro

✓ models/gemini-2.0-pro-exp-02-05
  Display Name: Gemini 2.0 Pro Experimental 02-05
  Description: Experimental release (March 25th, 2025) of Gemini 2.5 Pro

✓ models/gemini-exp-1206
  Display Name: Gemini Experimental 1206
  Description: Experimental release (March 25th, 2025) of Gemini 2.5 Pro

✓ models/gemini-2.0-flash-thinking-exp-01-21
  Display Name: Gemini 2.5 Flash Preview 05-20
  Description: Preview release (April 17th, 2025) of Gemini 2.5 Flash

✓ models/gemini-2.0-flash-thinking-exp
  Display Name: Gemini 2.5 Flash Preview 05-20
  Description: Preview release (April 17th, 2025) of Gemini 2.5 Flash

✓ models/gemini-2.0-flash-thinking-exp-1219
  Display Name: Gemini 2.5 Flash Preview 05-20
  Description: Preview release (April 17th, 2025) of Gemini 2.5 Flash

✓ models/gemini-2.5-flash-preview-tts
  Display Name: Gemini 2.5 Flash Preview TTS
  Description: Gemini 2.5 Flash Preview TTS

✓ models/gemini-2.5-pro-preview-tts
  Display Name: Gemini 2.5 Pro Preview TTS
  Description: Gemini 2.5 Pro Preview TTS

✓ models/learnlm-2.0-flash-experimental
  Display Name: LearnLM 2.0 Flash Experimental
  Description: LearnLM 2.0 Flash Experimental

✓ models/gemma-3-1b-it
  Display Name: Gemma 3 1B
  Description: 

✓ models/gemma-3-4b-it
  Display Name: Gemma 3 4B
  Description: 

✓ models/gemma-3-12b-it
  Display Name: Gemma 3 12B
  Description: 

✓ models/gemma-3-27b-it
  Display Name: Gemma 3 27B
  Description: 

✓ models/gemma-3n-e4b-it
  Display Name: Gemma 3n E4B
  Description: 

✓ models/gemma-3n-e2b-it
  Display Name: Gemma 3n E2B
  Description: 

✓ models/gemini-flash-latest
  Display Name: Gemini Flash Latest
  Description: Latest release of Gemini Flash

✓ models/gemini-flash-lite-latest
  Display Name: Gemini Flash-Lite Latest
  Description: Latest release of Gemini Flash-Lite

✓ models/gemini-pro-latest
  Display Name: Gemini Pro Latest
  Description: Latest release of Gemini Pro

✓ models/gemini-2.5-flash-lite
  Display Name: Gemini 2.5 Flash-Lite
  Description: Stable version of Gemini 2.5 Flash-Lite, released in July of 2025

✓ models/gemini-2.5-flash-image-preview
  Display Name: Nano Banana
  Description: Gemini 2.5 Flash Preview Image

✓ models/gemini-2.5-flash-image
  Display Name: Nano Banana
  Description: Gemini 2.5 Flash Preview Image

✓ models/gemini-2.5-flash-preview-09-2025
  Display Name: Gemini 2.5 Flash Preview Sep 2025
  Description: Gemini 2.5 Flash Preview Sep 2025

✓ models/gemini-2.5-flash-lite-preview-09-2025
  Display Name: Gemini 2.5 Flash-Lite Preview Sep 2025
  Description: Preview release (Septempber 25th, 2025) of Gemini 2.5 Flash-Lite

✓ models/gemini-3-pro-preview
  Display Name: Gemini 3 Pro Preview
  Description: Gemini 3 Pro Preview

✓ models/gemini-robotics-er-1.5-preview
  Display Name: Gemini Robotics-ER 1.5 Preview
  Description: Gemini Robotics-ER 1.5 Preview

✓ models/gemini-2.5-computer-use-preview-10-2025
  Display Name: Gemini 2.5 Computer Use Preview 10-2025
  Description: Gemini 2.5 Computer Use Preview 10-2025

"""
