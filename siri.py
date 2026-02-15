import asyncio
import edge_tts
import pygame
import speech_recognition as sr
import ollama
import os
import datetime
import re
import tempfile
import webbrowser
import pyautogui
import time

# --- 1. CONFIGURATION ---
VOICE = "en-PH-RosaNeural" 
MODEL = "llama3.2:3b"
BUFFER_FILE = "maya_stream.mp3"

# --- 2. AUTOMATION TOOLS ---
async def automation_handler(command):
    """Handles browser, system volume, and app switching."""
    cmd = command.lower()
    
    # --- System Volume Control ---
    if "volume" in cmd:
        if "increase" in cmd or "up" in cmd:
            await speak("Increasing volume, Sir.")
            for _ in range(5): pyautogui.press('volumeup')
        elif "decrease" in cmd or "down" in cmd:
            await speak("Decreasing volume, Sir.")
            for _ in range(5): pyautogui.press('volumedown')
        elif "mute" in cmd:
            await speak("Toggling mute, Sir.")
            pyautogui.press('volumemute')
        return True

    # --- App Switcher (Alt + Tab) ---
    elif "switch" in cmd and "app" in cmd:
        await speak("Switching apps, Sir.")
        pyautogui.hotkey('alt', 'tab')
        return True

    # --- YouTube Search ---
    elif "search" in cmd and "youtube" in cmd:
        search_query = cmd.replace("search", "").replace("on youtube", "").replace("for", "").strip()
        await speak(f"Searching for {search_query} on YouTube, Sir.")
        webbrowser.open("https://www.youtube.com")
        time.sleep(4) 
        pyautogui.press('/') 
        time.sleep(1)
        pyautogui.write(search_query, interval=0.1)
        pyautogui.press('enter')
        return True

    # --- Simple Browser Open ---
    elif "open" in cmd:
        if "youtube" in cmd:
            await speak("Opening YouTube, Sir.")
            webbrowser.open("https://www.youtube.com")
        elif "chrome" in cmd or "google" in cmd:
            await speak("Opening Chrome, Sir.")
            webbrowser.open("https://www.google.com")
        return True
    
    return False

# --- 3. VOICE ENGINE ---
async def speak(text):
    if not text.strip(): return
    clean_text = re.sub(r'[*#_]', '', text).strip()
    print(f"Maya: {clean_text}")
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        temp_filename = tmp_file.name

    try:
        communicate = edge_tts.Communicate(clean_text, VOICE)
        await communicate.save(temp_filename)
        if not pygame.mixer.get_init(): pygame.mixer.init()
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): await asyncio.sleep(0.05)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Voice Error: {e}")
    finally:
        if os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass

# --- 4. THE EARS ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 400 
recognizer.pause_threshold = 0.6 

def listen_instant():
    with sr.Microphone() as source:
        print("\n[READY]", end=" ", flush=True)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language='en-US')
            print(f"\rSir: {text}")
            return text
        except: return None

# --- 5. THE BRAIN ---
async def get_maya_response(user_input):
    try:
        stream = ollama.chat(model=MODEL, messages=[{"role": "user", "content": user_input}], stream=True)
        full_reply = ""
        sentence_buffer = ""
        for chunk in stream:
            token = chunk['message']['content']
            full_reply += token
            sentence_buffer += token
            if any(punc in token for punc in ['.', '?', '!', '\n']):
                if len(sentence_buffer.strip()) > 1:
                    await speak(sentence_buffer.strip())
                    sentence_buffer = ""
        if sentence_buffer.strip(): await speak(sentence_buffer.strip())
    except Exception as e:
        print(f"Brain Error: {e}")

# --- 6. MAIN LOOP ---
async def main():
    os.environ["OLLAMA_KEEP_ALIVE"] = "-1"
    with sr.Microphone() as source: recognizer.adjust_for_ambient_noise(source, duration=1.0)
    await speak("Systems integrated. Commands for volume and app switching are now active, Sir.")
    
    while True:
        try:
            user_input = await asyncio.to_thread(listen_instant)
            if user_input:
                was_automated = await automation_handler(user_input)
                
                if not was_automated:
                    if any(word in user_input.lower() for word in ['exit', 'goodbye']): break
                    await get_maya_response(user_input)
            
            await asyncio.sleep(0.1)
        except Exception: continue

if __name__ == "__main__":
    asyncio.run(main())