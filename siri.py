import asyncio
import edge_tts
import pygame
import speech_recognition as sr
import ollama
import os
import datetime
import re
import tempfile

# --- 1. CONFIGURATION ---
VOICE = "en-PH-RosaNeural" # Sophisticated English Female Voice
MODEL = "llama3.2:3b"     # Efficient and accurate for 2026 standards
BUFFER_FILE = "maya_stream.mp3"

# --- 2. VOICE ENGINE (TTS) ---
async def speak(text):
    if not text.strip(): return
    
    # Cleaning: Removing markdown and extra symbols
    clean_text = re.sub(r'[*#_]', '', text).strip()
    print(f"Maya: {clean_text}")
    
    # Use temporary files to avoid permission errors
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        temp_filename = tmp_file.name

    try:
        communicate = edge_tts.Communicate(clean_text, VOICE)
        await communicate.save(temp_filename)
        
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Voice Error: {e}")
    finally:
        if os.path.exists(temp_filename):
            try: os.remove(temp_filename)
            except: pass

# --- 3. THE EARS (STT) ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 400 
recognizer.dynamic_energy_threshold = False
recognizer.pause_threshold = 0.6 
recognizer.non_speaking_duration = 0.5 

def listen_instant():
    with sr.Microphone() as source:
        print("\n[LISTENING]", end=" ", flush=True)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            # Language changed to English (US)
            text = recognizer.recognize_google(audio, language='en-US')
            print(f"\rSir: {text}")
            return text
        except Exception:
            return None

# --- 4. THE BRAIN (English Persona) ---
current_date = datetime.datetime.now().strftime("%B %d, %Y")
chat_history = [
    {
        "role": "system",
        "content": (
            f"You are 'Maya', a highly intelligent, calm, and loyal AI assistant. "
            f"Today is {current_date}. You are assisting 'Sir'. "
            "Guidelines: 1. Respond only in English. 2. Be concise but informative. "
            "3. Maintain a deeply respectful and professional tone. "
            "4. Provide direct answers without unnecessary filler."
        )
    }
]

async def get_maya_response(user_input):
    chat_history.append({"role": "user", "content": user_input})
    
    try:
        # Streaming enabled for faster response
        stream = ollama.chat(
            model=MODEL, 
            messages=chat_history, 
            stream=True,
            options={"temperature": 0.5, "num_predict": 100}
        )
        
        full_reply = ""
        sentence_buffer = ""
        
        for chunk in stream:
            token = chunk['message']['content']
            full_reply += token
            sentence_buffer += token
            
            # Sentence detection for English punctuation
            if any(punc in token for punc in ['.', '?', '!', '\n']):
                if len(sentence_buffer.strip()) > 1:
                    await speak(sentence_buffer.strip())
                    sentence_buffer = ""

        if sentence_buffer.strip():
            await speak(sentence_buffer.strip())
            
        chat_history.append({"role": "assistant", "content": full_reply})
        
        # Keep memory optimized
        if len(chat_history) > 10:
            chat_history.pop(1)

    except Exception as e:
        print(f"Brain Error: {e}")
        await speak("I apologize, Sir, but I am having trouble processing that right now.")

# --- 5. MAIN LOOP ---
async def main():
    os.environ["OLLAMA_KEEP_ALIVE"] = "-1"
    
    print("Maya: Calibrating microphone...")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
    
    await speak("System online. Hello Sir, how may I assist you today?")
    
    while True:
        try:
            user_input = await asyncio.to_thread(listen_instant)
            
            if user_input:
                cmd = user_input.lower()
                
                # Shutdown commands
                if any(word in cmd for word in ['goodbye', 'shutdown', 'exit', 'stop maya']):
                    await speak("Goodbye, Sir. Have a wonderful day.")
                    break
                
                # Instant Tool: Time
                if any(w in cmd for w in ['time', 'clock']):
                    now = datetime.datetime.now().strftime("%I:%M %p")
                    await speak(f"The time is currently {now}, Sir.")
                    continue
                
                await get_maya_response(user_input)
            
            await asyncio.sleep(0.1)
        except Exception:
            continue

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMaya shutting down.")