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
import time
import keyboard
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. CONFIGURATION ---
VOICE = "en-IN-PradeepNeural"  # Male Indian English (Clean & Professional)
MODEL = "llama3:latest" 
speech_queue = asyncio.Queue()
processing_queue = asyncio.Queue()
stop_requested = False
last_speech_time = 0
is_speaking = False  # Global flag to cover the entire TTS lifecycle

# --- 2. VOICE ENGINE ---
async def speech_worker():
    global stop_requested, last_speech_time, is_speaking
    while True:
        text = await speech_queue.get()
        if stop_requested:
            speech_queue._queue.clear()
            speech_queue.task_done()
            continue
            
        is_speaking = True  # Signal that we are busy processing speech
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
            last_speech_time = time.time()
        except: pass
        finally:
            is_speaking = False  # Release the lock only after everything is done
            if os.path.exists(temp_filename):
                try: os.remove(temp_filename)
                except: pass
            speech_queue.task_done()

# --- 2.5 AI PROCESSING WORKER (The Brain Channel) ---
async def ai_processing_worker():
    global stop_requested
    while True:
        user_input = await processing_queue.get()
        if stop_requested:
            processing_queue.task_done()
            continue
            
        # Automation Check
        was_automated = await automation_handler(user_input)
        if not was_automated:
            await get_maya_response(user_input)
            
        processing_queue.task_done()

# --- 2.7 KEYBOARD MONITOR (Instant Kill Switch) ---
async def keyboard_monitor():
    while True:
        if keyboard.is_pressed('esc'):
            print("\n[EXIT] User pressed ESC (Force Kill).")
            # Force kill the process immediately, as threads might be blocking
            os._exit(0) 
        await asyncio.sleep(0.1)

# --- 3. THE EARS (High Accuracy Settings) ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 500  # Fixed high threshold for consistent sensitivity
recognizer.dynamic_energy_threshold = False # Disable dynamic adjustment to prevent "deafness" from sudden noises
recognizer.pause_threshold = 1.0 
recognizer.non_speaking_duration = 0.5

def listen_instant():
    # Don't listen if Maya is struggling to speak (generating or playing)
    if is_speaking: return None
        
    with sr.Microphone() as source:
        print("\n[READY]", end=" ", flush=True)
        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
            text = recognizer.recognize_google(audio, language='en-IN')
            if text and len(text) > 2: # Filter out noise hallucinations
                return text
            return None
        except sr.UnknownValueError: return None
        except sr.RequestError: return None
        except Exception: return None

# --- 4. THE BRAIN ---
async def get_maya_response(user_input):
    global stop_requested
    history = [
        {"role": "system", "content": "You are Maya, an advanced AI with a dry, sarcastic, JARVIS-like personality. Be proactively helpful but witty. Keep answers short (max 1 sentence)."},
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

# --- 4.5 SELENIUM BROWSER AUTOMATION ---
def play_youtube_automation(song_name):
    try:
        print(f"[SELENIUM] Initializing Browser for: {song_name}")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True) # Keep browser open after script ends
        options.add_argument("--start-maximized")
        options.add_argument("--log-level=3") # Suppress logs
        # Initialize Driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print(f"[SELENIUM] Searching in YouTube...")
        # Smart Navigation: Go directly to search results to save time
        query = song_name.replace(" ", "+")
        driver.get(f"https://www.youtube.com/results?search_query={query}&sp=EgIQAQ%253D%253D") # sp=EgIQAQ%3D%3D forces Video-only results
        
        # Click the first video
        time.sleep(2) 
        
        # Try to find the first video title link via XPath (more reliable for exact ID match)
        video_link = driver.find_element(By.XPATH, '//*[@id="video-title"]')
        if video_link:
            print(f"[SELENIUM] Playing video: {video_link.get_attribute('title')}")
            video_link.click()
            return True
    except Exception as e:
        print(f"[SELENIUM ERROR] {e}")
        return False

# --- 5. FULL AUTOMATION HANDLER (Restored) ---
async def automation_handler(command):
    cmd = command.lower()
    print(f"[DEBUG] Automation Check: {cmd}")
    
    # Volume Control
    if "volume" in cmd:
        if "up" in cmd or "increase" in cmd: [pyautogui.press('volumeup') for _ in range(5)]
        elif "down" in cmd or "decrease" in cmd: [pyautogui.press('volumedown') for _ in range(5)]
        elif "mute" in cmd: pyautogui.press('volumemute')
        return True

    # App Switching
    elif "switch" in cmd or "switch app" in cmd:
        # Extract the app name (if any)
        target = cmd.replace("switch", "").replace("switch app", "").replace("to", "").replace("app", "").replace("window", "").strip()
        
        if target:
            # "Switch to [App Name]" -> Uses Windows Search to find/focus
            pyautogui.press('win')
            time.sleep(0.2)
            pyautogui.write(target)
            time.sleep(0.5)
            pyautogui.press('enter')
        else:
            # "Switch" / "Which App" -> Generic Alt+Tab
            pyautogui.hotkey('alt', 'tab')
        return True
    
    # Browser & YouTube - Smart "Play" Command
    elif "play" in cmd:
        query = cmd.replace("play", "").replace("on youtube", "").replace("search", "").replace("for", "").strip()
        print(f"[ACTION] Playing (via Selenium) YouTube for: {query}")
        # Use asyncio.to_thread to prevent blocking the voice loop
        await asyncio.to_thread(play_youtube_automation, query)
        return True

    elif "youtube" in cmd and "open" not in cmd:
        query = cmd.replace("search", "").replace("on youtube", "").replace("for", "").strip()
        print(f"[ACTION] Searching YouTube for: {query}")
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True

    elif "open" in cmd:
        if "youtube" in cmd: 
            print("[ACTION] Opening YouTube Homepage")
            webbrowser.open("https://www.youtube.com")
            return True
        elif "chrome" in cmd or "google" in cmd: 
            print("[ACTION] Opening Google")
            webbrowser.open("https://www.google.com")
            return True
        elif "facebook" in cmd:
            webbrowser.open("https://www.facebook.com")
            return True
        return False

    # Window Management
    elif "close" in cmd or "exit window" in cmd:
        pyautogui.hotkey('alt', 'f4')
        return True

    elif "minimize" in cmd:
        pyautogui.hotkey('win', 'd')
        return True
    
    elif "maximize" in cmd:
        pyautogui.hotkey('win', 'up')
        return True
        
    elif "scroll" in cmd:
        if "up" in cmd: pyautogui.scroll(300)
        elif "down" in cmd: pyautogui.scroll(-300)
        return True
        
    elif "type" in cmd:
        text_to_type = cmd.split("type", 1)[1].strip()
        pyautogui.write(text_to_type)
        return True
        
    elif "press" in cmd:
        key = cmd.split("press", 1)[1].strip()
        if key in ['enter', 'escape', 'space', 'tab', 'backspace']:
            pyautogui.press(key)
        return True
    
    return False

# --- 6. MAIN LOOP ---
async def main():
    global stop_requested, is_speaking
    os.environ["OLLAMA_KEEP_ALIVE"] = "-1"
    
    # Start the distributed channels
    asyncio.create_task(speech_worker())
    asyncio.create_task(ai_processing_worker())
    asyncio.create_task(keyboard_monitor()) # Start the keyboard listener
    
    with sr.Microphone() as source:
        print("Calibrating room noise...")
        recognizer.adjust_for_ambient_noise(source, duration=2.0)
    
    print("Maya: Online and ready.")
    speech_queue.put_nowait("Online and ready, sir. Systems go.")
    
    while True:
        # Prevent "Self-Hearing": 
        # Check the global flag that covers the entire TTS lifecycle
        if is_speaking:
            await asyncio.sleep(0.05)
            continue
            
        # Cooldown period (0.5s) after she stops speaking
        if time.time() - last_speech_time < 0.5:
             await asyncio.sleep(0.05)
             continue
             
        # The 'Hearing' Channel runs continuously
        try:
            # increased timeout slightly so we check for speaking status more often if silence
            user_input = await asyncio.to_thread(listen_instant)
        except: user_input = None

        if user_input:
            # Double check: Did she start speaking while we were listening?
            if is_speaking:
                print(f"[IGNORED] Self-hearing prevention: '{user_input}'")
                continue 
            
            # Post-speech cooldown check again
            if time.time() - last_speech_time < 0.5:
                print(f"[IGNORED] Too soon after speaking: '{user_input}'")
                continue
                
            print(f"Sir: {user_input}")
            
            # --- PHONETIC CORRECTIONS ---
            # Fixes common misheard words due to accent/microphone
            corrections = {
                "momo": "moho",
                "mohan": "moho",
                "mojo": "moho",
                "moto": "moho"
            }
            lower_input = user_input.lower()
            for wrong, right in corrections.items():
                if wrong in lower_input:
                    user_input = lower_input.replace(wrong, right)
                    print(f"[CORRECTED] '{wrong}' -> '{right}'")
            
            cmd = user_input.lower()
            
            # Immediate Stop Override
            if any(word in cmd for word in ['stop', 'shutup', 'cancel', 'silence']):
                stop_requested = True
                pygame.mixer.music.stop()
                # Clear all queues
                while not speech_queue.empty(): speech_queue.get_nowait()
                while not processing_queue.empty(): processing_queue.get_nowait()
                print("[SILENCED]")
                await asyncio.sleep(0.5) # Debounce
                stop_requested = False
                continue
                
            if 'exit' in cmd: break
            
            # Feed the 'Processing' Channel
            processing_queue.put_nowait(user_input)
        
        await asyncio.sleep(0.05)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass