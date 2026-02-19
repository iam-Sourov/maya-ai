import asyncio
import edge_tts
import pygame
import speech_recognition as sr
import ollama
import os
import re
import tempfile
import webbrowser
import pyautogui

# --- 1. CONFIGURATION ---
VOICE = "en-PH-RosaNeural" 
MODEL = "llama3.2:3b"
speech_queue = asyncio.Queue()
stop_requested = False

# --- 2. VOICE ENGINE ---
async def speech_worker():
    global stop_requested
    while True:
        text = await speech_queue.get()
        if stop_requested:
            speech_queue._queue.clear()
            speech_queue.task_done()
            continue
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            temp_filename = tmp_file.name
        try:
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(temp_filename)
            if not pygame.mixer.get_init(): pygame.mixer.init()
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if stop_requested:
                    pygame.mixer.music.stop()
                    break
                await asyncio.sleep(0.01)
            pygame.mixer.music.unload()
        except: pass
        finally:
            if os.path.exists(temp_filename):
                try: os.remove(temp_filename)
                except: pass
            speech_queue.task_done()

# --- 3. THE EARS (High Accuracy Settings) ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 250  # Even more sensitive for quiet speech
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.pause_threshold = 1.2  # Allow longer pauses between words
recognizer.non_speaking_duration = 0.6

def listen_instant():
    with sr.Microphone() as source:
        print("\n[READY]", end=" ", flush=True)
        try:
            # Removed phrase_time_limit to prevent cutting off long sentences
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
            text = recognizer.recognize_google(audio, language='en-US')
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("[ERROR] Internet connection issue for speech recognition.")
            return None
        except Exception as e:
            return None

# --- 4. THE BRAIN ---
async def get_maya_response(user_input):
    global stop_requested
    history = [
        {"role": "system", "content": "You are Maya. No suggestions. Direct answers only. Brief (max 10 words)."},
        {"role": "user", "content": user_input}
    ]
    try:
        stream = ollama.chat(model=MODEL, messages=history, stream=True)
        sentence_buffer = ""
        for chunk in stream:
            if stop_requested: break
            token = chunk['message']['content']
            sentence_buffer += token
            if any(punc in token for punc in ['.', '?', '!', '\n']):
                speech_queue.put_nowait(sentence_buffer.strip())
                sentence_buffer = ""
        if sentence_buffer.strip() and not stop_requested:
            speech_queue.put_nowait(sentence_buffer.strip())
    except: pass

# --- 5. FULL AUTOMATION HANDLER (Restored) ---
async def automation_handler(command):
    cmd = command.lower()
    
    # Volume Control
    if "volume" in cmd:
        if "up" in cmd or "increase" in cmd: [pyautogui.press('volumeup') for _ in range(5)]
        elif "down" in cmd or "decrease" in cmd: [pyautogui.press('volumedown') for _ in range(5)]
        elif "mute" in cmd: pyautogui.press('volumemute')
        return True

    # App Switching
    elif "switch" in cmd and "app" in cmd:
        pyautogui.hotkey('alt', 'tab')
        return True

    # Browser & YouTube
    elif "search" in cmd and "youtube" in cmd:
        query = cmd.replace("search", "").replace("on youtube", "").replace("for", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True

    elif "open" in cmd:
        if "youtube" in cmd: webbrowser.open("https://www.youtube.com")
        elif "chrome" in cmd or "google" in cmd: webbrowser.open("https://www.google.com")
        return True

    # Window Management
    elif "refresh" in cmd or "reload" in cmd:
        pyautogui.press('f5')
        return True

    elif "minimise" in cmd:
        pyautogui.hotkey('win', 'd')
        return True
    
    return False

# --- 6. MAIN LOOP ---
async def main():
    global stop_requested
    os.environ["OLLAMA_KEEP_ALIVE"] = "-1"
    asyncio.create_task(speech_worker())
    
    with sr.Microphone() as source:
        print("Calibrating room noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2.0)
    
    print("Maya: Online and Accurate.")
    
    while True:
        user_input = await asyncio.to_thread(listen_instant)
        if user_input:
            print(f"Sir: {user_input}")
            cmd = user_input.lower()
            
            # Stop Feature
            if any(word in cmd for word in ['stop', 'shutup', 'cancel']):
                stop_requested = True
                pygame.mixer.music.stop()
                while not speech_queue.empty():
                    speech_queue.get_nowait()
                    speech_queue.task_done()
                continue

            stop_requested = False
            was_automated = await automation_handler(user_input)
            if not was_automated:
                if 'exit' in cmd: break
                await get_maya_response(user_input)
        
        await asyncio.sleep(0.05)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass